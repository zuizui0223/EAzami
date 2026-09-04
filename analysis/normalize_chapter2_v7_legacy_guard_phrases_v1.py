#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs" / "chapter2" / "MANUSCRIPT_JEB_V7_WORKING.md"

text = PATH.read_text(encoding="utf-8")
old = "This is an origin-versus-current-regime decoupling result, not evidence that environment was irrelevant at origin."
new = "This is an origin-versus-current-regime decoupling result and does not imply environmental irrelevance at origin."
if text.count(old) != 1:
    raise AssertionError(f"expected exactly one legacy-guard phrase, found {text.count(old)}")
PATH.write_text(text.replace(old, new, 1), encoding="utf-8")
print("normalized legacy guard wording")
