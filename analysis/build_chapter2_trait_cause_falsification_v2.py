#!/usr/bin/env python3
"""Outcome-blind three-trait cause-model elimination for Chapter 2.

The model families are fixed before execution. The analysis combines current
focal evolutionary results with frozen direct/analog manipulation evidence.
External effect sizes are never transported to East-Asian Cirsium.

Execution trigger: 2026-09-06 run 1; no model or threshold change.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"


def load_json(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def load_csv(name: str) -> list[dict[str, str]]:
    with (EVID / name).open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    out = {r[key]: r for r in rows}
    if len(out) != len(rows):
        raise AssertionError(f"duplicate {key}")
    return out


def build() -> dict:
    base = load_json("chapter2_trait_cause_falsification_v1.json")
    current = load_json("chapter2_current_claims_h1_h4_v1.json")
    orient_screen = load_json("orientation_mechanism_reduction_result_v1.json")
    fun_ext = index(load_csv("fdt1_broad_functional_calibration_seed_extension_v1.csv"), "study_id")
    cirs_ext = index(load_csv("cirsium_interaction_evidence_seed_extension_v1.csv"), "evidence_id")

    assert current["assembly"]["minimum_changes"]["orientation"] == "4-6 across UFBoot; ML 6"
    assert current["assembly"]["minimum_changes"]["phyllary"] == 3
    assert current["assembly"]["minimum_changes"]["stickiness"] == 5
    assert current["orientation_transition_regime"]["h1"]["strict_n10_exact_rank"] == "4/126 = 3.17%"
    assert current["historical_persistence"]["h4"]["overall_match"] == "99/376 = 26.3%"

    ph_v1 = {x["model"]: x["status"] for x in base["phyllary"]["models"]}
    st_v1 = {x["model"]: x["status"] for x in base["stickiness"]["models"]}
    assert ph_v1 == {
        "P1_pollinator_access_primary": "weakened",
        "P2_reproductive_enemy_protection": "compatible_leading_external_prior",
        "P3_broad_abiotic_or_geographic_sorting": "not_supported_current_public_panel",
    }
    assert st_v1 == {
        "S1_universal_antagonist_defence": "contradicted_as_universal_model",
        "S2_universal_trait_cost": "contradicted_as_universal_model",
        "S3_enemy_dependent_defence_cost_balance": "compatible_and_only_model_not_contradicted",
    }

    assert fun_ext["CREM_ORIENT_ACHENE_01"]["direction"] == "nodding_higher"
    assert abs(float(fun_ext["CREM_ORIENT_ACHENE_01"]["estimate"]) - 3.585987) < 1e-6
    assert fun_ext["CREM_ORIENT_POLL_01"]["direction"] == "no_preference"
    assert fun_ext["CREM_ORIENT_ABIOTIC_01"]["direction"] == "water_and_UVB_reduce_viability"
    assert fun_ext["CREM_ORIENT_TEMP_01"]["direction"] == "no_meaningful_thermal_difference"
    assert orient_screen["best_family"] == "combined_time_abiotic"
    assert orient_screen["ranking"][-1] == "static_pollinator_only"
    assert orient_screen["families"][0]["family"] == "static_pollinator_only"
    assert orient_screen["families"][0]["full_core_match_rate"] == 0.0
    best = next(x for x in orient_screen["families"] if x["family"] == "combined_time_abiotic")
    assert best["heldout_mean"] == 1.0

    assert fun_ext["CENTA_BR_POLL_FREQ_01"]["direction"] == "no_increase_after_spine_removal"
    assert float(fun_ext["CENTA_BR_POLL_DUR_01"]["estimate"]) == 20
    assert float(fun_ext["CENTA_BR_SEED_01"]["estimate"]) == -22
    assert fun_ext["CENTA_BR_LEPI_01"]["direction"] == "intact_spines_lower_illegitimate_visitation"

    assert cirs_ext["INT016"]["taxon"] == "Cirsium discolor"
    assert cirs_ext["INT016"]["direction"] == "sticky_defence_benefit"
    assert cirs_ext["INT017"]["taxon"] == "Cirsium flodmani"
    assert cirs_ext["INT017"]["direction"] == "null"
    assert cirs_ext["INT018"]["direction"] == "guild_selective"

    orientation_models = [
        {"model":"O1_static_pollinator_attraction_primary","prediction":"orientation should alter pollinator preference strongly enough to explain the focal pattern without abiotic exposure","tests":["Cremanthodium erect-vs-nodding manipulation: no pollinator preference","existing structural-sufficiency screen: static_pollinator_only ranks last and has full_core_match_rate=0"],"status":"weakened_not_supported_as_primary","reason":"both direct Asteraceae manipulation and the independent mechanism-reduction screen fail to support static pollinator attraction as the dominant explanation"},
        {"model":"O2_thermal_timing_primary","prediction":"orientation effects should be chiefly mediated by floral thermal conditions/timing","tests":["Cremanthodium manipulation: no meaningful internal thermal difference","mechanism-reduction screen: thermal_timing_only ranks below abiotic_protection_only and combined_time_abiotic"],"status":"secondary_compatible_not_primary","reason":"thermal timing can contribute in other systems, but direct Cremanthodium evidence does not support orientation-driven heating and the combined abiotic+timing family fits better"},
        {"model":"O3_abiotic_reproductive_exposure_plus_timing","prediction":"orientation should alter exposure to wetting/rain/UV or related time-window stress, with pollinator effects optional rather than required","tests":["focal East-Asian U-to-D transition regime exact rank 4/126 under strict coverage","Cremanthodium: water and UV-B reduce pollen viability; erect manipulation lowers achene set; no pollinator preference","mechanism-reduction: combined_time_abiotic ranks first and passes both held-out targets"],"status":"leading_mechanism_domain","reason":"this is the only orientation family simultaneously compatible with the focal transition-regime pattern, direct Asteraceae manipulation, and the existing mechanism-reduction screen"}
    ]
    phyllary_models = [
        {"model":"P1_pollinator_access_primary","tests":["Pedicularis protective-bract manipulation: pollinator effect null","Centaurea involucral-spine removal: legitimate pollinator visit frequency did not increase; visit duration increased about 20%"],"status":"weakened_by_independent_structural_manipulations","reason":"reducing protective architecture does not consistently increase legitimate visitation frequency; a handling/access cost remains possible but is not the main supported benefit"},
        {"model":"P2_mechanical_antagonist_exclusion","tests":["Pedicularis: draining protective bracts increased seed predation and lowered final seed set","Centaurea: involucral spines deterred illegitimate Lepidoptera and spine removal reduced filled seeds by 22%"],"status":"leading_external_mechanism_domain","reason":"two independent direct structural manipulations, including a close Cardueae analog, converge on antagonist exclusion with reproductive benefit"},
        {"model":"P3_broad_abiotic_or_geographic_sorting","tests":["frozen public phyllary spatial panel n=4 has segregation p=0.4998"],"status":"not_supported_current_public_panel","reason":"the current broad spatial panel supplies no supporting segregation pattern, although its small state-diverse sample cannot exclude local abiotic effects"}
    ]
    stickiness_models = [
        {"model":"S1_universal_antagonist_defence","tests":["1983 Cirsium discolor: defence benefit after occluding sticky exudate","1983 Cirsium flodmani: no treatment effect","2003 later Cirsium discolor: neutralization did not increase seed predation or reduce seed production"],"status":"contradicted_as_universal_rule_within_Cirsium","reason":"benefit and null responses occur within the genus and even differ across study periods in C. discolor"},
        {"model":"S2_universal_trait_cost","tests":["frozen Bejaria floral manipulation shows lower florivory and higher fruit set when sticky"],"status":"contradicted_as_universal_rule","reason":"direct floral stickiness can produce a net reproductive benefit in at least one system"},
        {"model":"S3_arthropod_community_filter_by_trait_cost","tests":["within-Cirsium benefit-vs-null context dependence in 1983","Thomas 2007: pollinators avoid contact, some seed predators bypass traps, ants/aphids are deterred, predators may glean","external Bejaria benefit and Datura cost contexts from frozen v1 evidence"],"status":"leading_and_only_general_model_not_contradicted","reason":"guild selectivity plus benefit/null/cost heterogeneity is expected if net value depends on local arthropod composition and secretion/resistance cost"}
    ]

    return {
        "version":"chapter2_trait_cause_falsification_v2","status_date":"2026-09-06","scope":"fixed three-trait mechanism-domain elimination; focal evolutionary evidence plus targeted manipulation extensions; no new environmental predictor search",
        "orientation":{"models":orientation_models,"leading_domain":"abiotic_reproductive_exposure_plus_timing","focal_support_level":"transition_level_ecological_pattern_plus_external_direct_manipulation","historical_origin_boundary":"the present regime matches only 99/376 origin scenarios, so the maintenance/current mechanism domain is not established as the historical origin cause"},
        "phyllary":{"models":phyllary_models,"leading_domain":"mechanical_antagonist_exclusion","focal_support_level":"repeated_history_plus_external_direct_manipulations_only","focal_boundary":"direct Cirsium phyllary manipulation is absent"},
        "stickiness":{"models":stickiness_models,"leading_domain":"arthropod_community_filter_by_trait_cost","focal_support_level":"repeated_history_plus_direct_within_genus_context_dependence","focal_boundary":"JPN15 within-species neutralization with local enemy and fitness endpoints is absent"},
        "whole_capitulum":{"one_common_driver":"not_supported_as_simplest_model","trait_specific_filter_model":"best_current_integrative_model","reason":"the three traits require different mechanism domains to accommodate the focal histories and direct manipulation evidence: abiotic exposure/timing for orientation, mechanical antagonist access for phyllary, and arthropod-community filtering under cost for stickiness","claim_boundary":"this does not prove genetic/developmental modularity or that every reconstructed transition was caused by the assigned domain"},
        "frozen_biological_mapping":{"orientation":"abiotic reproductive exposure / timing filter","phyllary_posture":"mechanical antagonist-access filter","stickiness":"adhesive arthropod-community filter under defence-cost tradeoff"}
    }


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); args=p.parse_args(); result=build(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(result,indent=2,ensure_ascii=False)); return 0

if __name__ == "__main__": raise SystemExit(main())
