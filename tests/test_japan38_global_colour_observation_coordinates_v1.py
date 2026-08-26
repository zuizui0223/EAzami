import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "validate_japan38_global_colour_observation_coordinates_v1.py"
spec = importlib.util.spec_from_file_location("coord_gate", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "evidence" / "japan38_global_colour_observation_coordinates_v1.csv"
PROV_PATH = ROOT / "data" / "evidence" / "japan38_global_colour_observation_coordinates_provenance_v1.json"


class CoordinateIntegrityTests(unittest.TestCase):
    def test_frozen_table_validates(self):
        result = mod.validate(CSV_PATH, PROV_PATH)
        self.assertEqual(result["row_count"], 187)
        self.assertEqual(result["unique_obs_ids"], 187)
        self.assertEqual(result["sha256"], mod.EXPECTED_SHA256)
        self.assertEqual(result["taxon_counts"], mod.EXPECTED_COUNTS)

    def test_any_byte_drift_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "mutated.csv"
            text = CSV_PATH.read_text(encoding="utf-8")
            p.write_text(text.replace("1459279", "1459278", 1), encoding="utf-8")
            with self.assertRaises(AssertionError):
                mod.validate(p)


if __name__ == "__main__":
    unittest.main()
