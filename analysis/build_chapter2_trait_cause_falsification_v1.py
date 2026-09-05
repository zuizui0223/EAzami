#!/usr/bin/env python3
"""Build a fail-closed trait-cause model-elimination summary for phyllary and stickiness.

This analysis does not search for new predictors. It evaluates a frozen set of
competing causal models against existing Chapter 2 history, occurrence-resolution,
and direct/analog functional evidence. External analogs are never transported as
Cirsium effect sizes.
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


def by_id(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {r[key]: r for r in rows}


def forced_fraction(depth: dict, trait: str, edge_id: str) -> float:
    rows = depth["ufboot1000_relative_event_depth"][trait]["forced_change_edge_frequencies"]
    hit = [r for r in rows if r["edge_id"] == edge_id]
    if len(hit) != 1:
        raise AssertionError(f"expected one forced edge {trait} {edge_id}, got {len(hit)}")
    return float(hit[0]["fraction"])


def build() -> dict:
    depth = load_json("japan38_relative_event_depth_v1.json")
    occ = load_json("chapter2_discrete_trait_occurrence_gate_sensitivity_v1.json")
    fun = by_id(load_csv("fdt1_broad_functional_calibration_seed_v1.csv"), "study_id")
    inter = by_id(load_csv("cirsium_interaction_evidence_seed_v1.csv"), "evidence_id")
    priorities = by_id(load_csv("chapter2_to_chapter3_sampling_priorities_v1.csv"), "priority_id")

    # Current history/provenance gates.
    ph = depth["ml_relative_event_depth"]["phyllary"]
    st = depth["ml_relative_event_depth"]["stickiness"]
    assert ph["minimum_steps"] == 3
    assert st["minimum_steps"] == 5
    ph36 = forced_fraction(depth, "phyllary", "JPN_36")
    st06 = forced_fraction(depth, "stickiness", "JPN_06")
    st36 = forced_fraction(depth, "stickiness", "JPN_36")
    st30 = forced_fraction(depth, "stickiness", "JPN_30")
    assert abs(ph36 - 0.728) < 1e-12
    assert abs(st06 - 0.995) < 1e-12
    assert abs(st36 - 0.707) < 1e-12
    assert abs(st30 - 0.545) < 1e-12
    assert "100/100 sisters" in priorities["P01"]["chapter2_result"]
    assert "current JPN36 terminal forced fraction 0.728" in priorities["P02"]["chapter2_result"]

    # Frozen functional rows.
    ped_poll = fun["PED_BR_POLL_01"]
    ped_pred = fun["PED_BR_PRED_01"]
    ped_seed = fun["PED_BR_FINALSET_01"]
    assert ped_poll["direction"] == "null_pollinator_effect" and abs(float(ped_poll["estimate"]) - 0.012) < 1e-12
    assert ped_pred["direction"] == "intact_water_holding_bracts_lower_seed_predation" and abs(float(ped_pred["estimate"]) + 0.072) < 1e-12
    assert ped_seed["direction"] == "intact_water_holding_bracts_higher_final_seed_set" and abs(float(ped_seed["estimate"]) - 0.025) < 1e-12

    bej_damage = fun["BEJ_STICK_FLORIV_01"]
    bej_fruit = fun["BEJ_STICK_FRUIT_01"]
    dat_seed = fun["DAT_STICK_COST_01"]
    dat_lambda = fun["DAT_STICK_LAMBDA_01"]
    cirsium_null = inter["INT006"]
    assert bej_damage["direction"] == "sticky_lower" and abs(float(bej_damage["estimate"]) + 0.21) < 1e-12
    assert bej_fruit["direction"] == "sticky_higher" and abs(float(bej_fruit["estimate"]) - 1.48148) < 1e-10
    assert dat_seed["direction"] == "sticky_lower" and float(dat_seed["estimate"]) == -53
    assert dat_lambda["direction"] == "sticky_lower" and float(dat_lambda["estimate"]) == -13
    assert cirsium_null["taxon"] == "Cirsium discolor" and cirsium_null["direction"] == "null"

    spatial = occ["broader_environment_free_spatial_support"]
    assert spatial["phyllary"]["state_counts"] == {"ascending": 3, "appressed": 1}
    assert spatial["stickiness"]["state_counts"] == {"nonsticky": 6, "sticky": 6}

    phyllary_models = [
        {
            "model": "P1_pollinator_access_primary",
            "prediction": "a protective bract state should require a detectable legitimate-pollinator access/visitation benefit or its removal should improve pollinator visitation",
            "evidence": "Pedicularis rex protective-bract manipulation: pollinator treatment beta=0.012, p=0.958 (external nonhomologous analog)",
            "status": "weakened",
            "reason": "the analog protective-bract benefit occurred without a pollinator-visitation effect; this does not directly test Cirsium phyllary geometry"
        },
        {
            "model": "P2_reproductive_enemy_protection",
            "prediction": "removing protective bract function should increase seed predation and reduce final seed set without requiring pollinator gain",
            "evidence": "Pedicularis rex: seed-predation beta=-0.072 for intact coding with p<0.0001; final-seed-set beta=+0.025 with p<0.0001; pollinator effect null",
            "status": "compatible_leading_external_prior",
            "reason": "all three qualitative predictions align in one direct manipulation, but the structure is nonhomologous to Cirsium phyllaries"
        },
        {
            "model": "P3_broad_abiotic_or_geographic_sorting",
            "prediction": "authority-coded posture should show broad spatial segregation if a coarse regional abiotic driver dominates",
            "evidence": f"broader public occurrence panel n=4 (3 ascending, 1 appressed), spatial-segregation p={spatial['phyllary']['spatial_segregation_p']}",
            "status": "not_supported_current_public_panel",
            "reason": "no broad spatial segregation is recovered; state replication is too small to exclude local abiotic or biotic effects"
        }
    ]

    stickiness_models = [
        {
            "model": "S1_universal_antagonist_defence",
            "prediction": "neutralizing floral stickiness should generally increase seed predators and reduce successful seed production",
            "evidence": "direct Cirsium discolor neutralization: no increase in seed predators and no decrease in seed production",
            "status": "contradicted_as_universal_model",
            "reason": "the closest genus-level direct manipulation returned the explicit null predicted against a universal-defence rule"
        },
        {
            "model": "S2_universal_trait_cost",
            "prediction": "sticky structures should generally reduce reproductive performance",
            "evidence": "Bejaria resinosa floral manipulation: florivory risk difference=-0.21 and fruit-set RR=1.48148 favor intact sticky flowers",
            "status": "contradicted_as_universal_model",
            "reason": "a direct floral-stickiness manipulation shows a context with clear defensive and reproductive benefit"
        },
        {
            "model": "S3_enemy_dependent_defence_cost_balance",
            "prediction": "stickiness can be beneficial where antagonists impose damage, neutral in some systems, and costly when enemy benefit is weak or excluded",
            "evidence": "Bejaria benefit + direct Cirsium discolor null + Datura cost under herbivore exclusion (first-year seed production about -53%, finite rate of increase -13%)",
            "status": "compatible_and_only_model_not_contradicted",
            "reason": "the observed benefit/null/cost sign heterogeneity is expected under context-dependent enemy pressure and trait cost"
        }
    ]

    return {
        "version": "chapter2_trait_cause_falsification_v1",
        "status_date": "2026-09-05",
        "scope": "frozen competing-model elimination using existing Chapter 2 history, occurrence-resolution and functional evidence; no new predictor search",
        "decision_rule": {
            "contradicted": "a model-required qualitative prediction fails in a direct manipulation relevant to that model",
            "weakened": "the primary prediction is absent in a nonhomologous analog or small focal panel",
            "compatible": "the observed qualitative evidence pattern is allowed by the model",
            "not_evaluable": "the focal mediator or manipulation is absent"
        },
        "phyllary": {
            "history": {
                "minimum_steps": 3,
                "JPN36_state": "appressed",
                "JPN36_ML_forced_terminal": True,
                "JPN36_UFBoot_forced_fraction": ph36,
                "median_relative_depth_envelope": [0.695, 1.0]
            },
            "models": phyllary_models,
            "current_best_explanation": "reproductive_enemy_protection_prior_leads_over_pollinator_access_and_broad_spatial_sorting",
            "focal_causation_status": "not_evaluable_without_Cirsium_phyllary_manipulation",
            "specific_next_falsifier": "JPN36 reversible appressed-phyllary access/protection manipulation versus sham measuring enemy attack, legitimate pollinator access/effective transfer, wetting and mature viable seed jointly",
            "claim_boundary": "Pedicularis bracts are nonhomologous analogs; no current result proves enemy protection, wetting protection or pollinator-access selection in Cirsium"
        },
        "stickiness": {
            "history": {
                "minimum_steps": 5,
                "median_relative_depth_envelope": [0.937, 0.954],
                "JPN06_state": "nonsticky_or_nearly_nonsticky",
                "JPN15_state": "sticky",
                "JPN06_JPN15_ML_sister_support": "100/100",
                "JPN06_UFBoot_forced_fraction": st06,
                "JPN36_UFBoot_forced_fraction": st36,
                "JPN30_UFBoot_forced_fraction": st30
            },
            "models": stickiness_models,
            "broad_spatial_auxiliary": {
                "n_taxa": 12,
                "state_counts": spatial["stickiness"]["state_counts"],
                "spatial_segregation_p": spatial["stickiness"]["spatial_segregation_p"],
                "reading": "simple broad spatial segregation is not supported; this does not test local antagonist communities"
            },
            "current_best_explanation": "local_enemy_pressure_by_trait_cost_selection_mosaic",
            "focal_causation_status": "not_evaluable_without_within_JPN15_neutralization",
            "specific_next_falsifier": "within-JPN15 natural-stickiness neutralization versus sham, with enemy access/damage, pollinator effective transfer, secretion-treatment controls and mature viable seed; JPN06 restoration remains secondary",
            "claim_boundary": "benefit/null/cost evidence comes from different taxa and systems and is model-discriminating rather than a pooled Cirsium effect"
        },
        "chapter2_interpretation": "Among the two previously unresolved modules, current evidence narrows phyllary toward a protective/enemy-exclusion mechanism prior and stickiness toward a context-dependent antagonist-defence-versus-cost mechanism. Only the stickiness universal-defence and universal-cost models are directly falsified as universal rules; focal East-Asian Cirsium causal mechanisms remain unproven."
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
