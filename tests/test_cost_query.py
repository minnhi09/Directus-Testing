"""Offline safeguards for P6 selection, counters and interrupted measurements."""
import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cost_query as cq


class CostTests(unittest.TestCase):
    def setUp(self):
        self.model = cq.load_json(cq.DATA / "query-cost-model-v1.json")
        self.catalog = cq.catalogue()

    def test_model_rejects_missing_combo_bad_query_and_lost_pair(self):
        cq.validate_model(self.model, self.catalog)
        broken = copy.deepcopy(self.model)
        broken["cases"].pop()
        altered = copy.deepcopy(self.model)
        altered["cases"][0]["query"]["filter[status][_eq]"] = "published"
        lost = copy.deepcopy(self.model)
        lost["cases"][0]["pairwise"] = False
        for candidate in [broken, altered, lost]:
            with self.subTest(candidate=candidate["cases"][0]["id"]), self.assertRaises(ValueError):
                cq.validate_model(candidate, self.catalog)

    def test_meter_counts_auth_http_error_network_without_credentials(self):
        secret = "private-password-token"
        http_error = urllib.error.HTTPError("http://directus:8055/auth/login", 403, "denied", {}, io.BytesIO())
        opener = SimpleNamespace(open=unittest.mock.Mock(side_effect=[SimpleNamespace(status=200), http_error,
                                                                      urllib.error.URLError("offline")]))
        meter = cq.MeteredOpener(opener)
        request = urllib.request.Request("http://directus:8055/auth/login?hidden=" + secret,
                                         data=secret.encode(), headers={"Authorization": secret})
        self.assertEqual(meter.open(request).status, 200)
        for exception in [urllib.error.HTTPError, urllib.error.URLError]:
            with self.assertRaises(exception):
                meter.open(request)
        self.assertEqual([e["status"] for e in meter.events], [200, 403, None])
        self.assertTrue(meter.events[-1]["network_error"])
        self.assertNotIn(secret, json.dumps(meter.events))

    def run_fake(self, failure):
        class FakeRunner:
            def __init__(self, lab, run_dir, budget):
                self.baseline = {"unchanged": True}
                self.title_order_verified = True
                self.cleaning = False
                self.calls = 0
            def preflight(self):
                pass
            def request(self, *args):
                self.calls += 1
                if self.calls == 2:
                    raise cq.BudgetExpired("test budget")
                return SimpleNamespace(status=200, elapsed=0.01, artifact="fixture.json", body={"data": [{"id": 1}]})
            def expected_query(self, *args):
                return [{"id": 1}]
            def assert_query(self, *args):
                if failure == "oracle":
                    raise AssertionError("wrong projection/order")
            def snapshot(self):
                return self.baseline
            def assert_snapshot(self, actual, expected):
                if failure == "restore":
                    raise AssertionError("state changed")
        lab = SimpleNamespace(api=SimpleNamespace(opener=None, trace=[]), authenticate=lambda: None, load_fixture=lambda: None)
        with tempfile.TemporaryDirectory() as temp, patch.object(cq, "Runner", FakeRunner):
            rc = cq.execute(lab, Path(temp), self.model, "pairwise", "offline")
            return rc, json.loads((Path(temp) / "cost-query-report.json").read_text())

    def test_budget_retains_partial_report_and_runs_state_guard(self):
        rc, report = self.run_fake("budget")
        self.assertEqual(rc, 1)
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["verification"], "PASS")
        self.assertEqual(len(report["not_run"]), 7)

    def test_oracle_failure_cannot_be_pass(self):
        rc, report = self.run_fake("oracle")
        self.assertEqual(rc, 1)
        self.assertEqual(report["results"][0]["verdict"], "FAIL")
        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["verification"], "PASS")

    def test_state_guard_failure_overrides_incomplete(self):
        rc, report = self.run_fake("restore")
        self.assertEqual(rc, 1)
        self.assertEqual(report["verification"], "FAIL")
        self.assertEqual(report["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
