#!/usr/bin/env python3
"""Validate the active Chapter 2 historical-differentiation evidence ceiling."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv"
SYNTHESIS = ROOT / "docs/chapter2/HISTORICAL_DIFFERENTIATION_EVIDENCE_SYNTHESIS_V1.md"
FINAL = ROOT / "data/evidence/chapter2_historical_differentiation_final_summary_v1.json"
CLIMATE = ROOT / "data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json"
SEA = ROOT / "data/evidence/chapter2_orientation_deboer_sealevel_envelope_v1_summary.json"
LINEAGE_CLIMATE = ROOT / "data/evidence/chapter2_lineage_differentiation_environment_atlas_v1_summary.json"
LINEAGE_SEA = ROOT / "data/evidence/chapter2_lineage_differentiation_sealevel_v1.json"
MPT = ROOT / "data/evidence/chapter2_orientation_mpt_overlap_audit_v1.json"
TREE_AUDIT = ROOT / "data/evidence/chapter2_public_dated_tree_recovery_audit_v2.json"

REQUIRED_MODULES = {
    "orientation",
    "phyllary_posture",
    "stickiness",
    "flower_colour",
    "coarse_capitulum_remodelling",
    "whole_capitulum",
}

REQUIRED_COLUMNS = {
    "trait_module",
    "history_resolution",
    "recurrence_lower_bound",
    "relative_depth_summary",
    "calendar_event_status",
    "dated_event_or_context",
    "paleolocation_status",
    "historical_climate_direction",
    "historical_climate_level",
    "historical_absolute_change",
    "historical_variability",
    "sea_level_range_context",
    "repeated_trigger_status",
    "current_allowed_inference",
    "next_required_evidence",
    "claim_ceiling",
}

FINAL_CLASS = (
    "repeated_differentiation_resolved_but_recurring_tested_"
    "environmental_trigger_not_identified_under_public_data"
)


def main() -> None:
    required_files = (
        LEDGER,
        SYNTHESIS,
        FINAL,
        CLIMATE,
        SEA,
        LINEAGE_CLIMATE,
        LINEAGE_SEA,
        MPT,
        TREE_AUDIT,
    )
    for p in required_files:
        if not p.exists():
            raise AssertionError(f"missing active differentiation evidence: {p.relative_to(ROOT)}")

    with LEDGER.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise AssertionError("ledger has no header")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise AssertionError(f"ledger missing columns: {sorted(missing)}")
        rows = list(reader)

    by = {r["trait_module"]: r for r in rows}
    if set(by) != REQUIRED_MODULES:
        raise AssertionError(f"unexpected module inventory: {sorted(by)}")

    orientation = by["orientation"]
    required_orientation = (
        "ML=6; UFBoot=4-6",
        "0.795-0.994",
        "direction_unresolved",
        "no variable passes robust level gate",
        "no variable passes robust absolute-change gate",
        "no variable passes robust variability gate",
        "de Boer model-based global series covers 94/94",
        "not_evaluable_single_dated_transition_event",
    )
    blob = " ".join(orientation.values())
    for phrase in required_orientation:
        if phrase not in blob:
            raise AssertionError(f"orientation ledger lost required boundary/result: {phrase}")

    if "exactly 3" not in by["phyllary_posture"]["recurrence_lower_bound"]:
        raise AssertionError("phyllary recurrence changed")
    if "not_evaluable" not in by["phyllary_posture"]["repeated_trigger_status"]:
        raise AssertionError("phyllary historical trigger must remain not_evaluable")

    if "exactly 5" not in by["stickiness"]["recurrence_lower_bound"]:
        raise AssertionError("stickiness recurrence changed")
    if "trait_age_unlinked" not in by["stickiness"]["repeated_trigger_status"]:
        raise AssertionError("stickiness range age must not become trait age")

    colour = by["flower_colour"]
    if "conditional" not in colour["calendar_event_status"]:
        raise AssertionError("colour dated branches must remain conditional")
    if "missing_historical_radiation" not in colour["repeated_trigger_status"]:
        raise AssertionError("colour historical radiation gap was lost")

    whole = by["whole_capitulum"]
    if "0/3" not in whole["dated_event_or_context"]:
        raise AssertionError("whole-capitulum shared localization boundary was lost")
    if whole["repeated_trigger_status"] != "universal_common_trigger_not_supported":
        raise AssertionError("whole-capitulum universal trigger boundary changed")

    final = json.loads(FINAL.read_text(encoding="utf-8"))
    if final["final_classification"] != FINAL_CLASS:
        raise AssertionError("final public-data differentiation classification changed")
    if final["calendar_identifiability"]["trait_transitions_with_calendar_paleolocation_environment_gate"] != 1:
        raise AssertionError("trait-transition calendar identifiability count changed")
    if final["lineage_level_climate_context"]["recurring_context_candidates"]:
        raise AssertionError("final summary must not manufacture recurring climate candidates")
    if final["global_sea_level_context"]["recurring_context_candidates"]:
        raise AssertionError("final summary must not manufacture recurring global sea-level candidates")

    lineage_climate = json.loads(LINEAGE_CLIMATE.read_text(encoding="utf-8"))
    lc_result = lineage_climate["formal_result"]
    if lineage_climate["inputs"]["n_bioclim_variables"] != 17:
        raise AssertionError("lineage climate variable family changed")
    if lineage_climate["inputs"]["n_dated_lineage_contexts"] != 6:
        raise AssertionError("lineage differentiation context count changed")
    if lc_result["n_event_level_robust_classes"] != 0:
        raise AssertionError("lineage climate robust class count changed")
    if lc_result["n_recurring_context_candidates"] != 0:
        raise AssertionError("lineage climate recurring candidate count changed")
    if lc_result["decision"] != "no_recurring_lineage_differentiation_context_survives_age_region_background_gates":
        raise AssertionError("lineage climate decision changed")

    lineage_sea = json.loads(LINEAGE_SEA.read_text(encoding="utf-8"))
    if lineage_sea["n_representative_groups"] != 3:
        raise AssertionError("lineage sea-level representative-group count changed")
    if len(lineage_sea["event_metric_classes"]) != 21:
        raise AssertionError("lineage sea-level event-metric family changed")
    if any(r["robust_class"] != "unresolved" for r in lineage_sea["event_metric_classes"]):
        raise AssertionError("lineage sea-level robust class appeared without evidence update")
    if lineage_sea["recurring_context_candidates"]:
        raise AssertionError("lineage sea-level recurring candidate appeared")
    if lineage_sea["decision"] != "no_recurring_global_sea_level_context_survives_age_background_window_gates":
        raise AssertionError("lineage sea-level decision changed")
    if "not local island connectivity" not in lineage_sea["analysis_scope"]:
        raise AssertionError("global sea-level/local-connectivity boundary was lost")

    tree = json.loads(TREE_AUDIT.read_text(encoding="utf-8"))
    if tree["decision"] != "no_public_machine_readable_dated_tree_recovered_for_additional_transition_calendarization":
        raise AssertionError("public dated-tree ceiling changed without updating the active evidence contract")
    if tree["consequence"]["repeated_trigger"] != "not_evaluable_single_dated_transition_event":
        raise AssertionError("dated-tree audit must not manufacture repeated trigger support")
    stop = " ".join(tree["stop_rules"]).lower()
    for phrase in ("published phylogeny graphics", "relative lineage depth", "lineage split or dispersal date"):
        if phrase not in stop:
            raise AssertionError(f"dated-tree stop rule lost: {phrase}")

    text = SYNTHESIS.read_text(encoding="utf-8")
    required_synthesis_phrases = (
        "repeated trait history is much better identified than repeated historical cause",
        "no_tested_climate_direction_survives_full_chronology_paleolocation_envelope",
        "no_recurring_lineage_differentiation_context_survives_age_region_background_gates",
        "robust event-level classes: **0/324**",
        "no_recurring_global_sea_level_context_survives_age_background_window_gates",
        "robust event-metric classes: **0/21**",
        "broad_mpt_overlap_high_but_not_event_discriminating",
        "local fragmentation therefore remains untested rather than rejected",
        "Historical alignment alone never establishes natural selection or adaptation",
    )
    for phrase in required_synthesis_phrases:
        if phrase not in text:
            raise AssertionError(f"active synthesis missing phrase: {phrase}")

    forbidden_upgrades = (
        "rain adaptation was demonstrated",
        "sea level caused orientation",
        "mid-pleistocene transition caused",
        "independent adaptive convergence was demonstrated",
        "climate was irrelevant",
        "fragmentation was ruled out",
    )
    lower = text.lower()
    for phrase in forbidden_upgrades:
        if phrase in lower:
            raise AssertionError(f"forbidden causal upgrade found: {phrase}")

    print(
        "Chapter 2 historical differentiation evidence: "
        f"{len(rows)} modules; final_class={FINAL_CLASS}; "
        "lineage_climate_candidates=0; lineage_sea_level_candidates=0"
    )


if __name__ == "__main__":
    main()
