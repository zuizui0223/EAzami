import importlib.util
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "colour_climate",
    ROOT / "analysis/run_japan38_colour_climate_coupling_v1.py",
)
assert SPEC and SPEC.loader
cc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cc)


class TestJapan38ColourClimateCoupling(unittest.TestCase):
    def test_zscore_columns(self):
        x = np.asarray([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
        z = cc.zscore_columns(x)
        np.testing.assert_allclose(z.mean(axis=0), [0.0, 0.0], atol=1e-12)
        np.testing.assert_allclose(z.std(axis=0, ddof=0), [1.0, 1.0], atol=1e-12)

    def test_pairwise_vectors_have_deterministic_order(self):
        x = np.asarray([1.0, 4.0, 10.0])
        np.testing.assert_allclose(cc.pairwise_absolute(x), [3.0, 9.0, 6.0])
        m = np.asarray([[0.0, 0.0], [3.0, 4.0], [0.0, 4.0]])
        np.testing.assert_allclose(cc.pairwise_euclidean(m), [5.0, 4.0, 3.0])

    def test_exact_permutation_space_is_exhaustive(self):
        fixed = np.asarray([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        lightness = np.asarray([1.0, 2.0, 4.0, 8.0])
        result = cc.exact_distance_test(fixed, lightness)
        self.assertEqual(result["exact_permutations"], math.factorial(4))
        self.assertGreaterEqual(result["positive_tail_p"], 0.0)
        self.assertLessEqual(result["positive_tail_p"], 1.0)
        self.assertGreaterEqual(result["two_sided_abs_p"], 0.0)
        self.assertLessEqual(result["two_sided_abs_p"], 1.0)

    def test_partial_spearman_matches_formula_and_is_finite(self):
        x = np.asarray([1, 2, 3, 4, 5, 6], dtype=float)
        y = np.asarray([2, 1, 4, 3, 6, 5], dtype=float)
        z = np.asarray([6, 5, 3, 4, 2, 1], dtype=float)
        value = cc.partial_spearman(x, y, z)
        self.assertTrue(math.isfinite(value))
        self.assertGreaterEqual(value, -1.0)
        self.assertLessEqual(value, 1.0)

    def test_join_uses_colour_bridge_lightness_not_environment_snapshot_lightness(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            colour = td / "colour.csv"
            env = td / "env.csv"
            colour.write_text(
                "paper_japan_member_id,taxon_name,n_colour_usable_observations,corolla_lab_lightness_species_median\n"
                "JPN_17,Cirsium maritimum,14,68.235294\n",
                encoding="utf-8",
            )
            env.write_text(
                "taxon_name,n_balanced_env_observations,corolla_lab_lightness_median_taxon_median,"
                "env_chelsa_bio01_species_median,env_chelsa_bio04_species_median,"
                "env_chelsa_bio12_species_median,env_chelsa_bio15_species_median\n"
                "Cirsium maritimum,18,1.0,2908.5,6231,2314.5,416.5\n",
                encoding="utf-8",
            )
            joined = cc.join_colour_environment(colour, env)
            self.assertEqual(joined["JPN_17"]["lightness"], 68.235294)
            self.assertNotEqual(joined["JPN_17"]["lightness"], 1.0)

    def test_nonexact_variety_concepts_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            colour = td / "colour.csv"
            env = td / "env.csv"
            colour.write_text(
                "paper_japan_member_id,taxon_name,n_colour_usable_observations,corolla_lab_lightness_species_median\n"
                "JPN_21,Cirsium nipponicum,10,60\n",
                encoding="utf-8",
            )
            env.write_text(
                "taxon_name,n_balanced_env_observations,env_chelsa_bio01_species_median,"
                "env_chelsa_bio04_species_median,env_chelsa_bio12_species_median,"
                "env_chelsa_bio15_species_median\n"
                "Cirsium nipponicum,10,2800,8000,1500,500\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                cc.join_colour_environment(colour, env)


if __name__ == "__main__":
    unittest.main()
