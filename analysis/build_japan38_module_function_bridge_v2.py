#!/usr/bin/env python3
"""Build the state-aware Japan38 repeated-history -> function bridge v2.

v2 corrects the intervention direction after auditing focal observed states. JPN06
and JPN36 are nonsticky/nearly nonsticky, while JPN15 is sticky and is the strongly
supported sister of JPN06 on the canonical ML tree. Therefore sticky neutralization
belongs on JPN15, whereas any restoration/addition test on JPN06 is a separate
sufficiency experiment requiring material-equivalence validation.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    for name in ["history","functional-summary","functional-seed","orientation-meta","cirsium-interactions","concept-map","trait-seed","tree","readiness"]:
        p.add_argument("--"+name, type=Path, required=True)
    p.add_argument("--bridge-output",type=Path,required=True)
    p.add_argument("--priority-output",type=Path,required=True)
    p.add_argument("--summary-output",type=Path,required=True)
    a=p.parse_args()

    history=json.loads(a.history.read_text())
    fsum=json.loads(a.functional_summary.read_text())
    ometa=json.loads(a.orientation_meta.read_text())
    readiness=json.loads(a.readiness.read_text())
    seed={r["study_id"]:r for r in read_csv(a.functional_seed)}
    interactions={r["evidence_id"]:r for r in read_csv(a.cirsium_interactions)}
    cmap={r["paper_japan_member_id"]:r for r in read_csv(a.concept_map)}
    traits={r["paper_japan_member_id"]:r for r in read_csv(a.trait_seed)}
    tree_text=a.tree.read_text().strip()

    mh=history["minimum_change_history"]; loc=history["transition_identifiability"]
    assert mh["orientation"]["resolved_concepts"]==19 and mh["orientation"]["ml_minimum_unordered_steps"]==6
    assert [mh["orientation"]["ufboot1000_steps_min"],mh["orientation"]["ufboot1000_steps_max"]]==[4,6]
    assert mh["orientation"]["ufboot_root_U_fraction"]==1.0
    assert mh["phyllary_posture"]["resolved_concepts"]==10 and mh["phyllary_posture"]["ufboot1000_steps_min"]==3 and mh["phyllary_posture"]["ufboot1000_steps_max"]==3
    assert mh["stickiness"]["resolved_concepts"]==12 and [mh["stickiness"]["ufboot1000_steps_min"],mh["stickiness"]["ufboot1000_steps_max"]]==[4,5]
    assert loc["orientation"]["ml_individually_forced_change_edges"]==0
    assert abs(loc["phyllary_posture"]["JPN_36_ufboot_forced_fraction"]-0.754)<1e-12
    assert abs(loc["stickiness"]["JPN_06_ufboot_forced_fraction"]-0.67)<1e-12
    assert abs(loc["stickiness"]["JPN_36_ufboot_forced_fraction"]-0.40)<1e-12

    assert traits["JPN_06"]["stickiness_state"]=="nonsticky_or_nearly_nonsticky"
    assert traits["JPN_15"]["stickiness_state"]=="sticky"
    assert traits["JPN_36"]["stickiness_state"]=="nonsticky_or_nearly_nonsticky"
    assert traits["JPN_36"]["phyllary_posture"]=="appressed"
    assert traits["JPN_06"]["authority_match_status"]=="exact_authority_concept_match"
    assert traits["JPN_15"]["authority_match_status"]=="exact_authority_concept_match"
    assert traits["JPN_36"]["authority_match_status"]=="exact_authority_concept_match"

    sister_pattern=r"\((?:J38S006:[^,]+,J38S015:[^)]+|J38S015:[^,]+,J38S006:[^)]+)\)100/100:"
    assert re.search(sister_pattern,tree_text), "JPN06/JPN15 100/100 sister relationship changed"
    assert cmap["JPN_06"]["tip_ids"]=="J38S006" and cmap["JPN_15"]["tip_ids"]=="J38S015"

    mods=fsum["modules"]
    assert mods["orientation"]["rows"]==11 and mods["orientation"]["quantitative_ready_rows"]==8
    assert mods["bract_defence"]["quantitative_ready_rows"]==3
    assert mods["stickiness"]["quantitative_ready_rows"]==2
    assert ometa["k"]==2 and abs(ometa["fixed_effect"]["RR"]-1.497566445)<1e-10
    assert abs(ometa["heterogeneity"]["I2_percent"]-93.5714188738)<1e-10
    for sid in ["POLY_ORIENT_POLLEN_01","PLAT_ORIENT_RAIN_01","PED_BR_POLL_01","PED_BR_FINALSET_01","PED_BR_PRED_01","BEJ_STICK_FLORIV_01","BEJ_STICK_FRUIT_01","DAT_STICK_COST_01","DAT_STICK_LAMBDA_01"]:
        assert sid in seed
    assert interactions["INT006"]["taxon"]=="Cirsium discolor" and interactions["INT006"]["direction"]=="null"
    assert readiness["colour"]["mainline_role"]=="secondary_negative_module_not_primary_recurrence_evidence"

    common={"history_to_function_status":"hypothesis_bridge_not_adaptation"}
    bridge=[
      {**common,"module":"orientation","function_axis":"effective_pollination","history_step_range":"4-6","transition_localization":"weak_no_forced_ML_edge","focal_observed_state":"no_branch_specific_focal_state","matched_comparator":"none_yet","functional_evidence_state":"near_ready_external_manipulation","quantitative_anchor":"Polygonatum downward_vs_upward stigma_pollen_RR=3.80292","direction_hypothesis":"orientation_can_improve_effective_pollen_transfer_contextually","allowed_use":"preregister_mediator_endpoint","next_test":"resolve_transition_branch_then_manipulate_orientation_and_measure_effective_transfer_plus_seed"},
      {**common,"module":"orientation","function_axis":"abiotic_reproductive_protection","history_step_range":"4-6","transition_localization":"weak_no_forced_ML_edge","focal_observed_state":"no_branch_specific_focal_state","matched_comparator":"none_yet","functional_evidence_state":"near_ready_mechanism","quantitative_anchor":"Platycodon rain_damage_context_about_30pct_pollen_burst_in_water","direction_hypothesis":"orientation_can_modify_rain_wetting_and_pollen_performance","allowed_use":"preregister_rain_protection_endpoint","next_test":"orientation_x_rain_factorial_with_pollen_performance_and_final_seed"},
      {**common,"module":"orientation","function_axis":"net_reproductive_fitness","history_step_range":"4-6","transition_localization":"weak_no_forced_ML_edge","focal_observed_state":"no_branch_specific_focal_state","matched_comparator":"none_yet","functional_evidence_state":"calibration_ready_not_transportable","quantitative_anchor":"two_study_fixed_RR=1.4976; random_RR=2.1016; I2=93.57pct","direction_hypothesis":"natural_or_protective_orientation_often_higher_but_heterogeneous","allowed_use":"external_effect_distribution_only","next_test":"add_independent_orientation_manipulation_and_focal_Cirsium_net_fitness"},
      {**common,"module":"phyllary_posture","function_axis":"reproductive_enemy_exclusion","history_step_range":"3-3","transition_localization":"JPN36_terminal_forced_0.754","focal_observed_state":"JPN36_appressed","matched_comparator":"none_ancestry_matched_yet","functional_evidence_state":"mechanism_replicated_not_pool_ready_analog","quantitative_anchor":"Pedicularis drainage: pollinator_visit_null; intact_coding seed_predation_beta=-0.072","direction_hypothesis":"protective_envelope_can_reduce_enemy_access_without_pollinator_gain","allowed_use":"defence_tradeoff_hypothesis","next_test":"pilot_damage_free_JPN36_phyllary_access_manipulation_vs_sham_then_enemy_pollinator_seed_endpoints"},
      {**common,"module":"phyllary_posture","function_axis":"net_reproductive_fitness","history_step_range":"3-3","transition_localization":"JPN36_terminal_forced_0.754","focal_observed_state":"JPN36_appressed","matched_comparator":"none_ancestry_matched_yet","functional_evidence_state":"fitness_direction_supported_not_pool_ready_analog","quantitative_anchor":"Pedicularis intact_bracts higher final_seed_set beta=0.025_model_scale","direction_hypothesis":"protective_envelope_can_preserve_seed_output_contextually","allowed_use":"high_information_focal_experiment_prior","next_test":"JPN36_joint_enemy_exclusion_pollinator_access_and_viable_seed_measurement"},
      {**common,"module":"stickiness","function_axis":"reproductive_enemy_exclusion","history_step_range":"4-5","transition_localization":"JPN06_terminal_forced_0.67; JPN36_terminal_forced_0.40","focal_observed_state":"JPN06_nonsticky; JPN36_nonsticky","matched_comparator":"JPN15_sticky_sister_of_JPN06_ML_100/100","functional_evidence_state":"context_discrimination_ready_no_single_loading","quantitative_anchor":"Bejaria florivory_RD=-0.21; direct_Cirsium_discolor_null","direction_hypothesis":"sticky_structures_can_reduce_enemy_damage_in_some_contexts_but_not_universally","allowed_use":"benefit_vs_null_vs_cost_model_discrimination","next_test":"JPN15_sticky_neutralization_vs_sham_for_necessity; optional_JPN06_adhesive_restoration_only_after_material_equivalence_validation"},
      {**common,"module":"stickiness","function_axis":"net_reproductive_fitness","history_step_range":"4-5","transition_localization":"JPN06_terminal_forced_0.67; JPN36_terminal_forced_0.40","focal_observed_state":"JPN06_nonsticky; JPN36_nonsticky","matched_comparator":"JPN15_sticky_sister_of_JPN06_ML_100/100","functional_evidence_state":"context_dependent_unresolved","quantitative_anchor":"Bejaria fruit_set_RR=1.48148 vs Datura seed_cost_about_53pct and lambda_cost_13pct","direction_hypothesis":"net_stickiness_fitness_depends_on_enemy_pressure_and_trait_cost","allowed_use":"competing_fitness_models","next_test":"JPN15_neutralization_x_enemy_exclusion_with_pollinator_and_viable_seed_endpoints; JPN06_restoration_is_secondary_sufficiency_test"},
      {**common,"module":"colour_lightness","function_axis":"Japan_radiation_anti_phylogenetic_recurrence","history_step_range":"not_discretized","transition_localization":"not_applicable","focal_observed_state":"source_balanced_Japan7","matched_comparator":"not_applicable","functional_evidence_state":"secondary_negative_contrast","quantitative_anchor":"Japan7_rho=+0.2675; preregistered_negative_tail_p=0.7579","direction_hypothesis":"none_for_recurrence_claim","allowed_use":"independent_colour_function_or_molecular_question_only","next_test":"no_sampling_to_rescue_anti_phylogenetic_hypothesis"},
    ]

    priorities=[
      {"priority_rank":1,"paper_japan_member_id":"JPN_06","taxon":cmap["JPN_06"]["paper_taxon_concept"],"matched_comparator":"JPN_15","comparator_taxon":cmap["JPN_15"]["paper_taxon_concept"],"role":"ancestry_matched_stickiness_transition_test","module":"stickiness","observed_state":"nonsticky_or_nearly_nonsticky","comparator_state":"sticky","history_information":"JPN06_terminal_forced_0.67; JPN06-JPN15_ML_sisters_100/100","required_next_measurement":"JPN15_sticky_neutralization_vs_sham; enemy_access; pollinator_effective_transfer; mature_viable_seed; optional_JPN06_restoration_after_material_validation","field_readiness":"not_established","claim_boundary":"Matched sister contrast strengthens design but species contrast alone is not causal; manipulation supplies causal test."},
      {"priority_rank":2,"paper_japan_member_id":"JPN_36","taxon":cmap["JPN_36"]["paper_taxon_concept"],"matched_comparator":"none","comparator_taxon":"none","role":"phyllary_transition_function_test","module":"phyllary_posture","observed_state":"appressed","comparator_state":"none","history_information":"JPN36_phyllary_terminal_forced_0.754; stickiness_secondary_0.40","required_next_measurement":"damage_free_phyllary_access_manipulation_or_mechanical_access_proxy_vs_sham; enemy_attack; pollinator_access; mature_viable_seed","field_readiness":"not_established","claim_boundary":"Strong transition localization; protective-bract evidence is analogical, not homologous proof."},
      {"priority_rank":3,"paper_japan_member_id":"JPN_34","taxon":cmap["JPN_34"]["paper_taxon_concept"],"matched_comparator":"none","comparator_taxon":"none","role":"history_coverage_gap","module":"orientation","observed_state":"missing_primary","comparator_state":"none","history_information":"missing_orientation_primary_state","required_next_measurement":"direct_primary_orientation_state","field_readiness":"not_established","claim_boundary":"Coverage repair before branch-specific orientation experiment selection."},
      {"priority_rank":4,"paper_japan_member_id":"JPN_15","taxon":cmap["JPN_15"]["paper_taxon_concept"],"matched_comparator":"JPN_06","comparator_taxon":cmap["JPN_06"]["paper_taxon_concept"],"role":"stickiness_comparator_plus_phyllary_coverage_gap","module":"stickiness|phyllary_posture","observed_state":"sticky; phyllary_missing_primary","comparator_state":"JPN06_nonsticky","history_information":"JPN06-JPN15_ML_sisters_100/100; JPN15_phyllary_missing","required_next_measurement":"sticky_neutralization_experiment_and_direct_primary_phyllary_state","field_readiness":"not_established","claim_boundary":"Sticky comparator is useful now; missing phyllary state remains separate coverage task."},
      {"priority_rank":5,"paper_japan_member_id":"JPN_24","taxon":cmap["JPN_24"]["paper_taxon_concept"],"matched_comparator":"none","comparator_taxon":"none","role":"history_coverage_gap","module":"stickiness","observed_state":"missing_primary","comparator_state":"none","history_information":"missing_stickiness_primary_state","required_next_measurement":"direct_primary_stickiness_state","field_readiness":"not_established","claim_boundary":"Coverage repair, not a functional target yet."},
    ]
    write_csv(a.bridge_output,bridge); write_csv(a.priority_output,priorities)
    summary={
      "contract_version":"japan38_module_function_bridge_v2","status_date":"2026-08-27",
      "state_direction_correction":{"reason":"JPN06 and JPN36 are observed nonsticky/nearly nonsticky, so neutralization cannot be the focal intervention on them.","JPN06_state":"nonsticky_or_nearly_nonsticky","JPN15_state":"sticky","JPN36_stickiness_state":"nonsticky_or_nearly_nonsticky","JPN36_phyllary_state":"appressed","JPN06_JPN15_sister_support":"100/100_on_canonical_ML_tree"},
      "module_decisions":{
        "orientation":{"history_ready":True,"function_ready":"calibration_ready","transition_localizable":False,"decision":"Keep functional endpoint priors but block named-branch adaptation until transition localization improves."},
        "phyllary_posture":{"history_ready":True,"function_ready":"analog_mechanism_and_fitness_direction_ready","transition_localizable":True,"best_target":"JPN_36","decision":"JPN36 appressed phyllaries are the strongest current transition-localized phyllary target; first prove a damage-free manipulation."},
        "stickiness":{"history_ready":True,"function_ready":"context_discrimination_ready","transition_localizable":True,"best_ancestry_matched_pair":["JPN_06","JPN_15"],"secondary_target":"JPN_36","decision":"Use sticky JPN15 neutralization as the primary necessity experiment and JPN06 nonsticky restoration only as a separately validated sufficiency test."},
        "colour_lightness":{"history_ready":False,"function_ready":"independent_questions_only","transition_localizable":False,"decision":"Retain as negative/contrast module; no rescue sampling."}
      },
      "highest_information_design":"JPN06 nonsticky vs JPN15 sticky sister pair, with within-JPN15 sticky neutralization as the primary causal test.",
      "next_mainline_action":"First verify field feasibility and live phenotype expression for JPN06/JPN15 and JPN36. In parallel repair JPN34 orientation, JPN15 phyllary and JPN24 stickiness primary states. Then run JPN15 stickiness-neutralization and JPN36 phyllary-access pilot only if manipulation/sham quality gates pass.",
      "claim_boundary":"State-aware experiment prioritization only. Sister-state contrast is not causal by itself; external function evidence is calibration, not a transported Cirsium effect or adaptation proof."
    }
    a.summary_output.parent.mkdir(parents=True,exist_ok=True); a.summary_output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
