import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class WorldClimMechanismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sampler = load("wc_sampler", "analysis/sample_worldclim_public_exposure_v1.py")
        cls.gate = load("wc_gate", "analysis/run_japan38_global_lightness_worldclim_mechanism_gate_v1.py")

    def test_vpd_proxy_formula(self):
        es20 = float(self.sampler.saturation_vapor_pressure_kpa([20.0])[0])
        self.assertAlmostEqual(es20, 2.338, places=3)
        self.assertGreater(es20 - 1.0, 0)

    def test_exact_gate_detects_constructed_positive_alignment(self):
        ids = ["JPN_17", "JPN_23", "JPN_29", "JPN_36", "JPN_37", "JPN_38"]
        counts = [14, 20, 9, 10, 92, 42]
        x = np.arange(1, 7, dtype=float)
        df = pd.DataFrame({
            "paper_japan_member_id": ids,
            "taxon_name": [f"Taxon {i}" for i in ids],
            "n_colour_observations": counts,
            self.gate.LIGHTNESS: x,
            self.gate.AXES["solar_radiation"]: x * 100,
            self.gate.AXES["wind_speed"]: x * 0.2,
            self.gate.AXES["vpd_tavg_proxy"]: x * 0.1,
        })
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "summary.csv"
            df.to_csv(p, index=False)
            result = self.gate.run(p)
        self.assertTrue(result["primary_gate_pass"])
        self.assertEqual(result["subsets"]["n_ge_5"]["results"]["exposure_3d"]["n_permutations"], 720)
        self.assertEqual(result["subsets"]["n_ge_10"]["results"]["exposure_3d"]["n_permutations"], 120)
        self.assertTrue(all(result["secondary_axis_robust_leads"].values()))


if __name__ == "__main__":
    unittest.main()
