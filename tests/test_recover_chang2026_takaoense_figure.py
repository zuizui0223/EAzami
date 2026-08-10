#!/usr/bin/env python3
"""Offline tests for Chang 2026 var. takaoense Figure 1 recovery."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "recover_chang2026_takaoense_figure.py"
)
SPEC = importlib.util.spec_from_file_location(
    "recover_chang2026_takaoense_figure", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["recover_chang2026_takaoense_figure"] = mod
SPEC.loader.exec_module(mod)


class ChangFigureRecoveryTests(unittest.TestCase):
    def test_parse_code_followed_by_state(self) -> None:
        text = (
            "Cirsium japonicum var. takaoense FC (W)\n"
            "Cirsium japonicum var. takaoense TJ (BP)\n"
        )
        self.assertEqual(
            mod.parse_direct_tip_labels(text),
            {"ccy3559": "W", "ccy3807": "BP"},
        )

    def test_parse_voucher_and_state_in_reverse_order(self) -> None:
        text = "(BP) Cirsium japonicum var. takaoense ccy3835"
        self.assertEqual(mod.parse_direct_tip_labels(text), {"ccy3835": "BP"})

    def test_no_locality_only_inference(self) -> None:
        text = (
            "Fenchihu is a mountain locality with white and bluish-purple flowers. "
            "The supplement lists ccy3559 but no sample-level morph state."
        )
        self.assertEqual(mod.parse_direct_tip_labels(text), {})

    def test_conflicting_explicit_labels_are_not_silently_resolved(self) -> None:
        text = "FC (W) elsewhere FC (BP)"
        self.assertEqual(mod.parse_direct_tip_labels(text), {"ccy3559": "CONFLICT"})

    def test_build_rows_preserves_unresolved_samples(self) -> None:
        rows = mod.build_tip_rows({"ccy3559": "W", "ccy3807": "BP"})
        by_voucher = {row["voucher"]: row for row in rows}
        self.assertEqual(len(rows), 6)
        self.assertEqual(by_voucher["ccy3559"]["flower_colour_state"], "white")
        self.assertEqual(by_voucher["ccy3559"]["binary_colour_code"], "W")
        self.assertEqual(
            by_voucher["ccy3807"]["flower_colour_state"], "bluish-purple"
        )
        self.assertEqual(by_voucher["ccy3807"]["binary_colour_code"], "C")
        self.assertEqual(
            by_voucher["ccy3835"]["review_status"],
            "unresolved_pending_figure_review",
        )
        self.assertIn("No assignment from geography", by_voucher["ccy3835"]["notes"])

    def test_normalize_label_text(self) -> None:
        self.assertEqual(
            mod.normalize_label_text("  FC\n  (W) — sample  "),
            "FC (W) - sample",
        )


if __name__ == "__main__":
    unittest.main()
