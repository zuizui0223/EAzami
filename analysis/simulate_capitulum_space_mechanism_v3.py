#!/usr/bin/env python3
"""Run the preregistered EAzami capitulum-space mechanism-v3 screen.

The generator emits the same seven estimands frozen in
``capitulum_space_mechanism_v3_contract.json``:

* within- and among-taxon registered-module contrasts;
* within/among association-matrix similarity;
* process-extension partial R2 beyond the four-variable CHELSA core at both
  scales; and
* growing-season-water partial R2 beyond the core at both scales.

The screen is prior-predictive and ABC-like.  It is not a likelihood analysis,
posterior model probability, Bayes factor, or causal inference.  The five model
families share one generator and differ only in declared driver classes and in
whether taxon lability is common across all units or module specific.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HUE_UNIT = "corolla_hue"
HUE_ENDPOINTS = ("corolla_hue_sin", "corolla_hue_cos")
CORE_NAMES = ("bio1", "bio4", "bio12", "bio15")
EXT_NAMES = ("rsds", "vpd", "wind", "gsp", "npp")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--structure", type=Path, required=True)
    p.add_argument("--incremental", type=Path, required=True)
    p.add_argument("--v2-heldout", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--draws-per-seed", type=int)
    p.add_argument("--seeds")
    p.add_argument("--accept-fraction", type=float)
    p.add_argument("--main-taxa", type=int, default=60)
    p.add_argument("--main-populations", type=int, default=6)
    p.add_argument("--replication-taxa", type=int, default=75)
    p.add_argument("--replication-populations", type=int, default=5)
    return p.parse_args()


def stable_seed(base: int, *parts: str) -> int:
    payload = "|".join([str(base), *parts]).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_observed(contract: dict[str, Any], structure_path: Path, incremental_path: Path) -> list[dict[str, Any]]:
    structure = {
        (row["target_id"], row["scope"], row["scale"]): row
        for row in load_csv(structure_path)
    }
    incremental = {
        (row["target_id"], row["scope"], row["scale"]): row
        for row in load_csv(incremental_path)
    }
    resolved: list[dict[str, Any]] = []
    for spec0 in contract["primary_fit_targets"]:
        spec = dict(spec0)
        key = (spec["target_id"], spec["scope"], spec["scale"])
        if spec["target_id"] in {
            "capitulum_within_module_integration_contrast",
            "capitulum_among_module_integration_contrast",
            "capitulum_cross_scale_association_matrix_similarity",
        }:
            row = structure[key]
            spec.update({
                "observed_value": float(row["value"]),
                "ci95_low": float(row["ci95_low"]),
                "ci95_high": float(row["ci95_high"]),
                "observed_support": True,
            })
        else:
            row = incremental[key]
            spec.update({
                "observed_value": float(row["partial_r2"]),
                "observed_support": str(row["supported_0_05"]).lower() == "true",
            })
        resolved.append(spec)
    if len(resolved) != 7:
        raise ValueError(f"Expected seven primary v3 targets, found {len(resolved)}")
    return resolved


def load_v2_heldout(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        row["family"]: float(row["heldout_mean_reproduction_rate"])
        for row in data["families"]
    }


def standardize(a: np.ndarray) -> np.ndarray:
    sd = a.std(axis=0, ddof=0)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 1e-12):
        raise ValueError("Invalid standard deviation")
    return (a - a.mean(axis=0)) / sd


def weighted_standardize(a: np.ndarray, weights: np.ndarray) -> np.ndarray:
    w = weights / weights.sum()
    mean = (w[:, None] * a).sum(axis=0)
    var = (w[:, None] * (a - mean) ** 2).sum(axis=0)
    sd = np.sqrt(var)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 1e-12):
        raise ValueError("Invalid weighted standard deviation")
    return (a - mean) / sd


def weighted_corr(a: np.ndarray, weights: np.ndarray) -> np.ndarray:
    z = weighted_standardize(a, weights)
    w = weights / weights.sum()
    corr = (w[:, None] * z).T @ z
    corr = np.clip((corr + corr.T) / 2.0, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)
    return corr


def corr_matrix(a: np.ndarray) -> np.ndarray:
    return np.corrcoef(a, rowvar=False)


def rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[order[stop]] == values[order[start]]:
            stop += 1
        rank = (start + stop - 1) / 2.0 + 1.0
        ranks[order[start:stop]] = rank
        start = stop
    return ranks


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = rank_average(a)
    br = rank_average(b)
    return float(np.corrcoef(ar, br)[0, 1])


def hue_multiple_r(corr: np.ndarray, other_endpoint: int, hue_indices: tuple[int, int]) -> float:
    idx = np.array(hue_indices)
    r = corr[other_endpoint, idx]
    rx = corr[np.ix_(idx, idx)]
    value = float(r @ np.linalg.pinv(rx) @ r)
    return math.sqrt(max(0.0, min(1.0, value)))


def unit_strength_matrix(
    endpoint_corr: np.ndarray,
    unit_ids: list[str],
    unit_endpoint_indices: dict[str, tuple[int, ...]],
) -> np.ndarray:
    n = len(unit_ids)
    out = np.eye(n, dtype=float)
    hue_idx = tuple(unit_endpoint_indices[HUE_UNIT])
    for i, left in enumerate(unit_ids):
        for j in range(i + 1, n):
            right = unit_ids[j]
            if left == HUE_UNIT:
                value = hue_multiple_r(endpoint_corr, unit_endpoint_indices[right][0], hue_idx)
            elif right == HUE_UNIT:
                value = hue_multiple_r(endpoint_corr, unit_endpoint_indices[left][0], hue_idx)
            else:
                value = abs(float(endpoint_corr[
                    unit_endpoint_indices[left][0], unit_endpoint_indices[right][0]
                ]))
            out[i, j] = out[j, i] = value
    return out


def module_contrast(matrix: np.ndarray, module_index: np.ndarray) -> float:
    within: list[float] = []
    between: list[float] = []
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            (within if module_index[i] == module_index[j] else between).append(float(matrix[i, j]))
    return float(np.mean(within) - np.mean(between))


def upper(matrix: np.ndarray) -> np.ndarray:
    return matrix[np.triu_indices_from(matrix, k=1)]


def fit_multivariate(y: np.ndarray, x: np.ndarray, weights: np.ndarray | None = None) -> float:
    if weights is None:
        yz = standardize(y)
        xz = standardize(x)
        beta = np.linalg.lstsq(xz, yz, rcond=None)[0]
        fitted = xz @ beta
        return float((fitted ** 2).sum() / (yz ** 2).sum())
    yz = weighted_standardize(y, weights)
    xz = weighted_standardize(x, weights)
    root = np.sqrt(weights)[:, None]
    beta = np.linalg.lstsq(xz * root, yz * root, rcond=None)[0]
    fitted = xz @ beta
    return float((weights[:, None] * fitted ** 2).sum() / (weights[:, None] * yz ** 2).sum())


def partial_r2(core: float, full: float) -> float:
    delta = max(0.0, full - core)
    return float(delta / max(1e-12, 1.0 - core))


def taxon_center(a: np.ndarray, taxa: np.ndarray) -> np.ndarray:
    out = a.copy()
    for taxon in np.unique(taxa):
        idx = taxa == taxon
        out[idx] -= out[idx].mean(axis=0)
    return out


def taxon_medians(a: np.ndarray, taxa: np.ndarray) -> np.ndarray:
    return np.vstack([np.median(a[taxa == taxon], axis=0) for taxon in np.unique(taxa)])


def make_registry(contract: dict[str, Any]) -> tuple[list[str], list[str], np.ndarray, dict[str, tuple[int, ...]]]:
    units = contract["inferential_units"]
    unit_ids = [row["unit_id"] for row in units]
    modules = [row["module"] for row in units]
    module_names = list(dict.fromkeys(modules))
    module_lookup = {name: i for i, name in enumerate(module_names)}
    module_index = np.array([module_lookup[name] for name in modules], dtype=int)
    endpoint_indices: dict[str, tuple[int, ...]] = {}
    endpoint_names: list[str] = []
    for unit in unit_ids:
        if unit == HUE_UNIT:
            endpoint_indices[unit] = (len(endpoint_names), len(endpoint_names) + 1)
            endpoint_names.extend(HUE_ENDPOINTS)
        else:
            endpoint_indices[unit] = (len(endpoint_names),)
            endpoint_names.append(unit)
    if len(endpoint_names) != 18:
        raise ValueError("Expected 18 endpoint columns after expanding circular hue")
    return unit_ids, module_names, module_index, endpoint_indices


def draw_parameters(contract: dict[str, Any], family: str, rng: np.random.Generator) -> dict[str, Any]:
    family_row = next(row for row in contract["model_families"] if row["family_id"] == family)
    env_on = bool(family_row["environment"])
    poll_on = bool(family_row["pollinator"])
    ant_on = bool(family_row["antagonist"])
    modular = family == "full_tradeoff_modular_evolvability"
    common = family == "full_tradeoff_common_lability"
    n_modules = 5

    # Driver priors are symmetric in sign.  Magnitudes are module-level and no
    # endpoint receives an individually tuned environmental coefficient.
    core_among = rng.normal(0.0, 0.42, size=(n_modules, 4)) if env_on else np.zeros((n_modules, 4))
    ext_among = rng.normal(0.0, 0.36, size=(n_modules, 5)) if env_on else np.zeros((n_modules, 5))
    core_within = rng.normal(0.0, 0.30, size=(n_modules, 4)) if env_on else np.zeros((n_modules, 4))
    ext_within = rng.normal(0.0, 0.10, size=(n_modules, 5)) if env_on else np.zeros((n_modules, 5))

    poll_among = rng.normal(0.0, 0.40, size=n_modules) if poll_on else np.zeros(n_modules)
    poll_within = rng.normal(0.0, 0.30, size=n_modules) if poll_on else np.zeros(n_modules)
    ant_among = rng.normal(0.0, 0.40, size=n_modules) if ant_on else np.zeros(n_modules)
    ant_within = rng.normal(0.0, 0.30, size=n_modules) if ant_on else np.zeros(n_modules)

    if modular:
        global_among = rng.uniform(0.20, 0.55)
        global_within = rng.uniform(0.10, 0.40)
        module_among = rng.uniform(0.45, 1.00, size=n_modules)
        module_within = rng.uniform(0.60, 1.15, size=n_modules)
        common_lability_sd = 0.0
        module_lability_sd = rng.uniform(0.25, 0.65)
    elif common:
        global_among = rng.uniform(0.65, 1.15)
        global_within = rng.uniform(0.60, 1.10)
        module_among = rng.uniform(0.10, 0.40, size=n_modules)
        module_within = rng.uniform(0.10, 0.40, size=n_modules)
        common_lability_sd = rng.uniform(0.25, 0.60)
        module_lability_sd = 0.0
    else:
        global_among = rng.uniform(0.35, 0.85)
        global_within = rng.uniform(0.30, 0.80)
        module_among = rng.uniform(0.20, 0.70, size=n_modules)
        module_within = rng.uniform(0.20, 0.75, size=n_modules)
        common_lability_sd = rng.uniform(0.10, 0.35)
        module_lability_sd = 0.0

    return {
        "family": family,
        "env_on": env_on,
        "poll_on": poll_on,
        "ant_on": ant_on,
        "modular": modular,
        "common": common,
        "core_among": core_among,
        "ext_among": ext_among,
        "core_within": core_within,
        "ext_within": ext_within,
        "poll_among": poll_among,
        "poll_within": poll_within,
        "ant_among": ant_among,
        "ant_within": ant_within,
        "global_among": global_among,
        "global_within": global_within,
        "module_among": module_among,
        "module_within": module_within,
        "common_lability_sd": common_lability_sd,
        "module_lability_sd": module_lability_sd,
        "cross_scale_alignment": rng.uniform(0.15, 0.75),
        "taxon_noise": rng.uniform(0.35, 0.75),
        "within_noise": rng.uniform(0.50, 0.95),
    }


def correlated_environment(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    # Four low-dimensional core variables.
    raw = rng.normal(size=(n, 4))
    core = np.empty_like(raw)
    core[:, 0] = raw[:, 0]
    core[:, 1] = 0.20 * raw[:, 0] + math.sqrt(0.96) * raw[:, 1]
    core[:, 2] = -0.25 * raw[:, 0] + 0.10 * raw[:, 1] + 0.96 * raw[:, 2]
    core[:, 3] = 0.15 * raw[:, 1] - 0.20 * raw[:, 2] + 0.96 * raw[:, 3]
    core = standardize(core)

    noise = rng.normal(size=(n, 5))
    rsds = 0.55 * core[:, 0] - 0.25 * core[:, 2] + 0.65 * noise[:, 0]
    vpd = 0.65 * core[:, 0] - 0.45 * core[:, 2] + 0.20 * core[:, 3] + 0.55 * noise[:, 1]
    wind = 0.15 * core[:, 1] + 0.90 * noise[:, 2]
    gsp = 0.65 * core[:, 2] - 0.25 * core[:, 3] + 0.60 * noise[:, 3]
    npp = 0.40 * core[:, 0] + 0.55 * core[:, 2] - 0.25 * vpd + 0.60 * noise[:, 4]
    ext = standardize(np.column_stack([rsds, vpd, wind, gsp, npp]))
    return core, ext


def simulate_dataset(
    contract: dict[str, Any],
    params: dict[str, Any],
    n_taxa: int,
    populations_per_taxon: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    units = contract["inferential_units"]
    n_units = len(units)
    module_names = list(dict.fromkeys(row["module"] for row in units))
    module_lookup = {name: i for i, name in enumerate(module_names)}
    unit_module = np.array([module_lookup[row["module"]] for row in units], dtype=int)
    taxa = np.repeat(np.arange(n_taxa), populations_per_taxon)
    n_obs = len(taxa)

    taxon_core, taxon_ext = correlated_environment(rng, n_taxa)
    within_core, within_ext = correlated_environment(rng, n_obs)
    # Population environments are taxon position plus local deviations.  Extension
    # residuals contain much more independent information among taxa than within,
    # matching the biological-scale question without forcing any trait outcome.
    core = taxon_core[taxa] + 0.65 * within_core
    ext = taxon_ext[taxa] + 0.35 * within_ext
    environment = np.column_stack([core, ext])

    poll_taxon = rng.normal(size=n_taxa)
    ant_taxon = rng.normal(size=n_taxa)
    poll_within = rng.normal(size=n_obs)
    ant_within = rng.normal(size=n_obs)
    global_taxon = rng.normal(size=n_taxa)
    global_within = rng.normal(size=n_obs)

    module_taxon = rng.normal(size=(n_taxa, len(module_names)))
    module_within = rng.normal(size=(n_obs, len(module_names)))
    align = float(params["cross_scale_alignment"])
    module_within = align * module_taxon[taxa] + math.sqrt(max(0.0, 1.0 - align ** 2)) * module_within

    if params["modular"]:
        taxon_lability = np.exp(rng.normal(-0.10, params["module_lability_sd"], size=(n_taxa, len(module_names))))
    else:
        common = np.exp(rng.normal(-0.10, params["common_lability_sd"], size=n_taxa))
        taxon_lability = np.repeat(common[:, None], len(module_names), axis=1)

    unit_values = np.zeros((n_obs, n_units), dtype=float)
    for module_idx in range(len(module_names)):
        units_idx = np.flatnonzero(unit_module == module_idx)
        lability = taxon_lability[taxa, module_idx]
        among_signal = (
            params["global_among"] * global_taxon[taxa]
            + params["module_among"][module_idx] * module_taxon[taxa, module_idx]
            + taxon_core[taxa] @ params["core_among"][module_idx]
            + taxon_ext[taxa] @ params["ext_among"][module_idx]
            + params["poll_among"][module_idx] * poll_taxon[taxa]
            + params["ant_among"][module_idx] * ant_taxon[taxa]
        )
        within_signal = (
            params["global_within"] * global_within
            + params["module_within"][module_idx] * module_within[:, module_idx]
            + within_core @ params["core_within"][module_idx]
            + within_ext @ params["ext_within"][module_idx]
            + params["poll_within"][module_idx] * poll_within
            + params["ant_within"][module_idx] * ant_within
        )
        shared = lability * (among_signal + within_signal)
        for unit_idx in units_idx:
            unit_values[:, unit_idx] = (
                shared
                + rng.normal(0.0, params["taxon_noise"], size=n_taxa)[taxa]
                + rng.normal(0.0, params["within_noise"], size=n_obs)
            )

    # Expand the circular hue unit into sine/cosine endpoints while keeping hue as
    # one inferential unit for association-strength summaries.
    endpoint_columns: list[np.ndarray] = []
    for unit_idx, row in enumerate(units):
        values = unit_values[:, unit_idx]
        if row["unit_id"] == HUE_UNIT:
            angle = np.pi + 0.85 * values
            endpoint_columns.extend([np.sin(angle), np.cos(angle)])
        else:
            endpoint_columns.append(values)
    endpoints = np.column_stack(endpoint_columns)
    return endpoints, environment, taxa


def summarize_dataset(
    contract: dict[str, Any],
    endpoints: np.ndarray,
    environment: np.ndarray,
    taxa: np.ndarray,
) -> dict[str, float]:
    unit_ids, _modules, module_index, endpoint_index = make_registry(contract)
    centered_y = taxon_center(endpoints, taxa)
    counts = np.bincount(taxa)
    weights = 1.0 / counts[taxa]
    within_endpoint_corr = weighted_corr(centered_y, weights)
    among_y = taxon_medians(endpoints, taxa)
    among_endpoint_corr = corr_matrix(among_y)
    within_units = unit_strength_matrix(within_endpoint_corr, unit_ids, endpoint_index)
    among_units = unit_strength_matrix(among_endpoint_corr, unit_ids, endpoint_index)

    centered_env = taxon_center(environment, taxa)
    among_env = taxon_medians(environment, taxa)
    core_w = fit_multivariate(centered_y, centered_env[:, :4], weights)
    full_w = fit_multivariate(centered_y, centered_env, weights)
    gsp_w = fit_multivariate(centered_y, centered_env[:, [0, 1, 2, 3, 7]], weights)
    core_a = fit_multivariate(among_y, among_env[:, :4])
    full_a = fit_multivariate(among_y, among_env)
    gsp_a = fit_multivariate(among_y, among_env[:, [0, 1, 2, 3, 7]])

    return {
        "capitulum_within_module_integration_contrast": module_contrast(within_units, module_index),
        "capitulum_among_module_integration_contrast": module_contrast(among_units, module_index),
        "capitulum_cross_scale_association_matrix_similarity": spearman(upper(within_units), upper(among_units)),
        "within_process_partial_r2": partial_r2(core_w, full_w),
        "among_process_partial_r2": partial_r2(core_a, full_a),
        "within_gsp_partial_r2": partial_r2(core_w, gsp_w),
        "among_gsp_partial_r2": partial_r2(core_a, gsp_a),
        "within_core_r2": core_w,
        "among_core_r2": core_a,
    }


def target_summary_key(target: dict[str, Any]) -> str:
    target_id = target["target_id"]
    scale = target["scale"]
    if target_id == "capitulum_within_module_integration_contrast":
        return target_id
    if target_id == "capitulum_among_module_integration_contrast":
        return target_id
    if target_id == "capitulum_cross_scale_association_matrix_similarity":
        return target_id
    if target_id.endswith("all_process_extension_beyond_core4"):
        return "within_process_partial_r2" if scale == "within_taxon" else "among_process_partial_r2"
    if target_id.endswith("growing_season_water_input_beyond_core4"):
        return "within_gsp_partial_r2" if scale == "within_taxon" else "among_gsp_partial_r2"
    raise KeyError(target_id)


def huber(z: float) -> float:
    z = abs(float(z))
    value = 0.5 * z * z if z <= 1.0 else z - 0.5
    return min(6.0, value)


def generated_support(target: dict[str, Any], value: float) -> bool:
    if target["target_id"].startswith("capitulum_"):
        return value > 0
    tolerance = float(target["tolerance"])
    observed = float(target["observed_value"])
    if bool(target["expected_support"]):
        threshold = max(0.02, observed - tolerance)
    else:
        threshold = tolerance
    return value >= threshold


def primary_distance(targets: list[dict[str, Any]], summary: dict[str, float]) -> tuple[float, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    weighted = 0.0
    total_weight = 0.0
    for target in targets:
        key = target_summary_key(target)
        value = float(summary[key])
        observed = float(target["observed_value"])
        weight = float(target["weight"])
        if target["distance"] == "bootstrap_standardized_huber":
            sigma = max(0.01, (float(target["ci95_high"]) - float(target["ci95_low"])) / 3.92)
            numeric = huber((value - observed) / sigma)
            support_match = value > 0
        else:
            tolerance = float(target["tolerance"])
            numeric = huber((value - observed) / tolerance)
            support_match = generated_support(target, value) == bool(target["expected_support"])
        component = numeric + (0.0 if support_match else 1.0)
        weighted += weight * component
        total_weight += weight
        rows.append({
            "target_id": target["target_id"],
            "scope": target["scope"],
            "scale": target["scale"],
            "observed": observed,
            "simulated": value,
            "support_match": support_match,
            "distance_component": component,
            "weight": weight,
        })
    return weighted / total_weight, rows


def replication_rate(summary: dict[str, float], targets: list[dict[str, Any]]) -> float:
    by = {(row["target_id"], row["scale"]): row for row in targets}
    among_process = by[("environment_incremental:all_process_extension_beyond_core4", "among_taxon")]
    among_gsp = by[("environment_incremental:growing_season_water_input_beyond_core4", "among_taxon")]
    checks = [
        summary["capitulum_within_module_integration_contrast"] > 0,
        summary["capitulum_among_module_integration_contrast"] > 0,
        summary["capitulum_cross_scale_association_matrix_similarity"] > 0,
        summary["within_process_partial_r2"] <= 0.03,
        summary["among_process_partial_r2"] >= max(0.02, float(among_process["observed_value"]) - float(among_process["tolerance"])),
        summary["among_gsp_partial_r2"] >= max(0.02, float(among_gsp["observed_value"]) - float(among_gsp["tolerance"])),
    ]
    return float(sum(checks) / len(checks))


def quantile(values: list[float], q: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), q))


def run_screen(
    contract: dict[str, Any],
    targets: list[dict[str, Any]],
    v2_heldout: dict[str, float],
    draws_per_seed: int,
    seeds: list[int],
    accept_fraction: float,
    main_taxa: int,
    main_populations: int,
    replication_taxa: int,
    replication_populations: int,
) -> dict[str, Any]:
    family_results: list[dict[str, Any]] = []
    all_draw_rows: list[dict[str, Any]] = []

    for family_row in contract["model_families"]:
        family = family_row["family_id"]
        draws: list[dict[str, Any]] = []
        for seed in seeds:
            for draw_idx in range(draws_per_seed):
                rng = np.random.default_rng(stable_seed(seed, family, str(draw_idx), "parameters"))
                params = draw_parameters(contract, family, rng)
                main_rng = np.random.default_rng(stable_seed(seed, family, str(draw_idx), "main"))
                main_data = simulate_dataset(contract, params, main_taxa, main_populations, main_rng)
                main_summary = summarize_dataset(contract, *main_data)
                distance, components = primary_distance(targets, main_summary)
                rep_rng = np.random.default_rng(stable_seed(seed, family, str(draw_idx), "replication"))
                rep_data = simulate_dataset(contract, params, replication_taxa, replication_populations, rep_rng)
                rep_summary = summarize_dataset(contract, *rep_data)
                rep_rate = replication_rate(rep_summary, targets)
                row = {
                    "family": family,
                    "seed": seed,
                    "draw_index": draw_idx,
                    "primary_distance": distance,
                    "replication_pattern_rate": rep_rate,
                    "main_summary": main_summary,
                    "replication_summary": rep_summary,
                    "distance_components": components,
                }
                draws.append(row)
                all_draw_rows.append({
                    "family": family,
                    "seed": seed,
                    "draw_index": draw_idx,
                    "primary_distance": distance,
                    "replication_pattern_rate": rep_rate,
                    **{f"main_{k}": v for k, v in main_summary.items()},
                })

        draws.sort(key=lambda row: row["primary_distance"])
        n_accept = max(int(contract["family_comparison"]["minimum_accepted_draws"]), math.ceil(len(draws) * accept_fraction))
        accepted = draws[:n_accept]
        seed_summaries = []
        for seed in seeds:
            subset = sorted((row for row in draws if row["seed"] == seed), key=lambda row: row["primary_distance"])
            n_seed_accept = max(1, math.ceil(len(subset) * accept_fraction))
            seed_acc = subset[:n_seed_accept]
            seed_summaries.append({
                "seed": seed,
                "accepted_draws": len(seed_acc),
                "primary_distance_median": float(np.median([row["primary_distance"] for row in seed_acc])),
                "replication_pattern_rate_mean": float(np.mean([row["replication_pattern_rate"] for row in seed_acc])),
            })
        distances = [row["primary_distance"] for row in accepted]
        family_results.append({
            "family": family,
            "total_draws": len(draws),
            "accepted_draws": len(accepted),
            "accept_fraction": accept_fraction,
            "best_primary_distance": distances[0],
            "primary_distance_median": float(np.median(distances)),
            "primary_distance_q10_q90": [quantile(distances, 0.10), quantile(distances, 0.90)],
            "replication_pattern_rate_mean": float(np.mean([row["replication_pattern_rate"] for row in accepted])),
            "existing_v2_heldout_rate": float(v2_heldout[family]),
            "seed_summaries": seed_summaries,
            "best_main_summary": accepted[0]["main_summary"],
            "best_replication_summary": accepted[0]["replication_summary"],
            "best_distance_components": accepted[0]["distance_components"],
        })

    ranking = sorted(
        family_results,
        key=lambda row: (
            row["primary_distance_median"],
            -row["replication_pattern_rate_mean"],
            -row["existing_v2_heldout_rate"],
        ),
    )
    by_family = {row["family"]: row for row in family_results}
    focal = ["full_tradeoff_common_lability", "full_tradeoff_modular_evolvability"]
    focal_sorted = sorted(focal, key=lambda fam: by_family[fam]["primary_distance_median"])
    winner, other = focal_sorted
    winner_seed = {row["seed"]: row for row in by_family[winner]["seed_summaries"]}
    other_seed = {row["seed"]: row for row in by_family[other]["seed_summaries"]}
    seedwise_stable = all(
        winner_seed[seed]["primary_distance_median"] < other_seed[seed]["primary_distance_median"]
        for seed in seeds
    )
    replication_not_worse = (
        by_family[winner]["replication_pattern_rate_mean"]
        >= by_family[other]["replication_pattern_rate_mean"] - 1e-12
    )
    heldout_not_worse = (
        by_family[winner]["existing_v2_heldout_rate"]
        >= by_family[other]["existing_v2_heldout_rate"] - 1e-12
    )
    decision = winner if seedwise_stable and replication_not_worse and heldout_not_worse else "unresolved"

    return {
        "contract_version": contract["contract_version"],
        "screen_version": "capitulum_space_mechanism_v3_screen_1",
        "status": "completed_prior_predictive_structural_sufficiency_screen",
        "draws_per_seed_per_family": draws_per_seed,
        "seeds": seeds,
        "accept_fraction": accept_fraction,
        "main_simulation": {"n_taxa": main_taxa, "populations_per_taxon": main_populations},
        "replication_simulation": {"n_taxa": replication_taxa, "populations_per_taxon": replication_populations},
        "families": family_results,
        "ranking": [row["family"] for row in ranking],
        "focal_common_vs_modular": {
            "distance_winner": winner,
            "other": other,
            "seedwise_distance_winner_stable": seedwise_stable,
            "replication_not_worse": replication_not_worse,
            "independent_v2_heldout_not_worse": heldout_not_worse,
            "registered_decision": decision,
        },
        "interpretation_boundary": (
            "ABC-like prior-predictive structural sufficiency under the frozen v3 contract. "
            "Not a likelihood, posterior model probability, Bayes factor, functional/genetic "
            "modularity estimate, selection test, adaptation test, plasticity test, or unique causal mechanism."
        ),
        "_draw_rows": all_draw_rows,
    }


def write_outputs(out_dir: Path, result: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    draw_rows = result.pop("_draw_rows")
    result_path = out_dir / "capitulum_space_mechanism_v3_result.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if draw_rows:
        fields = list(draw_rows[0].keys())
        with (out_dir / "capitulum_space_mechanism_v3_draws.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(draw_rows)
    print(json.dumps(result, indent=2))


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    comparison = contract["family_comparison"]
    draws = args.draws_per_seed or int(comparison["draws_per_seed_per_family"])
    seeds = (
        [int(x) for x in args.seeds.split(",") if x.strip()]
        if args.seeds else [int(x) for x in comparison["seeds"]]
    )
    accept_fraction = args.accept_fraction or float(comparison["accept_fraction"])
    if draws <= 0 or not seeds or not 0 < accept_fraction <= 0.2:
        raise ValueError("Invalid screen parameters")
    targets = load_observed(contract, args.structure, args.incremental)
    v2_heldout = load_v2_heldout(args.v2_heldout)
    result = run_screen(
        contract,
        targets,
        v2_heldout,
        draws,
        seeds,
        accept_fraction,
        args.main_taxa,
        args.main_populations,
        args.replication_taxa,
        args.replication_populations,
    )
    write_outputs(args.out_dir, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
