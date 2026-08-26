#!/usr/bin/env python3
"""Exact-permutation public WorldClim mechanism screen for global L* proxies."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

LIGHTNESS = "corolla_lab_lightness_median_species_median"
AXES = {
    "solar_radiation": "worldclim_srad_annual_mean_kj_m2_day_species_median",
    "wind_speed": "worldclim_wind_annual_mean_m_s_species_median",
    "vpd_tavg_proxy": "worldclim_vpd_tavg_proxy_annual_mean_kpa_species_median",
}


def pairwise_abs(values: np.ndarray) -> np.ndarray:
    return np.asarray([abs(values[i] - values[j]) for i in range(len(values)) for j in range(i + 1, len(values))], dtype=float)


def standardized_exposure_distance(frame: pd.DataFrame) -> np.ndarray:
    x = frame[list(AXES.values())].to_numpy(dtype=float)
    sd = x.std(axis=0, ddof=1)
    if np.any(sd <= 0) or not np.isfinite(sd).all():
        raise ValueError("non-positive or invalid exposure-axis SD")
    z = (x - x.mean(axis=0)) / sd
    return np.asarray([np.linalg.norm(z[i] - z[j]) for i in range(len(z)) for j in range(i + 1, len(z))], dtype=float)


def rho(x: np.ndarray, y: np.ndarray) -> float:
    value = float(spearmanr(x, y).statistic)
    if not np.isfinite(value):
        raise ValueError("undefined Spearman rho")
    return value


def exact_permutation(lightness: np.ndarray, predictor_distance: np.ndarray) -> dict:
    observed = rho(pairwise_abs(lightness), predictor_distance)
    permuted = []
    for perm in itertools.permutations(lightness.tolist()):
        permuted.append(rho(pairwise_abs(np.asarray(perm, dtype=float)), predictor_distance))
    arr = np.asarray(permuted, dtype=float)
    return {
        "rho": observed,
        "n_permutations": int(len(arr)),
        "p_positive_exact": float(np.mean(arr >= observed - 1e-12)),
        "p_negative_exact": float(np.mean(arr <= observed + 1e-12)),
        "p_two_sided_exact": float(np.mean(np.abs(arr) >= abs(observed) - 1e-12)),
    }


def loo_rhos(frame: pd.DataFrame, predictor_name: str) -> dict[str, float]:
    result = {}
    for omit in frame["paper_japan_member_id"]:
        sub = frame[frame["paper_japan_member_id"] != omit].reset_index(drop=True)
        light = sub[LIGHTNESS].to_numpy(dtype=float)
        if predictor_name == "exposure_3d":
            pred = standardized_exposure_distance(sub)
        else:
            pred = pairwise_abs(sub[AXES[predictor_name]].to_numpy(dtype=float))
        result[str(omit)] = rho(pairwise_abs(light), pred)
    return result


def holm_adjust(pvalues: dict[str, float]) -> dict[str, float]:
    ordered = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(ordered)
    adjusted = {}
    running = 0.0
    for rank, (name, p) in enumerate(ordered):
        value = min(1.0, (m - rank) * p)
        running = max(running, value)
        adjusted[name] = running
    return adjusted


def analyze_subset(frame: pd.DataFrame) -> dict:
    frame = frame.sort_values("paper_japan_member_id").reset_index(drop=True)
    light = frame[LIGHTNESS].to_numpy(dtype=float)
    results = {}
    for name, column in AXES.items():
        pred = pairwise_abs(frame[column].to_numpy(dtype=float))
        stats = exact_permutation(light, pred)
        stats["leave_one_out_rho"] = loo_rhos(frame, name)
        stats["leave_one_out_all_positive"] = all(v > 0 for v in stats["leave_one_out_rho"].values())
        results[name] = stats

    pred = standardized_exposure_distance(frame)
    stats = exact_permutation(light, pred)
    stats["leave_one_out_rho"] = loo_rhos(frame, "exposure_3d")
    stats["leave_one_out_all_positive"] = all(v > 0 for v in stats["leave_one_out_rho"].values())
    results["exposure_3d"] = stats

    adjusted = holm_adjust({name: results[name]["p_positive_exact"] for name in AXES})
    for name, p_adj in adjusted.items():
        results[name]["p_positive_holm_three_axes"] = p_adj

    return {
        "n_taxa": int(len(frame)),
        "taxa": frame["paper_japan_member_id"].tolist(),
        "results": results,
    }


def run(summary_csv: Path) -> dict:
    df = pd.read_csv(summary_csv)
    required = ["paper_japan_member_id", "taxon_name", "n_colour_observations", LIGHTNESS, *AXES.values()]
    missing = [c for c in required if c not in df]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if df[required].isna().any().any():
        raise ValueError("missing values in required WorldClim mechanism columns")

    subsets = {
        "n_ge_5": analyze_subset(df[df["n_colour_observations"] >= 5].copy()),
        "n_ge_10": analyze_subset(df[df["n_colour_observations"] >= 10].copy()),
    }
    if subsets["n_ge_5"]["n_taxa"] != 6 or subsets["n_ge_10"]["n_taxa"] != 5:
        raise AssertionError("unexpected high-evidence taxon counts")

    r6 = subsets["n_ge_5"]["results"]
    r5 = subsets["n_ge_10"]["results"]
    primary = (
        r6["exposure_3d"]["rho"] > 0
        and r6["exposure_3d"]["p_positive_exact"] <= 0.05
        and r5["exposure_3d"]["rho"] > 0
        and r6["exposure_3d"]["leave_one_out_all_positive"]
    )
    secondary = {}
    for name in AXES:
        secondary[name] = bool(
            r6[name]["rho"] > 0
            and r6[name]["p_positive_holm_three_axes"] <= 0.05
            and r5[name]["rho"] > 0
            and r6[name]["leave_one_out_all_positive"]
        )

    return {
        "contract_version": "japan38_global_lightness_worldclim_mechanism_gate_v1",
        "analysis_scope": "global exact-concept species-proxy exploratory sensitivity",
        "baseline": "WorldClim 2.1 1970-2000, 10 arc-minutes",
        "primary_predictor": "standardized 3-D distance across annual-mean solar radiation, wind speed, and mean-temperature VPD proxy",
        "primary_support_rule": "n>=5 rho>0; exact positive-tail p<=0.05; n>=10 rho>0; every n>=5 leave-one-taxon-out rho>0",
        "secondary_axis_rule": "same direction/LOO rule, with Holm correction across the three axis-specific n>=5 positive-tail tests",
        "subsets": subsets,
        "primary_gate_pass": bool(primary),
        "secondary_axis_robust_leads": secondary,
        "claim_boundary": "A pass would identify an exploratory public-data mechanism lead, not prove selection or causation. A fail means these WorldClim exposure axes do not explain the global species-proxy L* pattern under the frozen gate. This analysis is not Japan-local colour history.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
