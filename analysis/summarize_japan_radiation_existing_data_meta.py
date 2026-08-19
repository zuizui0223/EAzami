#!/usr/bin/env python3
"""Summarize the existing-data ceiling for the Japanese Cirsium radiation.

This script intentionally reports descriptive/meta-analytic evidence only. It does
not estimate diversification or trait-evolutionary rates before an accepted
branch-length nuclear topology ensemble exists.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def yes(value: str) -> bool:
    return str(value).strip().lower() == "yes"


def build_summary(root: Path) -> dict[str, Any]:
    evidence = root / "data" / "evidence"
    origin = read_json(evidence / "japan_cirsium_origin_meta_analysis_v1.json")
    hmm2 = read_csv(evidence / "hmm2_population_aware_transition_testability_v1.csv")
    cytotypes = read_csv(evidence / "hmm3_japan_radiation_focal_cytotypes_v1.csv")
    azami = read_json(evidence / "azami_ch1_macro_trait_snapshot_v1.json")
    ladder = read_csv(evidence / "japan_adaptive_radiation_evidence_ladder_v1.csv")

    dominant = int(origin["dominant_main_radiation"]["species_in_main_radiation"])
    sampled = int(origin["dominant_main_radiation"]["japanese_species_sampled"])
    exceptions = sampled - dominant

    lineare = origin["cirsium_lineare"]
    dipsa = origin["cirsium_dipsacolepis"]

    compressed = sum(yes(row["stage_a_state_compression"]) for row in hmm2)
    count_testable = sum(yes(row["stage_b_transition_count_testable"]) for row in hmm2)
    rate_testable = sum(yes(row["stage_c_transition_rate_testable"]) for row in hmm2)
    morph_linked_systems = sum(int(row["morph_linked_nuclear_samples"] or 0) > 0 for row in hmm2)
    tak = next(row for row in hmm2 if row["system"] == "TAK")

    dominant_cytotypes = [
        row for row in cytotypes
        if row["japan_origin_role"] == "dominant_main_japanese_radiation"
    ]
    ploidy_values = sorted({int(row["ploidy_x"]) for row in dominant_cytotypes if row["ploidy_x"]})
    all_ploidy_values = sorted({int(row["ploidy_x"]) for row in cytotypes if row["ploidy_x"]})

    status_counts = Counter(row["current_status"] for row in ladder)

    return {
        "contract_version": "japan_radiation_existing_data_meta_v1",
        "date": "2026-08-16",
        "scope": "descriptive_meta_analysis_before_accepted_294_296_branch_length_tree",
        "radiation_success_asymmetry": {
            "japanese_taxa_sampled": sampled,
            "dominant_radiation_sampled_taxa": dominant,
            "sampled_exceptions": exceptions,
            "dominant_fraction": dominant / sampled,
            "dominant_to_all_exceptions_sampled_richness_ratio": dominant / exceptions,
            "point_hypothesis_sample_occupancy": [dominant, 1, 1],
            "point_hypothesis_note": (
                "36:1:1 is descriptive occupancy of the currently sampled Japanese taxon concepts "
                "under the 3-history point hypothesis, not an age-corrected diversification rate."
            ),
            "lineare_analysis_support": [
                int(lineare["analyses_supporting"]), int(lineare["analyses_tested"])
            ],
            "lineare_independent_group_support": [
                int(lineare["data_generation_groups_supporting"]),
                int(lineare["data_generation_groups_tested"]),
            ],
            "dipsacolepis_independent_groups": int(dipsa["data_generation_groups_tested"]),
            "inference": "strong_descriptive_radiation_success_asymmetry_not_yet_rate_comparison",
        },
        "population_trait_resolution": {
            "reviewed_polymorphic_systems": len(hmm2),
            "systems_with_species_tip_state_compression": compressed,
            "morph_genotype_linked_systems": morph_linked_systems,
            "morph_genotype_linkage_fraction": morph_linked_systems / len(hmm2),
            "transition_count_testable_systems": count_testable,
            "transition_rate_testable_systems": rate_testable,
            "takaoense_species_tip_min_transitions": int(tak["species_tip_min_transitions"]),
            "takaoense_population_aware_min_transitions": int(tak["population_aware_min_transitions"]),
            "takaoense_transition_count_delta": int(tak["delta_min_transitions"]),
            "takaoense_minimum_count_ratio": (
                int(tak["population_aware_min_transitions"])
                / int(tak["species_tip_min_transitions"])
            ),
            "inference": "species_tip_coding_under_resolves_recent_colour_state_history_but_rate_inflation_is_unreplicated",
        },
        "cytogenetic_scope": {
            "focal_taxon_records": len(cytotypes),
            "dominant_radiation_focal_records": len(dominant_cytotypes),
            "dominant_radiation_observed_ploidy_levels": ploidy_values,
            "all_focal_observed_ploidy_levels": all_ploidy_values,
            "dominant_radiation_observed_ploidy_level_count": len(ploidy_values),
            "inference": (
                "multiple ploidy states are already documented within focal dominant-radiation taxa, "
                "but this sparse taxon-level audit cannot estimate ploidy-transition density or causation"
            ),
        },
        "macro_trait_scope": {
            "azami_taxa": int(azami["dataset"]["n_taxa"]),
            "azami_observations": int(azami["dataset"]["n_observations"]),
            "azami_heads": int(azami["dataset"]["n_heads"]),
            "azami_endpoints": int(azami["dataset"]["n_endpoints"]),
            "within_assigned_species_fraction_range": azami["nested_visible_variance"]["within_assigned_species_fraction_range"],
            "one_head_per_photo_fraction_range": azami["nested_visible_variance"]["one_head_per_photo_within_fraction_range"],
            "noise_adjusted_cross_scale_rho": azami["precision_aware_cross_scale_result"]["noise_adjusted_variation_association_spearman_rho"],
            "noise_adjusted_cross_scale_ci95": azami["precision_aware_cross_scale_result"]["species_bootstrap_ci95"],
            "hierarchical_cross_scale_effect": azami["precision_aware_cross_scale_result"]["hierarchical_log_variance_change_per_sd_visible_variation"],
            "hierarchical_cross_scale_p": azami["precision_aware_cross_scale_result"]["hierarchical_likelihood_ratio_p_value"],
            "inference": "large_visible_disparity_exists_but_does_not_yet_measure_evolutionary_rate_or_adaptation",
        },
        "evidence_ladder_status_counts": dict(sorted(status_counts.items())),
        "existing_data_ceiling": {
            "can_test_after_current_heavy_tree_without_new_biological_sampling": [
                "age_and_sampling_aware_radiation_success_asymmetry",
                "branch_length_and_internode_compression",
                "gene_tree_discordance_or_concordance_metrics_where_gene_trees_are_recoverable",
                "Azami_to_EAzami_trait_tip_bridge_for_colour_orientation_outline_and_existing_involucre_spine_proxies",
                "public_occurrence_niche_divergence_across_dominant_and_secondary_histories",
                "radiation_level_trait_disparity_and_transition_history_across_topology_ensemble",
                "descriptive_literature_mapped_ploidy_and_genome_size_sensitivity",
            ],
            "cannot_resolve_without_new_population_or_experimental_data": [
                "replicated_population_aware_colour_transition_rates_beyond_takaoense",
                "standing_variation_vs_introgression_for_pendulum_sieboldii_and_Arenicola",
                "population_cytotype_distribution_and_ploidy_aware_local_ancestry",
                "causal_trait_environment_fitness_links_required_for_adaptive_radiation",
                "replicated_genotype_to_floral_expression_to_pigment_to_phenotype_mechanisms",
            ],
        },
        "current_verdict": {
            "rapid_radiation": "strong",
            "radiation_success_asymmetry": "strong_descriptive_meta_result",
            "young_lineage_phenotype_ecology_divergence": "partial_local_support",
            "radiation_wide_trait_rate_acceleration": "unresolved_until_tree_plus_trait_bridge",
            "reticulation_ploidy_as_evolvability_driver": "unresolved_testable_partly_with_public_data_after_tree",
            "adaptive_radiation": "unresolved_requires_comparative_plus_replicated_fitness_evidence",
        },
        "claim_boundary": (
            "The 36:2 occupancy asymmetry, state-compression result and focal ploidy diversity are descriptive meta-results. "
            "They do not by themselves estimate diversification rate, trait evolutionary rate, causation or adaptation."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    summary = build_summary(Path(args.repo_root))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
