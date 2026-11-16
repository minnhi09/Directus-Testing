#!/usr/bin/env python3
"""Local P01 validator and set calculator. Never contacts SUT or rewrites inputs."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from check_offline import read_json, no_duplicate_keys, invalid_constant

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'docs/coverage/schemas'
NAMES = {'baseline-manifest': 'json', 'selection-manifest': 'json',
         'system-inventory': 'jsonl', 'requirements': 'jsonl', 'test-catalog': 'jsonl',
         'rtm-links': 'jsonl', 'gaps': 'jsonl', 'decisions': 'jsonl', 'executions': 'jsonl'}


class Invalid(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise Invalid(code)


def bundle_schema(name, version='1.0.0'):
    common = read_json(SCHEMAS / 'common.schema.json')['$defs']

    def expand(node):
        if isinstance(node, list):
            return [expand(x) for x in node]
        if not isinstance(node, dict):
            return node
        if '$ref' in node:
            prefix = 'common.schema.json#/$defs/'
            require(node['$ref'].startswith(prefix), 'UNSUPPORTED_SCHEMA_REF')
            return expand(common[node['$ref'][len(prefix):]])
        return {k: expand(v) for k, v in node.items()}
    if name == 'executions':
        require(version in ('1.0.0', '1.1.0'), 'UNSUPPORTED_EXECUTION_SCHEMA_VERSION')
    suffix = '.v1.1.schema.json' if name == 'executions' and version == '1.1.0' else '.schema.json'
    return expand(read_json(SCHEMAS / (name + suffix)))


def load(directory):
    data = {}
    for name, ext in NAMES.items():
        path = Path(directory) / (name + '.' + ext)
        if name == 'executions' and not path.exists():
            data[name] = []
        elif ext == 'json':
            data[name] = read_json(path)
        else:
            data[name] = [json.loads(line, object_pairs_hook=no_duplicate_keys,
                                     parse_constant=invalid_constant)
                          for line in path.read_text(encoding='utf-8').splitlines()]
    registry = Path(directory) / 'reference-registry.json'
    if registry.exists():
        data['reference-registry'] = read_json(registry)
    scopes = Path(directory) / 'assertion-scopes.json'
    if scopes.exists():
        data['assertion-scopes'] = read_json(scopes)
    archive = Path(directory) / 'input-archive.json'
    if archive.exists():
        data['input-archive'] = read_json(archive)
    return data


def schema_check(data):
    pwsh = shutil.which('pwsh')
    require(pwsh, 'MISSING_TOOL_POWERSHELL7_TEST_JSON')
    payload = []
    for name in NAMES:
        values = data[name] if NAMES[name] == 'jsonl' else [data[name]]
        for i, value in enumerate(values):
            schema = json.dumps(bundle_schema(name, value.get('schema_version', '1.0.0')))
            payload.append(dict(location=f'{name}:{i}', json=json.dumps(value), schema=schema))
    if 'assertion-scopes' in data:
        payload.append(dict(location='assertion-scopes', json=json.dumps(data['assertion-scopes']),
                            schema=json.dumps(bundle_schema('assertion-scopes'))))
    with tempfile.TemporaryDirectory(prefix='damh-coverage-') as temp:
        path = Path(temp) / 'payload.json'
        path.write_text(json.dumps(payload), encoding='utf-8')
        result = subprocess.run([pwsh, '-NoProfile', '-File', str(ROOT / 'scripts/coverage_schema.ps1'),
                                 '-Payload', str(path)], capture_output=True, text=True, timeout=180)
    if result.returncode:
        # Avoid echoing record values, stderr or credentials embedded in input strings.
        raise Invalid('SCHEMA_VALIDATION_FAILED')


def walk(value):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from walk(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk(v)


def archived_inputs(data):
    """Opt-in immutable provenance transport; never changes an expected digest.

    Historical bundle records stay byte-identical. A hash-pinned sidecar selects
    exact original kind/path/revision/hash identities. Unlisted refs still use
    their original source and must pass every existing integrity check.
    """
    policy = data.get('input-archive')
    if policy is None:
        return {}
    require(set(policy) == {'format','index_path','index_sha256'} and
            policy['format'] == 'P08_INPUT_ARCHIVE_1' and
            isinstance(policy['index_path'],str) and isinstance(policy['index_sha256'],str) and
            re.fullmatch('[0-9a-f]{64}',policy['index_sha256']), 'ARCHIVE_POLICY_INVALID')
    directory = (ROOT/'docs/coverage/sources/immutable-inputs-v1').resolve()
    index_path = (ROOT/policy['index_path']).resolve()
    require(index_path == directory/'index.json' and index_path.is_relative_to(ROOT.resolve()),
            'ARCHIVE_INDEX_PATH')
    raw = index_path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == policy['index_sha256'], 'ARCHIVE_INDEX_HASH')
    index = json.loads(raw, object_pairs_hook=no_duplicate_keys, parse_constant=invalid_constant)
    require(set(index) == {'format','entries'} and index['format'] == 'P08_INPUT_ARCHIVE_1'
            and isinstance(index['entries'], list), 'ARCHIVE_INDEX_INVALID')
    result = {}
    for entry in index['entries']:
        require(set(entry) == {'source_kind','source_path','revision','sha256','snapshot_path','bytes'},
                'ARCHIVE_ENTRY_INVALID')
        require(entry['source_kind'] in ('ARTIFACT','GIT_FILE') and
                isinstance(entry['source_path'],str) and isinstance(entry['snapshot_path'],str) and
                (entry['revision'] is None or isinstance(entry['revision'],str)) and
                isinstance(entry['sha256'], str) and re.fullmatch('[0-9a-f]{64}',entry['sha256']) and
                type(entry['bytes']) is int and entry['bytes'] >= 0, 'ARCHIVE_ENTRY_INVALID')
        path = (ROOT/entry['snapshot_path']).resolve()
        require(path == directory/(entry['sha256']+'.txt') and path.is_relative_to(ROOT.resolve())
                and not (ROOT/entry['snapshot_path']).is_symlink(), 'ARCHIVE_SNAPSHOT_PATH')
        key = (entry['source_kind'],entry['source_path'],entry['revision'],entry['sha256'])
        require(key not in result, 'ARCHIVE_DUPLICATE_IDENTITY')
        result[key] = (path,entry['bytes'])
    return result


def reference_check(data, sample):
    archive = archived_inputs(data)
    resolutions = {}
    cache = {}
    for ref in walk(data):
        if ref.get('kind') not in ('ARTIFACT', 'GIT_FILE', 'DESIGN'):
            continue
        if ref['kind'] == 'DESIGN':
            require(sample, 'DESIGN_REF_IN_REAL_BUNDLE')
        path = (ROOT / ref['path']).resolve()
        # No arbitrary host reads or real env/credential files through a ref.
        require(path.is_relative_to(ROOT) or
                (ref['kind'] == 'GIT_FILE' and path.is_relative_to(ROOT.parent / 'directus')),
                'REF_OUTSIDE_REPOSITORIES')
        require(not any(part.startswith('.') for part in Path(ref['path']).parts if part not in ('..', '.'))
                and not re.search(r'(^|[/\\])(?:.*\.env|.*\.pem|.*\.key)$', ref['path'], re.I),
                'SENSITIVE_REF_PATH')
        if ref['kind'] == 'GIT_FILE':
            require(ref['revision'] == data['baseline-manifest']['sut_commit'], 'REF_SOURCE_BASELINE')
        identity = (ref['kind'],ref['path'],ref.get('revision'),ref.get('sha256'))
        snapshot = archive.get(identity)
        key = (str(path), ref.get('revision'),ref.get('sha256'))
        if key not in cache:
            if snapshot:
                cache[key] = snapshot[0].read_bytes()
                require(len(cache[key]) == snapshot[1], 'ARCHIVE_SNAPSHOT_SIZE')
                resolutions[identity] = snapshot[0].relative_to(ROOT).as_posix()
            elif ref['kind'] == 'GIT_FILE':
                repo = ROOT.parent / 'directus' if path.is_relative_to(ROOT.parent / 'directus') else ROOT
                result = subprocess.run(['git', '-C', str(repo), 'show',
                                         ref['revision'] + ':' + path.relative_to(repo).as_posix()],
                                        capture_output=True, timeout=30)
                require(result.returncode == 0, 'SOURCE_OBJECT_MISSING')
                cache[key] = result.stdout
            else:
                require(path.is_file(), 'ARTIFACT_MISSING')
                cache[key] = path.read_bytes()
        raw = cache[key]
        if ref.get('sha256'):
            require(hashlib.sha256(raw).hexdigest() == ref['sha256'], 'ARTIFACT_HASH_MISMATCH')
        ptr = ref.get('pointer') or ''
        if ptr.startswith('#/'):
            value = json.loads(raw, object_pairs_hook=no_duplicate_keys)
            for token in ptr[2:].split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                try:
                    value = value[int(token)] if isinstance(value, list) else value[token]
                except (KeyError, IndexError, ValueError, TypeError):
                    raise Invalid('JSON_POINTER_MISSING') from None
        elif ptr.startswith('#L'):
            m = re.fullmatch(r'#L(\d+)(?:-L(\d+))?', ptr)
            require(m and 1 <= int(m[1]) <= int(m[2] or m[1]) <= len(raw.splitlines()), 'LINE_REF_RANGE')
    return {'format':'P08_REFERENCE_RESOLUTION_1','archived_identities':len(resolutions),
            'archive_index_sha256':data.get('input-archive',{}).get('index_sha256'),
            'expected_hashes_and_pointers_unchanged':True}


def indexed(rows, key):
    result = {}
    for row in rows:
        k = key(row)
        require(k not in result, 'DUPLICATE_REGISTRY_KEY')
        result[k] = row
    return result


def validate_assertion_scope(data, row, cat, req, edges, sample):
    scope = data.get('assertion-scopes')
    require(scope and scope.get('format') == 'P01_ASSERTION_SCOPES_1', 'ASSERTION_SCOPE_MISSING')
    require(scope['baseline_id'] == row['baseline_id'] and scope['scope_id'] == row['assertion_scope_id'],
            'ASSERTION_SCOPE_BASELINE_OR_ID')
    entries = indexed(scope['entries'], lambda x: (x['canonical_test_id'], x['test_version'], x['requirement_id']))
    cid, version = row['canonical_test_id'], row['test_version']
    targets = {e['requirement_id'] for e in edges if e['canonical_test_id'] == cid
               and e['test_version'] == version and e['coverage_role'] == 'DIRECT'}
    require(targets, 'ASSERTION_SCOPE_NO_DIRECT_REQUIREMENT')
    for rid in targets:
        entry = entries.get((cid, version, rid))
        require(entry, 'ASSERTION_SCOPE_ENTRY_MISSING')
        require(req[rid]['oracle_ref'] in entry['source_refs']
                and all(o in entry['source_refs'] for o in cat[cid, version]['oracle_refs']),
                'ASSERTION_SCOPE_ORACLE_BINDING')
        require(entry['source_refs'] and all(r['certainty'] in ('VERIFIED', 'HISTORICAL', 'PROPOSED' if sample else 'VERIFIED')
                                            for r in entry['source_refs']), 'ASSERTION_SCOPE_SOURCE_UNVERIFIED')
        dimensions = set(entry['mandatory_dimensions'])
        require('BUSINESS' in dimensions, 'BUSINESS_SCOPE_CANNOT_BE_REMOVED')
        if cat[cid, version]['test_type'] == 'CONTRACT':
            require('CONTRACT' in dimensions, 'CONTRACT_SCOPE_CANNOT_BE_REMOVED')
        if cat[cid, version]['test_type'] == 'AUTHORIZATION':
            require('AUTHORIZATION' in dimensions, 'AUTHORIZATION_SCOPE_CANNOT_BE_REMOVED')
        if row['execution_status'] == 'PASS':
            for dimension in dimensions:
                evidence = [a for a in row['assertion_results'] if rid in a['requirement_ids']
                            and a['dimension'] == dimension and a['mandatory']]
                require(evidence and all(a['verdict'] == 'PASS' and a['evidence_refs']
                                        and a['oracle_ref'] in entry['source_refs'] for a in evidence),
                        'MANDATORY_DIMENSION_EVIDENCE_MISSING_OR_FAILED')
            for dimension, field in [('BUSINESS', 'business_verdict'), ('CONTRACT', 'contract_verdict')]:
                if dimension in dimensions:
                    require(row[field] == 'PASS', 'MANDATORY_DIMENSION_VERDICT')


def resolve(data, sample=False):
    """Validate references and semantic invariants, without modifying source records."""
    b, s = data['baseline-manifest'], data['selection-manifest']
    if sample:
        require(all(x.get('data_origin') == 'DESIGN_EXAMPLE'
                    for name in NAMES for x in (data[name] if isinstance(data[name], list) else [data[name]])),
                'SAMPLE_REQUIRES_DESIGN_EXAMPLE')
    else:
        require(not any(x.get('data_origin') == 'DESIGN_EXAMPLE' for x in walk(data)),
                'EXAMPLE_IN_REAL_BUNDLE')
    inv = indexed(data['system-inventory'], lambda x: x['inventory_id'])
    req = indexed(data['requirements'], lambda x: x['requirement_id'])
    cat = indexed(data['test-catalog'], lambda x: (x['canonical_test_id'], x['version']))
    decisions = indexed(data['decisions'], lambda x: x['decision_id'])
    gaps = indexed(data['gaps'], lambda x: x['gap_id'])
    for node in walk(data):
        for field in ('generated_at', 'started_at', 'finished_at', 'locked_at'):
            value = node.get(field)
            if value:
                try:
                    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    require(parsed.tzinfo is not None, 'TIMESTAMP_WITHOUT_ZONE')
                except ValueError:
                    raise Invalid('TIMESTAMP_FORMAT') from None
        if node.get('date'):
            try:
                datetime.strptime(node['date'], '%Y-%m-%d')
            except ValueError:
                raise Invalid('DATE_FORMAT') from None
    indexed(data['system-inventory'], lambda x: x['operation_key'])
    aliases = {}
    for cid, version in cat:
        for alias in [cid] + cat[cid, version]['aliases']:
            require(alias not in aliases or aliases[alias] == cid, 'AMBIGUOUS_ALIAS')
            aliases[alias] = cid
    def test(cid, version):
        require(cid in aliases and (aliases[cid], version) in cat, 'TEST_REFERENCE_MISSING')
        return aliases[cid], version
    require(s['baseline_id'] == b['baseline_id'], 'SELECTION_BASELINE_MISMATCH')
    for row in data['system-inventory'] + data['requirements'] + data['rtm-links']:
        require(row['inventory_revision'] == b['inventory_revision'], 'INVENTORY_REVISION_MISMATCH')
    for row in data['test-catalog'] + data['rtm-links']:
        require(row['catalog_revision'] == b['catalog_revision'], 'CATALOG_REVISION_MISMATCH')
    registry = set(inv) | set(req) | {k[0] for k in cat} | {b['baseline_id'], s['selection_id']}
    registry |= {x['module_id'] for x in inv.values()} | {x['capability_id'] for x in inv.values()}
    # Explicit, evidence-backed sidecar registries; no arbitrary IDs may bypass FKs.
    external = data.get('reference-registry', {'format':'P08_REFERENCE_REGISTRY_1', 'records':[]})
    require(set(external) == {'format','records'} and external['format'] == 'P08_REFERENCE_REGISTRY_1',
            'EXTERNAL_REGISTRY_FORMAT')
    indexed(external['records'], lambda x: x['id'])
    for record in external['records']:
        require(set(record) == {'id','kind','source_ref'} and record['kind'] in ('CAPABILITY','UNRESOLVED'),
                'EXTERNAL_REGISTRY_KIND')
        source = record['source_ref']
        require(source.get('kind') == 'ARTIFACT' and source.get('sha256'), 'EXTERNAL_REGISTRY_PROVENANCE')
        path = (ROOT / source['path']).resolve()
        require(path.is_relative_to(ROOT / 'docs/coverage/inventory') and path.suffix == '.jsonl',
                'EXTERNAL_REGISTRY_PATH')
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'],
                'EXTERNAL_REGISTRY_HASH')
        field = 'capability_id' if record['kind'] == 'CAPABILITY' else 'unresolved_id'
        actual = [json.loads(line, object_pairs_hook=no_duplicate_keys) for line in path.read_text(encoding='utf-8').splitlines()]
        require(any(x.get(field) == record['id'] for x in actual), 'EXTERNAL_REGISTRY_ID_MISSING')
        registry.add(record['id'])
    for node in walk(data):
        if 'gap_ids' in node:
            require(set(node['gap_ids']) <= gaps.keys(), 'GAP_REFERENCE_MISSING')
        if node.get('decision_id'):
            require(node['decision_id'] in decisions, 'DECISION_REFERENCE_MISSING')
    for row in data['requirements']:
        require(set(row['inventory_ids']) <= inv.keys(), 'REQUIREMENT_OPERATION_MISSING')
        if row['applicability'] == 'NOT_APPLICABLE':
            d = decisions.get(row['decision_id'], {})
            require(d.get('status') == 'CONFIRMED' and d.get('approved_by') and d.get('date'), 'UNAPPROVED_NA')
        scores = [row['risk_impact'], row['risk_likelihood'], row['risk_criticality']]
        if all(isinstance(x, int) for x in scores):
            score = sum(scores)
            require(row['priority'] == ('P1' if score >= 8 else 'P2' if score >= 6 else 'P3' if score >= 4 else 'P4'),
                    'RISK_PRIORITY_MISMATCH')
    for row in data['system-inventory']:
        if row['transport'] == 'REST':
            require(row['operation_key'] == '|'.join(['REST', row['method'], row['path_template'],
                    row['route_variant'], row['feature_profile']]), 'OPERATION_KEY_MISMATCH')
    edges = []
    for edge in data['rtm-links']:
        require(edge['requirement_id'] in req, 'RTM_REQUIREMENT_MISSING')
        cid, version = test(edge['canonical_test_id'], edge['test_version'])
        edges.append({**edge, 'canonical_test_id': cid, 'test_version': version})
    indexed(edges, lambda x: (x['requirement_id'], x['canonical_test_id'], x['test_version']))
    for (cid, version), row in cat.items():
        require(set(row['operation_ids']) <= inv.keys(), 'CATALOG_OPERATION_MISSING')
        require(set(row['requirement_ids']) == {e['requirement_id'] for e in edges
                if (e['canonical_test_id'], e['test_version']) == (cid, version)}, 'RTM_PROJECTION_MISMATCH')
        for prereq in row['prerequisites']:
            require(prereq in aliases, 'PREREQUISITE_TEST_MISSING')
        for parent in row['derived_from']:
            test(parent['canonical_test_id'], parent['test_version'])
    def visit(key, active, done):
        require(key not in active, 'CATALOG_DEPENDENCY_CYCLE')
        if key in done:
            return
        active.add(key)
        row = cat[key]
        targets = [test(p['canonical_test_id'], p['test_version']) for p in row['derived_from']]
        targets += [k for p in row['prerequisites'] for k in cat if k[0] == aliases[p]]
        for target in targets:
            visit(target, active, done)
        active.remove(key)
        done.add(key)
    done = set()
    for key in cat:
        visit(key, set(), done)
    executions = []
    for original in data['executions']:
        row = copy.deepcopy(original)
        row['canonical_test_id'], row['test_version'] = test(row['canonical_test_id'], row['test_version'])
        require(row['baseline_id'] == b['baseline_id'], 'EXECUTION_BASELINE_MISMATCH')
        indexed(row['assertion_results'], lambda a: a['assertion_id'])
        for assertion in row['assertion_results']:
            require(set(assertion['requirement_ids']) <= req.keys(), 'ASSERTION_REQUIREMENT_MISSING')
            require(all(any(e['requirement_id'] == rid and e['canonical_test_id'] == row['canonical_test_id']
                            and e['test_version'] == row['test_version'] for e in edges)
                        for rid in assertion['requirement_ids']), 'ASSERTION_NOT_IN_RTM')
        for op in row['operation_evidence']:
            require(op['inventory_id'] in inv, 'EXECUTION_OPERATION_MISSING')
            require(op['inventory_id'] in cat[row['canonical_test_id'], row['test_version']]['operation_ids'],
                    'EXECUTION_OPERATION_NOT_IN_TEST')
        if row['schema_version'] == '1.1.0':
            validate_assertion_scope(data, row, cat, req, edges, sample)
        if row['execution_status'] == 'PASS':
            require(row['business_verdict'] != 'FAIL' and row['contract_verdict'] != 'FAIL', 'UNQUALIFIED_PASS')
            require(row['completion_status'] == 'COMPLETE' and row['infrastructure_status'] == 'HEALTHY'
                    and row['tool_status'] == 'PASSED' and row['tool_exit_code'] == 0
                    and row['cleanup_status'] in ('PASS', 'NOT_REQUIRED')
                    and row['assertion_results'] and all(a['verdict'] == 'PASS' for a in row['assertion_results'] if a['mandatory']),
                    'UNQUALIFIED_PASS')
        if row['cleanup_status'] == 'NOT_REQUIRED':
            require(cat[row['canonical_test_id'], row['test_version']]['cleanup_ref'], 'CLEANUP_REASON_MISSING')
        if row['started_at'] and row['finished_at']:
            require(datetime.fromisoformat(row['started_at'].replace('Z', '+00:00')) <=
                    datetime.fromisoformat(row['finished_at'].replace('Z', '+00:00')), 'TIMESTAMP_ORDER')
        executions.append(row)
    eb = indexed(executions, lambda x: x['execution_id'])
    registry |= set(eb) | {x['run_id'] for x in executions}
    for node in walk(data):
        require(not node.get('finding_id'), 'FINDING_REGISTRY_NOT_SUPPLIED')
    for d in data['decisions'] + data['gaps']:
        require(set(d['target_ids']) <= registry, 'TARGET_REGISTRY_MISSING')
    indexed(executions, lambda x: (x['run_id'], x['canonical_test_id'], x['test_version'], x['attempt']))
    for e in executions:
        parent = e['retry_of_execution_id']
        if parent:
            require(parent in eb, 'RETRY_PARENT_MISSING')
            p = eb[parent]
            require((e['run_id'], e['canonical_test_id'], e['test_version']) ==
                    (p['run_id'], p['canonical_test_id'], p['test_version']) and p['attempt'] < e['attempt'],
                    'RETRY_LINEAGE_INVALID')
    selected = {test(x['canonical_test_id'], x['test_version']) for x in s['tests']}
    require(set(s['requirement_ids']) <= req.keys() and set(s['inventory_ids']) <= inv.keys(), 'SELECTION_REF_MISSING')
    if s['state'] == 'LOCKED':
        d = decisions.get(s['decision_id'], {})
        require(b['review_state'] == 'LOCKED' and d.get('status') == 'CONFIRMED'
                and d.get('approved_by') and d.get('date'), 'UNAPPROVED_SELECTION')
    candidates = [x for x in executions if (x['canonical_test_id'], x['test_version']) in selected]
    policy = s['run_selection_policy']
    if policy == 'PREDECLARED_EXECUTIONS':
        require(set(s['execution_ids']) <= eb.keys(), 'PREDECLARED_EXECUTION_MISSING')
        candidates = [x for x in candidates if x['execution_id'] in s['execution_ids']]
    elif policy == 'LATEST_ATTEMPT_IN_PREDECLARED_RUNS':
        require(set(s['run_ids']) <= set(b['run_ids']) | {x['run_id'] for x in executions}, 'PREDECLARED_RUN_MISSING')
        candidates = [x for x in candidates if x['run_id'] in s['run_ids']]
    else:
        candidates = []
    latest = {}
    for x in candidates:
        key = (x['canonical_test_id'], x['test_version'])
        if key in latest:
            require(policy == 'LATEST_ATTEMPT_IN_PREDECLARED_RUNS', 'AMBIGUOUS_PREDECLARED_ATTEMPTS')
            order = lambda e: (datetime.fromisoformat(e['started_at'].replace('Z', '+00:00')).astimezone(timezone.utc)
                               if e['started_at'] else datetime.min.replace(tzinfo=timezone.utc), e['attempt'])
            require(order(x) != order(latest[key]), 'AMBIGUOUS_LATEST_ATTEMPT')
            if order(x) < order(latest[key]):
                continue
        latest[key] = x
    return dict(inv=inv, req=req, cat=cat, edges=edges, latest=latest, selected=selected,
                executions=executions)


def calculate(data, resolved, sample=False):
    s = data['selection-manifest']
    inv, req, cat, edges, latest = (resolved[k] for k in ('inv', 'req', 'cat', 'edges', 'latest'))
    locked = s['state'] == 'LOCKED' and data['baseline-manifest']['review_state'] == 'LOCKED'
    selected_req = {x for x in s['requirement_ids'] if req[x]['scope_tier'] in s['scope_tiers']
                    and (not s['module_ids'] or req[x]['module_id'] in s['module_ids'])}
    ready = locked and all(req[x]['applicability'] != 'UNKNOWN' for x in selected_req)
    R = {x for x in selected_req if req[x]['applicability'] == 'APPLICABLE' and req[x]['review_state'] in ('REVIEWED', 'LOCKED')}
    ready = ready and all(req[x]['review_state'] in ('REVIEWED', 'LOCKED') for x in R)
    def oracle(ref):
        return ref and (sample or ref['kind'] != 'DESIGN') and ref['certainty'] in ('VERIFIED', 'HISTORICAL', 'PROPOSED' if sample else 'VERIFIED')
    D, E, V = set(), set(), set()
    def evaluated(e, rid):
        return oracle(req[rid]['oracle_ref']) and e and e['execution_status'] in ('PASS', 'FAIL', 'INCOMPLETE') and any(
            rid in a['requirement_ids'] and a['verdict'] in ('PASS', 'FAIL') and oracle(a['oracle_ref'])
            and a['evidence_refs'] for a in e['assertion_results'])
    for rid in R:
        direct = [e for e in edges if e['requirement_id'] == rid and e['coverage_role'] == 'DIRECT'
                  and (e['canonical_test_id'], e['test_version']) in resolved['selected']]
        keys = [(e['canonical_test_id'], e['test_version']) for e in direct]
        if oracle(req[rid]['oracle_ref']) and any(cat[k]['fixture_profile'] and cat[k]['oracle_refs']
                                                and all(oracle(o) for o in cat[k]['oracle_refs']) for k in keys):
            D.add(rid)
        if any(evaluated(latest.get(k), rid) for k in keys):
            E.add(rid)
        mandatory = [(e['canonical_test_id'], e['test_version']) for e in direct if e['mandatory_for_requirement']]
        def verified(k):
            e = latest.get(k)
            return evaluated(e, rid) and e['execution_status'] == 'PASS' and e['infrastructure_status'] == 'HEALTHY' and e['cleanup_status'] in ('PASS', 'NOT_REQUIRED') and any(
                a['mandatory'] and rid in a['requirement_ids'] for a in e['assertion_results']) and all(
                a['verdict'] == 'PASS' for a in e['assertion_results'] if rid in a['requirement_ids'] and a['mandatory'])
        if rid in D and mandatory and all(verified(k) for k in mandatory) and not any(
            latest.get(k) and any(a['verdict'] == 'FAIL' and rid in a['requirement_ids'] for a in latest[k]['assertion_results']) for k in keys):
            V.add(rid)
    eligible_ops = {i for i in s['inventory_ids'] if 'REST' in s['transports'] and inv[i]['transport'] == 'REST'
                    and inv[i]['scope_tier'] in s['scope_tiers']
                    and (s['unit'] == 'REQUIREMENT' or not s['module_ids'] or inv[i]['module_id'] in s['module_ids'])}
    O = {i for i in eligible_ops if inv[i]['applicability'] == 'APPLICABLE'}
    op_ready = locked and all(inv[i]['applicability'] != 'UNKNOWN' for i in eligible_ops)
    hit, positive = set(), set()
    for e in latest.values():
        for o in e['operation_evidence']:
            i = o['inventory_id']
            if o['dispatch_verified'] is True and o['request_ref'] and o['response_ref']:
                hit.add(i)
                if o['positive_acceptance'] is True and e['business_verdict'] == 'PASS' and any(
                    a['verdict'] == 'PASS' and a['dimension'] in ('BUSINESS', 'INVARIANT') and a['evidence_refs']
                    and any(i in req[rid]['inventory_ids'] for rid in a['requirement_ids']) for a in e['assertion_results']):
                    positive.add(i)
    def metric(n, den, ok, reason):
        return dict(measurement_status='MEASURED' if ok and den else 'NOT_MEASURED',
                    numerator_ids=sorted(n & den) if ok else [], denominator_ids=sorted(den) if ok else [],
                    missing_ids=sorted(den - n), numerator_count=len(n & den) if ok and den else None,
                    denominator_count=len(den) if ok and den else None,
                    percentage=100 * len(n & den) / len(den) if ok and den else None,
                    reason=None if ok and den else reason)
    has_exec = any(evaluated(e, rid) for e in latest.values() for rid in R)
    has_operation = any(o['request_ref'] and o['response_ref'] for e in latest.values() for o in e['operation_evidence'])
    statuses = collections_status(resolved['executions'])
    flaky = []
    for key in resolved['selected']:
        attempts = [e for e in resolved['executions'] if (e['canonical_test_id'], e['test_version']) == key]
        if len({(e['execution_status'], e['business_verdict'], e['contract_verdict']) for e in attempts}) > 1:
            flaky.append(key[0] + '@' + key[1])
    return dict(format='P08_OFFLINE_SET_REPORT_1', data_origin='DESIGN_EXAMPLE' if sample else 'DERIVED',
                synthetic=sample, baseline_id=s['baseline_id'], selection_id=s['selection_id'],
                sets=dict(R=sorted(R) if ready else [], D=sorted(D) if ready else [],
                          E=sorted(E) if ready and has_exec else [], V=sorted(V) if ready and has_exec else [], O=sorted(O) if op_ready else []),
                metrics=dict(requirement_design=metric(D, R, ready, 'DENOMINATOR_NOT_LOCKED_OR_EMPTY'),
                             requirement_execution=metric(E, R, ready and has_exec, 'NO_SELECTED_EXECUTION_OR_UNLOCKED'),
                             requirement_verified=metric(V, R, ready and has_exec, 'NO_SELECTED_EXECUTION_OR_UNLOCKED'),
                             hit_coverage=metric(hit, O, op_ready and has_operation, 'NO_EXECUTION_OR_OPERATION_SCOPE_UNLOCKED'),
                             positive_acceptance=metric(positive, O, op_ready and has_operation, 'NO_EXECUTION_OR_OPERATION_SCOPE_UNLOCKED')),
                missing_requirement_ids=sorted(R-E), missing_operation_ids=sorted(O-hit),
                unknown_requirement_ids=sorted(x for x in selected_req if req[x]['applicability'] == 'UNKNOWN'),
                pending_selection_requirement_ids=sorted(selected_req if not ready else R-E),
                unknown_inventory_ids=sorted(i for i in eligible_ops if inv[i]['applicability'] == 'UNKNOWN'),
                source_only_ids=sorted(i for i in s['inventory_ids'] if i in O and inv[i]['oas_state']=='SOURCE_ONLY'),
                oas_only_ids=sorted(i for i in s['inventory_ids'] if i in O and inv[i]['oas_state']=='OAS_ONLY'),
                selected_execution_ids=sorted(x['execution_id'] for x in latest.values()),
                flaky_or_disagreeing_test_versions=sorted(flaky),
                observed_execution_dimensions=statuses,
                unsupported_metrics={k:'NOT_MEASURED' for k in ('specification','negative_authorization','module_mapped','module_touched','module_qualified','code_statement','code_line','code_function','code_branch','schema_parameter','schema_keyword','schema_response')},
                notes=['No denominator inferred from aliases/request counts.', 'Schema partial/violated is never promoted to PASS.',
                       'Specification usability, authorization-rule matrix, module DoD and code/schema traces require separate reviewed inputs.'])


def collections_status(executions):
    return {dimension: {status: sum(e[dimension] == status for e in executions)
                        for status in sorted({e[dimension] for e in executions})}
            for dimension in ('execution_status','business_verdict','contract_verdict','cleanup_status','infrastructure_status')}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate','calculate','inspect-history'])
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--sample', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect-history':
            report = read_json(args.bundle)
            key = 'scenarios' if 'scenarios' in report else 'cases'
            require(key in report and isinstance(report[key], list), 'UNSUPPORTED_LEGACY_REPORT')
            print(json.dumps(dict(format='P08_LEGACY_REPORT_INSPECTION_1',
                  sha256=hashlib.sha256(args.bundle.read_bytes()).hexdigest(),
                  baseline_transfer_allowed=False, converted_executions=0,
                  observations=[{k:x.get(k) for k in ('id','status','verdicts','cleanup_status')}
                                for x in report[key]]), ensure_ascii=True, indent=2))
            return 0
        data = load(args.bundle)
        schema_check(data)
        result = resolve(data, args.sample)
        references = reference_check(data, args.sample)
        output = calculate(data, result, args.sample) if args.command == 'calculate' else dict(valid=True, synthetic=args.sample)
        output['reference_resolution'] = references
        print(json.dumps(output, ensure_ascii=True, indent=2))
        return 0
    except (Invalid, ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        code = str(error) if isinstance(error, Invalid) else type(error).__name__
        print(json.dumps(dict(valid=False, error_code=code)))
        return 1


if __name__ == '__main__':
    sys.exit(main())
