#!/usr/bin/env python3
"""Validate trait-by-pressure explanatory triangulation.

The matrix records independent evidence links. It deliberately avoids a summed
score because recurrence, phenotype homology, current niche correspondence,
historical environment and focal fitness are not exchangeable evidence units.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
MATRIX = EVID / "chapter2_selection_pressure_triangulation_v1.csv"
DOC = ROOT / "docs" / "chapter2" / "SELECTION_PRESSURE_EXPLANATORY_RANKING_V1.md"
RELATIVE = EVID / "japan38_relative_event_depth_v1.json"
ECOLOGY = EVID / "chapter2_ecological_explanatory_reach_v1.json"
TAIWAN = EVID / "fdt4_taiwan_multisource_orientation_sensitivity_v1.json"
CLOSURE = EVID / "chapter2_space_time_public_data_closure_v1.csv"
FUNCTION = EVID / "chapter2_trait_function_history_table_v1.csv"
CONTINUOUS = EVID / "chapter2_time_axis_compute" / "continuous_primary_phylogenetic_structure_v1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    rows = read_csv(MATRIX)
    keyed = {(r["trait_id"], r["pressure_domain"]): r for r in rows}
    assert len(keyed) == len(rows) == 13

    rel = read_json(RELATIVE)
    ecology = read_json(ECOLOGY)
    taiwan = read_json(TAIWAN)
    closure = {r["trait_id"]: r for r in read_csv(CLOSURE)}
    function = {r["phenotype_component"]: r for r in read_csv(FUNCTION)}
    continuous = read_csv(CONTINUOUS)
    doc = DOC.read_text(encoding="utf-8")

    # R and T are exact frozen outputs, not values inferred from ecological fit.
    depth = rel["ufboot1000_relative_event_depth"]
    assert depth["orientation"]["metric_summaries"]["minimum_steps"]["min"] == 4.0
    assert depth["orientation"]["metric_summaries"]["minimum_steps"]["median"] == 5.0
    assert depth["orientation"]["metric_summaries"]["minimum_steps"]["max"] == 6.0
    assert depth["phyllary"]["metric_summaries"]["minimum_steps"]["min"] == 3.0
    assert depth["phyllary"]["metric_summaries"]["minimum_steps"]["max"] == 3.0
    assert depth["stickiness"]["metric_summaries"]["minimum_steps"]["min"] == 5.0
    assert depth["stickiness"]["metric_summaries"]["minimum_steps"]["max"] == 5.0

    hydric = keyed[("orientation", "hydric_exposure")]
    assert hydric["current_explanatory_class"] == "multi_axis_concordant_selection_pressure_candidate"
    assert "BIO12" in hydric["azami_spatial_gradient_S"]
    assert "BIO15" in hydric["eazami_current_ecology_C"]
    assert hydric["historical_environment_P"].startswith("not_evaluable_")
    assert hydric["focal_function_fitness_F"].startswith("not_evaluable_")

    # Current ecological direction is robust; threshold class is source-sensitive.
    assert ecology["orientation"]["status"] == "unresolved"
    assert ecology["orientation"]["chelsa_bio15"]["accepted_topology_sign_agreement"] == 1.0
    assert ecology["orientation"]["chelsa_bio15"]["species_loo_evaluations"] == 54
    assert ecology["orientation"]["chelsa_bio01"]["accepted_topology_sign_agreement"] == 1.0
    assert taiwan["native_tbn_tier"]["frozen_rule_status"] == "tendency_supported"
    assert taiwan["non_gbif_tbn_tier"]["frozen_rule_status"] == "unresolved"
    assert taiwan["decision"]["primary_status_change"] is False

    # Spatial breadth classes remain those frozen by the prior cross-repository audit.
    assert closure["orientation"]["cross_axis_class"] == "priority_space_time_ecology_bridge"
    assert closure["colour_continuous"]["cross_axis_class"] == "space_only_radiation_sorting_candidate"
    assert closure["phyllary_posture"]["cross_axis_class"] == "history_only_boundary"
    assert closure["stickiness"]["cross_axis_class"] == "history_only_boundary"

    # L is an independent mechanism prior and must retain focal-system boundaries.
    assert function["orientation"]["function_validation_status"] == "candidate_function_calibrated_not_validated_in_focal_Cirsium"
    assert function["phyllary_posture"]["function_validation_status"] == "candidate_function_analog_not_focal_validation"
    assert function["stickiness"]["function_validation_status"] == "context_discrimination_ready_no_generic_sign"
    assert "neutralization null" in function["stickiness"]["strongest_current_function_evidence"]
    assert function["colour_continuous"]["function_validation_status"] == "candidate_function_context_dependent"

    sticky_enemy = keyed[("stickiness", "reproductive_enemy_interaction")]
    assert sticky_enemy["current_explanatory_class"] == "recurrent_trait_generic_defence_weakened"
    assert "mixed/conflicting" in sticky_enemy["independent_mechanism_prior_L"]
    assert keyed[("phyllary_posture", "reproductive_enemy_exclusion")]["current_explanatory_class"] == "historical_mechanism_candidate_driver_unidentified"

    # No corrected continuous Japanese primary history may be silently promoted.
    primary_n2 = [r for r in continuous if r["scope"] == "nobs_ge_2"]
    assert len(primary_n2) == 8
    assert {r["history_support_class"] for r in primary_n2} == {"two_sided_not_supported"}
    assert keyed[("colour_continuous", "solar_radiative_environment")]["current_explanatory_class"] == "spatial_mechanism_candidate_temporal_depth_unresolved"

    # P and F remain open for every pressure row; convergence cannot be called adaptation.
    for row in rows:
        assert row["historical_environment_P"].startswith("not_evaluable_")
        assert row["focal_function_fitness_F"].startswith("not_evaluable_")
        assert row["forbidden_upgrade"].strip()

    required = [
        "independent evidence dimensions converge",
        "Why no numerical score is used",
        "orientation × hydric exposure",
        "hydric-domain convergence across independent facets",
        "Orientation × thermal regime is informative because it does not align simply",
        "repeated history does not rescue the generic mechanism",
        "Historical pollinator/enemy turnover needs its own data series",
        "Multi-axis concordance strengthens a candidate selective-pressure explanation",
    ]
    for phrase in required:
        assert phrase in doc, phrase

    forbidden = [
        "hydric exposure demonstrates adaptation",
        "BIO12 and BIO15 are the same variable",
        "stickiness is an adaptive defence",
        "relative lineage-depth gives event age",
        "visitor abundance proves pollination",
    ]
    low = doc.lower()
    for phrase in forbidden:
        assert phrase.lower() not in low, phrase

    print("selection-pressure triangulation matrix: validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
