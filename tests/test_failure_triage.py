"""Kiem tra quy tac phan loai nguyen nhan cua scripts/k05_failure_triage.py."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import k05_failure_triage as tri  # noqa: E402

BASE = "http://directus:8055"


class Cause5xxTest(unittest.TestCase):
    def test_path_id_outside_int4(self):
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles/9999999999", ""), "RC01")
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories/-173822012232", ""), "RC01")

    def test_path_id_inside_int4_is_not_rc01(self):
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles/2147483647", ""), "RC99")

    def test_aggregate_in_query(self):
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles?aggregate=%7B%22foo%22%3A1%7D", ""), "RC02")

    def test_nul_in_body(self):
        body = json.dumps({"name": "a\u0000b"})
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories", body), "RC04")

    def test_published_at_wrong_type_or_not_a_date(self):
        for value in (False, True, 123, "abc"):
            body = json.dumps([{"title": "t", "score": 1, "published_at": value}])
            self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles", body), "RC03", value)

    def test_valid_published_at_is_not_rc03(self):
        body = json.dumps({"title": "t", "score": 1, "published_at": "2026-11-24T00:00:00Z"})
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles", body), "RC99")

    def test_post_body_id_outside_int4_is_translated_by_directus_so_not_a_cause(self):
        body = json.dumps({"name": "x", "id": 9999999999})
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories", body), "RC99")

    def test_post_body_id_in_exponent_notation_is_rc13(self):
        for raw in ('{"name":"x","id":1e21}', '{"name":"x","id":1e25}'):
            self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories", raw), "RC13", raw)

    def test_wrong_typed_ids_are_rc13(self):
        for body in ([{"id": True, "name": "x"}], [{"id": "", "name": "x"}], {"id": "abc", "name": "x"},
                     {"title": "t", "score": 1, "category": {"id": "abc"}}):
            self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories", json.dumps(body)), "RC13", body)

    def test_null_array_element_is_rc12(self):
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories", "[null]"), "RC12")

    def test_other_query_causes(self):
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_categories?search=a%00b", ""), "RC04")
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles?groupBy=a)b(", ""), "RC16")
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles?groupBy=year(published_at)", ""), "RC99")
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles?limit=897434&page=17592186044417", ""), "RC15")
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles?limit=100&page=1000000", ""), "RC99")
        self.assertEqual(tri.cause_5xx(f"{BASE}/items/qa_articles?fields=sections.item:headings.title&export=csv", ""), "RC14")


class ClassifyTest(unittest.TestCase):
    def test_non_5xx_types(self):
        cases = {
            ("UnsupportedMethodResponse", 404): "RC05",
            ("UndefinedStatusCode", 204): "RC06",
            ("UndefinedStatusCode", 400): "RC07",
            ("UndefinedContentType", 200): "RC08",
            ("JsonSchemaError", 200): "RC09",
            ("RejectedPositiveData", 400): "RC10",
            ("AcceptedNegativeData", 200): "RC11",
        }
        for (ftype, status), expected in cases.items():
            self.assertEqual(tri.classify(ftype, status, f"{BASE}/x", ""), expected, ftype)

    def test_undefined_status_with_5xx_follows_the_cause(self):
        self.assertEqual(tri.classify("UndefinedStatusCode", 500, f"{BASE}/items/qa_articles/9999999999", ""), "RC01")

    def test_every_class_has_a_category(self):
        for rc, (category, text) in tri.RC.items():
            self.assertIn(category, {"PRODUCT", "SCHEMA", "HARNESS", "ENV", "UNRESOLVED"}, rc)
            self.assertTrue(text)


if __name__ == "__main__":
    unittest.main()
