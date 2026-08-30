#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "evidence" / "chapter2_space_time_concordance_v1.csv"
DOC = ROOT / "docs" / "chapter2" / "SPACE_TIME_CONCORDANCE_AUDIT_V1.md"


def main() -> int:
    rows = list(csv.DictReader(LEDGER.open(encoding="utf-8")))
    by_id = {r["trait_id"]: r for r in rows}
    assert len(rows) == 6
    assert by_id["orientation"]["concordance_class"] == "bridge_supported"
    assert by_id["colour_continuous"]["concordance_class"] == "spatial_sorting_temporal_lability_unresolved"
    assert by_id["phyllary_posture"]["concordance_class"] == "time_only_ontology_boundary"
    assert by_id["stickiness"]["concordance_class"] == "time_only_missing_space_axis"

    text = DOC.read_text(encoding="utf-8")
    required = [
        "BD1 — Spatial environmental sorting predicts temporal recurrence/lability",
        "BD2 — The same ecological domain recurs across space and time",
        "BD3 — Whole-capitulum breadth reflects synchronized temporal assembly",
        "cross-scale hydric correspondence",
        "zero of three trait pairs passes the cross-treatment rule",
        "trait-specific",
    ]
    for token in required:
        assert token in text, token

    # Claim ceilings: these terms may occur only as explicit negations/boundaries.
    assert "BIO12 and BIO15 are not the same variable" in text
    assert "This does not establish rain adaptation" in text
    assert "does not prove genetic modularity" in text
    assert "no defensible cross-trait significance test" in text
    print("chapter2 space-time concordance v1: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
