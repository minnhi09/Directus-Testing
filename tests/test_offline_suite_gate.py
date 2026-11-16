"""Accidental-I/O guard tests. No real process/network/credential access."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import offline_suite as gate


class OfflineGateTests(unittest.TestCase):
    def test_network_and_shell_rejected(self):
        with patch.object(gate,'ACTIVE',True):
            for event in ('socket.connect','socket.getaddrinfo','socket.bind','os.system','os.posix_spawn'):
                with self.assertRaisesRegex(RuntimeError,'REFUSED'):gate.audit_guard(event,())

    def test_private_profile_blocked_before_read(self):
        with patch.object(gate,'ACTIVE',True):
            for path in (gate.ROOT/'config/lab.env',gate.ROOT/'runtime/profiles/p09/p09.env'):
                with self.assertRaisesRegex(RuntimeError,'PRIVATE_PROFILE'):gate.audit_guard('open',(str(path),'r',0))

    def test_arbitrary_child_commands_refused(self):
        with patch.object(gate,'ACTIVE',True):
            for argv in (['docker','ps'],['git','show'],['pwsh','-Command','Get-Date']):
                with self.assertRaisesRegex(RuntimeError,'CHILD_PROCESS'):gate.audit_guard('subprocess.Popen',(argv[0],argv,None,None))

    def test_schema_command_accepts_native_argv_and_windows_serialization(self):
        with tempfile.TemporaryDirectory(prefix='offline gate ') as d:
            root=Path(d);script=root/'scripts/coverage_schema.ps1';script.parent.mkdir();script.write_text('# offline fixture')
            payload=root/'payload.json';payload.write_text('[]');executable=str(root/'pwsh.exe')
            argv=[executable,'-NoProfile','-File',str(script),'-Payload',str(payload)]
            with patch.object(gate,'ROOT',root),patch.object(gate,'ACTIVE',True),patch.object(gate.shutil,'which',return_value=executable):
                gate.audit_guard('subprocess.Popen',(executable,argv,None,None))
                gate.audit_guard('subprocess.Popen',(None,subprocess.list2cmdline(argv),None,None))
                argv[3]=str(root/'untrusted.ps1')
                with self.assertRaisesRegex(RuntimeError,'CHILD_PROCESS'):gate.audit_guard('subprocess.Popen',(None,subprocess.list2cmdline(argv),None,None))


if __name__=='__main__':unittest.main()
