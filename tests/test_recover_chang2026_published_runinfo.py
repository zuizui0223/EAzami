#!/usr/bin/env python3
"""Offline tests for the two-layer Chang 2026 SRA recovery."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import recover_chang2026_published_runinfo as mod  # noqa: E402


class ChangPublishedRuninfoTests(unittest.TestCase):
    def run_row(
        self,
        run: str,
        *,
        project: str = "PRJNA1311153",
        biosample: str = "SAMN1",
        experiment: str = "SRX1",
    ) -> dict[str, str]:
        return {
            "Run": run,
            "Experiment": experiment,
            "SRAStudy": "SRP1",
            "BioProject": project,
            "Sample": "SRS1",
            "BioSample": biosample,
            "ScientificName": "Cirsium japonicum var. japonicum",
            "LibraryName": "library1",
        }

    def test_embedded_accessions_accept_mixed_types(self) -> None:
        rows = [
            {"embedded_public_accession": "SRR30617347"},
            {"embedded_public_accession": ""},
            {"embedded_public_accession": "srr30617342"},
            {"embedded_public_accession": "SRX30258006"},
            {"embedded_public_accession": "SAMN43544268"},
            {"embedded_public_accession": "SRR30617347"},
        ]
        self.assertEqual(
            mod.embedded_accessions(rows),
            [
                "SAMN43544268",
                "SRR30617342",
                "SRR30617347",
                "SRX30258006",
            ],
        )
        self.assertEqual(mod.identifier_kind("SRR30617342"), "run")
        self.assertEqual(mod.identifier_kind("SRX30258006"), "experiment")
        self.assertEqual(mod.identifier_kind("SAMN43544268"), "biosample")

    def test_invalid_embedded_accession_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid embedded"):
            mod.embedded_accessions(
                [{"embedded_public_accession": "ERR30617347"}]
            )

    def test_identifier_row_matching_is_type_specific(self) -> None:
        row = self.run_row(
            "SRR1", biosample="SAMN43544268", experiment="SRX30258006"
        )
        self.assertTrue(mod.row_matches_identifier(row, "SRR1"))
        self.assertTrue(mod.row_matches_identifier(row, "SAMN43544268"))
        self.assertTrue(mod.row_matches_identifier(row, "SRX30258006"))
        self.assertFalse(mod.row_matches_identifier(row, "SAMN99999999"))

    def test_merge_preserves_two_provenance_layers(self) -> None:
        primary = [self.run_row("SRR1")]
        reused = [
            self.run_row(
                "SRR2", project="PRJNA777777", biosample="SAMN2"
            )
        ]
        rows = mod.merge_layers(primary, reused)
        by_run = {row["Run"]: row for row in rows}
        self.assertEqual(len(rows), 2)
        self.assertEqual(by_run["SRR1"]["recovery_scope"], "primary_bioproject")
        self.assertEqual(
            by_run["SRR2"]["recovery_scope"],
            "supplement_embedded_reused_run",
        )
        self.assertEqual(by_run["SRR2"]["BioProject"], "PRJNA777777")

    def test_same_run_can_record_both_scopes(self) -> None:
        row = self.run_row("SRR1")
        merged = mod.merge_layers([row], [row])
        self.assertEqual(len(merged), 1)
        self.assertEqual(
            merged[0]["recovery_scope"],
            "primary_bioproject|supplement_embedded_reused_run",
        )

    def test_enrichment_retains_numeric_isolate(self) -> None:
        rows = mod.enrich_with_biosample(
            [self.run_row("SRR1")],
            {
                "SAMN1": {
                    "isolate": "3559",
                    "geo_loc_name": "Taiwan",
                    "collection_date": "2022-06-01",
                }
            },
        )
        self.assertEqual(rows[0]["biosample_isolate"], "3559")
        self.assertEqual(rows[0]["geographic_location"], "Taiwan")

    def test_summary_records_identifier_types_and_union(self) -> None:
        supplement = [{"sample": str(index)} for index in range(3)]
        primary = [
            self.run_row("SRR1"),
            self.run_row("SRR2", biosample="SAMN2"),
        ]
        reused = [
            self.run_row(
                "SRR3", project="PRJNA777777", biosample="SAMN3"
            )
        ]
        complete = mod.merge_layers(primary, reused)
        identifiers = ["SAMN3", "SRR3"]
        summary = mod.build_summary(
            supplement,
            primary,
            identifiers,
            {
                "SAMN3": [reused[0]],
                "SRR3": [reused[0]],
            },
            complete,
        )
        self.assertEqual(summary["primary_bioproject_run_count"], 2)
        self.assertEqual(summary["supplement_embedded_identifier_count"], 2)
        self.assertEqual(
            summary["embedded_identifier_type_counts"],
            {"biosample": 1, "run": 1},
        )
        self.assertEqual(summary["complete_unique_run_count"], 3)
        self.assertEqual(summary["missing_embedded_identifiers"], [])


if __name__ == "__main__":
    unittest.main()
