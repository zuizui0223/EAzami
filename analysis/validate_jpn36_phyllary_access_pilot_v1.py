#!/usr/bin/env python3
"""Validate the frozen JPN36 non-destructive phyllary-access pilot contract."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/evidence/jpn36_phyllary_access_pilot_contract_v1.json"
AUTH_SCHEMA = ROOT / "data/schema/jpn36_phyllary_access_authorization_schema_v1.json"
ELIGIBLE = ROOT / "sampling/jpn36_phyllary_access_eligible_heads_v1.csv"
ASSIGNMENT = ROOT / "sampling/jpn36_phyllary_access_assignment_v1.csv"
OBSERVATIONS = ROOT / "sampling/jpn36_phyllary_access_observations_v1.csv"
FDT8 = ROOT / "data/evidence/fdt8_field_feasibility_registry_v1.csv"
READINESS_V18 = ROOT / "data/evidence/fdt_multitrait_execution_readiness_v18.json"
HISTORY = ROOT / "data/evidence/japan38_multitrait_history_summary_v1.json"
TRAITS = ROOT / "data/evidence/japan38_nmns_capitulum_trait_seed_v1.csv"
OUT = ROOT / "data/evidence/jpn36_phyllary_access_pilot_validation_v1.json"


ELIGIBLE_REQUIRED = {
    "pilot_id",
    "site_id",
    "population_id",
    "observation_date_local",
    "pair_id",
    "individual_id",
    "capitulum_id",
    "phenological_stage",
    "capitulum_diameter_mm",
    "capitulum_diameter_bin",
    "baseline_damage_fraction",
    "baseline_damage_bin",
    "phyllary_posture_class",
    "natural_stickiness_state",
    "minimum_access_gap_mm",
    "outer_phyllary_angle_deg",
    "natural_head_orientation_deg",
    "taxon_identity_confirmed",
    "live_state_confirmed",
    "permit_record_id",
    "land_manager_authorization_record_id",
    "conservation_review_record_id",
    "terminal_collection_authorization_record_id",
    "viability_authorization_record_id",
    "device_qualification_record_id",
    "eligible",
    "exclusion_reason",
}

ASSIGNMENT_REQUIRED = {
    "pilot_id",
    "site_id",
    "population_id",
    "pair_id",
    "individual_id",
    "capitulum_id",
    "matched_individual_id",
    "matched_capitulum_id",
    "assignment",
    "randomization_seed",
    "randomization_method",
    "assignment_hash",
    "authorization_record_id",
    "device_qualification_record_id",
    "device_id",
    "material_lot",
    "target_access_gap_mm",
    "treatment_attempted",
    "handling_duration_seconds",
    "achieved_access_gap_mm",
    "pre_head_orientation_deg",
    "post_head_orientation_deg",
    "device_retained",
    "floret_or_reproductive_contact",
    "tissue_injury",
    "treatment_integrity",
    "attrition_reason",
}

OBSERVATION_REQUIRED = {
    "pilot_id",
    "site_id",
    "population_id",
    "pair_id",
    "individual_id",
    "capitulum_id",
    "assignment",
    "observation_bout_id",
    "bout_type",
    "phenological_stage",
    "device_id",
    "treatment_integrity",
    "minimum_access_gap_mm",
    "outer_phyllary_angle_deg",
    "head_orientation_deg",
    "legitimate_visitor_approaches",
    "legitimate_visitor_landings",
    "probing_visits",
    "effective_reproductive_contact_count",
    "visitor_observation_minutes",
    "enemy_approaches",
    "enemy_contact_or_entry_attempts",
    "enemy_successful_access_events",
    "florivory_events",
    "external_damage_fraction",
    "predispersal_seed_predator_evidence",
    "mature_head_recovered",
    "total_achenes",
    "filled_achenes",
    "viability_assay_method",
    "viable_achenes",
    "floret_or_reproductive_contact",
    "tissue_injury",
    "stop_triggered",
    "stop_reason",
    "missingness_reason",
}


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def require_header(path: Path, required: set[str]) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        fields = set(next(csv.reader(handle)))
    missing = sorted(required - fields)
    if missing:
        raise RuntimeError(f"{path}: missing required columns: {missing}")
    return sorted(required)


def require_contains(items: list[str], tokens: list[str], label: str) -> None:
    joined = "\n".join(items).lower()
    missing = [token for token in tokens if token.lower() not in joined]
    if missing:
        raise RuntimeError(f"{label} is missing required concepts: {missing}")


def validate_contract(contract: dict) -> None:
    if contract.get("contract_version") != "jpn36_phyllary_access_pilot_v1":
        raise RuntimeError("Unexpected protocol version")
    taxon = contract["taxon"]
    expected = {
        "paper_japan_member_id": "JPN_36",
        "accepted_name": "Cirsium sieboldii",
        "authority_match_status": "exact_authority_concept_match",
        "natural_phyllary_state": "appressed",
        "natural_stickiness_state": "nonsticky_or_nearly_nonsticky",
    }
    for key, value in expected.items():
        if taxon.get(key) != value:
            raise RuntimeError(f"Taxon/state lock changed: {key}")
    if contract["scope"].get("current_field_execution_authorized") is not False:
        raise RuntimeError("Repository contract must fail closed until site-specific authorization exists")
    rights = contract["rights_and_conservation_gate"]
    if rights.get("maximum_fraction_of_counted_flowering_individuals") != 0.02:
        raise RuntimeError("Population intervention cap changed")
    if rights.get("maximum_experimental_heads") != 24:
        raise RuntimeError("Maximum experimental heads changed")
    require_contains(
        rights["required_before_randomization"],
        ["land_manager", "manipulation", "conservation", "collection", "viability", "census", "device"],
        "rights/conservation gate",
    )

    device = contract["device"]
    require_contains(
        device["common_requirements"],
        ["removable", "no adhesive", "no phyllary cutting", "no floret", "no intentional change"],
        "device requirements",
    )
    if "same collar/frame" not in device["sham_operation"]:
        raise RuntimeError("Sham must use the same external structure")

    field = contract["field_design"]
    if field.get("biological_unit") != "individual plant":
        raise RuntimeError("Biological unit must remain the individual plant")
    if field.get("target_pair_count") != 12 or field.get("target_individual_count") != 24:
        raise RuntimeError("Frozen sample allocation changed")
    if field.get("arms") != ["access_proxy", "sham"]:
        raise RuntimeError("Frozen arm order changed")
    if field.get("frozen_randomization_seed") != "JPN36-PHYLLARY-ACCESS-V1-20260827":
        raise RuntimeError("Frozen randomization seed changed")
    require_contains(
        list(contract["required_observations"]),
        ["baseline", "manipulation_integrity", "legitimate_visitors", "enemies", "reproduction"],
        "required observation families",
    )
    require_contains(
        contract["required_observations"]["reproduction"],
        ["total achenes", "filled achenes", "viability", "viable achenes", "missingness"],
        "reproductive observations",
    )
    require_contains(
        list(contract["stop_rules"]),
        ["before_start", "individual_head", "batch", "analysis"],
        "stop-rule families",
    )
    require_contains(
        contract["stop_rules"]["analysis"],
        ["do not replace", "nonsignificant", "do not invent", "adaptation"],
        "analysis stop rules",
    )
    require_contains(
        [contract["claim_boundary"]],
        ["cannot show", "adaptive", "historical transition", "fitness"],
        "claim boundary",
    )


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)

    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    forced = history["transition_identifiability"]["phyllary_posture"]["JPN_36_ufboot_forced_fraction"]
    if forced != 0.754:
        raise RuntimeError("Frozen JPN36 phyllary terminal support changed")

    trait = {row["paper_japan_member_id"]: row for row in csv_rows(TRAITS)}["JPN_36"]
    if trait["paper_taxon_concept"] != "Cirsium sieboldii":
        raise RuntimeError("JPN36 taxon concept changed")
    if trait["phyllary_posture"] != "appressed":
        raise RuntimeError("JPN36 phyllary state changed")
    if trait["stickiness_state"] != "nonsticky_or_nearly_nonsticky":
        raise RuntimeError("JPN36 stickiness state changed")

    fdt8_rows = csv_rows(FDT8)
    focal = next(
        row for row in fdt8_rows
        if row["paper_japan_member_id"] == "JPN_36" and row["module"] == "phyllary_posture"
    )
    if focal["priority_class"] != "field_first":
        raise RuntimeError("FDT8 no longer ranks JPN36 as field_first")
    if focal["observed_state"] != "appressed_phyllaries_nonsticky":
        raise RuntimeError("FDT8 JPN36 state changed")
    require_contains(
        [focal["recommended_execution"], focal["prohibited_shortcut"]],
        ["reversible", "versus sham", "enemy", "visitor", "mature/viable seed", "do not cut/remove"],
        "FDT8 execution contract",
    )

    readiness = json.loads(READINESS_V18.read_text(encoding="utf-8"))
    if not readiness["field_execution_priority"]["first"].startswith("JPN36 non-destructive"):
        raise RuntimeError("Readiness v18 no longer makes JPN36 the first field execution target")

    schema = json.loads(AUTH_SCHEMA.read_text(encoding="utf-8"))
    schema_required = set(schema["required"])
    require_contains(
        sorted(schema_required),
        ["execution_authorized", "land_manager", "manipulation", "conservation", "collection", "viability", "census", "device"],
        "authorization schema",
    )
    if schema["properties"]["execution_authorized"].get("const") is not True:
        raise RuntimeError("Authorization schema must require an explicit true execution gate")

    checked = {
        "eligible": require_header(ELIGIBLE, ELIGIBLE_REQUIRED),
        "assignment": require_header(ASSIGNMENT, ASSIGNMENT_REQUIRED),
        "observations": require_header(OBSERVATIONS, OBSERVATION_REQUIRED),
    }
    assignment_rows = csv_rows(ASSIGNMENT)
    if assignment_rows:
        raise RuntimeError("Assignment ledger must remain empty while field execution is unauthorized")

    summary = {
        "contract_version": "jpn36_phyllary_access_pilot_validation_v1",
        "status_date": "2026-08-27",
        "source_protocol": "data/evidence/jpn36_phyllary_access_pilot_contract_v1.json",
        "fdt8_alignment": {
            "field_first_target": "JPN_36",
            "taxon": "Cirsium sieboldii",
            "natural_phyllary_state": "appressed",
            "natural_stickiness_state": "nonsticky_or_nearly_nonsticky",
            "ufboot_terminal_forced_fraction": forced,
            "non_destructive_proxy_vs_sham": True,
            "joint_endpoint_families": [
                "enemy access/damage",
                "legitimate visitor access/effective contact",
                "mature/filled/viable achene output",
            ],
        },
        "protocol_schema_ready": True,
        "authorization_schema_ready": True,
        "ledger_schema_checks": checked,
        "sample_allocation": {
            "biological_unit": "individual plant",
            "pairs": 12,
            "individuals": 24,
            "arms": ["access_proxy", "sham"],
            "ratio_within_pair": "1:1",
            "one_head_per_individual": True,
            "randomization_seed": "JPN36-PHYLLARY-ACCESS-V1-20260827",
        },
        "field_execution_authorized": False,
        "empirical_result_available": False,
        "blocking_gates": [
            "site-specific land-manager and manipulation approval record",
            "conservation review and flowering-individual census",
            "terminal collection and viability-assay approval",
            "v1 device qualification and frozen natural-range access target",
        ],
        "next_gate": "Complete observation-only reference/state confirmation, qualify one frozen active/sham device, and supply a deidentified authorization record before deterministic pair allocation.",
        "claim_boundary": "Protocol and schema readiness only. No field execution, manipulation safety, enemy exclusion, pollinator effect, reproductive effect, historical mechanism or adaptation has been demonstrated.",
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
