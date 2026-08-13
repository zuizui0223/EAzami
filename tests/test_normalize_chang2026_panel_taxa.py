#!/usr/bin/env python3
"""Tests for the panel-only Chang taxon normalization ledger."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import normalize_chang2026_panel_taxa as mod  # noqa: E402


class ChangPanelTaxonNormalizationTests(unittest.TestCase):
    def test_autonym_is_mapped_but_source_name_is_preserved(self) -> None:
        rows, summary = mod.normalize_rows(
            [
                {
                    "taxon": "C. japonicum var. japonicum",
                    "code": "FKK",
                    "voucher": "ccy4204",
                },
                {
                    "taxon": "C. japonicum var. takaoense",
                    "code": "FC",
                    "voucher": "ccy3559",
                },
            ]
        )
        self.assertEqual(rows[0]["source_taxon"], "C. japonicum var. japonicum")
        self.assertEqual(rows[0]["taxon"], "Cirsium japonicum")
        self.assertEqual(rows[1]["source_taxon"], "C. japonicum var. takaoense")
        self.assertEqual(rows[1]["taxon"], "C. japonicum var. takaoense")
        self.assertEqual(summary["autonym_rows_collapsed_to_species_panel"], 1)

    def test_full_name_autonym_is_also_recognized(self) -> None:
        rows, _ = mod.normalize_rows(
            [
                {
                    "taxon": "Cirsium japonicum var. japonicum",
                    "code": "ASO",
                    "voucher": "ccy4220",
                }
            ]
        )
        self.assertEqual(rows[0]["taxon"], "Cirsium japonicum")

    def test_no_unrelated_variety_is_collapsed(self) -> None:
        rows, summary = mod.normalize_rows(
            [
                {
                    "taxon": "C. japonicum var. albescens",
                    "code": "BT",
                    "voucher": "ccy3173",
                }
            ]
        )
        self.assertEqual(rows[0]["taxon"], "C. japonicum var. albescens")
        self.assertEqual(summary["autonym_rows_collapsed_to_species_panel"], 0)


if __name__ == "__main__":
    unittest.main()
