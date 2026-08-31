#!/usr/bin/env python3
"""Compare Azami environmental state-space with EAzami historical trajectories.

Primary shared dimensions are BIO1/BIO4/BIO12/BIO15 because they are present in
both the frozen Azami atlas and PALEO-PGEM. BIO13/BIO16 are predeclared wet-side
mechanism refinements, with BIO14/BIO17 as dry-side controls. This is a local
0.79-0.47 Ma Taiwan sensitivity and not a full Japan38 dated-history analysis.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from run_chapter2_taiwan_orientation_paleohydric_window_v1 import (
    EVENT_OLD_KA,
    EVENT_YOUNG_KA,
    TAIWAN,
    WINDOW_KA,
    _coord_name,
    _data_var,
    _time_ka,
    matched_distribution,
    regional_series,
    window_stats,
)

SHARED = ("BIO1", "BIO4", "BIO12", "BIO15")
WET = ("BIO13", "BIO16")
DRY = ("BIO14", "BIO17")
ALL = SHARED + WET + DRY
AZAMI_PREDICTOR = {
    "BIO1": "chelsa_bio01",
    "BIO4": "chelsa_bio04",
    "BIO12": "chelsa_bio12",
    "BIO15": "chelsa_bio15",
}


def signed_delta(df: pd.DataFrame, young: float, old: float) -> float:
    w = df[(df.age_ka >= young) & (df.age_ka <= old)].sort_values("age_ka")
    if len(w) < 50:
        raise ValueError(f"insufficient points in {young}-{old} ka window")
    return float(w.iloc[0]["median"] - w.iloc[-1]["median"])


def signed_null(df: pd.DataFrame, width: float, step: float = 10.0) -> tuple[np.ndarray, np.ndarray]:
    max_age = min(5000.0, float(df.age_ka.max()))
    starts = np.arange(0.0, max_age - width + 1e-9, step)
    vals = np.asarray([signed_delta(df, float(s), float(s + width)) for s in starts], dtype=float)
    return starts, vals


def empirical_percentile(vals: np.ndarray, observed: float) -> float:
    return float((np.sum(vals <= observed) + 0.5) / (len(vals) + 1.0))


def cellwise_endpoint_delta(path: Path) -> dict:
    ds = xr.open_dataset(path, decode_times=False)
    var = _data_var(ds)
    da = ds[var]
    lat = _coord_name(ds, ("lat", "latitude", "y"))
    lon = _coord_name(ds, ("lon", "longitude", "x"))
    time = _coord_name(ds, ("time", "times", "t", "age", "ka"))
    lonvals = np.asarray(da[lon].values, dtype=float)
    if np.nanmax(lonvals) > 180:
        lon_min, lon_max = TAIWAN["lon_min"] % 360, TAIWAN["lon_max"] % 360
    else:
        lon_min, lon_max = TAIWAN["lon_min"], TAIWAN["lon_max"]
    sub = da.where(
        (da[lat] >= TAIWAN["lat_min"]) & (da[lat] <= TAIWAN["lat_max"]) &
        (da[lon] >= lon_min) & (da[lon] <= lon_max),
        drop=True,
    )
    ages = _time_ka(sub, time)
    iy = int(np.nanargmin(np.abs(ages - EVENT_YOUNG_KA)))
    io = int(np.nanargmin(np.abs(ages - EVENT_OLD_KA)))
    delta = (sub.isel({time: iy}) - sub.isel({time: io})).values.astype(float).ravel()
    delta = delta[np.isfinite(delta)]
    if delta.size == 0:
        raise ValueError("no finite Taiwan cellwise endpoint deltas")
    return {
        "n_cells": int(delta.size),
        "median": float(np.median(delta)),
        "q05": float(np.quantile(delta, 0.05)),
        "q95": float(np.quantile(delta, 0.95)),
        "fraction_positive": float(np.mean(delta > 0)),
        "fraction_negative": float(np.mean(delta < 0)),
        "fraction_zero": float(np.mean(delta == 0)),
        "young_age_ka_nearest": float(ages[iy]),
        "old_age_ka_nearest": float(ages[io]),
    }


def analyze_variable(path: Path) -> dict:
    df = regional_series(path)
    event = window_stats(df, EVENT_YOUNG_KA, EVENT_OLD_KA)
    null_windows = matched_distribution(df, WINDOW_KA)
    starts, delta_null = signed_null(df, WINDOW_KA)
    delta_obs = signed_delta(df, EVENT_YOUNG_KA, EVENT_OLD_KA)
    mu = float(np.mean(delta_null))
    sd = float(np.std(delta_null, ddof=1))
    delta_z = float((delta_obs - mu) / sd) if sd > 0 else float("nan")
    metrics = ("sd_time", "range_time", "net_change_abs", "mean_abs_1k_change", "max_abs_1k_change")
    pct = {
        m: float((np.sum(null_windows[m].to_numpy(float) <= event[m]) + 0.5) / (len(null_windows) + 1.0))
        for m in metrics
    }
    spatial_temporal_ratio = (
        float(event["median_spatial_iqr"] / event["sd_time"])
        if event["sd_time"] > 0 else float("inf")
    )
    return {
        "event_window": event,
        "directional_change_young_minus_old": delta_obs,
        "directional_background": {
            "mean": mu,
            "sd": sd,
            "z": delta_z,
            "signed_percentile": empirical_percentile(delta_null, delta_obs),
            "n_windows": int(len(delta_null)),
            "step_ka": 10.0,
        },
        "duration_matched_percentiles": pct,
        "paleolocation_resolution": {
            "regional_spatial_iqr_over_temporal_sd": spatial_temporal_ratio,
            "cellwise_endpoint_delta": cellwise_endpoint_delta(path),
        },
        "background_starts_ka": starts.tolist(),
        "background_signed_deltas": delta_null.tolist(),
    }


def azami_orientation_vector(path: Path) -> dict:
    rows = pd.read_csv(path)
    rows = rows[
        (rows["scope"] == "among_taxon_min5") &
        (rows["unit_id"] == "orientation_image_vertical_angle") &
        (rows["status"] == "ok")
    ]
    out = {}
    for key, pred in AZAMI_PREDICTOR.items():
        r = rows[rows["predictor"] == pred]
        if len(r) != 1:
            raise ValueError(f"expected one Azami orientation row for {pred}; got {len(r)}")
        rr = r.iloc[0]
        out[key] = {
            "beta_std": float(rr["beta_std"]),
            "p_value": float(rr["p_value"]),
            "q_fdr_bh_global_family": float(rr["q_fdr_bh_global_family"]),
            "fdr_significant_0_05": bool(rr["fdr_significant_0_05"]),
        }
    return out


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / den) if den > 0 else float("nan")


def shared_vector_test(results: dict, azami: dict) -> dict:
    beta = np.asarray([azami[v]["beta_std"] for v in SHARED], dtype=float)
    event_z = np.asarray([results[v]["directional_background"]["z"] for v in SHARED], dtype=float)
    observed = cosine(beta, event_z)
    starts = np.asarray(results[SHARED[0]]["background_starts_ka"], dtype=float)
    null_z = []
    for v in SHARED:
        vals = np.asarray(results[v]["background_signed_deltas"], dtype=float)
        mu = float(np.mean(vals)); sd = float(np.std(vals, ddof=1))
        null_z.append((vals - mu) / sd)
    zmat = np.column_stack(null_z)
    null_cos = np.asarray([cosine(beta, row) for row in zmat], dtype=float)
    finite = np.isfinite(null_cos)
    null_cos = null_cos[finite]
    return {
        "variables": list(SHARED),
        "azami_beta_std_vector": beta.tolist(),
        "event_background_standardized_change_vector": event_z.tolist(),
        "cosine_similarity": observed,
        "null_percentile": empirical_percentile(null_cos, observed),
        "two_sided_extremeness": float(2 * min(empirical_percentile(null_cos, observed), 1 - empirical_percentile(null_cos, observed))),
        "n_duration_matched_windows": int(len(null_cos)),
        "interpretation": "positive cosine means historical environmental movement during the U-to-D branch points in the same multivariate direction as present Azami orientation sorting; negative cosine means directional discordance",
    }


def wet_dry_test(results: dict) -> dict:
    wet_z = np.asarray([results[v]["directional_background"]["z"] for v in WET], dtype=float)
    dry_z = np.asarray([results[v]["directional_background"]["z"] for v in DRY], dtype=float)
    observed_signed = float(np.mean(wet_z) - np.mean(dry_z))
    observed_abs = float(np.mean(np.abs(wet_z)) - np.mean(np.abs(dry_z)))
    all_vars = WET + DRY
    null_z = {}
    for v in all_vars:
        vals = np.asarray(results[v]["background_signed_deltas"], dtype=float)
        null_z[v] = (vals - np.mean(vals)) / np.std(vals, ddof=1)
    n = len(null_z[all_vars[0]])
    signed_null = np.asarray([
        np.mean([null_z[v][i] for v in WET]) - np.mean([null_z[v][i] for v in DRY])
        for i in range(n)
    ])
    abs_null = np.asarray([
        np.mean([abs(null_z[v][i]) for v in WET]) - np.mean([abs(null_z[v][i]) for v in DRY])
        for i in range(n)
    ])
    return {
        "wet_variables": list(WET),
        "dry_control_variables": list(DRY),
        "event_wet_mean_z_minus_dry_mean_z": observed_signed,
        "event_wet_mean_abs_z_minus_dry_mean_abs_z": observed_abs,
        "signed_contrast_percentile": empirical_percentile(signed_null, observed_signed),
        "absolute_contrast_percentile": empirical_percentile(abs_null, observed_abs),
        "n_duration_matched_windows": int(n),
        "interpretation": "a high wet-minus-dry contrast would be more specific to episodic wet exposure than a generic change in all precipitation dimensions"
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--azami-table", type=Path, required=True)
    for v in ALL:
        ap.add_argument(f"--{v.lower()}", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    paths = {v: getattr(args, v.lower()) for v in ALL}
    results = {v: analyze_variable(paths[v]) for v in ALL}
    azami = azami_orientation_vector(args.azami_table)
    out = {
        "contract_version": "chapter2_taiwan_orientation_environment_state_trajectory_v1",
        "scope": "public-data local state-versus-trajectory sensitivity; not full Japan38 T3",
        "event_window_ma": [0.47, 0.79],
        "paleolocation": TAIWAN,
        "azami_orientation_shared_space_vector": azami,
        "variables": {
            v: {k: val for k, val in results[v].items() if not k.startswith("background_")}
            for v in ALL
        },
        "shared_state_trajectory_vector_test": shared_vector_test(results, azami),
        "wetting_specificity_test": wet_dry_test(results),
        "decision_rules": {
            "trajectory_vector": "report the preregistered cosine and its duration-matched percentile; do not select dimensions after observing the event",
            "wetting_specificity": "wet-side BIO13/BIO16 must outperform dry-side BIO14/BIO17 controls to support a wet-exposure-specific historical interpretation",
            "resolution": "cellwise sign disagreement or regional spatial IQR much larger than temporal SD limits historical-environment resolution"
        },
        "claim_boundary": "Local observational public-data sensitivity only; neither vector concordance nor wet-side specificity establishes selection, adaptation, convergence, or all-Japan event correspondence."
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
