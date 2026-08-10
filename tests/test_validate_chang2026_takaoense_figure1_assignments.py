#!/usr/bin/env python3
"""Tests for direct Figure 1 var. takaoense morph assignments."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from copy import deepcopy
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "validate_chang2026_takaoense_figure1_assignments.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validate_chang2026_takaoense_figure1_assignments", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["validate_chang2026_takaoense_figure1_assignments"] = mod
SPEC.loader.exec_module(mod)


class Figure1AssignmentTests(unittest.TestCase):
    def valid_rows(self) -> list[dict[str, str]]:
        rows = []
        for voucher, expected in mod.EXPECTED.items():
            row = {
                "accepted_taxon": "Cirsium japonicum var. takaoense",
                "code": expected["code"],
                "location": "Taiwan",
                "voucher": voucher,
                "run": expected["run"],
                "biosample": expected["biosample"],
                "direct_figure_label": expected["label"],
                "flower_colour_state": expected["state"],
                "binary_colour_code": expected["binary"],
                "source_figure": "Chang et al. 2026 Figure 1 panels B and C",
                "source_image_sha256": mod.IMAGE_SHA256,
                "source_image_width_px": mod.WIDTH,
                "source_image_height_px": mod.HEIGHT,
                "source_workflow_run": mod.WORKFLOW_RUN,
                "source_artifact_id": mod.ARTIFACT_ID,
                "source_artifact_sha256": mod.ARTIFACT_SHA256,
                "review_method": mod.REVIEW_METHOD,
                "assignment_confidence": "high",
                "review_status": mod.REVIEW_STATUS,
                "notes": "No inference from locality or topology",
            }
            row["figure1_panel_b_label"] = mod.expected_printed_label(row, "B")
            row["figure1_panel_c_label"] = mod.expected_printed_label(row, "C")
            rows.append(row)
        return rows

    def test_valid_assignments(self) -> None:
        summary = mod.validate(self.valid_rows())
        self.assertEqual(summary["assignment_rows"], 6)
        self.assertEqual(summary["panel_b_direct_labels"], 6)
        self.assertEqual(summary["panel_c_direct_labels"], 6)
        self.assertEqual(summary["morph_counts"], {"W": 3, "BP": 3})
        self.assertEqual(
            summary["white_vouchers"], ["ccy3560", "ccy3629", "ccy3839"]
        )
        self.assertEqual(
            summary["bluish_purple_vouchers"],
            ["ccy3559", "ccy3807", "ccy3835"],
        )
        self.assertTrue(summary["direct_morph_assignment_complete"])

    def test_wrong_morph_fails(self) -> None:
        rows = self.valid_rows()
        row = next(item for item in rows if item["voucher"] == "ccy3559")
        row["direct_figure_label"] = "W"
        row["flower_colour_state"] = "white"
        row["binary_colour_code"] = "W"
        row["figure1_panel_b_label"] = mod.expected_printed_label(row, "B")
        row["figure1_panel_c_label"] = mod.expected_printed_label(row, "C")
        with self.assertRaisesRegex(ValueError, "morph expected"):
            mod.validate(rows)

    def test_panel_b_label_mismatch_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["figure1_panel_b_label"] = "wrong"
        with self.assertRaisesRegex(ValueError, "Panel B label mismatch"):
            mod.validate(rows)

    def test_panel_c_label_mismatch_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["figure1_panel_c_label"] = "wrong"
        with self.assertRaisesRegex(ValueError, "Panel C label mismatch"):
            mod.validate(rows)

    def test_wrong_accession_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["biosample"] = "SAMNwrong"
        with self.assertRaisesRegex(ValueError, "biosample"):
            mod.validate(rows)

    def test_wrong_image_hash_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["source_image_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "image hash"):
            mod.validate(rows)

    def test_missing_no_inference_guard_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["notes"] = "assigned from figure"
        with self.assertRaisesRegex(ValueError, "no-inference guard"):
            mod.validate(rows)

    def test_missing_voucher_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "six Figure 1 assignment rows"):
            mod.validate(self.valid_rows()[:-1])

    def test_duplicate_voucher_fails(self) -> None:
        rows = self.valid_rows()
        rows[-1] = deepcopy(rows[0])
        with self.assertRaisesRegex(ValueError, "Voucher membership changed"):
            mod.validate(rows)


if __name__ == "__main__":
    unittest.main()
