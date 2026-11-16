import copy
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('p09', Path(__file__).resolve().parents[1]/'scripts/p09_preflight.py')
p09 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p09)


class IsolationTests(unittest.TestCase):
    def test_profile_isolated(self):
        p09.check_profile(json.loads(p09.PROFILE.read_text()))

    def test_legacy_namespace_rejected(self):
        for name in ['r06-k05', 'demo', '../other']:
            with self.assertRaises(ValueError):
                p09.namespace(name)

    def test_bind_to_old_host_storage_rejected(self):
        p = json.loads(p09.PROFILE.read_text())
        p['services']['directus']['volumes'] = ['D:/demo:/directus/uploads']
        with self.assertRaises(AssertionError):
            p09.check_profile(p)

    def test_external_volume_rejected(self):
        p = json.loads(p09.PROFILE.read_text())
        p['volumes']['db_data']['external'] = True
        with self.assertRaises(AssertionError):
            p09.check_profile(p)
