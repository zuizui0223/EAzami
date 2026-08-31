#!/usr/bin/env python3
"""Descendant-clade anthesis-window palaeoprecipitation sensitivity.

Public phenology supports Aug-Nov flowering for C. pengii, Sep-Oct for
C. kawakamii, and Aug-Oct for C. tatakaense. We therefore predeclare:
  * Sep-Oct = shared intersection among all three descendant D taxa;
  * Aug-Nov = union/envelope across the three taxa.

These present-day descendant phenologies are used only as a mechanism-oriented
sensitivity. They are not reconstructed ancestral phenology.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

from run_chapter2_taiwan_orientation_paleohydric_window_v1 import (
    EVENT_OLD_KA, EVENT_YOUNG_KA, WINDOW_KA, TAIWAN,
    _coord_name, _data_var, _time_ka, window_stats, matched_distribution, percentile,
)


def regional_sum_series(paths: list[Path]) -> pd.DataFrame:
    arrays = []
    meta = None
    for path in paths:
        ds = xr.open_dataset(path, decode_times=False)
        var = _data_var(ds)
        da = ds[var]
        lat = _coord_name(ds, ("lat", "latitude", "y"))
        lon = _coord_name(ds, ("lon", "longitude", "x"))
        time = _coord_name(ds, ("time", "times", "t", "age", "ka"))
        lonvals = np.asarray(da[lon].values, dtype=float)
        lon_min, lon_max = ((TAIWAN["lon_min"] % 360, TAIWAN["lon_max"] % 360)
                            if np.nanmax(lonvals) > 180 else (TAIWAN["lon_min"], TAIWAN["lon_max"]))
        sub = da.where(
            (da[lat] >= TAIWAN["lat_min"]) & (da[lat] <= TAIWAN["lat_max"]) &
            (da[lon] >= lon_min) & (da[lon] <= lon_max), drop=True)
        if meta is None:
            meta = (lat, lon, time, _time_ka(sub, time))
        arrays.append(sub)
    total = arrays[0]
    for x in arrays[1:]:
        total = total + x
    lat, lon, time, age = meta
    spatial_dims = [d for d in total.dims if d != time]
    med = total.median(dim=spatial_dims, skipna=True).values.astype(float)
    q25 = total.quantile(0.25, dim=spatial_dims, skipna=True).values.astype(float)
    q75 = total.quantile(0.75, dim=spatial_dims, skipna=True).values.astype(float)
    out = pd.DataFrame({"age_ka": age, "median": med, "q25": q25, "q75": q75})
    return out.replace([np.inf, -np.inf], np.nan).dropna().sort_values("age_ka").reset_index(drop=True)


def cellwise_endpoint_delta(paths: list[Path]) -> dict:
    young_total = None
    old_total = None
    for path in paths:
        ds = xr.open_dataset(path, decode_times=False)
        var = _data_var(ds)
        da = ds[var]
        lat = _coord_name(ds, ("lat", "latitude", "y"))
        lon = _coord_name(ds, ("lon", "longitude", "x"))
        time = _coord_name(ds, ("time", "times", "t", "age", "ka"))
        lonvals = np.asarray(da[lon].values, dtype=float)
        lon_min, lon_max = ((TAIWAN["lon_min"] % 360, TAIWAN["lon_max"] % 360)
                            if np.nanmax(lonvals) > 180 else (TAIWAN["lon_min"], TAIWAN["lon_max"]))
        sub = da.where(
            (da[lat] >= TAIWAN["lat_min"]) & (da[lat] <= TAIWAN["lat_max"]) &
            (da[lon] >= lon_min) & (da[lon] <= lon_max), drop=True)
        ages = _time_ka(sub, time)
        yi = int(np.nanargmin(np.abs(ages - EVENT_YOUNG_KA)))
        oi = int(np.nanargmin(np.abs(ages - EVENT_OLD_KA)))
        y = np.asarray(sub.isel({time: yi}).values, dtype=float)
        o = np.asarray(sub.isel({time: oi}).values, dtype=float)
        young_total = y if young_total is None else young_total + y
        old_total = o if old_total is None else old_total + o
    d = (young_total - old_total).ravel()
    d = d[np.isfinite(d)]
    return {
        "n_cells": int(d.size),
        "median": float(np.median(d)),
        "q05": float(np.quantile(d, 0.05)),
        "q95": float(np.quantile(d, 0.95)),
        "fraction_positive": float(np.mean(d > 0)),
        "fraction_negative": float(np.mean(d < 0)),
        "fraction_zero": float(np.mean(d == 0)),
    }


def analyze(paths: list[Path], label: str, months: list[int]) -> dict:
    df = regional_sum_series(paths)
    obs = window_stats(df, EVENT_YOUNG_KA, EVENT_OLD_KA)
    null = matched_distribution(df, WINDOW_KA)
    metrics = ["sd_time", "range_time", "net_change_abs", "mean_abs_1k_change", "max_abs_1k_change"]
    pct = {m: percentile(null, obs[m], m) for m in metrics}
    starts = null["young_ka"].to_numpy(float)
    signed = []
    for s in starts:
        w = df[(df.age_ka >= s) & (df.age_ka <= s + WINDOW_KA)].sort_values("age_ka")
        signed.append(float(w.iloc[0]["median"] - w.iloc[-1]["median"]))
    signed = np.asarray(signed)
    event_delta = float(df.iloc[(df.age_ka - EVENT_YOUNG_KA).abs().argmin()]["median"] -
                        df.iloc[(df.age_ka - EVENT_OLD_KA).abs().argmin()]["median"])
    bg_mean = float(np.mean(signed)); bg_sd = float(np.std(signed, ddof=1))
    return {
        "label": label,
        "months": months,
        "event_window": obs,
        "directional_change_young_minus_old": event_delta,
        "directional_background": {
            "mean": bg_mean,
            "sd": bg_sd,
            "z": float((event_delta - bg_mean) / bg_sd) if bg_sd > 0 else None,
            "signed_percentile": float((np.sum(signed <= event_delta) + 0.5) / (len(signed) + 1.0)),
            "n_windows": int(len(signed)),
        },
        "duration_matched_percentiles": pct,
        "cellwise_endpoint_delta": cellwise_endpoint_delta(paths),
        "regional_spatial_iqr_over_temporal_sd": float(obs["median_spatial_iqr"] / obs["sd_time"]) if obs["sd_time"] else None,
    }


def main():
    ap = argparse.ArgumentParser()
    for m in (8,9,10,11):
        ap.add_argument(f"--m{m}", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    paths = {m: getattr(a, f"m{m}") for m in (8,9,10,11)}
    result = {
        "contract_version": "chapter2_taiwan_orientation_anthesis_precipitation_v1",
        "scope": "public descendant-clade phenology sensitivity for the 0.79-0.47 Ma U->D branch",
        "phenology_basis": {
            "Cirsium pengii": "Aug-Nov",
            "Cirsium kawakamii": "Sep-Oct",
            "Cirsium tatakaense": "Aug-Oct",
            "shared_intersection": "Sep-Oct",
            "union_envelope": "Aug-Nov",
            "ancestral_phenology_status": "not reconstructed",
        },
        "expected_if_rain_exposure_concordant": "positive young-minus-old precipitation is directionally compatible with the present Azami higher-BIO12 -> downward orientation association; extremeness and paleolocation robustness are evaluated separately",
        "shared_sep_oct": analyze([paths[9], paths[10]], "shared descendant D-clade Sep-Oct precipitation", [9,10]),
        "envelope_aug_nov": analyze([paths[8], paths[9], paths[10], paths[11]], "descendant D-clade Aug-Nov phenology envelope precipitation", [8,9,10,11]),
        "claim_boundary": [
            "current descendant phenology is not ancestral phenology",
            "monthly palaeoprecipitation is a climatic exposure proxy, not measured rain-on-capitula",
            "one local event cannot establish historical rain selection or adaptation",
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
