#!/usr/bin/env python3
"""Validate trait-by-pressure explanatory triangulation against frozen evidence.

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
    required_columns = {
        "trait_id",
        "factor_domain",
        "azami_spatial_status",
        "azami_spatial_evidence",
        "eazami_repeat_count",
        "eazami_relative_timing",
        "eazami_present_ecology",
        "eazami_event_window_status",
        "mechanism_prior",
        "fitness_evidence",
        "concordance_class",
        "explanatory_tier",
        "allowed_claim",
        "forbidden_upgrade",
        "next_decisive_test",
    }
    assert rows
    assert required_columns <= set(rows[0]), sorted(set(rows[0]) ^ required_columns)
    keyed = {(r["trait_id"], r["factor_domain"]): r for r in rows}
    assert len(keyed) == len(rows) == 13

    rel = read_json(RELATIVE)
    ecology = read_json(ECOLOGY)
    taiwan = read_json(TAIWAN)
    closure = {r["trait_id"]: r for r in read_csv(CLOSURE)}
    function = {r["phenotype_component"]: r for r in read_csv(FUNCTION)}
    continuous = read_csv(CONTINUOUS)
    doc = DOC.read_text(encoding="utf-8")

    # R and T are exact frozen outputs, not values inferred from ecological fits.
    depth = rel["ufboot1000_relative_event_depth"]
    assert depth["orientation"]["metric_summaries"]["minimum_steps"] == {
        "min": 4.0,
        "q05": 4.0,
        "median": 5.0,
        "q95": 6.0,
        "max": 6.0,
    }
    assert depth["phyllary"]["metric_summaries"]["minimum_steps"]["min"] == 3.0
    assert depth["phyllary"]["metric_summaries"]["minimum_steps"]["max"] == 3.0
    assert depth["stickiness"]["metric_summaries"]["minimum_steps"]["min"] == 5.0
    assert depth["stickiness"]["metric_summaries"]["minimum_steps"]["max"] == 5.0

    hydric = keyed[("orientation", "hydric_regime")]
    assert hydric["concordance_class"] == "multi_axis_concordant_event_alignment_missing"
    assert hydric["explanatory_tier"] == "T2_cross_axis_selection_pressure_candidate"
    assert "BIO12" in hydric["azami_spatial_evidence"]
    assert "BIO15" in hydric["eazami_present_ecology"]
    assert hydric["eazami_event_window_status"] == "blocked_exact_dated_tree_crosswalk"
    assert "no ancestry-matched focal Japanese orientation-to-filled-achene path" in hydric["fitness_evidence"]

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

    sticky_enemy = keyed[("stickiness", "enemy_community_and_cost")]
    assert sticky_enemy["concordance_class"] == "history_recurrence_generic_defence_weakened"
    assert "neutralization result weakens" in sticky_enemy["mechanism_prior"]
    phyllary = keyed[("phyllary_posture", "enemy_access_wetting")]
    assert phyllary["concordance_class"] == "history_recurrence_driver_unidentified"

    # No corrected continuous Japanese primary history may be silently promoted.
    primary_n2 = [r for r in continuous if r["scope"] == "nobs_ge_2"]
    assert len(primary_n2) == 8
    assert {r["history_support_class"] for r in primary_n2} == {"two_sided_not_supported"}
    colour = keyed[("colour_continuous", "radiative_environment")]
    assert colour["concordance_class"] == "spatial_candidate_temporal_history_unidentified"
    assert colour["eazami_repeat_count"] == "not_identified"

    # Historical event alignment and focal fitness remain open for every biological
    # pressure row. Whole-capitulum common-lability is a negative constraint rather
    # than a biological driver and is therefore explicitly not applicable.
    open_event_prefixes = ("blocked_", "not_evaluable", "not_applicable")
    for row in rows:
        assert row["eazami_event_window_status"].startswith(open_event_prefixes), row
        assert row["forbidden_upgrade"].strip()
        assert row["next_decisive_test"].strip()
        if row["trait_id"] != "whole_capitulum":
            low_fitness = row["fitness_evidence"].casefold()
            assert any(token in low_fitness for token in ("no_", "no ", "not_applicable", "external", "genus_level")), row

    required_phrases = [
        "independent evidence dimensions converge",
        "Why no numerical score is used",
        "Orientation × hydric exposure",
        "hydric-domain convergence across independent facets",
        "Orientation × thermal regime is informative because it does not align simply",
        "repeated history does not rescue the generic mechanism",
        "Historical pollinator/enemy turnover needs its own data series",
        "Multi-axis concordance strengthens a candidate selective-pressure explanation",
    ]
    for phrase in required_phrases:
        assert phrase in doc, phrase

    forbidden_phrases = [
        "hydric exposure demonstrates adaptation",
        "BIO12 and BIO15 are the same variable",
        "stickiness is an adaptive defence",
        "relative lineage-depth gives event age",
        "visitor abundance proves pollination",
    ]
    low_doc = doc.casefold()
    for phrase in forbidden_phrases:
        assert phrase.casefold() not in low_doc, phrase

    print("selection-pressure triangulation matrix: validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
