"""Isolated P09 fixture adapter and read-only authenticated preflight. No campaign.

Credentials stay in the ignored private profile or child process environment.
The shared seed helper is reused unchanged; lab.sh's legacy target is never used.
"""
import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, ProxyHandler, build_opener

from p09_preflight import ROOT, PROFILE, check_profile, namespace

URL = 'http://127.0.0.1:18055'
PRIVATE_KEYS = {'P09_NAMESPACE', 'P09_ADMIN_PASSWORD', 'P09_EDITOR_PASSWORD',
                'P09_READER_PASSWORD'}


def docker_json(*args):
    result = subprocess.run(['docker', *args], capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError('DOCKER_METADATA_FAILED')
    return json.loads(result.stdout)


def check_resources(ns, containers, volumes, networks, profile):
    """Reject shared storage, wrong image, network or loopback binding before seed."""
    by_service = {}
    for item in containers:
        labels = item['Config']['Labels']
        service = labels.get('com.docker.compose.service')
        if labels.get('com.docker.compose.project') != ns or service not in ('database', 'directus'):
            raise ValueError('WRONG_PROJECT_OR_SERVICE')
        if service in by_service or item['Config']['Image'] != profile['services'][service]['image']:
            raise ValueError('DUPLICATE_SERVICE_OR_IMAGE_MISMATCH')
        if item['State'].get('Health', {}).get('Status') != 'healthy':
            raise ValueError('CONTAINER_NOT_HEALTHY')
        expected = {'database': {ns+'_db_data': '/var/lib/postgresql/data'},
                    'directus': {ns+'_uploads': '/directus/uploads', ns+'_extensions': '/directus/extensions'}}[service]
        actual = {m.get('Name'): m['Destination'] for m in item['Mounts'] if m['Type'] == 'volume'}
        if actual != expected or any(m['Type'] != 'volume' for m in item['Mounts']):
            raise ValueError('UNEXPECTED_STORAGE')
        if set(item['NetworkSettings']['Networks']) != {ns+'_network'}:
            raise ValueError('UNEXPECTED_NETWORK')
        ports = item['NetworkSettings']['Ports']
        published = {k:v for k,v in ports.items() if v}
        expected_ports = {'8055/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '18055'}]} if service == 'directus' else {}
        if published != expected_ports:
            raise ValueError('UNEXPECTED_PUBLISHED_PORT')
        by_service[service] = item
    if set(by_service) != {'database', 'directus'}:
        raise ValueError('MISSING_SERVICE')
    if {v['Name'] for v in volumes} != {ns+'_db_data', ns+'_uploads', ns+'_extensions'}:
        raise ValueError('MISSING_VOLUME')
    if {n['Name'] for n in networks} != {ns+'_network'}:
        raise ValueError('MISSING_NETWORK')
    for resource in [*volumes, *networks]:
        labels = resource.get('Labels') or {}
        if (labels.get('damh.phase'), labels.get('damh.namespace'), labels.get('com.docker.compose.project')) != ('P09', ns, ns):
            raise ValueError('RESOURCE_OWNERSHIP_MISMATCH')
    return by_service


def owned_resources(ns, profile):
    result = subprocess.run(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project='+ns],
                            capture_output=True, text=True, timeout=30, check=True)
    ids = result.stdout.split()
    if not ids:
        raise RuntimeError('P09_NOT_STARTED')
    return check_resources(ns, docker_json('inspect', *ids),
                           docker_json('volume', 'inspect', *[ns+s for s in ('_db_data','_uploads','_extensions')]),
                           docker_json('network', 'inspect', ns+'_network'), profile)


def private_values(path, ns, seed):
    values = {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        key, sep, value = line.partition('=')
        if sep and key in PRIVATE_KEYS:
            values[key] = value.strip().strip('"').strip("'")
    if values.get('P09_NAMESPACE') != ns or not values.get('P09_ADMIN_PASSWORD'):
        raise ValueError('PRIVATE_PROFILE_MISMATCH')
    if seed:
        additions = {k:secrets.token_urlsafe(32) for k in ('P09_EDITOR_PASSWORD','P09_READER_PASSWORD') if not values.get(k)}
        if additions:
            with path.open('a', encoding='utf-8') as handle:
                handle.write('\n'+''.join(k+'='+v+'\n' for k,v in additions.items()))
            values.update(additions)
    if not all(values.get(k) for k in ('P09_EDITOR_PASSWORD','P09_READER_PASSWORD')):
        raise ValueError('FIXTURE_ACTOR_CREDENTIALS_MISSING')
    return values


def seed_fixture(ns, private, runtime, profile, *, component='seed', output=None, trace=False, run_id=None):
    if component not in ('seed', 'export-schema', 'p10-scenarios'):
        raise ValueError('UNSUPPORTED_COMPONENT')
    owned_resources(ns, profile)
    bash = shutil.which('bash') if os.name != 'nt' else r'C:\Program Files\Git\bin\bash.exe'
    if not bash or not Path(bash).is_file():
        raise RuntimeError('GIT_BASH_MISSING')
    jq = ROOT/'runtime/tools/jq-1.8.2.exe'
    if os.name == 'nt' and (not jq.is_file() or hashlib.sha256(jq.read_bytes()).hexdigest() != 'a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627'):
        raise RuntimeError('PINNED_JQ_MISSING_OR_MISMATCH')
    env = os.environ.copy()
    # Ignore ambient meter/URL/profile overrides. Pass the existing helper interface.
    for key in list(env):
        if key.startswith('LAB_'):
            del env[key]
    run_dir = output or runtime/'preflight-seed'
    run_dir.mkdir(exist_ok=True)
    values = dict(ROOT_DIR=str(ROOT), RUN_DIR=str(run_dir), RUNTIME_ROOT=str(runtime),
                  API_URL=URL, RUNNER_API_URL='http://directus:8055', PROJECT_NAME=ns,
                  NETWORK_NAME=ns+'_network', ADMIN_EMAIL='admin@example.com',
                  ADMIN_PASSWORD=private['P09_ADMIN_PASSWORD'], EDITOR_EMAIL='editor@example.com',
                  EDITOR_PASSWORD=private['P09_EDITOR_PASSWORD'], READER_EMAIL='reader@example.com',
                  READER_PASSWORD=private['P09_READER_PASSWORD'], RUN_ID=ns+'-preflight',
                  FIXTURE_VERSION='r06-k05-v2', SCHEMATHESIS_IMAGE=profile['services']['runner']['image'])
    for key in ('ROOT_DIR', 'RUN_DIR', 'RUNTIME_ROOT'):
        values[key] = values[key].replace('\\', '/')
    env.update({'LAB_'+k:v for k,v in values.items()})
    if trace:
        if component not in ('p10-scenarios','export-schema'):
            raise ValueError('TRACE_REQUIRES_SCENARIOS_OR_SCHEMA_EXPORT')
        env['LAB_TRACE_SCENARIOS'] = '1'
    if run_id:
        env['LAB_RUN_ID'] = run_id
    if os.name == 'nt':
        env['LAB_JQ_EXE'] = jq.as_posix()
        # Bash imports PATH and converts these native directories.
        env['PATH'] = str(ROOT/'scripts/windows')+os.pathsep+env['PATH']
    env['LAB_COMPOSE_ENV_FILE'] = (ROOT/'runtime/profiles'/ns/'p09.env').as_posix()
    env['LAB_COMPOSE_FILE'] = PROFILE.as_posix()
    result = subprocess.run([bash, 'scripts/lab-components.sh', component], cwd=ROOT, env=env,
                            capture_output=True, timeout=360)
    # Deliberately don't publish child output: HTTP bodies remain private runtime files.
    return result.returncode


class API:
    def __init__(self):
        self.opener = build_opener(ProxyHandler({}))
        self.requests = []

    def call(self, path, token=None, data=None, *, method=None):
        headers = {'Content-Type':'application/json'}
        if token:
            headers['Authorization'] = 'Bearer '+token
        method = method or ('POST' if data is not None else 'GET')
        request = Request(URL+path, data=json.dumps(data).encode() if data is not None else None,
                          headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=15) as response:
                code, raw = response.status, response.read()
        except HTTPError as error:
            code, raw = error.code, error.read()
        self.requests.append({'method':method,'path':path,'status':code})
        try:
            body = json.loads(raw)
        except ValueError:
            body = {}
        return code, body

    def get(self, path, token):
        code, body = self.call(path, token)
        if code != 200 or 'data' not in body:
            raise RuntimeError('PREFLIGHT_HTTP_FAILED')
        return body['data']

    def login(self, actor, password):
        code, body = self.call('/auth/login', data={'email':actor+'@example.com','password':password})
        if code != 200 or not body.get('data',{}).get('access_token'):
            raise RuntimeError('ACTOR_LOGIN_FAILED')
        return body['data']['access_token']


def verify(api, private, runtime):
    tokens = {a:api.login(a, private['P09_'+a.upper()+'_PASSWORD']) for a in ('admin','editor','reader')}
    admin = tokens['admin']
    # Least-privilege actors expose only their ID through /users/me. Resolve
    # active status and role with admin, rather than broadening their policies.
    self_ids = {a:api.get('/users/me?fields=id', t)['id'] for a,t in tokens.items()}
    identities = {a:api.get('/users/'+actor_id+'?fields=id,role,status', admin) for a,actor_id in self_ids.items()}
    license_data = api.get('/license', admin)
    entry = license_data['entitlements']['custom_permission_rules_enabled']
    entitlement = entry.get('override') if entry.get('override') is not None else entry.get('default')
    if entitlement is not True:
        raise RuntimeError('BLOCKED_LICENSE')
    code, health = api.call('/server/health', admin)
    if code != 200 or health.get('status') != 'ok':
        raise RuntimeError('HEALTH_FAILED')
    categories = api.get('/items/qa_categories?limit=-1', admin)
    articles = api.get('/items/qa_articles?limit=-1', admin)
    fixture = json.loads((runtime/'fixture-ids.json').read_text(encoding='utf-8'))
    reader_articles = api.get('/items/qa_articles?limit=-1&fields=*', tokens['reader'])
    reader_categories = api.get('/items/qa_categories?limit=-1', tokens['reader'])
    editor_articles = api.get('/items/qa_articles?limit=-1&fields=id,status', tokens['editor'])
    policies = api.get('/policies?fields=id,name,admin_access,app_access', admin)
    permissions = api.get('/permissions?fields=policy,collection,action,fields,permissions&limit=-1', admin)
    accesses = api.get('/access?fields=role,user,policy&limit=-1', admin)
    roles = api.get('/roles?fields=id,name&limit=-1', admin)
    policy_by_name = {p['name']:p for p in policies}
    checks = {'three_categories':len(categories)==3, 'twelve_articles':len(articles)==12,
              'authenticated_health':True,
              'license_active':license_data.get('status')=='active',
              'license_no_invalid_reason':license_data.get('invalid_reason') is None,
              'six_draft_six_published':sum(a['status']=='draft' for a in articles)==6 and sum(a['status']=='published' for a in articles)==6,
              'editor_reads_all_fixture':len(editor_articles)==12,
              'reader_only_six_published':len(reader_articles)==6 and all(a['status']=='published' for a in reader_articles),
              'reader_hidden_internal_notes':all('internal_notes' not in a for a in reader_articles),
              'reader_categories':len(reader_categories)==3,
              'distinct_active_actor_ids':len({a['id'] for a in identities.values()})==3 and all(a['status']=='active' for a in identities.values())}
    checks['fixture_map_matches_runtime'] = (fixture['project']==runtime.name and fixture['fixture_version']=='r06-k05-v2'
        and set(fixture['fixtures']['qa_categories'].values())=={c['id'] for c in categories}
        and len(fixture['fixtures']['qa_categories'])==3
        and set(fixture['fixtures']['qa_articles'].values())=={a['id'] for a in articles}
        and len(fixture['fixtures']['qa_articles'])==12)
    admin_policy_ids = {p['id'] for p in policies if p['admin_access'] is True}
    checks['admin_effective_policy'] = any(a['policy'] in admin_policy_ids and
        (a['user']==identities['admin']['id'] or (a['role'] is not None and a['role']==identities['admin']['role'])) for a in accesses)
    for actor in ('editor', 'reader'):
        prefix = 'R06 '+actor.title()
        policy = policy_by_name[prefix+' API Policy']
        checks[actor+'_no_admin_or_studio'] = policy['admin_access'] is False and policy['app_access'] is False
        expected_role = next(r['id'] for r in roles if r['name']==prefix)
        checks[actor+'_role_policy_binding'] = identities[actor]['role']==expected_role and any(a['role']==expected_role and a['policy']==policy['id'] for a in accesses)
        perms = [p for p in permissions if p['policy']==policy['id']]
        if actor == 'editor':
            checks['editor_crud_policy'] = len(perms)==8 and all(any(p['collection']==c and p['action']==a and p['fields']==['*'] and p['permissions'] in ({},None) for p in perms) for c in ('qa_articles','qa_categories') for a in ('create','read','update','delete'))
        else:
            read = [p for p in perms if p['collection']=='qa_articles' and p['action']=='read']
            checks['reader_published_policy'] = len(read)==1 and read[0]['permissions']=={'status':{'_eq':'published'}} and 'internal_notes' not in read[0]['fields'] and '*' not in read[0]['fields']
            checks['reader_no_writable_fields'] = all(p['action']=='read' or (p['action']=='update' and p['fields']==[]) for p in perms)
    for collection in ('qa_categories','qa_articles'):
        code, _ = api.call('/items/'+collection+'?limit=1')
        checks['anonymous_denied_'+collection] = code in (401,403)
    fields = api.get('/fields/qa_articles', admin)
    relations = api.get('/relations/qa_articles', admin)
    fs = {f['field']:f for f in fields}
    checks['field_validation_config'] = (fs['title']['schema']['max_length']==120 and fs['status']['meta']['validation']=={'status':{'_in':['draft','published']}} and fs['score']['meta']['validation']=={'score':{'_gte':0,'_lte':5}})
    checks['nullable_category_set_null'] = fs['category']['schema']['is_nullable'] is True and any(r['field']=='category' and r['related_collection']=='qa_categories' and r['schema']['on_delete']=='SET NULL' for r in relations)
    return {'checks':checks,'actor_ids':{a:v['id'] for a,v in identities.items()},
            'license':{k:license_data.get(k) for k in ('status','source','invalid_reason')},
            'custom_permission_rules_enabled':entitlement,
            'fixture_map_sha256':hashlib.sha256((runtime/'fixture-ids.json').read_bytes()).hexdigest(),
            'fixture_map_keys':sorted(fixture), 'requests':api.requests}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--namespace', required=True, type=namespace)
    parser.add_argument('--seed', action='store_true', help='Reuse shared seed twice to check idempotency; only P09-owned resources')
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    if args.report.exists():
        parser.error('REPORT_ALREADY_EXISTS: choose a new snapshot path')
    report = {'schema':'P09_RUNTIME_1','created_at':datetime.now(timezone.utc).isoformat(),
              'namespace':args.namespace,'host_url':URL,'campaign':'NOT_RUN', 'P10':'NOT_RUN',
              'execution_coverage':'NOT_MEASURED','status':'BLOCKED'}
    try:
        profile = json.loads(PROFILE.read_text())
        check_profile(profile)
        owned = owned_resources(args.namespace, profile)
        version = subprocess.run(['docker','exec',owned['directus']['Id'],'node','-p',
                                  "require('/directus/package.json').version"], capture_output=True, text=True, timeout=30)
        if version.returncode or version.stdout.strip() != '12.5.0':
            raise RuntimeError('RUNTIME_VERSION_MISMATCH')
        report['runtime_version'] = version.stdout.strip()
        report['resources'] = {s:{'id':v['Id'],'image':v['Config']['Image'],'mounts':[{'name':m['Name'],'destination':m['Destination']} for m in v['Mounts']]} for s,v in owned.items()}
        runtime = ROOT/'runtime/profiles'/args.namespace
        private = private_values(runtime/'p09.env', args.namespace, args.seed)
        if args.seed:
            # Check license before allowing the shared seed to mutate this fixture.
            api = API()
            lic = api.get('/license',api.login('admin',private['P09_ADMIN_PASSWORD']))
            ent = lic['entitlements']['custom_permission_rules_enabled']
            if (ent.get('override') if ent.get('override') is not None else ent.get('default')) is not True:
                raise RuntimeError('BLOCKED_LICENSE')
            report['seed_exit_codes'] = []
            for _ in range(2):
                owned_resources(args.namespace, profile)
                code = seed_fixture(args.namespace, private, runtime, profile)
                report['seed_exit_codes'].append(code)
                if code:
                    raise RuntimeError('SHARED_SEED_FAILED')
                fixture_hash = hashlib.sha256((runtime/'fixture-ids.json').read_bytes()).hexdigest()
                report.setdefault('seed_fixture_hashes',[]).append(fixture_hash)
            if len(set(report['seed_fixture_hashes'])) != 1:
                raise RuntimeError('SEED_IDS_NOT_STABLE')
        report.update(verify(API(), private, runtime))
        report['status'] = 'READY' if all(report['checks'].values()) else 'BLOCKED'
    except Exception as error:
        # Never render exception text, request/response body, subprocess output or secrets.
        allowed = {'BLOCKED_LICENSE','SHARED_SEED_FAILED','SEED_IDS_NOT_STABLE'}
        report['gap'] = str(error) if str(error) in allowed else type(error).__name__
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status':report['status'],'gap':report.get('gap'), 'seed_exit_codes':report.get('seed_exit_codes'), 'report':str(args.report)}))
    return 0 if report['status']=='READY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
