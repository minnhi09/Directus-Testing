"""Offline guards for explicit P09 project integration; never call the SUT."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from designed_cases import Runner, PreconditionError
import p09_runtime


class ProjectGuardTests(unittest.TestCase):
    def test_resume_completed_run_cannot_overwrite_report(self):
        from p10_regression import main
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); out=root/'docs/coverage/runs/P10-20261116-guard'
            out.mkdir(parents=True); (out/'designed-report.json').write_text('{}')
            (out/'run-report.json').write_text('immutable')
            with patch.object(p09_runtime,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'already recorded'):
                    main('r06-k05-p09-test','P10-20261116-guard',True)
            self.assertEqual((out/'run-report.json').read_text(),'immutable')

    def guard(self, map_project, configured):
        stub=SimpleNamespace(lab=SimpleNamespace(fixture_map={'project':map_project,'fixture_version':'r06-k05-v2'},editor_schema={},reader_schema={}))
        with patch.dict(os.environ,{'LAB_PROJECT_NAME':configured}):
            Runner.preflight(stub)

    def test_explicit_p09_reaches_schema_gate_without_aliasing_project(self):
        with self.assertRaisesRegex(PreconditionError,'Export Editor'):
            self.guard('r06-k05-p09-test','r06-k05-p09-test')

    def test_wrong_map_project_stops_before_schema_or_network(self):
        with self.assertRaisesRegex(PreconditionError,'Wrong fixture'):
            self.guard('r06-k05','r06-k05-p09-test')

    def test_foreign_project_rejected(self):
        with self.assertRaisesRegex(PreconditionError,'Unsupported'):
            self.guard('demo','demo')

    def test_component_allowlist_before_resource_lookup(self):
        with patch.object(p09_runtime,'owned_resources') as lookup:
            with self.assertRaises(ValueError):
                p09_runtime.seed_fixture('demo',{},Path('unused'),{},component='raw')
            lookup.assert_not_called()
