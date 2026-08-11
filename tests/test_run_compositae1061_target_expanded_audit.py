#!/usr/bin/env python3
"""Tests for the URL-safe expanded Compositae1061 audit runner."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
MODULE_PATH = ANALYSIS_DIR / "run_compositae1061_target_expanded_audit.py"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
SPEC = importlib.util.spec_from_file_location(
    "run_compositae1061_target_expanded_audit", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["run_compositae1061_target_expanded_audit"] = mod
SPEC.loader.exec_module(mod)


class UrlSafeExpandedAuditTests(unittest.TestCase):
    def test_encodes_literal_spaces_in_path_and_query(self) -> None:
        raw = (
            "https://api.github.com/repositories/1/contents/data/raw/"
            "Navigating phylogene.html?ref=abc def"
        )
        self.assertEqual(
            mod.safe_url(raw),
            "https://api.github.com/repositories/1/contents/data/raw/"
            "Navigating%20phylogene.html?ref=abc%20def",
        )

    def test_preserves_existing_percent_escapes(self) -> None:
        raw = "https://example.org/a%20b/target.fasta?ref=x%2Fy"
        self.assertEqual(mod.safe_url(raw), raw)

    def test_safe_download_delegates_with_encoded_url(self) -> None:
        calls: list[tuple[str, str]] = []
        original = mod.expanded.base.download

        def fake(key: str, url: str, *args, **kwargs):
            calls.append((key, url))
            return "ok"

        try:
            mod.expanded.base.download = fake
            mod.install_safe_download()
            result = mod.expanded.base.download(
                "candidate",
                "https://example.org/Navigating phylogene.html",
            )
        finally:
            mod.expanded.base.download = original

        self.assertEqual(result, "ok")
        self.assertEqual(
            calls,
            [("candidate", "https://example.org/Navigating%20phylogene.html")],
        )


if __name__ == "__main__":
    unittest.main()
