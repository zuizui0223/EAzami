#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import validate_chapter2_diversity_depth_v1 as target


class DiversityDepthContractTests(unittest.TestCase):
    def test_inventory_is_complete_and_classified(self) -> None:
        rows = target.validate_inventory()
        self.assertEqual(len(rows), 17)
        self.assertEqual(rows[0]["asset"], "Japan38 / Comp1061 nuclear scaffold")
        self.assertEqual(rows[-1]["classification"], "design_only")

    def test_current_native_continuous_layer_is_bounded_not_a_completion_gate(self) -> None:
        contract = json.loads(target.CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            target.validate_native_input(contract), "ADMITTED_bounded_not_completion_gate"
        )
        target.validate_independence_boundary(contract)

    def test_chapter3_radseq_is_a_falsification_bridge_not_dependency(self) -> None:
        contract = json.loads(target.CONTRACT_PATH.read_text(encoding="utf-8"))
        rows = target.validate_chapter2_to_chapter3_bridge(contract)
        self.assertEqual(len(rows), 5)
        self.assertIn("JPN_06", rows[0]["focal_concepts"])
        self.assertIn("JPN_15", rows[0]["focal_concepts"])
        self.assertIn("JPN_36", rows[1]["focal_concepts"])
        self.assertFalse(
            contract["chapter2_to_chapter3_bridge"]["own_radseq_required_for_chapter2"]
        )

    def test_frozen_negative_results_are_not_promoted(self) -> None:
        target.validate_frozen_results()
        target.validate_native_history_diagnostic()

    def test_repo_wide_recovery_has_five_main_result_groups(self) -> None:
        rows = target.validate_core_result_recovery()
        main = [row for row in rows if row["result_id"].startswith("M")]
        self.assertEqual([row["result_id"] for row in main], ["M01", "M02", "M03", "M04", "M05"])
        self.assertEqual(main[1]["paper_role"], "MAIN_BIOLOGICAL_RESULT")
        self.assertIn("at least three harmonized", main[1]["headline_result"])

    def test_active_jeb_v4_is_minimum_change_framed_and_bounded(self) -> None:
        target.validate_active_manuscript()

    def test_all_analyses_have_resolution_and_meta_simulation_dispositions(self) -> None:
        resolution, meta_sim = target.validate_resolution_and_meta_sim_audit()
        self.assertEqual(len(resolution), 34)
        self.assertEqual(len(meta_sim), 22)
        lookup = {row["analysis_id"]: row for row in resolution}
        self.assertEqual(
            lookup["D04"]["epistemic_class"],
            "CERTAIN_TOPOLOGY_CONDITIONAL_MINIMUM",
        )
        self.assertEqual(
            lookup["D31"]["negative_status"],
            "NOT_A_BIOLOGICAL_NEGATIVE",
        )
        self.assertEqual(
            lookup["D34"]["epistemic_class"],
            "CERTAIN_TOPOLOGY_CONDITIONAL_DEPTH_ENVELOPE",
        )


if __name__ == "__main__":
    unittest.main()
