#!/usr/bin/env python3
"""Tests for the exhaustive six-tip takaoense topology sensitivity."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
MODULE_PATH = ANALYSIS_DIR / "chang2026_takaoense_topology_uncertainty.py"
SPEC = importlib.util.spec_from_file_location(
    "chang2026_takaoense_topology_uncertainty", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["chang2026_takaoense_topology_uncertainty"] = mod
SPEC.loader.exec_module(mod)


class TakaoenseTopologyUncertaintyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = mod.analyze_topologies()
        cls.summary = mod.build_summary(cls.rows)

    def test_all_rooted_binary_topologies_are_unique(self) -> None:
        trees = mod.all_rooted_binary_trees(mod.TIP_NAMES)
        self.assertEqual(len(trees), 945)
        self.assertEqual(len({mod.tree_key(tree) for tree in trees}), 945)

    def test_exact_displayed_topology_is_recovered_once(self) -> None:
        exact = [
            row for row in self.rows if row["is_exact_displayed_topology"] == "yes"
        ]
        self.assertEqual(len(exact), 1)
        row = exact[0]
        self.assertEqual(row["bp_monophyletic"], "yes")
        self.assertEqual(row["w_monophyletic"], "no")
        self.assertEqual(row["minimum_changes_coloured_sinocirsium_root"], 2)
        self.assertEqual(row["optimal_directional_combinations"], "losses=1;regains=1")
        self.assertEqual(row["regain_required_at_minimum"], "yes")
        self.assertEqual(row["minimum_no_regain_changes"], 4)
        self.assertEqual(row["no_regain_change_penalty"], 2)

    def test_exhaustive_regain_boundary(self) -> None:
        self.assertEqual(self.summary["rooted_binary_topologies_enumerated"], 945)
        self.assertEqual(self.summary["regain_required_topologies"], 270)
        self.assertEqual(
            self.summary["no_regain_allowed_at_minimum_topologies"], 675
        )
        self.assertAlmostEqual(
            self.summary["regain_required_proportion"], 270 / 945
        )
        self.assertAlmostEqual(
            self.summary["no_regain_allowed_at_minimum_proportion"], 675 / 945
        )

    def test_monophyly_counts(self) -> None:
        self.assertEqual(self.summary["bp_monophyletic_topologies"], 45)
        self.assertEqual(self.summary["w_monophyletic_topologies"], 45)
        self.assertEqual(self.summary["both_morphs_monophyletic_topologies"], 9)
        self.assertEqual(
            self.summary["bp_monophyletic_w_nonmonophyletic_topologies"], 36
        )
        self.assertEqual(
            self.summary["bp_monophyletic_w_nonmonophyletic_regain_required"],
            36,
        )

    def test_no_regain_penalty_distribution(self) -> None:
        self.assertEqual(
            self.summary["no_regain_penalty_counts_among_required"],
            {"1": 252, "2": 18},
        )

    def test_aggregate_counts_sum_to_945(self) -> None:
        aggregate = mod.aggregate_rows(self.rows)
        self.assertEqual(sum(int(row["n_topologies"]) for row in aggregate), 945)
        expected = {
            ("no", "no", "no", "0"): 630,
            ("no", "no", "yes", "1"): 234,
            ("no", "yes", "no", "0"): 36,
            ("yes", "no", "yes", "1"): 18,
            ("yes", "no", "yes", "2"): 18,
            ("yes", "yes", "no", "0"): 9,
        }
        observed = {
            (
                row["bp_monophyletic"],
                row["w_monophyletic"],
                row["regain_required_at_minimum"],
                str(row["no_regain_change_penalty"]),
            ): int(row["n_topologies"])
            for row in aggregate
        }
        self.assertEqual(observed, expected)

    def test_uniform_enumeration_is_not_labelled_probability(self) -> None:
        self.assertFalse(self.summary["uniform_topology_enumeration_is_probability"])
        self.assertIn("not a posterior probability", self.summary["interpretation_limit"])


if __name__ == "__main__":
    unittest.main()
