#!/usr/bin/env python3
"""Tests for deterministic FASTA header prefixing."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import prefix_fasta_headers as mod  # noqa: E402


class PrefixFastaHeadersTests(unittest.TestCase):
    def test_prefixes_identifiers_and_preserves_sequences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.fa"
            output_path = Path(tmp) / "output.fa"
            input_path.write_text(
                ">transcript1 description\nMPEPTIDE\n>transcript2\nACGTACGT\n",
                encoding="utf-8",
            )
            summary = mod.prefix_fasta(input_path, output_path, "FC_ccy3559")
            self.assertEqual(summary["record_count"], 2)
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                ">FC_ccy3559|transcript1\nMPEPTIDE\n"
                ">FC_ccy3559|transcript2\nACGTACGT\n",
            )

    def test_duplicate_original_identifier_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.fa"
            output_path = Path(tmp) / "output.fa"
            input_path.write_text(
                ">x one\nAAAA\n>x two\nCCCC\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                mod.prefix_fasta(input_path, output_path, "sample")

    def test_invalid_sample_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.fa"
            output_path = Path(tmp) / "output.fa"
            input_path.write_text(">x\nAAAA\n", encoding="utf-8")
            for sample_id in ("", "bad id", "bad|id"):
                with self.subTest(sample_id=sample_id):
                    with self.assertRaises(ValueError):
                        mod.prefix_fasta(input_path, output_path, sample_id)

    def test_sequence_before_header_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.fa"
            output_path = Path(tmp) / "output.fa"
            input_path.write_text("AAAA\n>x\nCCCC\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.prefix_fasta(input_path, output_path, "sample")


if __name__ == "__main__":
    unittest.main()
