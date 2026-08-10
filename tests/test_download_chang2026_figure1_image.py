#!/usr/bin/env python3
"""Offline tests for the direct Chang 2026 Figure 1 image downloader."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "download_chang2026_figure1_image.py"
)
SPEC = importlib.util.spec_from_file_location(
    "download_chang2026_figure1_image", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["download_chang2026_figure1_image"] = mod
SPEC.loader.exec_module(mod)


class ChangFigureImageTests(unittest.TestCase):
    def test_png_magic(self) -> None:
        self.assertEqual(mod.image_kind(b"\x89PNG\r\n\x1a\nrest"), "png")

    def test_jpeg_magic(self) -> None:
        self.assertEqual(mod.image_kind(b"\xff\xd8\xff\xe0rest"), "jpeg")

    def test_webp_magic(self) -> None:
        self.assertEqual(mod.image_kind(b"RIFF1234WEBPrest"), "webp")

    def test_unknown_magic(self) -> None:
        self.assertEqual(mod.image_kind(b"<!doctype html>"), "unknown")

    def test_official_urls_are_figure_one(self) -> None:
        self.assertTrue(mod.DEFAULT_URLS)
        for url in mod.DEFAULT_URLS:
            self.assertIn("12870_2026_8097_Fig1_HTML.png", url)
            self.assertIn("media.springernature.com", url)


if __name__ == "__main__":
    unittest.main()
