from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/audit_functional_time_existing_materials_v1.py"

spec = importlib.util.spec_from_file_location("audit_existing", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_japan38_multitrait_counts_are_recomputed_from_existing_files():
    summary = mod.build_summary()
    multi = summary["japan38_multitrait"]
    assert multi["japan38_taxon_concepts"] == 38
    assert multi["nmns_exact_trait_rows"] == 22
    assert multi["authority_exact_rows"] == 22

    ori = multi["orientation"]
    assert ori["primary_resolved"] == 19
    assert ori["state_counts"] == {
        "downward_or_nodding": 6,
        "upward_or_erect": 13,
    }
    assert ori["unknown"] == 2
    assert ori["source_conflict_or_nonbinary"] == 1

    sticky = multi["stickiness"]
    assert sticky["resolved"] == 12
    assert sticky["state_counts"] == {
        "nonsticky_or_nearly_nonsticky": 6,
        "sticky": 6,
    }
    assert sticky["minor_to_major_state_balance"] == 1.0

    phyllary = multi["phyllary_posture"]
    assert phyllary["resolved"] == 10
    assert phyllary["raw_state_classes"] >= 5


def test_time_program_does_not_overclaim_current_readiness():
    summary = mod.build_summary()
    statuses = {r["analysis_id"]: r["status"] for r in summary["fdt_layer_readiness"]}
    assert statuses["FDT1"] == "partial_ready"
    assert statuses["FDT2"] == "not_yet_executable_as_cross_module_meta_regression"
    assert statuses["FDT3"] == "partial_ready"
    assert statuses["FDT4"] == "partial_ready"
    assert statuses["FDT5"] == "blocked"
    assert statuses["FDT7"] == "design_ready_not_parameterized"


def test_known_reusable_assets_are_present_and_missing_gates_remain_missing():
    summary = mod.build_summary()
    assets = summary["known_assets"]
    assert "antagonist_meta" in assets
    assert "focal_niche_builder" in assets
    assert "focal_branch_length_tree" in assets
    assert "orientation_posttree" in assets

    missing = summary["program_assets_not_yet_present"]
    assert "cross_module_trait_function_matrix" in missing
    assert "georeferenced_cross_module_effect_ledger" in missing
    assert "exact_tip_dated_tree" in missing
    assert "event_window_registry" in missing
    assert "simulation_engine" in missing


def test_stickiness_is_promoted_only_as_history_preflight_not_adaptation():
    summary = mod.build_summary()
    sticky = summary["japan38_multitrait"]["stickiness"]
    assert "repeated-state preflight" in sticky["decision"]
    assert "weakened" in sticky["claim_boundary"]
    assert "adapt" in sticky["claim_boundary"]
