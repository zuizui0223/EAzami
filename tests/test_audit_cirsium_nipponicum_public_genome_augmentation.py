from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "nipponicum_audit", ROOT / "analysis/audit_cirsium_nipponicum_public_genome_augmentation.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["nipponicum_audit"] = mod
SPEC.loader.exec_module(mod)


class NipponicumGenomeAuditTests(unittest.TestCase):
    def fixture(self):
        return {
            "id": 26927092,
            "title": "Genome assembly and annotations of Cirsium nipponicum",
            "doi": "10.6084/m9.figshare.26927092",
            "files": [
                {
                    "id": 1,
                    "name": "Cirsium_nipponicum_genome.fasta.gz",
                    "size": 1000,
                    "download_url": "https://example.org/genome.gz",
                    "supplied_md5": "abc",
                    "computed_md5": "abc",
                    "is_link_only": False,
                },
                {
                    "id": 2,
                    "name": "Cirsium_nipponicum.gff3.gz",
                    "size": 100,
                    "download_url": "https://example.org/ann.gz",
                    "supplied_md5": "def",
                    "computed_md5": "def",
                    "is_link_only": False,
                },
            ],
        }

    def test_public_sequence_files_make_augmentation_candidate(self):
        rows, summary = mod.audit(self.fixture())
        self.assertEqual(len(rows), 2)
        self.assertTrue(summary["augmentation_candidate"])
        self.assertFalse(summary["primary_294_panel_changed"])
        self.assertFalse(summary["tree_tip_promotion_allowed"])
        self.assertEqual(summary["sequence_or_archive_candidate_count"], 2)

    def test_wrong_article_is_fatal(self):
        data = self.fixture()
        data["id"] = 1
        with self.assertRaisesRegex(ValueError, "unexpected Figshare article id"):
            mod.audit(data)

    def test_nonsequence_files_do_not_promote(self):
        data = self.fixture()
        data["files"] = [{
            "id": 3,
            "name": "README.txt",
            "size": 50,
            "download_url": "https://example.org/readme",
            "supplied_md5": "",
            "computed_md5": "",
            "is_link_only": False,
        }]
        _, summary = mod.audit(data)
        self.assertFalse(summary["augmentation_candidate"])


if __name__ == "__main__":
    unittest.main()
