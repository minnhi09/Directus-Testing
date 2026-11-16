#!/usr/bin/env python3
"""P02 static/offline checks; no lab, network, package installation or env file."""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
WORKFLOW = ROOT / '.github/workflows/static-offline.yml'
guard_active = False


class MissingTool(RuntimeError):
    pass


def offline_guard(event, args):
    if not guard_active:
        return
    if event in {'socket.connect', 'socket.getaddrinfo', 'socket.bind',
                 'subprocess.Popen', 'os.system', 'os.posix_spawn'}:
        raise RuntimeError('P02 offline guard refused network or process execution')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = Path(args[0].decode() if isinstance(args[0], bytes) else args[0])
        if path.resolve() == (ROOT / 'config/lab.env').resolve():
            raise RuntimeError('P02 offline guard refused lab.env access')


sys.addaudithook(offline_guard)


@contextlib.contextmanager
def guarded():
    global guard_active
    guard_active = True
    try:
        yield
    finally:
        guard_active = False


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('Non-JSON numeric constant: ' + value)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=no_duplicate_keys,
                      parse_constant=invalid_constant)


def python_syntax():
    paths = sorted((ROOT / 'scripts').glob('*.py')) + sorted((ROOT / 'tests').glob('*.py'))
    for path in paths:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    return {'files_parsed': len(paths), 'bytecode_written': False}


def json_syntax():
    paths = sorted((ROOT / 'scripts/data').glob('*.json'))
    paths += sorted((ROOT / 'docs/coverage/schemas').glob('*.json'))
    paths += sorted((ROOT / 'docs/coverage/examples').glob('*.json'))
    for path in paths:
        read_json(path)
    records = 0
    for path in sorted((ROOT / 'docs/coverage/examples').glob('*.jsonl')):
        for line in path.read_text(encoding='utf-8').splitlines():
            json.loads(line, object_pairs_hook=no_duplicate_keys, parse_constant=invalid_constant)
            records += 1
    return {'json_files': len(paths), 'jsonl_records': records}


def catalog_selectors():
    with guarded():
        import designed_cases as dc
        import cost_query as cq
        catalog = dc.catalogue()
        ids = [row['id'] for row in catalog]
        if len(ids) != len(set(ids)):
            raise ValueError('Catalog IDs are not unique')
        selections = {}
        for selection in ('course', 'short', 'assertable', 'all'):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), patch.object(
                    sys, 'argv', ['designed_cases.py', '--selection', selection, '--list']):
                if dc.main() != 0:
                    raise ValueError('Selector --list returned nonzero')
            listed = json.loads(output.getvalue())
            selected_ids = [row['id'] for row in listed]
            if len(selected_ids) != len(set(selected_ids)) or not set(selected_ids) <= set(ids):
                raise ValueError('Selector returned duplicate or unknown IDs')
            selections[selection] = len(listed)
        if 'P3-CONTRACT-QA_ARTICLES-OBJECT' not in {
                row['id'] for row in dc.select_cases(catalog, 'course', None, None)}:
            raise ValueError('Course selector lost the known contract case')
        cq.validate_model(dc.load_json(dc.DATA / 'query-cost-model-v1.json'), catalog)
        if dc.load_json(dc.DATA / 'query-cost-protocol-v1.json')['protocol_id'] != 'P6-COST-v1':
            raise ValueError('Unexpected query-cost protocol')
    return {'catalog_ids': len(ids), 'selector_sizes': selections,
            'meaning': 'design/selection validation, not executed API cases'}


