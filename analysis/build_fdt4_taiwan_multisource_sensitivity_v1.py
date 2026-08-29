#!/usr/bin/env python3
"""Build versioned Taiwan GBIF + TBN occurrence sensitivities for FDT4.

Primary frozen GBIF-only analysis remains unchanged. This script creates two
outcome-blind multi-source sensitivity tiers from the all-seven-taxon TBN audit:

1. ``native``: only direct TBN Plant occurrence records with explicit TBN source
   URL, tbn.dp.plant external ID, CC BY licence, <=10 km uncertainty, and a new
   0.05-degree cell relative to the source-guarded GBIF panel;
2. ``non_gbif``: any source-name-guarded strict TBN record not explicitly marked
   as a GBIF mirror, again restricted to new GBIF cells.

Both tiers apply the same rule to all seven Taiwan orientation taxa. Neither tier
changes the frozen n>=10 gate. CHELSA v2.1 values are sampled for added records so
existing six-topology PGLS code can consume the outputs without modification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import build_focal_occurrence_niche_sample_information_v1 as niche


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--gbif-occurrences", type=Path, required=True)
    p.add_argument("--tbn-audit", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def select_one_per_cell(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    x = frame.copy()
    x["coordinate_uncertainty_m"] = pd.to_numeric(x["coordinate_uncertainty_m"], errors="coerce")
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


def build_tier(tbn: pd.DataFrame, tier: str) -> pd.DataFrame:
    strict = as_bool(tbn["strict_le_10km"])
    new_cell = as_bool(tbn["new_vs_gbif_thin_cell"])
    external = tbn["external_id"].fillna("").astype(str)
    source = tbn["source"].fillna("").astype(str)
    licence = tbn["license"].fillna("").astype(str)
    if tier == "native":
        mask = (
            strict
            & new_cell
            & external.str.startswith("tbn.dp.plant.")
            & source.str.startswith("https://plant.tbn.org.tw/occurrence/")
            & licence.str.contains("CC BY", case=False, regex=False)
        )
    elif tier == "non_gbif":
        mask = strict & new_cell & ~external.str.startswith("gbif:")
    else:
        raise ValueError(tier)
    return select_one_per_cell(tbn.loc[mask].copy())


def environment_frame(selected: pd.DataFrame, predictors: dict[str, str], tier: str) -> pd.DataFrame:
    if selected.empty:
        cols = ["scientific_name_query", "latitude", "longitude", "environment_complete"] + [f"chelsa_{k}" for k in predictors]
        return pd.DataFrame(columns=cols)
    x = pd.DataFrame(
        {
            "scientific_name_query": selected["query_taxon"].astype(str),
            "latitude": pd.to_numeric(selected["decimal_latitude"], errors="coerce"),
            "longitude": pd.to_numeric(selected["decimal_longitude"], errors="coerce"),
            "coordinate_uncertainty_m": pd.to_numeric(selected["coordinate_uncertainty_m"], errors="coerce"),
            "thin_lat": pd.to_numeric(selected["thin_lat"], errors="coerce").astype("Int64"),
            "thin_lon": pd.to_numeric(selected["thin_lon"], errors="coerce").astype("Int64"),
            "tbn_occurrence_id": selected["occurrence_id"].astype(str),
            "tbn_external_id": selected["external_id"].fillna("").astype(str),
            "tbn_dataset_uuid": selected["dataset_uuid"].fillna("").astype(str),
            "tbn_source": selected["source"].fillna("").astype(str),
            "tbn_license": selected["license"].fillna("").astype(str),
            "occurrence_source": f"TBN_v2.6_{tier}",
        }
    )
    x, _ = niche.sample_chelsa(x, predictors)
    env_cols = [f"chelsa_{k}" for k in predictors]
    x["environment_complete"] = x[env_cols].notna().all(axis=1)
    return x.loc[x["environment_complete"]].reset_index(drop=True)


def count_taxa(gbif: pd.DataFrame, additions: pd.DataFrame, taxa: list[str]) -> list[dict[str, object]]:
    gbif_counts = gbif.groupby("scientific_name_query").size().to_dict()
    add_counts = additions.groupby("scientific_name_query").size().to_dict() if not additions.empty else {}
    rows = []
    for taxon in taxa:
        g = int(gbif_counts.get(taxon, 0))
        a = int(add_counts.get(taxon, 0))
        rows.append({"taxon": taxon, "gbif_environment_complete_cells": g, "added_tbn_cells": a, "union_cells": g + a, "passes_n_ge_10": g + a >= 10})
    return rows


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    gbif = pd.read_csv(args.gbif_occurrences)
    if "environment_complete" in gbif.columns:
        gbif = gbif.loc[as_bool(gbif["environment_complete"])].copy()
    tbn = pd.read_csv(args.tbn_audit)
    taxa = [str(x["scientific_name"]) for x in cfg["taxa"]]
    predictors = cfg["chelsa"]["predictors"]

    payload: dict[str, object] = {
        "contract_version": "fdt4_taiwan_multisource_sensitivity_v1",
        "status": "supporting_sensitivity_not_frozen_primary_replacement",
        "frozen_primary_gate": ">=10 independent 0.05-degree thinned environment-complete occurrences per taxon",
        "taxa": taxa,
        "tiers": {},
        "claim_boundary": "Multi-source sensitivity only. Any promotion of the GBIF-only primary ecological classification requires a separate explicit decision after topology and LOO robustness are re-evaluated.",
    }

    for tier in ("native", "non_gbif"):
        selected = build_tier(tbn, tier)
        additions = environment_frame(selected, predictors, tier)
        selected.to_csv(args.out_dir / f"tbn_{tier}_selected_cells.csv", index=False)
        additions.to_csv(args.out_dir / f"tbn_{tier}_additions_environment_complete.csv", index=False)
        coverage = count_taxa(gbif, additions, taxa)
        pd.DataFrame(coverage).to_csv(args.out_dir / f"tbn_{tier}_union_coverage.csv", index=False)
        payload["tiers"][tier] = {
            "selected_new_cells": int(len(selected)),
            "environment_complete_additions": int(len(additions)),
            "coverage": coverage,
        }

    (args.out_dir / "fdt4_taiwan_multisource_sensitivity_manifest_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
