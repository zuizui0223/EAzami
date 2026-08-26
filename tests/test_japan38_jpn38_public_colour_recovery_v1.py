import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jpn38_recovery",
    ROOT / "analysis/run_japan38_jpn38_public_colour_recovery_v1.py",
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestJPN38PublicColourRecovery(unittest.TestCase):
    def test_median_abs_deviation(self):
        self.assertEqual(mod.median_abs_deviation([1.0, 2.0, 10.0]), 1.0)
        self.assertIsNone(mod.median_abs_deviation([]))

    def test_truthy(self):
        for value in ["true", "TRUE", "yes", "1", True]:
            self.assertTrue(mod.truthy(value))
        for value in ["false", "0", "", None]:
            self.assertFalse(mod.truthy(value))

    def test_registry_is_utf8_csv(self):
        rows = mod.read_csv(ROOT / "data/evidence/japan38_jpn38_public_colour_recovery_sources_v1.csv")
        self.assertEqual(len(rows), 3)
        self.assertEqual({r["paper_japan_member_id"] for r in rows}, {"JPN_38"})
        self.assertTrue(all(mod.truthy(r["automated_use"]) for r in rows))
        self.assertTrue(all("Japan" in r["location"] for r in rows))
        self.assertEqual(
            {r["rights_status"] for r in rows},
            {"verified_open_license", "verify_in_ci"},
        )
        self.assertTrue(all("commons.wikimedia.org" in r["source_page_url"] for r in rows))


if __name__ == "__main__":
    unittest.main()
