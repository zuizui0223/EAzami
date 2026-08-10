#!/usr/bin/env python3
"""Tests for Chang 2026 public TSA/Assembly metadata audit."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import audit_chang2026_public_transcriptome_assemblies as mod  # noqa: E402


class ChangPublicAssemblyAuditTests(unittest.TestCase):
    def manifest_row(self, confidence: str = "verified") -> dict[str, str]:
        return {
            "taxon": "C. japonicum var. takaoense",
            "code": "FC",
            "voucher": "ccy3559",
            "published_figure_label": "BP",
            "flower_colour_state": "bluish-purple",
            "matched_run": "SRR100",
            "matched_biosample": "SAMN100",
            "match_confidence": confidence,
        }

    def test_query_construction(self) -> None:
        self.assertEqual(
            mod.tsa_query_for_biosample("SAMN100"),
            '"SAMN100"[BioSample] AND tsa[filter]',
        )
        self.assertEqual(
            mod.tsa_query_for_voucher("ccy3559"),
            '"ccy3559"[All Fields] AND tsa[filter]',
        )
        self.assertEqual(
            mod.assembly_query_for_biosample("SAMN100"),
            '"SAMN100"[BioSample]',
        )

    def test_parses_nuccore_summary(self) -> None:
        parsed = mod.parse_nuccore_summaries(
            [
                {
                    "uid": "1",
                    "caption": "GABC00000000",
                    "title": "Cirsium transcriptome shotgun assembly",
                    "assemblyacc": "GABC00000000.1",
                }
            ]
        )
        self.assertEqual(parsed[0]["accession"], "GABC00000000")
        self.assertEqual(parsed[0]["assembly_accession"], "GABC00000000.1")

    def test_public_tsa_is_preferred(self) -> None:
        def search(db: str, term: str):
            if db == "nuccore" and "BioSample" in term:
                return ["1"]
            return []

        def summary(db: str, ids):
            if db == "nuccore" and ids:
                return [
                    {
                        "uid": "1",
                        "caption": "GABC00000000",
                        "title": "Cirsium TSA",
                        "assemblyacc": "GABC00000000.1",
                    }
                ]
            return []

        row = mod.audit_row(
            self.manifest_row(), search_fn=search, summary_fn=summary
        )
        self.assertEqual(row["public_transcriptome_status"], "public_tsa_recovered")
        self.assertEqual(row["preferred_public_source"], "NCBI_TSA")
        self.assertEqual(row["tsa_accessions"], "GABC00000000")

    def test_voucher_fallback_is_used_only_after_empty_biosample_query(self) -> None:
        calls = []

        def search(db: str, term: str):
            calls.append((db, term))
            if db == "nuccore" and "All Fields" in term:
                return ["2"]
            return []

        def summary(db: str, ids):
            if db == "nuccore" and ids:
                return [{"uid": "2", "caption": "GDEF00000000", "title": "fallback"}]
            return []

        row = mod.audit_row(
            self.manifest_row(), search_fn=search, summary_fn=summary
        )
        self.assertEqual(row["tsa_biosample_hit_count"], 0)
        self.assertEqual(row["tsa_voucher_fallback_hit_count"], 1)
        self.assertEqual(row["public_transcriptome_status"], "public_tsa_recovered")
        self.assertIn(("nuccore", '"ccy3559"[All Fields] AND tsa[filter]'), calls)

    def test_assembly_record_without_tsa_is_retained(self) -> None:
        def search(db: str, term: str):
            return ["10"] if db == "assembly" else []

        def summary(db: str, ids):
            if db == "assembly" and ids:
                return [
                    {
                        "uid": "10",
                        "assemblyaccession": "GCA_000000001.1",
                        "assemblyname": "test assembly",
                        "assemblystatus": "Contig",
                    }
                ]
            return []

        row = mod.audit_row(
            self.manifest_row(), search_fn=search, summary_fn=summary
        )
        self.assertEqual(
            row["public_transcriptome_status"],
            "public_assembly_record_recovered_no_tsa_hit",
        )
        self.assertEqual(row["preferred_public_source"], "NCBI_Assembly")
        self.assertEqual(row["assembly_accessions"], "GCA_000000001.1")

    def test_no_hit_selects_de_novo_sra_fallback(self) -> None:
        row = mod.audit_row(
            self.manifest_row(),
            search_fn=lambda db, term: [],
            summary_fn=lambda db, ids: [],
        )
        self.assertEqual(
            row["public_transcriptome_status"],
            "not_recovered_by_current_ncbi_query",
        )
        self.assertEqual(
            row["preferred_public_source"], "de_novo_from_official_SRA"
        )

    def test_unverified_run_is_not_queried(self) -> None:
        calls = []

        def search(db: str, term: str):
            calls.append((db, term))
            return []

        row = mod.audit_row(
            self.manifest_row(confidence="ambiguous"),
            search_fn=search,
            summary_fn=lambda db, ids: [],
        )
        self.assertEqual(calls, [])
        self.assertEqual(
            row["public_transcriptome_status"],
            "run_or_biosample_not_verified",
        )
        self.assertEqual(row["preferred_public_source"], "resolve_run_first")

    def test_query_error_is_not_misreported_as_no_hit(self) -> None:
        def search(db: str, term: str):
            raise RuntimeError("temporary error")

        row = mod.audit_row(
            self.manifest_row(),
            search_fn=search,
            summary_fn=lambda db, ids: [],
        )
        self.assertEqual(
            row["public_transcriptome_status"],
            "query_incomplete_due_to_ncbi_error",
        )
        self.assertIn("RuntimeError", row["query_error"])

    def test_summary_separates_takaoense_fallback(self) -> None:
        rows = [
            {
                "taxon": "C. japonicum var. takaoense",
                "code": "FC",
                "voucher": "ccy3559",
                "published_figure_label": "BP",
                "matched_run": "SRR1",
                "matched_biosample": "SAMN1",
                "public_transcriptome_status": "not_recovered_by_current_ncbi_query",
                "preferred_public_source": "de_novo_from_official_SRA",
                "tsa_accessions": "",
                "assembly_accessions": "",
            },
            {
                "taxon": "C. lineare",
                "code": "LN",
                "voucher": "x",
                "published_figure_label": "",
                "matched_run": "SRR2",
                "matched_biosample": "SAMN2",
                "public_transcriptome_status": "public_tsa_recovered",
                "preferred_public_source": "NCBI_TSA",
                "tsa_accessions": "GABC00000000",
                "assembly_accessions": "",
            },
        ]
        summary = mod.build_summary(rows)
        self.assertEqual(summary["sample_rows"], 2)
        self.assertEqual(summary["samples_with_public_tsa"], 1)
        self.assertEqual(summary["takaoense_rows"], 1)
        self.assertEqual(summary["takaoense_de_novo_sra_fallback_rows"], 1)


if __name__ == "__main__":
    unittest.main()
