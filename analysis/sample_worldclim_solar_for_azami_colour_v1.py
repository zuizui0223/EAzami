#!/usr/bin/env python3
"""Sample WorldClim 2.1 solar radiation and climate at Azami image cells.

The script downloads official 2.5-minute WorldClim archives, records response and
file checksums, samples annual-mean monthly solar radiation plus BIO1/BIO12/BIO15,
and joins values back to the schema-resolved public colour observations. Sampling
is performed once per unique 0.05-degree cell to avoid redundant raster reads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
import requests

URLS = {
    "srad": "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_2.5m_srad.zip",
    "bio": "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_2.5m_bio.zip",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--observations", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(session: requests.Session, label: str, url: str, cache: Path) -> dict[str, Any]:
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / Path(url).name
    headers: dict[str, str] = {}
    if not dest.exists() or dest.stat().st_size == 0:
        with session.get(url, stream=True, timeout=180, allow_redirects=True) as response:
            response.raise_for_status()
            headers = {k.casefold(): v for k, v in response.headers.items()}
            with dest.open("wb") as out:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        out.write(chunk)
    extract = cache / label
    extract.mkdir(exist_ok=True)
    marker = extract / ".complete"
    if not marker.exists():
        with zipfile.ZipFile(dest) as zf:
            for member in zf.infolist():
                p = Path(member.filename)
                if member.is_dir() or p.is_absolute() or ".." in p.parts:
                    continue
                if p.suffix.casefold() != ".tif":
                    continue
                zf.extract(member, extract)
        marker.write_text("ok\n")
    return {
        "label": label,
        "url": url,
        "archive_path": str(dest),
        "archive_bytes": dest.stat().st_size,
        "archive_sha256": sha256(dest),
        "etag": headers.get("etag", ""),
        "last_modified": headers.get("last-modified", ""),
        "tif_count": len(list(extract.rglob("*.tif"))),
    }


def find_single(root: Path, patterns: list[str]) -> Path:
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(root.rglob(pattern))
    unique = sorted(set(matches))
    if len(unique) != 1:
        raise RuntimeError(f"expected one raster for {patterns}, found {unique}")
    return unique[0]


def sample_raster(path: Path, coordinates: list[tuple[float, float]]) -> np.ndarray:
    with rasterio.open(path) as src:
        if src.crs is None or str(src.crs).upper() not in {"EPSG:4326", "OGC:CRS84"}:
            raise RuntimeError(f"unexpected raster CRS {src.crs} for {path}")
        values = np.array([float(v[0]) for v in src.sample(coordinates)], dtype=float)
        nodata = src.nodata
        if nodata is not None:
            values[np.isclose(values, nodata)] = np.nan
        values[~np.isfinite(values)] = np.nan
        return values


def main() -> int:
    a = parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    observations = pd.read_csv(a.observations)
    required = {"latitude", "longitude", "canonical_cell_005_lat", "canonical_cell_005_lon"}
    missing = required - set(observations.columns)
    if missing:
        raise KeyError(sorted(missing))
    cells = (
        observations[["canonical_cell_005_lat", "canonical_cell_005_lon", "latitude", "longitude"]]
        .dropna()
        .sort_values(["canonical_cell_005_lat", "canonical_cell_005_lon"])
        .drop_duplicates(["canonical_cell_005_lat", "canonical_cell_005_lon"], keep="first")
        .reset_index(drop=True)
    )
    coords = list(zip(cells.longitude.astype(float), cells.latitude.astype(float)))
    if not coords:
        raise RuntimeError("no valid observation coordinates")

    session = requests.Session()
    session.headers.update({"User-Agent": "EAzami-Azami-public-solar-analysis/1.0"})
    provenance = [download(session, label, url, a.cache_dir) for label, url in URLS.items()]
    srad_root = a.cache_dir / "srad"
    bio_root = a.cache_dir / "bio"

    srad_paths = []
    for month in range(1, 13):
        srad_paths.append(find_single(srad_root, [f"*srad_{month:02d}.tif", f"*srad{month:02d}.tif"]))
    srad = np.vstack([sample_raster(path, coords) for path in srad_paths])
    cells["worldclim21_srad_annual_mean"] = np.nanmean(srad, axis=0)
    cells["worldclim21_srad_months_complete"] = np.isfinite(srad).sum(axis=0)

    for number, label in [(1, "bio01"), (12, "bio12"), (15, "bio15")]:
        path = find_single(bio_root, [f"*bio_{number}.tif", f"*bio{number}.tif"])
        cells[f"worldclim21_{label}"] = sample_raster(path, coords)

    merged = observations.merge(
        cells.drop(columns=["latitude", "longitude"]),
        on=["canonical_cell_005_lat", "canonical_cell_005_lon"],
        how="left",
        validate="many_to_one",
    )
    env_cols = ["worldclim21_srad_annual_mean", "worldclim21_bio01", "worldclim21_bio12", "worldclim21_bio15"]
    merged["worldclim_environment_complete"] = merged[env_cols].notna().all(axis=1) & merged["worldclim21_srad_months_complete"].eq(12)
    merged.to_csv(a.out_dir / "azami_colour_worldclim_environment_v1.csv", index=False)
    cells.to_csv(a.out_dir / "azami_colour_worldclim_unique_cells_v1.csv", index=False)

    payload = {
        "contract_version": "azami_colour_worldclim_environment_v1",
        "worldclim_version": "2.1",
        "spatial_resolution": "2.5 arc-minutes",
        "solar_metric": "arithmetic mean of the 12 WorldClim monthly solar-radiation layers at each unique 0.05-degree observation cell representative coordinate",
        "solar_units": "retain native WorldClim srad units; downstream effects are standardized",
        "climate_covariates": ["BIO1 annual mean temperature", "BIO12 annual precipitation", "BIO15 precipitation seasonality"],
        "download_provenance": provenance,
        "observation_rows": int(len(observations)),
        "unique_cells": int(len(cells)),
        "environment_complete_rows": int(merged["worldclim_environment_complete"].sum()),
        "environment_complete_taxa": int(merged.loc[merged["worldclim_environment_complete"], "taxon_raw"].nunique()),
        "claim_boundary": "Raster sampling supplies present-day climatological covariates. It does not calibrate photographic colour, reconstruct historical radiation or establish adaptive causation.",
    }
    (a.out_dir / "azami_colour_worldclim_environment_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
