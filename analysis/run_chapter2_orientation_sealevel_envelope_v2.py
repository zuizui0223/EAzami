#!/usr/bin/env python3
"""Partial sea-level sensitivity across the bounded orientation chronology envelope.

The refined orientation chronology contains 94 admissible parent-child age pairs,
but the public Spratt-Lisiecki long sea-level stack used here ends at 798 ka.
Therefore this script evaluates only chronology pairs fully covered by that series
and fails closed on any full-envelope trigger claim.

Global sea level is treated as a generic range-reorganization opportunity, not as
a local Ryukyu/Taiwan connectivity reconstruction and not as a selective pressure.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

METRICS = (
    "mean_m",
    "sd_m",
    "range_m",
    "endpoint_abs_change_m",
    "mean_abs_1k_change_m",
    "max_abs_1k_change_m",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--orientation-contract", type=Path, required=True)
    p.add_argument("--noaa", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args()


def enumerate_age_pairs(contract: dict[str, Any]) -> list[tuple[float, float]]:
    """Reproduce the frozen orientation 94-pair chronology grid without climate imports."""
    c = contract["chronology_scenarios"]
    parent = c["parent_node"]
    child = c["child_node"]
    parent_grid = np.linspace(parent["lower_ma"], parent["upper_ma"], 16)
    child_grid = np.linspace(child["lower_ma"], child["upper_ma"], 10)
    pairs: set[tuple[float, float]] = set()
    for old_ma in parent_grid:
        for young_ma in child_grid:
            if old_ma > young_ma and (old_ma - young_ma) >= 0.010:
                pairs.add((round(float(young_ma), 6), round(float(old_ma), 6)))
    central = (round(float(child["central_ma"]), 6), round(float(parent["central_ma"]), 6))
    if central[1] > central[0]:
        pairs.add(central)
    return sorted(pairs, key=lambda x: (x[1] - x[0], x[0], x[1]))


def load_noaa(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line.startswith("age_calkaBP\t"))
    df = pd.read_csv(io.StringIO("\n".join(lines[header_i:])), sep="\t")
    df["age_calkaBP"] = pd.to_numeric(df["age_calkaBP"], errors="coerce")
    df["SeaLev_longPC1"] = pd.to_numeric(df["SeaLev_longPC1"], errors="coerce")
    return (
        df.dropna(subset=["age_calkaBP", "SeaLev_longPC1"])
        .sort_values("age_calkaBP")
        .drop_duplicates("age_calkaBP", keep="first")
        .reset_index(drop=True)
    )


def interp_values(df: pd.DataFrame, ages: np.ndarray) -> np.ndarray:
    return np.interp(
        np.asarray(ages, dtype=float),
        df["age_calkaBP"].to_numpy(float),
        df["SeaLev_longPC1"].to_numpy(float),
    )


def window_metrics(df: pd.DataFrame, young_ka: float, old_ka: float) -> dict[str, float]:
    duration = float(old_ka - young_ka)
    if duration <= 0:
        raise ValueError("non-positive duration")
    n = max(3, int(np.ceil(duration)) + 1)
    ages = young_ka + np.linspace(0.0, duration, n)
    y = interp_values(df, ages)
    diffs = np.diff(y)
    return {
        "mean_m": float(np.mean(y)),
        "sd_m": float(np.std(y, ddof=1)),
        "range_m": float(np.max(y) - np.min(y)),
        "endpoint_abs_change_m": float(abs(y[-1] - y[0])),
        "mean_abs_1k_change_m": float(np.mean(np.abs(diffs))),
        "max_abs_1k_change_m": float(np.max(np.abs(diffs))),
    }


def percentile(null: np.ndarray, value: float) -> float:
    x = np.asarray(null, dtype=float)
    return float((np.sum(x <= value) + 0.5) / (len(x) + 1.0))


def qsummary(values: list[float]) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    return {
        "min": float(np.min(x)),
        "q05": float(np.quantile(x, 0.05)),
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "max": float(np.max(x)),
    }


def matched_windows(df: pd.DataFrame, duration_ka: float) -> dict[str, np.ndarray]:
    min_age = float(df.age_calkaBP.min())
    max_age = float(df.age_calkaBP.max())
    starts = np.arange(np.ceil(min_age), np.floor(max_age - duration_ka) + 1e-9, 1.0)
    if len(starts) < 20:
        raise ValueError(f"too few matched sea-level windows for duration={duration_ka}: {len(starts)}")
    rows = [window_metrics(df, float(s), float(s + duration_ka)) for s in starts]
    return {m: np.asarray([r[m] for r in rows], dtype=float) for m in METRICS}


def main() -> int:
    args = parse_args()
    contract = json.loads(args.orientation_contract.read_text(encoding="utf-8"))
    pairs = enumerate_age_pairs(contract)
    if len(pairs) != 94:
        raise AssertionError(f"expected frozen 94 chronology pairs, got {len(pairs)}")

    sea = load_noaa(args.noaa)
    min_ka = float(sea.age_calkaBP.min())
    max_ka = float(sea.age_calkaBP.max())
    covered = [(young, old) for young, old in pairs if young * 1000.0 >= min_ka and old * 1000.0 <= max_ka]
    uncovered = [(young, old) for young, old in pairs if (young, old) not in covered]

    cache: dict[float, dict[str, np.ndarray]] = {}
    scenario_rows: list[dict[str, Any]] = []
    for young_ma, old_ma in covered:
        young_ka = float(young_ma * 1000.0)
        old_ka = float(old_ma * 1000.0)
        duration = old_ka - young_ka
        key = round(duration, 6)
        if key not in cache:
            cache[key] = matched_windows(sea, duration)
        event = window_metrics(sea, young_ka, old_ka)
        rec: dict[str, Any] = {
            "young_ma": young_ma,
            "old_ma": old_ma,
            "duration_ka": duration,
            **event,
            "n_matched_windows": int(len(cache[key]["mean_m"])),
        }
        for metric in METRICS:
            rec[f"{metric}_percentile"] = percentile(cache[key][metric], event[metric])
        scenario_rows.append(rec)

    metric_summary = {
        metric: qsummary([float(r[f"{metric}_percentile"]) for r in scenario_rows])
        for metric in METRICS
    }
    central = min(
        scenario_rows,
        key=lambda r: abs(float(r["young_ma"]) - 0.74) + abs(float(r["old_ma"]) - 0.79),
    )

    result = {
        "contract_version": "chapter2_orientation_sealevel_envelope_v2",
        "status_date": "2026-09-02",
        "event_id": "ORI_CORE_NIPPONO_STEM",
        "source": {
            "dataset": "Spratt and Lisiecki 2016 global sea-level stack",
            "dataset_doi": "10.25921/rd66-5820",
            "publication_doi": "10.5194/cp-12-1079-2016",
            "series": "SeaLev_longPC1",
            "observed_coverage_ka": [min_ka, max_ka],
        },
        "chronology_coverage": {
            "n_total_pairs": len(pairs),
            "n_fully_covered_pairs": len(covered),
            "coverage_fraction": float(len(covered) / len(pairs)),
            "n_uncovered_pairs": len(uncovered),
            "full_chronology_classification": "not_evaluable_full_chronology_sea_level_coverage_limited",
        },
        "estimand_role": "partial global sea-level range-reorganization sensitivity; not local paleogeographic connectivity and not selection",
        "matched_window_design": {
            "same_duration": True,
            "global_series_only": True,
            "step_ka": 1,
            "percentiles_are_descriptive_not_probabilities": True,
        },
        "metric_percentile_summary_across_covered_chronologies": metric_summary,
        "central_0_79_to_0_74_ma": central,
        "scenario_rows": scenario_rows,
        "decision": "The public sea-level stack does not cover enough of the refined chronology envelope for a full trigger test. Covered chronology rows are a partial sensitivity only, even if individual percentiles appear extreme.",
        "claim_boundary": [
            "Only chronology pairs fully inside the 0-798 ka public series are evaluated.",
            "Coverage-limited sea-level rows cannot stand in for the full 94-pair chronology envelope.",
            "Global sea level is not a local Ryukyu/Taiwan land-bridge or fragmentation reconstruction.",
            "Sea-level variability is a range-reorganization opportunity context, not a selective pressure on capitulum orientation.",
            "One bounded orientation event cannot establish a repeated differentiation trigger."
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "chronology_coverage": result["chronology_coverage"],
        "metric_percentile_summary": metric_summary,
        "central_pair": central,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
