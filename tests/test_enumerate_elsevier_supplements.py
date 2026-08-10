#!/usr/bin/env python3
"""Offline tests for Elsevier supplementary enumeration."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "enumerate_elsevier_supplements.py"
SPEC = importlib.util.spec_from_file_location("enumerate_elsevier_supplements", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["enumerate_elsevier_supplements"] = mod
SPEC.loader.exec_module(mod)


class ElsevierEnumerationTests(unittest.TestCase):
    def test_candidate_url(self) -> None:
        self.assertEqual(
            mod.candidate_url("S1055790325000028", 2, "zip"),
            "https://ars.els-cdn.com/content/image/1-s2.0-S1055790325000028-mmc2.zip",
        )

    def test_magic_classes(self) -> None:
        self.assertEqual(mod.magic_class(b"PK\x03\x04abc"), "zip_container")
        self.assertEqual(mod.magic_class(b"%PDF-1.7"), "pdf")
        self.assertEqual(mod.magic_class(b"#NEXUS\nBEGIN TREES;"), "nexus_text")
        self.assertEqual(mod.magic_class(b" (A,B);"), "possible_newick_text")
        self.assertEqual(mod.magic_class(b"<html>challenge</html>"), "html")

    def test_enumeration_keeps_only_responses(self) -> None:
        original = mod.inspect_candidate
        try:
            def fake(url: str):
                if "mmc1.docx" in url:
                    return {
                        "status": 200,
                        "content_type": "application/docx",
                        "content_length": "123",
                        "final_url": url,
                        "magic_hex": "504b0304",
                        "magic_class": "zip_container",
                        "validation": "candidate_exists",
                        "error": "",
                    }
                return None
            mod.inspect_candidate = fake
            rows = mod.enumerate_candidates("S1055790325000028", 2, ("docx", "zip"))
        finally:
            mod.inspect_candidate = original
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["index"], 1)
        self.assertEqual(rows[0]["extension"], "docx")


if __name__ == "__main__":
    unittest.main()
