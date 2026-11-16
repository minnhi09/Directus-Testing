"""Offline integrity checks for explicitly captured scenario HTTP mappings."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SCENARIOS={f'S{i}' for i in range(1,7)}


def validate(rows, root, *, require_contract_metadata=False):
    root=Path(root).resolve()
    result=[]
    for row in rows:
        if row['scenario'] not in SCENARIOS:
            continue
        if row['actor'] not in ('admin','editor','reader','anonymous'):
            raise ValueError('UNKNOWN_ACTOR')
        if row['curl_exit_code'] != 0 or not 100 <= row['status'] <= 599:
            raise ValueError('NO_HTTP_RESPONSE')
        if not re.fullmatch(r'http-[0-9]+\.json',row['response_ref']):
            raise ValueError('UNSAFE_RESPONSE_REF')
        if not row['path'].startswith('/items/qa_'):
            raise ValueError('OUTSIDE_SCENARIO_ITEMS')
        if require_contract_metadata:
            if row.get('trace_version') != 2 or not all(k in row for k in ('content_type','elapsed_seconds','http_version','effective_url')):
                raise ValueError('MISSING_HTTP_METADATA')
            if (not isinstance(row['content_type'],str) or type(row['elapsed_seconds']) not in (int,float)
                    or row['elapsed_seconds'] < 0 or not row['http_version']):
                raise ValueError('INVALID_HTTP_METADATA')
            url=urlsplit(row['effective_url'])
            if (url.scheme != 'http' or url.hostname != '127.0.0.1' or url.port != 18055
                    or url.username or url.password or url.path != row['path'].split('?')[0]):
                raise ValueError('HTTP_TARGET_MISMATCH')
        raw=(root/row['response_ref']).read_bytes()
        if raw or row['status'] != 204:
            json.loads(raw)
        result.append({**row,'response_sha256':hashlib.sha256(raw).hexdigest()})
    if {r['scenario'] for r in result} != SCENARIOS:
        raise ValueError('MISSING_SCENARIO_TRACE')
    return result


def anonymous_schema_state(status, raw):
    if status != 200:
        return 'BLOCKED_SCHEMA_EXPORT'
    schema=json.loads(raw)
    if schema.get('openapi') != '3.0.1' or not isinstance(schema.get('paths'),dict):
        raise ValueError('INVALID_ANONYMOUS_OAS')
    return 'PRESENT' if 'get' in schema['paths'].get('/items/qa_articles',{}) else 'OPERATION_NOT_IN_ANONYMOUS_OAS'
