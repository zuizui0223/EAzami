#!/usr/bin/env python3
"""Tests for the frozen Chang var. takaoense voucher evidence ledger."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from copy import deepcopy
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "validate_chang2026_takaoense_voucher_evidence.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validate_chang2026_takaoense_voucher_evidence", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["validate_chang2026_takaoense_voucher_evidence"] = mod
SPEC.loader.exec_module(mod)


class ChangVoucherEvidenceTests(unittest.TestCase):
    def row(
        self,
        voucher: str,
        code: str,
        s1: str,
        s6_status: str,
        label: str,
        state: str,
        binary: str,
        s6_herbarium: str = "",
        s6_text: str = "",
        main_text: str = "",
        notes_extra: str = "",
    ) -> dict[str, str]:
        notes = (
            f"Panels B and C both print {code}-{voucher.removeprefix('ccy')}({label}); "
            f"official Figure 1 image SHA256 {mod.EXPECTED_FIGURE_IMAGE_HASH}; "
            "no colour inferred from locality"
        )
        if notes_extra:
            notes += "; " + notes_extra
        return {
            "accepted_taxon": "Cirsium japonicum var. takaoense",
            "location": "Taiwan",
            "code": code,
            "voucher": voucher,
            "herbarium_supplement_s1": s1,
            "supplement_s6_status": s6_status,
            "supplement_s6_transcription": s6_text,
            "supplement_s6_herbarium": s6_herbarium,
            "main_text_voucher_evidence": main_text,
            "figure1_state_definition": mod.EXPECTED_FIGURE_DEFINITION,
            "direct_sample_morph_label": label,
            "flower_colour_state": state,
            "binary_colour_code": binary,
            "review_status": mod.EXPECTED_REVIEW_STATUS,
            "next_action": "reuse labelled transcriptome",
            "source_artifact_sha256": mod.EXPECTED_SUPPLEMENT_HASH,
            "notes": notes,
        }

    def valid_rows(self) -> list[dict[str, str]]:
        return [
            self.row(
                "ccy3559", "FC", "TNM", "exact_collector_number_found",
                "BP", "bluish-purple", "C",
                "TNM", "C.Y.Chang 3559 (TNM)"
            ),
            self.row(
                "ccy3807", "TJ", "TCF", "collector_number_not_found_in_s6",
                "BP", "bluish-purple", "C",
                notes_extra="S6 non-recovery retained"
            ),
            self.row(
                "ccy3835", "NH", "TCF", "collector_number_not_found_in_s6",
                "BP", "bluish-purple", "C",
                main_text="Specimen 3835 is mentioned in the taxonomic treatment",
                notes_extra="main text contains no independent colour statement"
            ),
            self.row(
                "ccy3560", "WY", "TNM", "exact_collector_number_found",
                "W", "white", "W",
                "TNM", "C.Y.Chang 3560 (TNM)"
            ),
            self.row(
                "ccy3629", "FB", "TNM", "exact_collector_number_found",
                "W", "white", "W",
                "TNM", "C.Y.Chang 3629 (TNM)"
            ),
            self.row(
                "ccy3839", "LT", "TCF", "exact_collector_number_found",
                "W", "white", "W",
                "TNM", "C.Y.Chang 3839 (TNM)",
                notes_extra="direct S1/S6 herbarium conflict remains TCF versus TNM"
            ),
        ]

    def test_valid_ledger(self) -> None:
        summary = mod.validate(self.valid_rows())
        self.assertEqual(summary["voucher_rows"], 6)
        self.assertEqual(summary["supplement_s6_exact_records"], 4)
        self.assertEqual(summary["supplement_s6_not_recovered"], 2)
        self.assertEqual(summary["s1_s6_herbarium_conflicts"], ["ccy3839"])
        self.assertEqual(summary["direct_sample_morph_assignments"], 6)
        self.assertEqual(summary["morph_counts"], {"W": 3, "BP": 3})
        self.assertEqual(
            summary["white_vouchers"], ["ccy3560", "ccy3629", "ccy3839"]
        )
        self.assertEqual(
            summary["bluish_purple_vouchers"],
            ["ccy3559", "ccy3807", "ccy3835"],
        )
        self.assertEqual(summary["unresolved_vouchers"], [])

    def test_wrong_morph_assignment_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["direct_sample_morph_label"] = "W"
        rows[0]["flower_colour_state"] = "white"
        rows[0]["binary_colour_code"] = "W"
        with self.assertRaisesRegex(ValueError, "Figure 1 morph mismatch"):
            mod.validate(rows)

    def test_missing_figure_hash_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["notes"] = "Panels B and C both print FC-3559(BP); no colour inferred from locality"
        with self.assertRaisesRegex(ValueError, "image hash"):
            mod.validate(rows)

    def test_single_panel_claim_fails(self) -> None:
        rows = self.valid_rows()
        rows[0]["notes"] = (
            f"Panel C prints FC-3559(BP); official Figure 1 image SHA256 "
            f"{mod.EXPECTED_FIGURE_IMAGE_HASH}; no colour inferred from locality"
        )
        with self.assertRaisesRegex(ValueError, "two-panel transcription"):
            mod.validate(rows)

    def test_silent_herbarium_harmonization_fails(self) -> None:
        rows = self.valid_rows()
        for row in rows:
            if row["voucher"] == "ccy3839":
                row["supplement_s6_herbarium"] = "TCF"
        with self.assertRaisesRegex(ValueError, "conflicts"):
            mod.validate(rows)

    def test_extra_conflict_fails(self) -> None:
        rows = self.valid_rows()
        for row in rows:
            if row["voucher"] == "ccy3559":
                row["supplement_s6_herbarium"] = "TCF"
        with self.assertRaisesRegex(ValueError, "conflicts"):
            mod.validate(rows)

    def test_missing_voucher_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "six voucher rows"):
            mod.validate(self.valid_rows()[:-1])

    def test_nonrecovered_s6_cannot_contain_data(self) -> None:
        rows = self.valid_rows()
        for row in rows:
            if row["voucher"] == "ccy3807":
                row["supplement_s6_transcription"] = "invented"
        with self.assertRaisesRegex(ValueError, "invented data"):
            mod.validate(rows)

    def test_wrong_figure_definition_fails(self) -> None:
        rows = deepcopy(self.valid_rows())
        rows[0]["figure1_state_definition"] = "W and BP exist"
        with self.assertRaisesRegex(ValueError, "Figure 1 state definition"):
            mod.validate(rows)


if __name__ == "__main__":
    unittest.main()
