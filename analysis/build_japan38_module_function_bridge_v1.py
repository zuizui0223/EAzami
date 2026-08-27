#!/usr/bin/env python3
"""Build a fail-closed bridge from Japan38 repeated trait history to FDT1 function evidence.

The bridge deliberately does not pool unlike effect-size families and does not turn
external angiosperm manipulations into Cirsium adaptation claims. History strength,
transition localization, function evidence and focal-system priority remain separate.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--history", type=Path, required=True)
    p.add_argument("--functional-summary", type=Path, required=True)
    p.add_argument("--functional-seed", type=Path, required=True)
    p.add_argument("--orientation-meta", type=Path, required=True)
    p.add_argument("--cirsium-interactions", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--readiness", type=Path, required=True)
    p.add_argument("--bridge-output", type=Path, required=True)
    p.add_argument("--priority-output", type=Path, required=True)
    p.add_argument("--summary-output", type=Path, required=True)
    args = p.parse_args()

    history = json.loads(args.history.read_text())
    fsum = json.loads(args.functional_summary.read_text())
    orient_meta = json.loads(args.orientation_meta.read_text())
    readiness = json.loads(args.readiness.read_text())
    seed = read_csv(args.functional_seed)
    interactions = read_csv(args.cirsium_interactions)
    cmap = {r["paper_japan_member_id"]: r["paper_taxon_concept"] for r in read_csv(args.concept_map)}

    # Canonical-history contract: fail if the bridge silently drifts from PR #88.
    mh = history["minimum_change_history"]
    assert mh["orientation"]["resolved_concepts"] == 19
    assert mh["orientation"]["ml_minimum_unordered_steps"] == 6
    assert [mh["orientation"]["ufboot1000_steps_min"], mh["orientation"]["ufboot1000_steps_max"]] == [4, 6]
    assert mh["orientation"]["ufboot_root_U_fraction"] == 1.0
    assert mh["phyllary_posture"]["resolved_concepts"] == 10
    assert mh["phyllary_posture"]["ml_minimum_unordered_steps"] == 3
    assert [mh["phyllary_posture"]["ufboot1000_steps_min"], mh["phyllary_posture"]["ufboot1000_steps_max"]] == [3, 3]
    assert mh["stickiness"]["resolved_concepts"] == 12
    assert [mh["stickiness"]["ufboot1000_steps_min"], mh["stickiness"]["ufboot1000_steps_max"]] == [4, 5]

    loc = history["transition_identifiability"]
    assert loc["orientation"]["ml_individually_forced_change_edges"] == 0
    assert abs(loc["phyllary_posture"]["JPN_36_ufboot_forced_fraction"] - 0.754) < 1e-12
    assert abs(loc["stickiness"]["JPN_06_ufboot_forced_fraction"] - 0.67) < 1e-12
    assert abs(loc["stickiness"]["JPN_36_ufboot_forced_fraction"] - 0.40) < 1e-12

    # Functional-evidence contract.
    modules = fsum["modules"]
    assert modules["orientation"]["rows"] == 11 and modules["orientation"]["quantitative_ready_rows"] == 8
    assert modules["bract_defence"]["rows"] == 3 and modules["bract_defence"]["quantitative_ready_rows"] == 3
    assert modules["stickiness"]["rows"] == 2 and modules["stickiness"]["quantitative_ready_rows"] == 2
    assert orient_meta["k"] == 2
    assert abs(orient_meta["fixed_effect"]["RR"] - 1.4975664450) < 1e-10
    assert abs(orient_meta["heterogeneity"]["I2_percent"] - 93.5714188738) < 1e-10

    by_id = {r["study_id"]: r for r in seed}
    for required in [
        "POLY_ORIENT_POLLEN_01", "POLY_ORIENT_SEEDSET_01", "PLAT_ORIENT_RAIN_01",
        "BEJ_STICK_FLORIV_01", "BEJ_STICK_FRUIT_01",
        "PED_BR_POLL_01", "PED_BR_FINALSET_01", "PED_BR_PRED_01",
        "DAT_STICK_COST_01", "DAT_STICK_LAMBDA_01",
    ]:
        assert required in by_id
    cdis = [r for r in interactions if r["evidence_id"] == "INT006"]
    assert len(cdis) == 1 and cdis[0]["taxon"] == "Cirsium discolor" and cdis[0]["direction"] == "null"
    assert readiness["colour"]["mainline_role"] == "secondary_negative_module_not_primary_recurrence_evidence"

    bridge = [
        {
            "module": "orientation",
            "function_axis": "effective_pollination",
            "history_recurrence": "robust_lower_bound",
            "history_step_range": "4-6",
            "transition_localization": "weak_no_individually_forced_ML_edge",
            "priority_transition_concepts": "none_branch_specific_yet",
            "functional_evidence_state": "near_ready_external_manipulation",
            "quantitative_anchor": "Polygonatum downward_vs_upward stigma_pollen_RR=3.80292",
            "direction_hypothesis": "natural_or_protective_orientation_can_improve_effective_pollen_transfer_contextually",
            "cirsium_transport": "hypothesis_only",
            "allowed_current_use": "functional_axis_prior_and_field_manipulation_design",
            "next_decisive_test": "resolve_focal_transition_state_then_manipulate_orientation_with_pollen_transfer_and_seed_output",
        },
        {
            "module": "orientation",
            "function_axis": "abiotic_reproductive_protection",
            "history_recurrence": "robust_lower_bound",
            "history_step_range": "4-6",
            "transition_localization": "weak_no_individually_forced_ML_edge",
            "priority_transition_concepts": "none_branch_specific_yet",
            "functional_evidence_state": "near_ready_mechanism",
            "quantitative_anchor": "Platycodon rain_damage_context_about_30pct_pollen_burst_in_water",
            "direction_hypothesis": "orientation_can_modify_rain_wetting_and_pollen_performance",
            "cirsium_transport": "hypothesis_only",
            "allowed_current_use": "mechanism_specific_exposure_prior",
            "next_decisive_test": "orientation_x_rain_manipulation_with_pollen_viability_and_final_seed_endpoint",
        },
        {
            "module": "orientation",
            "function_axis": "net_reproductive_fitness",
            "history_recurrence": "robust_lower_bound",
            "history_step_range": "4-6",
            "transition_localization": "weak_no_individually_forced_ML_edge",
            "priority_transition_concepts": "none_branch_specific_yet",
            "functional_evidence_state": "ready_candidate_calibration_only",
            "quantitative_anchor": "two_study_fixed_RR=1.4976; random_RR=2.1016; I2=93.57pct",
            "direction_hypothesis": "natural_downward_or_nodding_orientation_often_higher_but_highly_heterogeneous",
            "cirsium_transport": "not_directly_transportable",
            "allowed_current_use": "external_effect_distribution_candidate_not_Cirsium_effect",
            "next_decisive_test": "add_independent_orientation_manipulation_and_focal_Cirsium_net_fitness_test",
        },
        {
            "module": "phyllary_posture",
            "function_axis": "reproductive_enemy_exclusion",
            "history_recurrence": "topology_robust",
            "history_step_range": "3-3",
            "transition_localization": "partly_localizable",
            "priority_transition_concepts": "JPN_36",
            "functional_evidence_state": "mechanism_replicated_not_pool_ready_analog",
            "quantitative_anchor": "Pedicularis drained_bracts_increase_seed_predation; treatment_beta=-0.072_for_intact_coding",
            "direction_hypothesis": "protective_envelope_can_reduce_enemy_access_or_damage_without_increasing_pollinator_visitation",
            "cirsium_transport": "nonhomologous_bract_analog_only",
            "allowed_current_use": "defence_mechanism_hypothesis_and_reverse_design",
            "next_decisive_test": "JPN36_phyllary_access_manipulation_with_enemy_attack_pollinator_access_and_seed_output",
        },
        {
            "module": "phyllary_posture",
            "function_axis": "net_reproductive_fitness",
            "history_recurrence": "topology_robust",
            "history_step_range": "3-3",
            "transition_localization": "JPN36_terminal_forced_in_75.4pct_UFBoot",
            "priority_transition_concepts": "JPN_36",
            "functional_evidence_state": "fitness_direction_supported_not_pool_ready_analog",
            "quantitative_anchor": "Pedicularis intact_water_holding_bracts_higher_final_seed_set; beta=0.025_model_scale",
            "direction_hypothesis": "protective_envelope_can_preserve_final_seed_output_contextually",
            "cirsium_transport": "requires_direct_phyllary_validation",
            "allowed_current_use": "high_information_focal_experiment_prior",
            "next_decisive_test": "measure_JPN36_enemy_exclusion_pollinator_cost_and_final_seed_jointly",
        },
        {
            "module": "stickiness",
            "function_axis": "reproductive_enemy_exclusion",
            "history_recurrence": "robust_lower_bound",
            "history_step_range": "4-5",
            "transition_localization": "partly_localizable",
            "priority_transition_concepts": "JPN_06|JPN_36",
            "functional_evidence_state": "context_discrimination_ready_not_single_loading",
            "quantitative_anchor": "Bejaria intact_sticky florivory_RD=-0.21; Cirsium_discolor_direct_null",
            "direction_hypothesis": "sticky_structures_can_reduce_enemy_damage_in_some_contexts_but_not_universally",
            "cirsium_transport": "direct_Cirsium_null_requires_focal_context_test",
            "allowed_current_use": "competing_benefit_null_context_hypotheses",
            "next_decisive_test": "JPN06_and_JPN36_stickiness_neutralization_with_enemy_access_and_seed_output",
        },
        {
            "module": "stickiness",
            "function_axis": "net_reproductive_fitness",
            "history_recurrence": "robust_lower_bound",
            "history_step_range": "4-5",
            "transition_localization": "JPN06_67pct_and_JPN36_40pct_terminal_forced_UFBoot",
            "priority_transition_concepts": "JPN_06|JPN_36",
            "functional_evidence_state": "context_dependent_unresolved",
            "quantitative_anchor": "Bejaria fruit_set_RR=1.48148_vs_Datura_first_year_seed_cost_about_53pct_and_lambda_cost_13pct",
            "direction_hypothesis": "net_stickiness_fitness_depends_on_enemy_pressure_and_trait_costs",
            "cirsium_transport": "no_generic_sign",
            "allowed_current_use": "model_discrimination_and_negative_control_design",
            "next_decisive_test": "factorial_enemy_exclusion_x_stickiness_neutralization_in_JPN06_JPN36",
        },
        {
            "module": "colour_lightness",
            "function_axis": "Japan_radiation_anti_phylogenetic_recurrence",
            "history_recurrence": "not_supported_in_source_balanced_Japan7",
            "history_step_range": "not_discretized",
            "transition_localization": "not_applicable",
            "priority_transition_concepts": "none_for_rescue_sampling",
            "functional_evidence_state": "separate_functional_questions_only",
            "quantitative_anchor": "Japan7_rho=+0.2675; anti_phylogenetic_negative_tail_p=0.7579",
            "direction_hypothesis": "none_for_recurrence_claim",
            "cirsium_transport": "secondary_negative_module",
            "allowed_current_use": "contrast_module_or_independent_colour_function_question",
            "next_decisive_test": "no_more_sampling_to_rescue_anti_phylogenetic_hypothesis",
        },
    ]

    priorities = [
        {
            "priority_rank": 1,
            "paper_japan_member_id": "JPN_36",
            "taxon": cmap["JPN_36"],
            "role": "transition_localized_discrimination_target",
            "module": "phyllary_posture|stickiness",
            "history_information": "phyllary_terminal_forced_0.754; stickiness_terminal_forced_0.40",
            "functional_question": "protective_envelope_enemy_exclusion_vs_sticky_defence_and_cost",
            "required_next_measurement": "validate_observed_states_then_joint_pollinator_enemy_final_seed_manipulation",
            "field_readiness": "not_established_by_bridge",
            "claim_boundary": "High information conditional on phenotype validation and feasibility; not an adaptation claim.",
        },
        {
            "priority_rank": 2,
            "paper_japan_member_id": "JPN_06",
            "taxon": cmap["JPN_06"],
            "role": "stickiness_transition_discrimination_target",
            "module": "stickiness",
            "history_information": "stickiness_terminal_forced_0.67",
            "functional_question": "Bejaria_like_enemy_benefit_vs_Cirsium_discolor_null_vs_cost",
            "required_next_measurement": "validate_stickiness_then_neutralization_x_enemy_access_x_seed_output",
            "field_readiness": "not_established_by_bridge",
            "claim_boundary": "Strongest current stickiness branch target; functional sign remains open.",
        },
        {
            "priority_rank": 3,
            "paper_japan_member_id": "JPN_34",
            "taxon": cmap["JPN_34"],
            "role": "history_coverage_gap",
            "module": "orientation",
            "history_information": "missing_orientation_primary_state",
            "functional_question": "none_until_state_is_resolved",
            "required_next_measurement": "direct_primary_orientation_state",
            "field_readiness": "not_established_by_bridge",
            "claim_boundary": "Coverage repair, not a functional experiment target yet.",
        },
        {
            "priority_rank": 4,
            "paper_japan_member_id": "JPN_15",
            "taxon": cmap["JPN_15"],
            "role": "history_coverage_gap",
            "module": "phyllary_posture",
            "history_information": "missing_phyllary_primary_state",
            "functional_question": "none_until_state_is_resolved",
            "required_next_measurement": "direct_primary_phyllary_state",
            "field_readiness": "not_established_by_bridge",
            "claim_boundary": "Coverage repair, not a functional experiment target yet.",
        },
        {
            "priority_rank": 5,
            "paper_japan_member_id": "JPN_24",
            "taxon": cmap["JPN_24"],
            "role": "history_coverage_gap",
            "module": "stickiness",
            "history_information": "missing_stickiness_primary_state",
            "functional_question": "none_until_state_is_resolved",
            "required_next_measurement": "direct_primary_stickiness_state",
            "field_readiness": "not_established_by_bridge",
            "claim_boundary": "Coverage repair, not a functional experiment target yet.",
        },
    ]

    write_csv(args.bridge_output, bridge)
    write_csv(args.priority_output, priorities)
    summary = {
        "contract_version": "japan38_module_function_bridge_v1",
        "status_date": "2026-08-27",
        "module_decisions": {
            "orientation": {
                "history_ready": True,
                "function_ready": "calibration_ready",
                "transition_localizable": False,
                "decision": "Repeated orientation history is robust, but branch-specific causal mapping is blocked by weak edge localization. Use external pollination/protection/net-fitness effects as hypotheses, not transported Cirsium effects."
            },
            "phyllary_posture": {
                "history_ready": True,
                "function_ready": "mechanism_and_fitness_direction_ready_analog",
                "transition_localizable": True,
                "best_target": "JPN_36",
                "decision": "Three transitions are topology-robust and JPN36 is the strongest current terminal target. Protective-bract experiments justify enemy-exclusion and seed-fitness hypotheses, but not homology or adaptation."
            },
            "stickiness": {
                "history_ready": True,
                "function_ready": "context_discrimination_ready",
                "transition_localizable": True,
                "best_targets": ["JPN_06", "JPN_36"],
                "decision": "Repeated stickiness history is robust enough for focal tests. Bejaria benefit, Cirsium discolor null and Datura cost prohibit a generic positive defence loading and make focal experiments maximally discriminating."
            },
            "colour_lightness": {
                "history_ready": False,
                "function_ready": "independent_questions_only",
                "transition_localizable": False,
                "decision": "Source-balanced Japan7 rejected the preregistered anti-phylogenetic lightness pattern. Colour is retained as a negative/contrast module rather than rescued by more sampling."
            }
        },
        "highest_information_focal_targets": ["JPN_36", "JPN_06"],
        "coverage_repair_targets": ["JPN_34", "JPN_15", "JPN_24"],
        "next_mainline_action": "Resolve the three missing primary states in parallel, while designing ancestry-aware manipulations for JPN36 phyllary/stickiness and JPN06 stickiness. Do not assign branch-specific orientation function until transition localization improves.",
        "claim_boundary": "Bridge between repeated-history evidence and external functional calibration only. It prioritizes discriminating tests; it does not prove adaptation, causal selection, functional homology, or branch-specific ecological drivers."
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
