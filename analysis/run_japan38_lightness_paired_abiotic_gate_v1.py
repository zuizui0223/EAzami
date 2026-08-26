#!/usr/bin/env python3
"""Test same-cohort abiotic explanations for Japan38 lightness overdispersion.

Unlike the earlier species-summary climate gate, this analysis uses environment
summaries reconstructed from the *same strict-spatial colour-usable observations*
that generate the exact-concept LAB-lightness bridge. It tests climate,
topography, and their combination at n>=5 and n>=10 colour evidence depth using
exhaustive lightness-label permutations. Soil is retained as an exploratory
coverage-limited screen because JPN_17 has only four soil-linked observations.

The canonical tree has substitution-length branch lengths; patristic distance is
used only as a sensitivity covariate, never as time.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import spearmanr

CLIMATE = ["chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15"]
TOPOGRAPHY = ["topo_elevation", "topo_slope", "topo_roughness"]
SOIL = [
    "soil_bdod_0_30cm", "soil_cec_0_30cm", "soil_cfvo_0_30cm",
    "soil_clay_0_30cm", "soil_sand_0_30cm", "soil_silt_0_30cm",
    "soil_nitrogen_0_30cm", "soil_phh2o_0_30cm", "soil_soc_0_30cm",
    "soil_ocd_0_30cm",
]
PRIMARY_MODULES = {
    "paired_climate": CLIMATE,
    "paired_topography": TOPOGRAPHY,
    "paired_climate_plus_topography": CLIMATE + TOPOGRAPHY,
}
COLOUR_THRESHOLDS = (5, 10)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_summary(path: Path) -> dict[str, dict[str, object]]:
    rows = read_csv(path)
    if len(rows) != 6:
        raise ValueError(f"expected six paired high-depth concepts, found {len(rows)}")
    out = {}
    for row in rows:
        mid = row["paper_japan_member_id"]
        if mid in out:
            raise ValueError(f"duplicate concept: {mid}")
        parsed: dict[str, object] = {
            "taxon_name": row["taxon_name"],
            "n_colour": int(row["n_colour_usable_observations"]),
            "lightness": float(row["corolla_lab_lightness_species_median"]),
        }
        for variable in CLIMATE + TOPOGRAPHY + SOIL:
            parsed[variable] = float(row[f"{variable}_median"])
            parsed[f"n_{variable}"] = int(row[f"n_{variable}"])
        out[mid] = parsed
    expected = {"JPN_17", "JPN_23", "JPN_29", "JPN_36", "JPN_37", "JPN_38"}
    if set(out) != expected:
        raise ValueError(f"paired concept set changed: {sorted(out)}")
    return out


def read_concept_tips(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    if len(rows) != 38:
        raise ValueError(f"expected 38 concept-map rows, found {len(rows)}")
    out = {}
    for row in rows:
        tips = [x for x in row["tip_ids"].split("|") if x]
        if len(tips) == 1:
            out[row["paper_japan_member_id"]] = tips[0]
    return out


def rho(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or len(x) != len(y):
        return math.nan
    if np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return math.nan
    return float(spearmanr(x, y).statistic)


def pairwise_abs(values) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return np.asarray(
        [abs(float(values[i] - values[j])) for i in range(len(values)) for j in range(i)],
        dtype=float,
    )


def pairwise_euclidean(matrix) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=float)
    return np.asarray(
        [
            float(np.linalg.norm(matrix[i] - matrix[j]))
            for i in range(len(matrix))
            for j in range(i)
        ],
        dtype=float,
    )


def zscore_columns(matrix) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=float)
    scale = matrix.std(axis=0, ddof=0)
    if np.any(scale <= 0):
        raise ValueError("zero-variance abiotic axis")
    return (matrix - matrix.mean(axis=0)) / scale


def partial_spearman(x, y, z) -> float:
    rxy, rxz, ryz = rho(x, y), rho(x, z), rho(y, z)
    if not all(math.isfinite(v) for v in (rxy, rxz, ryz)):
        return math.nan
    den = math.sqrt(max(0.0, (1.0 - rxz**2) * (1.0 - ryz**2)))
    if den <= 1e-12:
        return math.nan
    return float((rxy - rxz * ryz) / den)


def exact_test(distance, lightness, patristic=None) -> dict[str, object]:
    lightness = np.asarray(lightness, dtype=float)
    observed_trait = pairwise_abs(lightness)
    observed = rho(distance, observed_trait) if patristic is None else partial_spearman(distance, observed_trait, patristic)
    null = []
    for permuted in itertools.permutations(lightness.tolist()):
        trait = pairwise_abs(np.asarray(permuted, dtype=float))
        value = rho(distance, trait) if patristic is None else partial_spearman(distance, trait, patristic)
        if math.isfinite(value):
            null.append(value)
    arr = np.asarray(null, dtype=float)
    expected = math.factorial(len(lightness))
    if len(arr) != expected:
        raise ValueError(f"incomplete exact permutation space: {len(arr)} != {expected}")
    tol = 1e-12
    return {
        "rho": float(observed),
        "exact_permutations": int(len(arr)),
        "positive_tail_p": float(np.mean(arr >= observed - tol)),
        "negative_tail_p": float(np.mean(arr <= observed + tol)),
        "two_sided_abs_p": float(np.mean(np.abs(arr) >= abs(observed) - tol)),
    }


def patristic_vector(tree, tips: list[str]) -> np.ndarray:
    names = {tip.name for tip in tree.get_terminals()}
    if not set(tips).issubset(names):
        raise ValueError(f"tree missing tips: {sorted(set(tips)-names)}")
    return np.asarray(
        [float(tree.distance(tips[i], tips[j])) for i in range(len(tips)) for j in range(i)],
        dtype=float,
    )


def module_distance(rows, ids: list[str], variables: list[str]) -> np.ndarray:
    matrix = np.asarray([[float(rows[mid][v]) for v in variables] for mid in ids], dtype=float)
    return pairwise_euclidean(zscore_columns(matrix))


def summarize_primary_subset(tree, tips, rows, ids: list[str]) -> dict[str, object]:
    lightness = np.asarray([float(rows[mid]["lightness"]) for mid in ids], dtype=float)
    pat = patristic_vector(tree, [tips[mid] for mid in ids])
    trait_dist = pairwise_abs(lightness)
    modules = {}
    for name, variables in PRIMARY_MODULES.items():
        distance = module_distance(rows, ids, variables)
        primary = exact_test(distance, lightness)
        partial = exact_test(distance, lightness, patristic=pat)
        modules[name] = {
            "axes": variables,
            "distance_definition": "Euclidean distance after within-subset z-standardization",
            "abiotic_distance_vs_absolute_lightness_difference": primary,
            "partial_controlling_patristic_distance": partial,
            "patristic_vs_abiotic_distance_rho": rho(pat, distance),
        }
    return {
        "n_concepts": len(ids),
        "paper_japan_member_ids": ids,
        "n_colour_usable_observations": {mid: int(rows[mid]["n_colour"]) for mid in ids},
        "patristic_vs_absolute_lightness_difference_rho": rho(pat, trait_dist),
        "modules": modules,
    }


def leave_one_out_module(tree, tips, rows, ids: list[str], variables: list[str]) -> dict[str, float]:
    out = {}
    for dropped in ids:
        keep = [mid for mid in ids if mid != dropped]
        lightness = np.asarray([float(rows[mid]["lightness"]) for mid in keep])
        distance = module_distance(rows, keep, variables)
        out[dropped] = rho(distance, pairwise_abs(lightness))
    return out


def soil_exploratory(tree, tips, rows, minimum_soil_observations: int) -> dict[str, object]:
    qualified = []
    coverage = {}
    for mid, row in rows.items():
        counts = [int(row[f"n_{v}"]) for v in SOIL]
        coverage[mid] = {
            "minimum_nonmissing_across_soil_axes": min(counts),
            "maximum_nonmissing_across_soil_axes": max(counts),
        }
        if min(counts) >= minimum_soil_observations and int(row["n_colour"]) >= 5:
            qualified.append(mid)
    qualified.sort()
    result: dict[str, object] = {
        "minimum_soil_observations_required": minimum_soil_observations,
        "coverage_by_concept": coverage,
        "qualified_concepts": qualified,
        "six_taxon_replicated_gate_ready": len(qualified) == 6,
        "reason_if_blocked": (
            None if len(qualified) == 6 else
            "Soil coverage does not retain the full six-concept n>=5 colour subset; no n>=5 to n>=10 replicated soil gate is claimed."
        ),
    }
    if len(qualified) >= 5:
        lightness = np.asarray([float(rows[mid]["lightness"]) for mid in qualified])
        distance = module_distance(rows, qualified, SOIL)
        pat = patristic_vector(tree, [tips[mid] for mid in qualified])
        result["exploratory_clean_subset"] = {
            "n_concepts": len(qualified),
            "paper_japan_member_ids": qualified,
            "soil_distance_vs_absolute_lightness_difference": exact_test(distance, lightness),
            "partial_controlling_patristic_distance": exact_test(distance, lightness, patristic=pat),
            "patristic_vs_soil_distance_rho": rho(pat, distance),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paired-summary", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--concept-map", type=Path, required=True)
    parser.add_argument("--minimum-soil-observations", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = read_summary(args.paired_summary)
    tips = read_concept_tips(args.concept_map)
    tree = Phylo.read(str(args.tree), "newick")

    subsets = {}
    for threshold in COLOUR_THRESHOLDS:
        ids = sorted(mid for mid, row in rows.items() if int(row["n_colour"]) >= threshold)
        if len(ids) < 5:
            raise ValueError(f"too few concepts for colour threshold {threshold}: {len(ids)}")
        subsets[f"n_colour_usable_ge_{threshold}"] = summarize_primary_subset(tree, tips, rows, ids)

    ids5 = subsets["n_colour_usable_ge_5"]["paper_japan_member_ids"]
    module_decisions = {}
    for name, variables in PRIMARY_MODULES.items():
        m5 = subsets["n_colour_usable_ge_5"]["modules"][name]["abiotic_distance_vs_absolute_lightness_difference"]
        m10 = subsets["n_colour_usable_ge_10"]["modules"][name]["abiotic_distance_vs_absolute_lightness_difference"]
        loo = leave_one_out_module(tree, tips, rows, ids5, variables)
        supported = bool(
            m5["rho"] > 0
            and m5["positive_tail_p"] <= 0.05
            and m10["rho"] > 0
            and all(v > 0 for v in loo.values())
        )
        module_decisions[name] = {
            "tracking_supported": supported,
            "rule": "Require positive n>=5 association with exact positive-tail p<=0.05, positive n>=10 direction, and positive direction after every n>=5 leave-one-out removal.",
            "leave_one_taxon_out_rho": loo,
            "leave_one_taxon_out_all_positive": all(v > 0 for v in loo.values()),
            "leave_one_taxon_out_all_negative": all(v < 0 for v in loo.values()),
        }

    result = {
        "contract_version": "japan38_lightness_paired_abiotic_gate_v1",
        "status_date": "2026-08-26",
        "paired_evidence_contract": {
            "summary": str(args.paired_summary),
            "meaning": "Lightness and environmental medians are reconstructed from the same strict-spatial colour-usable observations within each exact taxon concept.",
            "climate_axes": CLIMATE,
            "topography_axes": TOPOGRAPHY,
            "soil_axes": SOIL,
            "absent_axes": ["solar radiation / rsds", "VPD / aridity", "wind / sfcWind"],
        },
        "tree_contract": {
            "tree": str(args.tree),
            "branch_length_semantics": "substitutions/site, not dated time",
        },
        "subsets": subsets,
        "primary_module_decisions": module_decisions,
        "soil": soil_exploratory(tree, tips, rows, args.minimum_soil_observations),
        "overall_decision": {
            "paired_current_climate_or_topography_explains_lightness_overdispersion": any(
                item["tracking_supported"] for item in module_decisions.values()
            ),
            "interpretation": "Same-cohort current climate/topography tracking is supported only if at least one frozen module gate passes; soil remains separate because coverage does not preserve the same depth-replicated concept set.",
        },
        "claim_boundary": "Small observational species-level same-cohort diagnostic. Pairing reduces evidence-layer mismatch but does not establish causal selection. No radiation/VPD/wind variables are present in the source artifact; soil coverage is uneven; the tree is not dated. No convergence, adaptation, ancestral-colour, or evolutionary-rate claim is made."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
