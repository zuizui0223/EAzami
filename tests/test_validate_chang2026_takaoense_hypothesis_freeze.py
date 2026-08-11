import csv
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = REPO_ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import validate_chang2026_takaoense_hypothesis_freeze as mod


class HypothesisFreezeTests(unittest.TestCase):
    def test_current_frozen_set_matches_current_sources(self):
        rows = mod.validate(mod.DEFAULT_NEAREST, mod.DEFAULT_ROBUSTNESS, mod.DEFAULT_FROZEN)
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["hypothesis_id"], "H_REG_PUBLISHED")
        self.assertEqual(
            [row["hypothesis_id"] for row in rows[1:]],
            [f"H_LOSS_ONLY_RF4_{index:02d}" for index in range(1, 8)],
        )

    def test_stale_topology_is_rejected(self):
        rows = mod.read_csv(mod.DEFAULT_FROZEN)
        rows[1]["topology_newick"] = "(stale,topology);"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stale.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "differs from current sources"):
                mod.validate(mod.DEFAULT_NEAREST, mod.DEFAULT_ROBUSTNESS, path)


if __name__ == "__main__":
    unittest.main()
