#!/usr/bin/env python3
"""Build deduplicated Taiwan taxonomic-alias occurrence sensitivity tiers.

Alias-derived cells are added only when absent from the corresponding already-frozen
Taiwan GBIF + direct-TBN tier. Spatial and uncertainty rules remain unchanged.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

import build_focal_occurrence_niche_sample_information_v1 as niche


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--niche-config", type=Path, required=True)
    p.add_argument("--alias-contract", type=Path, required=True)
    p.add_argument("--gbif-occurrences", type=Path, required=True)
    p.add_argument("--direct-native", type=Path, required=True)
    p.add_argument("--direct-broad", type=Path, required=True)
    p.add_argument("--alias-audit", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def as_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def env_only(frame: pd.DataFrame) -> pd.DataFrame:
    if "environment_complete" in frame.columns:
        return frame.loc[as_bool(frame["environment_complete"])].copy()
    return frame.copy()


def cell_from_row(row: pd.Series, thin: float) -> tuple[int, int] | None:
    if "thin_lat" in row and "thin_lon" in row and pd.notna(row.get("thin_lat")) and pd.notna(row.get("thin_lon")):
        return int(row["thin_lat"]), int(row["thin_lon"])
    lat = pd.to_numeric(pd.Series([row.get("latitude", row.get("decimal_latitude"))]), errors="coerce").iloc[0]
    lon = pd.to_numeric(pd.Series([row.get("longitude", row.get("decimal_longitude"))]), errors="coerce").iloc[0]
    if pd.isna(lat) or pd.isna(lon):
        return None
    return math.floor(float(lat) / thin), math.floor(float(lon) / thin)


def cell_sets(frames: list[pd.DataFrame], taxa: list[str], thin: float) -> dict[str, set[tuple[int, int]]]:
    out = {t: set() for t in taxa}
    for frame in frames:
        for _, row in env_only(frame).iterrows():
            taxon = str(row.get("scientific_name_query", ""))
            if taxon not in out:
                continue
            cell = cell_from_row(row, thin)
            if cell is not None:
                out[taxon].add(cell)
    return out


def source_mask(tbn: pd.DataFrame, tier: str) -> pd.Series:
    strict = as_bool(tbn["strict_le_10km"])
    external = tbn["external_id"].fillna("").astype(str)
    source = tbn["source"].fillna("").astype(str)
    licence = tbn["license"].fillna("").astype(str)
    if tier == "native":
        return strict & external.str.startswith("tbn.dp.plant.") & source.str.startswith("https://plant.tbn.org.tw/occurrence/") & licence.str.contains("CC BY", case=False, regex=False)
    if tier == "broad":
        return strict & ~external.str.startswith("gbif:")
    raise ValueError(tier)


def select_new_cells(tbn: pd.DataFrame, base_cells: dict[str, set[tuple[int, int]]], tier: str) -> pd.DataFrame:
    x = tbn.loc[source_mask(tbn, tier)].copy()
    if x.empty:
        return x
    x["coordinate_uncertainty_m"] = pd.to_numeric(x["coordinate_uncertainty_m"], errors="coerce")
    keep = []
    for _, row in x.iterrows():
        taxon = str(row["query_taxon"])
        cell = (int(row["thin_lat"]), int(row["thin_lon"]))
        keep.append(taxon in base_cells and cell not in base_cells[taxon])
    x = x.loc[keep].copy()
    if x.empty:
        return x
    x["native_rank"] = ~(
        x["external_id"].fillna("").astype(str).str.startswith("tbn.dp.plant.")
        & x["source"].fillna("").astype(str).str.startswith("https://plant.tbn.org.tw/occurrence/")
    )
    x = x.sort_values(
        ["query_taxon", "thin_lat", "thin_lon", "native_rank", "coordinate_uncertainty_m", "occurrence_id"],
        ascending=[True, True, True, True, True, True],
        na_position="last",
    )
    return x.drop_duplicates(["query_taxon", "thin_lat", "thin_lon"], keep="first").copy()


def sample_environment(selected: pd.DataFrame, predictors: dict[str, str], tier: str) -> pd.DataFrame:
    if selected.empty:
        cols = ["scientific_name_query", "latitude", "longitude", "environment_complete"] + [f"chelsa_{k}" for k in predictors]
        return pd.DataFrame(columns=cols)
    x = pd.DataFrame({
        "scientific_name_query": selected["query_taxon"].astype(str),
        "latitude": pd.to_numeric(selected["decimal_latitude"], errors="coerce"),
        "longitude": pd.to_numeric(selected["decimal_longitude"], errors="coerce"),
        "coordinate_uncertainty_m": pd.to_numeric(selected["coordinate_uncertainty_m"], errors="coerce"),
        "thin_lat": pd.to_numeric(selected["thin_lat"], errors="coerce").astype("Int64"),
        "thin_lon": pd.to_numeric(selected["thin_lon"], errors="coerce").astype("Int64"),
        "tbn_occurrence_id": selected["occurrence_id"].astype(str),
        "tbn_external_id": selected["external_id"].fillna("").astype(str),
        "tbn_source": selected["source"].fillna("").astype(str),
        "tbn_license": selected["license"].fillna("").astype(str),
        "alias_lookup_mode": selected["lookup_mode"].astype(str),
        "alias_matched_name_field": selected["matched_name_field"].astype(str),
        "alias_matched_source_name": selected["matched_source_name"].astype(str),
        "occurrence_source": f"TBN_v2.6_alias_{tier}",
    })
    x, _ = niche.sample_chelsa(x, predictors)
    env_cols = [f"chelsa_{k}" for k in predictors]
    x["environment_complete"] = x[env_cols].notna().all(axis=1)
    return x.loc[x["environment_complete"]].reset_index(drop=True)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    niche_cfg = json.loads(args.niche_config.read_text(encoding="utf-8"))
    alias_cfg = json.loads(args.alias_contract.read_text(encoding="utf-8"))
    taxa = [r["analysis_taxon"] for r in alias_cfg["rules"]]
    thin = float(alias_cfg["global_filters"]["spatial_thin_degrees"])
    predictors = niche_cfg["chelsa"]["predictors"]
    gbif = pd.read_csv(args.gbif_occurrences)
    direct_native = pd.read_csv(args.direct_native)
    direct_broad = pd.read_csv(args.direct_broad)
    audit = pd.read_csv(args.alias_audit)

    payload: dict[str, object] = {
        "contract_version": "fdt4_taiwan_alias_sensitivity_v1",
        "status": "supporting_alias_sensitivity_not_primary_replacement",
        "frozen_gate": ">=10 independent 0.05-degree thinned environment-complete occurrences per taxon",
        "tiers": {},
        "claim_boundary": "Alias additions are deduplicated against the already-frozen Taiwan GBIF + direct-TBN cells. No primary threshold, coordinate filter or taxon state is changed.",
    }

    for tier, direct in (("native", direct_native), ("broad", direct_broad)):
        base_frames = [gbif, direct]
        base_cells = cell_sets(base_frames, taxa, thin)
        selected = select_new_cells(audit, base_cells, tier)
        additions = sample_environment(selected, predictors, tier)
        selected.to_csv(args.out_dir / f"alias_{tier}_selected_new_cells.csv", index=False)
        additions.to_csv(args.out_dir / f"alias_{tier}_additions_environment_complete.csv", index=False)
        add_cells = cell_sets([additions], taxa, thin)
        coverage = []
        for taxon in taxa:
            n_base = len(base_cells[taxon])
            n_add = len(add_cells[taxon])
            coverage.append({
                "taxon": taxon,
                "base_gbif_plus_direct_tbn_cells": n_base,
                "new_alias_environment_complete_cells": n_add,
                "union_cells": n_base + n_add,
                "passes_n_ge_10": n_base + n_add >= int(alias_cfg["global_filters"]["minimum_environment_complete_cells"]),
            })
        pd.DataFrame(coverage).to_csv(args.out_dir / f"alias_{tier}_union_coverage.csv", index=False)
        payload["tiers"][tier] = {
            "selected_alias_cells_before_environment_gate": int(len(selected)),
            "environment_complete_alias_additions": int(len(additions)),
            "coverage": coverage,
        }

    (args.out_dir / "fdt4_taiwan_alias_sensitivity_manifest_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
