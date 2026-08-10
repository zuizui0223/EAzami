#!/usr/bin/env python3
"""Tests for the source-backed East Asian Cirsium colour-history screen."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "published_east_asia_colour_history.py"
SPEC = importlib.util.spec_from_file_location("published_east_asia_colour_history", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
history = importlib.util.module_from_spec(SPEC)
sys.modules["published_east_asia_colour_history"] = history
SPEC.loader.exec_module(history)


class PublishedColourHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = {row["scenario"]: row for row in history.scenario_rows()}

    def test_nipponocirsium_requires_one_white_loss(self) -> None:
        row = self.rows["chang2025_nipponocirsium_species_level"]
        self.assertEqual(row["minimum_fitch_changes"], 1)
        self.assertEqual(row["fitch_root_states"], "C")
        self.assertEqual(row["root_C_directional_combinations"], "losses=1;regains=0")

    def test_arenicola_sister_context_does_not_require_regain(self) -> None:
        row = self.rows["chang2026_arenicola_plus_taiwan_nipponocirsium"]
        self.assertEqual(row["minimum_fitch_changes"], 2)
        self.assertEqual(row["root_C_directional_combinations"], "losses=2;regains=0")

    def test_population_aware_coding_adds_a_transition(self) -> None:
        taxon = self.rows["chang2026_full_taxon_level_takaoense_ambiguous"]
        population = self.rows["chang2026_full_population_aware_takaoense"]
        self.assertEqual(taxon["minimum_fitch_changes"], 3)
        self.assertEqual(population["minimum_fitch_changes"], 4)

    def test_regain_is_possible_but_not_required(self) -> None:
        row = self.rows["chang2026_full_population_aware_takaoense"]
        combinations = set(row["root_C_directional_combinations"].split("|"))
        self.assertEqual(
            combinations,
            {"losses=4;regains=0", "losses=3;regains=1"},
        )


if __name__ == "__main__":
    unittest.main()
