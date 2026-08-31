#!/usr/bin/env python3
"""Public-data local T3 sensitivity for orientation x hydric regime.

This analysis deliberately uses only the published-age six-taxon East-Asian
scaffold and PALEO-PGEM-Series. It does NOT claim to date the full Japan38
4-6-change history. On the six-taxon scaffold, U/U/U vs D/D/D tip states force
one minimum U->D transition onto the lineage between the Nipponocirsium parent
node (0.79 Ma) and Taiwan-trio crown (0.47 Ma), independent of the three frozen
within-trio topology variants.

The test asks whether Taiwan regional BIO12/BIO15 behaviour inside that
interval is unusual relative to duration-matched windows across the full 5-Myr
PALEO-PGEM series. This is a local historical-environment sensitivity, not a
branch-opportunity null and not evidence of adaptation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

EVENT_OLD_KA = 790.0
EVENT_YOUNG_KA = 470.0
WINDOW_KA = EVENT_OLD_KA - EVENT_YOUNG_KA
TAIWAN = dict(lat_min=21.5, lat_max=25.6, lon_min=119.0, lon_max=122.5)


def _coord_name(ds: xr.Dataset, candidates: tuple[str, ...]) -> str:
    low = {k.lower(): k for k in list(ds.coords) + list(ds.dims)}
    for c in candidates:
        if c in low:
            return low[c]
    raise KeyError(f"coordinate not found among {list(ds.coords)} / {list(ds.dims)}")


def _data_var(ds: xr.Dataset) -> str:
    vars_ = list(ds.data_vars)
    if len(vars_) == 1:
        return vars_[0]
    return max(vars_, key=lambda v: ds[v].size)


def _time_ka(da: xr.DataArray, time_name: str) -> np.ndarray:
    vals = np.asarray(da[time_name].values)
    if np.issubdtype(vals.dtype, np.number):
        vals = vals.astype(float)
        mn = float(np.nanmin(vals))
        mx = float(np.nanmax(vals))
        # PALEO-PGEM currently stores time as numeric "years since 1970", which
        # is not a CF-decodable calendar unit. Preserve the raw values and map
        # negative millions-of-years coordinates to positive ka before present.
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
        f"cannot infer PALEO-PGEM time coordinate: dtype={vals.dtype}, "
        f"min={np.nanmin(vals)}, max={np.nanmax(vals)}, n={len(vals)}"
    )


def regional_series(path: Path) -> pd.DataFrame:
    # decode_times=False is required because PALEO-PGEM uses the nonstandard
    # unit string "years since 1970" for a palaeotime coordinate.
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
    if sub.sizes.get(lat, 0) == 0 or sub.sizes.get(lon, 0) == 0:
        raise ValueError("Taiwan regional selection returned no grid cells")
    spatial_dims = [d for d in sub.dims if d != time]
    med = sub.median(dim=spatial_dims, skipna=True).values.astype(float)
    q25 = sub.quantile(0.25, dim=spatial_dims, skipna=True).values.astype(float)
    q75 = sub.quantile(0.75, dim=spatial_dims, skipna=True).values.astype(float)
    age = _time_ka(sub, time)
    out = pd.DataFrame({"age_ka": age, "median": med, "q25": q25, "q75": q75})
    out = out.replace([np.inf, -np.inf], np.nan).dropna(subset=["age_ka", "median"])
    return out.sort_values("age_ka").reset_index(drop=True)


def window_stats(df: pd.DataFrame, young: float, old: float) -> dict[str, float]:
    w = df[(df.age_ka >= young) & (df.age_ka <= old)].copy()
    if len(w) < 50:
        raise ValueError(f"window {young}-{old} ka has only {len(w)} observations")
    y = w["median"].to_numpy(float)
    return {
        "young_ka": float(young),
        "old_ka": float(old),
        "n_kyr": int(len(w)),
        "mean": float(np.nanmean(y)),
        "sd_time": float(np.nanstd(y, ddof=1)),
        "range_time": float(np.nanmax(y) - np.nanmin(y)),
        "net_change_abs": float(abs(y[-1] - y[0])),
        "mean_abs_1k_change": float(np.nanmean(np.abs(np.diff(y)))),
        "max_abs_1k_change": float(np.nanmax(np.abs(np.diff(y)))),
        "median_spatial_iqr": float(np.nanmedian((w.q75 - w.q25).to_numpy(float))),
    }


def matched_distribution(df: pd.DataFrame, width: float, step: float = 10.0) -> pd.DataFrame:
    max_age = min(5000.0, float(df.age_ka.max()))
    starts = np.arange(0.0, max_age - width + 1e-9, step)
    return pd.DataFrame([window_stats(df, s, s + width) for s in starts])


def percentile(null: pd.DataFrame, observed: float, key: str) -> float:
    vals = null[key].to_numpy(float)
    return float((np.sum(vals <= observed) + 0.5) / (len(vals) + 1.0))


def analyze_one(mean_path: Path, sd_path: Path | None, label: str) -> dict:
    mean_ts = regional_series(mean_path)
    obs = window_stats(mean_ts, EVENT_YOUNG_KA, EVENT_OLD_KA)
    null = matched_distribution(mean_ts, WINDOW_KA)
    metrics = ["sd_time", "range_time", "net_change_abs", "mean_abs_1k_change", "max_abs_1k_change"]
    pct = {m: percentile(null, obs[m], m) for m in metrics}
    out = {
        "variable": label,
        "event_window": obs,
        "duration_matched_5myr_percentiles": pct,
        "n_matched_windows": int(len(null)),
        "null_step_ka": 10.0,
    }
    if sd_path is not None:
        sd_ts = regional_series(sd_path)
        sdw = sd_ts[(sd_ts.age_ka >= EVENT_YOUNG_KA) & (sd_ts.age_ka <= EVENT_OLD_KA)]
        out["emulator_uncertainty_window"] = {
            "median_sd": float(np.nanmedian(sdw["median"])),
            "max_sd": float(np.nanmax(sdw["median"])),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bio12-mean", type=Path, required=True)
    ap.add_argument("--bio12-sd", type=Path)
    ap.add_argument("--bio15-mean", type=Path, required=True)
    ap.add_argument("--bio15-sd", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    result = {
        "contract_version": "chapter2_taiwan_orientation_paleohydric_window_v1",
        "scope": "public-data local dated sensitivity; not full Japan38 T3",
        "trait_state_basis": {
            "Arenicola": {"Cirsium brevicaule": "U", "Cirsium irumtiense": "U"},
            "Nipponocirsium": {
                "Cirsium morii": "U",
                "Cirsium pengii": "D",
                "Cirsium kawakamii": "D",
                "Cirsium tatakaense": "D",
            },
        },
        "dated_scaffold": {
            "arenicola_nipponocirsium_root_ma": 1.02,
            "arenicola_pair_ma": 0.93,
            "nipponocirsium_parent_morii_split_ma": 0.79,
            "taiwan_trio_crown_ma": 0.47,
            "terminal_pair_ma": 0.35,
            "minimum_orientation_transition_window_ma": [0.47, 0.79],
            "logic": "Under unordered minimum-change reconstruction, all three Taiwan-trio tips are D while their sister C. morii and both Arenicola tips are U; one U->D change is therefore required on the 0.79-to-0.47 Ma lineage, independent of within-trio resolution.",
        },
        "paleolocation": {
            "region": "Taiwan regional grid uncertainty",
            **TAIWAN,
            "reason": "parent and descendant focal Nipponocirsium concepts are Taiwan taxa; no single modern descendant coordinate is substituted for the ancestral branch",
        },
        "BIO12": analyze_one(args.bio12_mean, args.bio12_sd, "BIO12_annual_precipitation"),
        "BIO15": analyze_one(args.bio15_mean, args.bio15_sd, "BIO15_precipitation_seasonality"),
        "interpretation_rule": {
            "high_variability_signal": "event-window variability metric percentile >=0.95 in the duration-matched 5-Myr climate-window distribution",
            "low_or_typical": "percentile <0.95; do not promote historical hydric alignment",
            "claim_ceiling": "Even >=0.95 is only a local historical-environment sensitivity because the null is climate-window matched, not a full branch-opportunity/topology/age posterior null.",
        },
        "prohibitions": [
            "do not generalize this single local event to all 4-6 Japan38 orientation changes",
            "do not call rain adaptation or adaptive convergence",
            "do not treat central published node ages as an exact posterior chronogram",
            "do not substitute current tip niches for palaeoclimate",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
