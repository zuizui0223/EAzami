#!/usr/bin/env python3
import argparse
import copy
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="data/evidence/micro_to_macro_evidence_synthesis_v1.json")
    p.add_argument("--matrix", default="data/evidence/micro_to_macro_evidence_matrix_v2.csv")
    p.add_argument("--macro-snapshot", default="data/evidence/azami_ch1_macro_trait_snapshot_v1.json")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    out = copy.deepcopy(load_json(args.base))
    matrix = read_csv(args.matrix)
    snap = load_json(args.macro_snapshot)

    class_counts = Counter(r["evidence_class"] for r in matrix)
    scale_counts = Counter(r["scale"] for r in matrix)
    groups = defaultdict(set)
    for row in matrix:
        group = (row.get("data_generation_group") or "").strip()
        if group:
            groups[row["evidence_class"]].add(group)

    out["contract_version"] = "micro_to_macro_evidence_synthesis_v2"
    out["evidence_matrix"] = {
        "rows": len(matrix),
        "class_counts": dict(sorted(class_counts.items())),
        "scale_counts": dict(sorted(scale_counts.items())),
        "independent_data_generation_groups_by_class": {
            k: sorted(v) for k, v in sorted(groups.items())
        },
    }

    pa = snap["precision_aware_cross_scale_result"]
    nv = snap["nested_visible_variance"]
    out["own_preliminary_macro_trait_result"] = {
        "evidence_class": snap["evidence_class"],
        "source_repo": snap["source_repo"],
        "source_commit": snap["source_commit"],
        "analysis_release": snap["analysis_release"],
        "n_taxa": snap["dataset"]["n_taxa"],
        "n_observations": snap["dataset"]["n_observations"],
        "n_heads": snap["dataset"]["n_heads"],
        "n_endpoints": snap["dataset"]["n_endpoints"],
        "one_head_per_photo_within_fraction_range": nv["one_head_per_photo_within_fraction_range"],
        "balanced_10_photo_within_fraction_range": nv["balanced_10_photo_median_within_fraction_range"],
        "noise_adjusted_rho": pa["noise_adjusted_variation_association_spearman_rho"],
        "noise_adjusted_rho_ci95": pa["species_bootstrap_ci95"],
        "hierarchical_effect": pa["hierarchical_log_variance_change_per_sd_visible_variation"],
        "hierarchical_ci95": pa["hierarchical_profile_ci95"],
        "hierarchical_p": pa["hierarchical_likelihood_ratio_p_value"],
        "allowed_interpretation": snap["allowed_interpretation"],
        "forbidden_inference": snap["forbidden_inference"],
    }

    out["EAzami_discovered_problems"]["P_MACRO_06_species_mean_scale_compression"] = {
        "basis": "own cross-project image-phenomics preliminary analysis (zuizui0223/azami)",
        "result": (
            "Across nine image-derived endpoints, at least about half of visible variance remains below assigned-species means under photo-balance sensitivities, "
            f"while precision-aware variation-vs-climate association is near zero (rho={pa['noise_adjusted_variation_association_spearman_rho']:.4f}; "
            f"hierarchical b={pa['hierarchical_log_variance_change_per_sd_visible_variation']:.4f}, P={pa['hierarchical_likelihood_ratio_p_value']:.3f})."
        ),
        "why_problem": "species means and a single trait-lability axis collapse distinct within-species, environment-association, and macroevolutionary scales",
        "hypothesis": "HMM2|HMM6",
    }

    out["EAzami_hypotheses"]["HMM6"] = {
        "name": "cross-scale trait decoupling",
        "derived_from": [
            "P_MACRO_03_species_tip_state_aggregation",
            "P_MACRO_06_species_mean_scale_compression",
        ],
        "prediction": "after measurement and topology uncertainty are propagated, within-species visible dispersion, population-aware discrete transition density, within-species environment-trait association, and among-species niche/trait divergence remain only partially coupled rather than collapsing to one universal lability axis",
        "falsifier": "validated cross-trait analyses recover a strong, consistent mapping from within-species dispersion to population transition density and among-species ecological/phylogenetic divergence across modules and clades",
    }

    out["claim_boundary"] = (
        "Published conclusions, EAzami reanalysis findings, and own preliminary results are stored as separate evidence classes. "
        "EAzami hypotheses are derived from problems exposed by our analyses; own preliminary macro-trait results may generate hypotheses but cannot be promoted to genetic variance, plasticity, adaptation, or evolutionary-rate evidence."
    )

    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
