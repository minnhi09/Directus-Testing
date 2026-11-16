"""Read-only P09 preflight; never start/stop/reset a lab or read old lab.env."""
import argparse
import hashlib
import json
import re
import shutil
import socket
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'profiles/p09/compose.json'


def namespace(value):
    if not re.fullmatch(r'r06-k05-p09-[a-z0-9][a-z0-9-]{0,35}', value):
        raise ValueError('P09_NAMESPACE_REQUIRED')
    return value


def check_profile(profile):
    assert set(profile['services']) == {'database', 'directus', 'runner'}
    for svc in profile['services'].values():
        assert re.search(r'@sha256:[0-9a-f]{64}$', svc['image'])
        assert not svc.get('container_name')
        for mount in svc.get('volumes', []):
            assert mount.split(':')[0] in profile['volumes']
    assert 'ports' not in profile['services']['database']
    assert profile['services']['directus']['ports'] == ['127.0.0.1:18055:8055']
    for name, cfg in {**profile['volumes'], **profile['networks']}.items():
        assert not cfg.get('external') and cfg['name'].startswith('${P09_NAMESPACE}_')
        assert cfg['labels']['damh.phase'] == 'P09'
    assert profile['name'] == '${P09_NAMESPACE:?P09_NAMESPACE required}'


def command(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=20)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 124, ''


def run(ns):
    namespace(ns)
    profile = json.loads(PROFILE.read_text(encoding='utf-8'))
    check_profile(profile)
    report = dict(schema='P09_PREFLIGHT_1', created_at=datetime.now(timezone.utc).isoformat(),
                  namespace=ns, profile_sha256=hashlib.sha256(PROFILE.read_bytes()).hexdigest(),
                  host_url='http://127.0.0.1:18055', runner_url='http://directus:8055',
                  actor_roles=['admin-bootstrap', 'editor', 'reader', 'anonymous'],
                  actor_identity='NOT_VERIFIED', profile_isolation='PASS_STATIC',
                  created_resources=[], campaign='NOT_RUN', coverage='NOT_MEASURED',
                  runtime_checks={k:'BLOCKED' for k in ['health','version','license','policy','fixture','CLI_help']},
                  tracecov='CHƯA XÁC MINH', old_lab_touched=False)
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', 18055))
            report['loopback_port_available'] = True
        except OSError:
            report['loopback_port_available'] = False
    docker = shutil.which('docker')
    if not docker:
        report.update(status='BLOCKED', gap='DOCKER_CLI_MISSING')
        return report
    rc, version = command([docker, 'compose', 'version', '--short'])
    report['compose_version'] = version.strip() if rc == 0 else None
    # Only synthetic values, never copy credentials or license from the old lab.
    with tempfile.TemporaryDirectory(prefix='damh-p09-config-') as tmp:
        env = Path(tmp) / 'example.env'
        env.write_text('P09_NAMESPACE='+ns+'\nP09_DB_PASSWORD=STATIC_ONLY\nP09_KEY=STATIC_ONLY\n'
                       'P09_SECRET=STATIC_ONLY_NOT_RUNTIME_SECRET_32\nP09_ADMIN_PASSWORD=STATIC_ONLY\n', encoding='utf-8')
        rc, rendered = command([docker, 'compose', '--project-name', ns, '--env-file', str(env),
                                '--file', str(PROFILE), 'config', '--format', 'json'])
        report['compose_config_exit_code'] = rc
        if rc == 0:
            config = json.loads(rendered)
            assert config['name'] == ns
            assert all(v['name'].startswith(ns+'_') for v in config['volumes'].values())
    rc, data = command([docker, 'version', '--format', '{{json .Server}}'])
    report['docker_engine_exit_code'] = rc
    if rc != 0 or data.strip() in ('', 'null'):
        report.update(status='BLOCKED', gap='DOCKER_LINUX_ENGINE_UNREACHABLE',
                      resource_ownership='CHƯA XÁC MINH; engine unavailable, no existing lab reused')
        return report
    report['server_version'] = json.loads(data).get('Version')
    rc, containers = command([docker, 'ps', '-a', '--filter', 'label=com.docker.compose.project='+ns,
                              '--format', '{{.ID}}'])
    report['namespace_existing_container_count'] = len(containers.splitlines()) if rc == 0 else None
    report.update(status='BLOCKED', gap='RUNTIME_AUTHENTICATED_GATES_PENDING' if containers.strip() else 'RUNTIME_PROFILE_NOT_STARTED',
                  resource_ownership='Must check containers/networks/volumes before starting this fresh namespace')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--namespace', required=True, type=namespace)
    args = parser.parse_args()
    result = run(args.namespace)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit(0 if result['status'] == 'READY' else 2)
