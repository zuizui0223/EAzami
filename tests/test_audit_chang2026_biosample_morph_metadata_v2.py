#!/usr/bin/env python3
"""Tests for PRJNA1311153 collector-number reconciliation."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
MODULE_PATH = ANALYSIS_DIR / "audit_chang2026_biosample_morph_metadata_v2.py"
SPEC = importlib.util.spec_from_file_location(
    "audit_chang2026_biosample_morph_metadata_v2", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["audit_chang2026_biosample_morph_metadata_v2"] = mod
SPEC.loader.exec_module(mod)


class ChangCollectorReconciliationTests(unittest.TestCase):
    def seed(self, voucher: str = "ccy3559", code: str = "FC") -> dict[str, str]:
        return {
            "voucher": voucher,
            "code": code,
            "location": "TAIWAN. Chiayi County: Fenchihu",
        }

    def run_row(self, sample_name: str, **updates: str) -> dict[str, str]:
        row = {
            "Run": "SRR35152718",
            "BioSample": "SAMN50798021",
            "ScientificName": "Cirsium japonicum var. japonicum",
            "SampleName": sample_name,
            "LibraryName": "8",
        }
        row.update(updates)
        return row

    def test_collector_number(self) -> None:
        self.assertEqual(mod.collector_number("ccy3559"), "3559")
        self.assertEqual(mod.collector_number("3559"), "3559")
        self.assertEqual(mod.collector_number("FC"), "")

    def test_exact_takaoense_collector_number_matches(self) -> None:
        score, basis = mod.score_seed_run(
            self.seed(),
            self.run_row("Cirsium japonicum var. takaoense-3559"),
        )
        self.assertEqual(score, 95)
        self.assertEqual(
            basis, "exact_takaoense_collector_number_in_sample_name"
        )

    def test_wrong_collector_number_does_not_match(self) -> None:
        score, basis = mod.score_seed_run(
            self.seed(),
            self.run_row("Cirsium japonicum var. takaoense-3560"),
        )
        self.assertEqual(score, 0)
        self.assertEqual(basis, "unmatched")

    def test_same_number_wrong_taxon_does_not_match(self) -> None:
        score, basis = mod.score_seed_run(
            self.seed(),
            self.run_row("Cirsium japonicum var. australe-3559"),
        )
        self.assertEqual(score, 0)
        self.assertEqual(basis, "unmatched")

    def test_direct_voucher_text_remains_highest_priority(self) -> None:
        score, basis = mod.score_seed_run(
            self.seed(),
            self.run_row("Cirsium japonicum var. takaoense-3559", Notes="ccy3559"),
        )
        self.assertEqual(score, 100)
        self.assertEqual(basis, "exact_voucher_in_runinfo")

    def test_six_real_sample_names_match_one_to_one(self) -> None:
        seeds = [
            self.seed("ccy3559", "FC"),
            self.seed("ccy3560", "WY"),
            self.seed("ccy3629", "FB"),
            self.seed("ccy3807", "TJ"),
            self.seed("ccy3835", "NH"),
            self.seed("ccy3839", "LT"),
        ]
        runs = [
            self.run_row(
                f"Cirsium japonicum var. takaoense-{number}",
                Run=f"SRR{number}",
                BioSample=f"SAMN{number}",
            )
            for number in ("3559", "3560", "3629", "3807", "3835", "3839")
        ]
        matches, ambiguous = mod.base.match_runs_to_seeds(seeds, runs)
        self.assertEqual(len(matches), 0, "base matcher should not see the wrapper without patch")
        self.assertEqual(ambiguous, [])

        original = mod.base.score_seed_run
        try:
            mod.base.score_seed_run = mod.score_seed_run
            matches, ambiguous = mod.base.match_runs_to_seeds(seeds, runs)
        finally:
            mod.base.score_seed_run = original
        self.assertEqual(len(matches), 6)
        self.assertEqual(ambiguous, [])
        self.assertEqual(
            matches["ccy3839"][0]["BioSample"], "SAMN3839"
        )
        self.assertTrue(
            all(
                basis == "exact_takaoense_collector_number_in_sample_name"
                for _, basis in matches.values()
            )
        )

    def test_provenance_match_does_not_assign_colour(self) -> None:
        original = mod.base.score_seed_run
        try:
            mod.base.score_seed_run = mod.score_seed_run
            runs = [self.run_row("Cirsium japonicum var. takaoense-3559")]
            matches, _ = mod.base.match_runs_to_seeds([self.seed()], runs)
        finally:
            mod.base.score_seed_run = original
        rows = mod.base.build_audit_rows(
            [
                {
                    "accepted_taxon": mod.base.TARGET_TAXON,
                    "location": "TAIWAN. Chiayi County: Fenchihu",
                    "code": "FC",
                    "coordinate": "x",
                    "altitude_m": "1364",
                    "voucher": "ccy3559",
                    "herbarium_supplement_s1": "TNM",
                }
            ],
            matches,
            {
                "SAMN50798021": {
                    "isolate": "3559",
                    "geo_loc_name": "Taiwan: Chiayi County, Fenchihu",
                }
            },
        )
        self.assertEqual(rows[0]["biosample"], "SAMN50798021")
        self.assertEqual(rows[0]["direct_ncbi_colour_label"], "")
        self.assertEqual(
            rows[0]["review_status"], "no_explicit_ncbi_colour_attribute"
        )


if __name__ == "__main__":
    unittest.main()
