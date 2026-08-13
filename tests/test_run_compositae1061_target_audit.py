#!/usr/bin/env python3
"""Tests for the URL-safe first-pass Compositae1061 audit runner."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
MODULE_PATH = ANALYSIS_DIR / "run_compositae1061_target_audit.py"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
SPEC = importlib.util.spec_from_file_location(
    "run_compositae1061_target_audit", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["run_compositae1061_target_audit"] = mod
SPEC.loader.exec_module(mod)


class UrlSafeBaseAuditTests(unittest.TestCase):
    def test_encodes_metadata_title_joined_as_path(self) -> None:
        raw = (
            "https://data.mendeley.com/api/datasets/x/versions/"
            "Paleomagnetic study supporting information."
        )
        self.assertEqual(
            mod.safe_url(raw),
            "https://data.mendeley.com/api/datasets/x/versions/"
            "Paleomagnetic%20study%20supporting%20information.",
        )

    def test_safe_download_delegates_with_encoded_url(self) -> None:
        calls: list[tuple[str, str]] = []
        original = mod.audit.download

        def fake(key: str, url: str, *args, **kwargs):
            calls.append((key, url))
            return "ok"

        try:
            mod.audit.download = fake
            mod.install_safe_download()
            result = mod.audit.download(
                "candidate",
                "https://example.org/Supporting information.pdf",
            )
        finally:
            mod.audit.download = original

        self.assertEqual(result, "ok")
        self.assertEqual(
            calls,
            [("candidate", "https://example.org/Supporting%20information.pdf")],
        )


if __name__ == "__main__":
    unittest.main()
