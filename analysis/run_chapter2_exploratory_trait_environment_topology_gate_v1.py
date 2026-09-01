#!/usr/bin/env python3
"""Apply an all-row phylogenetic/topology sensitivity gate to the EAzami common9 atlas.

No trait-environment row is selected by Azami or by the common9 raw P value before
this analysis. The ML layer uses empirical Comp1061 branch lengths in substitutions
per site. The 1000 UFBoot layer is topology-only with unit branch lengths because
the archived UFBoot Newick lines do not retain optimized branch lengths.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import spearmanr

TRAIT_COLUMNS = {
    "orientation_angle_degrees": "orientation_angle_degrees_median_taxon_median",
    "corolla_lab_lightness": "corolla_lab_lightness_median_taxon_median",
    "corolla_lab_chroma": "corolla_lab_chroma_median_taxon_median",
    "shape_aspect_ratio": "shape_aspect_ratio_median_taxon_median",
    "shape_circularity": "shape_circularity_median_taxon_median",
    "shape_solidity": "shape_solidity_median_taxon_median",
    "shape_width_cv": "shape_width_cv_median_taxon_median",
}
ENV_COLUMNS = {
    "BIO1": "chelsa_bio01",
    "BIO4": "chelsa_bio04",
    "BIO12": "chelsa_bio12",
    "BIO15": "chelsa_bio15",
    "RSDS": "chelsa_rsds_mean",
    "VPD": "chelsa_vpd_mean",
    "SFCWIND": "chelsa_sfcwind_mean",
    "GSP": "chelsa_gsp",
    "NPP": "chelsa_npp",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--atlas-json", type=Path, required=True)
    p.add_argument("--taxon-medians", type=Path, required=True)
    p.add_argument("--mapping", type=Path, required=True)
    p.add_argument("--ml-tree", type=Path, required=True)
    p.add_argument("--ufboot", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def bh_adjust(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    n = len(p)
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.minimum(adjusted, 1.0)
    out = np.empty(n, dtype=float)
    out[order] = adjusted
    return out.tolist()


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    sd = float(values.std(ddof=0))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("No finite variation")
    return (values - values.mean()) / sd


def brownian_covariance(tree, tips: list[str]) -> np.ndarray:
    root = tree.root
    n = len(tips)
    matrix = np.zeros((n, n), dtype=float)
    for i, tip_i in enumerate(tips):
        matrix[i, i] = float(tree.distance(root, tip_i))
        for j in range(i):
            ancestor = tree.common_ancestor(tip_i, tips[j])
            value = float(tree.distance(root, ancestor))
            matrix[i, j] = value
            matrix[j, i] = value
    diag_mean = float(np.mean(np.diag(matrix)))
    if not np.isfinite(diag_mean) or diag_mean <= 0:
        raise ValueError("Degenerate phylogenetic covariance")
    matrix /= diag_mean
    matrix += np.eye(n) * 1e-8
    return matrix


def residual_precision(covariance: np.ndarray) -> np.ndarray:
    precision = np.linalg.pinv(covariance)
    ones = np.ones(len(covariance), dtype=float)
    w1 = precision @ ones
    denom = float(ones @ w1)
    if not np.isfinite(denom) or abs(denom) <= 1e-12:
        raise ValueError("Degenerate intercept precision")
    return precision - np.outer(w1, w1) / denom


def gls_slope(y: np.ndarray, x: np.ndarray, residual_p: np.ndarray) -> float:
    yz = zscore(y)
    xz = zscore(x)
    numerator = float(xz @ residual_p @ yz)
    denominator = float(xz @ residual_p @ xz)
    if not np.isfinite(denominator) or abs(denominator) <= 1e-12:
        raise ValueError("Degenerate GLS predictor denominator")
    return numerator / denominator


def exact_permutation_p(y: np.ndarray, x: np.ndarray, residual_p: np.ndarray, permutations: np.ndarray) -> tuple[float, float]:
    yz = zscore(y)
    xz = zscore(x)
    observed_num = float(xz @ residual_p @ yz)
    observed_den = float(xz @ residual_p @ xz)
    observed = observed_num / observed_den
    permuted_x = xz[permutations]
    permuted_m = permuted_x @ residual_p
    numerator = permuted_m @ yz
    denominator = np.einsum("ij,ij->i", permuted_m, permuted_x)
    beta = numerator / denominator
    p_value = float(np.mean(np.abs(beta) >= abs(observed) - 1e-12))
    return float(observed), p_value


def topology_class(fraction_same: float) -> str:
    if fraction_same >= 0.95:
        return "stable_same_direction"
    if fraction_same >= 0.80:
        return "mostly_same_direction"
    if fraction_same > 0.20:
        return "topology_sensitive"
    if fraction_same > 0.05:
        return "mostly_reversed"
    return "reversed"


def main() -> int:
    args = parse_args()
    atlas = json.loads(args.atlas_json.read_text(encoding="utf-8"))
    if atlas.get("status") != "executed" or atlas.get("n_tests") != 63:
        raise ValueError("Input common9 atlas is not the executed 63-row result")
    medians = pd.read_csv(args.taxon_medians)
    mapping_contract = json.loads(args.mapping.read_text(encoding="utf-8"))
    exact_map = {
        row["taxon_name"]: row["tip_id"]
        for row in mapping_contract["mappings"]
        if row.get("status") == "exact" and row.get("tip_id")
    }
    atlas_taxa = medians["taxon_name"].astype(str).tolist()
    exact_taxa = [taxon for taxon in atlas_taxa if taxon in exact_map]
    excluded_taxa = [taxon for taxon in atlas_taxa if taxon not in exact_map]
    subset = medians.loc[medians["taxon_name"].isin(exact_taxa)].copy()
    subset = subset.sort_values("taxon_name").reset_index(drop=True)
    exact_taxa = subset["taxon_name"].tolist()
    tips = [exact_map[taxon] for taxon in exact_taxa]
    n_taxa = len(subset)
    if n_taxa < 5:
        raise RuntimeError(f"Too few exact Japan38 taxa for topology gate: {n_taxa}")

    atlas_rows = {(row["trait"], row["environment"]): row for row in atlas["rows"]}
    if len(atlas_rows) != 63:
        raise AssertionError("Expected 63 unique common9 atlas rows")

    ml_tree = Phylo.read(str(args.ml_tree), "newick")
    ml_residual_p = residual_precision(brownian_covariance(ml_tree, tips))
    permutations = np.asarray(list(itertools.permutations(range(n_taxa))), dtype=np.int16)

    bootstrap_residual_p: list[np.ndarray] = []
    for line in args.ufboot.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        tree = Phylo.read(StringIO(line), "newick")
        tree.root.branch_length = 0.0
        for clade in tree.find_clades(order="level"):
            if clade is not tree.root:
                clade.branch_length = 1.0
        bootstrap_residual_p.append(residual_precision(brownian_covariance(tree, tips)))
    if len(bootstrap_residual_p) != 1000:
        raise AssertionError(f"Expected 1000 UFBoot trees, got {len(bootstrap_residual_p)}")

    rows: list[dict] = []
    for trait_id, trait_col in TRAIT_COLUMNS.items():
        y = subset[trait_col].to_numpy(dtype=float)
        yz = zscore(y)
        for env_id, env_col in ENV_COLUMNS.items():
            x = subset[env_col].to_numpy(dtype=float)
            xz = zscore(x)
            raw_subset_rho = float(spearmanr(y, x).statistic)
            ml_beta, ml_p = exact_permutation_p(y, x, ml_residual_p, permutations)
            bootstrap_beta = np.asarray([
                float((xz @ matrix @ yz) / (xz @ matrix @ xz))
                for matrix in bootstrap_residual_p
            ])
            sign_reference = float(np.sign(ml_beta)) if ml_beta != 0 else float(np.sign(raw_subset_rho))
            same = float(np.mean(np.sign(bootstrap_beta) == sign_reference))
            original = atlas_rows[(trait_id, env_id)]
            rows.append({
                "trait": trait_id,
                "environment": env_id,
                "environment_block": original["environment_block"],
                "atlas8_n_taxa": int(original["n_taxa"]),
                "atlas8_spearman_rho": float(original["spearman_rho"]),
                "atlas8_exact_p": float(original["exact_two_sided_p"]),
                "atlas8_bh_q_63": float(original["bh_q_63"]),
                "atlas8_status": original["status"],
                "exact_tree_n_taxa": n_taxa,
                "exact_tree_subset_spearman_rho": raw_subset_rho,
                "ml_branch_aware_beta": ml_beta,
                "ml_exact_permutation_p": ml_p,
                "ufboot1000_positive_fraction": float(np.mean(bootstrap_beta > 0)),
                "ufboot1000_same_sign_fraction_vs_ml": same,
                "ufboot1000_beta_q05": float(np.quantile(bootstrap_beta, 0.05)),
                "ufboot1000_beta_median": float(np.median(bootstrap_beta)),
                "ufboot1000_beta_q95": float(np.quantile(bootstrap_beta, 0.95)),
                "topology_sign_class": topology_class(same),
            })

    q_values = bh_adjust([row["ml_exact_permutation_p"] for row in rows])
    for row, q in zip(rows, q_values):
        row["ml_bh_q_63"] = float(q)
        row["ml_support_class"] = "bh_supported" if q < 0.05 else "not_bh_supported"

    atlas_raw_leads = [
        row for row in rows
        if row["atlas8_exact_p"] <= 0.05
    ]
    stable_rows = [row for row in rows if row["topology_sign_class"] == "stable_same_direction"]
    result = {
        "contract_version": "chapter2_exploratory_trait_environment_topology_gate_v1",
        "status_date": "2026-09-01",
        "scope": "all 63 EAzami common9 rows; exact Japan38 taxon mapping only; ML branch-aware plus 1000-tree topology-only sensitivity",
        "source_common9": {
            "artifact_id": 9788634414,
            "workflow_run_id": 33477091186,
            "artifact_digest": "sha256:d64a9cee1eb3bcd709776e1785e6fcfe4eefa2f1a511ff823c8be3baca8f3073"
        },
        "source_tree": mapping_contract["tree_sources"],
        "atlas_taxa": atlas_taxa,
        "exact_tree_taxa": exact_taxa,
        "exact_tree_tip_ids": tips,
        "excluded_from_tree_gate": excluded_taxa,
        "n_exact_tree_taxa": n_taxa,
        "n_rows": len(rows),
        "ml_exact_permutations_per_row": math.factorial(n_taxa),
        "ufboot_trees": len(bootstrap_residual_p),
        "rows": rows,
        "summary": {
            "ml_bh_supported_rows": sum(row["ml_bh_q_63"] < 0.05 for row in rows),
            "topology_stable_same_direction_rows": len(stable_rows),
            "atlas_raw_p_le_0_05_rows": len(atlas_raw_leads),
            "atlas_raw_leads_after_topology_gate": atlas_raw_leads,
            "smallest_ml_p_rows": sorted(rows, key=lambda row: (row["ml_exact_permutation_p"], -abs(row["ml_branch_aware_beta"])))[:10]
        },
        "interpretation_boundary": (
            "This is a phylogenetic/topology sensitivity layer for an exploratory small-taxon atlas. "
            "A stable sign across UFBoot topologies is not a confirmatory ecological association and "
            "does not identify adaptation or historical causation. ML branch lengths are substitutions/site; "
            "UFBoot slopes use unit branches and therefore test topology only."
        ),
        "claim_boundary": mapping_contract["claim_boundary"]
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(args.out_csv, index=False)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
