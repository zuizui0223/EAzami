#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "docs" / "chapter2" / "README.md"
TOKENS = (
    "chapter2_differentiation_time_axis_contract_v1.json",
    "MANUSCRIPT_JEB_V6_REFRAME_OUTLINE.md",
    "HISTORICAL_DIFFERENTIATION_TRIGGER_RESULT_V1.md",
)
text = P.read_text(encoding="utf-8")
if all(t in text for t in TOKENS):
    print("legacy V6 audit route already present")
    raise SystemExit(0)
block = """

### Superseded V6 space-time audit route

The following files remain a **historical audit route only**; they are not the active V7 scientific spine:

- `chapter2_differentiation_time_axis_contract_v1.json`;
- `MANUSCRIPT_JEB_V6_REFRAME_OUTLINE.md`;
- `HISTORICAL_DIFFERENTIATION_TRIGGER_RESULT_V1.md`.
"""
P.write_text(text.rstrip() + block + "\n", encoding="utf-8")
print("added superseded V6 audit route references")
