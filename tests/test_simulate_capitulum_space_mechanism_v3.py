from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "simulate_capitulum_space_mechanism_v3.py"
spec = importlib.util.spec_from_file_location("capitulum_v3", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

CONTRACT_PATH = ROOT / "data" / "contracts" / "capitulum_space_mechanism_v3_contract.json"
STRUCTURE_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv"
INCREMENTAL_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv"
HELDOUT_PATH = ROOT / "data" / "evidence" / "macro_interaction_pattern_reduction_result_v2.json"


class CapitulumSpaceMechanismV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.targets = MOD.load_observed(cls.contract, STRUCTURE_PATH, INCREMENTAL_PATH)
        cls.heldout = MOD.load_v2_heldout(HELDOUT_PATH)

    def test_registry_expands_17_units_to_18_endpoints(self):
        units, modules, module_index, endpoint_index = MOD.make_registry(self.contract)
        self.assertEqual(len(units), 17)
        self.assertEqual(len(modules), 5)
        self.assertEqual(len(module_index), 17)
        self.assertEqual(len(endpoint_index[MOD.HUE_UNIT]), 2)
        self.assertEqual(sum(len(v) for v in endpoint_index.values()), 18)

    def test_module_contrast_matches_constructed_matrix(self):
        _units, _modules, module_index, _endpoint_index = MOD.make_registry(self.contract)
        matrix = np.eye(17)
        for i in range(17):
            for j in range(i + 1, 17):
                matrix[i, j] = matrix[j, i] = 0.8 if module_index[i] == module_index[j] else 0.2
        self.assertAlmostEqual(MOD.module_contrast(matrix, module_index), 0.6, places=12)

    def test_partial_r2_is_nested_and_nonnegative(self):
        self.assertAlmostEqual(MOD.partial_r2(0.10, 0.28), 0.20)
        self.assertEqual(MOD.partial_r2(0.20, 0.10), 0.0)

    def test_one_draw_emits_all_seven_estimands(self):
        rng = np.random.default_rng(20260827)
        params = MOD.draw_parameters(
            self.contract, "full_tradeoff_modular_evolvability", rng
        )
        data = MOD.simulate_dataset(
            self.contract, params, n_taxa=20, populations_per_taxon=5,
            rng=np.random.default_rng(20260828),
        )
        summary = MOD.summarize_dataset(self.contract, *data)
        required = {
            "capitulum_within_module_integration_contrast",
            "capitulum_among_module_integration_contrast",
            "capitulum_cross_scale_association_matrix_similarity",
            "within_process_partial_r2",
            "among_process_partial_r2",
            "within_gsp_partial_r2",
            "among_gsp_partial_r2",
        }
        self.assertTrue(required <= set(summary))
        self.assertTrue(all(np.isfinite(summary[key]) for key in required))
        distance, rows = MOD.primary_distance(self.targets, summary)
        self.assertTrue(np.isfinite(distance))
        self.assertEqual(len(rows), 7)

    def test_small_screen_is_deterministic_and_keeps_claim_boundary(self):
        kwargs = dict(
            contract=self.contract,
            targets=self.targets,
            v2_heldout=self.heldout,
            draws_per_seed=2,
            seeds=[20260827],
            accept_fraction=0.05,
            main_taxa=15,
            main_populations=5,
            replication_taxa=16,
            replication_populations=5,
        )
        first = MOD.run_screen(**kwargs)
        second = MOD.run_screen(**kwargs)
        self.assertEqual(first["ranking"], second["ranking"])
        self.assertEqual(
            first["focal_common_vs_modular"], second["focal_common_vs_modular"]
        )
        self.assertEqual(len(first["families"]), 5)
        self.assertEqual(first["draws_per_seed_per_family"], 2)
        self.assertIn("Not a likelihood", first["interpretation_boundary"])
        self.assertIn(first["focal_common_vs_modular"]["registered_decision"], {
            "full_tradeoff_common_lability",
            "full_tradeoff_modular_evolvability",
            "unresolved",
        })


if __name__ == "__main__":
    unittest.main()
