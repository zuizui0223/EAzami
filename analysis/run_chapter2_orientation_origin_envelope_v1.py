#!/usr/bin/env python3
"""Cross-study chronology × paleolocation envelope for the origin of nodding orientation.

This public-data sensitivity does not treat marginal node-age intervals from
separate studies as a joint posterior.  It enumerates a deterministic age grid,
retains topologically admissible parent > child pairs, evaluates several
predeclared regional paleolocation scenarios, and asks whether branch-endpoint
PALEO-PGEM trajectories align with the frozen Azami present-space orientation
vector more strongly than same-duration background climate windows.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr


VARIABLES = ("BIO1", "BIO4", "BIO12", "BIO15")


def _coord_name(ds: xr.Dataset, candidates: tuple[str, ...]) -> str:
    low = {k.lower(): k for k in list(ds.coords) + list(ds.dims)}
    for candidate in candidates:
        if candidate.lower() in low:
            return low[candidate.lower()]
    raise KeyError(f"coordinate not found among coords={list(ds.coords)} dims={list(ds.dims)}")


def _data_var(ds: xr.Dataset) -> str:
    vars_ = list(ds.data_vars)
    if not vars_:
        raise ValueError("NetCDF contains no data variables")
    if len(vars_) == 1:
        return vars_[0]
    return max(vars_, key=lambda v: ds[v].size)


def _time_ka(da: xr.DataArray, time_name: str) -> np.ndarray:
    vals = np.asarray(da[time_name].values)
    if np.issubdtype(vals.dtype, np.number):
        vals = vals.astype(float)
        mn = float(np.nanmin(vals))
        mx = float(np.nanmax(vals))
        if mn <= -1_000_000 and mx <= 100_000:
            return np.abs(vals) / 1000.0
        if mx >= 1_000_000:
            return vals / 1000.0
        if 4500 <= mx <= 5500 and mn >= 0:
            return vals
    n = da.sizes[time_name]
    if n in (5001, 5002, 5003):
        return np.linspace(5000.0, 0.0, n)
    raise ValueError(
        "Cannot infer PALEO-PGEM time coordinate: "
        f"dtype={vals.dtype}, min={np.nanmin(vals)}, max={np.nanmax(vals)}, n={len(vals)}"
    )


def regional_series(path: Path, region: dict[str, float]) -> pd.DataFrame:
    ds = xr.open_dataset(path, decode_times=False)
    try:
        var = _data_var(ds)
        da = ds[var]
        lat = _coord_name(ds, ("lat", "latitude", "y"))
        lon = _coord_name(ds, ("lon", "longitude", "x"))
        time = _coord_name(ds, ("time", "times", "t", "age", "ka"))

        lonvals = np.asarray(da[lon].values, dtype=float)
        if np.nanmax(lonvals) > 180:
            lon_min = region["lon_min"] % 360
            lon_max = region["lon_max"] % 360
        else:
            lon_min = region["lon_min"]
            lon_max = region["lon_max"]

        sub = da.where(
            (da[lat] >= region["lat_min"])
            & (da[lat] <= region["lat_max"])
            & (da[lon] >= lon_min)
            & (da[lon] <= lon_max),
            drop=True,
        )
        if sub.sizes.get(lat, 0) == 0 or sub.sizes.get(lon, 0) == 0:
            raise ValueError(f"Region returned no cells: {region}")
        spatial_dims = [d for d in sub.dims if d != time]
        med = sub.median(dim=spatial_dims, skipna=True).values.astype(float)
        q25 = sub.quantile(0.25, dim=spatial_dims, skipna=True).values.astype(float)
        q75 = sub.quantile(0.75, dim=spatial_dims, skipna=True).values.astype(float)
        ages = _time_ka(sub, time)
        n_cells = int(np.prod([sub.sizes[d] for d in spatial_dims]))
    finally:
        ds.close()

    out = pd.DataFrame(
        {"age_ka": ages, "median": med, "q25": q25, "q75": q75}
    ).replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=["age_ka", "median"]).sort_values("age_ka")
    out = out.drop_duplicates("age_ka", keep="first").reset_index(drop=True)
    out.attrs["n_cells"] = n_cells
    return out


def interp(df: pd.DataFrame, ages_ka: np.ndarray | float) -> np.ndarray:
    return np.interp(
        np.asarray(ages_ka, dtype=float),
        df["age_ka"].to_numpy(float),
        df["median"].to_numpy(float),
    )


def quantile_summary(values: np.ndarray) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    return {
        "min": float(np.nanmin(x)),
        "q05": float(np.nanquantile(x, 0.05)),
        "median": float(np.nanmedian(x)),
        "q95": float(np.nanquantile(x, 0.95)),
        "max": float(np.nanmax(x)),
    }


def enumerate_age_pairs(contract: dict[str, Any]) -> list[tuple[float, float]]:
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


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0 or not np.isfinite(denom):
        return float("nan")
    return float(np.dot(a, b) / denom)


def analyze_region(
    name: str,
    series: dict[str, pd.DataFrame],
    pairs: list[tuple[float, float]],
    beta: np.ndarray,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    min_age = max(float(df.age_ka.min()) for df in series.values())
    max_age = min(float(df.age_ka.max()) for df in series.values())
    cache: dict[float, dict[str, Any]] = {}

    def duration_background(duration_ka: float) -> dict[str, Any]:
        key = round(float(duration_ka), 6)
        if key in cache:
            return cache[key]
        starts = np.arange(min_age, max_age - duration_ka + 1e-9, 10.0)
        if len(starts) < 100:
            raise ValueError(f"Only {len(starts)} matched windows for duration={duration_ka}")
        raw = np.column_stack(
            [interp(series[var], starts) - interp(series[var], starts + duration_ka) for var in VARIABLES]
        )
        means = np.nanmean(raw, axis=0)
        sds = np.nanstd(raw, axis=0, ddof=1)
        if np.any(~np.isfinite(sds)) or np.any(sds <= 0):
            raise ValueError(f"Non-finite background SD for duration={duration_ka}: {sds}")
        z = (raw - means) / sds
        null_cos = np.asarray([cosine(beta, row) for row in z], dtype=float)
        cache[key] = {
            "starts": starts,
            "means": means,
            "sds": sds,
            "null_cos": null_cos,
            "n": int(len(starts)),
        }
        return cache[key]

    rows: list[dict[str, Any]] = []
    for young_ma, old_ma in pairs:
        young_ka = young_ma * 1000.0
        old_ka = old_ma * 1000.0
        duration = old_ka - young_ka
        bg = duration_background(duration)
        delta = np.asarray(
            [float(interp(series[var], young_ka) - interp(series[var], old_ka)) for var in VARIABLES]
        )
        z = (delta - bg["means"]) / bg["sds"]
        c = cosine(beta, z)
        null_cos = bg["null_cos"]
        pct = float((np.sum(null_cos <= c) + 0.5) / (len(null_cos) + 1.0))
        rows.append(
            {
                "region": name,
                "young_ma": young_ma,
                "old_ma": old_ma,
                "duration_ka": duration,
                "delta": {v: float(delta[i]) for i, v in enumerate(VARIABLES)},
                "background_z": {v: float(z[i]) for i, v in enumerate(VARIABLES)},
                "raw_direction_agreement": {
                    v: bool(beta[i] * delta[i] > 0) for i, v in enumerate(VARIABLES)
                },
                "z_direction_agreement": {
                    v: bool(beta[i] * z[i] > 0) for i, v in enumerate(VARIABLES)
                },
                "cosine_similarity": c,
                "cosine_null_percentile": pct,
                "n_duration_matched_windows": bg["n"],
            }
        )

    cosines = np.asarray([r["cosine_similarity"] for r in rows], dtype=float)
    pcts = np.asarray([r["cosine_null_percentile"] for r in rows], dtype=float)
    central = min(rows, key=lambda r: abs(r["young_ma"] - 0.74) + abs(r["old_ma"] - 0.79))
    variable_agreement = {}
    for var in VARIABLES:
        variable_agreement[var] = {
            "raw_direction_fraction": float(np.mean([r["raw_direction_agreement"][var] for r in rows])),
            "background_z_direction_fraction": float(np.mean([r["z_direction_agreement"][var] for r in rows])),
        }
    summary = {
        "region": name,
        "n_grid_cells": int(next(iter(series.values())).attrs.get("n_cells", 0)),
        "n_chronology_scenarios": int(len(rows)),
        "cosine_similarity": quantile_summary(cosines),
        "cosine_null_percentile": quantile_summary(pcts),
        "fraction_cosine_positive": float(np.mean(cosines > 0)),
        "fraction_cosine_negative": float(np.mean(cosines < 0)),
        "fraction_null_percentile_ge_0_95": float(np.mean(pcts >= 0.95)),
        "fraction_null_percentile_le_0_05": float(np.mean(pcts <= 0.05)),
        "variable_direction_agreement": variable_agreement,
        "central_estimate_pair": central,
    }
    return summary, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    for var in VARIABLES:
        ap.add_argument(f"--{var.lower()}", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    beta_map = contract["environment"]["azami_standardized_orientation_vector"]
    beta = np.asarray([float(beta_map[v]) for v in VARIABLES], dtype=float)
    pairs = enumerate_age_pairs(contract)
    paths = {v: getattr(args, v.lower()) for v in VARIABLES}

    region_summaries: dict[str, Any] = {}
    all_rows: list[dict[str, Any]] = []
    for region_name, bounds in contract["paleolocation_scenarios"].items():
        series = {v: regional_series(paths[v], bounds) for v in VARIABLES}
        summary, rows = analyze_region(region_name, series, pairs, beta)
        region_summaries[region_name] = summary
        all_rows.extend(rows)

    all_cos = np.asarray([r["cosine_similarity"] for r in all_rows], dtype=float)
    all_pct = np.asarray([r["cosine_null_percentile"] for r in all_rows], dtype=float)
    all_q05_positive = all(s["cosine_similarity"]["q05"] > 0 for s in region_summaries.values())
    all_q95_negative = all(s["cosine_similarity"]["q95"] < 0 for s in region_summaries.values())
    tail_high = float(np.mean(all_pct >= 0.95))
    tail_low = float(np.mean(all_pct <= 0.05))
    if all_q05_positive and tail_high >= 0.5:
        classification = "robust_state_trajectory_concordance_under_scenario_envelope"
    elif all_q95_negative and tail_low >= 0.5:
        classification = "robust_state_trajectory_discordance_under_scenario_envelope"
    else:
        classification = "origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty"

    durations = np.asarray([(old - young) * 1000.0 for young, old in pairs], dtype=float)
    result = {
        "contract_version": contract["contract_version"],
        "analysis_scope": "cross-study scenario envelope; not a joint chronology posterior",
        "chronology": {
            "n_valid_age_pairs": len(pairs),
            "duration_ka": quantile_summary(durations),
            "central_pair_ma": [0.74, 0.79],
            "broad_marginal_envelope_ma": [
                contract["chronology_scenarios"]["child_node"]["lower_ma"],
                contract["chronology_scenarios"]["parent_node"]["upper_ma"],
            ],
        },
        "azami_beta_vector": {v: float(beta[i]) for i, v in enumerate(VARIABLES)},
        "region_summaries": region_summaries,
        "cross_scenario_summary": {
            "n_region_by_chronology_scenarios": len(all_rows),
            "cosine_similarity": quantile_summary(all_cos),
            "cosine_null_percentile": quantile_summary(all_pct),
            "fraction_cosine_positive": float(np.mean(all_cos > 0)),
            "fraction_cosine_negative": float(np.mean(all_cos < 0)),
            "fraction_null_percentile_ge_0_95": tail_high,
            "fraction_null_percentile_le_0_05": tail_low,
            "classification": classification,
        },
        "scenario_rows": all_rows,
        "claim_boundary": contract["claim_boundary"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "chronology": result["chronology"],
        "region_summaries": region_summaries,
        "cross_scenario_summary": result["cross_scenario_summary"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
