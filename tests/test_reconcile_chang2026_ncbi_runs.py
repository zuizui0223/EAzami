#!/usr/bin/env python3
"""Tests for Chang 2026 supplement-to-PRJNA1311153 reconciliation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import reconcile_chang2026_ncbi_runs as mod  # noqa: E402


class ChangNcbiReconciliationTests(unittest.TestCase):
    def source(
        self,
        *,
        taxon: str = "C. japonicum var. takaoense",
        code: str = "FC",
        voucher: str = "ccy3559",
        location: str = "TAIWAN. Chiayi County: Fenchihu",
        raw_reads: str = "49885086",
        accession: str = "",
    ) -> dict[str, str]:
        return {
            "taxon": taxon,
            "sample_number_within_taxon": "1",
            "location": location,
            "code": code,
            "voucher": voucher,
            "herbarium": "TNM",
            "raw_reads": raw_reads,
            "embedded_public_accession": accession,
        }

    def run(
        self,
        *,
        run: str = "SRR100",
        scientific_name: str = "Cirsium japonicum var. takaoense",
        library: str = "ccy3559_FC",
        sample_name: str = "ccy3559",
        spots: str = "24942543",
        locality: str = "Taiwan: Fenchihu",
    ) -> dict[str, str]:
        return {
            "Run": run,
            "Experiment": "SRX100",
            "BioSample": "SAMN100",
            "BioProject": "PRJNA1311153",
            "ScientificName": scientific_name,
            "LibraryName": library,
            "SampleName": sample_name,
            "spots": spots,
            "geographic_location": locality,
        }

    def test_taxon_normalization(self) -> None:
        self.assertEqual(
            mod.canonical_taxon("C. japonicum var. takaoense"),
            "cirsium japonicum var. takaoense",
        )
        self.assertEqual(
            mod.taxon_relation(
                "C. japonicum var. takaoense",
                "Cirsium japonicum var. takaoense",
            ),
            "exact_taxon",
        )
        self.assertEqual(
            mod.taxon_relation(
                "C. japonicum var. takaoense",
                "Cirsium japonicum",
            ),
            "same_species_broad_name",
        )

    def test_exact_accession_dominates(self) -> None:
        source = self.source(accession="SRR200")
        candidates = [
            self.run(run="SRR100", library="ccy3559", sample_name="ccy3559"),
            self.run(
                run="SRR200",
                library="unlabelled",
                sample_name="unlabelled",
                spots="10",
                locality="",
            ),
        ]
        ranked = sorted(
            (mod.score_candidate(source, row) for row in candidates),
            key=lambda row: -int(row["score"]),
        )
        status, confidence, _ = mod.classify_match(source, ranked)
        self.assertEqual(ranked[0]["run"], "SRR200")
        self.assertEqual(status, "verified_exact_run_accession")
        self.assertEqual(confidence, "verified")

    def test_voucher_token_verifies_unique_run(self) -> None:
        source = self.source(raw_reads="")
        candidates = [
            self.run(run="SRR100", library="ccy3559_RNA", spots=""),
            self.run(
                run="SRR101",
                library="ccy9999_RNA",
                sample_name="ccy9999",
                spots="",
                locality="Taiwan",
            ),
        ]
        ranked = sorted(
            (mod.score_candidate(source, row) for row in candidates),
            key=lambda row: -int(row["score"]),
        )
        status, confidence, _ = mod.classify_match(source, ranked)
        self.assertEqual(ranked[0]["run"], "SRR100")
        self.assertEqual(status, "verified_unique_voucher_token")
        self.assertEqual(confidence, "verified")

    def test_exact_paired_read_count_plus_taxon_verifies(self) -> None:
        source = self.source(voucher="", code="ZZ", location="")
        candidates = [
            self.run(
                run="SRR100",
                library="unknown",
                sample_name="unknown",
                spots="24942543",
                locality="",
            ),
            self.run(
                run="SRR101",
                scientific_name="Cirsium lineare",
                library="unknown2",
                sample_name="unknown2",
                spots="20000000",
                locality="",
            ),
        ]
        ranked = sorted(
            (mod.score_candidate(source, row) for row in candidates),
            key=lambda row: -int(row["score"]),
        )
        status, confidence, _ = mod.classify_match(source, ranked)
        self.assertEqual(ranked[0]["read_count_relation"], "exact_paired_end_raw_reads_equals_2x_spots")
        self.assertEqual(status, "verified_unique_read_count_and_taxon")
        self.assertEqual(confidence, "verified")

    def test_short_code_or_locality_alone_never_verifies(self) -> None:
        source = self.source(voucher="", raw_reads="")
        candidate = self.run(
            scientific_name="Cirsium lineare",
            library="FC",
            sample_name="other",
            spots="",
            locality="Taiwan: Fenchihu",
        )
        ranked = [mod.score_candidate(source, candidate)]
        status, confidence, _ = mod.classify_match(source, ranked)
        self.assertEqual(confidence, "ambiguous")
        self.assertEqual(status, "ambiguous_insufficient_independent_evidence")

    def test_tied_exact_read_count_is_ambiguous(self) -> None:
        source = self.source(voucher="", code="", location="")
        candidates = [
            self.run(run="SRR100", library="a", sample_name="a"),
            self.run(run="SRR101", library="b", sample_name="b"),
        ]
        ranked = sorted(
            (mod.score_candidate(source, row) for row in candidates),
            key=lambda row: (-int(row["score"]), str(row["run"])),
        )
        status, confidence, _ = mod.classify_match(source, ranked)
        self.assertEqual(ranked[0]["score"], ranked[1]["score"])
        self.assertEqual(status, "ambiguous_tied_top_candidates")
        self.assertEqual(confidence, "ambiguous")

    def test_run_collision_is_downgraded(self) -> None:
        sources = [
            self.source(voucher="ccy3559", code="FC", raw_reads=""),
            self.source(voucher="ccy3559", code="FC", raw_reads=""),
        ]
        matches, _ = mod.reconcile(sources, [self.run(spots="")], {})
        self.assertEqual(len(matches), 2)
        self.assertTrue(
            all(row["run_assignment_collision"] == "true" for row in matches)
        )
        self.assertTrue(
            all(row["match_confidence"] == "ambiguous" for row in matches)
        )

    def test_morph_assignment_is_joined_by_voucher(self) -> None:
        source = self.source()
        morphs = {
            "ccy3559": {
                "published_figure_label": "BP",
                "flower_colour_state": "bluish-purple",
                "binary_colour_code": "C",
            }
        }
        matches, _ = mod.reconcile([source], [self.run()], morphs)
        self.assertEqual(matches[0]["published_figure_label"], "BP")
        self.assertEqual(matches[0]["binary_colour_code"], "C")


if __name__ == "__main__":
    unittest.main()
