#!/usr/bin/env python3
"""Offline tests for the PRJNA1311153 takaoense BioSample audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
MODULE_PATH = ANALYSIS_DIR / "audit_chang2026_biosample_morph_metadata.py"
SPEC = importlib.util.spec_from_file_location(
    "audit_chang2026_biosample_morph_metadata", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["audit_chang2026_biosample_morph_metadata"] = mod
SPEC.loader.exec_module(mod)


class ChangBioSampleMorphAuditTests(unittest.TestCase):
    def seed(self, voucher: str = "ccy3559", code: str = "FC") -> dict[str, str]:
        return {
            "accepted_taxon": mod.TARGET_TAXON,
            "location": "TAIWAN. Chiayi County: Fenchihu",
            "code": code,
            "coordinate": "23°30'N, 120°41'E",
            "altitude_m": "1364",
            "voucher": voucher,
            "herbarium_supplement_s1": "TNM",
        }

    def run_row(self, **updates: str) -> dict[str, str]:
        row = {
            "Run": "SRR1",
            "Experiment": "SRX1",
            "BioSample": "SAMN1",
            "ScientificName": "Cirsium japonicum var. takaoense",
            "LibraryName": "ccy3559_FC",
            "SampleName": "Fenchihu",
        }
        row.update(updates)
        return row

    def test_seed_filter_expands_abbreviated_genus(self) -> None:
        rows = [
            {
                "taxon": "C. japonicum var. takaoense",
                "location": "Fenchihu",
                "code": "FC",
                "coordinate": "x",
                "altitude_m": "1",
                "voucher": "ccy3559",
                "herbarium": "TNM",
            },
            {"taxon": "C. japonicum var. australe", "voucher": "other"},
        ]
        selected = mod.target_seed_rows(rows)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["voucher"], "ccy3559")

    def test_exact_voucher_match_has_priority(self) -> None:
        score, basis = mod.score_seed_run(self.seed(), self.run_row())
        self.assertEqual(score, 100)
        self.assertEqual(basis, "exact_voucher_in_runinfo")

    def test_sample_code_match_is_allowed_for_identity_not_colour(self) -> None:
        run = self.run_row(LibraryName="FC", SampleName="unknown")
        score, basis = mod.score_seed_run(self.seed(), run)
        self.assertEqual(score, 80)
        self.assertEqual(basis, "exact_sample_code_in_runinfo")

    def test_locality_can_link_metadata_but_does_not_assign_morph(self) -> None:
        run = self.run_row(LibraryName="unknown", SampleName="Fenchihu")
        score, basis = mod.score_seed_run(self.seed(), run)
        self.assertEqual(score, 50)
        self.assertIn("explicit_locality_in_runinfo", basis)
        rows = mod.build_audit_rows(
            [self.seed()],
            {"ccy3559": (run, basis)},
            {"SAMN1": {"geo_loc_name": "Taiwan: Fenchihu"}},
        )
        self.assertEqual(rows[0]["direct_ncbi_colour_label"], "")
        self.assertEqual(
            rows[0]["review_status"], "no_explicit_ncbi_colour_attribute"
        )

    def test_explicit_white_attribute_assigns_W(self) -> None:
        relevant = [("phenotype", "white-flowered morph")]
        self.assertEqual(
            mod.direct_colour_state(relevant),
            ("W", "white", "assigned_from_explicit_ncbi_attribute"),
        )

    def test_explicit_bluish_purple_attribute_assigns_BP(self) -> None:
        relevant = [("flower color", "bluish-purple")]
        self.assertEqual(
            mod.direct_colour_state(relevant),
            ("BP", "bluish-purple", "assigned_from_explicit_ncbi_attribute"),
        )

    def test_polymorphic_attribute_remains_ambiguous(self) -> None:
        relevant = [("phenotype", "white and bluish-purple corolla polymorphism")]
        self.assertEqual(
            mod.direct_colour_state(relevant),
            ("", "", "ambiguous_or_polymorphic_ncbi_attribute"),
        )

    def test_generic_metadata_does_not_assign_colour(self) -> None:
        relevant = [("sample description", "flowering plant collected at Fenchihu")]
        self.assertEqual(
            mod.direct_colour_state(relevant),
            ("", "", "no_explicit_ncbi_colour_attribute"),
        )

    def test_ambiguous_run_matches_are_not_silently_chosen(self) -> None:
        seed = self.seed(voucher="ccy9999", code="FC")
        runs = [
            self.run_row(Run="SRR1", BioSample="SAMN1", LibraryName="FC"),
            self.run_row(Run="SRR2", BioSample="SAMN2", LibraryName="FC"),
        ]
        matches, ambiguous = mod.match_runs_to_seeds([seed], runs)
        self.assertEqual(matches, {})
        self.assertEqual(len(ambiguous), 1)
        self.assertEqual(ambiguous[0]["candidate_runs"], "SRR1|SRR2")

    def test_build_audit_requires_direct_attribute_for_assignment(self) -> None:
        rows = mod.build_audit_rows(
            [self.seed()],
            {"ccy3559": (self.run_row(), "exact_voucher_in_runinfo")},
            {
                "SAMN1": {
                    "geo_loc_name": "Taiwan: Fenchihu",
                    "collection_date": "2024",
                    "flower color": "white",
                }
            },
        )
        self.assertEqual(rows[0]["direct_ncbi_colour_label"], "W")
        self.assertEqual(rows[0]["binary_colour_code"], "W")
        self.assertEqual(rows[0]["assignment_confidence"], "high")
        self.assertIn("flower color=white", rows[0]["morph_relevant_attributes"])


if __name__ == "__main__":
    unittest.main()
