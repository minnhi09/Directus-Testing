"""Offline only. Run in pinned image, --network none, mounts read-only."""
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, '/code')
from contract_checks import validate

run = Path('/run')
output = []
for case in json.loads((run/'designed-report.json').read_bytes())['cases']:
    checks, missing = [], []
    for step in case['steps']:
        if step['stage'] not in ('target', 'producer', 'transition'):
            continue
        actor = step['actor']
        if actor not in ('editor', 'reader'):
            missing.append({'reason':'ACTOR_OAS_NOT_CAPTURED', 'actor':actor, 'step_id':step['step_id']})
            continue
        schema = json.loads((run/'raw-oas'/(actor+'.json')).read_bytes())
        actual = step['path'].split('?')[0]
        template = re.sub(r'(/items/[^/]+)/[^/]+$', r'\1/{id}', actual)
        params = {'id':actual.rsplit('/',1)[-1]} if template != actual else None
        if step['method'].lower() not in schema.get('paths',{}).get(template,{}):
            missing.append({'reason':'OPERATION_ABSENT_FROM_ACTOR_OAS','step_id':step['step_id']})
            continue
        response = SimpleNamespace(status=step['status'], content_type=step['content_type'], headers={},
                                   elapsed=step['elapsed'], raw=(run/step['response_artifact']).read_bytes())
        checks.append({'step_id':step['step_id'], 'method':step['method'], 'path':step['path'],
                       'actor':actor, 'response_artifact':step['response_artifact'],
                       'checks':validate(schema,step['method'],template,response,path_parameters=params)})
    output.append({'canonical_test_id':case['id'], 'mode':'OFFLINE_EXISTING_CAPTURE_ONLY',
                   'source_business_status_unchanged':case['verdicts']['business'], 'steps':checks, 'gaps':missing})
print(json.dumps(output))
