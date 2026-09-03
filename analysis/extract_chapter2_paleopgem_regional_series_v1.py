#!/usr/bin/env python3
"""Extract regional median PALEO-PGEM time series for the lineage-differentiation atlas.

This utility is deliberately trait-blind. It receives one public PALEO-PGEM
BIOCLIM mean field and reduces it to the predeclared regional sensitivity boxes
in the lineage-differentiation contract. The output retains the full 5-Myr
1-kyr time axis so downstream background horizons and fixed-window metrics can
be changed only through the frozen analysis contract, not by re-downloading a
trait-selected subset.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


def coord_name(ds: xr.Dataset, candidates: tuple[str, ...]) -> str:
    low = {k.lower(): k for k in list(ds.coords) + list(ds.dims)}
    for candidate in candidates:
        if candidate.lower() in low:
            return low[candidate.lower()]
    raise KeyError(f"coordinate not found among coords={list(ds.coords)} dims={list(ds.dims)}")


def data_var(ds: xr.Dataset) -> str:
    vars_ = list(ds.data_vars)
    if not vars_:
        raise ValueError("NetCDF contains no data variables")
    if len(vars_) == 1:
        return vars_[0]
    return max(vars_, key=lambda v: ds[v].size)


def time_ka(da: xr.DataArray, time_name: str) -> np.ndarray:
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--variable", required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    variable = args.variable.upper()
    allowed = set(contract["paleoclimate"]["available_bioclim_variables_used"])
    if variable not in allowed:
        raise ValueError(f"{variable} is not admitted by contract")

    ds = xr.open_dataset(args.input, decode_times=False)
    try:
        var = data_var(ds)
        da = ds[var]
        lat = coord_name(ds, ("lat", "latitude", "y"))
        lon = coord_name(ds, ("lon", "longitude", "x"))
        time = coord_name(ds, ("time", "times", "t", "age", "ka"))
        ages = time_ka(da, time)
        lonvals = np.asarray(da[lon].values, dtype=float)
        use_360 = bool(np.nanmax(lonvals) > 180)

        rows: list[dict[str, float | int | str]] = []
        for region_name, region in contract["regions"].items():
            lon_min = float(region["lon_min"])
            lon_max = float(region["lon_max"])
            if use_360:
                lon_min %= 360
                lon_max %= 360
            sub = da.where(
                (da[lat] >= float(region["lat_min"]))
                & (da[lat] <= float(region["lat_max"]))
                & (da[lon] >= lon_min)
                & (da[lon] <= lon_max),
                drop=True,
            )
            if sub.sizes.get(lat, 0) == 0 or sub.sizes.get(lon, 0) == 0:
                raise ValueError(f"Region returned no cells: {region_name} {region}")
            spatial_dims = [d for d in sub.dims if d != time]
            med = sub.median(dim=spatial_dims, skipna=True).values.astype(float)
            n_cells = int(np.prod([sub.sizes[d] for d in spatial_dims]))
            if len(med) != len(ages):
                raise ValueError(f"time/value length mismatch for {variable} {region_name}")
            for age, value in zip(ages, med, strict=True):
                if np.isfinite(age) and np.isfinite(value):
                    rows.append(
                        {
                            "variable": variable,
                            "region": region_name,
                            "age_ka": float(age),
                            "regional_median": float(value),
                            "n_grid_cells": n_cells,
                        }
                    )
    finally:
        ds.close()

    out = pd.DataFrame(rows)
    if out.empty:
        raise ValueError("No regional series rows generated")
    out = out.sort_values(["variable", "region", "age_ka"]).drop_duplicates(
        ["variable", "region", "age_ka"], keep="first"
    )
    expected_regions = set(contract["regions"])
    observed_regions = set(out["region"])
    if observed_regions != expected_regions:
        raise ValueError(f"region mismatch observed={sorted(observed_regions)} expected={sorted(expected_regions)}")
    counts = out.groupby("region")["age_ka"].nunique()
    if int(counts.min()) < 4900:
        raise ValueError(f"unexpectedly short time series: {counts.to_dict()}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(
        json.dumps(
            {
                "variable": variable,
                "regions": len(expected_regions),
                "rows": int(len(out)),
                "age_min_ka": float(out.age_ka.min()),
                "age_max_ka": float(out.age_ka.max()),
                "cells_by_region": out.groupby("region")["n_grid_cells"].first().astype(int).to_dict(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
