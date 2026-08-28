from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/evidence/functional_diversity_time_meta_registry_v1.csv"
PROGRAM = ROOT / "docs/FUNCTIONAL_DIVERSITY_TIME_META_ANALYSIS_PROGRAM_2026-08-24.md"
README = ROOT / "README.md"
MAINLINE = ROOT / "docs/chapter2/MAINLINE_V2.md"


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


def test_time_axis_programme_is_supporting_not_repository_mainline():
    readme = README.read_text(encoding="utf-8")
    mainline = MAINLINE.read_text(encoding="utf-8")
    assert "Chapter 1: present-day space/environment" in readme
    assert "Chapter 2: evolutionary time/history" in readme
    assert "Chapter 3: function/fitness" in readme
    assert "Present-state v3/v4 covariance generators" in readme
    assert "modular evolvability" in mainline
    assert "endpoint hypothesis" in mainline
    assert "adaptive convergence" in mainline
    # The older FDT programme remains available as a supporting time-axis
    # analysis, but it no longer defines the repository entry point.
    start_here = readme.split("Start here:", 1)[-1].split("## Evidence boundaries", 1)[0]
    assert "docs/FUNCTIONAL_DIVERSITY_TIME_META_ANALYSIS_PROGRAM_2026-08-24.md" not in start_here
