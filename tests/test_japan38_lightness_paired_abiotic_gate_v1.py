import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "paired_abiotic",
    ROOT / "analysis/run_japan38_lightness_paired_abiotic_gate_v1.py",
)
assert SPEC and SPEC.loader
pa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pa)


class TestPairedAbioticGate(unittest.TestCase):
    def test_pairwise_helpers(self):
        np.testing.assert_allclose(pa.pairwise_abs([1, 4, 10]), [3, 9, 6])
        z = pa.zscore_columns(np.asarray([[1., 10.], [2., 20.], [3., 30.]]))
        np.testing.assert_allclose(z.mean(axis=0), [0, 0], atol=1e-12)
        np.testing.assert_allclose(z.std(axis=0), [1, 1], atol=1e-12)

    def test_exact_permutation_is_exhaustive(self):
        distance = np.asarray([1, 2, 3, 4, 5, 6], dtype=float)
        result = pa.exact_test(distance, [1, 2, 4, 8])
        self.assertEqual(result["exact_permutations"], math.factorial(4))
        self.assertTrue(0 <= result["positive_tail_p"] <= 1)
        self.assertTrue(0 <= result["two_sided_abs_p"] <= 1)

    def test_frozen_paired_summary_contract(self):
        rows = pa.read_summary(
            ROOT / "data/evidence/japan38_lightness_paired_environment_summary_v1.csv"
        )
        self.assertEqual(set(rows), {"JPN_17", "JPN_23", "JPN_29", "JPN_36", "JPN_37", "JPN_38"})
        self.assertEqual(rows["JPN_37"]["n_colour"], 92)
        self.assertAlmostEqual(rows["JPN_17"]["lightness"], 68.23529434)
        self.assertEqual(rows["JPN_17"]["n_soil_bdod_0_30cm"], 4)
        self.assertEqual(rows["JPN_23"]["n_soil_bdod_0_30cm"], 17)

    def test_primary_modules_are_frozen(self):
        self.assertEqual(pa.PRIMARY_MODULES["paired_climate"], pa.CLIMATE)
        self.assertEqual(pa.PRIMARY_MODULES["paired_topography"], pa.TOPOGRAPHY)
        self.assertEqual(pa.PRIMARY_MODULES["paired_climate_plus_topography"], pa.CLIMATE + pa.TOPOGRAPHY)
        self.assertEqual(pa.COLOUR_THRESHOLDS, (5, 10))


if __name__ == "__main__":
    unittest.main()
