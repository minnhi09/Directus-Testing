"""Offline checks for oracle v2 rules (no lab, no network, no child process)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import oracle_v2 as ov


class OracleV2Tests(unittest.TestCase):
    def test_every_case_without_oracle_has_a_rule(self):
        ids = ov.target_ids()
        self.assertEqual(len(ids), 66)
        self.assertFalse([i for i in ids if ov.rule_for(i) is None])

    def test_rules_carry_prediction_confidence_and_source_refs(self):
        for cid in ov.target_ids():
            rule = ov.rule_for(cid)
            self.assertIn(rule["outcome"], ("ACCEPT", "REJECT", "ACCEPT_OR_REJECT"), cid)
            self.assertIn(rule["confidence"], ("HIGH", "MEDIUM"), cid)
            self.assertTrue(rule["refs"] and all("@" + ov.SHA in ref or "scripts/lab-components.sh" in ref for ref in rule["refs"]), cid)
            self.assertTrue(rule["predicted"], cid)
            self.assertTrue(rule["why"], cid)

    def test_unknown_case_has_no_rule(self):
        self.assertIsNone(ov.rule_for("P3-NOT-A-CASE"))


if __name__ == "__main__":
    unittest.main()
