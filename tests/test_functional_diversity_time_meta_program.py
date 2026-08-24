from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/evidence/functional_diversity_time_meta_registry_v1.csv"
PROGRAM = ROOT / "docs/FUNCTIONAL_DIVERSITY_TIME_META_ANALYSIS_PROGRAM_2026-08-24.md"
README = ROOT / "README.md"


def test_registry_has_complete_analysis_ladder():
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["analysis_id"] for r in rows] == [f"FDT{i}" for i in range(1, 9)]
    assert all(r["question"] and r["primary_data"] and r["claim_if_supported"] for r in rows)


def test_program_is_time_axis_not_azami_spatial_repeat():
    text = PROGRAM.read_text(encoding="utf-8")
    assert "Azami is the spatial discovery layer" in text
    assert "functional disparity through time" in text.lower()
    assert "temporal concordance between functional transition and niche shift" in text
    assert "do **not** pretend that present pollinator maps are literal 1-Ma historical distributions" in text


def test_competing_simulation_models_are_predeclared():
    text = PROGRAM.read_text(encoding="utf-8")
    for model in ("M0", "M1", "M2", "M3", "M4", "M5"):
        assert f"### {model}" in text
    assert "common-lability" in text
    assert "modular selection mosaic" in text
    assert "ecological-opportunity pulse" in text


def test_first_paper_precedes_causal_field_claims():
    text = README.read_text(encoding="utf-8")
    assert "Paper A — Azami global phenomics: **space**" in text
    assert "Paper B — EAzami functional diversification through **time**" in text
    assert "trend/hypothesis-generating paper before new causal field experiments" in text
    assert "Adaptive-radiation inference remains downstream of causal validation" in text
