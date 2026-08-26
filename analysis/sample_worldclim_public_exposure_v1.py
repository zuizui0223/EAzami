#!/usr/bin/env python3
"""Sample WorldClim 2.1 public exposure normals at frozen colour observations.

WorldClim baseline: 1970-2000, 10 arc-minutes. This script samples monthly
solar radiation, wind speed, water-vapor pressure, and average temperature at
the exact public-image colour observation coordinates. It derives a monthly
mean-temperature VPD proxy as saturation vapor pressure at tavg minus WorldClim
water-vapor pressure, clipped at zero, then averages monthly values.

This is an independent public-data sensitivity baseline, not a replacement for
or merge with the existing CHELSA environment gate.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

MONTHS = tuple(range(1, 13))
VARIABLES = ("srad", "wind", "vapr", "tavg")


def saturation_vapor_pressure_kpa(temp_c):
    arr = np.asarray(temp_c, dtype=float)
    return 0.6108 * np.exp((17.27 * arr) / (arr + 237.3))


def _sample_one(path: Path, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as src:
        coords = list(zip(lon.tolist(), lat.tolist()))
        out = []
        nodata = src.nodata
        for sample in src.sample(coords, masked=True):
            value = sample[0]
            if np.ma.is_masked(value):
                out.append(np.nan)
                continue
            value = float(value)
            if nodata is not None and math.isclose(value, float(nodata), rel_tol=0, abs_tol=1e-12):
                out.append(np.nan)
            else:
                out.append(value)
        return np.asarray(out, dtype=float)


def sample_worldclim(coords_csv: Path, worldclim_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(coords_csv)
    lon = df["longitude"].to_numpy(dtype=float)
    lat = df["latitude"].to_numpy(dtype=float)

    monthly: dict[str, list[np.ndarray]] = {v: [] for v in VARIABLES}
    for variable in VARIABLES:
        for month in MONTHS:
            path = worldclim_dir / f"wc2.1_10m_{variable}_{month:02d}.tif"
            if not path.exists():
                raise FileNotFoundError(path)
            monthly[variable].append(_sample_one(path, lon, lat))

    arrays = {v: np.column_stack(monthly[v]) for v in VARIABLES}
    complete = np.ones(len(df), dtype=bool)
    for arr in arrays.values():
        complete &= np.isfinite(arr).all(axis=1)

    es = saturation_vapor_pressure_kpa(arrays["tavg"])
    vpd_monthly = np.maximum(es - arrays["vapr"], 0.0)

    out = df.copy()
    out["worldclim_complete_48_monthly_cells"] = complete
    out["worldclim_srad_annual_mean_kj_m2_day"] = np.nanmean(arrays["srad"], axis=1)
    out["worldclim_wind_annual_mean_m_s"] = np.nanmean(arrays["wind"], axis=1)
    out["worldclim_vapr_annual_mean_kpa"] = np.nanmean(arrays["vapr"], axis=1)
    out["worldclim_tavg_annual_mean_c"] = np.nanmean(arrays["tavg"], axis=1)
    out["worldclim_vpd_tavg_proxy_annual_mean_kpa"] = np.nanmean(vpd_monthly, axis=1)
    return out


def aggregate_species(obs: pd.DataFrame) -> pd.DataFrame:
    metric_cols = [
        "corolla_lab_lightness_median",
        "worldclim_srad_annual_mean_kj_m2_day",
        "worldclim_wind_annual_mean_m_s",
        "worldclim_vapr_annual_mean_kpa",
        "worldclim_tavg_annual_mean_c",
        "worldclim_vpd_tavg_proxy_annual_mean_kpa",
    ]
    rows = []
    for (jpn, taxon), group in obs.groupby(["paper_japan_member_id", "taxon_name"], sort=True):
        complete = group[group["worldclim_complete_48_monthly_cells"]]
        row = {
            "paper_japan_member_id": jpn,
            "taxon_name": taxon,
            "n_colour_observations": int(len(group)),
            "n_worldclim_complete_observations": int(len(complete)),
        }
        for col in metric_cols:
            row[col + "_species_median"] = float(complete[col].median()) if len(complete) else None
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--coordinates", type=Path, required=True)
    p.add_argument("--worldclim-dir", type=Path, required=True)
    p.add_argument("--observation-output", type=Path, required=True)
    p.add_argument("--summary-output", type=Path, required=True)
    p.add_argument("--metadata-output", type=Path, required=True)
    args = p.parse_args()

    obs = sample_worldclim(args.coordinates, args.worldclim_dir)
    summary = aggregate_species(obs)
    args.observation_output.parent.mkdir(parents=True, exist_ok=True)
    obs.to_csv(args.observation_output, index=False)
    summary.to_csv(args.summary_output, index=False)

    metadata = {
        "contract_version": "japan38_global_colour_worldclim_sampling_v1",
        "worldclim_version": "2.1",
        "baseline": "1970-2000",
        "resolution": "10 arc-minutes",
        "variables": {
            "srad": "monthly solar radiation, kJ m^-2 day^-1",
            "wind": "monthly wind speed, m s^-1",
            "vapr": "monthly water vapor pressure, kPa",
            "tavg": "monthly average temperature, degrees C",
            "vpd_tavg_proxy": "max(es(tavg)-vapr, 0), kPa; monthly values averaged across 12 months",
        },
        "coordinate_rows": int(len(obs)),
        "complete_rows": int(obs["worldclim_complete_48_monthly_cells"].sum()),
        "species_rows": int(len(summary)),
        "claim_boundary": "Independent WorldClim public-data sensitivity baseline for global exact-concept species proxies; not a Japan-local colour-history analysis and not interchangeable with the CHELSA gate.",
    }
    args.metadata_output.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
