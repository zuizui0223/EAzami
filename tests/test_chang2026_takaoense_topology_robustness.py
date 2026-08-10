#!/usr/bin/env python3
"""Tests for exhaustive Chang 2026 takaoense topology sensitivity."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import chang2026_takaoense_topology_robustness as mod  # noqa: E402


class TakaoenseTopologyRobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = mod.analyse_topologies()
        cls.groups = mod.build_group_summaries(cls.rows)
        cls.group_index = {row["group"]: row for row in cls.groups}
        cls.minimum_distance, cls.nearest = mod.nearest_no_regain_rows(cls.rows)
        cls.summary = mod.build_summary(
            cls.rows, cls.groups, cls.minimum_distance, cls.nearest
        )

    def test_enumerates_all_rooted_binary_topologies(self) -> None:
        self.assertEqual(
            len(mod.all_rooted_binary_trees(mod.SAMPLE_LABELS)), 945
        )
        four_tips = ("a", "b", "c", "d")
        self.assertEqual(len(mod.all_rooted_binary_trees(four_tips)), 15)

    def test_topology_newicks_are_unique(self) -> None:
        newicks = [row["sample_topology_newick"] for row in self.rows]
        self.assertEqual(len(newicks), len(set(newicks)))

    def test_published_topology_reproduces_two_change_regain_result(self) -> None:
        published = [
            row for row in self.rows if row["is_published_topology"] == "true"
        ]
        self.assertEqual(len(published), 1)
        row = published[0]
        self.assertEqual(row["topology_id"], "T0297")
        self.assertEqual(row["rooted_rf_distance_from_published"], 0)
        self.assertEqual(row["sinocirsium_coloured_root_minimum_changes"], 2)
        self.assertEqual(
            row["sinocirsium_coloured_root_optimal_histories"], "1L+1R"
        )
        self.assertEqual(row["regain_required_at_global_minimum"], "true")
        self.assertEqual(row["minimum_no_regain_changes"], 4)
        self.assertEqual(row["no_regain_penalty"], 2)

    def test_every_single_split_perturbation_still_requires_regain(self) -> None:
        group = self.group_index[
            "published_plus_single_split_perturbations"
        ]
        self.assertEqual(group["topology_count"], 9)
        self.assertEqual(group["regain_required_count"], 9)
        self.assertEqual(group["no_regain_equal_optimum_count"], 0)
        self.assertEqual(group["no_regain_penalty_1_count"], 4)
        self.assertEqual(group["no_regain_penalty_2_count"], 5)

    def test_all_topology_summary_is_not_overstated(self) -> None:
        group = self.group_index["all_rooted_binary_topologies"]
        self.assertEqual(group["topology_count"], 945)
        self.assertEqual(group["regain_required_count"], 270)
        self.assertEqual(group["no_regain_equal_optimum_count"], 675)
        self.assertEqual(group["no_regain_penalty_1_count"], 252)
        self.assertEqual(group["no_regain_penalty_2_count"], 18)

    def test_morph_monophyly_has_directional_consequences(self) -> None:
        bp = self.group_index["bp_monophyletic"]
        white = self.group_index["w_monophyletic"]
        self.assertEqual(bp["topology_count"], 45)
        self.assertEqual(bp["regain_required_count"], 36)
        self.assertEqual(white["topology_count"], 45)
        self.assertEqual(white["regain_required_count"], 0)

    def test_nearest_loss_only_escape_requires_two_split_changes(self) -> None:
        self.assertEqual(self.minimum_distance, 4)
        self.assertEqual(len(self.nearest), 7)
        self.assertTrue(
            all(
                row["rooted_rf_distance_from_published"] == 4
                and row["no_regain_penalty"] == 0
                for row in self.nearest
            )
        )

    def test_summary_preserves_claim_limits(self) -> None:
        self.assertFalse(self.summary["branch_lengths_used"])
        self.assertEqual(self.summary["rooted_binary_topology_count"], 945)
        self.assertEqual(
            self.summary["minimum_rf_distance_to_no_regain_optimum"], 4
        )
        self.assertIn(
            "Introgression",
            self.summary["interpretation"]["claim_limit"],
        )


if __name__ == "__main__":
    unittest.main()
