#!/usr/bin/env python3
"""Offline tests for the source-backed COS763 HybPiper-readiness audit."""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
MODULE_PATH = ANALYSIS_DIR / "audit_cos763_hybpiper_readiness.py"
SPEC = importlib.util.spec_from_file_location(
    "audit_cos763_hybpiper_readiness", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["audit_cos763_hybpiper_readiness"] = mod
SPEC.loader.exec_module(mod)


class Cos763ReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def alignment_zip() -> bytes:
        """Create all 763 expected loci with known frame diagnostics."""
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            for index in range(1, 764):
                locus = f"COS_{index}"
                if index == 1:
                    # Gap removal must recover a direct 90-nt candidate.
                    aligned = "ATG-" * 30
                elif index == 2:
                    # Mapping-compatible but not divisible by three.
                    aligned = ("ATG" * 30) + "A"
                elif index == 3:
                    # Divisible by three but contains one internal frame-0 stop.
                    aligned = ("ATG" * 10) + "TAA" + ("ATG" * 19)
                else:
                    aligned = "ATG" * 30
                archive.writestr(
                    f"COS_alignment_files_NEW/{locus}.fasta",
                    f">Taxon_{index} reference\n{aligned}\n",
                )
        return payload.getvalue()

    def test_analyze_preserves_all_loci_and_rejects_incompatible_sequences(self) -> None:
        sequence_rows, locus_rows, mapping, direct = mod.analyze(
            self.alignment_zip(),
            min_length=90,
            max_ambiguous_fraction=0.01,
        )
        self.assertEqual(len(sequence_rows), 763)
        self.assertEqual(len(locus_rows), 763)
        self.assertEqual(len(mapping), 763)
        self.assertEqual(len(direct), 761)

        first = next(row for row in sequence_rows if row["locus"] == "COS_1")
        second = next(row for row in sequence_rows if row["locus"] == "COS_2")
        third = next(row for row in sequence_rows if row["locus"] == "COS_3")
        self.assertEqual(first["ungapped_length"], 90)
        self.assertEqual(first["mapping_header"], "Taxon_1-COS_1")
        self.assertEqual(first["direct_cds_candidate"], "true")
        self.assertEqual(second["length_mod_3"], 1)
        self.assertEqual(second["direct_cds_candidate"], "false")
        self.assertEqual(third["internal_stop_count_frame0"], 1)
        self.assertEqual(third["direct_cds_candidate"], "false")

    def test_summary_refuses_incomplete_direct_target(self) -> None:
        alignment_zip = self.alignment_zip()
        sequence_rows, locus_rows, mapping, direct = mod.analyze(
            alignment_zip,
            min_length=90,
            max_ambiguous_fraction=0.01,
        )
        source = self.root / "dryad_outer.zip"
        source.write_bytes(b"source archive bytes")
        summary = mod.build_summary(
            source_archive=source,
            nested_member="nested/COS_alignment_files_NEW.zip",
            source_bytes=source.read_bytes(),
            alignment_zip=alignment_zip,
            sequence_rows=sequence_rows,
            locus_rows=locus_rows,
            mapping_count=len(mapping),
            direct_count=len(direct),
            min_length=90,
            max_ambiguous_fraction=0.01,
        )
        self.assertEqual(summary["locus_count"], 763)
        self.assertEqual(summary["sequence_count"], 763)
        self.assertEqual(summary["loci_with_at_least_one_direct_cds_candidate"], 761)
        self.assertFalse(summary["ready_as_complete_direct_hybpiper_nucleotide_target"])
        self.assertEqual(
            summary["recommended_role"],
            "mapping_reference_or_frame-correction_input_only",
        )
        self.assertIn("not the exact Moreyra", summary["claim_limit"])

    def test_locates_one_nested_alignment_archive(self) -> None:
        expected = self.alignment_zip()
        outer = self.root / "downloaded_dryad_candidate.zip"
        with zipfile.ZipFile(outer, "w") as archive:
            archive.writestr(
                "nested/COS_alignment_files_NEW.zip",
                expected,
            )
            archive.writestr("README.txt", "provenance")

        source, member, payload = mod.locate_alignment_archive(
            archive=outer,
            archive_dir=None,
        )
        self.assertEqual(source, outer)
        self.assertEqual(member, "nested/COS_alignment_files_NEW.zip")
        self.assertEqual(payload, expected)

    def test_requires_exactly_763_alignment_files(self) -> None:
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("COS_1.fasta", ">Taxon\nATGATGATG\n")
        with self.assertRaisesRegex(ValueError, "Expected 763"):
            mod.analyze(
                payload.getvalue(),
                min_length=3,
                max_ambiguous_fraction=0.01,
            )


if __name__ == "__main__":
    unittest.main()
