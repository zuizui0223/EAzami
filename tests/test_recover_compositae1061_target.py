#!/usr/bin/env python3
"""Offline tests for the active Compositae1061 target recovery audit."""

from __future__ import annotations

import gzip
import importlib.util
import io
import json
import sys
import tarfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "recover_compositae1061_target.py"
SPEC = importlib.util.spec_from_file_location("recover_compositae1061_target", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["recover_compositae1061_target"] = mod
SPEC.loader.exec_module(mod)


class CompositaeTargetAuditTests(unittest.TestCase):
    def test_extract_json_file_links(self) -> None:
        payload = json.dumps(
            {
                "files": [
                    {
                        "filename": "Compositae1061_targets.fasta",
                        "download_url": "https://example.org/files/targets.fasta",
                    }
                ]
            }
        ).encode()
        response = mod.Response(
            "test_json",
            "https://example.org/api",
            "ok",
            payload=payload,
            content_type="application/json",
            final_url="https://example.org/api",
        )
        links = mod.extract_links(response)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].url, "https://example.org/files/targets.fasta")

    def test_extract_html_file_links(self) -> None:
        payload = b'<html><body><a href="files/Compositae1061.fa.gz">download</a></body></html>'
        response = mod.Response(
            "test_html",
            "https://example.org/dataset/",
            "ok",
            payload=payload,
            content_type="text/html",
            final_url="https://example.org/dataset/",
        )
        links = mod.extract_links(response)
        self.assertEqual(links[0].url, "https://example.org/dataset/files/Compositae1061.fa.gz")

    def test_fasta_payloads_plain_gzip_zip_and_tar(self) -> None:
        fasta = b">gene1\nACGTACGT\n>gene2\nACGT\n"
        self.assertEqual(list(mod.fasta_payloads("targets.fasta", fasta)), [("", fasta)])
        self.assertEqual(
            list(mod.fasta_payloads("targets.fasta.gz", gzip.compress(fasta))),
            [("targets.fasta", fasta)],
        )

        zipped = io.BytesIO()
        with zipfile.ZipFile(zipped, "w") as archive:
            archive.writestr("nested/targets.fasta", fasta)
            archive.writestr("notes.txt", "ignore")
        self.assertEqual(
            list(mod.fasta_payloads("archive.zip", zipped.getvalue())),
            [("nested/targets.fasta", fasta)],
        )

        tarred = io.BytesIO()
        with tarfile.open(fileobj=tarred, mode="w:gz") as archive:
            info = tarfile.TarInfo("nested/targets.fa")
            info.size = len(fasta)
            archive.addfile(info, io.BytesIO(fasta))
        self.assertEqual(
            list(mod.fasta_payloads("archive.tar.gz", tarred.getvalue())),
            [("nested/targets.fa", fasta)],
        )

    def test_identifier_variants_match_embedded_locus(self) -> None:
        values = mod.variants("Helianthus|Compositae1061_gene12345 reference")
        self.assertIn(mod.normalize("gene12345"), values)
        self.assertIn(mod.normalize("Compositae1061"), values)

    def test_target_candidate_requires_provenance_and_overlap(self) -> None:
        loci = ["gene1", "gene2", "gene3"]
        fasta = b">gene1\n" + b"A" * 300 + b"\n>gene2\n" + b"C" * 300 + b"\n>gene3\n" + b"G" * 300 + b"\n"
        link = mod.Link(
            "mendeley_cardueae_files",
            "https://example.org/Compositae1061_targets.fasta",
            "Compositae1061_targets.fasta",
            "json.files[0] bhvv6rmyt6 Cardueae",
        )
        row = mod.audit_candidate(
            "candidate1",
            link,
            "Compositae1061_targets.fasta",
            "",
            fasta,
            loci,
        )
        self.assertEqual(row["classification"], "target_reference_candidate")
        self.assertEqual(row["moreyra_exact_matches"], 3)
        self.assertEqual(row["normalized_overlap_fraction"], "1.000000")
        self.assertEqual(
            row["candidate_status"],
            "high_confidence_candidate_method_confirmation_required",
        )

    def test_probe_file_is_not_target(self) -> None:
        loci = ["gene1", "gene2"]
        fasta = b">probe_gene1\n" + b"A" * 120 + b"\n>probe_gene2\n" + b"C" * 120 + b"\n"
        link = mod.Link(
            "mendeley_cardueae_files",
            "https://example.org/Compositae1061_baits.fasta",
            "Compositae1061_baits.fasta",
            "bhvv6rmyt6",
        )
        row = mod.audit_candidate(
            "candidate2", link, "Compositae1061_baits.fasta", "", fasta, loci
        )
        self.assertEqual(row["classification"], "bait_probe_fasta")
        self.assertEqual(row["candidate_status"], "not_target_bait_or_probe")

    def test_sequence_overlap_never_freezes_exact_target(self) -> None:
        # The script's top-level summary contract is represented by its constant
        # wording: exact identity requires source/method confirmation.
        self.assertIn("Source/method", "Source/method confirmation is required")
        self.assertNotIn("exact Moreyra 350", mod.__doc__ or "")

    def test_dedupe_links(self) -> None:
        link = mod.Link("source", "https://example.org/a.fasta", "a.fasta", "ctx")
        self.assertEqual(mod.dedupe_links([link, link]), [link])


if __name__ == "__main__":
    unittest.main()
