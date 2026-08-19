#!/usr/bin/env python3
"""Summarize the post-admission common-locus 294–296 sensitivity matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MODES = ("bwa", "blastx")
SCENARIOS = {
    "ea01_295": ("EA01",),
    "cnipg_295": ("CNIPG",),
    "ea01_cnipg_296": ("EA01", "CNIPG"),
}
EXPECTED_INPUT_CONTRACT = "maximum_public_combined_tree_inputs_v2"
MINIMUM_COMMON_LOCI = 100


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(root: Path) -> dict[str, object]:
    mode_results: dict[str, object] = {}
    overall_pass = True
    common_counts: dict[str, int] = {}

    for mode in MODES:
        mode_root = root / mode
        inputs = load(mode_root / "paired_inputs/combined_input_summary.json")
        if inputs.get("contract_version") != EXPECTED_INPUT_CONTRACT:
            raise ValueError(f"{mode}: unexpected combined input contract")
        if inputs.get("independent_gate_prerequisite_passed") is not True:
            raise ValueError(f"{mode}: independent-gate prerequisite missing")
        if inputs.get("all_four_scenarios_use_identical_locus_set") is not True:
            raise ValueError(f"{mode}: scenario locus sets are not identical")
        if inputs.get("scenario_count") != 4:
            raise ValueError(f"{mode}: expected four scenarios")
        if inputs.get("ea02_enters_combined_tree") is not False:
            raise ValueError(f"{mode}: EA02 entered the combined tree")
        if inputs.get("combined_tree_acceptance_pre_authorized") is not False:
            raise ValueError(f"{mode}: combined input stage pre-authorized acceptance")
        n_common = int(inputs.get("baseline_ea01_cnipg_common_paired_loci", -1))
        minimum = int(inputs.get("minimum_common_loci", -1))
        if minimum < MINIMUM_COMMON_LOCI:
            raise ValueError(f"{mode}: minimum common-locus gate was relaxed below {MINIMUM_COMMON_LOCI}")
        common_counts[mode] = n_common

        scenario_results: dict[str, object] = {}
        mode_pass = n_common >= minimum >= MINIMUM_COMMON_LOCI
        for scenario, candidates in SCENARIOS.items():
            candidate_results: dict[str, object] = {}
            scenario_pass = True
            for candidate in candidates:
                data = load(mode_root / "evaluation" / f"{scenario}_{candidate}_concat.json")
                candidate_pass = (
                    int(data.get("shared_baseline_focal_tips", -1)) == 294
                    and int(data.get("unrooted_rf_distance_on_shared_baseline_tips", -1)) == 0
                    and data.get("exact_shared_tip_backbone_invariance") is True
                    and data.get("same_taxon_among_nearest_baseline_tips") is True
                )
                candidate_results[candidate] = {
                    "passed": candidate_pass,
                    "shared_baseline_focal_tips": data.get("shared_baseline_focal_tips"),
                    "rf": data.get("unrooted_rf_distance_on_shared_baseline_tips"),
                    "same_taxon_neighbor": data.get("same_taxon_among_nearest_baseline_tips"),
                    "nearest_baseline_tip_ids": data.get("candidate_nearest_baseline_tip_ids", []),
                }
                scenario_pass = scenario_pass and candidate_pass

            astral = load(mode_root / "evaluation" / f"{scenario}_astral_backbone.json")
            astral_pass = (
                int(astral.get("unrooted_rf_distance_on_shared_species", -1)) == 0
                and astral.get("exact_shared_species_backbone_invariance") is True
            )
            scenario_pass = scenario_pass and astral_pass
            scenario_results[scenario] = {
                "passed": scenario_pass,
                "candidate_results": candidate_results,
                "astral_passed": astral_pass,
                "astral_rf": astral.get("unrooted_rf_distance_on_shared_species"),
            }
            mode_pass = mode_pass and scenario_pass

        mode_results[mode] = {
            "passed": mode_pass,
            "baseline_ea01_cnipg_common_paired_loci": n_common,
            "minimum_common_loci": minimum,
            "scenarios": scenario_results,
        }
        overall_pass = overall_pass and mode_pass

    return {
        "contract_version": "maximum_public_combined_sensitivity_summary_v2",
        "accepted_primary_before_combined_gate": 294,
        "candidate_ids": ["EA01", "CNIPG"],
        "excluded_duplicate_controls": ["EA02"],
        "mapping_modes": list(MODES),
        "baseline_ea01_cnipg_common_paired_loci_by_mode": common_counts,
        "mode_results": mode_results,
        "all_modes_all_subset_scenarios_passed": overall_pass,
        "combined_296_sample_tree_acceptance_allowed": overall_pass,
        "resulting_sample_level_tip_count_if_accepted": 296 if overall_pass else 294,
        "new_analysis_taxon_labels_added_if_accepted": 0,
        "ea02_enters_biological_tree_inputs": False,
        "new_china_sampling_freeze_allowed": False,
        "flower_colour_history_claim_changed_by_this_gate": False,
        "manual_review_required": not overall_pass,
        "claim_boundary": (
            "This gate can accept a 296-sample public nuclear sensitivity state only after EA01 and CNIPG pass "
            "independently and all common-locus subset/backbone checks pass under both baseline mapping modes. "
            "EA02 remains excluded as a duplicate-readset control. Any failure keeps the accepted primary at 294."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--root", type=Path, required=True); p.add_argument("--output", type=Path, required=True); a = p.parse_args()
    result = summarize(a.root); a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); print(json.dumps(result, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
