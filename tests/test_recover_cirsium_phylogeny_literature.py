#!/usr/bin/env python3
"""Unit tests for the reproducible Cirsium phylogeny literature search."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "recover_cirsium_phylogeny_literature.py"
SPEC = importlib.util.spec_from_file_location("recover_cirsium_phylogeny_literature", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
lit = importlib.util.module_from_spec(SPEC)
sys.modules["recover_cirsium_phylogeny_literature"] = lit
SPEC.loader.exec_module(lit)


class LiteratureRecoveryTests(unittest.TestCase):
    def test_normalization_helpers(self) -> None:
        self.assertEqual(lit.canonical_doi("https://doi.org/10.1000/ABC. "), "10.1000/abc")
        self.assertEqual(
            lit.normalize_title("<i>Cirsium</i>: A phylogeny!"),
            "cirsium a phylogeny",
        )
        self.assertEqual(lit.clean_markup("A <i>thorny</i>   tale"), "A thorny tale")

    def test_read_queries_skips_comments_and_blanks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queries.txt"
            path.write_text("# comment\n\nCirsium phylogeny\n Cirsium RADseq \n", encoding="utf-8")
            self.assertEqual(
                lit.read_queries(path),
                ["Cirsium phylogeny", "Cirsium RADseq"],
            )

    def test_parse_crossref(self) -> None:
        payload = {
            "message": {
                "items": [
                    {
                        "DOI": "10.1111/TEST",
                        "title": ["A <i>Cirsium</i> phylogeny"],
                        "container-title": ["Systematic Botany"],
                        "published-online": {"date-parts": [[2025, 1, 2]]},
                        "author": [
                            {"given": "Ada", "family": "Lovelace"},
                            {"given": "Ruiqi", "family": "Zhang"},
                        ],
                        "URL": "https://doi.org/10.1111/TEST",
                        "abstract": "<jats:p>Target capture in Cirsium.</jats:p>",
                        "type": "journal-article",
                    }
                ]
            }
        }
        rows = lit.parse_crossref(payload, "Cirsium phylogeny")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["doi"], "10.1111/test")
        self.assertEqual(rows[0]["year"], "2025")
        self.assertEqual(rows[0]["title"], "A Cirsium phylogeny")
        self.assertEqual(rows[0]["authors"], "Ada Lovelace|Ruiqi Zhang")
        self.assertIn("Target capture", rows[0]["abstract"])

    def test_parse_europepmc(self) -> None:
        payload = {
            "resultList": {
                "result": [
                    {
                        "id": "12345678",
                        "source": "MED",
                        "title": "Reticulate evolution in Cirsium",
                        "pubYear": "2024",
                        "doi": "10.2222/RETICULATE",
                        "journalTitle": "Molecular Ecology",
                        "authorList": {
                            "author": [
                                {"fullName": "A Researcher"},
                                {"fullName": "B Botanist"},
                            ]
                        },
                        "abstractText": "RAD-seq detects introgression.",
                        "pubType": "research-article",
                    }
                ]
            }
        }
        rows = lit.parse_europepmc(payload, "Cirsium introgression")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["doi"], "10.2222/reticulate")
        self.assertEqual(rows[0]["authors"], "A Researcher|B Botanist")
        self.assertEqual(rows[0]["source"], "europepmc")
        self.assertTrue(rows[0]["url"].endswith("/MED/12345678"))

    def test_dedupe_merges_sources_and_scores_topics(self) -> None:
        records = [
            {
                "source": "crossref",
                "query": "Cirsium phylogeny",
                "title": "Phylogenomics of Cirsium",
                "year": "2025",
                "doi": "10.1000/SAME",
                "journal": "Journal A",
                "authors": "A Author",
                "url": "https://doi.org/10.1000/SAME",
                "abstract": "Target capture resolves hybridization in Cirsium.",
                "publication_type": "journal-article",
            },
            {
                "source": "europepmc",
                "query": "Cirsium hybridization",
                "title": "Phylogenomics of Cirsium",
                "year": "2025",
                "doi": "https://doi.org/10.1000/same",
                "journal": "Journal A",
                "authors": "A Author|B Author",
                "url": "https://europepmc.org/article/MED/1",
                "abstract": "Target capture resolves hybridization and introgression in Cirsium.",
                "publication_type": "research-article",
            },
        ]
        rows = lit.dedupe(records)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["doi"], "10.1000/same")
        self.assertEqual(row["source"], "crossref|europepmc")
        self.assertEqual(
            row["query"],
            "Cirsium hybridization|Cirsium phylogeny",
        )
        self.assertIn("cirsium", row["topic_flags"])
        self.assertIn("phylogeny_systematics", row["topic_flags"])
        self.assertIn("reticulation", row["topic_flags"])
        self.assertIn("genome_scale", row["topic_flags"])
        self.assertEqual(row["screening_status"], "unreviewed")
        self.assertGreater(float(row["relevance_score"]), 8.0)


if __name__ == "__main__":
    unittest.main()
