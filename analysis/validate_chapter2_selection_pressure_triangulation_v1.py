#!/usr/bin/env python3
"""Validate the Chapter 2 space-time selection-pressure triangulation contract."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
DOC = ROOT / "docs" / "chapter2" / "SELECTION_PRESSURE_TRIANGULATION_V1.md"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)


def main() -> int:
    tri_path = EVID / "chapter2_selection_pressure_triangulation_v1.csv"
    contract_path = EVID / "chapter2_temporal_environment_alignment_contract_v1.json"
    asset_path = EVID / "chapter2_dated_tree_paleoclimate_asset_audit_v1.csv"
    history_path = EVID / "japan38_relative_event_depth_v1.json"
    ecology_path = EVID / "chapter2_ecological_explanatory_reach_v1.json"
    source_path = EVID / "fdt4_taiwan_multisource_orientation_sensitivity_v1.json"
    function_path = EVID / "chapter2_trait_function_history_table_v1.csv"

    for path in (
        tri_path,
        contract_path,
        asset_path,
        history_path,
        ecology_path,
        source_path,
        function_path,
        DOC,
    ):
        assert path.exists(), f"missing required file: {path.relative_to(ROOT)}"

    tri = read_csv(tri_path)
    assert len(tri) >= 9
    by_key = {(r["trait_id"], r["factor_domain"]): r for r in tri}
    required = {
        ("orientation", "hydric_regime"),
        ("orientation", "thermal_regime"),
        ("orientation", "radiation_pollinator_presentation"),
        ("colour_continuous", "radiative_environment"),
        ("phyllary_posture", "enemy_access_wetting"),
        ("stickiness", "enemy_community_and_cost"),
        ("capitulum_outline_shape", "multivariate_environment"),
        ("involucre_architecture_armature", "hydric_radiative_mechanical_enemy"),
        ("display_quantity", "pollinator_enemy_resource"),
        ("whole_capitulum", "common_lability_or_single_syndrome"),
    }
    assert required.issubset(by_key)

    orient_h = by_key[("orientation", "hydric_regime")]
    assert orient_h["eazami_repeat_count"] == "4-6"
    assert orient_h["explanatory_tier"] == "T2_cross_axis_selection_pressure_candidate"
    assert orient_h["concordance_class"] == "multi_axis_concordant_event_alignment_missing"
    assert orient_h["eazami_event_window_status"] == "blocked_exact_dated_tree_crosswalk"
    assert "BIO12" in orient_h["azami_spatial_evidence"]
    assert "BIO15" in orient_h["eazami_present_ecology"]
    assert "rain adaptation demonstrated" in orient_h["forbidden_upgrade"]

    orient_t = by_key[("orientation", "thermal_regime")]
    assert orient_t["concordance_class"] == "scale_dependent_or_confounded"
    assert orient_t["explanatory_tier"].startswith("T1_")

    colour = by_key[("colour_continuous", "radiative_environment")]
    assert colour["eazami_repeat_count"] == "not_identified"
    assert colour["concordance_class"] == "spatial_candidate_temporal_history_unidentified"
    assert colour["explanatory_tier"].startswith("T1_")

    phyllary = by_key[("phyllary_posture", "enemy_access_wetting")]
    sticky = by_key[("stickiness", "enemy_community_and_cost")]
    assert phyllary["eazami_repeat_count"] == "3"
    assert sticky["eazami_repeat_count"] == "5"
    assert "generic_defence_weakened" in sticky["concordance_class"]
    assert phyllary["eazami_present_ecology"].startswith("Not evaluable")
    assert sticky["eazami_present_ecology"].startswith("Not evaluable")

    whole = by_key[("whole_capitulum", "common_lability_or_single_syndrome")]
    assert whole["concordance_class"] == "universal_synchronized_syndrome_not_supported"
    assert "zero of three" in whole["eazami_relative_timing"].lower()

    history = read_json(history_path)
    ml = history["ml_relative_event_depth"]
    boot = history["ufboot1000_relative_event_depth"]
    assert ml["orientation"]["minimum_steps"] == 6
    assert boot["orientation"]["metric_summaries"]["minimum_steps"]["min"] == 4.0
    assert boot["orientation"]["metric_summaries"]["minimum_steps"]["max"] == 6.0
    assert ml["phyllary"]["minimum_steps"] == 3
    assert boot["phyllary"]["metric_summaries"]["minimum_steps"]["min"] == 3.0
    assert boot["phyllary"]["metric_summaries"]["minimum_steps"]["max"] == 3.0
    assert ml["stickiness"]["minimum_steps"] == 5
    assert boot["stickiness"]["metric_summaries"]["minimum_steps"]["min"] == 5.0
    assert boot["stickiness"]["metric_summaries"]["minimum_steps"]["max"] == 5.0

    assert close(ml["orientation"]["mean_relative_lineage_depth_interval"][0], 0.7666666667)
    assert close(ml["phyllary"]["mean_relative_lineage_depth_interval"][0], 0.6952380952)
    assert close(ml["stickiness"]["mean_relative_lineage_depth_interval"][0], 0.9428571429)
    assert close(ml["stickiness"]["mean_relative_lineage_depth_interval"][1], 0.9542857143)

    ecology = read_json(ecology_path)
    assert ecology["orientation"]["status"] == "unresolved"
    bio15 = ecology["orientation"]["chelsa_bio15"]
    bio1 = ecology["orientation"]["chelsa_bio01"]
    assert min(bio15["beta_D_minus_U_sd_range"]) > 0
    assert max(bio1["beta_D_minus_U_sd_range"]) < 0
    assert bio15["species_loo_evaluations"] == 54
    assert bio1["species_loo_evaluations"] == 54
    assert ecology["phyllary_posture"]["status"] == "not_evaluable"
    assert ecology["stickiness"]["status"] == "not_evaluable"

    source = read_json(source_path)
    assert source["native_tbn_tier"]["frozen_rule_status"] == "tendency_supported"
    assert source["non_gbif_tbn_tier"]["frozen_rule_status"] == "unresolved"
    for tier in ("native_tbn_tier", "non_gbif_tbn_tier"):
        assert min(source[tier]["bio15"]["beta_D_minus_U_sd_range"]) > 0
        assert max(source[tier]["bio01"]["beta_D_minus_U_sd_range"]) < 0
        assert source[tier]["bio15"]["species_loo_sign_agreement"] == 1.0
        assert source[tier]["bio01"]["species_loo_sign_agreement"] == 1.0

    functions = {r["trait_id"]: r for r in read_csv(function_path)}
    assert functions["TF01"]["phenotype_component"] == "orientation"
    assert "rain_UV_wetting_protection" in functions["TF01"]["candidate_function"]
    assert functions["TF04"]["phenotype_component"] == "stickiness"
    assert "neutralization null" in functions["TF04"]["strongest_current_function_evidence"]

    contract = read_json(contract_path)
    assert contract["current_status"] == "BLOCKED_EXACT_DATED_TREE_CROSSWALK"
    assert contract["current_tier_decisions"]["orientation_hydric"] == "T2"
    assert contract["trait_specific_primary_tests"]["orientation"]["primary_variables"] == ["BIO12", "BIO15"]
    assert contract["explanatory_evidence_tiers"]["T5"].startswith("the trait-to-function path")
    assert contract["calendar_context"]["published_japanese_radiation_context_ma"] == 2.4
    assert contract["calendar_context"]["published_interval_ma"] == [1.7, 3.6]
    assert "Do not assign" in contract["calendar_context"]["prohibition"]
    assert contract["required_missing_inputs"]["exact_dated_tree"]["current_state"].startswith("not identified")

    assets = {r["asset_id"]: r for r in read_csv(asset_path)}
    assert assets["japan38_comp1061_current"]["status"] == "available_primary_history_scaffold"
    assert assets["moreyra2025_machine_readable_dated_tree"]["status"] == "not_identified_in_current_public_repo_audit"
    assert assets["paleo_pgem_series"]["time_resolution"] == "1_kyr_steps"
    assert assets["paleo_pgem_series"]["spatial_resolution"] == "1_degree_grid"
    assert "BIO1 BIO12 BIO15" in assets["paleo_pgem_series"]["variables_or_content"]
    assert assets["historical_pollinator_enemy_pressure"]["status"] == "not_available"

    text = DOC.read_text(encoding="utf-8")
    required_phrases = [
        "present spatial gradient → repeated history → relative event placement",
        "Azami: `trait ~ present environmental gradient across space`",
        "EAzami: `trait transition windows ~ environmental level/change/variability through time`",
        "Tier T2: cross-axis selection-pressure candidate",
        "BIO12 and BIO15 are different predictors",
        "Do not replace it with “rain adaptation was demonstrated.”",
        "exact event age remains `STOP_NOT_IDENTIFIABLE`",
        "whole-capitulum synchronized temporal assembly is not supported",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"missing narrative contract phrase: {phrase}"

    # Guard against affirmative causal upgrades while allowing explicit negations/stop rules.
    forbidden_affirmations = [
        "We demonstrate rain adaptation",
        "We established adaptive convergence",
        "The transitions occurred at 2.4 Ma",
        "Stickiness is a universal defence",
        "BIO12 and BIO15 reproduce the same coefficient",
    ]
    for phrase in forbidden_affirmations:
        assert phrase not in text

    print("Chapter 2 selection-pressure triangulation v1: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