def bash_syntax():
    # Prefer Git Bash on Windows; do not accidentally start WSL's bash.exe.
    if sys.platform == 'win32':
        git = shutil.which('git')
        executable = Path(git).resolve().parents[1] / 'bin/bash.exe' if git else Path('')
        if not executable.is_file():
            raise MissingTool('Git Bash missing; no WSL fallback or installation')
        bash = str(executable)
    else:
        bash = shutil.which('bash')
        if not bash:
            raise MissingTool('bash missing; no installation')
    paths = [ROOT / 'lab.sh', ROOT / 'scripts/lab-components.sh']
    for path in paths:
        subprocess.run([bash, '--noprofile', '--norc', '-n', path.name],
                       cwd=path.parent, check=True, capture_output=True, text=True)
    version = subprocess.run([bash, '--version'], check=True, capture_output=True,
                             text=True).stdout.splitlines()[0]
    return {'files_parsed': len(paths), 'bash_version': version, 'scripts_executed': False}


def powershell_and_examples():
    pwsh = shutil.which('pwsh')
    if not pwsh:
        raise MissingTool('pwsh/Test-Json missing; no installation')
    result = subprocess.run([pwsh, '-NoProfile', '-NonInteractive', '-File',
                             str(ROOT / 'scripts/check_coverage_examples.ps1')],
                            cwd=ROOT, check=True, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)


def markdown_links():
    paths = [ROOT / 'docs/CI_STATIC_OFFLINE.md']
    paths += sorted((ROOT / 'docs/coverage').rglob('*.md'))
    links = 0
    for path in paths:
        text = path.read_text(encoding='utf-8')
        link_base = path.parent
        # Immutable plan snapshots retain links relative to their original docs/
        # location. Verify their content-addressed name before resolving there.
        if path.parent == ROOT / 'docs/coverage/sources' and path.name in {
                'plan-72d6707cd28a.md', 'plan-da96feb6774e.md'}:
            prefix = path.stem.removeprefix('plan-')
            if not hashlib.sha256(path.read_bytes()).hexdigest().startswith(prefix):
                raise ValueError('Archived plan fingerprint mismatch: ' + path.name)
            link_base = ROOT / 'docs'
        if not text.endswith('\n') or any(line.rstrip() != line for line in text.splitlines()):
            raise ValueError('Markdown newline/whitespace error: ' + path.name)
        for target in re.findall(r'\]\(([^)]+)\)', text):
            parsed = urlsplit(target.strip('<>'))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue  # No HTTP calls or whole-repo legacy link audit.
            candidate = (link_base / unquote(parsed.path)).resolve()
            if not candidate.is_relative_to(ROOT) or not candidate.exists():
                raise ValueError('Missing/outside-repo local Markdown target: ' + path.name)
            links += 1
    return {'markdown_files': len(paths), 'local_link_targets': links,
            'external_links_checked': False, 'fragments_checked': False}


def workflow_contract():
    # JSON is a YAML 1.2 subset, so this .yml needs no additional YAML package.
    workflow = read_json(WORKFLOW)
    if set(workflow['on']) != {'push', 'pull_request', 'workflow_dispatch'}:
        raise ValueError('Unexpected workflow trigger')
    if workflow['permissions'] != {'contents': 'read'}:
        raise ValueError('Unexpected workflow permissions')
    if set(workflow['jobs']) != {'static-offline'}:
        raise ValueError('P02 workflow must contain only the static job')
    job = workflow['jobs']['static-offline']
    if 'container' in job or 'services' in job or job['runs-on'] != 'ubuntu-24.04':
        raise ValueError('Static job must not create integration services')
    steps = job['steps']
    if len(steps) != 3:
        raise ValueError('Unexpected additional workflow step')
    if steps[0]['uses'] != 'actions/checkout@v6' or steps[0]['with']['persist-credentials'] is not False:
        raise ValueError('Unexpected checkout configuration')
    if steps[1]['run'] != 'python3 scripts/check_offline.py --output-dir artifacts/runs/p02-static':
        raise ValueError('Unexpected static command')
    upload = steps[2]
    if (upload['uses'] != 'actions/upload-artifact@v6' or upload['if'] != 'always()'
            or upload['with']['path'] != 'artifacts/runs/p02-static/offline-summary.json'
            or upload['with']['retention-days'] != 14 or upload['with']['if-no-files-found'] != 'error'):
        raise ValueError('Artifact must be the small summary, even after check failure')
    for node in [workflow, job, *steps]:
        if any(k in node for k in ('continue-on-error', 'secrets', 'env')):
            raise ValueError('Static checks cannot use secrets or hide errors')
    if 'permissions' in job or 'secrets.' in json.dumps(workflow):
        raise ValueError('Static job cannot override permissions or reference secrets')
    return {'format': 'JSON-compatible YAML 1.2', 'remote_run_verified': False}


