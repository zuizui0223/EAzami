import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "geo_gate", ROOT / "analysis/audit_japan38_colour_geographic_provenance_v1.py"
)
assert SPEC and SPEC.loader
geo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(geo)


class TestJapan38ColourGeographicProvenance(unittest.TestCase):
    def test_operational_japan_window_examples(self):
        self.assertTrue(geo.operational_japan_window(35.68, 139.76))  # Tokyo
        self.assertTrue(geo.operational_japan_window(43.06, 141.35))  # Hokkaido
        self.assertTrue(geo.operational_japan_window(26.21, 127.68))  # Okinawa
        self.assertFalse(geo.operational_japan_window(37.56, 126.98))  # Seoul
        self.assertFalse(geo.operational_japan_window(43.12, 131.89))  # Vladivostok
        self.assertFalse(geo.operational_japan_window(29.4, 79.7))    # Himalaya

    def test_exact_label_test_enumerates_all_labels(self):
        fixed = np.asarray([1, 2, 3, 4, 5, 6], dtype=float)
        values = [1.0, 2.0, 4.0, 8.0]
        out = geo.exact_label_test(fixed, values)
        self.assertEqual(out["exact_permutations"], math.factorial(4))
        self.assertGreaterEqual(out["negative_tail_p"], 0.0)
        self.assertLessEqual(out["negative_tail_p"], 1.0)
        self.assertGreaterEqual(out["two_sided_abs_p"], 0.0)
        self.assertLessEqual(out["two_sided_abs_p"], 1.0)


if __name__ == "__main__":
    unittest.main()
