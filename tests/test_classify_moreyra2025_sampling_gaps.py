#!/usr/bin/env python3
"""Tests for sequencing decisions derived from the Moreyra audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "classify_moreyra2025_sampling_gaps.py"
SPEC = importlib.util.spec_from_file_location("classify_moreyra2025_sampling_gaps", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["classify_moreyra2025_sampling_gaps"] = mod
SPEC.loader.exec_module(mod)


class GapClassificationTests(unittest.TestCase):
    def row(self, priority: str, supplement: str, ncbi: str) -> dict[str, str]:
        return {
            "accepted_taxon": "Cirsium testii",
            "focal_region": "East_Asia",
            "priority_class": priority,
            "supplement_match_status": supplement,
            "ncbi_match_status": ncbi,
            "combined_evidence_state": "test",
        }

    def test_covered_transition_moves_to_population_data(self) -> None:
        result = mod.classify(self.row("A_transition", "matched", "matched"))
        self.assertEqual(
            result["species_backbone_class"],
            "modern_nuclear_sample_and_public_reads_verified",
        )
        self.assertIn("RAD-seq_or_resequencing", result["recommended_data"])
        self.assertNotIn("target_capture_then", result["recommended_data"])

    def test_true_transition_gap_requires_target_capture_first(self) -> None:
        result = mod.classify(self.row("A_transition", "not_recovered", "not_recovered"))
        self.assertEqual(
            result["population_history_class"],
            "transition-critical_species_and_population_gap",
        )
        self.assertTrue(result["recommended_data"].startswith("Compositae1061"))

    def test_historical_white_form_requires_verification(self) -> None:
        result = mod.classify(
            self.row("A2_white_form_screen", "not_recovered", "not_recovered")
        )
        self.assertIn("extant_voucher_confirmation", result["population_history_class"])
        self.assertIn("verify_white_morph", result["recommended_data"])

    def test_ranking_is_descending(self) -> None:
        rows = [
            self.row("B_backbone", "matched", "matched"),
            {
                **self.row("A_population_colour", "matched", "matched"),
                "accepted_taxon": "Cirsium highii",
            },
        ]
        ranked = mod.rank(rows)
        self.assertEqual(ranked[0]["accepted_taxon"], "Cirsium highii")
        self.assertGreaterEqual(
            float(ranked[0]["decision_score"]), float(ranked[1]["decision_score"])
        )


if __name__ == "__main__":
    unittest.main()
