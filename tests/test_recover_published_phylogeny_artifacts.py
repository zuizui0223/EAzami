#!/usr/bin/env python3
"""Tests for public phylogeny artifact manifest recovery and DOCX extraction."""

from __future__ import annotations

import csv
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "recover_published_phylogeny_artifacts.py"
SPEC = importlib.util.spec_from_file_location("recover_published_phylogeny_artifacts", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
art = importlib.util.module_from_spec(SPEC)
sys.modules["recover_published_phylogeny_artifacts"] = art
SPEC.loader.exec_module(art)


def minimal_docx(path: Path) -> None:
    document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Supplementary Table S1</w:t></w:r></w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>Taxon</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Voucher</w:t></w:r></w:p></w:tc>
      </w:tr>
      <w:tr>
        <w:tc><w:p><w:r><w:t>Cirsium testum</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>ABC123</w:t></w:r></w:p></w:tc>
      </w:tr>
    </w:tbl>
    <w:p><w:r><w:t>End.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("[Content_Types].xml", "<Types/>")


class ArtifactRecoveryTests(unittest.TestCase):
    def test_safe_name_and_bool(self) -> None:
        self.assertEqual(art.safe_name(" Chang 2026 / supp "), "Chang_2026_supp")
        self.assertTrue(art.parse_bool("TRUE"))
        self.assertFalse(art.parse_bool("false"))

    def test_sha256_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.txt"
            path.write_bytes(b"abc")
            self.assertEqual(
                art.sha256_file(path),
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            )

    def test_extract_docx_text_and_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docx = root / "supp.docx"
            minimal_docx(docx)
            text_path, table_paths = art.extract_docx(docx, root / "extracted")
            self.assertEqual(len(table_paths), 1)
            text = text_path.read_text(encoding="utf-8")
            self.assertIn("Supplementary Table S1", text)
            self.assertIn("[TABLE 1: table_001.csv]", text)
            self.assertIn("End.", text)
            with table_paths[0].open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            self.assertEqual(rows[0], ["Taxon", "Voucher"])
            self.assertEqual(rows[1], ["Cirsium testum", "ABC123"])

    def test_manifest_validation_and_duplicate_detection(self) -> None:
        fields = [
            "artifact_key", "citation_key", "artifact_type", "host", "landing_url",
            "download_url", "requires_auth", "license", "expected_size_bytes",
            "expected_filename", "status", "extraction", "notes",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "artifact_key": "one", "citation_key": "Study", "artifact_type": "tree",
                    "host": "Dryad", "landing_url": "x", "download_url": "y",
                    "requires_auth": "false", "license": "CC0", "expected_size_bytes": "1",
                    "expected_filename": "tree.nwk", "status": "verified", "extraction": "plain_text",
                    "notes": "",
                })
            rows = art.read_manifest(path)
            self.assertEqual(rows[0]["artifact_key"], "one")

            with path.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writerow({
                    "artifact_key": "one", "citation_key": "Study2", "artifact_type": "tree",
                    "host": "Dryad", "landing_url": "x", "download_url": "z",
                    "requires_auth": "false", "license": "CC0", "expected_size_bytes": "",
                    "expected_filename": "tree2.nwk", "status": "verified", "extraction": "plain_text",
                    "notes": "",
                })
            with self.assertRaisesRegex(ValueError, "Duplicate artifact_key"):
                art.read_manifest(path)

    def test_recover_skips_auth_and_unverified_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp)
            downloader = art.Downloader()
            base = {
                "artifact_key": "auth", "citation_key": "X", "artifact_type": "dataset",
                "host": "Mendeley", "download_url": "", "requires_auth": "true",
                "expected_filename": "x", "expected_size_bytes": "", "extraction": "mendeley_api",
            }
            auth = art.recover_one(base, outdir, downloader)
            self.assertEqual(auth["status"], "skipped_requires_auth")
            no_url_row = dict(base)
            no_url_row.update({"artifact_key": "no_url", "requires_auth": "false"})
            no_url = art.recover_one(no_url_row, outdir, downloader)
            self.assertEqual(no_url["status"], "skipped_no_verified_direct_url")


if __name__ == "__main__":
    unittest.main()
