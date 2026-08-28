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

    def test_current_native_continuous_gate_is_fail_closed(self) -> None:
        contract = json.loads(target.CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(target.validate_native_input(contract), "ADMITTED_coverage_insufficient")
        target.validate_independence_boundary(contract)

    def test_frozen_negative_results_are_not_promoted(self) -> None:
        target.validate_frozen_results()
        target.validate_native_history_diagnostic()


if __name__ == "__main__":
    unittest.main()
