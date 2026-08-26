#!/usr/bin/env python3
"""Test whether current climate explains Japan38 lightness overdispersion.

This is an exploratory follow-up to the frozen continuous-colour history result.
The primary question is deliberately narrow: among exact Japan38 concepts with
reasonably deep image-colour evidence, do taxa that occupy more different
present-day climates also differ more in corolla LAB lightness?

The test uses exact taxon-label permutations for the small n>=5 and n>=10
subsets. Four CHELSA species-median axes (BIO1, BIO4, BIO12, BIO15) are
standardized within each subset and combined as Euclidean climate distance.
Patristic distance on the canonical substitution-length Japan38 tree is
reported separately and used in a partial-Spearman sensitivity diagnostic.

This is not a causal climate-adaptation test. Colour and climate summaries come
from different species-level evidence layers and are not paired observations.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np
from Bio import Phylo
from scipy.stats import spearmanr

ENV_COLUMNS = {
    "BIO1": "env_chelsa_bio01_species_median",
    "BIO4": "env_chelsa_bio04_species_median",
    "BIO12": "env_chelsa_bio12_species_median",
    "BIO15": "env_chelsa_bio15_species_median",
}
COLOUR_N_COLUMN = "n_colour_usable_observations"
LIGHTNESS_COLUMN = "corolla_lab_lightness_species_median"
ENV_N_COLUMN = "n_balanced_env_observations"
THRESHOLDS = (5, 10)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def finite_float(row: dict[str, str], column: str) -> float:
    value = float(row[column])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {column}: {row}")
    return value


def read_concept_map(path: Path) -> dict[str, list[str]]:
    rows = read_csv(path)
    if len(rows) != 38:
        raise ValueError(f"expected 38 Japan38 concepts, found {len(rows)}")
    out: dict[str, list[str]] = {}
    for row in rows:
        mid = row["paper_japan_member_id"]
        if mid in out:
            raise ValueError(f"duplicate concept: {mid}")
        out[mid] = [x for x in row["tip_ids"].split("|") if x]
    if out.get("JPN_20") != ["J38S020", "J38S021"]:
        raise ValueError("canonical JPN_20 replicate map changed")
    return out


def join_colour_environment(
    colour_path: Path,
    environment_path: Path,
) -> dict[str, dict[str, object]]:
    colour = read_csv(colour_path)
    environment = read_csv(environment_path)
    env_by_taxon = {row["taxon_name"]: row for row in environment}
    if len(env_by_taxon) != len(environment):
        raise ValueError("environment snapshot contains duplicate taxon names")

    out: dict[str, dict[str, object]] = {}
    for row in colour:
        mid = row["paper_japan_member_id"]
        taxon = row["taxon_name"]
        if mid in {"JPN_20", "JPN_21", "JPN_31"}:
            raise ValueError(f"non-exact/conflicted colour concept entered bridge: {mid}")
        env = env_by_taxon.get(taxon)
        if env is None:
            continue
        if mid in out:
            raise ValueError(f"duplicate colour concept: {mid}")
        out[mid] = {
            "paper_japan_member_id": mid,
            "taxon_name": taxon,
            "lightness": finite_float(row, LIGHTNESS_COLUMN),
            "n_colour": int(row[COLOUR_N_COLUMN]),
            "n_environment": int(env[ENV_N_COLUMN]),
            "environment": {
                axis: finite_float(env, column)
                for axis, column in ENV_COLUMNS.items()
            },
        }
    return out


def rho(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) != len(y) or len(x) < 3:
        return math.nan
    if np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return math.nan
    return float(spearmanr(x, y).statistic)


def pairwise_absolute(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return np.asarray(
        [abs(float(values[i] - values[j])) for i in range(len(values)) for j in range(i)],
        dtype=float,
    )


def pairwise_euclidean(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=float)
    return np.asarray(
        [
            float(np.linalg.norm(matrix[i] - matrix[j]))
            for i in range(len(matrix))
            for j in range(i)
        ],
        dtype=float,
    )


def zscore_columns(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=float)
    means = matrix.mean(axis=0)
    scales = matrix.std(axis=0, ddof=0)
    if np.any(scales <= 0):
        raise ValueError("environment axis has zero variance in subset")
    return (matrix - means) / scales


def partial_spearman(x, y, z) -> float:
    r_xy = rho(x, y)
    r_xz = rho(x, z)
    r_yz = rho(y, z)
    if not all(math.isfinite(v) for v in (r_xy, r_xz, r_yz)):
        return math.nan
    denominator = math.sqrt(max(0.0, (1.0 - r_xz**2) * (1.0 - r_yz**2)))
    if denominator <= 1e-12:
        return math.nan
    return float((r_xy - r_xz * r_yz) / denominator)


def exact_tail_summary(observed: float, null: list[float]) -> dict[str, object]:
    usable = np.asarray([v for v in null if math.isfinite(v)], dtype=float)
    if not math.isfinite(observed) or not len(usable):
        return {
            "observed": observed,
            "exact_permutations": int(len(usable)),
            "positive_tail_p": None,
            "negative_tail_p": None,
            "two_sided_abs_p": None,
        }
    tol = 1e-12
    return {
        "observed": float(observed),
        "exact_permutations": int(len(usable)),
        "positive_tail_p": float(np.mean(usable >= observed - tol)),
        "negative_tail_p": float(np.mean(usable <= observed + tol)),
        "two_sided_abs_p": float(np.mean(np.abs(usable) >= abs(observed) - tol)),
        "null_range": [float(usable.min()), float(usable.max())],
    }


def exact_distance_test(
    fixed_distance: np.ndarray,
    lightness: np.ndarray,
    statistic: Callable[[np.ndarray, np.ndarray], float] | None = None,
) -> dict[str, object]:
    if statistic is None:
        statistic = rho
    lightness = np.asarray(lightness, dtype=float)
    observed_difference = pairwise_absolute(lightness)
    observed = statistic(fixed_distance, observed_difference)
    null: list[float] = []
    for permuted in itertools.permutations(lightness.tolist()):
        null.append(
            statistic(fixed_distance, pairwise_absolute(np.asarray(permuted, dtype=float)))
        )
    result = exact_tail_summary(observed, null)
    expected = math.factorial(len(lightness))
    if result["exact_permutations"] != expected:
        raise ValueError(
            f"exact permutation space incomplete: {result['exact_permutations']} != {expected}"
        )
    return result


def exact_directional_test(environment: np.ndarray, lightness: np.ndarray) -> dict[str, object]:
    environment = np.asarray(environment, dtype=float)
    lightness = np.asarray(lightness, dtype=float)
    observed = rho(environment, lightness)
    null = [
        rho(environment, np.asarray(permuted, dtype=float))
        for permuted in itertools.permutations(lightness.tolist())
    ]
    result = exact_tail_summary(observed, null)
    expected = math.factorial(len(lightness))
    if result["exact_permutations"] != expected:
        raise ValueError("directional exact permutation space incomplete")
    return result


def patristic_vector(tree, tips: list[str]) -> np.ndarray:
    terminal_names = {tip.name for tip in tree.get_terminals()}
    missing = sorted(set(tips) - terminal_names)
    if missing:
        raise ValueError(f"canonical tree missing tips: {missing}")
    return np.asarray(
        [
            float(tree.distance(tips[i], tips[j]))
            for i in range(len(tips))
            for j in range(i)
        ],
        dtype=float,
    )


def subset_records(
    joined: dict[str, dict[str, object]],
    threshold: int,
    minimum_environment_observations: int,
) -> list[dict[str, object]]:
    rows = [
        row
        for row in joined.values()
        if int(row["n_colour"]) >= threshold
        and int(row["n_environment"]) >= minimum_environment_observations
    ]
    return sorted(rows, key=lambda row: str(row["paper_japan_member_id"]))


def summarize_subset(
    tree,
    concept_map: dict[str, list[str]],
    records: list[dict[str, object]],
) -> dict[str, object]:
    ids = [str(row["paper_japan_member_id"]) for row in records]
    if len(ids) > 8:
        raise ValueError("exact permutation gate is intentionally limited to <=8 taxa")
    tips: list[str] = []
    for mid in ids:
        mapped = concept_map[mid]
        if len(mapped) != 1:
            raise ValueError(f"exact climate-colour subset requires singleton tree concept: {mid}")
        tips.append(mapped[0])

    lightness = np.asarray([float(row["lightness"]) for row in records], dtype=float)
    environment_matrix = np.asarray(
        [
            [float(row["environment"][axis]) for axis in ENV_COLUMNS]
            for row in records
        ],
        dtype=float,
    )
    standardized = zscore_columns(environment_matrix)
    climate_distance = pairwise_euclidean(standardized)
    lightness_difference = pairwise_absolute(lightness)
    patristic = patristic_vector(tree, tips)

    primary = exact_distance_test(climate_distance, lightness)
    primary_partial = exact_distance_test(
        climate_distance,
        lightness,
        statistic=lambda x, y: partial_spearman(x, y, patristic),
    )

    axis_distance: dict[str, object] = {}
    axis_directional: dict[str, object] = {}
    for index, axis in enumerate(ENV_COLUMNS):
        values = environment_matrix[:, index]
        axis_distance[axis] = {
            **exact_distance_test(pairwise_absolute(values), lightness),
            "patristic_vs_environment_difference_rho": rho(
                patristic, pairwise_absolute(values)
            ),
            "partial_controlling_patristic": exact_distance_test(
                pairwise_absolute(values),
                lightness,
                statistic=lambda x, y: partial_spearman(x, y, patristic),
            ),
        }
        axis_directional[axis] = exact_directional_test(values, lightness)

    leave_one_out: dict[str, object] = {}
    if len(records) >= 5:
        for dropped_index, dropped in enumerate(records):
            keep = [row for i, row in enumerate(records) if i != dropped_index]
            keep_ids = [str(row["paper_japan_member_id"]) for row in keep]
            keep_tips = [concept_map[mid][0] for mid in keep_ids]
            keep_lightness = np.asarray([float(row["lightness"]) for row in keep])
            keep_env = np.asarray(
                [[float(row["environment"][axis]) for axis in ENV_COLUMNS] for row in keep],
                dtype=float,
            )
            keep_climate_distance = pairwise_euclidean(zscore_columns(keep_env))
            keep_patristic = patristic_vector(tree, keep_tips)
            keep_primary = exact_distance_test(keep_climate_distance, keep_lightness)
            keep_partial = exact_distance_test(
                keep_climate_distance,
                keep_lightness,
                statistic=lambda x, y: partial_spearman(x, y, keep_patristic),
            )
            leave_one_out[str(dropped["paper_japan_member_id"])] = {
                "remaining_concepts": keep_ids,
                "multivariate_climate_vs_lightness_difference": keep_primary,
                "partial_controlling_patristic": keep_partial,
            }

    return {
        "n_concepts": len(ids),
        "paper_japan_member_ids": ids,
        "taxa": [str(row["taxon_name"]) for row in records],
        "n_colour_usable_observations": {
            str(row["paper_japan_member_id"]): int(row["n_colour"])
            for row in records
        },
        "n_balanced_environment_observations": {
            str(row["paper_japan_member_id"]): int(row["n_environment"])
            for row in records
        },
        "phylogenetic_context": {
            "patristic_vs_absolute_lightness_difference_rho": rho(
                patristic, lightness_difference
            ),
            "patristic_vs_multivariate_climate_distance_rho": rho(
                patristic, climate_distance
            ),
        },
        "primary_multivariate_climate_distance": {
            **primary,
            "distance_definition": "Euclidean distance after within-subset z-standardization of BIO1/BIO4/BIO12/BIO15",
            "partial_controlling_patristic": primary_partial,
        },
        "secondary_axis_distance": axis_distance,
        "secondary_axis_directional": axis_directional,
        "leave_one_taxon_out_primary": leave_one_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--concept-map", type=Path, required=True)
    parser.add_argument("--colour-bridge", type=Path, required=True)
    parser.add_argument("--environment-snapshot", type=Path, required=True)
    parser.add_argument("--minimum-environment-observations", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    concept_map = read_concept_map(args.concept_map)
    joined = join_colour_environment(args.colour_bridge, args.environment_snapshot)
    tree = Phylo.read(str(args.tree), "newick")

    subsets: dict[str, object] = {}
    for threshold in THRESHOLDS:
        records = subset_records(
            joined,
            threshold,
            args.minimum_environment_observations,
        )
        if len(records) < 5:
            raise ValueError(
                f"need >=5 taxa for threshold {threshold}; found {len(records)}"
            )
        subsets[f"n_colour_usable_ge_{threshold}"] = summarize_subset(
            tree, concept_map, records
        )

    primary = subsets["n_colour_usable_ge_5"]
    deep = subsets["n_colour_usable_ge_10"]
    p_primary = primary["primary_multivariate_climate_distance"]
    p_deep = deep["primary_multivariate_climate_distance"]
    loo_rho = [
        item["multivariate_climate_vs_lightness_difference"]["observed"]
        for item in primary["leave_one_taxon_out_primary"].values()
    ]
    current_climate_tracking_supported = bool(
        p_primary["observed"] > 0
        and p_primary["positive_tail_p"] <= 0.05
        and p_deep["observed"] > 0
        and all(v > 0 for v in loo_rho)
    )

    directional_replicated_axes = []
    for axis in ENV_COLUMNS:
        a = primary["secondary_axis_directional"][axis]
        b = deep["secondary_axis_directional"][axis]
        if (
            a["two_sided_abs_p"] <= 0.05
            and b["two_sided_abs_p"] <= 0.05
            and a["observed"] * b["observed"] > 0
        ):
            directional_replicated_axes.append(axis)

    result = {
        "contract_version": "japan38_colour_climate_coupling_v1",
        "status_date": "2026-08-26",
        "analysis_status": "exploratory_followup_after_lightness_overdispersion_detection",
        "tree_contract": {
            "tree": str(args.tree),
            "concept_map": str(args.concept_map),
            "branch_length_semantics": "substitutions/site phylogram; not dated time",
        },
        "trait_contract": {
            "colour_source": str(args.colour_bridge),
            "response": "absolute pairwise difference in exact-concept image-derived corolla LAB lightness",
            "colour_evidence_thresholds": list(THRESHOLDS),
            "important_boundary": "The lightness values come from the exact-concept strict-spatial Azami colour bridge, not from the older lightness column stored in the pre-tree environment snapshot.",
        },
        "environment_contract": {
            "source": str(args.environment_snapshot),
            "axes": list(ENV_COLUMNS),
            "minimum_balanced_environment_observations": args.minimum_environment_observations,
            "primary_predictor": "multivariate standardized CHELSA distance",
            "secondary_predictors": "axis-specific absolute distance and directional Spearman screens",
            "important_boundary": "Species-level current-climate medians are a separate evidence layer from colour observations; this is not a within-observation or causal environmental exposure analysis.",
        },
        "permutation_contract": {
            "primary": "exhaustive permutation of lightness labels across taxa; no Monte Carlo approximation",
            "tails_reported": ["positive", "negative", "two_sided_absolute"],
            "partial_sensitivity": "partial Spearman of pairwise climate distance and lightness difference controlling pairwise patristic distance, with the same exact lightness-label permutation",
        },
        "subsets": subsets,
        "decision_gate": {
            "current_four_axis_climate_tracking_supported": current_climate_tracking_supported,
            "rule": "Require positive multivariate climate-distance/lightness-distance association with exact positive-tail p<=0.05 in the n>=5 subset, the same positive direction in n>=10, and positive leave-one-out direction after every n>=5 taxon removal.",
            "replicated_directional_axes_at_two_sided_0_05": directional_replicated_axes,
            "interpretation": (
                "Current BIO1/BIO4/BIO12/BIO15 differences do not explain the observed lightness overdispersion under this gate."
                if not current_climate_tracking_supported
                else "Current four-axis climate distance is consistent with tracking of continuous lightness differences in this small subset."
            ),
        },
        "claim_boundary": (
            "Exploratory six-/five-taxon species-level diagnostic only. Failure of this gate does not reject climatic selection generally: the climate layer is limited to four current CHELSA axes, colour and environment are not measured on the same individuals, and historical climates are not modelled. Secondary axis screens are descriptive and are not corrected confirmatory tests. No adaptation, convergence, evolutionary-rate, ancestral-colour, or causal-environment claim follows from this analysis."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
