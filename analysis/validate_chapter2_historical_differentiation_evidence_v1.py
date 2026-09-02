#!/usr/bin/env python3
"""Validate the active Chapter 2 historical-differentiation evidence ledger."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv"
SYNTHESIS = ROOT / "docs/chapter2/HISTORICAL_DIFFERENTIATION_EVIDENCE_SYNTHESIS_V1.md"
CLIMATE = ROOT / "data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json"
SEA = ROOT / "data/evidence/chapter2_orientation_deboer_sealevel_envelope_v1_summary.json"
MPT = ROOT / "data/evidence/chapter2_orientation_mpt_overlap_audit_v1.json"

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


def main() -> None:
    for p in (LEDGER, SYNTHESIS, CLIMATE, SEA, MPT):
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

    text = SYNTHESIS.read_text(encoding="utf-8")
    for phrase in (
        "identifiability gradient across capitulum modules",
        "repeated history is much better identified than repeated historical cause",
        "no_tested_climate_direction_survives_full_chronology_paleolocation_envelope",
        "no_global_sea_level_metric_survives_full_chronology_gate",
        "Mid-Pleistocene Transition",
        "A stronger lineage-level result cannot be borrowed",
        "Historical alignment alone never establishes natural selection or adaptation",
    ):
        if phrase not in text:
            raise AssertionError(f"active synthesis missing phrase: {phrase}")

    forbidden_upgrades = (
        "rain adaptation was demonstrated",
        "sea level caused orientation",
        "mid-pleistocene transition caused",
        "independent adaptive convergence was demonstrated",
    )
    lower = text.lower()
    for phrase in forbidden_upgrades:
        if phrase in lower:
            raise AssertionError(f"forbidden causal upgrade found: {phrase}")

    print(f"Chapter 2 historical differentiation ledger: {len(rows)} modules validated")


if __name__ == "__main__":
    main()
