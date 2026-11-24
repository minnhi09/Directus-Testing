"""Read-only project inventory; writes only Phase 0 documentation/local backup."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / 'DAMH'
RUNS = REPO / 'artifacts/runs'
OUT = ROOT / 'output/phase0-20261018'
DOC = REPO / 'docs/hoan-thien'
assert not OUT.exists(), 'Use a new checkpoint directory; do not overwrite an existing snapshot.'
OUT.mkdir(parents=True)
DOC.mkdir(parents=True, exist_ok=True)

def git(repo, *args):
    return subprocess.check_output(
        ['git', '--no-optional-locks', '-c', f'safe.directory={repo.as_posix()}',
         '-c', 'core.quotepath=false', '-C', str(repo), *args],
        stderr=subprocess.PIPE,
    ).decode('utf-8').rstrip('\r\n')

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def pick(value, keys):
    return {k: value[k] for k in keys if k in value}

def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

pre_git = {
    'repository': REPO.as_posix(),
    'head': git(REPO, 'rev-parse', 'HEAD'),
    'branch': git(REPO, 'branch', '--show-current'),
    'status_before_phase0_outputs': git(REPO, 'status', '--porcelain=v1', '-uall').splitlines(),
    'diff_numstat': git(REPO, 'diff', '--numstat').splitlines(),
    'diff_summary': git(REPO, 'diff', '--summary').splitlines(),
    'staged_paths': git(REPO, 'diff', '--cached', '--name-only').splitlines(),
    'directus_head': git(ROOT / 'directus', 'rev-parse', 'HEAD'),
    'directus_status': git(ROOT / 'directus', 'status', '--porcelain=v1').splitlines(),
}
write_json(OUT / 'git-state-before.json', pre_git)

# Preserve tracked/nonignored project files, excluding local-only instructions/plans.
# Ignored .env, raw HTTP/log/event files, .git and mnhy are never enumerated here.
names = set(git(REPO, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split('\0'))
excluded = {'AGENTS.md', '01_ke_hoach_trien_khai_R06_K05.md'}
capture = [REPO / n for n in sorted(names) if n and n not in excluded and (REPO / n).is_file()]
helper_names = ['run-lab.ps1', 'verify-lab.ps1', 'verify-k05.ps1', 'jq', 'jq.exe',
                'jq-sha256sum.txt', 'check-acl.sh', 'check-runtime-profile.sh',
                'expected-fixture.json', 'expected-fixture.sh', 'unicode-check.sh',
                'rebuild-inventory.sh']
capture += [ROOT / 'tmp/lab-tools' / n for n in helper_names if (ROOT / 'tmp/lab-tools' / n).is_file()]
capture += list((REPO / 'runtime').rglob('*.json'))
for path in capture:
    assert path.resolve().is_relative_to(ROOT)
    assert path.name != 'lab.env'
    assert '.git' not in path.relative_to(ROOT).parts
    if path.suffix.lower() in {'.md', '.json', '.yaml', '.yml', '.sh', '.py', '.ps1', '.example'} or path.name == 'jq':
        content = path.read_text(encoding='utf-8-sig')
        suspicious = re.search(r'\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', content)
        assert not suspicious, f'Review possible credential before capture: {path.relative_to(ROOT)}'

snapshot_files = []
with zipfile.ZipFile(OUT / 'checkpoint.zip', 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(set(capture)):
        rel = p.relative_to(ROOT).as_posix()
        archive.write(p, rel)
        snapshot_files.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': sha(p)})
write_json(OUT / 'checkpoint-manifest.json', {
    'schema': 1, 'client_date': '2026-10-18', 'timezone': 'Asia/Bangkok',
    'kind': 'local_file_snapshot_before_phase0_document_updates',
    'not_a_git_commit_or_database_backup': True,
    'excludes': ['config/lab.env', '.git', 'mnhy', 'raw artifacts/runs', *sorted(excluded)],
    'archive_sha256': sha(OUT / 'checkpoint.zip'),
    'files': snapshot_files,
})

selected = {
    '20261013T040059Z-1536': 'reference_doctor_latest',
    '20261013T035929Z-1688': 'reference_up_latest',
    '20261012T191100Z-757': 'reference_seed_after_campaign',
    '20261012T222250Z-1431': 'reference_smoke_latest',
    '20261012T185734Z-1667': 'reference_actor_schema_export',
    '20261012T222311Z-1412': 'reference_scenarios_latest',
    '20261012T185934Z-1453': 'reference_invariants',
    '20261012T185942Z-1219': 'reference_aggregate_finding',
    '20261012T185950Z-1994': 'reference_contract_finding',
    '20261012T185958Z-355': 'reference_windows_raw_pilot',
    '20261012T190350Z-1047': 'reference_windows_guided_pilot',
    '20261012T190820Z-1761': 'reference_windows_raw_post_fix_short',
    '20261012T190912Z-1225': 'reference_windows_guided_post_fix_short',
    '20261012T191034Z-777': 'reference_delete_replay',
    '20261012T112746Z-20300': 'historical_long_campaign_raw',
    '20261012T122826Z-22781': 'historical_long_campaign_guided_interrupted',
    '20261011T085034Z-76481': 'historical_v2_raw',
    '20261011T095117Z-89079': 'historical_v2_guided',
}
rows, campaign_rows, selected_rows, errors = [], [], [], []
evidence_hashes = []
meta_keys = ['run_id', 'command', 'status', 'exit_code', 'started_at', 'finished_at',
             'duration_seconds', 'harness_sha', 'working_tree', 'runtime_profile',
             'fixture_version', 'actor', 'schema_hash', 'seed']

def group(m, has_metadata):
    if not has_metadata:
        return 'manual_repair_without_run_metadata'
    if m.get('runtime_profile') == 'windows-20261013-oig':
        return 'windows_post_oig'
    if m.get('runtime_profile') == 'windows-20261013':
        return 'windows_pre_oig'
    if m.get('fixture_version') == 'r06-k05-v1':
        return 'historical_fixture_v1'
    if m.get('fixture_version') == 'r06-k05-v2':
        return 'historical_fixture_v2_no_runtime_profile'
    return 'interface_environment_or_unspecified_fixture'

for directory in sorted(p for p in RUNS.iterdir() if p.is_dir()):
    rid = directory.name
    mp = directory / 'metadata.json'
    m = load(mp) if mp.exists() else {}
    budget = m.get('budget')
    if isinstance(budget, str):
        try: budget = json.loads(budget)
        except ValueError: errors.append({'run_id': rid, 'note': 'legacy_text_budget_not_json'}); budget = {}
    budget = budget or {}
    row = {'run_id': rid, 'group': group(m, mp.exists()), 'selected_role': selected.get(rid, ''),
           **{k: m.get(k, '') for k in meta_keys if k != 'run_id'},
           'budget_raw': m.get('budget'),
           'max_time_seconds': budget.get('max_time_seconds', ''),
           'max_examples_per_operation': budget.get('max_examples_per_operation', ''),
           'workers': budget.get('workers', ''), 'rate_limit': budget.get('rate_limit', ''),
           'request_timeout_seconds': budget.get('request_timeout_seconds', ''),
           'baseline_images': json.dumps(pick(m.get('baseline', {}), ['directus_image', 'postgres_image', 'schemathesis_image']), ensure_ascii=False),
           'metadata_present': mp.exists(), 'run_log_present': (directory / 'run.log').exists(),
           'scenario_report_present': (directory / 'scenario-report.json').exists(),
           'invariant_report_present': (directory / 'invariant-report.json').exists(),
           'campaign_index_present': (directory / 'campaign-index.json').exists(),
           'artifact_path': directory.relative_to(REPO).as_posix()}
    sr = directory / 'scenario-report.json'
    ir = directory / 'invariant-report.json'
    if sr.exists():
        counts = collections.Counter(x.get('status', 'unknown') for x in load(sr).get('scenarios', []))
        row['scenario_counts'] = json.dumps(dict(counts), sort_keys=True)
    if ir.exists(): row['invariant_counts'] = json.dumps(load(ir).get('summary', {}), sort_keys=True)
    rows.append(row)
    cp = directory / 'campaign-index.json'
    campaigns = load(cp).get('campaigns', []) if cp.exists() else []
    for c in campaigns:
        st = c.get('schemathesis') or {}
        prof = load(cp).get('profile')
        sd = directory / prof / f"seed-{c.get('seed')}"
        cr = {'run_id': rid, 'group': row['group'], 'selected_role': row['selected_role'],
              'profile': prof, 'harness_sha': m.get('harness_sha'), 'working_tree': m.get('working_tree'),
              'actor': m.get('actor'), 'fixture_version': m.get('fixture_version'),
              'seed': c.get('seed'), **pick(c, ['status', 'termination', 'runner_exit_code', 'restore_exit_code', 'schema_sha256']),
              **pick(c.get('budget', {}), ['max_time_seconds', 'max_examples_per_operation', 'workers', 'rate_limit', 'request_timeout_seconds']),
              'operations_tested': st.get('operations', {}).get('tested'),
              **pick(st.get('test_cases', {}), ['generated', 'with_failures', 'unique_failures', 'errored']),
              'running_time': st.get('running_time'), 'seed_artifact_path': sd.relative_to(REPO).as_posix()}
        for fname in ['schemathesis-report.json', 'schemathesis-events.ndjson', 'schemathesis-coverage.json', 'campaign-summary.json', 'operation-inventory.json', 'metrics.json']:
            cr[fname + '_present'] = (sd / fname).exists()
        mf = sd / 'schema-manifest.json'
        if mf.exists():
            sm = load(mf)
            cr['source_schema_sha256'] = sm.get('source_sha256')
            scoped = sd / f'schema-{prof}.json'
            cr['scoped_schema_hash_verified'] = scoped.exists() and sha(scoped) == c.get('schema_sha256') == sm.get('scoped_sha256')
        campaign_rows.append(cr)
    if rid in selected:
        v = {'role': selected[rid], 'metadata': pick(m, meta_keys), 'budget': budget,
             'baseline': pick(m.get('baseline', {}), ['directus_image', 'postgres_image', 'schemathesis_image'])}
        if sr.exists(): v['scenarios'] = [pick(x, ['id', 'name', 'status', 'expected', 'actual', 'details']) for x in load(sr).get('scenarios', [])]
        if ir.exists():
            im = load(ir)
            v['invariant_summary'] = im.get('summary')
            v['cases'] = [pick(x, ['id', 'name', 'status', 'expected', 'actual']) for x in im.get('cases', [])]
        if campaigns: v['campaigns'] = [x for x in campaign_rows if x['run_id'] == rid]
        rp = directory / 'reproducer-schemathesis-j0ZjQ0.json'
        if rp.exists(): v['replay'] = pick(load(rp), ['case_id', 'actor', 'status', 'replay_scope', 'actual_status', 'expected_status', 'source_status', 'restore_exit_code'])
        selected_rows.append(v)
        # Hash selected authoritative files without copying raw HTTP, token-bearing logs or events.
        paths = [mp, sr, ir, cp, directory/'schema-manifest.json', directory/'contract-validation.json']
        paths += list(directory.glob('reproducer-*.json'))
        for c in campaigns:
            sd = directory / load(cp)['profile'] / f"seed-{c.get('seed')}"
            paths += [sd/n for n in ['schema-manifest.json', f"schema-{load(cp)['profile']}.json", 'campaign-summary.json', 'schemathesis-report.json', 'schemathesis-coverage.json', 'operation-inventory.json', 'metrics.json']]
        for f in paths:
            if f.is_file(): evidence_hashes.append({'path': f.relative_to(REPO).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)})

fields = list(dict.fromkeys(k for row in rows for k in row))
write_csv(DOC/'00-evidence-index.csv', rows, fields)
fields = list(dict.fromkeys(k for row in campaign_rows for k in row))
write_csv(DOC/'00-campaign-index.csv', campaign_rows, fields)
write_json(DOC/'00-selected-evidence.json', {'schema': 1, 'client_date': '2026-10-18', 'kind': 'read_only_extract_not_a_new_test_run', 'selected': selected_rows})
write_json(DOC/'00-evidence-hashes.json', {'schema': 1, 'scope': 'selected_original_evidence_files_only', 'files': evidence_hashes})

schemas = []
for p in sorted((REPO/'runtime').rglob('*.json')):
    if p.name not in {'admin.json','editor.json','reader.json','anonymous.json'}: continue
    value = load(p)
    methods = {'get','post','patch','delete','put','head','options','trace'}
    qa_ops = [(method.upper(), path) for path,item in value.get('paths',{}).items()
              if path.startswith('/items/qa_') for method in item if method in methods]
    schemas.append({'path':p.relative_to(REPO).as_posix(), 'sha256':sha(p), 'qa_operation_count':len(qa_ops)})
write_json(DOC/'00-schema-inventory.json', {'schema':1,'scope':'qa_* operation count, not all system endpoints','snapshots':schemas})
summary = {
    'client_date':'2026-10-18','timezone':'Asia/Bangkok',
    'run_directories':len(rows), 'with_metadata':sum(r['metadata_present'] for r in rows),
    'groups':dict(collections.Counter(r['group'] for r in rows)),
    'statuses':dict(collections.Counter(r.get('status') or 'no_metadata' for r in rows)),
    'campaign_seed_rows':len(campaign_rows),'selected_runs':len(selected_rows),
    'selected_evidence_files_hashed':len(evidence_hashes),
    'schema_snapshots':len(schemas),'snapshot_files':len(snapshot_files),
    'archive_bytes':(OUT/'checkpoint.zip').stat().st_size,
    'original_untracked_files':sum(x.startswith('?? ') for x in pre_git['status_before_phase0_outputs']),
    'legacy_format_notes':errors,
    'live_runtime_check':{'status':'not_verified','method':'docker ps --filter label=com.docker.compose.project=r06-k05',
                          'observation':'Docker config access denied and docker_engine named pipe unavailable in this execution context; not proof that the user machine daemon is stopped.'},
}
write_json(DOC/'00-inventory-summary.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
