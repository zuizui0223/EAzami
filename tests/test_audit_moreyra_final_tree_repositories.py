#!/usr/bin/env python3
"""Offline tests for the Moreyra final-tree repository audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "audit_moreyra_final_tree_repositories.py"
SPEC = importlib.util.spec_from_file_location("audit_moreyra_final_tree_repositories", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["audit_moreyra_final_tree_repositories"] = mod
SPEC.loader.exec_module(mod)


class FinalTreeRepositoryAuditTests(unittest.TestCase):
    def test_article_matching_by_doi_or_title(self) -> None:
        self.assertTrue(mod.matches_article("unrelated", [mod.ARTICLE_DOI]))
        self.assertTrue(mod.matches_article(mod.TITLE.upper(), []))
        self.assertTrue(mod.matches_article("A thorny tale — diversification of Cirsium", []))
        self.assertFalse(mod.matches_article("A thorny tale of hedgehog parasites", []))

    def test_file_classifier(self) -> None:
        self.assertEqual(mod.classify_file("final_astral.treefile"), {"tree"})
        self.assertEqual(mod.classify_file("350_alignments.zip"), {"alignment", "archive"})
        self.assertEqual(mod.classify_file("species_tree.nex"), {"tree", "alignment"})
        self.assertEqual(mod.classify_file("README.md"), set())

    def test_crossref_relation_parsing(self) -> None:
        payload = {
            "message": {
                "DOI": mod.ARTICLE_DOI.upper(),
                "title": [mod.TITLE],
                "relation": {
                    "is-preprint-of": [{"id": mod.PREPRINT_DOI}],
                    "is-supplemented-by": [{"id": "10.9999/dataset"}],
                },
            }
        }
        parsed = mod.parse_crossref(payload)
        self.assertEqual(parsed.record_count, 1)
        self.assertEqual(len(parsed.matches), 1)
        identifiers = parsed.matches[0]["identifiers"]
        self.assertIn(mod.ARTICLE_DOI.upper(), identifiers)
        self.assertIn("is-preprint-of:" + mod.PREPRINT_DOI, identifiers)
        self.assertIn("is-supplemented-by:10.9999/dataset", identifiers)

    def test_datacite_keeps_only_matching_records(self) -> None:
        payload = {
            "data": [
                {
                    "id": "10.1234/data",
                    "attributes": {
                        "doi": "10.1234/data",
                        "titles": [{"title": "Dataset for another paper"}],
                        "relatedIdentifiers": [
                            {"relatedIdentifier": mod.ARTICLE_DOI}
                        ],
                    },
                },
                {
                    "id": "10.9999/other",
                    "attributes": {
                        "doi": "10.9999/other",
                        "titles": [{"title": "Unrelated"}],
                    },
                },
            ]
        }
        parsed = mod.parse_datacite(payload)
        self.assertEqual(parsed.record_count, 2)
        self.assertEqual(len(parsed.matches), 1)
        self.assertEqual(parsed.matches[0]["title"], "Dataset for another paper")

    def test_zenodo_file_detection_is_limited_to_matching_record(self) -> None:
        payload = {
            "hits": {
                "total": 2,
                "hits": [
                    {
                        "doi": "10.1234/zenodo-data",
                        "metadata": {
                            "title": mod.TITLE,
                            "related_identifiers": [
                                {"identifier": mod.ARTICLE_DOI}
                            ],
                        },
                        "files": [
                            {"key": "final_astral.treefile"},
                            {"key": "alignments.tar.gz"},
                        ],
                    },
                    {
                        "doi": "10.1234/unrelated",
                        "metadata": {"title": "Unrelated"},
                        "files": [{"key": "unrelated.nwk"}],
                    },
                ],
            }
        }
        parsed = mod.parse_zenodo(payload)
        self.assertEqual(parsed.record_count, 2)
        self.assertEqual(len(parsed.matches), 1)
        self.assertEqual(parsed.files, ["final_astral.treefile", "alignments.tar.gz"])

    def test_dryad_matching(self) -> None:
        payload = {
            "count": 2,
            "_embedded": {
                "stash:datasets": [
                    {"title": mod.TITLE, "identifier": "doi:10.5061/dryad.test"},
                    {"title": "Another dataset", "identifier": "doi:10.5061/other"},
                ]
            },
        }
        parsed = mod.parse_dryad(payload)
        self.assertEqual(parsed.record_count, 2)
        self.assertEqual(len(parsed.matches), 1)

    def test_figshare_matching(self) -> None:
        payload = [
            {
                "title": mod.TITLE,
                "doi": "10.6084/m9.figshare.1",
                "resource_doi": mod.ARTICLE_DOI,
            },
            {"title": "Other", "doi": "10.6084/other"},
        ]
        parsed = mod.parse_figshare(payload)
        self.assertEqual(parsed.record_count, 2)
        self.assertEqual(len(parsed.matches), 1)

    def test_github_public_history_summary(self) -> None:
        parsed = mod.parse_github_repository(
            [{"name": "main"}],
            [],
            [],
            [{"sha": "abc"}],
            {
                "tree": [
                    {"path": "hybpiper_stats_exonerate.tsv"},
                    {"path": "seq_lengths_exonerate.tsv"},
                    {"path": "paralog_report.xlsx"},
                ]
            },
        )
        self.assertEqual(parsed.record_count, 3)
        self.assertEqual(len(parsed.matches), 1)
        self.assertIn("branches=1", parsed.matches[0]["identifiers"])
        self.assertEqual(len(parsed.files), 3)

    def test_result_row_counts_candidates(self) -> None:
        row = mod.result_row(
            service="Zenodo",
            query_label="test",
            method="GET",
            url="https://example.invalid",
            checked_at="2026-08-10T00:00:00Z",
            status="queried",
            http_status=200,
            parsed=mod.ParsedResult(
                1,
                [{"title": mod.TITLE, "identifiers": [mod.ARTICLE_DOI]}],
                ["final.treefile", "matrix.fasta", "bundle.zip"],
            ),
        )
        self.assertEqual(row["matching_record_count"], 1)
        self.assertEqual(row["tree_like_file_count"], 1)
        self.assertEqual(row["alignment_like_file_count"], 1)
        self.assertEqual(row["archive_file_count"], 1)

    def test_summary_does_not_promote_search_hit_to_recovered_tree(self) -> None:
        rows = [
            mod.result_row(
                service="DataCite",
                query_label="test",
                method="GET",
                url="https://example.invalid",
                checked_at="2026-08-10T00:00:00Z",
                status="queried",
                http_status=200,
                parsed=mod.ParsedResult(
                    1,
                    [{"title": mod.TITLE, "identifiers": [mod.ARTICLE_DOI]}],
                    [],
                ),
            )
        ]
        summary = mod.summary(rows)
        self.assertEqual(summary["services_with_matching_record"], ["DataCite"])
        self.assertEqual(summary["services_with_tree_like_file_candidate"], [])
        self.assertFalse(summary["machine_readable_final_tree_recovered"])


if __name__ == "__main__":
    unittest.main()
