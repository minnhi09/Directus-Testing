"""Offline captured-response checks only; use pinned Schemathesis image."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace
from urllib.parse import urlsplit
from contract_checks import validate


def prepare(row, metadata, raw_schema, raw_response):
    required=('content_type','elapsed_seconds','http_version','effective_url')
    if row.get('trace_version')!=2 or not all(key in row for key in required):
        return {'measurement_status':'NOT_MEASURED','reason':'MISSING_HTTP_METADATA'}
    if (not isinstance(row['content_type'],str) or type(row['elapsed_seconds']) not in (int,float)
            or row['elapsed_seconds'] < 0 or not row['http_version']):
        return {'measurement_status':'NOT_MEASURED','reason':'INVALID_HTTP_METADATA'}
    if metadata is None or metadata['actor']!=row['actor']:
        return {'measurement_status':'NOT_MEASURED','reason':'ACTOR_SCHEMA_MISSING_OR_MISMATCH'}
    if metadata['status']!=200:
        return {'measurement_status':'NOT_MEASURED','reason':'ACTOR_SCHEMA_EXPORT_BLOCKED'}
    if hashlib.sha256(raw_schema).hexdigest()!=metadata['sha256']:
        raise ValueError('ACTOR_SCHEMA_HASH_MISMATCH')
    if hashlib.sha256(raw_response).hexdigest()!=row['response_sha256']:
        raise ValueError('RESPONSE_HASH_MISMATCH')
    schema=json.loads(raw_schema); actual=urlsplit(row['path']).path
    template=re.sub(r'(/items/[^/]+)/[^/]+$',r'\1/{id}',actual)
    if row['method'].lower() not in schema.get('paths',{}).get(template,{}):
        return {'measurement_status':'NOT_MEASURED','reason':'OPERATION_ABSENT_FROM_ACTOR_SCHEMA'}
    return {'measurement_status':'MEASURED','schema':schema,'template':template,
            'parameters':{'id':actual.rsplit('/',1)[-1]} if actual!=template else None}


def run(directory):
    root=Path(directory); metadata={r['actor']:r for r in json.loads((root/'schema-metadata.json').read_bytes())}; results=[]
    for i,row in enumerate(json.loads((root/'trace.json').read_bytes())):
        meta=metadata.get(row['actor']); schema=(root/'raw-oas'/(row['actor']+'.json')).read_bytes() if meta else b''
        body=(root/row['response_ref']).read_bytes(); prepared=prepare(row,meta,schema,body)
        entry={'trace_index':i,'scenario':row['scenario'],'actor':row['actor'],'method':row['method'],'path':row['path'],
               'status':row['status'],'captured_content_type':row.get('content_type'),
               'response_ref':row['response_ref'],'response_sha256':row['response_sha256'],
               'schema_sha256':meta['sha256'] if meta else None,'measurement_status':prepared['measurement_status']}
        if prepared['measurement_status']=='MEASURED':
            response=SimpleNamespace(status=row['status'],content_type=row['content_type'],headers={},
                                     elapsed=row['elapsed_seconds'],raw=body)
            checks=validate(prepared['schema'],row['method'],prepared['template'],response,path_parameters=prepared['parameters'])
            entry.update(checks=checks,contract_verdict='FAIL' if any(c['status']=='failed' for c in checks)
                         else 'PASS' if all(c['status']=='passed' for c in checks) else 'INCOMPLETE')
        else:entry.update(contract_verdict='NOT_MEASURED',reason=prepared['reason'])
        results.append(entry)
    return {'mode':'OFFLINE_CAPTURED_RESPONSE_REVALIDATION','new_HTTP_requests':0,'records':results}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('directory')
    print(json.dumps(run(parser.parse_args().directory)))
