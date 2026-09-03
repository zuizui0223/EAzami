#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window, from_bounds

SEED = 20260903
BOOTSTRAPS = 10000
CELL_DEGREES = 0.05
SYSTEMS = {
    "ARENICOLA_BREVICAULE_IRUMTIENSE": ("Cirsium brevicaule", "Cirsium irumtiense"),
    "TAIWAN_KAWAKAMII_TATAKAENSE": ("Cirsium kawakamii", "Cirsium tatakaense"),
}
WORLD_COVER_CLASSES = {
    "open_surface_fraction_500m": {30, 40, 50, 60, 90},
    "bare_built_crop_fraction_500m": {40, 50, 60},
    "bare_sparse_fraction_500m": {60},
    "tree_fraction_500m": {10},
    "wetland_water_fraction_500m": {80, 90, 95},
}
PRIMARY = {
    "open_surface_fraction_500m": 1,
    "hand_median_250m": -1,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--cohort", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--rsds-result", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    return p.parse_args()


def northing(lat: float) -> str:
    base = math.floor(lat)
    return f"N{base:02d}_00" if base >= 0 else f"S{abs(base):02d}_00"


def easting(lon: float) -> str:
    base = math.floor(lon)
    return f"E{base:03d}_00" if base >= 0 else f"W{abs(base):03d}_00"


def worldcover_tile(lat: float, lon: float) -> str:
    lat0 = math.floor(lat / 3.0) * 3
    lon0 = math.floor(lon / 3.0) * 3
    ns = f"N{lat0:02d}" if lat0 >= 0 else f"S{abs(lat0):02d}"
    ew = f"E{lon0:03d}" if lon0 >= 0 else f"W{abs(lon0):03d}"
    return f"{ns}{ew}"


def hand_urls(lat: float, lon: float, base: str) -> list[str]:
    name = f"Copernicus_DSM_COG_10_{northing(lat)}_{easting(lon)}_HAND.tif"
    primary = f"{base.rstrip('/')}/{name}"
    fallback = f"https://glo-30-hand.s3.amazonaws.com/v1/2021/{name}"
    return list(dict.fromkeys([primary, fallback]))


def worldcover_urls(lat: float, lon: float, base: str) -> list[str]:
    tile = worldcover_tile(lat, lon)
    name = f"ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
    primary = f"{base.rstrip('/')}/{name}"
    fallback = f"https://esa-worldcover.s3.amazonaws.com/v200/2021/map/{name}"
    return list(dict.fromkeys([primary, fallback]))


class DatasetCache:
    def __init__(self) -> None:
        self._datasets: dict[str, Any] = {}
        self._resolved: dict[str, str] = {}

    def open_candidates(self, key: str, urls: list[str]):
        if key in self._datasets:
            return self._datasets[key]
        errors: list[str] = []
        for url in urls:
            try:
                ds = rasterio.open(f"/vsicurl/{url}")
                self._datasets[key] = ds
                self._resolved[key] = url
                return ds
            except Exception as exc:  # fail closed after trying declared mirrors
                errors.append(f"{url}: {type(exc).__name__}: {exc}")
        raise RuntimeError("Could not open declared COG candidates for " + key + "\n" + "\n".join(errors))

    @property
    def resolved(self) -> dict[str, str]:
        return dict(self._resolved)

    def close(self) -> None:
        for ds in self._datasets.values():
            ds.close()
        self._datasets.clear()


def clipped_window(ds, lon: float, lat: float, radius_m: float) -> Window:
    lat_delta = radius_m / 111_320.0
    lon_delta = radius_m / max(1.0, 111_320.0 * math.cos(math.radians(lat)))
    requested = from_bounds(
        lon - lon_delta,
        lat - lat_delta,
        lon + lon_delta,
        lat + lat_delta,
        transform=ds.transform,
    ).round_offsets().round_lengths()
    full = Window(0, 0, ds.width, ds.height)
    try:
        return requested.intersection(full)
    except Exception:
        return Window(0, 0, 0, 0)


def read_window(ds, lon: float, lat: float, radius_m: float) -> np.ndarray:
    window = clipped_window(ds, lon, lat, radius_m)
    if window.width <= 0 or window.height <= 0:
        return np.array([], dtype=float)
    return ds.read(1, window=window, masked=False)


def sample_worldcover(ds, lon: float, lat: float) -> dict[str, float]:
    arr = read_window(ds, lon, lat, 500.0)
    if arr.size == 0:
        return {key: float("nan") for key in WORLD_COVER_CLASSES}
    valid_codes = {10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100}
    valid = np.isin(arr, list(valid_codes))
    n = int(valid.sum())
    if n == 0:
        return {key: float("nan") for key in WORLD_COVER_CLASSES}
    return {
        key: float(np.isin(arr[valid], list(classes)).mean())
        for key, classes in WORLD_COVER_CLASSES.items()
    }


def sample_hand(ds, lon: float, lat: float) -> float:
    arr = read_window(ds, lon, lat, 250.0).astype(float, copy=False)
    if arr.size == 0:
        return float("nan")
    valid = np.isfinite(arr) & (arr >= 0)
    if ds.nodata is not None and math.isfinite(float(ds.nodata)):
        valid &= arr != float(ds.nodata)
    if not np.any(valid):
        return float("nan")
    return float(np.median(arr[valid]))


def spatial_cell(frame: pd.DataFrame, degrees: float = CELL_DEGREES) -> pd.Series:
    lat = pd.to_numeric(frame["latitude"], errors="coerce").to_numpy(float)
    lon = pd.to_numeric(frame["longitude"], errors="coerce").to_numpy(float)
    ilat = np.floor((lat + 90.0) / degrees).astype(int)
    ilon = np.floor((lon + 180.0) / degrees).astype(int)
    return pd.Series([f"{a}:{b}" for a, b in zip(ilat, ilon)], index=frame.index)


def finite_values(series: pd.Series) -> np.ndarray:
    return pd.to_numeric(series, errors="coerce").dropna().to_numpy(float)


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    gt = 0
    lt = 0
    for x in a:
        gt += int(np.sum(x > b))
        lt += int(np.sum(x < b))
    return float((gt - lt) / (len(a) * len(b)))


def contrast(white: np.ndarray, coloured: np.ndarray, rng: np.random.Generator, expected_multiplier: int) -> dict[str, Any]:
    white = white[np.isfinite(white)]
    coloured = coloured[np.isfinite(coloured)]
    if len(white) == 0 or len(coloured) == 0:
        return {
            "n_white": int(len(white)),
            "n_coloured": int(len(coloured)),
            "median_white": float("nan"),
            "median_coloured": float("nan"),
            "difference_white_minus_coloured": float("nan"),
            "bootstrap_95": [float("nan"), float("nan")],
            "cliffs_delta_white_minus_coloured": float("nan"),
            "directional_cliffs_delta": float("nan"),
            "expected_direction_met": False,
            "bootstrap_expected_side_excludes_zero": False,
        }
    observed = float(np.median(white) - np.median(coloured))
    boot = np.empty(BOOTSTRAPS, dtype=float)
    for i in range(BOOTSTRAPS):
        boot[i] = float(
            np.median(rng.choice(white, size=len(white), replace=True))
            - np.median(rng.choice(coloured, size=len(coloured), replace=True))
        )
    ci = [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]
    cd = cliffs_delta(white, coloured)
    expected = bool(expected_multiplier * observed > 0)
    excludes = bool(ci[0] > 0) if expected_multiplier > 0 else bool(ci[1] < 0)
    return {
        "n_white": int(len(white)),
        "n_coloured": int(len(coloured)),
        "median_white": float(np.median(white)),
        "median_coloured": float(np.median(coloured)),
        "difference_white_minus_coloured": observed,
        "bootstrap_95": ci,
        "cliffs_delta_white_minus_coloured": cd,
        "directional_cliffs_delta": float(expected_multiplier * cd),
        "expected_direction_met": expected,
        "bootstrap_expected_side_excludes_zero": excludes,
    }


def cell_medians(frame: pd.DataFrame, metric: str) -> pd.DataFrame:
    work = frame[["taxon_name", "latitude", "longitude", metric]].copy()
    work[metric] = pd.to_numeric(work[metric], errors="coerce")
    work = work[work[metric].notna()].copy()
    if work.empty:
        return pd.DataFrame(columns=["taxon_name", "cell_id", metric])
    work["cell_id"] = spatial_cell(work)
    return work.groupby(["taxon_name", "cell_id"], as_index=False)[metric].median()


def metric_payload(frame: pd.DataFrame, metric: str, expected_multiplier: int, rng: np.random.Generator) -> dict[str, Any]:
    system_payload: dict[str, Any] = {}
    robust_count = 0
    obs_count = 0
    cell_count = 0
    cells = cell_medians(frame, metric)
    for system_id, (white_taxon, coloured_taxon) in SYSTEMS.items():
        part = frame[frame["system_id"].eq(system_id)]
        obs = contrast(
            finite_values(part.loc[part["taxon_name"].eq(white_taxon), metric]),
            finite_values(part.loc[part["taxon_name"].eq(coloured_taxon), metric]),
            rng,
            expected_multiplier,
        )
        cell_part = cells[cells["taxon_name"].isin([white_taxon, coloured_taxon])]
        cell = contrast(
            finite_values(cell_part.loc[cell_part["taxon_name"].eq(white_taxon), metric]),
            finite_values(cell_part.loc[cell_part["taxon_name"].eq(coloured_taxon), metric]),
            rng,
            expected_multiplier,
        )
        obs_count += int(obs["expected_direction_met"])
        cell_count += int(cell["expected_direction_met"])
        robust = bool(obs["expected_direction_met"] and cell["expected_direction_met"])
        robust_count += int(robust)
        system_payload[system_id] = {
            "white_taxon": white_taxon,
            "coloured_taxon": coloured_taxon,
            "observation_level": obs,
            "spatial_0_05_degree_cell_sensitivity": cell,
            "robust_expected_direction": robust,
        }
    return {
        "expected_white_minus_coloured_multiplier": expected_multiplier,
        "systems": system_payload,
        "observation_direction_count": obs_count,
        "cell_direction_count": cell_count,
        "robust_shared_direction_count": robust_count,
        "robust_shared_direction": robust_count == 2,
    }


def main() -> int:
    args = parse_args()
    cohort = pd.read_csv(args.cohort, dtype={"obs_id": str}, low_memory=False)
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    rsds = json.loads(args.rsds_result.read_text(encoding="utf-8"))
    required = {"obs_id", "taxon_name", "system_id", "pair_role", "latitude", "longitude"}
    missing = sorted(required.difference(cohort.columns))
    if missing:
        raise ValueError(f"cohort missing required columns: {missing}")
    if cohort["obs_id"].duplicated().any():
        raise ValueError("cohort obs_id must be unique")
    if len(cohort) != int(contract["input_cohort"]["n_observations"]):
        raise ValueError("cohort row count differs from frozen contract")
    if set(cohort["system_id"]) != set(SYSTEMS):
        raise ValueError("unexpected sister-system set")

    world_base = contract["source_contracts"]["worldcover"]["base_url"]
    hand_base = contract["source_contracts"]["hand"]["base_url"]
    cache = DatasetCache()
    enriched_rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    env_opts = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
        "GDAL_HTTP_MULTIRANGE": "YES",
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
    }
    try:
        with rasterio.Env(**env_opts):
            for row in cohort.to_dict(orient="records"):
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                out = dict(row)
                try:
                    wkey = "worldcover:" + worldcover_tile(lat, lon)
                    wds = cache.open_candidates(wkey, worldcover_urls(lat, lon, world_base))
                    out.update(sample_worldcover(wds, lon, lat))
                except Exception as exc:
                    for key in WORLD_COVER_CLASSES:
                        out[key] = float("nan")
                    errors.append({"obs_id": str(row["obs_id"]), "source": "worldcover", "error": str(exc)})
                try:
                    hkey = "hand:" + northing(lat) + ":" + easting(lon)
                    hds = cache.open_candidates(hkey, hand_urls(lat, lon, hand_base))
                    out["hand_median_250m"] = sample_hand(hds, lon, lat)
                except Exception as exc:
                    out["hand_median_250m"] = float("nan")
                    errors.append({"obs_id": str(row["obs_id"]), "source": "hand", "error": str(exc)})
                enriched_rows.append(out)
    finally:
        cache.close()

    enriched = pd.DataFrame(enriched_rows)
    coverage = {
        metric: float(pd.to_numeric(enriched[metric], errors="coerce").notna().mean())
        for metric in [*WORLD_COVER_CLASSES, "hand_median_250m"]
    }
    if coverage["open_surface_fraction_500m"] < 0.90:
        raise RuntimeError(f"WorldCover primary coverage below 0.90: {coverage['open_surface_fraction_500m']:.3f}")
    if coverage["hand_median_250m"] < 0.90:
        raise RuntimeError(f"HAND primary coverage below 0.90: {coverage['hand_median_250m']:.3f}")

    rng = np.random.default_rng(SEED)
    metrics: dict[str, Any] = {}
    for metric in WORLD_COVER_CLASSES:
        multiplier = 1
        if metric == "tree_fraction_500m":
            multiplier = -1
        elif metric == "wetland_water_fraction_500m":
            multiplier = 1
        metrics[metric] = metric_payload(enriched, metric, multiplier, rng)
    metrics["hand_median_250m"] = metric_payload(enriched, "hand_median_250m", -1, rng)

    open_pass = bool(metrics["open_surface_fraction_500m"]["robust_shared_direction"])
    hand_pass = bool(metrics["hand_median_250m"]["robust_shared_direction"])
    if open_pass and hand_pass:
        classification = "multi_proxy_shared_establishment_context"
    elif open_pass or hand_pass:
        classification = "single_proxy_shared_establishment_context"
    else:
        classification = "no_shared_establishment_proxy"

    rsds_count = int(rsds.get("primary_concordant_systems", -1))
    primary_counts = {
        "current_rsds": rsds_count,
        "open_surface_fraction_500m": int(metrics["open_surface_fraction_500m"]["robust_shared_direction_count"]),
        "hand_median_250m": int(metrics["hand_median_250m"]["robust_shared_direction_count"]),
    }
    max_establishment = max(primary_counts["open_surface_fraction_500m"], primary_counts["hand_median_250m"])

    contrast_rows: list[dict[str, Any]] = []
    for metric, payload in metrics.items():
        for system_id, sys in payload["systems"].items():
            obs = sys["observation_level"]
            cell = sys["spatial_0_05_degree_cell_sensitivity"]
            contrast_rows.append({
                "metric": metric,
                "system_id": system_id,
                "expected_multiplier": payload["expected_white_minus_coloured_multiplier"],
                "delta_observation": obs["difference_white_minus_coloured"],
                "bootstrap_low95": obs["bootstrap_95"][0],
                "bootstrap_high95": obs["bootstrap_95"][1],
                "directional_cliffs_delta_observation": obs["directional_cliffs_delta"],
                "expected_direction_observation": obs["expected_direction_met"],
                "delta_cell": cell["difference_white_minus_coloured"],
                "directional_cliffs_delta_cell": cell["directional_cliffs_delta"],
                "expected_direction_cell": cell["expected_direction_met"],
                "robust_expected_direction": sys["robust_expected_direction"],
            })

    payload = {
        "contract_version": "chapter2_white_establishment_surface_gate_result_v1",
        "source_contract_version": contract["contract_version"],
        "n_observations": int(len(enriched)),
        "n_taxa": int(enriched["taxon_name"].nunique()),
        "coverage": coverage,
        "resolved_remote_cogs": cache.resolved,
        "n_sampling_errors": len(errors),
        "sampling_errors": errors[:20],
        "metrics": metrics,
        "primary_direction_counts": primary_counts,
        "classification": classification,
        "establishment_proxy_more_directionally_replicated_than_rsds": bool(max_establishment > rsds_count),
        "interpretation": (
            "This test asks whether present-day open-establishment or drainage-relative terrain proxies "
            "repeat across the two frozen white-coloured sister systems more consistently than current RSDS. "
            "It does not identify disturbance history, transition-time environment, or selection."
        ),
        "claim_boundary": contract["claim_boundary"],
    }

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out / "chapter2_white_establishment_surface_enriched_cohort_v1.csv", index=False)
    pd.DataFrame(contrast_rows).to_csv(out / "chapter2_white_establishment_surface_system_contrasts_v1.csv", index=False)
    (out / "chapter2_white_establishment_surface_gate_result_v1.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "chapter2_white_establishment_surface_sampling_errors_v1.json").write_text(
        json.dumps(errors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "classification": classification,
        "primary_direction_counts": primary_counts,
        "coverage": coverage,
        "n_sampling_errors": len(errors),
        "more_directionally_replicated_than_rsds": payload["establishment_proxy_more_directionally_replicated_than_rsds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
