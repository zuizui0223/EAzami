#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import run_chapter2_eazami_native_continuous_history_diagnostic_v1 as target


class NativeContinuousHistoryDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.design_path = (
            ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_history_design_v1.json"
        )
        cls.result_path = (
            ROOT / "data" / "evidence" / "chapter2_eazami_native_continuous_history_diagnostic_v1.json"
        )
        cls.csv_path = (
            ROOT
            / "data"
            / "evidence"
            / "chapter2_eazami_native_continuous_history_diagnostic_by_topology_v1.csv"
        )
        cls.design = json.loads(cls.design_path.read_text(encoding="utf-8"))
        cls.result = json.loads(cls.result_path.read_text(encoding="utf-8"))

    def test_frozen_design_is_fail_closed(self) -> None:
        self.assertEqual(len(self.design["fixed_taxa"]), 7)
        self.assertEqual(len(self.design["fixed_traits"]), 4)
        self.assertEqual(self.design["null"]["exact_permutations"], 5040)
        self.assertIn("every one of the six topologies", self.design["decision_rule"]["trait_supported"])
        self.assertIn("Do not substitute ranges", self.design["stop_rules"][3])

    def test_frozen_result_does_not_promote_weak_patterns(self) -> None:
        self.assertEqual(self.result["topology_count"], 6)
        self.assertEqual(self.result["supported_traits"], [])
        self.assertEqual(
            self.result["panel_decision"],
            "not_supported_no_topology_robust_retention_detected",
        )
        self.assertEqual(
            {item["decision"] for item in self.result["by_trait"].values()},
            {"not_supported_as_topology_robust_phylogenetic_retention"},
        )
        protrusion = self.result["by_trait"]["phyllary_protrusion_mm"]
        self.assertGreater(protrusion["rho_min"], 0)
        self.assertGreater(protrusion["positive_tail_bh_q_min"], 0.05)
        self.assertEqual(protrusion["lambda_mle_min"], 1.0)

    def test_all_trait_topology_combinations_are_frozen(self) -> None:
        with self.csv_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 24)
        self.assertEqual({int(row["topology"]) for row in rows}, set(range(1, 7)))
        self.assertEqual({row["trait_id"] for row in rows}, set(self.design["fixed_traits"]))
        self.assertTrue(all(int(row["n_taxa"]) == 7 for row in rows))

    def test_bh_and_stable_serialization_helpers(self) -> None:
        self.assertEqual(target.bh([0.01, 0.02, 0.2, 0.5]), [0.04, 0.04, 0.26666666666666666, 0.5])
        self.assertEqual(target.stable_numbers(0.1234567890123456), 0.123456789012)


if __name__ == "__main__":
    unittest.main()
