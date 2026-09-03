#!/usr/bin/env python3
"""Test environmental level, change and variability across the bounded orientation branch.

This is a differentiation-time analysis only.  It reuses the frozen chronology and
paleolocation scenario contract but does not use the present-day effect vector,
cosine concordance, or any current environmental association.

For every chronology x paleolocation scenario and PALEO-PGEM variable we measure:
- signed endpoint change (young - old),
- mean environmental level within the branch interval,
- absolute endpoint change,
- temporal SD within the branch interval.

Each metric is compared with same-duration windows stepped every 10 kyr in the same
region.  Percentiles are descriptive matched-window positions, not posterior
probabilities or selection tests.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import run_chapter2_orientation_origin_envelope_v1 as base

VARIABLES = ("BIO1", "BIO4", "BIO12", "BIO15")
REGIONS = ("taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--orientation-contract", type=Path, required=True)
    p.add_argument("--trigger-contract", type=Path, required=True)
    for var in VARIABLES:
        p.add_argument(f"--{var.lower()}", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args()


def percentile(null: np.ndarray, value: float) -> float:
    x = np.asarray(null, dtype=float)
    return float((np.sum(x <= value) + 0.5) / (len(x) + 1.0))


def qs(values: list[float] | np.ndarray) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    return {
        "min": float(np.min(x)),
        "q05": float(np.quantile(x, 0.05)),
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "max": float(np.max(x)),
    }


def window_metrics(series, young_ka: float, old_ka: float) -> dict[str, float]:
    duration = float(old_ka - young_ka)
    if duration <= 0:
        raise ValueError("Non-positive event duration")
    n = max(2, int(math.ceil(duration)) + 1)
    ages = young_ka + np.linspace(0.0, duration, n)
    values = base.interp(series, ages)
    delta = float(values[0] - values[-1])
    return {
        "level_mean": float(np.mean(values)),
        "delta": delta,
        "absolute_delta": abs(delta),
        "temporal_sd": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
    }


def matched_background(series, duration: float) -> dict[str, np.ndarray]:
    min_age = float(series.age_ka.min())
    max_age = float(series.age_ka.max())
    starts = np.arange(min_age, max_age - duration + 1e-9, 10.0)
    if len(starts) < 100:
        raise ValueError(f"Too few matched windows for duration {duration}: {len(starts)}")
    metrics = [window_metrics(series, float(start), float(start + duration)) for start in starts]
    return {k: np.asarray([m[k] for m in metrics], dtype=float) for k in metrics[0]}


def classify_direction(region_summary: dict[str, Any]) -> str:
    if all(region_summary[r]["delta"]["q05"] > 0 for r in REGIONS):
        return "robust_increase"
    if all(region_summary[r]["delta"]["q95"] < 0 for r in REGIONS):
        return "robust_decrease"
    return "direction_unresolved"


def classify_percentile(region_summary: dict[str, Any], metric: str) -> str:
    key = f"{metric}_percentile"
    if all(region_summary[r][key]["q05"] >= 0.95 for r in REGIONS):
        return f"{metric}_consistently_high_vs_matched_windows"
    if all(region_summary[r][key]["q95"] <= 0.05 for r in REGIONS):
        return f"{metric}_consistently_low_vs_matched_windows"
    return f"{metric}_matched_window_position_unresolved"


def main() -> int:
    args = parse_args()
    orientation_contract = json.loads(args.orientation_contract.read_text(encoding="utf-8"))
    trigger_contract = json.loads(args.trigger_contract.read_text(encoding="utf-8"))
    pairs = base.enumerate_age_pairs(orientation_contract)
    if len(pairs) != 94:
        raise AssertionError(f"Expected frozen 94 chronology scenarios, got {len(pairs)}")
    paths = {v: getattr(args, v.lower()) for v in VARIABLES}

    all_rows: list[dict[str, Any]] = []
    summaries: dict[str, Any] = {v: {} for v in VARIABLES}
    background_cache: dict[tuple[str, str, float], dict[str, np.ndarray]] = {}

    for region in REGIONS:
        bounds = orientation_contract["paleolocation_scenarios"][region]
        series_by_var = {v: base.regional_series(paths[v], bounds) for v in VARIABLES}
        for var in VARIABLES:
            series = series_by_var[var]
            region_rows = []
            for young_ma, old_ma in pairs:
                young_ka = float(young_ma * 1000.0)
                old_ka = float(old_ma * 1000.0)
                duration = float(old_ka - young_ka)
                event = window_metrics(series, young_ka, old_ka)
                cache_key = (region, var, round(duration, 6))
                if cache_key not in background_cache:
                    background_cache[cache_key] = matched_background(series, duration)
                bg = background_cache[cache_key]
                rec = {
                    "region": region,
                    "variable": var,
                    "young_ma": young_ma,
                    "old_ma": old_ma,
                    "duration_ka": duration,
                    **event,
                    "level_mean_percentile": percentile(bg["level_mean"], event["level_mean"]),
                    "absolute_delta_percentile": percentile(bg["absolute_delta"], event["absolute_delta"]),
                    "temporal_sd_percentile": percentile(bg["temporal_sd"], event["temporal_sd"]),
                    "n_matched_windows": int(len(bg["level_mean"])),
                }
                region_rows.append(rec)
                all_rows.append(rec)

            summaries[var][region] = {
                "n_chronology_scenarios": len(region_rows),
                "delta": qs([r["delta"] for r in region_rows]),
                "fraction_delta_positive": float(np.mean([r["delta"] > 0 for r in region_rows])),
                "fraction_delta_negative": float(np.mean([r["delta"] < 0 for r in region_rows])),
                "level_mean_percentile": qs([r["level_mean_percentile"] for r in region_rows]),
                "absolute_delta_percentile": qs([r["absolute_delta_percentile"] for r in region_rows]),
                "temporal_sd_percentile": qs([r["temporal_sd_percentile"] for r in region_rows]),
                "central_pair": min(
                    region_rows,
                    key=lambda r: abs(float(r["young_ma"]) - 0.74) + abs(float(r["old_ma"]) - 0.79),
                ),
            }

    variable_results: dict[str, Any] = {}
    for var in VARIABLES:
        per_region = summaries[var]
        variable_results[var] = {
            "per_region": per_region,
            "signed_change_direction": classify_direction(per_region),
            "level_class": classify_percentile(per_region, "level_mean"),
            "absolute_change_class": classify_percentile(per_region, "absolute_delta"),
            "variability_class": classify_percentile(per_region, "temporal_sd"),
        }

    any_robust_direction = [v for v, r in variable_results.items() if r["signed_change_direction"] != "direction_unresolved"]
    any_extreme_change = [v for v, r in variable_results.items() if not r["absolute_change_class"].endswith("unresolved")]
    any_extreme_variability = [v for v, r in variable_results.items() if not r["variability_class"].endswith("unresolved")]
    any_extreme_level = [v for v, r in variable_results.items() if not r["level_class"].endswith("unresolved")]

    result = {
        "contract_version": "chapter2_orientation_differentiation_environment_v2",
        "status_date": trigger_contract["status_date"],
        "analysis_scope": "orientation differentiation branch only; historical level/change/variability against same-duration regional background; no present-day prior",
        "event_id": "ORI_CORE_NIPPONO_STEM",
        "transition": "erect_or_upward -> nodding_or_downward",
        "chronology": {
            "n_valid_age_pairs": 94,
            "n_paleolocation_scenarios": 4,
            "n_region_by_chronology_scenarios": 376,
            "scenario_rows_are_not_posterior_draws": True,
        },
        "matched_window_design": {
            "step_ka": 10,
            "same_duration": True,
            "same_paleolocation_region": True,
            "percentiles_are_descriptive_not_probabilities": True,
        },
        "variables": variable_results,
        "cross_variable_summary": {
            "variables_with_robust_signed_direction": any_robust_direction,
            "variables_with_consistently_extreme_level": any_extreme_level,
            "variables_with_consistently_extreme_absolute_change": any_extreme_change,
            "variables_with_consistently_extreme_variability": any_extreme_variability,
            "repeated_trigger_status": "not_evaluable_single_dated_transition_event",
        },
        "scenario_rows": all_rows,
        "claim_boundary": [
            "No current or Chapter-1 environmental coefficient is used in this analysis.",
            "The chronology grid and paleolocation boxes are scenario envelopes, not posterior probabilities.",
            "The trait transition instant can lie anywhere on the bounded branch; branch-window climate does not identify its exact exposure.",
            "Matched-window extremeness is historical alignment, not evidence of natural selection.",
            "A single dated transition envelope cannot establish a repeated environmental trigger."
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "variables_with_robust_signed_direction": any_robust_direction,
        "variables_with_consistently_extreme_level": any_extreme_level,
        "variables_with_consistently_extreme_absolute_change": any_extreme_change,
        "variables_with_consistently_extreme_variability": any_extreme_variability,
        "repeated_trigger_status": result["cross_variable_summary"]["repeated_trigger_status"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
