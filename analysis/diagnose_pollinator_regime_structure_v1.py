#!/usr/bin/env python3
"""Diagnose the remaining C. purpuratum pollinator-regime residual in pattern reduction v2.

The four frozen head-probing slopes admit exact least-squares solutions in log space for
four nested parameterizations. A deterministic random search is retained only as a
convergence/sanity check. Raw residual distance is used as a structural diagnostic, not as
model selection: the four-parameter structure is saturated for four observations.

This is not a fit of the full capitulum model and not posterior inference.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path

TARGET_IDS = [
    "CIR_DISPLAY_PROBE_97HD",
    "CIR_DISPLAY_PROBE_97LD",
    "CIR_DISPLAY_PROBE_98HD",
    "CIR_DISPLAY_PROBE_98LD",
]
MODES = [
    "COMMON_MEAN_COMMON_RATIO",
    "YEAR_MEAN_COMMON_RATIO",
    "COMMON_MEAN_YEAR_RATIO",
    "YEAR_MEAN_YEAR_RATIO",
]
PARAMETER_COUNTS = {
    "COMMON_MEAN_COMMON_RATIO": 2,
    "YEAR_MEAN_COMMON_RATIO": 3,
    "COMMON_MEAN_YEAR_RATIO": 3,
    "YEAR_MEAN_YEAR_RATIO": 4,
}
MEAN_BOUNDS = (0.05, 0.30)
RATIO_BOUNDS = (1.0, 5.0)
SCORE_SCALE = 0.35


def load_slopes(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = {row["target_id"]: row for row in csv.DictReader(handle)}
    return [float(rows[target_id]["estimate"]) for target_id in TARGET_IDS]


def score(pred, obs):
    return sum(
        ((math.log(max(p, 1e-12)) - math.log(o)) / SCORE_SCALE) ** 2
        for p, o in zip(pred, obs)
    )


def _inside(value, bounds):
    return bounds[0] <= value <= bounds[1]


def exact_fit(mode, obs):
    """Return the exact log-space least-squares optimum for one nested structure."""
    y97h, y97l, y98h, y98l = map(math.log, obs)
    m97 = (y97h + y97l) / 2.0
    m98 = (y98h + y98l) / 2.0
    d97 = y97l - y97h
    d98 = y98l - y98h
    common_m = (m97 + m98) / 2.0
    common_d = (d97 + d98) / 2.0

    if mode == "COMMON_MEAN_COMMON_RATIO":
        pars = {"mean": math.exp(common_m), "density_ratio": math.exp(common_d)}
        pred = [
            math.exp(common_m - common_d / 2.0),
            math.exp(common_m + common_d / 2.0),
            math.exp(common_m - common_d / 2.0),
            math.exp(common_m + common_d / 2.0),
        ]
    elif mode == "YEAR_MEAN_COMMON_RATIO":
        pars = {
            "mean_1997": math.exp(m97),
            "mean_1998": math.exp(m98),
            "density_ratio": math.exp(common_d),
        }
        pred = [
            math.exp(m97 - common_d / 2.0),
            math.exp(m97 + common_d / 2.0),
            math.exp(m98 - common_d / 2.0),
            math.exp(m98 + common_d / 2.0),
        ]
    elif mode == "COMMON_MEAN_YEAR_RATIO":
        pars = {
            "mean": math.exp(common_m),
            "density_ratio_1997": math.exp(d97),
            "density_ratio_1998": math.exp(d98),
        }
        pred = [
            math.exp(common_m - d97 / 2.0),
            math.exp(common_m + d97 / 2.0),
            math.exp(common_m - d98 / 2.0),
            math.exp(common_m + d98 / 2.0),
        ]
    elif mode == "YEAR_MEAN_YEAR_RATIO":
        pars = {
            "mean_1997": math.exp(m97),
            "mean_1998": math.exp(m98),
            "density_ratio_1997": math.exp(d97),
            "density_ratio_1998": math.exp(d98),
        }
        pred = list(obs)
    else:
        raise ValueError(mode)

    means = [value for key, value in pars.items() if key.startswith("mean")]
    ratios = [value for key, value in pars.items() if key.startswith("density_ratio")]
    bounds_ok = all(_inside(value, MEAN_BOUNDS) for value in means) and all(
        _inside(value, RATIO_BOUNDS) for value in ratios
    )
    return pred, pars, score(pred, obs), bounds_ok


def draw_log(rng, lo, hi):
    return math.exp(rng.uniform(math.log(lo), math.log(hi)))


def random_prediction(mode, rng):
    if mode == "COMMON_MEAN_COMMON_RATIO":
        g = draw_log(rng, *MEAN_BOUNDS)
        r = draw_log(rng, *RATIO_BOUNDS)
        return [g / math.sqrt(r), g * math.sqrt(r), g / math.sqrt(r), g * math.sqrt(r)]
    if mode == "YEAR_MEAN_COMMON_RATIO":
        g97 = draw_log(rng, *MEAN_BOUNDS)
        g98 = draw_log(rng, *MEAN_BOUNDS)
        r = draw_log(rng, *RATIO_BOUNDS)
        return [g97 / math.sqrt(r), g97 * math.sqrt(r), g98 / math.sqrt(r), g98 * math.sqrt(r)]
    if mode == "COMMON_MEAN_YEAR_RATIO":
        g = draw_log(rng, *MEAN_BOUNDS)
        r97 = draw_log(rng, *RATIO_BOUNDS)
        r98 = draw_log(rng, *RATIO_BOUNDS)
        return [g / math.sqrt(r97), g * math.sqrt(r97), g / math.sqrt(r98), g * math.sqrt(r98)]
    g97 = draw_log(rng, *MEAN_BOUNDS)
    g98 = draw_log(rng, *MEAN_BOUNDS)
    r97 = draw_log(rng, *RATIO_BOUNDS)
    r98 = draw_log(rng, *RATIO_BOUNDS)
    return [g97 / math.sqrt(r97), g97 * math.sqrt(r97), g98 / math.sqrt(r98), g98 * math.sqrt(r98)]


def random_search_best(mode, obs, draws):
    rng = random.Random(20260820 + sum(map(ord, mode)))
    best = float("inf")
    for _ in range(draws):
        best = min(best, score(random_prediction(mode, rng), obs))
    return best


def run(targets: Path, draws=100000):
    obs = load_slopes(targets)
    results = {}
    for mode in MODES:
        pred, pars, exact_distance, bounds_ok = exact_fit(mode, obs)
        random_distance = random_search_best(mode, obs, draws)
        k = PARAMETER_COUNTS[mode]
        results[mode] = {
            "parameter_count": k,
            "residual_df": len(obs) - k,
            "exact_min_distance": exact_distance,
            "exact_predicted_slopes": pred,
            "exact_parameters": pars,
            "parameter_bounds_ok": bounds_ok,
            "random_search_best_distance": random_distance,
            "random_search_gap": random_distance - exact_distance,
        }

    shared_distance = results["COMMON_MEAN_COMMON_RATIO"]["exact_min_distance"]
    for mode in MODES:
        results[mode]["raw_distance_reduction_vs_shared"] = (
            (shared_distance - results[mode]["exact_min_distance"]) / shared_distance
            if shared_distance > 0
            else 0.0
        )

    raw_distance_ranking = sorted(MODES, key=lambda mode: results[mode]["exact_min_distance"])
    nonsaturated = [mode for mode in MODES if results[mode]["residual_df"] > 0]
    nonsaturated_raw_ranking = sorted(nonsaturated, key=lambda mode: results[mode]["exact_min_distance"])

    return {
        "contract_version": "pollinator_regime_structure_v1_exact_df_audit",
        "status_date": "2026-08-20",
        "observed_slopes": dict(zip(TARGET_IDS, obs)),
        "observation_count": len(obs),
        "random_draws_per_structure": draws,
        "score_scale_log": SCORE_SCALE,
        "mean_bounds": list(MEAN_BOUNDS),
        "density_ratio_bounds": list(RATIO_BOUNDS),
        "results": results,
        "raw_distance_ranking": raw_distance_ranking,
        "nonsaturated_raw_ranking": nonsaturated_raw_ranking,
        "headline": (
            "Both one-axis context extensions reduce the shared pollinator residual. The fully "
            "context-specific four-parameter structure interpolates all four slopes exactly, but it is "
            "saturated (residual df = 0) and therefore cannot be preferred from raw fit alone."
        ),
        "interpretation": (
            "The v2 pollinator-regime residual is genuinely associated with forcing shared response "
            "structure across 1997 and 1998: year-specific mean response reduces raw distance by about "
            "62%, and year-specific density ratio by about 38%. The next full-model upgrade should "
            "represent context heterogeneity with shrinkage or replicated-data validation rather than "
            "adding an unconstrained parameter for every observed context."
        ),
        "claim_boundary": (
            "This diagnostic uses four published slopes from one C. purpuratum study system. The "
            "four-parameter exact fit is algebraically expected for four observations and is not model-"
            "selection evidence. The operational 0.35 score scale is not a validated sampling-error SE, "
            "so AIC/posterior-style inference is not claimed."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=100000)
    args = parser.parse_args()
    output = run(args.targets, args.draws)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
