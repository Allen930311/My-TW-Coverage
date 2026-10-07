import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import event_census
import freshness


class FreshnessTests(unittest.TestCase):
    def test_roc_date(self):
        self.assertEqual(event_census.parse_roc_date("1150704").isoformat(), "2026-07-04")
        self.assertEqual(event_census.parse_roc_date("115/07/04").isoformat(), "2026-07-04")
        self.assertIsNone(event_census.parse_roc_date("bad"))

    def test_roc_month(self):
        self.assertEqual(event_census.parse_roc_month("11506"), "2026-06")
        self.assertIsNone(event_census.parse_roc_month("115060"))

    def test_material_event_actions(self):
        actions = event_census.actions_for_material_event("公告新客戶訂單", "預期擴充產能")
        self.assertIn("revalidate_supply_chain", actions)
        self.assertIn("revalidate_company_profile", actions)

    def test_timestamp_classification(self):
        rule = {"max_age_hours": 24}
        now = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
        self.assertEqual(freshness.classify_timestamp("2026-10-07T00:00:00Z", rule, now), "FRESH")
        self.assertEqual(freshness.classify_timestamp("2026-10-05T00:00:00Z", rule, now), "STALE")
        self.assertEqual(freshness.classify_timestamp(None, rule, now), "UNKNOWN")
        self.assertEqual(freshness.classify_timestamp("2026-10-08T12:00:00Z", rule, now), "BLOCKED")

    def test_publication_gate_fail_closed(self):
        contract = {
            "publication_gate": {
                "always_required": ["listing_universe", "financials"],
                "claim_scoped": {"supply_chain_claim": ["supply_chain"]},
                "allowed_statuses": ["FRESH"],
            }
        }
        states = {"listing_universe": "FRESH", "financials": "FRESH", "supply_chain": "UNKNOWN"}
        gate = freshness.publication_gate(states, contract, ["supply_chain_claim"])
        self.assertFalse(gate["ready"])
        self.assertEqual(gate["blockers"]["supply_chain"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
