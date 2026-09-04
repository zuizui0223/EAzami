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
    assert "tree_execution_gate" in sticky["decision"]

    phyllary = multi["phyllary_posture"]
    assert phyllary["resolved"] == 10
    assert phyllary["raw_state_classes"] >= 5


def test_phyllary_harmonization_is_predeclared_and_remains_exploratory():
    summary = mod.build_summary()
    ph = summary["phyllary_harmonization"]
    assert ph["coarse_state_counts"] == {
        "closed_to_ascending": 7,
        "spreading_to_recurved": 2,
        "unresolved_cross_boundary": 1,
    }
    assert ph["binary_compatible_resolved"] == 9
    assert ph["minor_state_count"] == 2
    assert ph["decision"] == "exploratory_only_not_primary_history_ready"


def test_japan_wide_machine_tree_is_a_real_gate_not_inferred_from_sample_count():
    summary = mod.build_summary()
    gate = summary["japan_wide_tree_gate"]
    assert gate["accepted_294_sample_composition"] is True
    assert gate["execution_bundle_present"] is True
    assert gate["machine_readable_japan_wide_tree_present"] is False
    assert gate["heavy_tree_execution_remaining_in_current_state"] is True
    assert "do_not_infer_Japan38_transition_counts" in gate["decision"]


def test_existing_event_windows_are_frozen_without_promoting_point_estimates():
    summary = mod.build_summary()
    ev = summary["ecological_event_windows"]
    assert ev["event_rows"] == 7
    assert ev["eligible_biogeographic_opportunity_windows"] == 3
    assert ev["eligible_event_ids"] == ["EV01", "EV02", "EV03"]
    assert ev["lineage_split_anchors"] == 4
    assert "dated_trait_tree" in ev["decision"]


def test_time_program_does_not_overclaim_current_readiness():
    summary = mod.build_summary()
    statuses = {r["analysis_id"]: r["status"] for r in summary["fdt_layer_readiness"]}
    assert statuses["FDT1"] == "seed_registry_ready_effect_harmonization_next"
    assert statuses["FDT2"] == "not_yet_executable_as_cross_module_meta_regression"
    assert statuses["FDT3"] == "partial_ready_tree_gated"
    assert statuses["FDT4"] == "partial_ready"
    assert statuses["FDT5"] == "blocked"
    assert statuses["FDT6"] == "event_windows_frozen_dated_transition_tree_missing"
    assert statuses["FDT7"] == "design_ready_not_parameterized"


def test_known_reusable_assets_are_present_and_missing_gates_remain_missing():
    summary = mod.build_summary()
    assets = summary["known_assets"]
    assert "antagonist_meta" in assets
    assert "multiagent_registry" in assets
    assert "pollinator_gradient_registry" in assets
    assert "fdt1_existing_seed_registry" in assets
    assert "phyllary_harmonization_contract" in assets
    assert "event_window_registry" in assets
    assert "focal_niche_builder" in assets
    assert "focal_branch_length_tree" in assets
    assert "orientation_posttree" in assets
    assert "japan294_execution_bundle" in assets

    missing = summary["program_assets_not_yet_present"]
    assert "cross_module_trait_function_matrix" in missing
    assert "georeferenced_cross_module_effect_ledger" in missing
    assert "japan_wide_machine_readable_tree" in missing
    assert "exact_tip_dated_tree" in missing
    assert "simulation_engine" in missing
    assert "event_window_registry" not in missing


def test_existing_effect_seed_registry_is_complete_before_new_search():
    summary = mod.build_summary()
    seed = summary["fdt1_existing_seed"]
    assert seed["registered_existing_evidence_families"] == 7
    assert seed["all_paths_present"] is True
    assert seed["decision"] == "reuse_existing_ledgers_first_before_new_systematic_search"


def test_stickiness_remains_negative_control_not_adaptation():
    summary = mod.build_summary()
    sticky = summary["japan38_multitrait"]["stickiness"]
    assert "weakened" in sticky["claim_boundary"]
    assert "adaptive" in sticky["claim_boundary"]
