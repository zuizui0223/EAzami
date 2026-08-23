from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/doctoral_global_to_east_asia_evidence_ladder_v2.csv"
OUTPUT = ROOT / "data/evidence/doctoral_global_to_east_asia_summary_v2.json"

REQUIRED_IDS = [f"L{i}" for i in range(10)]
REQUIRED_COLUMNS = {
    "order_id", "scope", "module", "question_or_prior_hypothesis",
    "meta_or_literature_result", "meta_status", "azami_self_analysis",
    "eazami_self_analysis", "current_conclusion", "new_hypothesis_or_prediction",
    "existing_data_can_still_resolve", "doctoral_empirical_requirement",
    "doctoral_issue_gate", "claim_boundary",
}


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError("Evidence ladder has no header")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise RuntimeError(f"Evidence ladder missing columns: {sorted(missing)}")
        return [{k: str(v or "").strip() for k, v in row.items()} for row in reader]


def main() -> None:
    rows = read_rows()
    ids = [r["order_id"] for r in rows]
    if ids != REQUIRED_IDS:
        raise RuntimeError(f"Unexpected evidence-ladder order/coverage: {ids}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate evidence-ladder IDs")
    for row in rows:
        for key in REQUIRED_COLUMNS:
            if not row[key]:
                raise RuntimeError(f"{row['order_id']} missing {key}")

    by_id = {r["order_id"]: r for r in rows}

    # Azami boundary must remain observational.
    l0 = by_id["L0"]
    if "Azami is observational phenomics" not in l0["claim_boundary"]:
        raise RuntimeError("Azami observational boundary lost")
    if "no genetic variance" not in l0["claim_boundary"]:
        raise RuntimeError("Azami causal overclaim guard lost")

    # Meta-analysis decisions.
    if by_id["L2"]["meta_status"] != "resolved_general_pressure":
        raise RuntimeError("Antagonist pressure status drifted")
    if "RR=2.674" not in by_id["L2"]["meta_or_literature_result"]:
        raise RuntimeError("Antagonist RR drifted")
    if "selection mosaic" not in by_id["L1"]["current_conclusion"].lower():
        raise RuntimeError("Selection-mosaic conclusion lost")
    if by_id["L6"]["meta_status"] != "weakened_general_hypothesis":
        raise RuntimeError("Generic stickiness defence must remain weakened")

    # Current self-analysis conclusions.
    if "minimum of 5 orientation changes" not in by_id["L3"]["eazami_self_analysis"]:
        raise RuntimeError("Orientation repeated-state result drifted")
    if "parallel/convergent adaptation is not yet established" not in by_id["L3"]["claim_boundary"]:
        raise RuntimeError("Orientation overclaim guard lost")
    if "C=17/W=3" not in by_id["L4"]["eazami_self_analysis"]:
        raise RuntimeError("Colour state gate drifted")
    if "regain" not in by_id["L4"]["claim_boundary"].lower():
        raise RuntimeError("Colour regain boundary lost")
    if "common-lability" not in by_id["L8"]["new_hypothesis_or_prediction"]:
        raise RuntimeError("Competing common-lability model lost")
    if "adaptive radiation" not in by_id["L8"]["claim_boundary"].lower():
        raise RuntimeError("Adaptive-radiation boundary lost")

    summary = {
        "version": "v2_evidence_ladder",
        "status_date": "2026-08-23",
        "evidence_ladder_rows": 10,
        "architecture": [
            "Azami global observational phenomics",
            "EAzami quantitative ecological literature synthesis",
            "EAzami East-Asian rapid-radiation evolutionary-history zoom",
            "Doctoral ancestry-resolved ecological function tests",
            "Flower-colour molecular reuse test",
        ],
        "meta_conclusions": {
            "single_universal_driver": "not_supported_as_general_model",
            "selection_mosaic": "working_general_support",
            "reproductive_antagonist_pressure": "resolved_general_pressure_RR_2.674_CI_2.388_2.993",
            "reproductive_assurance_and_demographic_gating": "working_support",
            "stickiness_general_defence": "weakened",
            "display_tradeoff": "working_mechanistic_support",
            "orientation_timing_protection": "mechanistic_candidate",
            "phyllary_spine_defence": "mechanistic_candidate_requires_direct_validation",
        },
        "self_analysis_resolutions": {
            "azami": "large_below_taxon_visible_variance_and_trait_specific_environmental_structure_without_causal_claim",
            "east_asia_tree": "accepted_153_locus_branch_length_framework_with_six_topology_uncertainty_set",
            "orientation": "minimum_five_state_changes_on_all_six_topologies_direction_and_ancestor_unresolved",
            "colour": "C17_W3_tree_ready_fixed_white_breadth_and_rate_identifiability_still_block_loss_vs_regain",
        },
        "central_hypothesis": "semi_independent_capitulum_modules_redeployed_across_local_selection_mosaics_during_young_East_Asian_radiation",
        "competing_hypothesis": "shared_common_lability_axis",
        "multiscale_prediction": "within_population_selection_mosaics_and_ancestry_linked_variation_connect_to_repeated_among_lineage_states",
        "doctoral_frontier": {
            "Aim1": "population_and_voucher_validated_transition_history_with_nuclear_ancestry_plastid_and_cytotype",
            "Aim2": "trait_to_pollination_protection_antagonism_to_filled_achene_causal_tests",
            "Aim3": "at_least_two_independent_colour_transitions_with_haplotype_floral_RNA_pigment_and_colour",
            "adaptive_radiation_gate": "requires_causal_trait_mechanism_reproductive_fitness_link",
        },
        "generic_meta_stop_rule": "reopen_only_for_prespecified_homologous_estimand_or_study_that_changes_a_focal_mechanism_or_sampling_decision",
    }
    OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