def unit_harness():
    from offline_suite import run_suite
    return run_suite()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    output = args.output_dir or ROOT / 'artifacts/runs' / now.strftime('p02-static-%Y%m%dT%H%M%S%fZ')
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    if not output.is_relative_to((ROOT / 'artifacts/runs').resolve()):
        parser.error('output-dir must stay within artifacts/runs')
    output.mkdir(parents=True, exist_ok=False)  # Never overwrite earlier evidence.
    in_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    report = {'schema': 1, 'phase': 'P02', 'kind': 'STATIC_OFFLINE_CHECKS',
              'started_at': now.isoformat(), 'run_id': output.name,
              'python_version': platform.python_version(), 'checks': [],
              'integration': {'execution_status': 'NOT_RUN',
                              'reason': 'P02 static-only; no lab/license/environment gate verified'},
              'directus_code_coverage': 'NOT_MEASURED',
              'execution_context': 'GITHUB_ACTIONS' if in_actions else 'LOCAL',
              'remote_ci': 'IN_PROGRESS' if in_actions else 'NOT_RUN',
              'github_run_id': os.environ.get('GITHUB_RUN_ID') if in_actions else None,
              'github_run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT') if in_actions else None,
              'workflow_conclusion': 'UNVERIFIED' if in_actions else 'NOT_RUN'}
    for key, command in [('harness_sha', ['git', 'rev-parse', 'HEAD']),
                         ('working_tree', ['git', 'status', '--porcelain=v1'])]:
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        value = process.stdout.strip()
        report[key] = ('DIRTY' if value else 'CLEAN') if key == 'working_tree' else value
        if process.returncode:
            report[key] = 'UNKNOWN'
    checks = [python_syntax, json_syntax, catalog_selectors, bash_syntax,
              powershell_and_examples, markdown_links, workflow_contract, unit_harness]
    for check in checks:
        record = {'name': check.__name__}
        try:
            record.update(status='PASS', details=check())
        except MissingTool as error:
            record.update(status='BLOCKED', reason=str(error))
        except Exception as error:
            record.update(status='FAIL', error_type=type(error).__name__)
            if isinstance(error, subprocess.CalledProcessError):
                record['process_exit_code'] = error.returncode
            elif isinstance(error, (ValueError, SyntaxError)):
                record['reason'] = str(error)
        report['checks'].append(record)
        print(check.__name__ + ': ' + record['status'])
    exit_code = int(any(r['status'] != 'PASS' for r in report['checks']))
    report.update(exit_code=exit_code, finished_at=datetime.now(timezone.utc).isoformat())
    paths = [WORKFLOW, ROOT / 'lab.sh', ROOT / 'scripts/lab-components.sh']
    for directory, pattern in [('scripts', '*.py'), ('scripts', '*.ps1'),
                               ('scripts/windows', '*.ps1'), ('tests', '*.py'),
                               ('scripts/data', '*.json'), ('docs/coverage/schemas', '*.json'),
                               ('docs/coverage/examples', '*.json'), ('docs/coverage/examples', '*.jsonl')]:
        paths.extend(sorted((ROOT / directory).glob(pattern)))
    report['input_sha256'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in paths}
    (output / 'offline-summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Report: ' + str(output.relative_to(ROOT) / 'offline-summary.json'))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
