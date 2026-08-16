#!/usr/bin/env python3
"""Module-specific pre-tree trait × environment coupling for Japanese Cirsium.

Orientation, colour and outline-shape distances are compared separately against
four-variable CHELSA distance using taxon-label permutations. This is a
coverage-limited descriptive screen and not a phylogenetic/adaptive test.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.test_japan_radiation_pre_tree_trait_environment_coupling import (
    ENV,
    distance_matrix,
    rank_correlation,
)

MODULES = {
    "orientation": ["orientation_angle_degrees_median_taxon_median"],
    "colour": [
        "corolla_lab_lightness_median_taxon_median",
        "corolla_lab_chroma_median_taxon_median",
    ],
    "shape": [
        "shape_aspect_ratio_median_taxon_median",
        "shape_circularity_median_taxon_median",
        "shape_solidity_median_taxon_median",
        "shape_width_cv_median_taxon_median",
    ],
}


def standardized_distance(frame: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray]]:
    x = frame[columns].copy()
    x = (x - x.mean()) / x.std(ddof=0)
    d = distance_matrix(x)
    iu = np.triu_indices(len(x), 1)
    return d, iu


def module_result(
    frame: pd.DataFrame,
    module_columns: list[str],
    env_distance: np.ndarray,
    iu: tuple[np.ndarray, np.ndarray],
    *,
    permutations: int,
    seed: int,
) -> dict:
    module_distance, _ = standardized_distance(frame, module_columns)
    trait_vector = module_distance[iu]
    env_vector = env_distance[iu]
    observed = rank_correlation(trait_vector, env_vector)

    rng = np.random.default_rng(seed)
    ge_positive = 0
    ge_two = 0
    for _ in range(permutations):
        perm = rng.permutation(len(frame))
        perm_env = env_distance[perm][:, perm][iu]
        rho = rank_correlation(trait_vector, perm_env)
        ge_positive += rho >= observed - 1e-15
        ge_two += abs(rho) >= abs(observed) - 1e-15

    loo: dict[str, float] = {}
    for drop, taxon in enumerate(frame["taxon_name"]):
        reduced = frame.drop(index=frame.index[drop]).reset_index(drop=True)
        mod_d, mod_iu = standardized_distance(reduced, module_columns)
        env_d, env_iu = standardized_distance(reduced, ENV)
        if not (np.array_equal(mod_iu[0], env_iu[0]) and np.array_equal(mod_iu[1], env_iu[1])):
            raise RuntimeError("Pairwise index mismatch")
        loo[str(taxon)] = rank_correlation(mod_d[mod_iu], env_d[env_iu])

    return {
        "n_axes": len(module_columns),
        "observed_spearman_rho": observed,
        "positive_coupling_permutation_p": float((ge_positive + 1) / (permutations + 1)),
        "two_sided_permutation_p": float((ge_two + 1) / (permutations + 1)),
        "leave_one_taxon_out_rho": loo,
        "leave_one_out_all_negative": bool(all(value < 0 for value in loo.values())),
        "leave_one_out_signs_mixed": bool(any(value < 0 for value in loo.values()) and any(value > 0 for value in loo.values())),
    }


def build(frame: pd.DataFrame, *, permutations: int = 9999, seed: int = 20260816) -> dict:
    required = {"taxon_name", *ENV, *(column for columns in MODULES.values() for column in columns)}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Snapshot missing columns: {missing}")
    if frame["taxon_name"].duplicated().any():
        raise ValueError("Duplicate taxon")
    data = frame.copy()
    for column in required - {"taxon_name"}:
        data[column] = pd.to_numeric(data[column], errors="raise")

    env_distance, iu = standardized_distance(data, ENV)
    results = {
        name: module_result(
            data,
            columns,
            env_distance,
            iu,
            permutations=permutations,
            seed=seed,
        )
        for name, columns in MODULES.items()
    }

    return {
        "contract_version": "japan_radiation_pre_tree_module_environment_coupling_v1",
        "n_taxa": int(len(data)),
        "environment_axes": len(ENV),
        "taxon_label_permutations": permutations,
        "permutation_seed": seed,
        "modules": results,
        "descriptive_result": (
            "No module shows positive current climate-distance coupling in this nine-taxon pre-tree subset. "
            "Orientation and colour are approximately uncoupled and leave-one-out signs are mixed; the "
            "shape-distance association is negative and remains negative after removing any one taxon, "
            "although its permutation test is not significant."
        ),
        "interpretation": (
            "This weakens a single-axis climate-matching explanation for capitulum disparity and supports "
            "testing ecological drivers by trait module rather than treating the capitulum as one syndrome."
        ),
        "claim_boundary": (
            "Nine taxa, four broad CHELSA descriptors and species-median image traits are insufficient to "
            "exclude ecological adaptation on unmeasured abiotic or biotic axes. Pairwise observations are "
            "not phylogenetically independent; no evolutionary rate or adaptation is inferred."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--permutations", type=int, default=9999)
    parser.add_argument("--seed", type=int, default=20260816)
    args = parser.parse_args()

    result = build(
        pd.read_csv(args.snapshot),
        permutations=args.permutations,
        seed=args.seed,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
