from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "simulate_scale_specific_covariance_v4.py"
spec = importlib.util.spec_from_file_location("scale_cov_v4_screen", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

V4_CONTRACT_PATH = ROOT / "data" / "contracts" / "scale_specific_covariance_v4_contract.json"
PRIORS_PATH = ROOT / "data" / "contracts" / "scale_specific_covariance_v4_implementation_priors.json"
V3_CONTRACT_PATH = ROOT / "data" / "contracts" / "capitulum_space_mechanism_v3_contract.json"
STRUCTURE_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv"
ENVIRONMENT_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_eazami_targets_run33035785120.csv"
INCREMENTAL_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv"
HELDOUT_PATH = ROOT / "data" / "evidence" / "macro_interaction_pattern_reduction_result_v2.json"


class ScaleSpecificCovarianceV4ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v4 = json.loads(V4_CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.priors = json.loads(PRIORS_PATH.read_text(encoding="utf-8"))
        cls.v3 = json.loads(V3_CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.targets = MOD.v3.load_observed(cls.v3, STRUCTURE_PATH, INCREMENTAL_PATH)
        cls.context = MOD.load_context_targets(ENVIRONMENT_PATH)
        cls.heldout = MOD.v3.load_v2_heldout(HELDOUT_PATH)["full_tradeoff_common_lability"]

    def test_registered_priors_validate(self):
        MOD.validate_priors(self.v4, self.priors)

    def test_taxon_centring_is_exact_to_machine_precision(self):
        taxa = np.repeat(np.arange(4), 5)
        raw = np.random.default_rng(1).normal(size=(20, 3))
        centred = MOD.centre_by_taxon(raw, taxa)
        for taxon in np.unique(taxa):
            self.assertTrue(np.allclose(centred[taxa == taxon].mean(axis=0), 0.0, atol=1e-15))

    def test_mosaic_loadings_have_zero_module_means(self):
        _units, _modules, module_index, _endpoint_index = MOD.module_registry(self.v3)
        loadings = MOD.centred_mosaic_loadings(
            np.random.default_rng(2), len(module_index), 5, module_index
        )
        for module in np.unique(module_index):
            self.assertTrue(
                np.allclose(loadings[module_index == module].mean(axis=0), 0.0, atol=1e-14)
            )

    def test_all_families_emit_seven_primary_and_twelve_context_estimands(self):
        for family in self.v4["model_families"]:
            data = MOD.simulate_family_dataset(
                self.v4,
                self.priors,
                self.v3,
                family["family_id"],
                shared_params_seed=11,
                shared_data_seed=12,
                addition_seed=13,
                n_taxa=15,
                populations_per_taxon=5,
            )
            summary = MOD.summarize(self.v3, data[0], data[1], data[2])
            distance, rows = MOD.v3.primary_distance(self.targets, summary)
            self.assertTrue(np.isfinite(distance))
            self.assertEqual(len(rows), 7)
            context_keys = [key for key in summary if key.startswith("context_r2:")]
            self.assertEqual(len(context_keys), 12)
            self.assertTrue(np.isfinite(MOD.context_rmse(summary, self.context)))

    def test_feature_sets_are_nested_as_declared(self):
        by = {row["family_id"]: row for row in self.v4["model_families"]}
        self.assertTrue(MOD.nested(by["shared_scale_baseline"], by["within_only_module_factor"]))
        self.assertTrue(MOD.nested(by["within_only_module_factor"], by["combined_scale_decoupling"]))
        self.assertTrue(MOD.nested(by["combined_scale_decoupling"], by["combined_scale_decoupling_with_rotation"]))
        self.assertFalse(MOD.nested(by["within_only_module_factor"], by["among_unit_mosaic_loadings"]))

    def test_small_screen_is_deterministic_and_preserves_boundary(self):
        kwargs = dict(
            v4_contract=self.v4,
            priors=self.priors,
            v3_contract=self.v3,
            targets=self.targets,
            context_targets=self.context,
            inherited_heldout=self.heldout,
            draws_per_seed=2,
            seeds=[20260827],
        )
        first = MOD.run_screen(**kwargs)
        second = MOD.run_screen(**kwargs)
        self.assertEqual(first["ranking"], second["ranking"])
        self.assertEqual(first["eligible_families"], second["eligible_families"])
        self.assertEqual(first["registered_decision"], second["registered_decision"])
        self.assertEqual(len(first["families"]), 5)
        self.assertIn(first["registered_decision"], {
            "no_adequate_family",
            "structural_nonidentifiability",
            "shared_scale_baseline",
            "within_only_module_factor",
            "among_unit_mosaic_loadings",
            "combined_scale_decoupling",
            "combined_scale_decoupling_with_rotation",
        })
        self.assertIn("Not a likelihood", first["interpretation_boundary"])
        for row in first["families"]:
            self.assertIn("eligibility_gates", row)
            self.assertIn("eligible", row)


if __name__ == "__main__":
    unittest.main()
