#!/usr/bin/env python3
"""Offline tests for metadata-aware Compositae1061 target discovery."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "recover_compositae1061_target_expanded.py"
)
SPEC = importlib.util.spec_from_file_location(
    "recover_compositae1061_target_expanded", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["recover_compositae1061_target_expanded"] = mod
SPEC.loader.exec_module(mod)


class ExpandedTargetDiscoveryTests(unittest.TestCase):
    def test_pairs_filename_with_nested_download_url(self) -> None:
        payload = {
            "files": [
                {
                    "id": "uuid-1",
                    "filename": "Compositae1061_targets.fasta",
                    "size": 12345,
                    "content_details": {
                        "download_url": "https://example.org/file_downloaded"
                    },
                }
            ]
        }
        values = list(
            mod.walk_file_mappings(
                payload,
                source_key="mendeley_bhvv6rmyt6_api",
                repository="Mendeley_Data",
                dataset_id="bhvv6rmyt6",
                dataset_version="1",
                base_url="https://example.org/api",
            )
        )
        direct = [
            value
            for value in values
            if value.discovery_method == "json_field_pair"
        ]
        self.assertEqual(len(direct), 1)
        self.assertEqual(direct[0].filename, "Compositae1061_targets.fasta")
        self.assertEqual(
            direct[0].download_url, "https://example.org/file_downloaded"
        )
        self.assertEqual(direct[0].declared_size, "12345")

    def test_constructs_mendeley_public_file_url(self) -> None:
        payload = {
            "files": [
                {
                    "id": "abc-def",
                    "filename": "targets.fasta",
                    "file_size": 500,
                }
            ]
        }
        values = list(
            mod.walk_file_mappings(
                payload,
                source_key="mendeley",
                repository="Mendeley_Data",
                dataset_id="bhvv6rmyt6",
                dataset_version="1",
            )
        )
        constructed = [
            value
            for value in values
            if value.discovery_method == "constructed_from_public_file_id"
        ]
        self.assertEqual(len(constructed), 1)
        self.assertEqual(
            constructed[0].download_url,
            "https://data.mendeley.com/public-files/datasets/bhvv6rmyt6/"
            "files/abc-def/file_downloaded",
        )

    def test_constructs_dryad_download_url(self) -> None:
        payload = {
            "id": 1234,
            "filename": "target.fa",
            "filesize": 1000,
        }
        values = list(
            mod.walk_file_mappings(
                payload,
                source_key="dryad_files",
                repository="Dryad",
                dataset_id=mod.DRYAD_DOI,
            )
        )
        self.assertTrue(
            any(
                value.download_url
                == "https://datadryad.org/api/v2/files/1234/download"
                for value in values
            )
        )

    def test_extracts_next_data_json(self) -> None:
        html = """
        <html><head></head><body>
        <script id="__NEXT_DATA__" type="application/json">
        {"props":{"files":[{"id":"x1","filename":"panel.fasta"}]}}
        </script>
        </body></html>
        """
        parsed = mod.extract_script_json(html)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(
            parsed[0]["props"]["files"][0]["filename"], "panel.fasta"
        )

    def test_candidates_from_response_preserves_dataset_context(self) -> None:
        payload = json.dumps(
            {
                "files": [
                    {
                        "id": "x1",
                        "filename": "Compositae1061_targets.fasta",
                    }
                ]
            }
        ).encode()
        response = mod.base.Response(
            "mendeley_test",
            "https://example.org/api",
            "ok",
            payload=payload,
            content_type="application/json",
            final_url="https://example.org/api",
        )
        candidates = mod.candidates_from_response(
            response,
            repository="Mendeley_Data",
            dataset_id="bhvv6rmyt6",
            dataset_version="1",
        )
        self.assertEqual(candidates[0].dataset_id, "bhvv6rmyt6")
        self.assertEqual(candidates[0].dataset_version, "1")
        self.assertGreaterEqual(mod.candidate_score(candidates[0]), 1)

    def test_deduplicates_repeated_candidate(self) -> None:
        candidate = mod.Candidate(
            source_key="source",
            repository="Mendeley_Data",
            dataset_id="dataset",
            dataset_version="1",
            filename="target.fasta",
            download_url="https://example.org/target.fasta",
        )
        self.assertEqual(mod.dedupe_candidates([candidate, candidate]), [candidate])

    def test_candidate_key_is_stable(self) -> None:
        candidate = mod.Candidate(
            source_key="source",
            repository="Dryad",
            dataset_id="doi",
            dataset_version="1",
            filename="target.fasta",
            download_url="https://example.org/target.fasta",
            file_id="123",
        )
        self.assertEqual(candidate.candidate_key, candidate.candidate_key)
        self.assertTrue(candidate.candidate_key.startswith("candidate_"))


if __name__ == "__main__":
    unittest.main()
