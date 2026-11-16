"""All offline unit tests with no network, real credentials or arbitrary child CLI.

The only real child process permitted is local P01 JSON Schema validation through
coverage_schema.ps1. This is an accidental-I/O guard, not an untrusted-code sandbox.
"""
import contextlib
import io
from pathlib import Path
import shutil
import shlex
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = False


def audit_guard(event, args):
    if not ACTIVE:
        return
    if event in {'socket.connect','socket.getaddrinfo','socket.bind','os.system','os.posix_spawn'}:
        raise RuntimeError('OFFLINE_SUITE_REFUSED_NETWORK_OR_SHELL')
    if event == 'subprocess.Popen':
        executable, command = args[:2]
        # Windows emits the serialized CreateProcess command line at this audit
        # event; POSIX emits the original argv list. No shell is invoked here.
        if isinstance(command,str):
            command=[part[1:-1] if part.startswith('"') and part.endswith('"') else part
                     for part in shlex.split(command,posix=False)]
        pwsh=shutil.which('pwsh')
        if not (pwsh and isinstance(command,(list,tuple)) and len(command)==6
                and Path(executable or command[0]).resolve()==Path(pwsh).resolve()
                and Path(command[0]).resolve()==Path(pwsh).resolve()
                and command[1:3]==['-NoProfile','-File']
                and Path(command[3]).resolve()==(ROOT/'scripts/coverage_schema.ps1').resolve()
                and command[4]=='-Payload' and Path(command[5]).is_file()):
            raise RuntimeError('OFFLINE_SUITE_REFUSED_CHILD_PROCESS')
    if event == 'open' and isinstance(args[0],(str,bytes)):
        path=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).resolve()
        if (path == ROOT/'config/lab.env' or
                (path.is_relative_to(ROOT/'runtime') and path.suffix.lower()=='.env')):
            raise RuntimeError('OFFLINE_SUITE_REFUSED_PRIVATE_PROFILE')


sys.addaudithook(audit_guard)


def run_suite():
    global ACTIVE
    captured=io.StringIO()
    try:
        ACTIVE=True
        with contextlib.redirect_stdout(captured),contextlib.redirect_stderr(captured):
            suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
            result=unittest.TextTestRunner(stream=captured,verbosity=2).run(suite)
    finally:
        ACTIVE=False
    details={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
             'skipped':len(result.skipped),'network':'REFUSED','private_profiles':'REFUSED',
             'real_child_allowlist':['PowerShell7 coverage_schema.ps1 -Payload local-json'],
             'synthetic_unit_logs_are_not_SUT_runs':True,
             'unsuccessful_tests':[test.id() for test,_ in result.failures+result.errors]}
    if not result.wasSuccessful() or result.skipped or result.testsRun==0:
        raise ValueError('Full offline unit gate failed: '+__import__('json').dumps(details))
    return details


if __name__=='__main__':
    import json
    try:
        print(json.dumps(run_suite(),indent=2))
    except ValueError as error:
        print(str(error));sys.exit(1)
