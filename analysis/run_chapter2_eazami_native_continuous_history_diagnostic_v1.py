#!/usr/bin/env python3
"""Run the frozen n=7 EAzami-native continuous-history diagnostic.

The primary statistic is the distance correlation predeclared in the design
contract. All 7! tip-label permutations are enumerated. Pagel lambda and
leave-one-out results are descriptive sensitivities; no rate or convergence
claim is permitted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
from io import StringIO
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.optimize import minimize_scalar
from scipy.stats import rankdata


def sha256(path: Path) -> str:
    """Hash frozen UTF-8 text canonically so LF and CRLF checkouts are identical."""
    text = path.read_text(encoding="utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_taxon(taxon: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", taxon.replace(" ", "_").replace(".", ""))


def read_registry(path: Path, design: dict) -> tuple[list[str], list[str], dict[str, dict[str, float]]]:
    if sha256(path) != design["input_registry"]["sha256"]:
        raise ValueError("STOP: native registry hash differs from the frozen design")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    taxa = list(design["fixed_taxa"])
    traits = list(design["fixed_traits"])
    selected = [
        row
        for row in rows
        if row["taxon_concept"] in taxa
        and row["trait_id"] in traits
        and row["admission_status"] == "admitted_comparable_scalar"
    ]
    values: dict[str, dict[str, float]] = {trait: {} for trait in traits}
    for row in selected:
        trait = row["trait_id"]
        taxon = row["taxon_concept"]
        if taxon in values[trait]:
            raise ValueError(f"STOP: duplicate scalar record for {taxon} {trait}")
        values[trait][taxon] = float(row["value"])
    for trait in traits:
        if sorted(values[trait]) != sorted(taxa):
            raise ValueError(f"STOP: frozen seven-taxon panel differs for {trait}")
    complete_traits = sorted(
        trait
        for trait, trait_values in values.items()
        if sorted(trait_values) == sorted(taxa)
    )
    if complete_traits != sorted(traits):
        raise ValueError("STOP: complete-trait set differs from the frozen four-trait design")
    return taxa, traits, values


def read_trees(path: Path, design: dict, taxa: list[str]) -> list:
    expected = design["topology_ensemble"]["au_trees_sha256"]
    if sha256(path) != expected:
        raise ValueError("STOP: AU tree artifact hash differs from the frozen design")
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 6:
        raise ValueError("STOP: fewer than six AU trees")
    expected_tips = {normalize_taxon(taxon) for taxon in taxa}
    trees = []
    for line in lines[:6]:
        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()
        tree = Phylo.read(StringIO(line), "newick")
        terminals = {tip.name: tip for tip in tree.get_terminals()}
        if "OUTGROUP_saff" not in terminals:
            raise ValueError("STOP: AU tree lacks frozen outgroup")
        tree.root_with_outgroup(terminals["OUTGROUP_saff"])
        for tip in list(tree.get_terminals()):
            if tip.name not in expected_tips:
                tree.prune(tip)
        observed = {tip.name for tip in tree.get_terminals()}
        if observed != expected_tips:
            raise ValueError(
                f"STOP: tree/taxon mismatch missing={sorted(expected_tips-observed)} "
                f"extra={sorted(observed-expected_tips)}"
            )
        if any(clade.branch_length is None for clade in tree.find_clades() if clade is not tree.root):
            raise ValueError("STOP: pruned AU tree lacks branch lengths")
        trees.append(tree)
    return trees


def patristic_distances(tree, tip_names: list[str]) -> np.ndarray:
    terminals = {tip.name: tip for tip in tree.get_terminals()}
    return np.asarray(
        [
            float(tree.distance(terminals[tip_names[i]], terminals[tip_names[j]]))
            for i in range(len(tip_names))
            for j in range(i)
        ],
        dtype=float,
    )


def ranked_correlation(left: np.ndarray, right: np.ndarray) -> float:
    x = rankdata(left, method="average").astype(float)
    y = rankdata(right, method="average").astype(float)
    x -= x.mean()
    y -= y.mean()
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= 0:
        raise ValueError("undefined rank correlation")
    return float(x @ y / denominator)


def trait_distances(values: tuple[float, ...] | list[float]) -> np.ndarray:
    return np.asarray(
        [abs(float(values[i]) - float(values[j])) for i in range(len(values)) for j in range(i)],
        dtype=float,
    )


def exact_signal(tree, tip_names: list[str], values: list[float]) -> dict:
    pdist = patristic_distances(tree, tip_names)
    observed = ranked_correlation(pdist, trait_distances(values))
    null = [
        ranked_correlation(pdist, trait_distances(permutation))
        for permutation in itertools.permutations(values)
    ]
    positive = sum(value >= observed for value in null) / len(null)
    negative = sum(value <= observed for value in null) / len(null)
    two_sided = sum(abs(value) >= abs(observed) for value in null) / len(null)
    loo: dict[str, float] = {}
    for omitted in range(len(tip_names)):
        keep_names = [name for index, name in enumerate(tip_names) if index != omitted]
        keep_values = [value for index, value in enumerate(values) if index != omitted]
        loo[tip_names[omitted]] = ranked_correlation(
            patristic_distances(tree, keep_names), trait_distances(keep_values)
        )
    return {
        "rho_patristic_vs_absolute_trait_difference": observed,
        "exact_positive_tail_p": positive,
        "exact_negative_tail_p": negative,
        "exact_two_sided_p": two_sided,
        "exact_label_permutations": len(null),
        "loo_rho_by_omitted_tip": loo,
        "loo_rho_min": min(loo.values()),
        "loo_rho_max": max(loo.values()),
        "loo_all_positive": all(value > 0 for value in loo.values()),
    }


def covariance_matrix(tree, tip_names: list[str]) -> tuple[np.ndarray, float]:
    terminals = {tip.name: tip for tip in tree.get_terminals()}
    matrix = np.zeros((len(tip_names), len(tip_names)), dtype=float)
    for i, left in enumerate(tip_names):
        matrix[i, i] = float(tree.distance(tree.root, terminals[left]))
        for j in range(i):
            right = tip_names[j]
            ancestor = tree.common_ancestor(terminals[left], terminals[right])
            matrix[i, j] = matrix[j, i] = float(tree.distance(tree.root, ancestor))
    scale = float(np.median(np.diag(matrix)))
    if scale <= 0 or np.any(np.diag(matrix) <= 0):
        raise ValueError("invalid Brownian covariance")
    return matrix / scale, scale


def lambda_loglik(values: np.ndarray, covariance: np.ndarray, lam: float) -> float:
    matrix = covariance.copy()
    matrix[~np.eye(len(values), dtype=bool)] *= lam
    matrix[np.diag_indices(len(values))] += 1e-10
    sign, logdet = np.linalg.slogdet(matrix)
    if sign <= 0:
        return -math.inf
    inverse = np.linalg.inv(matrix)
    ones = np.ones(len(values))
    mean = float((ones @ inverse @ values) / (ones @ inverse @ ones))
    residual = values - mean
    variance = max(float(residual @ inverse @ residual / len(values)), 1e-12)
    return float(
        -0.5
        * (
            len(values) * math.log(2 * math.pi)
            + len(values) * math.log(variance)
            + float(logdet)
            + len(values)
        )
    )


def fit_lambda(tree, tip_names: list[str], values: list[float]) -> dict:
    covariance, scale = covariance_matrix(tree, tip_names)
    array = np.asarray(values, dtype=float)
    objective = lambda lam: -lambda_loglik(array, covariance, float(lam))
    optimum = minimize_scalar(objective, bounds=(0.0, 1.0), method="bounded")
    candidates = [0.0, 1.0] + [float(value) for value in np.linspace(0, 1, 101)]
    if optimum.success:
        candidates.append(float(optimum.x))
    scored = [(lambda_loglik(array, covariance, lam), lam) for lam in candidates]
    likelihood, lam = max(scored)
    return {
        "lambda_mle": float(lam),
        "delta_loglik_vs_lambda0": float(likelihood - lambda_loglik(array, covariance, 0.0)),
        "delta_loglik_vs_lambda1": float(likelihood - lambda_loglik(array, covariance, 1.0)),
        "median_root_to_tip_substitutions_per_site": scale,
        "interpretation": "descriptive small-n diagnostic; not an absolute evolutionary rate",
    }


def bh(values: list[float]) -> list[float]:
    array = np.asarray(values, dtype=float)
    order = np.argsort(array)
    ranked = array[order]
    adjusted = np.empty(len(array), dtype=float)
    running = 1.0
    for index in range(len(array) - 1, -1, -1):
        running = min(running, float(ranked[index]) * len(array) / (index + 1))
        adjusted[index] = running
    result = np.empty(len(array), dtype=float)
    result[order] = np.clip(adjusted, 0, 1)
    return [float(value) for value in result]


def analyze(design: dict, registry_path: Path, trees_path: Path) -> tuple[dict, list[dict]]:
    taxa, traits, values = read_registry(registry_path, design)
    trees = read_trees(trees_path, design, taxa)
    tip_names = [normalize_taxon(taxon) for taxon in taxa]
    topology_rows: list[dict] = []
    flat_rows: list[dict] = []
    for topology_index, tree in enumerate(trees, start=1):
        trait_results = []
        for trait in traits:
            trait_values = [values[trait][taxon] for taxon in taxa]
            signal = exact_signal(tree, tip_names, trait_values)
            result = {
                "trait_id": trait,
                "n_taxa": len(taxa),
                "value_min": min(trait_values),
                "value_max": max(trait_values),
                **signal,
                "pagel_lambda": fit_lambda(tree, tip_names, trait_values),
            }
            trait_results.append(result)
        adjusted = bh([row["exact_positive_tail_p"] for row in trait_results])
        for row, q_value in zip(trait_results, adjusted):
            row["positive_tail_bh_q_within_topology"] = q_value
            flat_rows.append(
                {
                    "topology": topology_index,
                    "trait_id": row["trait_id"],
                    "n_taxa": row["n_taxa"],
                    "rho": row["rho_patristic_vs_absolute_trait_difference"],
                    "positive_tail_p": row["exact_positive_tail_p"],
                    "positive_tail_bh_q": q_value,
                    "negative_tail_p": row["exact_negative_tail_p"],
                    "two_sided_p": row["exact_two_sided_p"],
                    "loo_rho_min": row["loo_rho_min"],
                    "loo_rho_max": row["loo_rho_max"],
                    "lambda_mle": row["pagel_lambda"]["lambda_mle"],
                }
            )
        topology_rows.append({"topology": topology_index, "traits": trait_results})

    by_trait = {}
    for trait in traits:
        rows = [row for row in flat_rows if row["trait_id"] == trait]
        supported = all(row["rho"] > 0 and row["positive_tail_bh_q"] < 0.05 for row in rows)
        by_trait[trait] = {
            "rho_min": min(row["rho"] for row in rows),
            "rho_max": max(row["rho"] for row in rows),
            "positive_tail_p_min": min(row["positive_tail_p"] for row in rows),
            "positive_tail_p_max": max(row["positive_tail_p"] for row in rows),
            "positive_tail_bh_q_min": min(row["positive_tail_bh_q"] for row in rows),
            "positive_tail_bh_q_max": max(row["positive_tail_bh_q"] for row in rows),
            "loo_rho_min_across_topologies": min(row["loo_rho_min"] for row in rows),
            "loo_rho_max_across_topologies": max(row["loo_rho_max"] for row in rows),
            "lambda_mle_min": min(row["lambda_mle"] for row in rows),
            "lambda_mle_max": max(row["lambda_mle"] for row in rows),
            "decision": (
                "supported_as_topology_robust_phylogenetic_retention_diagnostic"
                if supported
                else "not_supported_as_topology_robust_phylogenetic_retention"
            ),
        }
    supported_traits = [trait for trait in traits if by_trait[trait]["decision"].startswith("supported")]
    output = {
        "contract_version": "chapter2_eazami_native_continuous_history_diagnostic_v1",
        "status_date": "2026-08-28",
        "design_contract": design["contract_version"],
        "design_sha256": "",
        "registry_sha256": sha256(registry_path),
        "au_trees_sha256": sha256(trees_path),
        "taxa": taxa,
        "traits": traits,
        "topology_count": len(trees),
        "exact_permutations_per_trait_topology": 5040,
        "by_topology": topology_rows,
        "by_trait": by_trait,
        "supported_traits": supported_traits,
        "panel_decision": (
            "supported_at_least_one_topology_robust_retention_diagnostic"
            if supported_traits
            else "not_supported_no_topology_robust_retention_detected"
        ),
        "japan38_transfer": "PROHIBITED_ZERO_ADMITTED_SCALAR_JAPAN38_TIPS",
        "claim_boundary": design["claim_boundary"],
    }
    return output, flat_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stable_numbers(value):
    """Remove numerical-library tail digits before freezing cross-platform output."""
    if isinstance(value, float):
        rounded = float(f"{value:.12g}")
        return 0.0 if rounded == 0 else rounded
    if isinstance(value, list):
        return [stable_numbers(item) for item in value]
    if isinstance(value, dict):
        return {key: stable_numbers(item) for key, item in value.items()}
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--au-trees", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    design = read_json(args.design)
    output, rows = analyze(design, args.registry, args.au_trees)
    output["design_sha256"] = sha256(args.design)
    output = stable_numbers(output)
    rows = stable_numbers(rows)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    write_csv(args.output_csv, rows)
    print(json.dumps({key: output[key] for key in ("panel_decision", "supported_traits", "japan38_transfer")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
