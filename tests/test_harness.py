"""Offline regression tests for verdicts, lifecycle and safe replay; no lab writes."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from invariants import Api, ApiResponse, NoRedirect, rejected
from designed_cases import Runner, BudgetExpired, PreconditionError, catalogue, data_object, data_list, same, run_selected, select_cases
from replay_cases import ReplayError, chain_ids, check_match, collection_path, map_ids, remap_request


class VerdictTests(unittest.TestCase):
    def test_course_scope_keeps_invalid_boundaries_and_contract_failure(self):
        cases = select_cases(catalogue(), "course", None, None)
        self.assertEqual({c["id"] for c in cases}, {
            "P3-ST-01", "P3-AUTHZ-DR-047", "P3-SCORE-POST-MINUS1",
            "P3-SCORE-POST-0", "P3-SCORE-POST-5", "P3-SCORE-POST-6",
            "P3-CONTRACT-QA_ARTICLES-OBJECT",
        })
        self.assertEqual(len(cases), 7)
        self.assertEqual(len(select_cases(catalogue(), "short", None, None)), 58)

    def test_course_scope_refuses_missing_case_instead_of_running_partial_suite(self):
        cases = [c for c in catalogue() if c["id"] != "P3-CONTRACT-QA_ARTICLES-OBJECT"]
        with self.assertRaises(ValueError):
            select_cases(cases, "course", None, None)

    def test_category_permission_controls_use_category_fields(self):
        for case in catalogue():
            request = case["request_template"]
            if case["group"] == "authorization" and request["path"].startswith("/items/qa_categories") and request["method"] == "GET":
                self.assertEqual(request["query"]["fields"], "id,name", case["id"])

    def test_denial_requires_status_and_error_code(self):
        for status in (0, 200, 400, 500, 503):
            self.assertFalse(rejected(ApiResponse(status, {"errors": [{"extensions": {"code": "FORBIDDEN"}}]}, b""), 403, {"FORBIDDEN"}))
        self.assertFalse(rejected(ApiResponse(403, {}, b""), 403, {"FORBIDDEN"}))
        self.assertFalse(rejected(ApiResponse(403, {"errors": [{"extensions": {"code": "INVALID_TOKEN"}}]}, b""), 403, {"FORBIDDEN"}))
        self.assertTrue(rejected(ApiResponse(403, {"errors": [{"extensions": {"code": "FORBIDDEN"}}]}, b""), 403, {"FORBIDDEN"}))

    def test_positive_requires_json_shape(self):
        for body in ({}, "<html>error</html>", {"data": None}):
            with self.assertRaises(AssertionError):
                data_object(ApiResponse(200, body, b""))
            with self.assertRaises(AssertionError):
                data_list(ApiResponse(200, body, b""))

    def test_bool_is_not_integer_oracle(self):
        self.assertFalse(same({"id": True}, {"id": 1}))

    def test_status_equality_is_not_reproduced_failure(self):
        source = [{"name": "response_schema_conformance", "status": "failure", "failure_info": {"failure": {"type": "JsonSchemaError"}}}]
        self.assertFalse(check_match(source, [{"name": "response_schema_conformance", "status": "passed"}], 200, 200)["reproduced"])
        self.assertFalse(check_match([], [], 200, 200)["reproduced"])
        actual = [{"name": "response_schema_conformance", "status": "failed", "failures": [{"type": "JsonSchemaError"}]}]
        self.assertTrue(check_match(source, actual, 200, 200)["reproduced"])
        self.assertFalse(check_match(source, actual, 200, 500)["reproduced"])


class ReplayTests(unittest.TestCase):
    def test_typed_mapping_does_not_rewrite_score_metadata_or_limit(self):
        mappings = {"qa_articles": {"5": 105}, "qa_categories": {"5": 205}}
        path, body = remap_request("http://old/items/qa_articles/5?limit=5&filter[id][_eq]=5", {"category": 5, "score": 5, "metadata": {"counter": 5}, "title": "id 5"}, mappings)
        self.assertTrue(path.startswith("/items/qa_articles/105?limit=5&"))
        self.assertIn("105", path)
        self.assertEqual(body, {"category": 205, "score": 5, "metadata": {"counter": 5}, "title": "id 5"})
        self.assertEqual(remap_request("/items/qa_categories/5", {"id": 5}, mappings), ("/items/qa_categories/205", {"id": 5}))

    def test_producer_mapping_uses_identity_not_row_position(self):
        old = {"data": [{"id": 1, "name": "Alpha"}, {"id": 2, "name": "Beta"}]}
        new = {"data": [{"id": 102, "name": "Beta"}, {"id": 101, "name": "Alpha"}]}
        self.assertEqual(map_ids(old, new, "qa_categories"), {"1": 101, "2": 102})
        with self.assertRaises(ReplayError):
            map_ids(old, {"data": [{"id": 101, "name": "Alpha"}, {"id": 102, "name": "Alpha"}]}, "qa_categories")
        with self.assertRaises(ReplayError):
            map_ids({"data": {"id": True, "name": "A"}}, {"data": {"id": 1, "name": "A"}}, "qa_categories")

    def test_missing_or_cyclic_parent_refuses_fallback(self):
        for cases in ({"b": {"parent_id": "missing"}}, {"b": {"parent_id": "a"}, "a": {"parent_id": "b"}}):
            with self.assertRaises(ReplayError):
                chain_ids(cases, "b")
        self.assertEqual(chain_ids({"a": {}, "b": {"parent_id": "a"}}, "b"), ["a", "b"])

    def test_replay_path_scope(self):
        for path in ("/users", "/items/qa_articles/1/nested", "/items/qa_articles/%2e%2e", "/items/other"):
            with self.assertRaises(ReplayError):
                collection_path(path)


class LifecycleTests(unittest.TestCase):
    def test_cleanup_failure_stops_next_case_and_persists_result(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = SimpleNamespace(run_case=Mock(return_value={"id": "a", "status": "failed", "cleanup_status": "failed"}))
            report = {"cases": [], "stop_reason": None}
            run_selected(runner, [{"id": "a"}, {"id": "b"}], report, Path(directory))
            self.assertEqual(runner.run_case.call_count, 1)
            self.assertEqual(report["stop_reason"], "cleanup_failed")
            self.assertEqual(json.loads((Path(directory) / "designed-report.json").read_bytes()), report)

    def test_budget_and_precondition_still_cleanup_and_report(self):
        for failure, status in ((BudgetExpired("budget"), "incomplete"), (PreconditionError("fixture"), "blocked"), (AttributeError("unexpected harness bug"), "failed")):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                runner = object.__new__(Runner)
                runner.run_dir = Path(directory)
                runner.api = SimpleNamespace(scrub=lambda x: x)
                runner.expected = {"baseline": 1}
                runner.snapshot = Mock(return_value=runner.expected)
                runner.assert_snapshot = Mock()
                runner.execute = Mock(side_effect=failure)
                runner.cleanup = Mock()
                design = {"id": "P3-test", "BR": "BR-test", "AC": "AC-test", "actor": "editor", "oracle_readiness": "ASSERTABLE", "expected_response": "known", "expected_state": "unchanged"}
                result = runner.run_case(design)
                self.assertEqual(result["status"], status)
                runner.cleanup.assert_called_once_with(runner.expected)
                self.assertTrue((Path(directory) / "case-P3-test.json").is_file())

    def test_wrong_fixture_sends_no_target(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = object.__new__(Runner)
            runner.run_dir = Path(directory)
            runner.api = SimpleNamespace(scrub=lambda x: x)
            runner.expected = {}
            runner.snapshot = Mock(return_value={"wrong": 1})
            runner.assert_snapshot = Mock(side_effect=AssertionError("fixture mismatch"))
            runner.execute, runner.cleanup = Mock(), Mock()
            design = {"id": "P3-test", "BR": "", "AC": "", "actor": "editor", "oracle_readiness": "ASSERTABLE", "expected_response": "", "expected_state": ""}
            self.assertEqual(runner.run_case(design)["status"], "blocked")
            runner.execute.assert_not_called()

    def test_url_scope_and_redirect_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            for url in ("https://example.org", "http://127.0.0.1:8056", "http://user@directus:8055"):
                with self.assertRaises(RuntimeError):
                    Api(url, Path(directory))
            api = Api("http://127.0.0.1:8055", Path(directory))
            api.opener = Mock()
            for path in ("http://evil/items/qa_articles", "//evil/x", "/items/other", "/items/qa_articles/../users"):
                with self.assertRaises(RuntimeError):
                    api.request("GET", path)
            api.opener.open.assert_not_called()
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "", {}, "https://external"))


if __name__ == "__main__":
    unittest.main()
