"""Manual trusted CI: one regression, captured-HTTP diagnostics, guarded publication.

No seed/reset, no campaign and no Git writes. Exit 1 preserves SUT findings;
exit 2 means infrastructure/harness/cleanup/evidence failure. Neither is green.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import p09_runtime as p09
from scenario_trace import validate

ROOT = p09.ROOT
NS = 'r06-k05-p09-20261115-audit01'
SECRET_KEYS = {'P09_DB_PASSWORD', 'P09_KEY', 'P09_SECRET', 'P09_ADMIN_PASSWORD',
               'P09_EDITOR_PASSWORD', 'P09_READER_PASSWORD', 'LICENSE_KEY', 'P09_LICENSE_KEY'}
TRUSTED_INPUTS = ['scripts','profiles','.github','lab.sh','tests',
                  'docs/coverage/baselines','docs/coverage/schemas',
                  'docs/coverage/acceptance/P15-HTTP-20261116-01',
                  'docs/coverage/sources/immutable-inputs-v1',
                  'docs/coverage/acceptance/M2-COVERAGE-20261116/bundle/input-archive.json']


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2)+'\n', encoding='utf-8')


def load(path):
    return json.loads(path.read_bytes())


def contained(root, path):
    root, path = Path(root).resolve(), Path(path)
    # Reject junctions/symlinks as well as lexical traversal before publication.
    if not path.resolve().is_relative_to(root):
        raise ValueError('UNSAFE_ARTIFACT_PATH')
    for item in (path, *path.parents):
        if item == root:
            break
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            raise ValueError('UNSAFE_ARTIFACT_LINK')
    return path


def secret_values(private):
    values = []
    for line in private.read_text(encoding='utf-8-sig').splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() in SECRET_KEYS:
            value = value.strip().strip('"').strip("'")
            if value:
                values.append(value)
    values += [os.environ[k] for k in ('GITHUB_TOKEN','GH_TOKEN') if os.environ.get(k)]
    return values


def check_private_profile(private):
    """Fail before credential reads when profile/directory permissions are broad."""
    if not private.is_file() or private.is_symlink() or private.parent.is_symlink():
        raise ValueError('BLOCKED_PRIVATE_ACL')
    if os.name == 'nt':
        result = subprocess.run(['pwsh','-NoProfile','-NonInteractive','-File',
                                 str(ROOT/'scripts/private_profile_acl.ps1'),
                                 '-Mode','Check','-Namespace',NS],capture_output=True,timeout=45)
        if result.returncode:
            raise ValueError('BLOCKED_PRIVATE_ACL')
        report=json.loads(result.stdout.decode('utf-8-sig'))
        if report.get('status')!='PASS' or report.get('secret_bytes_read')!=0:
            raise ValueError('BLOCKED_PRIVATE_ACL')
        return report
    if any(path.stat().st_mode & 0o077 for path in (private,private.parent)):
        raise ValueError('BLOCKED_PRIVATE_ACL')
    return {'status':'PASS','scope':'POSIX_OWNER_ONLY_DIRECTORY_AND_ENV','secret_bytes_read':0}


def safe_bytes(raw, secrets):
    for secret in secrets:
        if any(value in raw for value in (secret.encode(), json.dumps(secret)[1:-1].encode())):
            raise ValueError('ARTIFACT_SECRET_DETECTED')
    if re.search(rb'(?i)(bearer\s+[a-z0-9_.-]{20,}|"(?:access_token|refresh_token)"\s*:\s*"[^"\s]{16,}|set-cookie\s*:)', raw):
        raise ValueError('ARTIFACT_CREDENTIAL_PATTERN')
    return raw


def publish(source, target, secrets):
    # Scan every file BEFORE copying any. Never redact or rewrite a raw contract.
    entries = []
    for path in sorted(source.rglob('*')):
        contained(source, path)
        if path.is_file() and path.relative_to(source) != Path('artifact-index.json'):
            raw = safe_bytes(path.read_bytes(), secrets)
            entries.append((path.relative_to(source), raw))
    target.mkdir(exist_ok=False)
    for rel, raw in entries:
        out = target/rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
    save(target/'artifact-index.json', {p.as_posix():{'sha256':hashlib.sha256(raw).hexdigest(), 'bytes':len(raw)} for p,raw in entries})


def regression_state(report, code):
    cases = report.get('cases', [])
    if (code not in (0,1) or report.get('execution_complete') is not True
            or len(cases) != 13 or len({c['canonical_test_id'] for c in cases}) != 13
            or report.get('cleanup') != 'passed'
            or any(c.get('cleanup_status', 'passed') != 'passed' or c['status'] not in ('passed','failed') for c in cases)):
        return 'HARNESS_INFRA_OR_CLEANUP_ERROR'
    failed = [c for c in cases if c['status'] == 'failed']
    if bool(failed) != (code == 1):
        return 'HARNESS_INFRA_OR_CLEANUP_ERROR'
    known = [c for c in failed if c['canonical_test_id'] == 'P3-CONTRACT-QA_ARTICLES-OBJECT'
             and c.get('verdicts',{}).get('business') == 'passed'
             and c.get('verdicts',{}).get('contract') == 'failed']
    return 'KNOWN_TC13_CONTRACT_FAIL' if failed and len(known) == len(failed) else 'SUT_ASSERTION_FAIL' if failed else 'PASS'


def final_code(regression, diagnostic, cleanup):
    if regression == 'HARNESS_INFRA_OR_CLEANUP_ERROR' or diagnostic in ('ERROR','NOT_RUN','NOT_MEASURED') or cleanup != 'PASS':
        return 2
    return 1 if regression != 'PASS' or diagnostic == 'FAIL' else 0


def check_remote_source(source, github_sha):
    if not github_sha or source['harness_sha'] != github_sha:
        raise ValueError('CI_REVISION_MISMATCH')
    if source['uncommitted_code']:
        raise ValueError('CI_SOURCE_NOT_COMMITTED')


def require_remote_context():
    if (os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_EVENT_NAME')!='workflow_dispatch'
            or os.environ.get('GITHUB_REPOSITORY')!='minnhi09/Directus-Testing' or os.environ.get('GITHUB_REF')!='refs/heads/main'):
        raise ValueError('UNTRUSTED_CI_CONTEXT')


def source_state():
    tracked=subprocess.run(['git','diff','--quiet','HEAD','--',*TRUSTED_INPUTS],cwd=ROOT).returncode
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--',*TRUSTED_INPUTS],cwd=ROOT,text=True).splitlines()
    code_files=[p for p in untracked if Path(p).suffix!='.pyc']
    return dict(harness_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                uncommitted_code=bool(tracked or code_files),
                fingerprints={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                  ('scripts/ci_m2.py','scripts/p10_regression.py','scripts/p09_runtime.py','scripts/lab-components.sh',
                   'scripts/windows/jq','scripts/check_scenario_contracts.py','scripts/contract_checks.py',
                   '.github/workflows/p10-integration-preflight.yml','scripts/private_profile_acl.ps1')})


def collect_regression(run, work, regression):
    """Keep partial reports on failure too; never copy whole private runtime."""
    regression.mkdir()
    for path in run.glob('*.json'):
        shutil.copyfile(contained(run,path),regression/path.name)
    raw=regression/'raw-oas'; raw.mkdir()
    for actor in ('admin','editor','reader'):
        path=run/'raw-oas'/f'{actor}.json'
        if path.is_file():shutil.copyfile(contained(run,path),raw/path.name)
    designed_path=work/'designed/designed-report.json'
    if not designed_path.is_file():return
    designed=load(designed_path)
    for case in designed['cases']:
        for step in case['steps']:
            ref=step.get('response_artifact')
            if ref:
                if not re.fullmatch(r'python-http/response-[0-9]+\.json',ref):
                    raise ValueError('UNSAFE_DESIGNED_RESPONSE_REF')
                target=regression/ref;target.parent.mkdir(exist_ok=True)
                shutil.copyfile(contained(work/'designed',work/'designed'/ref),target)


def pack(run, work, dest):
    dest.mkdir(parents=True)
    raw = dest/'raw-oas'; raw.mkdir()
    metadata = []
    exports = [json.loads(line) for line in (work/'export/scenario-trace.ndjson').read_text().splitlines()]
    for actor in ('admin','editor','reader','anonymous'):
        rows = [row for row in exports if row['method']=='GET' and row['path']=='/server/specs/oas' and row['actor']==actor]
        if len(rows) != 1 or rows[0]['curl_exit_code'] or rows[0].get('trace_version') != 2:
            raise ValueError('MISSING_ACTOR_SCHEMA_EXPORT')
        row = rows[0]
        body = (work/'schemas/r06-k05-v2'/f'{actor}.json').read_bytes()
        captured = contained(work/'export', work/'export'/row['response_ref']).read_bytes()
        if body != captured:
            raise ValueError('ACTOR_SCHEMA_EXPORT_MISMATCH')
        (raw/f'{actor}.json').write_bytes(body)
        metadata.append(dict(actor=actor, authorization_sent=actor!='anonymous', status=row['status'],
                             content_type=row['content_type'], observed_at=row['recorded_at'], sha256=hashlib.sha256(body).hexdigest()))
    save(dest/'schema-metadata.json', metadata)
    scenarios = work/'scenarios'
    rows = [json.loads(line) for line in (scenarios/'scenario-trace.ndjson').read_text().splitlines()]
    trace = validate(rows, scenarios, require_contract_metadata=True)
    http = dest/'http'; http.mkdir()
    for row in trace:
        shutil.copyfile(contained(scenarios, scenarios/row['response_ref']), http/row['response_ref'])
        row['response_ref'] = 'http/'+row['response_ref']
    save(dest/'trace.json', trace)
    for name in ('scenario-report.json','scenario-outcomes.json','database-oracle.json','baseline-articles.json','baseline-categories.json'):
        shutil.copyfile(scenarios/name, dest/name)
    verification = [row for row in rows if row['scenario']=='VERIFY']
    if len(verification) != 2:
        raise ValueError('MISSING_RESTORE_VERIFICATION')
    for row in verification:
        body = contained(scenarios, scenarios/row['response_ref']).read_bytes()
        coll = row['path'].split('?')[0].split('/')[2]
        if coll not in ('qa_articles','qa_categories') or row['status'] != 200 or row['curl_exit_code']:
            raise ValueError('INVALID_RESTORE_VERIFICATION')
        before = load(scenarios/('baseline-'+coll[3:]+'.json'))['data']
        if sorted(json.loads(body)['data'], key=lambda r:r['id']) != sorted(before,key=lambda r:r['id']):
            raise ValueError('BASELINE_CHANGED')
        (http/row['response_ref']).write_bytes(body)
        row['response_sha256'] = hashlib.sha256(body).hexdigest()
        row['response_ref'] = 'http/'+row['response_ref']
    save(dest/'verification-trace.json', verification)


def execute(key, *, remote=False, preflight_only=False, replay_key=None):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}',key):
        raise ValueError('INVALID_CI_KEY')
    if remote:
        require_remote_context()
    if replay_key and (remote or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}',replay_key)):
        raise ValueError('REPLAY_REQUIRES_LOCAL_SNAPSHOT')
    base = ROOT/'artifacts/runs/m2-ci'/key
    base.mkdir(parents=True,exist_ok=False)
    # Staging stays in ignored runtime and is NEVER an upload wildcard.
    stage = ROOT/'runtime/ci-m2'/key
    stage.mkdir(parents=True,exist_ok=False)
    report = dict(task='M2_CI', key=key, mode='GITHUB_ACTIONS' if remote else 'LOCAL_REHEARSAL',
                  remote_CI='RUNNING' if remote else 'NOT_RUN', started_at=datetime.now(timezone.utc).isoformat(),
                  regression='NOT_RUN', diagnostic='NOT_RUN', cleanup='UNVERIFIED', final_exit_code=2,
                  seed='NOT_RUN', campaign='NOT_RUN', execution_coverage='NOT_MEASURED', new_canonical_tests=0)
    private = ROOT/'runtime/profiles'/NS/'p09.env'
    secrets = []
    try:
        report['source']=source_state()
        report['github'] = {k:os.environ.get(k) for k in ('GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_SHA','GITHUB_REF','RUNNER_NAME','RUNNER_OS','RUNNER_ARCH')} if remote else {}
        if remote:
            check_remote_source(report['source'],os.environ.get('GITHUB_SHA'))
        if subprocess.run(['git','check-ignore','-q',str(private)],cwd=ROOT).returncode != 0:
            raise ValueError('PRIVATE_PROFILE_NOT_IGNORED')
        if subprocess.run(['git','ls-files','--error-unmatch',str(private)],cwd=ROOT,capture_output=True).returncode == 0:
            raise ValueError('PRIVATE_PROFILE_TRACKED')
        report['private_profile_access']=check_private_profile(private)
        secrets=secret_values(private)
        code = subprocess.run([sys.executable,'-B','scripts/p09_runtime.py','--namespace',NS,'--report',str(stage/'preflight.json')],cwd=ROOT,capture_output=True,timeout=180).returncode
        report['preflight_exit_code'] = code
        if code or load(stage/'preflight.json')['status']!='READY':
            raise ValueError('PREFLIGHT_BLOCKED')
        report['preflight'] = 'READY'
        if preflight_only:
            report.update(cleanup='NOT_REQUIRED_NO_MUTATION',final_exit_code=0,task_status='PREFLIGHT_ONLY_READY')
        else:
            run_id = 'P10-'+datetime.now().strftime('%Y%m%d')+'-'+key
            if replay_key:
                source=ROOT/'artifacts/runs/m2-ci'/replay_key/'public/ci-summary.json'
                previous=load(source)
                run_id=previous['regression_run_id']
                if not re.fullmatch(r'P10-[0-9]{8}-[A-Za-z0-9-]+',run_id):
                    raise ValueError('INVALID_REPLAY_SOURCE')
                report['evidence_resume']={'source':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                                           'regression_rerun':False,'original_regression_exit_code':previous['regression_exit_code']}
            report['regression_run_id'] = run_id
            code = previous['regression_exit_code'] if replay_key else subprocess.run([sys.executable,'-B','scripts/p10_regression.py','--namespace',NS,'--run-id',run_id,'--http-trace'],cwd=ROOT,capture_output=True,timeout=1050).returncode
            report['regression_exit_code'] = code
            run = ROOT/'docs/coverage/runs'/run_id
            collect_regression(run,ROOT/'runtime/profiles'/NS/run_id,stage/'regression')
            report['regression'] = regression_state(load(run/'run-report.json'),code)
            if report['regression']=='HARNESS_INFRA_OR_CLEANUP_ERROR':
                raise ValueError('REGRESSION_INCOMPLETE')
            pack(run,ROOT/'runtime/profiles'/NS/run_id,stage/'contract-capture')
            profile = load(p09.PROFILE)
            # Offline check only. Capture may FAIL; never skip this after TC13 exit 1.
            result = subprocess.run(['docker','run','--rm','--network','none',
                 '--mount',f'type=bind,src={ROOT / "scripts"},dst=/work/scripts,readonly',
                 '--mount',f'type=bind,src={stage / "contract-capture"},dst=/work/capture,readonly',
                 '--entrypoint','python3',profile['services']['runner']['image'],
                 '/work/scripts/check_scenario_contracts.py','/work/capture'],capture_output=True,timeout=120)
            report['diagnostic_process_exit_code'] = result.returncode
            if result.returncode:
                raise ValueError('DIAGNOSTIC_PROCESS_FAILED')
            diagnostic = json.loads(result.stdout)
            save(stage/'contract-diagnostics.json',diagnostic)
            states = {row['contract_verdict'] for row in diagnostic['records']}
            report['diagnostic'] = 'NOT_MEASURED' if not states or states-{'PASS','FAIL'} else 'FAIL' if 'FAIL' in states else 'PASS'
    except Exception as error:
        # Do not serialize exception text/child stdout: may contain credentials.
        report['harness_error'] = type(error).__name__
        allowed = {'PRIVATE_PROFILE_NOT_IGNORED','PRIVATE_PROFILE_TRACKED','CI_SOURCE_NOT_COMMITTED',
                   'PREFLIGHT_BLOCKED','REGRESSION_INCOMPLETE','DIAGNOSTIC_PROCESS_FAILED',
                   'MISSING_ACTOR_SCHEMA_EXPORT','ACTOR_SCHEMA_EXPORT_MISMATCH','BASELINE_CHANGED','CI_REVISION_MISMATCH','BLOCKED_PRIVATE_ACL'}
        report['harness_reason'] = str(error) if str(error) in allowed else 'SEE_STAGE_EVIDENCE'
        report['task_status'] = 'BLOCKED_HARNESS_INFRA_OR_EVIDENCE'
    finally:
        if report.get('regression_run_id'):
            # Read-only finalizer. Do not broadly restore/reset a shared baseline.
            try:
                profile = load(p09.PROFILE); p09.owned_resources(NS,profile)
                values = p09.private_values(private,NS,False)
                after = p09.verify(p09.API(),values,ROOT/'runtime/profiles'/NS)
                save(stage/'cleanup-verification.json',after)
                run = ROOT/'docs/coverage/runs'/report['regression_run_id']
                rr = load(run/'run-report.json')
                report['cleanup'] = 'PASS' if all(after['checks'].values()) and rr.get('cleanup')=='passed' and rr.get('execution_complete') is True else 'UNVERIFIED'
            except Exception:
                report['cleanup'] = 'UNVERIFIED'
            report['final_exit_code'] = final_code(report['regression'],report['diagnostic'],report['cleanup']) if 'harness_error' not in report else 2
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        if remote:
            report['remote_CI'] = 'EXECUTED_UPLOAD_PENDING'
        save(stage/'ci-summary.json',report)
        try:
            publish(stage,base/'public',secrets)
        except Exception:
            # No partial raw publication. Fail closed, publish only fixed safe error.
            report['final_exit_code']=2
            save(base/'publication-error.json',{'state':'BLOCKED_ARTIFACT_SAFETY','exit_code':2})
            safe = base/'public'
            safe.mkdir(exist_ok=True)
            save(safe/'ci-summary.json',{'state':'BLOCKED_ARTIFACT_SAFETY','final_exit_code':2,'publication_complete':False})
        print(json.dumps({k:report[k] for k in ('key','regression','diagnostic','cleanup','final_exit_code')}))
    return report['final_exit_code']


def finalize(key, *, remote=False):
    """Always-step: read-only postcondition, including interrupted/missing runs."""
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}',key):
        raise ValueError('INVALID_CI_KEY')
    public = ROOT/'artifacts/runs/m2-ci'/key/'public'
    contained(ROOT,public)
    public.mkdir(parents=True,exist_ok=True)
    result = {'mode':'READ_ONLY_WORKFLOW_FINALIZER','cleanup':'UNVERIFIED',
              'automatic_reset_or_broad_restore':False,'interrupted_run':'CHUA_XAC_MINH'}
    code = 2
    try:
        if remote:
            require_remote_context()
            check_remote_source(source_state(),os.environ.get('GITHUB_SHA'))
        private = ROOT/'runtime/profiles'/NS/'p09.env'
        check_private_profile(private)
        secrets = secret_values(private)
        profile=load(p09.PROFILE); p09.owned_resources(NS,profile)
        after=p09.verify(p09.API(),p09.private_values(private,NS,False),private.parent)
        summary=load(public/'ci-summary.json')
        result['runtime_checks']=after
        if all(after['checks'].values()) and summary.get('cleanup')=='PASS':
            result.update(cleanup='PASS',interrupted_run=False)
            code=0
        result['pipeline_exit_code']=summary.get('final_exit_code',2)
        safe_bytes(json.dumps(result).encode(),secrets)
    except Exception:
        result={'mode':'READ_ONLY_WORKFLOW_FINALIZER','cleanup':'UNVERIFIED',
                'state':'BLOCKED_MISSING_OR_UNSAFE_EVIDENCE','automatic_reset_or_broad_restore':False}
    save(public/'workflow-finalizer.json',result)
    save(public/'artifact-index.json',{p.relative_to(public).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
                                      for p in public.rglob('*') if contained(public,p).is_file() and p.name!='artifact-index.json'})
    print(json.dumps({'finalizer_exit_code':code,'cleanup':result['cleanup']}))
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key',required=True)
    parser.add_argument('--remote',action='store_true')
    parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--finalize',action='store_true',help='Read-only always-step; never reset/restore')
    parser.add_argument('--replay-key',help='Local evidence-only continuation: reuse recorded regression, no SUT tests rerun')
    args = parser.parse_args()
    raise SystemExit(finalize(args.key,remote=args.remote) if args.finalize else execute(args.key,remote=args.remote,preflight_only=args.preflight_only,replay_key=args.replay_key))
