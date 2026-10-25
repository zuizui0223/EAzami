"""Frozen empirical source-join gates; never imply global tree/climate execution."""
from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from audit_global_nuclear_orientation_multisource_v2 import (  # noqa: E402
    classify, run,
)


class WorldwideNuclearU2DEvidenceJoin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary, cls.rows = run()
        cls.by_name = {r["tree_code"]: r for r in cls.rows}

    def test_exact_source_roster_and_candidate_counts(self):
        x = self.summary
        self.assertEqual(x["moreyra_linked_cirsium_source_rows"], 257)
        self.assertEqual(x["moreyra_distinct_biosamples"], 256)
        self.assertEqual(x["moreyra_tree_code_labels"], 256)
        self.assertEqual(x["source_backed_exact_name_overlaps"], 41)
        self.assertEqual(x["candidate_resolved_orientation_labels"], 30)
        self.assertEqual(x["candidate_U"], 23)
        self.assertEqual(x["candidate_D"], 7)

    def test_ambiguous_source_veto_not_forced(self):
        for taxon in ("Cirsium maritimum", "Cirsium japonicum", "Cirsium fanjingshanense"):
            self.assertEqual(self.by_name[taxon]["orientation_U_D_or_unresolved"], "")
            self.assertEqual(self.by_name[taxon]["status"], "explicit_ambiguous_or_conflict_veto")

    def test_polymorphic_head_orientation_is_not_single_state(self):
        self.assertEqual(self.by_name["Cirsium sieboldii"]["orientation_U_D_or_unresolved"], "")
        self.assertEqual(self.by_name["Cirsium sieboldii"]["status"], "orientation_polymorphism_veto")

    def test_no_orientation_statement_is_neutral_not_conflicting(self):
        self.assertEqual(self.by_name["Cirsium nipponicum"]["orientation_U_D_or_unresolved"], "U")
        self.assertEqual(self.by_name["Cirsium nipponicum"]["status"], "exact_name_evidence_candidate")
        self.assertEqual(classify([
            {"state": "U", "orientation_polymorphism": False},
            {"state": "unknown", "orientation_polymorphism": False},
        ]), ("exact_name_evidence_candidate", "U"))

    def test_opposing_sources_and_polymorphism_fail_closed(self):
        self.assertEqual(classify([
            {"state": "U", "orientation_polymorphism": False},
            {"state": "D", "orientation_polymorphism": False},
        ]), ("conflicting_orientation_sources_veto", ""))
        self.assertEqual(classify([
            {"state": "U", "orientation_polymorphism": False},
            {"state": "U", "orientation_polymorphism": True},
        ]), ("orientation_polymorphism_veto", ""))

    def test_exact_source_examples_not_silent_name_synonyms(self):
        self.assertEqual(self.by_name["Cirsium vulgare"]["orientation_U_D_or_unresolved"], "U")
        self.assertEqual(self.by_name["Cirsium yezoense"]["orientation_U_D_or_unresolved"], "D")
        self.assertEqual(self.by_name["Cirsium lidjiangense"]["orientation_U_D_or_unresolved"], "D")
        self.assertEqual(self.by_name["Cirsium aduncum 1"]["status"], "unassessed_by_available_evidence")
        self.assertEqual(self.by_name["Cirsium aduncum 2"]["status"], "unassessed_by_available_evidence")

    def test_north_american_flora_explicit_heads_are_independent_candidates(self):
        for taxon, expected in (
            ("Cirsium vinaceum", "D"),
            ("Cirsium ownbeyi", "U"),
            ("Cirsium flodmanii", "U"),
            ("Cirsium longistylum", "U"),
        ):
            row = self.by_name[taxon]
            self.assertEqual(row["orientation_U_D_or_unresolved"], expected)
            self.assertEqual(row["status"], "exact_name_evidence_candidate")
            self.assertIn("independent_fna_north_america", row["source_lanes"])
            self.assertIn("flora_id=1", row["source_urls"])
        for taxon in ("Cirsium eatonii", "Cirsium joannae"):
            row = self.by_name[taxon]
            self.assertEqual(row["status"], "explicit_ambiguous_or_conflict_veto")
            self.assertEqual(row["orientation_U_D_or_unresolved"], "")

    def test_no_voucher_claim_and_world_model_still_blocked(self):
        for row in self.rows:
            self.assertEqual(row["same_molecular_voucher_phenotyped"], "false")
            self.assertEqual(row["needs_taxon_name_authority_review"], "true")
        self.assertTrue(all(v is False for v in self.summary["audit_gates"].values()))

    def test_d_coverage_is_not_a_worldwide_replication(self):
        for row in self.rows:
            if row["orientation_U_D_or_unresolved"] == "D":
                self.assertTrue(row["source_lanes"])
                self.assertTrue(row["source_urls"])
        self.assertFalse(self.summary["audit_gates"]["global_transition_regime_model_executed"])


if __name__ == "__main__":
    unittest.main()
