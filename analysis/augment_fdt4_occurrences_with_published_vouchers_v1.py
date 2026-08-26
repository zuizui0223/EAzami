#!/usr/bin/env python3
"""Augment a frozen FDT4 occurrence panel with source-backed voucher localities.

Every eligible voucher row is admitted before spatial thinning. Existing guarded
GBIF cells win ties, so published vouchers can add geographic coverage but cannot
silently replace the frozen public-occurrence representatives.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_focal_occurrence_niche_sample_information_v1 as niche_v1  # noqa: E402


REQUIRED_VOUCHER_COLUMNS = {
    "record_id", "taxon", "source_class", "source_doi", "source_url",
    "source_locator", "voucher", "locality", "latitude", "longitude",
    "coordinate_crs", "coordinate_precision_arcminutes",
    "coordinate_uncertainty_m", "coordinate_uncertainty_basis",
    "basis_of_record", "evidence_scope",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_voucher_seed(seed: pd.DataFrame, config: dict) -> pd.DataFrame:
    missing = sorted(REQUIRED_VOUCHER_COLUMNS.difference(seed.columns))
    if missing:
        raise ValueError(f"Voucher seed is missing columns: {missing}")
    if seed.empty:
        raise ValueError("Voucher seed is empty")
    if seed["record_id"].astype(str).duplicated().any():
        raise ValueError("Voucher record_id must be unique")
    if seed[["taxon", "voucher"]].astype(str).duplicated().any():
        raise ValueError("Voucher must be unique within taxon")

    out = seed.copy()
    for column in ("latitude", "longitude", "coordinate_uncertainty_m"):
        out[column] = pd.to_numeric(out[column], errors="coerce")
        if out[column].isna().any():
            raise ValueError(f"Voucher seed contains invalid {column}")
    if set(out["source_class"].astype(str)) != {"published_voucher"}:
        raise ValueError("Only published_voucher source_class is admitted")
    if set(out["coordinate_crs"].astype(str)) != {"WGS84"}:
        raise ValueError("Every voucher coordinate must be explicitly WGS84")
    if (out["coordinate_uncertainty_m"] <= 0).any():
        raise ValueError("Voucher coordinate uncertainty must be positive")
    max_unc = float(config["gbif"]["max_coordinate_uncertainty_m_primary"])
    if (out["coordinate_uncertainty_m"] > max_unc).any():
        raise ValueError("Voucher coordinate uncertainty exceeds the frozen primary limit")

    required_text = [
        "record_id", "taxon", "source_doi", "source_url", "source_locator",
        "voucher", "locality", "coordinate_uncertainty_basis", "evidence_scope",
    ]
    for column in required_text:
        if out[column].fillna("").astype(str).str.strip().eq("").any():
            raise ValueError(f"Voucher seed contains blank {column}")

    bounds = config["gbif"]["japan_bounds"]
    in_bounds = (
        out["latitude"].between(float(bounds["lat_min"]), float(bounds["lat_max"]))
        & out["longitude"].between(float(bounds["lon_min"]), float(bounds["lon_max"]))
    )
    if not in_bounds.all():
        raise ValueError("Voucher seed contains coordinates outside the frozen Taiwan bounds")
    return out


def voucher_occurrence_rows(seed: pd.DataFrame, thin_degrees: float) -> pd.DataFrame:
    rows = pd.DataFrame({
        "scientific_name_query": seed["taxon"].astype(str),
        "gbif_match_key": pd.NA,
        "gbif_match_scientific_name": seed["taxon"].astype(str),
        "gbif_key": seed["record_id"].astype(str),
        "acceptedScientificName": seed["taxon"].astype(str),
        "scientificName": seed["taxon"].astype(str),
        "basisOfRecord": seed["basis_of_record"].astype(str),
        "year": pd.NA,
        "decimalLatitude": seed["latitude"].astype(float),
        "decimalLongitude": seed["longitude"].astype(float),
        "coordinateUncertaintyInMeters": seed["coordinate_uncertainty_m"].astype(float),
        "stateProvince": "Taiwan",
        "locality": seed["locality"].astype(str),
        "island": "Taiwan",
        "datasetKey": seed["source_doi"].astype(str),
        "issues": "PUBLISHED_COORDINATE_TO_ARCMINUTE",
        "latitude": seed["latitude"].astype(float),
        "longitude": seed["longitude"].astype(float),
        "coordinate_uncertainty_m": seed["coordinate_uncertainty_m"].astype(float),
        "strict_coordinate_quality": True,
        "record_source_class": seed["source_class"].astype(str),
        "source_record_id": seed["record_id"].astype(str),
        "source_doi": seed["source_doi"].astype(str),
        "source_url": seed["source_url"].astype(str),
        "source_locator": seed["source_locator"].astype(str),
        "voucher": seed["voucher"].astype(str),
        "coordinate_uncertainty_basis": seed["coordinate_uncertainty_basis"].astype(str),
        "evidence_scope": seed["evidence_scope"].astype(str),
    })
    rows["thin_lat"] = np.floor(rows["latitude"] / thin_degrees).astype(int)
    rows["thin_lon"] = np.floor(rows["longitude"] / thin_degrees).astype(int)
    rows["year_sort"] = -1
    return rows


def augment_occurrences(
    existing: pd.DataFrame,
    voucher_seed: pd.DataFrame,
    config: dict,
    *,
    sampler: Callable[[pd.DataFrame, dict[str, str]], tuple[pd.DataFrame, dict]],
) -> tuple[pd.DataFrame, dict]:
    seed = validate_voucher_seed(voucher_seed, config)
    thin = float(config["gbif"]["spatial_thin_degrees"])
    vouchers = voucher_occurrence_rows(seed, thin)
    env_cols = [f"chelsa_{key}" for key in config["chelsa"]["predictors"]]
    if not set(env_cols).issubset(seed.columns) or seed[env_cols].isna().any(axis=None):
        vouchers, raster_meta = sampler(vouchers, config["chelsa"]["predictors"])
    else:
        vouchers[env_cols] = seed[env_cols].to_numpy()
        raster_meta = {"mode": "seed_values"}
    vouchers["environment_complete"] = vouchers[env_cols].notna().all(axis=1)
    vouchers = vouchers.loc[vouchers["environment_complete"]].copy()

    current = existing.copy()
    for column, value in {
        "record_source_class": "guarded_gbif",
        "source_record_id": "",
        "source_doi": "",
        "source_url": "",
        "source_locator": "",
        "voucher": "",
        "coordinate_uncertainty_basis": "GBIF_coordinateUncertaintyInMeters",
        "evidence_scope": "source_name_guarded_GBIF_occurrence",
    }.items():
        if column not in current.columns:
            current[column] = value
    if "thin_lat" not in current.columns or "thin_lon" not in current.columns:
        current["thin_lat"] = np.floor(pd.to_numeric(current["latitude"]) / thin).astype(int)
        current["thin_lon"] = np.floor(pd.to_numeric(current["longitude"]) / thin).astype(int)

    cell_columns = ["scientific_name_query", "thin_lat", "thin_lon"]
    current_cells = set(map(tuple, current[cell_columns].itertuples(index=False, name=None)))
    vouchers["cell_already_in_frozen_panel"] = [
        tuple(row) in current_cells
        for row in vouchers[cell_columns].itertuples(index=False, name=None)
    ]
    eligible_new = vouchers.loc[~vouchers["cell_already_in_frozen_panel"]].copy()
    eligible_new = eligible_new.sort_values(
        cell_columns + ["coordinate_uncertainty_m", "source_record_id"]
    ).drop_duplicates(cell_columns, keep="first")

    # All-NA compatibility columns (for example GBIF taxon keys on published
    # vouchers) add no information and trigger dtype-dependent concat behavior.
    eligible_for_concat = eligible_new.dropna(axis=1, how="all")
    combined = pd.concat([current, eligible_for_concat], ignore_index=True, sort=False)
    combined = combined.sort_values(cell_columns + ["record_source_class", "gbif_key"]).reset_index(drop=True)
    if combined.duplicated(cell_columns).any():
        raise AssertionError("Augmented occurrence panel is not unique by frozen spatial cell")
    combined["environment_complete"] = combined[env_cols].notna().all(axis=1)

    if len(combined) >= 3:
        z = StandardScaler().fit_transform(combined[env_cols].astype(float))
        pcs = PCA(n_components=min(3, len(env_cols), len(combined))).fit_transform(z)
        for index in range(pcs.shape[1]):
            combined[f"PC{index + 1}"] = pcs[:, index]

    before = current.groupby("scientific_name_query").size().to_dict()
    after = combined.groupby("scientific_name_query").size().to_dict()
    details = []
    for taxon in sorted(seed["taxon"].unique()):
        taxon_vouchers = vouchers.loc[vouchers["scientific_name_query"].eq(taxon)]
        taxon_added = eligible_new.loc[eligible_new["scientific_name_query"].eq(taxon)]
        details.append({
            "taxon": taxon,
            "frozen_cells_before": int(before.get(taxon, 0)),
            "published_vouchers_screened": int(len(taxon_vouchers)),
            "published_vouchers_in_existing_cells": int(taxon_vouchers["cell_already_in_frozen_panel"].sum()),
            "published_voucher_cells_added": int(len(taxon_added)),
            "environment_complete_cells_after": int(after.get(taxon, 0)),
            "frozen_n_ge_10_gate": bool(after.get(taxon, 0) >= 10),
            "added_record_ids": sorted(taxon_added["source_record_id"].astype(str).tolist()),
        })

    summary = {
        "contract_version": "fdt4_taiwan_published_voucher_augmentation_v1",
        "selection_rule": "all eligible published vouchers are screened before frozen 0.05-degree cell thinning; existing guarded GBIF cells win ties",
        "spatial_thin_degrees": thin,
        "voucher_rows_screened": int(len(seed)),
        "voucher_environment_complete_rows": int(len(vouchers)),
        "voucher_cells_added": int(len(eligible_new)),
        "taxa": details,
        "raster_sampling": raster_meta,
        "claim_boundary": "Published voucher localities increase present-day taxon niche coverage. They do not make the taxon-concept orientation states same-voucher phenotypes and do not establish historical range, convergence, adaptation or causation.",
    }
    return combined, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--voucher-seed", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    existing = pd.read_csv(args.occurrences)
    seed = pd.read_csv(args.voucher_seed)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    combined, summary = augment_occurrences(
        existing, seed, config, sampler=niche_v1.sample_chelsa
    )
    summary["inputs"] = {
        "occurrences": args.occurrences.as_posix(),
        "occurrences_sha256": sha256(args.occurrences),
        "voucher_seed": args.voucher_seed.as_posix(),
        "voucher_seed_sha256": sha256(args.voucher_seed),
        "config": args.config.as_posix(),
        "config_sha256": sha256(args.config),
    }
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.out_csv, index=False)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
