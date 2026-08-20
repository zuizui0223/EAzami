import csv
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import simulate_orientation_mechanism_reduction as sim


class OrientationReductionTest(unittest.TestCase):
    def test_targets(self):
        path = ROOT / "data/evidence/orientation_mechanism_reduction_targets_v1.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(r["role"] == "core" for r in rows), 5)
        self.assertEqual(sum(r["role"] == "heldout" for r in rows), 2)

    def test_deterministic_small_run(self):
        path = ROOT / "data/evidence/orientation_mechanism_reduction_targets_v1.csv"
        a = sim.run(path, draws=20, seed=1234)
        b = sim.run(path, draws=20, seed=1234)
        self.assertEqual(a, b)
        self.assertEqual(len(a["families"]), 5)
        self.assertEqual(set(a["ranking"]), set(sim.FAMILIES))


if __name__ == "__main__":
    unittest.main()
