from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/evidence/functional_diversity_time_meta_registry_v1.csv"
PROGRAM = ROOT / "docs/FUNCTIONAL_DIVERSITY_TIME_META_ANALYSIS_PROGRAM_2026-08-24.md"
README = ROOT / "README.md"
FDT7_BRIDGE = ROOT / "data/evidence/fdt7_legacy_simulation_bridge_v1.json"
LOADING_CONTRACT = ROOT / "data/evidence/fdt1_trait_function_loading_contract_v1.csv"


def test_registry_has_complete_analysis_ladder():
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["analysis_id"] for r in rows] == [f"FDT{i}" for i in range(1, 9)]
    assert all(r["question"] and r["primary_data"] and r["claim_if_supported"] for r in rows)
    by = {r["analysis_id"]: r for r in rows}
    assert "not all-topology robust" in by["FDT4"]["main_blocker"]
    assert "dated tree/posterior absent" in by["FDT5"]["main_blocker"]
    assert "M0-M5 semantics are frozen" in by["FDT7"]["main_blocker"]
    assert "fdt1_trait_function_loading_contract_v1" in by["FDT1"]["cirsium_link"]
    assert "no current external loading" in by["FDT1"]["main_blocker"]
    assert "READINESS_REGISTRY_ONLY" in by["FDT2"]["main_blocker"]
    assert "23 study clusters" in by["FDT2"]["main_blocker"]
    assert "NOT_READY_ZERO_PRIMARY_EVENT_LEDGER_ROWS" in by["FDT3"]["main_blocker"]


def test_program_is_time_axis_not_azami_spatial_repeat():
    text = PROGRAM.read_text(encoding="utf-8")
    assert "Azami series Chapter 2" in text
    assert "Azami is the spatial discovery layer" in text
    assert "functional disparity through time" in text.lower()
    assert "temporal concordance between functional transition and niche shift" in text
    assert "do **not** pretend that present pollinator maps are literal 1-Ma historical distributions" in text
    assert "substitutions/site trees cannot be" in text
    assert "15" in text and "module-function rows" in text
    assert "STOP_BEFORE_MODERATOR_MODEL" in text
    assert "23 primary-source study clusters" in text
    assert "NOT_READY_ZERO_PRIMARY_EVENT_LEDGER_ROWS" in text
    assert LOADING_CONTRACT.exists()


def test_competing_simulation_models_are_predeclared():
    text = PROGRAM.read_text(encoding="utf-8")
    for model in ("M0", "M1", "M2", "M3", "M4", "M5"):
        assert f"### {model}" in text
    assert "common-lability" in text
    assert "modular selection mosaic" in text
    assert "ecological-opportunity pulse" in text


def test_fdt7_bridge_freezes_semantics_without_false_legacy_equivalence():
    bridge = json.loads(FDT7_BRIDGE.read_text(encoding="utf-8"))
    aliases = bridge["model_aliases"]
    assert [aliases[f"M{i}"] for i in range(6)] == [
        "neutral_or_unconstrained",
        "single_abiotic_driver",
        "single_biotic_driver",
        "common_lability",
        "modular_selection_mosaic",
        "ecological_opportunity_pulse",
    ]
    assert "not a one-to-one mapping" in aliases["alias_scope"]
    assert "closed until a machine-readable dated tree" in bridge["chapter_2_execution_gate"]["FDT5_FDT7_absolute_time"]
    assert "do not relabel substitutions-per-site" in bridge["chapter_2_execution_gate"]["forbidden_shortcut"]


def test_chapter_2_precedes_causal_field_claims():
    text = README.read_text(encoding="utf-8")
    assert "Chapter 1 — Azami global phenomics: **space**" in text
    assert "Chapter 2 — EAzami functional diversification through **time**" in text
    assert "trend/hypothesis-generating chapter/manuscript before new causal field experiments" in text
    assert "Adaptive-radiation inference remains downstream of causal validation" in text
