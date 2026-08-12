from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis/validate_fixed_white_target_capture_panel.py"
SPEC = importlib.util.spec_from_file_location("white_panel_validator", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
PANEL = ROOT / "sampling/FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv"


class FixedWhiteTargetCapturePanelTests(unittest.TestCase):
    def test_frozen_panel(self):
        summary = module.validate(PANEL)
        self.assertEqual(summary["candidate_count"], 5)
        self.assertEqual(summary["a1_fixed_white_tip_gain_if_both_resolved"], 2)
        self.assertEqual(summary["projected_fixed_white_gate_if_a1_both_resolved"], 5)
        self.assertEqual(summary["a1_taxa"], ["Cirsium boninense", "Cirsium wulongense"])

    def test_henryi_guard_cannot_be_removed(self):
        with PANEL.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
            fields = list(rows[0])
        target = next(row for row in rows if row["taxon"] == "Cirsium henryi")
        target["identity_guard"] = "use Cirsium henryi"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "panel.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "identity guard"):
                module.validate(path)

    def test_single_individual_design_is_rejected(self):
        with PANEL.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
            fields = list(rows[0])
        rows[0]["minimum_individuals"] = "1"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "panel.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, ">=2 individuals"):
                module.validate(path)


if __name__ == "__main__":
    unittest.main()
