"""One P14 category-module pilot on a run-owned collection and actor.

No old fixture mutations, no raw OAS edits, no dependency installation.
"""
import argparse
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
from datetime import datetime, timezone
import p09_runtime as p09

ROOT=p09.ROOT
NS='r06-k05-p09-20261115-audit01'


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')


def scoped(raw, collection):
    result=copy.deepcopy(raw); prefix='/items/'+collection
    expected={prefix:{'get','post'},prefix+'/{id}':{'get','patch','delete'}}
    result['paths']={path:{key:value for key,value in raw['paths'][path].items() if key in methods or key=='parameters'} for path,methods in expected.items()}
    if any(not methods <= set(result['paths'][path]) for path,methods in expected.items()):
        raise ValueError('Actor OAS lacks selected operation')
    return result


def overlay(raw,collection,ids):
    result=copy.deepcopy(raw); prefix='/items/'+collection
    for path, item in result['paths'].items():
        for method,operation in item.items():
            if method not in ('get','post','patch','delete'): continue
            for param in operation.get('parameters',[]):
                if param.get('in')=='path' and param.get('name')=='id': param['example']=ids[0]
            if method in ('post','patch'):
                operation['requestBody']['content']['application/json']['example']={'name':'P14 valid category'}
    return result


def main(run_id, resume_guided=False):
    if not __import__('re').fullmatch(r'P14-[0-9]{8}-[0-9]{2}',run_id): raise ValueError('Invalid run ID')
    out=ROOT/'docs/coverage/runs'/run_id; out.mkdir(exist_ok=resume_guided)
    if resume_guided and (out/'guided/report.json').exists():
        raise ValueError('Guided execution already recorded; use a new run ID')
    private=ROOT/'runtime/profiles'/NS/run_id; private.mkdir(exist_ok=resume_guided)
    profile=json.loads(p09.PROFILE.read_bytes()); p09.owned_resources(NS,profile)
    creds=p09.private_values(ROOT/'runtime/profiles'/NS/'p09.env',NS,False)
    api=p09.API(); admin=api.login('admin',creds['P09_ADMIN_PASSWORD'])
    pre=p09.verify(p09.API(),creds,ROOT/'runtime/profiles'/NS); save(out/'preflight-before.json',pre)
    assert all(pre['checks'].values())
    collection='qa_sys_categories_'+run_id.lower().replace('-','_')
    path='/items/'+collection
    report={'run_id':run_id,'module':'ITEM/category','selection_basis':'P07 regression13 category binding; P10 P3-ST-01; approved 10 item CRUD pairs',
        'collection':collection,'namespace':NS,'baseline':'M1-REGRESSION-13-v1','sut_version':'12.5.0','source_pin':'4f77933bf9551cac6b289576078783e189b8f4e3',
        'budget':{'source':'plan9.3','seed':101,'max_examples_per_operation':10,'max_time_seconds_per_profile':60,'workers':1,'rate':'2/s','request_timeout':10},
        'actor':'run-owned editor-equivalent category CRUD','allowlist':[(m,p) for p,ms in [(path,['GET','POST']),(path+'/{id}',['GET','PATCH','DELETE'])] for m in ms],
        'started_at':datetime.now(timezone.utc).isoformat(),'profiles':[],'status':'IN_PROGRESS','keyword_coverage':'NOT_MEASURED','remote_ci':'NOT_RUN'}
    if resume_guided:
        previous=json.loads((out/'run-report.json').read_bytes())
        save(out/'run-report-before-guided-resume.json',previous)
        report['profiles']=previous['profiles']
        report['resume_reason']='TypeError serializing restore filename after verified raw restore; raw not rerun'
    else: save(out/'run-config.json',report)
    owned=[]
    def call(method,url,data=None,token=admin):
        code,body=api.call(url,token,data,method=method)
        if not 200 <= code < 300: raise RuntimeError('P14_HTTP_'+str(code))
        return body.get('data')
    def remember(kind,body):
        row=call('POST','/'+kind,body); owned.append((kind,row['id'])); return row['id']
    def snapshot():
        return call('GET',path+'?limit=-1&sort=id&fields=id,name')
    def restore(before):
        # The entire collection is run-owned. Refuse any other collection target.
        assert collection.startswith('qa_sys_categories_p14_')
        for row in snapshot(): call('DELETE',path+'/'+str(row['id']))
        for row in before: call('POST',path,row)
        if snapshot()!=before: raise RuntimeError('RESTORE_MISMATCH')
    try:
        assert api.call('/collections/'+collection,admin)[0] in (403,404)
        call('POST','/collections',{'collection':collection,'meta':{'note':run_id},'schema':{},'fields':[
            {'field':'id','type':'integer','schema':{'is_primary_key':True,'has_auto_increment':True,'is_nullable':False},'meta':{'hidden':True}},
            {'field':'name','type':'string','schema':{'is_nullable':False,'max_length':80},'meta':{'interface':'input','required':True}}]})
        owned.append(('collections',collection))
        role=remember('roles',{'name':run_id,'icon':'science'})
        policy=remember('policies',{'name':run_id,'admin_access':False,'app_access':False})
        remember('access',{'role':role,'policy':policy})
        for action in ('create','read','update','delete'):
            remember('permissions',{'policy':policy,'collection':collection,'action':action,'fields':['*'],'permissions':None,'validation':None,'presets':None})
        password=secrets.token_urlsafe(32); email=run_id.lower()+'@example.com'
        remember('users',{'email':email,'password':password,'role':role,'status':'active'})
        token=api.login(run_id.lower(),password)
        spec=json.loads((ROOT/'scripts/data/fixture-oracle.json').read_bytes())
        for row in spec['categories']: call('POST',path,{'name':row['name']})
        before=snapshot(); save(out/'fixture-map.json',before)
        rawdir=out/'raw-oas'; rawdir.mkdir(exist_ok=resume_guided)
        actor_bytes=None
        # Preserve original bytes, not a reserialized representation.
        from urllib.request import Request
        for actor,t in [('admin',admin),('actor',token)]:
            with api.opener.open(Request(p09.URL+'/server/specs/oas',headers={'Authorization':'Bearer '+t}),timeout=20) as res: rawbytes=res.read()
            target=rawdir/(actor+('-resume' if resume_guided else '')+'.json'); target.write_bytes(rawbytes)
            if actor=='actor': actor_bytes=rawbytes
        report['raw_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in rawdir.iterdir()}
        raw=scoped(json.loads(actor_bytes),collection); guided=overlay(raw,collection,[r['id'] for r in before])
        if resume_guided:
            assert json.loads((out/'schema-raw.json').read_bytes())==raw, 'Resume scoped raw changed'
            assert json.loads((out/'schema-guided.json').read_bytes())==guided, 'Resume guided changed'
        else:
            save(out/'schema-raw.json',raw); save(out/'schema-guided.json',guided)
        (out/'guided.diff').write_text(''.join(difflib.unified_diff((out/'schema-raw.json').read_text().splitlines(True),(out/'schema-guided.json').read_text().splitlines(True),fromfile='raw',tofile='guided')),encoding='utf-8')
        image=profile['services']['runner']['image']
        for args,filename in [(['--version'],'runner-version.txt'),(['run','--help'],'runner-help.txt')]:
            r=subprocess.run(['docker','run','--rm','--entrypoint','schemathesis',image,*args],capture_output=True,timeout=30); assert r.returncode==0; (out/filename).write_bytes(r.stdout)
        env=os.environ.copy(); env['P14_TOKEN']=token
        for flavor in (('guided',) if resume_guided else ('raw','guided')):
            stage=private/flavor; stage.mkdir(); schema=out/('schema-'+flavor+'.json');
            args=['docker','run','--rm','--network',NS+'_network','-e','P14_TOKEN',
                '--mount','type=bind,src='+str(schema)+',dst=/work/schema.json,readonly',
                '--mount','type=bind,src='+str(stage)+',dst=/work/run','--entrypoint','sh',image,'-c',
                'exec schemathesis run /work/schema.json --url http://directus:8055 --workers 1 --max-examples 10 --seed 101 --request-timeout 10 --rate-limit 2/s --max-time 60 --phases examples,fuzzing --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance,unsupported_method,negative_data_rejection,positive_data_acceptance --report json,ndjson --report-json-path /work/run/report.json --report-ndjson-path /work/run/events.ndjson --coverage-format json --coverage-report-json-path /work/run/coverage.json --output-sanitize true --no-color -H "Authorization: Bearer $P14_TOKEN"']
            p09.owned_resources(NS,profile)
            r=subprocess.run(args,env=env,capture_output=True,timeout=100)
            # Exact-value sanitize all public outputs; private generation cache is not exported.
            public=out/flavor; public.mkdir()
            secret_values=[token,password,creds['P09_ADMIN_PASSWORD'],creds['P09_EDITOR_PASSWORD'],creds['P09_READER_PASSWORD']]
            for f in stage.iterdir():
                if f.is_file() and f.name in ('report.json','events.ndjson','coverage.json'):
                    data=f.read_bytes()
                    for value in secret_values: data=data.replace(value.encode(),b'[REDACTED]')
                    (public/f.name).write_bytes(data)
            stdout=r.stdout+r.stderr
            for value in secret_values: stdout=stdout.replace(value.encode(),b'[REDACTED]')
            (public/'console.txt').write_bytes(stdout)
            outcome={'profile':flavor,'exit_code':r.returncode,'reports_present':(public/'report.json').exists(),'restore':'PENDING'}
            report['profiles'].append(outcome); save(out/'run-report.json',report)
            restore(before); outcome['restore']='PASS'; save(out/('restore-'+flavor+'.json'),{'status':'PASS','before':before,'after':snapshot()})
            save(out/'run-report.json',report)
        report['status']='RUNS_FINISHED'
        # Replay of a representative POST/schema mismatch with the original actor OAS.
        row=call('POST',path,{'name':'P14 representative replay'},token)
        response=call('GET',path+'/'+str(row['id']),token=token)
        save(out/'replay-response.json',{'data':row})
        save(out/'replay.json',{'method':'POST','path':path,'body':{'name':'P14 representative replay'},'status':200,'response_file':'replay-response.json','readback_equal':response==row,'expected_raw_data_type':raw['paths'][path]['post']['responses']['200']['content']['application/json']['schema']['properties']['data'].get('type'),'actual_data_type':'object','classification':'SCHEMA_CONTRACT_CANDIDATE','replay_scope':'deterministic representative, recorded-event linkage pending'})
        restore(before); save(out/'restore-replay.json',{'status':'PASS','snapshot':snapshot()})
    except Exception as error:
        report.update(status='BLOCKED_OR_INCOMPLETE',error_type=type(error).__name__,error_code=str(error) if str(error).startswith(('P14_HTTP_','RESTORE_')) else 'SEE_PRIVATE_CONTEXT')
    finally:
        cleanup=[]
        for kind,item_id in reversed(owned):
            try: call('DELETE','/'+kind+'/'+str(item_id)); cleanup.append({'kind':kind,'id':item_id,'status':'PASS'})
            except Exception: cleanup.append({'kind':kind,'id':item_id,'status':'FAIL'})
        report['cleanup']=cleanup; report['finished_at']=datetime.now(timezone.utc).isoformat()
        report['phase_status']='IN_PROGRESS_REVIEW_EVIDENCE'
        save(out/'run-report.json',report)
        after=p09.verify(p09.API(),creds,ROOT/'runtime/profiles'/NS); save(out/'preflight-after.json',after)
        print(json.dumps({'run_id':run_id,'status':report['status'],'profiles':report['profiles'],'cleanup':all(c['status']=='PASS' for c in cleanup)}))
    if report['status']!='RUNS_FINISHED' or not all(c['status']=='PASS' for c in report['cleanup']): return 2
    return 1 if any(p['exit_code'] for p in report['profiles']) else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--run-id',required=True); parser.add_argument('--resume-guided',action='store_true')
    args=parser.parse_args(); raise SystemExit(main(args.run_id,args.resume_guided))
