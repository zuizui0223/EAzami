#!/usr/bin/env python3
"""Integrate current ASR and full-occurrence niche evidence into a sampling decision gate.

The gate is intentionally conservative: it identifies whether current evidence requires
new populations now, can position already-existing population slots, or only creates a
conditional future addition after another discriminator is observed.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run(asr_path: Path, niche_path: Path, manifest_path: Path):
    asr = json.loads(asr_path.read_text(encoding="utf-8"))
    niche = load_csv(niche_path)
    manifest = load_csv(manifest_path)
    by_taxon = {r["taxon"]: r for r in niche}
    by_pid = {r["population_id"]: r for r in manifest}

    pair_states = set(asr["pair_only"]["optimal_arenicola_mrca_states"].split("|"))
    if pair_states != {"C", "W"}:
        raise ValueError(f"Arenicola pair is no longer exactly ambiguous: {pair_states}")
    sister = asr["published_sister_context"]
    if int(sister["white_ancestor_penalty_changes"]) != 1:
        raise ValueError("Expected one-step sister-context preference")
    if sister["force_white_deep_root_arenicola_mrca"] != "W":
        raise ValueError("Deep-root sensitivity no longer reverses Arenicola state")

    total_core = sum(int(r["minimum_individuals"]) for r in manifest)
    if total_core != 190:
        raise ValueError(f"Core manifest no longer sums to 190: {total_core}")

    for taxon in ["Cirsium brevicaule", "Cirsium irumtiense", "Cirsium pendulum"]:
        if int(by_taxon[taxon]["niche_cluster_gap"] or 0) != 0:
            raise ValueError(f"Unexpected immediate niche coverage gap for {taxon}")

    sieb_gap = int(by_taxon["Cirsium sieboldii"]["niche_cluster_gap"] or 0)
    if sieb_gap <= 0 or by_taxon["Cirsium sieboldii"]["morph_linkage_required"] != "yes":
        raise ValueError("Expected a conditional morph-linked C. sieboldii replication gap")

    return {
        "contract_version": "doctoral_sampling_information_gate_v1",
        "status_date": "2026-08-21",
        "current_core_individuals": 190,
        "immediate_new_population_additions": [],
        "immediate_decision": "keep_core190_no_new_population_count",
        "existing_slot_repositioning": [
            {
                "population_id": "P003",
                "required_region": by_pid["P003"]["required_region"],
                "reason": "full_occurrence_niche_bridge_coverage",
            },
            {
                "population_id": "P004",
                "required_region": by_pid["P004"]["required_region"],
                "reason": "full_occurrence_niche_bridge_coverage",
            },
        ],
        "asr_gate": {
            "pair_only_direction": "unresolved_loss_vs_regain_tie",
            "current_sister_context": "coloured_Arenicola_MRCA_preferred_by_one_parsimony_step",
            "root_sensitivity": "forcing_white_deep_root_reverses_Arenicola_MRCA_to_white",
            "sampling_implication": "do_not_add_focal_population_count_to_solve_deep_ASR_polarity",
            "higher_value_next_information": [
                "trusted_branch_length_nuclear_topology_ensemble",
                "broader_source_backed_colour_states_in_Arenicola_sister_and_adjacent_East_Asian_lineages",
            ],
            "role_of_P001_P008": "resolve_population_origin_alternatives_standing_variation_vs_introgression_vs_lineage_specific_change_not_deep_root_state",
        },
        "niche_gate": {
            "Cirsium_brevicaule": "four_planned_populations_cover_major_public_niche_strata_and_P003_P004_are_now_positioned",
            "Cirsium_irumtiense": "four_planned_populations_match_four_diagnostic_strata_but_coordinate_quality_requires_field_verification",
            "Cirsium_pendulum": "four_planned_populations_match_four_diagnostic_strata_morph_linkage_is_next_gate",
            "Cirsium_sieboldii": "two_planned_populations_underrepresent_full_occurrence_niche_structure_but_morph_linkage_is_missing",
        },
        "conditional_additions": [
            {
                "taxon": "Cirsium sieboldii",
                "trigger": "verified_W_C_populations_show_P013_P014_do_not_span_an_independent_niche_context_replicate",
                "action": "add_second_matched_white_coloured_population_pair",
                "additional_populations_if_triggered": 2,
                "additional_individuals_if_triggered": 30,
                "status": "conditional_not_added_now",
            }
        ],
        "conditional_controls": [
            {"taxon": "Cirsium lineare", "minimum_individuals_if_activated": 16, "status": "unchanged_conditional_control"},
            {"taxon": "Cirsium dipsacolepis", "minimum_individuals_if_activated": 16, "status": "unchanged_conditional_control"},
        ],
        "next_information_order": [
            "verify_P003_P004_extant_populations_within_the_two_ranked_region_strata",
            "link_pendulum_and_sieboldii_white_coloured_populations_to_occurrence_niche_space",
            "recover_trusted_branch_length_tree_and_broaden_colour_atlas_for_full_ASR",
            "only_then_recompute_composite_sample_value_with_ASR_trait_ancestry_components",
        ],
        "claim_boundary": "The gate distinguishes deep ancestral-state polarity from population-origin inference. Niche coverage can position existing field slots but cannot substitute for ancestry or morph linkage. No new population count is added until a declared conditional trigger is observed.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--asr", type=Path, required=True)
    p.add_argument("--niche", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = run(a.asr, a.niche, a.manifest)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
