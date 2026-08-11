#!/usr/bin/env python3
"""Tests for source-backed reconciliation of the complete Chang run universe."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import reconcile_chang2026_complete_runs as mod  # noqa: E402


class ChangCompleteReconciliationTests(unittest.TestCase):
    def supplement_row(
        self,
        *,
        voucher: str = "ccy3559",
        code: str = "FC",
        accession: str = "",
        raw_reads: str = "49885086",
    ) -> dict[str, str]:
        return {
            "taxon": "C. japonicum var. takaoense",
            "sample_number_within_taxon": "1",
            "location": "TAIWAN. Chiayi County: Fenchihu",
            "code": code,
            "voucher": voucher,
            "herbarium": "TNM",
            "raw_reads": raw_reads,
            "embedded_public_accession": accession,
        }

    def run_row(
        self,
        *,
        run: str = "SRR35152718",
        isolate: str = "3559",
        spots: str = "24942543",
        biosample: str = "SAMN50798021",
        experiment: str = "SRX30258006",
        layout: str = "PAIRED",
    ) -> dict[str, str]:
        return {
            "Run": run,
            "Experiment": experiment,
            "BioSample": biosample,
            "BioProject": "PRJNA1311153",
            "ScientificName": "Cirsium japonicum var. japonicum",
            "LibraryName": "8",
            "LibraryLayout": layout,
            "SampleName": "",
            "spots": spots,
            "biosample_isolate": isolate,
            "recovery_scope": "primary_bioproject",
        }

    def morph_row(
        self,
        *,
        voucher: str = "ccy3559",
        label: str = "BP",
    ) -> dict[str, str]:
        return {
            "voucher": voucher,
            "direct_figure_label": label,
            "flower_colour_state": "bluish-purple" if label == "BP" else "white",
            "binary_colour_code": "C" if label == "BP" else "W",
        }

    def test_numeric_biosample_isolate_becomes_exact_voucher_alias(self) -> None:
        rows, aliases = mod.enrich_runinfo_with_voucher_aliases(
            [self.supplement_row()],
            [self.run_row()],
        )
        self.assertEqual(aliases, {"ccy3559": "SRR35152718"})
        self.assertEqual(rows[0]["derived_voucher_alias"], "ccy3559")
        self.assertIn("voucher_alias:ccy3559", rows[0]["Description"])

    def test_alias_is_not_created_for_unlisted_isolate(self) -> None:
        rows, aliases = mod.enrich_runinfo_with_voucher_aliases(
            [self.supplement_row()],
            [self.run_row(isolate="9999")],
        )
        self.assertEqual(aliases, {})
        self.assertEqual(rows[0]["derived_voucher_alias"], "")

    def test_duplicate_alias_across_runs_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "not unique"):
            mod.enrich_runinfo_with_voucher_aliases(
                [self.supplement_row()],
                [
                    self.run_row(run="SRR1"),
                    self.run_row(run="SRR2"),
                ],
            )

    def test_direct_figure_label_is_normalized(self) -> None:
        index = mod.normalize_morph_rows([self.morph_row()])
        self.assertEqual(index["ccy3559"]["published_figure_label"], "BP")
        self.assertEqual(index["ccy3559"]["binary_colour_code"], "C")

    def test_official_layout_is_attached_by_exact_run(self) -> None:
        matches = [{"matched_run": "SRR35152718"}]
        counts = mod.attach_official_library_layout(matches, [self.run_row()])
        self.assertEqual(matches[0]["matched_library_layout"], "PAIRED")
        self.assertEqual(dict(counts), {"PAIRED": 1})

    def test_missing_or_unsupported_layout_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported LibraryLayout"):
            mod.attach_official_library_layout(
                [{"matched_run": "SRR35152718"}],
                [self.run_row(layout="")],
            )

    def test_voucher_alias_morph_and_layout_produce_verified_match(self) -> None:
        matches, candidates, summary = mod.reconcile_complete(
            [self.supplement_row()],
            [self.run_row()],
            [self.morph_row()],
        )
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual(row["matched_run"], "SRR35152718")
        self.assertEqual(row["match_status"], "verified_unique_voucher_token")
        self.assertEqual(row["match_confidence"], "verified")
        self.assertEqual(row["published_figure_label"], "BP")
        self.assertEqual(row["binary_colour_code"], "C")
        self.assertEqual(row["matched_library_layout"], "PAIRED")
        self.assertTrue(candidates)
        self.assertEqual(summary["verified_or_probable_rows"], 1)
        self.assertEqual(summary["derived_unique_voucher_aliases"], 1)
        self.assertEqual(summary["official_library_layout_counts"], {"PAIRED": 1})

    def test_embedded_run_accession_remains_strongest_evidence(self) -> None:
        matches, _, summary = mod.reconcile_complete(
            [
                self.supplement_row(
                    accession="SRR30617342",
                    voucher="ccy3446",
                    code="XH",
                    raw_reads="62493916",
                )
            ],
            [
                {
                    **self.run_row(
                        run="SRR30617342", isolate="", spots="31246958"
                    ),
                    "ScientificName": "Cirsium lineare",
                    "BioProject": "PRJNA777777",
                }
            ],
            [],
        )
        self.assertEqual(matches[0]["match_status"], "verified_exact_run_accession")
        self.assertEqual(matches[0]["matched_run"], "SRR30617342")
        self.assertEqual(matches[0]["embedded_public_accession"], "SRR30617342")
        self.assertEqual(matches[0]["matched_library_layout"], "PAIRED")
        self.assertEqual(summary["embedded_identifier_type_counts"], {"run": 1})

    def test_embedded_biosample_resolves_to_run_and_preserves_accession(self) -> None:
        matches, _, summary = mod.reconcile_complete(
            [self.supplement_row(accession="SAMN50798021")],
            [self.run_row()],
            [self.morph_row()],
        )
        row = matches[0]
        self.assertEqual(row["matched_run"], "SRR35152718")
        self.assertEqual(row["embedded_public_accession"], "SAMN50798021")
        self.assertEqual(
            row["match_status"],
            "verified_exact_embedded_biosample_accession",
        )
        self.assertEqual(row["match_confidence"], "verified")
        self.assertIn("exact_embedded_biosample_accession", row["match_evidence"])
        self.assertEqual(
            summary["embedded_identifier_type_counts"], {"biosample": 1}
        )

    def test_embedded_experiment_resolves_to_run(self) -> None:
        matches, _, _ = mod.reconcile_complete(
            [self.supplement_row(accession="SRX30258006")],
            [self.run_row()],
            [self.morph_row()],
        )
        self.assertEqual(
            matches[0]["match_status"],
            "verified_exact_embedded_experiment_accession",
        )
        self.assertEqual(matches[0]["embedded_public_accession"], "SRX30258006")


if __name__ == "__main__":
    unittest.main()
