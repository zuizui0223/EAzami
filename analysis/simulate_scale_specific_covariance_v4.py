#!/usr/bin/env python3
"""Run the registered scale-specific covariance v4 structural screen.

All v4 families inherit the same full environment + pollinator + antagonist
interaction layer and the same v3.1 common-lability baseline priors.  They differ
only by predeclared covariance additions: a taxon-centred within-only module
factor, exchangeable unit-level among-taxon environmental loadings, and an
optional low-rank taxon-level rotation.

The screen reuses the seven frozen v3.1 fit targets unchanged, evaluates the
>=2 scope as an out-of-fit replication pattern, and holds twelve main-scope
stand-alone environmental-block R2 values as context validation.  It is a
nested prior-predictive structural-sufficiency screen, not likelihood-based or
causal model selection.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import simulate_capitulum_space_mechanism_v3 as v3  # noqa: E402


BLOCKS = {
    "core_thermal": [0, 1],
    "core_precipitation": [2, 3],
    "radiative_atmospheric_drying": [4, 5],
    "mechanical_exposure": [6],
    "growing_season_water_input": [7],
    "climatic_productivity": [8],
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--priors", type=Path, required=True)
    p.add_argument("--v3-contract", type=Path, required=True)
    p.add_argument("--structure", type=Path, required=True)
    p.add_argument("--environment", type=Path, required=True)
    p.add_argument("--incremental", type=Path, required=True)
    p.add_argument("--v2-heldout", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--draws-per-seed", type=int)
    p.add_argument("--seeds")
    p.add_argument("--accept-fraction", type=float)
    return p.parse_args()


def stable_seed(base: int, *parts: str) -> int:
    payload = "|".join([str(base), *parts]).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(out):
        raise ValueError(f"{label} must be finite")
    return out


def validate_priors(contract: dict[str, Any], priors: dict[str, Any]) -> None:
    if priors.get("version") != "scale_specific_covariance_v4_implementation_priors_2026-08-27":
        raise ValueError("Unexpected v4 implementation-prior version")
    if priors.get("status") != "frozen_before_v4_family_outcomes":
        raise ValueError("v4 priors must remain frozen before outcomes")
    if priors.get("parent_contract") != "data/contracts/scale_specific_covariance_v4_contract.json":
        raise ValueError("v4 prior parent contract changed")
    if contract.get("contract_version") != "scale_specific_covariance_v4_2026-08-27":
        raise ValueError("Unexpected v4 contract version")
    sizes = priors["simulation_sizes"]
    if (sizes["main_taxa"], sizes["main_populations_per_taxon"], sizes["replication_taxa"], sizes["replication_populations_per_taxon"]) != (60, 6, 75, 5):
        raise ValueError("Registered v4 simulation sizes changed")
    for section, expected in [
        ("within_only_module_factor", (0.05, 0.50)),
        ("among_unit_mosaic_loadings.core_scale_distribution", (0.05, 0.35)),
        ("among_unit_mosaic_loadings.process_scale_distribution", (0.25, 0.90)),
        ("historical_rotation", (0.10, 0.70)),
    ]:
        if "." in section:
            first, second = section.split(".")
            dist = priors[first][second]
        elif section == "within_only_module_factor":
            dist = priors[section]["common_scale_distribution"]
        else:
            dist = priors[section]["scale_distribution"]
        if (finite(dist["low"], section), finite(dist["high"], section)) != expected:
            raise ValueError(f"Registered prior range changed for {section}")


def load_context_targets(path: Path) -> dict[tuple[str, str], float]:
    rows = load_csv(path)
    result: dict[tuple[str, str], float] = {}
    for row in rows:
        if not row["target_id"].startswith("environment_block_r2:"):
            continue
        if row["scope"] != "complete18_env_min5":
            continue
        block = row["target_id"].split(":", 1)[1]
        key = (block, row["scale"])
        result[key] = finite(row["value"], f"context target {key}")
    expected = {(block, scale) for block in BLOCKS for scale in ("within_taxon", "among_taxon")}
    if set(result) != expected:
        raise ValueError(f"Expected twelve main context R2 targets; found {sorted(result)}")
    return result


def module_registry(v3_contract: dict[str, Any]) -> tuple[list[str], list[str], np.ndarray, dict[str, tuple[int, ...]]]:
    unit_ids, module_names, module_index, endpoint_index = v3.make_registry(v3_contract)
    return unit_ids, module_names, module_index, endpoint_index


def centre_by_taxon(values: np.ndarray, taxa: np.ndarray) -> np.ndarray:
    out = values.copy()
    for taxon in np.unique(taxa):
        idx = taxa == taxon
        out[idx] -= out[idx].mean(axis=0)
    return out


def unit_effects_to_endpoints(
    endpoints: np.ndarray,
    unit_effects: np.ndarray,
    unit_ids: list[str],
    endpoint_index: dict[str, tuple[int, ...]],
) -> np.ndarray:
    out = endpoints.copy()
    for unit_idx, unit_id in enumerate(unit_ids):
        effect = unit_effects[:, unit_idx]
        indices = endpoint_index[unit_id]
        if unit_id == v3.HUE_UNIT:
            sin_idx, cos_idx = indices
            angle = np.arctan2(out[:, sin_idx], out[:, cos_idx]) + effect
            out[:, sin_idx] = np.sin(angle)
            out[:, cos_idx] = np.cos(angle)
        else:
            out[:, indices[0]] += effect
    return out


def rms_normalize_within_modules(loadings: np.ndarray, module_index: np.ndarray) -> np.ndarray:
    out = loadings.copy()
    for module in np.unique(module_index):
        idx = module_index == module
        rms = math.sqrt(float(np.mean(out[idx] ** 2)))
        if rms > 0:
            out[idx] /= rms
    return out


def centred_mosaic_loadings(
    rng: np.random.Generator,
    n_units: int,
    n_predictors: int,
    module_index: np.ndarray,
) -> np.ndarray:
    loadings = rng.normal(size=(n_units, n_predictors))
    for module in np.unique(module_index):
        idx = module_index == module
        loadings[idx] -= loadings[idx].mean(axis=0, keepdims=True)
    for predictor in range(n_predictors):
        rms = math.sqrt(float(np.mean(loadings[:, predictor] ** 2)))
        if rms > 1e-12:
            loadings[:, predictor] /= rms
    return loadings


def add_within_only_factor(
    endpoints: np.ndarray,
    taxa: np.ndarray,
    unit_ids: list[str],
    module_index: np.ndarray,
    endpoint_index: dict[str, tuple[int, ...]],
    priors: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[str, float]]:
    n_obs = len(endpoints)
    n_modules = int(module_index.max()) + 1
    factors = centre_by_taxon(rng.normal(size=(n_obs, n_modules)), taxa)
    raw_loadings = rng.normal(size=len(unit_ids))
    loadings = rms_normalize_within_modules(raw_loadings[:, None], module_index)[:, 0]
    scale_dist = priors["within_only_module_factor"]["common_scale_distribution"]
    scale = rng.uniform(scale_dist["low"], scale_dist["high"])
    effects = scale * factors[:, module_index] * loadings[None, :]
    return unit_effects_to_endpoints(endpoints, effects, unit_ids, endpoint_index), {
        "within_only_module_scale": float(scale),
    }


def add_among_mosaic(
    endpoints: np.ndarray,
    environment: np.ndarray,
    taxa: np.ndarray,
    unit_ids: list[str],
    module_index: np.ndarray,
    endpoint_index: dict[str, tuple[int, ...]],
    priors: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[str, float]]:
    taxon_env = v3.taxon_medians(environment, taxa)
    core_loadings = centred_mosaic_loadings(rng, len(unit_ids), 4, module_index)
    process_loadings = centred_mosaic_loadings(rng, len(unit_ids), 5, module_index)
    core_dist = priors["among_unit_mosaic_loadings"]["core_scale_distribution"]
    process_dist = priors["among_unit_mosaic_loadings"]["process_scale_distribution"]
    core_scale = rng.uniform(core_dist["low"], core_dist["high"])
    process_scale = rng.uniform(process_dist["low"], process_dist["high"])
    taxon_effects = (
        core_scale * (taxon_env[:, :4] @ core_loadings.T)
        + process_scale * (taxon_env[:, 4:] @ process_loadings.T)
    )
    effects = taxon_effects[taxa]
    return unit_effects_to_endpoints(endpoints, effects, unit_ids, endpoint_index), {
        "among_mosaic_core_scale": float(core_scale),
        "among_mosaic_process_scale": float(process_scale),
    }


def add_historical_rotation(
    endpoints: np.ndarray,
    taxa: np.ndarray,
    unit_ids: list[str],
    endpoint_index: dict[str, tuple[int, ...]],
    priors: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[str, float]]:
    rotation = priors["historical_rotation"]
    rank = int(rng.choice(rotation["rank_distribution"]["values"]))
    q, _ = np.linalg.qr(rng.normal(size=(len(unit_ids), rank)))
    scores = rng.normal(size=(int(taxa.max()) + 1, rank))
    scale_dist = rotation["scale_distribution"]
    scale = rng.uniform(scale_dist["low"], scale_dist["high"])
    taxon_effects = scale * (scores @ q[:, :rank].T)
    return unit_effects_to_endpoints(endpoints, taxon_effects[taxa], unit_ids, endpoint_index), {
        "historical_rotation_rank": float(rank),
        "historical_rotation_scale": float(scale),
    }


def family_row(contract: dict[str, Any], family_id: str) -> dict[str, Any]:
    return next(row for row in contract["model_families"] if row["family_id"] == family_id)


def simulate_family_dataset(
    v4_contract: dict[str, Any],
    priors: dict[str, Any],
    v3_contract: dict[str, Any],
    family_id: str,
    shared_params_seed: int,
    shared_data_seed: int,
    addition_seed: int,
    n_taxa: int,
    populations_per_taxon: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    params_rng = np.random.default_rng(shared_params_seed)
    params = v3.draw_parameters(v3_contract, "full_tradeoff_common_lability", params_rng)
    family = family_row(v4_contract, family_id)
    if family["among_unit_mosaic_loadings"]:
        params = copy.deepcopy(params)
        params["core_among"] = np.zeros_like(params["core_among"])
        params["ext_among"] = np.zeros_like(params["ext_among"])
    endpoints, environment, taxa = v3.simulate_dataset(
        v3_contract,
        params,
        n_taxa,
        populations_per_taxon,
        np.random.default_rng(shared_data_seed),
    )
    unit_ids, _module_names, module_index, endpoint_index = module_registry(v3_contract)
    rng = np.random.default_rng(addition_seed)
    parameters: dict[str, float] = {}
    if family["within_only_module_factor"]:
        endpoints, drawn = add_within_only_factor(
            endpoints, taxa, unit_ids, module_index, endpoint_index, priors, rng
        )
        parameters.update(drawn)
    if family["among_unit_mosaic_loadings"]:
        endpoints, drawn = add_among_mosaic(
            endpoints, environment, taxa, unit_ids, module_index, endpoint_index, priors, rng
        )
        parameters.update(drawn)
    if family["historical_rotation"]:
        endpoints, drawn = add_historical_rotation(
            endpoints, taxa, unit_ids, endpoint_index, priors, rng
        )
        parameters.update(drawn)
    return endpoints, environment, taxa, parameters


def block_r2_summary(endpoints: np.ndarray, environment: np.ndarray, taxa: np.ndarray) -> dict[str, float]:
    centred_y = v3.taxon_center(endpoints, taxa)
    centred_env = v3.taxon_center(environment, taxa)
    counts = np.bincount(taxa)
    weights = 1.0 / counts[taxa]
    among_y = v3.taxon_medians(endpoints, taxa)
    among_env = v3.taxon_medians(environment, taxa)
    out: dict[str, float] = {}
    for block, columns in BLOCKS.items():
        out[f"context_r2:{block}:within_taxon"] = v3.fit_multivariate(
            centred_y, centred_env[:, columns], weights
        )
        out[f"context_r2:{block}:among_taxon"] = v3.fit_multivariate(
            among_y, among_env[:, columns]
        )
    return out


def summarize(
    v3_contract: dict[str, Any],
    endpoints: np.ndarray,
    environment: np.ndarray,
    taxa: np.ndarray,
) -> dict[str, float]:
    result = v3.summarize_dataset(v3_contract, endpoints, environment, taxa)
    result.update(block_r2_summary(endpoints, environment, taxa))
    return result


def context_rmse(summary: dict[str, float], observed: dict[tuple[str, str], float]) -> float:
    errors = []
    for (block, scale), target in observed.items():
        value = summary[f"context_r2:{block}:{scale}"]
        errors.append((value - target) ** 2)
    return math.sqrt(float(np.mean(errors)))


def accepted_count(total_draws: int, contract: dict[str, Any]) -> int:
    screen = contract["screen_design"]
    return max(
        int(screen["minimum_accepted_draws"]),
        math.ceil(total_draws * float(screen["accept_fraction"])),
    )


def feature_set(row: dict[str, Any]) -> frozenset[str]:
    return frozenset(
        key for key in [
            "within_only_module_factor",
            "among_unit_mosaic_loadings",
            "historical_rotation",
        ]
        if row[key]
    )


def nested(left: dict[str, Any], right: dict[str, Any]) -> bool:
    a, b = feature_set(left), feature_set(right)
    return a.issubset(b) or b.issubset(a)


def run_screen(
    v4_contract: dict[str, Any],
    priors: dict[str, Any],
    v3_contract: dict[str, Any],
    targets: list[dict[str, Any]],
    context_targets: dict[tuple[str, str], float],
    inherited_heldout: float,
    draws_per_seed: int,
    seeds: list[int],
) -> dict[str, Any]:
    sizes = priors["simulation_sizes"]
    family_results: list[dict[str, Any]] = []
    draw_rows: list[dict[str, Any]] = []

    for family in v4_contract["model_families"]:
        family_id = family["family_id"]
        draws: list[dict[str, Any]] = []
        for seed in seeds:
            for draw_index in range(draws_per_seed):
                shared_params_seed = stable_seed(seed, str(draw_index), "shared_params")
                main_data_seed = stable_seed(seed, str(draw_index), "main_data")
                replication_data_seed = stable_seed(seed, str(draw_index), "replication_data")
                main = simulate_family_dataset(
                    v4_contract,
                    priors,
                    v3_contract,
                    family_id,
                    shared_params_seed,
                    main_data_seed,
                    stable_seed(seed, family_id, str(draw_index), "main_additions"),
                    sizes["main_taxa"],
                    sizes["main_populations_per_taxon"],
                )
                main_summary = summarize(v3_contract, main[0], main[1], main[2])
                distance, _components = v3.primary_distance(targets, main_summary)
                main_context = context_rmse(main_summary, context_targets)
                replication = simulate_family_dataset(
                    v4_contract,
                    priors,
                    v3_contract,
                    family_id,
                    shared_params_seed,
                    replication_data_seed,
                    stable_seed(seed, family_id, str(draw_index), "replication_additions"),
                    sizes["replication_taxa"],
                    sizes["replication_populations_per_taxon"],
                )
                replication_summary = summarize(
                    v3_contract, replication[0], replication[1], replication[2]
                )
                replication_rate = v3.replication_rate(replication_summary, targets)
                row = {
                    "family": family_id,
                    "seed": seed,
                    "draw_index": draw_index,
                    "primary_distance": distance,
                    "replication_pattern_rate": replication_rate,
                    "context_r2_rmse": main_context,
                    "parameters": main[3],
                    "main_summary": main_summary,
                }
                draws.append(row)
                draw_rows.append({
                    "family": family_id,
                    "seed": seed,
                    "draw_index": draw_index,
                    "primary_distance": distance,
                    "replication_pattern_rate": replication_rate,
                    "context_r2_rmse": main_context,
                    **{f"main_{key}": value for key, value in main_summary.items()},
                    **{f"parameter_{key}": value for key, value in main[3].items()},
                })

        draws.sort(key=lambda row: row["primary_distance"])
        n_accept = accepted_count(len(draws), v4_contract)
        accepted = draws[:n_accept]
        seed_summaries = []
        for seed in seeds:
            subset = sorted(
                (row for row in draws if row["seed"] == seed),
                key=lambda row: row["primary_distance"],
            )
            n_seed = max(1, math.ceil(len(subset) * float(v4_contract["screen_design"]["accept_fraction"])))
            accepted_seed = subset[:n_seed]
            seed_summaries.append({
                "seed": seed,
                "accepted_draws": len(accepted_seed),
                "primary_distance_median": float(np.median([row["primary_distance"] for row in accepted_seed])),
                "replication_pattern_rate_mean": float(np.mean([row["replication_pattern_rate"] for row in accepted_seed])),
                "context_r2_rmse_median": float(np.median([row["context_r2_rmse"] for row in accepted_seed])),
            })
        family_results.append({
            "family": family_id,
            "complexity_level": family["complexity_level"],
            "parent_family": family["parent_family"],
            "features": sorted(feature_set(family)),
            "total_draws": len(draws),
            "accepted_draws": len(accepted),
            "best_primary_distance": float(accepted[0]["primary_distance"]),
            "primary_distance_median": float(np.median([row["primary_distance"] for row in accepted])),
            "primary_distance_q10_q90": [
                float(np.quantile([row["primary_distance"] for row in accepted], 0.10)),
                float(np.quantile([row["primary_distance"] for row in accepted], 0.90)),
            ],
            "replication_pattern_rate_mean": float(np.mean([row["replication_pattern_rate"] for row in accepted])),
            "context_r2_rmse_median": float(np.median([row["context_r2_rmse"] for row in accepted])),
            "inherited_independent_heldout_rate": inherited_heldout,
            "seed_summaries": seed_summaries,
            "best_main_summary": accepted[0]["main_summary"],
            "best_parameters": accepted[0]["parameters"],
        })

    by = {row["family"]: row for row in family_results}
    screen = v4_contract["screen_design"]
    absolute_threshold = float(screen["absolute_primary_adequacy_threshold"])
    replication_threshold = float(screen["minimum_replication_pattern_rate"])
    improvement_threshold = float(screen["minimum_relative_primary_distance_improvement_over_parent"])
    context_limit = float(screen["maximum_context_r2_rmse_increase_relative_to_parent"])

    for family in v4_contract["model_families"]:
        row = by[family["family_id"]]
        parent_id = family["parent_family"]
        absolute = row["primary_distance_median"] <= absolute_threshold
        replication_ok = row["replication_pattern_rate_mean"] >= replication_threshold
        if parent_id is None:
            improvement = None
            improvement_ok = True
            context_ratio = None
            context_ok = True
            seedwise_count = 4
            seedwise_ok = True
        else:
            parent = by[parent_id]
            improvement = (
                parent["primary_distance_median"] - row["primary_distance_median"]
            ) / max(abs(parent["primary_distance_median"]), 1e-12)
            improvement_ok = improvement >= improvement_threshold
            context_ratio = row["context_r2_rmse_median"] / max(parent["context_r2_rmse_median"], 1e-12)
            context_ok = context_ratio <= 1.0 + context_limit
            parent_seeds = {x["seed"]: x for x in parent["seed_summaries"]}
            seedwise_count = sum(
                child["primary_distance_median"] <= parent_seeds[child["seed"]]["primary_distance_median"]
                for child in row["seed_summaries"]
            )
            seedwise_ok = seedwise_count >= 3
        row["eligibility_gates"] = {
            "absolute_primary_adequacy": absolute,
            "replication_adequacy": replication_ok,
            "relative_improvement_over_parent": improvement,
            "relative_improvement_gate": improvement_ok,
            "context_rmse_ratio_to_parent": context_ratio,
            "context_gate": context_ok,
            "seedwise_not_worse_count": seedwise_count,
            "seedwise_gate": seedwise_ok,
        }
        row["eligible"] = bool(
            absolute and replication_ok and improvement_ok and context_ok and seedwise_ok
        )

    eligible = [row for row in family_results if row["eligible"]]
    if not eligible:
        registered_decision = "no_adequate_family"
        selected_families: list[str] = []
        selection_reason = "all_families_failed_one_or_more_preregistered_gates"
    else:
        best_distance = min(row["primary_distance_median"] for row in eligible)
        near_best = [
            row for row in eligible
            if row["primary_distance_median"] <= best_distance * 1.05
        ]
        contract_rows = {row["family_id"]: row for row in v4_contract["model_families"]}
        nonnested_pair = any(
            not nested(contract_rows[left["family"]], contract_rows[right["family"]])
            for i, left in enumerate(near_best)
            for right in near_best[i + 1:]
        )
        if nonnested_pair:
            registered_decision = "structural_nonidentifiability"
            selected_families = sorted(row["family"] for row in near_best)
            selection_reason = "multiple_adequate_near_tied_nonnested_structures"
        else:
            selected = min(
                near_best,
                key=lambda row: (row["complexity_level"], row["primary_distance_median"]),
            )
            registered_decision = selected["family"]
            selected_families = [selected["family"]]
            selection_reason = "lowest_complexity_near_best_adequate_nested_structure"

    ranking = sorted(
        family_results,
        key=lambda row: (
            not row["eligible"],
            row["primary_distance_median"],
            -row["replication_pattern_rate_mean"],
            row["context_r2_rmse_median"],
            row["complexity_level"],
        ),
    )
    return {
        "contract_version": v4_contract["contract_version"],
        "implementation_prior_version": priors["version"],
        "screen_version": "scale_specific_covariance_v4_screen_1",
        "status": "completed_nested_prior_predictive_structural_sufficiency_screen",
        "draws_per_seed_per_family": draws_per_seed,
        "seeds": seeds,
        "accept_fraction": float(screen["accept_fraction"]),
        "families": family_results,
        "ranking": [row["family"] for row in ranking],
        "eligible_families": sorted(row["family"] for row in eligible),
        "registered_decision": registered_decision,
        "selected_families": selected_families,
        "selection_reason": selection_reason,
        "interpretation_boundary": (
            "Nested prior-predictive structural sufficiency for a covariance architecture. "
            "Not a likelihood, posterior model probability, Bayes factor, causal model selection, "
            "proof that a within-only factor is biological rather than photographic, phylogenetic "
            "inference, adaptation, selection, plasticity, or a unique mechanism."
        ),
        "_draw_rows": draw_rows,
    }


def write_outputs(out_dir: Path, result: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    draw_rows = result.pop("_draw_rows")
    (out_dir / "scale_specific_covariance_v4_result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    if draw_rows:
        fields = sorted({key for row in draw_rows for key in row})
        with (out_dir / "scale_specific_covariance_v4_draws.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(draw_rows)
    print(json.dumps(result, indent=2))


def main() -> int:
    args = parse_args()
    v4_contract = json.loads(args.contract.read_text(encoding="utf-8"))
    priors = json.loads(args.priors.read_text(encoding="utf-8"))
    v3_contract = json.loads(args.v3_contract.read_text(encoding="utf-8"))
    validate_priors(v4_contract, priors)
    targets = v3.load_observed(v3_contract, args.structure, args.incremental)
    context_targets = load_context_targets(args.environment)
    heldout = v3.load_v2_heldout(args.v2_heldout)["full_tradeoff_common_lability"]
    screen = v4_contract["screen_design"]
    draws = args.draws_per_seed or int(screen["draws_per_seed_per_family"])
    seeds = (
        [int(value) for value in args.seeds.split(",") if value.strip()]
        if args.seeds
        else [int(value) for value in screen["seeds"]]
    )
    accept_fraction = args.accept_fraction or float(screen["accept_fraction"])
    if accept_fraction != float(screen["accept_fraction"]):
        raise ValueError("The registered screen does not allow changing accept_fraction")
    if draws <= 0 or not seeds:
        raise ValueError("Invalid screen request")
    result = run_screen(
        v4_contract,
        priors,
        v3_contract,
        targets,
        context_targets,
        heldout,
        draws,
        seeds,
    )
    write_outputs(args.out_dir, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
