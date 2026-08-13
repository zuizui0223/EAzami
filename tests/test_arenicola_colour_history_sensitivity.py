from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "analysis" / "arenicola_colour_history_sensitivity.py"
SPEC = importlib.util.spec_from_file_location("arenicola_colour_history_sensitivity", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class ArenicolaColourHistorySensitivityTests(unittest.TestCase):
    def test_source_backed_tip_states_are_frozen(self):
        states = mod.load_tip_states(ROOT / "data/evidence/arenicola_flower_colour_history_evidence_v1.csv")
        self.assertEqual(states, mod.EXPECTED_TIP_STATES)

    def test_pair_alone_is_exactly_unpolarized(self):
        children, root, tips = mod.pair_tree()
        free = mod.enumerate_optima(children, tips, root=root)
        coloured = mod.enumerate_optima(children, tips, root=root, constraints={"AREN_MRCA": "C"})
        white = mod.enumerate_optima(children, tips, root=root, constraints={"AREN_MRCA": "W"})
        self.assertEqual(free["minimum_changes"], 1)
        self.assertEqual(free["optimal_arenicola_mrca_states"], "C|W")
        self.assertEqual(coloured["minimum_changes"], 1)
        self.assertEqual(white["minimum_changes"], 1)

    def test_published_sister_context_prefers_coloured_arenicola_mrca(self):
        children, root = mod.full_tree("published_pengii_basal")
        tips = mod.EXPECTED_TIP_STATES
        free = mod.enumerate_optima(children, tips, root=root)
        coloured = mod.enumerate_optima(children, tips, root=root, constraints={"AREN_MRCA": "C"})
        white = mod.enumerate_optima(children, tips, root=root, constraints={"AREN_MRCA": "W"})
        self.assertEqual(free["minimum_changes"], 2)
        self.assertEqual(free["optimal_root_states"], "C")
        self.assertEqual(free["optimal_arenicola_mrca_states"], "C")
        self.assertEqual(coloured["minimum_changes"], 2)
        self.assertEqual(white["minimum_changes"], 3)

    def test_white_deep_root_flips_preferred_arenicola_state(self):
        children, root = mod.full_tree("published_pengii_basal")
        forced = mod.enumerate_optima(children, mod.EXPECTED_TIP_STATES, root=root, constraints={"ROOT": "W"})
        self.assertEqual(forced["minimum_changes"], 3)
        self.assertEqual(forced["optimal_arenicola_mrca_states"], "W")

    def test_nipponocirsium_core_resolution_does_not_change_free_result(self):
        for variant in (
            "published_pengii_basal",
            "alternative_kawakamii_basal",
            "alternative_tatakaense_basal",
        ):
            children, root = mod.full_tree(variant)
            free = mod.enumerate_optima(children, mod.EXPECTED_TIP_STATES, root=root)
            self.assertEqual(free["minimum_changes"], 2)
            self.assertEqual(free["optimal_arenicola_mrca_states"], "C")

    def test_summary_keeps_regain_as_competing_hypothesis(self):
        rows = mod.scenario_rows(mod.EXPECTED_TIP_STATES)
        summary = mod.build_summary(rows, mod.DEFAULT_EVIDENCE)
        self.assertEqual(summary["pair_only"]["optimal_arenicola_mrca_states"], "C|W")
        self.assertEqual(summary["published_sister_context"]["white_ancestor_penalty_changes"], 1)
        self.assertIn("remains an explicit competing hypothesis", summary["working_inference"])


if __name__ == "__main__":
    unittest.main()
