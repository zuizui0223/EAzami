#!/usr/bin/env python3
"""Descriptive pre-tree trait-space comparison for Japan-38 public-image taxa.

This analysis asks whether a replicated secondary-history lineage (C. lineare)
is uniquely isolated in Azami image-trait space. It is deliberately descriptive:
no branch lengths, phylogenetic correction, evolutionary rates or adaptation are
inferred before the accepted EAzami topology ensemble exists.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


LINEAR_ENDPOINTS = {
    "orientation": "orientation_angle_degrees_median_taxon_median",
    "lightness": "corolla_lab_lightness_median_taxon_median",
    "chroma": "corolla_lab_chroma_median_taxon_median",
    "aspect_ratio": "shape_aspect_ratio_median_taxon_median",
    "circularity": "shape_circularity_median_taxon_median",
    "solidity": "shape_solidity_median_taxon_median",
    "width_cv": "shape_width_cv_median_taxon_median",
}


def euclidean(a: pd.Series, b: pd.Series) -> float:
    return float(np.sqrt(np.square(a.to_numpy(dtype=float) - b.to_numpy(dtype=float)).sum()))


def build_summary(
    traits: pd.DataFrame,
    *,
    min_observations: int = 10,
    secondary_taxon: str = "Cirsium lineare",
) -> dict:
    required = {"taxon_name", "n_observations_detector_positive", *LINEAR_ENDPOINTS.values()}
    missing = sorted(required.difference(traits.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    eligible = traits.loc[
        pd.to_numeric(traits["n_observations_detector_positive"], errors="coerce").ge(min_observations)
    ].copy()
    for column in LINEAR_ENDPOINTS.values():
        eligible[column] = pd.to_numeric(eligible[column], errors="coerce")
    eligible = eligible.dropna(subset=list(LINEAR_ENDPOINTS.values()))
    if secondary_taxon not in set(eligible["taxon_name"]):
        raise ValueError(f"Secondary-history comparator {secondary_taxon} is not eligible")

    matrix = eligible.set_index("taxon_name")[list(LINEAR_ENDPOINTS.values())]
    dominant = matrix.drop(index=secondary_taxon)
    if len(dominant) < 3:
        raise ValueError("Need at least three dominant-radiation comparison taxa")

    mean = dominant.mean()
    sd = dominant.std(ddof=0)
    if sd.le(0).any():
        raise ValueError("At least one endpoint has zero variance in the dominant comparison set")
    standardized = (matrix - mean) / sd
    dominant_standardized = standardized.loc[dominant.index]

    secondary_centroid_distance = euclidean(
        standardized.loc[secondary_taxon], pd.Series(0.0, index=standardized.columns)
    )

    loo = {}
    for taxon in dominant.index:
        rest = dominant.drop(index=taxon)
        rest_sd = rest.std(ddof=0)
        if rest_sd.le(0).any():
            raise ValueError("Leave-one-out standardization produced zero variance")
        z = (dominant.loc[taxon] - rest.mean()) / rest_sd
        loo[taxon] = float(np.sqrt(np.square(z.to_numpy(dtype=float)).sum()))

    within_pairs = []
    for first, second in combinations(dominant_standardized.index, 2):
        within_pairs.append({
            "taxon_a": first,
            "taxon_b": second,
            "distance": euclidean(dominant_standardized.loc[first], dominant_standardized.loc[second]),
        })
    lineare_pairs = [
        {
            "taxon": taxon,
            "distance": euclidean(standardized.loc[secondary_taxon], dominant_standardized.loc[taxon]),
        }
        for taxon in dominant_standardized.index
    ]

    max_within = max(within_pairs, key=lambda row: row["distance"])
    max_loo_taxon, max_loo = max(loo.items(), key=lambda item: item[1])
    lineare_values = [row["distance"] for row in lineare_pairs]

    return {
        "contract_version": "japan_radiation_pre_tree_trait_disparity_v1",
        "analysis_scope": "descriptive_pre_tree_public_image_trait_space",
        "min_detector_positive_observations": min_observations,
        "endpoint_names": list(LINEAR_ENDPOINTS),
        "circular_hue_components_excluded": True,
        "n_eligible_trait_taxa": int(len(matrix)),
        "n_dominant_radiation_trait_taxa": int(len(dominant)),
        "secondary_history_comparator": secondary_taxon,
        "eligible_taxa": list(matrix.index),
        "secondary_distance_to_dominant_centroid": secondary_centroid_distance,
        "dominant_leave_one_out_distances": loo,
        "largest_dominant_leave_one_out_distance": {
            "taxon": max_loo_taxon,
            "distance": max_loo,
        },
        "within_dominant_pairwise": {
            "n_pairs": len(within_pairs),
            "median_distance": float(np.median([row["distance"] for row in within_pairs])),
            "maximum": max_within,
        },
        "secondary_to_dominant_pairwise": {
            "n_pairs": len(lineare_pairs),
            "minimum_distance": min(lineare_values),
            "median_distance": float(np.median(lineare_values)),
            "maximum_distance": max(lineare_values),
        },
        "descriptive_result": (
            "The secondary-history comparator is not uniquely outside the current dominant-radiation "
            "image-trait disparity envelope: at least one dominant-radiation taxon has a larger "
            "leave-one-out multivariate displacement, and the largest within-dominant pairwise distance "
            "exceeds the largest observed secondary-to-dominant pairwise distance."
        ),
        "claim_boundary": (
            "This small, coverage-filtered public-image comparison does not estimate evolutionary rate, "
            "prove phenotypic convergence, resolve phylogeny, or demonstrate adaptation. It motivates "
            "the branch-length/topology-aware trait analysis after the EAzami nuclear tree is accepted."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traits", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--min-observations", type=int, default=10)
    args = parser.parse_args()

    traits = pd.read_csv(args.traits)
    summary = build_summary(traits, min_observations=args.min_observations)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
