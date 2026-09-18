from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "simulate_scale_specific_covariance_v4_1.py"
spec = importlib.util.spec_from_file_location("scale_cov_v4_1", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

V4_CONTRACT_PATH = ROOT / "data" / "contracts" / "scale_specific_covariance_v4_contract.json"
PRIORS_PATH = ROOT / "data" / "contracts" / "scale_specific_covariance_v4_implementation_priors.json"
V3_CONTRACT_PATH = ROOT / "data" / "contracts" / "capitulum_space_mechanism_v3_contract.json"


class ScaleSpecificCovarianceV41Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v4 = json.loads(V4_CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.priors = json.loads(PRIORS_PATH.read_text(encoding="utf-8"))
        cls.v3 = json.loads(V3_CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_amended_priors_preserve_preoutcome_boundary(self):
        MOD.validate_priors(self.v4, self.priors)
        self.assertEqual(
            self.priors["version"],
            "scale_specific_covariance_v4_1_implementation_priors_2026-08-27",
        )
        self.assertIn("33043095287", self.priors["amendment_note"])
        self.assertIn("No result, log or artifact", self.priors["amendment_note"])

    def test_symmetric_factor_has_zero_mean_and_median_for_even_replication(self):
        taxa = np.repeat(np.arange(5), 6)
        factors = MOD.paired_symmetric_by_taxon(
            taxa, n_columns=5, rng=np.random.default_rng(20260827)
        )
        for taxon in np.unique(taxa):
            values = factors[taxa == taxon]
            self.assertTrue(np.allclose(values.mean(axis=0), 0.0, atol=1e-15))
            self.assertTrue(np.allclose(np.median(values, axis=0), 0.0, atol=1e-15))

    def test_symmetric_factor_has_zero_mean_and_median_for_odd_replication(self):
        taxa = np.repeat(np.arange(5), 5)
        factors = MOD.paired_symmetric_by_taxon(
            taxa, n_columns=5, rng=np.random.default_rng(20260828)
        )
        for taxon in np.unique(taxa):
            values = factors[taxa == taxon]
            self.assertTrue(np.allclose(values.mean(axis=0), 0.0, atol=1e-15))
            self.assertTrue(np.allclose(np.median(values, axis=0), 0.0, atol=1e-15))

    def test_within_only_addition_has_zero_latent_unit_mean_and_median(self):
        unit_ids, _modules, module_index, endpoint_index = MOD.base.module_registry(self.v3)
        taxa = np.repeat(np.arange(4), 5)
        endpoints = np.zeros((len(taxa), 18), dtype=float)
        # A valid hue base representation is needed before the latent angle is shifted.
        hue_sin, hue_cos = endpoint_index[MOD.base.v3.HUE_UNIT]
        endpoints[:, hue_sin] = 0.0
        endpoints[:, hue_cos] = 1.0
        updated, metadata = MOD.add_within_only_factor(
            endpoints,
            taxa,
            unit_ids,
            module_index,
            endpoint_index,
            self.priors,
            np.random.default_rng(20260829),
        )
        self.assertIn("within_only_module_scale", metadata)
        self.assertTrue(np.isfinite(updated).all())
        # Non-hue endpoint additions are directly visible and must have zero taxon median.
        for unit_id in unit_ids:
            if unit_id == MOD.base.v3.HUE_UNIT:
                continue
            endpoint = endpoint_index[unit_id][0]
            for taxon in np.unique(taxa):
                values = updated[taxa == taxon, endpoint]
                self.assertAlmostEqual(float(values.mean()), 0.0, places=14)
                self.assertAlmostEqual(float(np.median(values)), 0.0, places=14)

    def test_v4_1_changes_only_local_factor_hook(self):
        self.assertIsNot(MOD.add_within_only_factor, MOD.base.add_within_only_factor)
        # Shared registered functions remain inherited rather than copied or tuned.
        self.assertTrue(callable(MOD.base.add_among_mosaic))
        self.assertTrue(callable(MOD.base.add_historical_rotation))
        self.assertTrue(callable(MOD.base.run_screen))


if __name__ == "__main__":
    unittest.main()
