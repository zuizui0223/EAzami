#!/usr/bin/env python3
"""Offline tests for ResearchGate preprint Figure 1 recovery."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
MODULE_PATH = ANALYSIS_DIR / "recover_chang2026_takaoense_preprint.py"
SPEC = importlib.util.spec_from_file_location(
    "recover_chang2026_takaoense_preprint", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["recover_chang2026_takaoense_preprint"] = mod
SPEC.loader.exec_module(mod)


class FakePage:
    def __init__(self, text: str) -> None:
        self.text = text

    def get_text(self, kind: str = "text") -> str:
        del kind
        return self.text


class FakeDocument:
    def __init__(self, pages: list[str]) -> None:
        self.pages = [FakePage(text) for text in pages]
        self.page_count = len(self.pages)

    def load_page(self, index: int) -> FakePage:
        return self.pages[index]


class ChangPreprintRecoveryTests(unittest.TestCase):
    def test_direct_pdf_url_is_researchgate_preprint(self) -> None:
        self.assertIn("researchgate.net", mod.PDF_URL)
        self.assertIn("400638061", mod.PDF_URL)
        self.assertTrue(mod.PDF_URL.endswith("thistles.pdf"))

    def test_is_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.pdf"
            path.write_bytes(b"%PDF" + b"x" * 2000)
            self.assertTrue(mod.is_pdf(path))
            path.write_bytes(b"<html>" + b"x" * 2000)
            self.assertFalse(mod.is_pdf(path))

    def test_caption_page_detection_includes_neighbours(self) -> None:
        doc = FakeDocument(
            [
                "ordinary page",
                "figure image page",
                (
                    "Figure 1 Phylotranscriptomic reconstruction and species "
                    "delimitation of Cirsium subsections"
                ),
                "caption continuation",
                "ordinary page",
            ]
        )
        self.assertEqual(mod.caption_page_indices(doc), [1, 2, 3])

    def test_caption_fallback_uses_morph_definition(self) -> None:
        doc = FakeDocument(
            [
                "ordinary page",
                (
                    "Phylotranscriptomic reconstruction and species delimitation. "
                    "(W) denotes the white-corolla morph and (BP) denotes the "
                    "bluish-purple-corolla morph."
                ),
                "ordinary page",
            ]
        )
        self.assertEqual(mod.caption_page_indices(doc), [0, 1, 2])

    def test_missing_caption_fails(self) -> None:
        with self.assertRaises(ValueError):
            mod.caption_page_indices(FakeDocument(["ordinary", "ordinary"]))


if __name__ == "__main__":
    unittest.main()
