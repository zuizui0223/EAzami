#!/usr/bin/env python3
"""Offline tests for Moreyra et al. 2025 evidence recovery."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "recover_moreyra2025_evidence.py"
SPEC = importlib.util.spec_from_file_location("recover_moreyra2025_evidence", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["recover_moreyra2025_evidence"] = mod
SPEC.loader.exec_module(mod)


class MoreyraRecoveryTests(unittest.TestCase):
    def test_canonical_taxon_strips_authorship_and_keeps_rank(self) -> None:
        self.assertEqual(mod.canonical_taxon("Cirsium pendulum Fisch. ex DC."), "cirsium pendulum")
        self.assertEqual(
            mod.canonical_taxon("Cirsium nipponicum var. incomptum Kitam."),
            "cirsium nipponicum var. incomptum",
        )

    def test_sample_table_selection_prefers_biosample_voucher_table(self) -> None:
        small = [["Metric", "Value"], ["AIC", "12.2"]]
        samples = [
            ["Species", "Sample", "BioSample", "Voucher", "Country"],
            ["Cirsium pendulum", "x1", "SAMN1", "V1", "Japan"],
        ] + [["Cirsium test", str(i), f"SAMN{i}", f"V{i}", "China"] for i in range(30)]
        self.assertEqual(mod.select_sample_table([small, samples]), 1)

    def test_normalized_table_and_taxon_extraction(self) -> None:
        rows = [
            ["Supplementary Table S1", "", ""],
            ["Species", "BioSample", "Voucher"],
            ["Cirsium sieboldii Nakai", "SAMN1", "ABC123"],
        ]
        normalized = mod.normalized_table(rows)
        self.assertEqual(len(normalized), 1)
        self.assertEqual(mod.extract_taxon(normalized[0]), "Cirsium sieboldii")
        self.assertEqual(normalized[0]["biosample"], "SAMN1")

    def test_name_lookup_preserves_alias_status(self) -> None:
        rows = [
            {
                "accepted_taxon": "Cirsium sieboldii",
                "aliases": "Cirsium paludigenum;Cirsium sieboldii f. albiflorum",
                "focal_region": "Japan_China",
                "priority_class": "A",
            }
        ]
        lookup = mod.name_lookup(rows)
        self.assertEqual(lookup["cirsium sieboldii"], ("Cirsium sieboldii", "accepted"))
        self.assertEqual(lookup["cirsium paludigenum"], ("Cirsium sieboldii", "alias"))

    def test_combined_state_is_conservative(self) -> None:
        state, text = mod.combine_state(0, 0, False)
        self.assertEqual(state, "not_recovered_after_current_name_audit")
        self.assertIn("not proof", text)
        alias_state, _ = mod.combine_state(1, 1, True)
        self.assertTrue(alias_state.endswith("_via_alias"))


if __name__ == "__main__":
    unittest.main()
