from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

BUILD_PATH = ANALYSIS / "build_cirsium_flower_colour_atlas_v0_3.py"
BUILD_SPEC = importlib.util.spec_from_file_location("build_colour_atlas_v03_for_rate_gate", BUILD_PATH)
assert BUILD_SPEC and BUILD_SPEC.loader
build = importlib.util.module_from_spec(BUILD_SPEC)
sys.modules[BUILD_SPEC.name] = build
BUILD_SPEC.loader.exec_module(build)

GATE_PATH = ANALYSIS / "validate_flower_colour_rate_fit_preconditions.py"
GATE_SPEC = importlib.util.spec_from_file_location("rate_gate", GATE_PATH)
assert GATE_SPEC and GATE_SPEC.loader
gate = importlib.util.module_from_spec(GATE_SPEC)
sys.modules[GATE_SPEC.name] = gate
GATE_SPEC.loader.exec_module(gate)

BASE = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_2.csv"
EXPANSION = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_3_expansion_evidence.csv"
TREE = ROOT / "data/evidence/flower_colour_rate_tree_contract_v0_1.json"
REFERENCE = ROOT / "data/evidence/comp1061_original_reference_contract_v1.json"


class FlowerColourRateFitPreconditionsTests(unittest.TestCase):
    def current_inputs(self):
        _, _, atlas = build.build(BASE, EXPANSION)
        tree = json.loads(TREE.read_text(encoding="utf-8"))
        return atlas, tree

    def test_frozen_original_reference_contract(self):
        x = json.loads(REFERENCE.read_text(encoding="utf-8"))
        self.assertTrue(x["compatibility_reanalysis_usable"])
        self.assertFalse(x["moreyra_augmented_reference_recovered"])
        self.assertEqual(x["locus_count"], 1061)
        self.assertEqual(x["sequence_record_count"], 2597)
        self.assertEqual(
            x["sha256"],
            "77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c",
        )

    def test_current_project_is_blocked_by_white_tips_and_tree(self):
        atlas, tree = self.current_inputs()
        result = gate.evaluate(atlas, tree)
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["eligible_taxa"], 20)
        self.assertEqual(result["eligible_state_counts"], {"C": 17, "W": 3})
        self.assertEqual(
            result["blockers"],
            ["atlas_minimum_white_tips", "branch_length_tree_unavailable"],
        )
        self.assertTrue(result["comp1061_original_reference_available"])
        self.assertFalse(result["moreyra_augmented_reference_available"])
        self.assertEqual(
            result["target_reference_status"],
            "original_compatible_reference_recovered_augmented_not_recovered",
        )

    def test_white_tips_alone_do_not_unlock_rates(self):
        atlas, tree = self.current_inputs()
        atlas = json.loads(json.dumps(atlas))
        atlas["readiness_conditions"]["minimum_white_tips"] = True
        atlas["transition_rate_fit_ready"] = True
        atlas["rate_fit_eligible_state_counts"] = {"C": 17, "W": 5}
        result = gate.evaluate(atlas, tree)
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["blockers"], ["branch_length_tree_unavailable"])

    def test_tree_alone_does_not_unlock_rates(self):
        atlas, tree = self.current_inputs()
        tree = json.loads(json.dumps(tree))
        tree["empirical_branch_length_tree_ready"] = True
        tree["rate_fit_execution_allowed"] = True
        tree["accepted_tree_route"] = "test_empirical_tree"
        result = gate.evaluate(atlas, tree)
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["blockers"], ["atlas_minimum_white_tips"])

    def test_both_gates_are_required(self):
        atlas, tree = self.current_inputs()
        atlas = json.loads(json.dumps(atlas))
        tree = json.loads(json.dumps(tree))
        atlas["readiness_conditions"]["minimum_white_tips"] = True
        atlas["transition_rate_fit_ready"] = True
        atlas["rate_fit_eligible_state_counts"] = {"C": 17, "W": 5}
        tree["empirical_branch_length_tree_ready"] = True
        tree["rate_fit_execution_allowed"] = True
        tree["accepted_tree_route"] = "test_empirical_tree"
        result = gate.evaluate(atlas, tree)
        self.assertTrue(result["execution_allowed"])
        self.assertEqual(result["blockers"], [])


if __name__ == "__main__":
    unittest.main()
