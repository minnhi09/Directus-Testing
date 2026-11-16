"""P10 only: isolated regression13; preserve failures and immutable run snapshots."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2)+'\n',encoding='utf-8')


def inside():
    from invariants import Lab
    from designed_cases import Runner, catalogue, select_cases
    run = Path('/work/run')
    lab = Lab(run); lab.authenticate(); lab.load_fixture()

    class OwnedRunner(Runner):
        def __init__(self, *args):
            super().__init__(*args); self.owned = {'qa_articles':set(), 'qa_categories':set()}

        def request(self, method, path, actor='editor', body=None):
            collection = path.split('?')[0].split('/')[2] if path.startswith('/items/') else None
            if method in ('POST','PATCH','DELETE'):
                if collection not in self.owned:
                    raise RuntimeError('Mutation outside fixture allowlist')
                if method != 'POST' and int(path.split('?')[0].split('/')[-1]) not in self.owned[collection]:
                    raise RuntimeError('Mutation target not created by this run')
            response = super().request(method,path,actor,body)
            if method=='POST' and collection in self.owned and 200 <= response.status < 300:
                data = response.body.get('data')
                for row in data if isinstance(data,list) else [data]:
                    if isinstance(row,dict) and isinstance(row.get('id'),int): self.owned[collection].add(row['id'])
            return response

        def cleanup(self, before):
            current = self.snapshot()
            for coll,rows in current.items():
                extras = {r['id'] for r in rows} - {r['id'] for r in before[coll]}
                if not extras <= self.owned[coll]:
                    raise RuntimeError('Unknown rows detected; refuse broad cleanup')
            super().cleanup(before)

    runner = OwnedRunner(lab,run,600); runner.preflight()
    report={'cases':[], 'execution_complete':False, 'runner_exit_code':1}
    selected=select_cases(catalogue(),'course',None,None)
    for design in selected:
        result=runner.run_case(design); report['cases'].append(result)
        save(run/'designed-report.json',report)
        if result['cleanup_status']!='passed' or result['status'] in ('blocked','incomplete'):
            break
    report['execution_complete']=len(report['cases'])==7
    report['runner_exit_code']=0 if report['execution_complete'] and all(c['status']=='passed' for c in report['cases']) else 1
    save(run/'designed-report.json',report)
    return report['runner_exit_code']


def main(ns, run_id, resume=False, http_trace=False):
    import p09_runtime as p09
    from p10_selection import validate, BASE
    p09.namespace(ns)
    if not __import__('re').fullmatch(r'P10-[0-9]{8}-[A-Za-z0-9-]+',run_id):
        raise ValueError('Invalid P10 run ID')
    root=p09.ROOT; out=root/'docs/coverage/runs'/run_id
    if resume and (out/'designed-report.json').exists():
        raise ValueError('Designed execution already recorded; use a new run ID')
    out.mkdir(exist_ok=resume)
    baseline=json.loads(BASE.read_text(encoding='utf-8')); selection=json.loads(BASE.read_text(encoding='utf-8'))
    selection.update(selection_id=run_id,run_ids=[run_id],execution_ids=[run_id+'-'+t['canonical_test_id'] for t in selection['tests']],locked_at=datetime.now(timezone.utc).isoformat())
    if resume:
        selection=json.loads((out/'selection-manifest.json').read_text(encoding='utf-8'))
    validate(selection,baseline)
    if not resume: save(out/'selection-manifest.json',selection)
    runtime=root/'runtime/profiles'/ns
    profile=json.loads(p09.PROFILE.read_text(encoding='utf-8')); owned=p09.owned_resources(ns,profile)
    private=p09.private_values(runtime/'p09.env',ns,False)
    report={'run_id':run_id,'baseline_id':selection['baseline_id'],'source_pin':'4f77933bf9551cac6b289576078783e189b8f4e3',
        'image_digest':profile['services']['directus']['image'],'harness_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'worktree':'DIRTY','namespace':ns,'host_url':p09.URL,'remote_ci':'NOT_RUN','coverage':'NOT_MEASURED',
        'started_at':datetime.now(timezone.utc).isoformat(),'cases':[],'status':'BLOCKED'}
    if resume: shutil.copyfile(out/'run-report.json',out/'run-report-before-resume.json')
    save(out/'run-report.json',report)
    before=p09.verify(p09.API(),private,runtime); save(out/'preflight-before.json',before)
    if not all(before['checks'].values()): raise RuntimeError('P09 gates failed')
    work=runtime/run_id; work.mkdir(exist_ok=resume)
    shutil.copyfile(runtime/'fixture-ids.json',work/'fixture-ids.json')
    stages=work/'export'; stages.mkdir(exist_ok=resume)
    code=0 if resume and (work/'schemas/r06-k05-v2/reader.json').exists() else p09.seed_fixture(ns,private,work,profile,component='export-schema',output=stages,trace=http_trace,run_id=run_id if http_trace else None)
    report['schema_export_exit_code']=code
    if code: raise RuntimeError('Schema export failed')
    raw=out/'raw-oas'; raw.mkdir(exist_ok=resume)
    for actor in ('admin','editor','reader'):
        if not (raw/f'{actor}.json').exists(): shutil.copyfile(work/'schemas/r06-k05-v2'/f'{actor}.json',raw/f'{actor}.json')
    report['actor_schema_sha256']={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()}
    scenarios=work/'scenarios'; scenarios.mkdir(exist_ok=resume)
    report['scenarios_exit_code']=0 if resume and (scenarios/'scenario-outcomes.json').exists() else p09.seed_fixture(ns,private,work,profile,component='p10-scenarios',output=scenarios,trace=http_trace,run_id=run_id if http_trace else None)
    for name in ('scenario-report.json','scenario-outcomes.json','database-oracle.json'):
        if (scenarios/name).exists(): shutil.copyfile(scenarios/name,out/name)
    scenario_data=json.loads((scenarios/'scenario-report.json').read_text(encoding='utf-8'))
    report['cases'].extend({'canonical_test_id':c['id'],'status':c['status'],'source':'scenario-report.json'} for c in scenario_data['scenarios'])
    # Verify baseline before allowing a second mutating suite, regardless of case verdict.
    mid=p09.verify(p09.API(),private,runtime)
    if not all(mid['checks'].values()) or not (scenarios/'scenario-outcomes.json').exists():
        report['cleanup']='FAILED_OR_UNVERIFIED'; save(out/'run-report.json',report); return 2
    designed=work/'designed'; designed.mkdir()
    shutil.copyfile(scenarios/'database-oracle.json',designed/'database-oracle.json')
    env=os.environ.copy(); args=['docker','run','--rm','--init','--network',ns+'_network']
    values={'LAB_ROOT_DIR':'/work','LAB_RUN_DIR':'/work/run','LAB_RUNTIME_ROOT':'/work/runtime','LAB_API_URL':'http://directus:8055',
        'LAB_PROJECT_NAME':ns,'LAB_RUN_ID':run_id,'LAB_RATE_LIMIT':'5/s','PYTHONDONTWRITEBYTECODE':'1',
        'LAB_HARNESS_SHA':report['harness_sha']}
    for actor in ('ADMIN','EDITOR','READER'):
        values['LAB_'+actor+'_EMAIL']=actor.lower()+'@example.com'
        values['LAB_'+actor+'_PASSWORD']=private['P09_'+actor+'_PASSWORD']
    for k,v in values.items(): env[k]=v; args.extend(['-e',k])
    for source,target,readonly in [(root/'scripts','/work/scripts',True),(work,'/work/runtime',True),(designed,'/work/run',False)]:
        args.extend(['--mount','type=bind,src='+str(source)+',dst='+target+(',readonly' if readonly else '')])
    args.extend(['--entrypoint','python3',profile['services']['runner']['image'],'/work/scripts/p10_regression.py','--inside'])
    p09.owned_resources(ns,profile)
    result=subprocess.run(args,env=env,capture_output=True,timeout=750)
    report['designed_exit_code']=result.returncode
    if (designed/'designed-report.json').exists():
        data=json.loads((designed/'designed-report.json').read_text(encoding='utf-8'))
        shutil.copyfile(designed/'designed-report.json',out/'designed-report.json')
        report['cases'].extend({'canonical_test_id':c['id'],'status':c['status'],'verdicts':c['verdicts'],'cleanup_status':c['cleanup_status'],'source':'designed-report.json'} for c in data['cases'])
        # Keep response bodies private; copy sanitized case records and referenced triage artifacts separately when reviewed.
    else: report['runner_error']='NO_DESIGNED_REPORT'
    after=p09.verify(p09.API(),private,runtime); save(out/'preflight-after.json',after)
    report.update(cleanup='passed' if all(after['checks'].values()) else 'failed',finished_at=datetime.now(timezone.utc).isoformat(),
                  execution_complete=len(report['cases'])==13)
    for case in report['cases']:
        index=next(i for i,t in enumerate(selection['tests']) if t['canonical_test_id']==case['canonical_test_id'])
        case.update(test_version=selection['tests'][index]['test_version'],execution_id=selection['execution_ids'][index])
    report['status']='FAILED' if any(c['status']=='failed' for c in report['cases']) else 'PASSED' if report['execution_complete'] else 'INCOMPLETE'
    save(out/'run-report.json',report)
    print(json.dumps({'run_id':run_id,'status':report['status'],'cases':len(report['cases']),'cleanup':report['cleanup']}))
    return 0 if report['status']=='PASSED' and report['cleanup']=='passed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inside',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--http-trace',action='store_true',help='Capture schema/scenario metadata for CI diagnostics without repeating S1-S6')
    parser.add_argument('--namespace'); parser.add_argument('--run-id')
    args=parser.parse_args()
    raise SystemExit(inside() if args.inside else main(args.namespace,args.run_id,args.resume,args.http_trace))
