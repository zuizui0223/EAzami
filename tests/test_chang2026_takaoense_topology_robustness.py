#!/usr/bin/env python3
"""Tests for the current Figure 1 takaoense topology-robustness analysis."""
from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import chang2026_takaoense_topology_robustness as mod


class TakaoenseTopologyRobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = mod.analyse_topologies()
        cls.groups = mod.build_group_summaries(cls.rows)
        cls.group_index = {row["group"]: row for row in cls.groups}
        cls.minimum_distance, cls.nearest = mod.nearest_no_regain_rows(cls.rows)
        cls.summary = mod.build_summary(cls.rows, cls.groups, cls.minimum_distance, cls.nearest)

    def test_enumerates_current_945_topologies(self):
        self.assertEqual(len(self.rows), 945)
        self.assertEqual(len({row["sample_topology_newick"] for row in self.rows}), 945)

    def test_published_topology_is_current_figure1_tree(self):
        published = [row for row in self.rows if row["is_published_topology"] == "true"]
        self.assertEqual(len(published), 1)
        row = published[0]
        self.assertEqual(row["topology_id"], "T0297")
        self.assertEqual(
            row["sample_topology_newick"],
            "(((((NH_3835_BP,TJ_3807_BP),FC_3559_BP),LT_3839_W),FB_3629_W),WY_3560_W);",
        )
        self.assertEqual(row["rooted_rf_distance_from_published"], 0)
        self.assertEqual(row["sinocirsium_coloured_root_minimum_changes"], 2)
        self.assertEqual(row["sinocirsium_coloured_root_optimal_histories"], "1L+1R")
        self.assertEqual(row["no_regain_penalty"], 2)

    def test_rooted_rf_distribution_is_cluster_symmetric_difference(self):
        observed = Counter(int(row["rooted_rf_distance_from_published"]) for row in self.rows)
        self.assertEqual(observed, {0: 1, 2: 8, 4: 42, 6: 188, 8: 706})
        self.assertEqual(
            self.summary["rooted_rf_definition"],
            "symmetric difference in nontrivial rooted descendant clusters",
        )

    def test_true_nearest_no_regain_set(self):
        self.assertEqual(self.minimum_distance, 4)
        self.assertEqual(
            [row["topology_id"] for row in self.nearest],
            ["T0403", "T0409", "T0755", "T0846", "T0894", "T0901", "T0944"],
        )
        self.assertTrue(all(row["no_regain_penalty"] == 0 for row in self.nearest))
        self.assertTrue(all(row["rooted_rf_distance_from_published"] == 4 for row in self.nearest))

    def test_local_robustness_is_retained(self):
        group = self.group_index["published_plus_single_split_perturbations"]
        self.assertEqual(group["topology_count"], 9)
        self.assertEqual(group["regain_required_count"], 9)
        self.assertEqual(group["no_regain_penalty_1_count"], 4)
        self.assertEqual(group["no_regain_penalty_2_count"], 5)
        self.assertEqual(group["minimum_change_2_count"], 7)
        self.assertEqual(group["minimum_change_3_count"], 2)

    def test_global_and_monophyly_counts(self):
        all_group = self.group_index["all_rooted_binary_topologies"]
        self.assertEqual(all_group["regain_required_count"], 270)
        self.assertEqual(all_group["no_regain_equal_optimum_count"], 675)
        self.assertEqual(all_group["minimum_change_2_count"], 81)
        self.assertEqual(all_group["minimum_change_3_count"], 486)
        self.assertEqual(all_group["minimum_change_4_count"], 378)
        bp = self.group_index["bp_monophyletic"]
        white = self.group_index["w_monophyletic"]
        self.assertEqual((bp["topology_count"], bp["regain_required_count"]), (45, 36))
        self.assertEqual((white["topology_count"], white["regain_required_count"]), (45, 0))

    def test_nh_tj_group_is_recomputed_from_current_topology(self):
        group = self.group_index["nh_tj_cherry"]
        self.assertEqual(group["topology_count"], 105)
        self.assertEqual(group["regain_required_count"], 66)
        self.assertEqual(group["no_regain_equal_optimum_count"], 39)

    def test_summary_records_stale_set_correction(self):
        self.assertIn("stale", self.summary["audit_note"].lower())
        self.assertEqual(self.summary["nearest_no_regain_topology_count"], 7)
        self.assertEqual(self.summary["single_split_perturbation_regain_required_count"], 9)
        self.assertFalse(self.summary["branch_lengths_used"])


if __name__ == "__main__":
    unittest.main()
