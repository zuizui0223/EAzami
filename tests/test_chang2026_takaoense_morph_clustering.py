#!/usr/bin/env python3
"""Tests for exact W/BP label clustering on the Chang six-tip tree."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
MODULE_PATH = ANALYSIS_DIR / "chang2026_takaoense_morph_clustering.py"
SPEC = importlib.util.spec_from_file_location(
    "chang2026_takaoense_morph_clustering", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
clustering = importlib.util.module_from_spec(SPEC)
sys.modules["chang2026_takaoense_morph_clustering"] = clustering
SPEC.loader.exec_module(clustering)


class TakaoenseMorphClusteringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = clustering.allocation_rows()
        self.summary = clustering.summarize(self.rows)

    def test_six_unique_tips(self) -> None:
        tips = clustering.tip_names(clustering.TAKAOENSE_SIX)
        self.assertEqual(len(tips), 6)
        self.assertEqual(len(set(tips)), 6)
        self.assertEqual(
            set(tips),
            set(clustering.OBSERVED_BP | clustering.OBSERVED_W),
        )

    def test_all_twenty_balanced_allocations_are_enumerated(self) -> None:
        self.assertEqual(len(self.rows), 20)
        self.assertEqual(
            {int(row["allocation_index"]) for row in self.rows},
            set(range(1, 21)),
        )
        for row in self.rows:
            self.assertEqual(len(str(row["bp_tips"]).split("|")), 3)
            self.assertEqual(len(str(row["w_tips"]).split("|")), 3)

    def test_observed_assignment_has_one_change(self) -> None:
        observed = [
            row for row in self.rows
            if row["is_observed_oriented_assignment"] == "yes"
        ]
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]["fitch_changes"], 1)
        self.assertEqual(observed[0]["fitch_root_states"], "W")
        self.assertEqual(
            observed[0]["bp_tips"],
            "FC_3559_BP|NH_3835_BP|TJ_3807_BP",
        )

    def test_score_distribution_is_frozen(self) -> None:
        self.assertEqual(
            self.summary["score_distribution"],
            {"1": 2, "2": 10, "3": 8},
        )
        self.assertEqual(self.summary["observed_fitch_changes"], 1)
        self.assertEqual(self.summary["minimum_possible_fitch_changes"], 1)

    def test_exact_probabilities(self) -> None:
        self.assertEqual(self.summary["oriented_observed_allocations"], 1)
        self.assertEqual(
            self.summary["unordered_observed_partition_allocations"], 2
        )
        self.assertEqual(
            self.summary["allocations_at_least_as_clustered_as_observed"], 2
        )
        self.assertAlmostEqual(
            self.summary["exact_oriented_assignment_probability"], 0.05
        )
        self.assertAlmostEqual(
            self.summary["exact_unordered_partition_probability"], 0.10
        )
        self.assertAlmostEqual(
            self.summary["exact_at_least_as_clustered_probability"], 0.10
        )

    def test_only_observed_partition_and_colour_swapped_complement_score_one(self) -> None:
        one_change = [row for row in self.rows if row["fitch_changes"] == 1]
        self.assertEqual(len(one_change), 2)
        self.assertTrue(
            all(
                row["is_observed_unordered_partition"] == "yes"
                for row in one_change
            )
        )
        self.assertEqual(
            sum(
                row["is_observed_oriented_assignment"] == "yes"
                for row in one_change
            ),
            1,
        )

    def test_summary_retains_topology_and_caveat(self) -> None:
        self.assertEqual(
            self.summary["topology"],
            "(((((NH_BP,TJ_BP),FC_BP),LT_W),FB_W),WY_W)",
        )
        self.assertIn("conditional", self.summary["caveat"].lower())
        self.assertIn("altitude", self.summary["caveat"].lower())
        self.assertIn("reticulation", self.summary["caveat"].lower())


if __name__ == "__main__":
    unittest.main()
