from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "run_capitulum_space_mechanism_v3_gated.py"
spec = importlib.util.spec_from_file_location("v3_gated", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

CONTRACT_PATH = ROOT / "data" / "contracts" / "capitulum_space_mechanism_v3_contract.json"


class CapitulumSpaceMechanismV31GateTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def base_result(self):
        families = []
        for family, distance, replication, heldout in [
            ("environment_only", 1.4, 0.5, 0.13),
            ("pollinator_only", 1.2, 0.6, 0.32),
            ("antagonist_only", 1.1, 0.7, 0.42),
            ("full_tradeoff_common_lability", 0.80, 0.82, 0.69),
            ("full_tradeoff_modular_evolvability", 0.60, 0.85, 0.71),
        ]:
            families.append({
                "family": family,
                "primary_distance_median": distance,
                "replication_pattern_rate_mean": replication,
                "existing_v2_heldout_rate": heldout,
            })
        return {
            "contract_version": "old",
            "screen_version": "raw",
            "status": "raw",
            "families": families,
            "focal_common_vs_modular": {
                "distance_winner": "full_tradeoff_modular_evolvability",
                "other": "full_tradeoff_common_lability",
                "seedwise_distance_winner_stable": True,
                "replication_not_worse": True,
                "independent_v2_heldout_not_worse": True,
                "registered_decision": "full_tradeoff_modular_evolvability",
            },
        }

    def test_current_contract_has_valid_preoutcome_gates(self):
        thresholds = MOD.validate_v3_1_contract(self.contract)
        self.assertEqual(thresholds["maximum_primary_distance_median"], 1.0)
        self.assertEqual(thresholds["minimum_relative_improvement"], 0.10)
        self.assertEqual(thresholds["minimum_replication_rate"], 0.75)

    def test_all_gates_promote_stable_modular_winner(self):
        result = MOD.apply_v3_1_gate(self.base_result(), self.contract)
        focal = result["focal_common_vs_modular"]
        self.assertEqual(
            focal["registered_decision"],
            "full_tradeoff_modular_evolvability",
        )
        self.assertTrue(focal["absolute_primary_adequacy"])
        self.assertTrue(focal["minimum_relative_distance_improvement_met"])
        self.assertTrue(focal["replication_absolute_adequacy"])

    def test_inadequate_relative_winner_remains_unresolved(self):
        result = self.base_result()
        by = {row["family"]: row for row in result["families"]}
        by["full_tradeoff_modular_evolvability"]["primary_distance_median"] = 1.20
        by["full_tradeoff_common_lability"]["primary_distance_median"] = 1.40
        gated = MOD.apply_v3_1_gate(result, self.contract)
        focal = gated["focal_common_vs_modular"]
        self.assertFalse(focal["absolute_primary_adequacy"])
        self.assertEqual(focal["registered_decision"], "unresolved")

    def test_small_separation_remains_unresolved(self):
        result = self.base_result()
        by = {row["family"]: row for row in result["families"]}
        by["full_tradeoff_modular_evolvability"]["primary_distance_median"] = 0.76
        by["full_tradeoff_common_lability"]["primary_distance_median"] = 0.80
        gated = MOD.apply_v3_1_gate(result, self.contract)
        focal = gated["focal_common_vs_modular"]
        self.assertFalse(focal["minimum_relative_distance_improvement_met"])
        self.assertEqual(focal["registered_decision"], "unresolved")

    def test_low_replication_remains_unresolved(self):
        result = self.base_result()
        by = {row["family"]: row for row in result["families"]}
        by["full_tradeoff_modular_evolvability"]["replication_pattern_rate_mean"] = 0.70
        gated = MOD.apply_v3_1_gate(result, self.contract)
        focal = gated["focal_common_vs_modular"]
        self.assertFalse(focal["replication_absolute_adequacy"])
        self.assertEqual(focal["registered_decision"], "unresolved")

    def test_invalid_adequacy_threshold_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["family_comparison"][
            "maximum_accepted_primary_distance_median_for_adequacy"
        ] = 0
        with self.assertRaisesRegex(ValueError, "Absolute distance"):
            MOD.validate_v3_1_contract(contract)

    def test_old_contract_version_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["contract_version"] = "capitulum_space_mechanism_v3_2026-08-27"
        with self.assertRaisesRegex(ValueError, "Only capitulum_space_mechanism_v3_1"):
            MOD.validate_v3_1_contract(contract)


if __name__ == "__main__":
    unittest.main()
