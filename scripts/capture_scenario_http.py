"""Bounded S1-S6 capture on the verified P09 lab; no seed/reset/campaign."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from datetime import datetime, timezone
from urllib.request import Request
from urllib.error import HTTPError
import p09_runtime as p09
from scenario_trace import validate


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')


def main(run_id):
    if not re.fullmatch(r'P15-HTTP-[0-9]{8}-[0-9]{2}',run_id):
        raise ValueError('INVALID_CAPTURE_RUN_ID')
    root=p09.ROOT; ns='r06-k05-p09-20261115-audit01'
    out=root/'docs/coverage/acceptance'/run_id; out.mkdir(exist_ok=False)
    runtime=root/'runtime/profiles'/ns; work=runtime/run_id; work.mkdir()
    previous=root/'docs/coverage/acceptance/P15-TRACE-20261116-01'
    selection=json.loads((previous/'selection-manifest.json').read_bytes())
    selection.update(selection_id=run_id,run_ids=[run_id,'P10-20261116-02'])
    selection['execution_ids']=[run_id+'-'+t['canonical_test_id'] if t['canonical_test_id'] in {f'S{i}' for i in range(1,7)}
                                else 'P10-20261116-02-'+t['canonical_test_id'] for t in selection['tests']]
    save(out/'selection-manifest.json',selection)
    save(out/'source-hashes.json',{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in
                                   ('scripts/lab-components.sh','scripts/p09_runtime.py','scripts/scenario_trace.py','scripts/capture_scenario_http.py')})
    profile=json.loads(p09.PROFILE.read_bytes()); p09.owned_resources(ns,profile)
    credentials=p09.private_values(runtime/'p09.env',ns,False)
    before=p09.verify(p09.API(),credentials,runtime); save(out/'preflight-before.json',before)
    if not all(before['checks'].values()):raise RuntimeError('PREFLIGHT_FAILED')
    api=p09.API(); metadata=[]; oas=out/'raw-oas'; oas.mkdir()
    for actor in ('admin','editor','reader','anonymous'):
        token=api.login(actor,credentials['P09_'+actor.upper()+'_PASSWORD']) if actor!='anonymous' else None
        headers={'Authorization':'Bearer '+token} if token else {}
        try:
            with api.opener.open(Request(p09.URL+'/server/specs/oas',headers=headers),timeout=20) as res:
                status,content_type,raw=res.status,res.headers.get('Content-Type',''),res.read()
        except HTTPError as error:
            status,content_type,raw=error.code,error.headers.get('Content-Type',''),error.read()
        (oas/(actor+'.json')).write_bytes(raw)
        metadata.append(dict(actor=actor,authorization_sent=bool(token),status=status,content_type=content_type,
                             observed_at=datetime.now(timezone.utc).isoformat(),sha256=hashlib.sha256(raw).hexdigest()))
    save(out/'schema-metadata.json',metadata)
    if any(m['status']!=200 for m in metadata if m['actor'] in ('editor','reader')):
        raise RuntimeError('REQUIRED_ACTOR_SCHEMA_UNAVAILABLE')
    code=p09.seed_fixture(ns,credentials,runtime,profile,component='p10-scenarios',output=work,trace=True,run_id=run_id)
    save(out/'runner-outcome.json',dict(run_id=run_id,exit_code=code,TC13='NOT_RERUN',campaign='NOT_RUN'))
    after=p09.verify(p09.API(),credentials,runtime); save(out/'preflight-after.json',after)
    rows=[json.loads(line) for line in (work/'scenario-trace.ndjson').read_text(encoding='utf-8').splitlines()]
    trace=validate(rows,work,require_contract_metadata=True)
    public=out/'http'; public.mkdir()
    for row in trace:
        shutil.copyfile(work/row['response_ref'],public/row['response_ref'])
        row['response_ref']='http/'+row['response_ref']
    save(out/'trace.json',trace)
    for name in ('scenario-report.json','scenario-outcomes.json','database-oracle.json','baseline-articles.json','baseline-categories.json'):
        if (work/name).exists():shutil.copyfile(work/name,out/name)
    verification=[row for row in rows if row['scenario']=='VERIFY']
    for row in verification:
        shutil.copyfile(work/row['response_ref'],public/row['response_ref']); row['response_ref']='http/'+row['response_ref']
        collection='articles' if '/qa_articles' in row['path'] else 'categories'
        if json.loads((out/row['response_ref']).read_bytes())['data']!=json.loads((out/('baseline-'+collection+'.json')).read_bytes())['data']:
            raise RuntimeError('BASELINE_SNAPSHOT_MISMATCH')
    save(out/'verification-trace.json',verification)
    save(out/'capture-summary.json',{'run_id':run_id,'scenario_records':len(trace),'trace_version':2,
          'runner_exit_code':code,'cleanup':'PASS' if (work/'scenario-outcomes.json').exists() and all(after['checks'].values()) else 'UNVERIFIED',
          'historical_reports_modified':False,'new_canonical_tests':0,'new_selected_execution_ids':6})
    print(json.dumps({'run_id':run_id,'scenario_records':len(trace),'runner_exit':code,'post_preflight':all(after['checks'].values())}))
    return code if all(after['checks'].values()) else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--run-id',required=True)
    raise SystemExit(main(parser.parse_args().run_id))
