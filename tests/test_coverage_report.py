"""Kiem tra phan hop (union) cua scripts/k05_coverage_report.py bang du lieu tong hop nho."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import k05_coverage_report as cov  # noqa: E402


def seed(keywords, responses=None, hits=1):
    op = {
        "method": "GET",
        "path": "/x",
        "hits": hits,
        "parameters": [{
            "location": "query", "name": "q", "hits": hits,
            "coverage": {"covered": 0, "partial": 0, "total": 3, "percent": 0.0},
            "keywords": keywords,
        }],
        "responses": responses or [],
        "unexpected_responses": [],
    }
    return {"actor": "editor", "profile": "raw", "seed": 1, "cov": {"operations": [op]}}


class UnionKeywordsTest(unittest.TestCase):
    def test_missing_in_one_seed_is_covered(self):
        a = seed([{"schema_path": "/a", "state": "miss"}, {"schema_path": "/b", "state": "miss"}])
        b = seed([{"schema_path": "/a", "state": "miss"}])  # /b du o seed nay
        self.assertEqual(cov.union_keywords([a, b]), {"total": 3, "covered": 2})

    def test_valid_and_invalid_across_seeds_complete_a_keyword(self):
        a = seed([{"schema_path": "/a", "state": "partial", "valid": 2, "invalid": 0}])
        b = seed([{"schema_path": "/a", "state": "partial", "valid": 0, "invalid": 1}])
        self.assertEqual(cov.union_keywords([a, b]), {"total": 3, "covered": 3})

    def test_only_one_side_stays_uncovered(self):
        a = seed([{"schema_path": "/a", "state": "partial", "valid": 2, "invalid": 0}])
        b = seed([{"schema_path": "/a", "state": "partial", "valid": 1, "invalid": 0}])
        self.assertEqual(cov.union_keywords([a, b]), {"total": 3, "covered": 2})


class UnionResponsesTest(unittest.TestCase):
    def test_documented_status_hit_in_any_seed(self):
        a = seed([], responses=[{"status": "200", "hits": 0}, {"status": "401", "hits": 0}])
        b = seed([], responses=[{"status": "200", "hits": 3}, {"status": "401", "hits": 0}])
        u = cov.union_ops_responses([a, b])
        self.assertTrue(u["docs"][(("GET", "/x"), "200")])
        self.assertFalse(u["docs"][(("GET", "/x"), "401")])
        self.assertEqual(u["ops_hit"][("GET", "/x")], 2)


if __name__ == "__main__":
    unittest.main()
