#!/usr/bin/env python3
"""Tests for the exact Chang 2026 var. takaoense sample topology screen."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "chang2026_takaoense_sample_colour_history.py"
)
SPEC = importlib.util.spec_from_file_location(
    "chang2026_takaoense_sample_colour_history", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
history = importlib.util.module_from_spec(SPEC)
sys.modules["chang2026_takaoense_sample_colour_history"] = history
SPEC.loader.exec_module(history)


class TakaoenseSampleColourHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = {row["scenario"]: row for row in history.scenario_rows()}

    def test_exact_six_tip_topology_has_white_fitch_root_and_one_change(self) -> None:
        root_states, steps = history.fitch(
            history.TAKAOENSE_SIX,
            {key: {value} for key, value in history.TAKAOENSE_STATES.items()},
        )
        self.assertEqual(root_states, {history.W})
        self.assertEqual(steps, 1)

    def test_six_sample_white_root_requires_one_regain(self) -> None:
        row = self.rows["takaoense_six_samples_root_W"]
        self.assertEqual(row["minimum_changes_fixed_root"], 1)
        self.assertEqual(
            row["optimal_directional_combinations"],
            "losses=0;regains=1",
        )
        self.assertEqual(row["regain_required_at_global_minimum"], "yes")
        self.assertEqual(row["minimum_no_regain_changes"], "impossible")
        self.assertEqual(row["no_regain_change_penalty"], "impossible")

    def test_six_sample_coloured_root_allows_no_regain_at_three_changes(self) -> None:
        row = self.rows["takaoense_six_samples_root_C"]
        self.assertEqual(row["minimum_changes_fixed_root"], 3)
        self.assertEqual(
            set(row["optimal_directional_combinations"].split("|")),
            {"losses=2;regains=1", "losses=3;regains=0"},
        )
        self.assertEqual(row["regain_required_at_global_minimum"], "no")
        self.assertEqual(row["minimum_no_regain_changes"], 3)
        self.assertEqual(row["no_regain_change_penalty"], 0)

    def test_albescens_plus_takaoense_coloured_root_prefers_regain(self) -> None:
        row = self.rows["albescens_plus_takaoense_root_C"]
        self.assertEqual(row["minimum_changes_fixed_root"], 3)
        self.assertEqual(
            row["optimal_directional_combinations"],
            "losses=2;regains=1",
        )
        self.assertEqual(row["regain_required_at_global_minimum"], "yes")
        self.assertEqual(row["minimum_no_regain_changes"], 4)
        self.assertEqual(row["no_regain_change_penalty"], 1)

    def test_sinocirsium_coloured_root_requires_one_loss_and_one_regain(self) -> None:
        row = self.rows["sinocirsium_exact_sample_topology_root_C"]
        self.assertEqual(row["minimum_changes_fixed_root"], 2)
        self.assertEqual(
            row["optimal_directional_combinations"],
            "losses=1;regains=1",
        )
        self.assertEqual(row["regain_required_at_global_minimum"], "yes")
        self.assertEqual(row["minimum_no_regain_changes"], 4)
        self.assertEqual(row["no_regain_change_penalty"], 2)

    def test_full_east_asia_coloured_root_requires_regain_at_minimum(self) -> None:
        row = self.rows["full_east_asia_exact_takaoense_root_C"]
        self.assertEqual(row["minimum_changes_fixed_root"], 4)
        self.assertEqual(
            row["optimal_directional_combinations"],
            "losses=3;regains=1",
        )
        self.assertEqual(row["regain_required_at_global_minimum"], "yes")
        self.assertEqual(row["minimum_no_regain_changes"], 6)
        self.assertEqual(row["no_regain_change_penalty"], 2)

    def test_exact_sample_topology_changes_previous_generic_sensitivity(self) -> None:
        exact = self.rows["full_east_asia_exact_takaoense_root_C"]
        self.assertNotIn(
            "losses=4;regains=0",
            exact["optimal_directional_combinations"],
        )
        self.assertEqual(exact["minimum_fitch_changes_unconstrained_root"], 4)
        self.assertEqual(exact["fitch_root_states"], "C")

    def test_scenario_count_and_names_are_frozen(self) -> None:
        self.assertEqual(
            set(self.rows),
            {
                "takaoense_six_samples_root_W",
                "takaoense_six_samples_root_C",
                "albescens_plus_takaoense_root_C",
                "sinocirsium_exact_sample_topology_root_C",
                "full_east_asia_exact_takaoense_root_C",
            },
        )


if __name__ == "__main__":
    unittest.main()
