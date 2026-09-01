#!/usr/bin/env python3
"""Build the EAzami-first 7-trait x 9-environment exploratory atlas.

Inputs
------
1. The frozen source-name-guarded, 0.1-degree-thinned Japan occurrence cohort
   from the historical FDT4 artifact. BIO1/BIO4/BIO12/BIO15 are already attached.
2. The frozen nine-environment source contract. Five additional CHELSA v2.1
   BIOCLIM+ layers are sampled at the exact same occurrence coordinates.
3. The existing nine-taxon continuous-trait snapshot.

The analysis does NOT select predictors from Azami outcomes. Azami only supplies
an intentionally common measurement universe for later concordance analysis.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]

TRAIT_COLUMNS = [
    "orientation_angle_degrees_median_taxon_median",
    "corolla_lab_lightness_median_taxon_median",
    "corolla_lab_chroma_median_taxon_median",
    "shape_aspect_ratio_median_taxon_median",
    "shape_circularity_median_taxon_median",
    "shape_solidity_median_taxon_median",
    "shape_width_cv_median_taxon_median",
]
EXISTING_ENV = {
    "BIO1": "chelsa_bio01",
    "BIO4": "chelsa_bio04",
    "BIO12": "chelsa_bio12",
    "BIO15": "chelsa_bio15",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--occurrences", type=Path, required=True)
    p.add_argument("--trait-snapshot", type=Path, required=True)
    p.add_argument("--environment-contract", type=Path, required=True)
    p.add_argument("--minimum-environment-records", type=int, default=10)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-taxon-medians", type=Path, required=True)
    return p.parse_args()


def normalize_name(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def source_name_matches_query(source_name: object, query_name: object) -> bool:
    source = normalize_name(source_name).casefold()
    query = normalize_name(query_name).casefold()
    return bool(source and query and (source == query or source.startswith(query + " ")))


def normalized_rank(values: np.ndarray) -> np.ndarray:
    ranks = rankdata(values, method="average")
    centered = ranks - ranks.mean()
    norm = float(np.sqrt(np.sum(centered * centered)))
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("No finite rank variation")
    return centered / norm


def bh_adjust(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    n = len(p)
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.minimum(adjusted, 1.0)
    out = np.empty(n, dtype=float)
    out[order] = adjusted
    return out.tolist()


def sample_remote_raster(frame: pd.DataFrame, url: str) -> tuple[np.ndarray, dict]:
    coords = list(zip(frame["longitude"].astype(float), frame["latitude"].astype(float)))
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff",
        GDAL_HTTP_MULTIRANGE="YES",
        GDAL_HTTP_TIMEOUT="120",
        GDAL_HTTP_MAX_RETRY="4",
        GDAL_HTTP_RETRY_DELAY="3",
    ):
        with rasterio.open(f"/vsicurl/{url}") as src:
            raw = np.array([float(v[0]) for v in src.sample(coords, indexes=1, masked=False)], dtype=float)
            nodata = src.nodata
            if nodata is not None:
                raw[np.isclose(raw, float(nodata))] = np.nan
            # Preserve the pinned sampler convention: apply raster scale/offset when supplied.
            scale = float(src.scales[0]) if src.scales else 1.0
            offset = float(src.offsets[0]) if src.offsets else 0.0
            values = raw * scale + offset
            meta = {
                "url": url,
                "crs": str(src.crs),
                "scale": scale,
                "offset": offset,
                "nodata": None if nodata is None else float(nodata),
                "width": int(src.width),
                "height": int(src.height),
            }
    return values, meta


def clean_trait(name: str) -> str:
    return name.removesuffix("_median_taxon_median")


def main() -> int:
    args = parse_args()
    contract = json.loads(args.environment_contract.read_text(encoding="utf-8"))
    occurrence = pd.read_csv(args.occurrences)
    traits = pd.read_csv(args.trait_snapshot)

    required_occ = {
        "scientific_name_query", "scientificName", "latitude", "longitude",
        *EXISTING_ENV.values(),
    }
    missing = sorted(required_occ.difference(occurrence.columns))
    if missing:
        raise ValueError(f"Occurrence asset missing columns: {missing}")
    required_traits = {"taxon_name", *TRAIT_COLUMNS}
    missing_traits = sorted(required_traits.difference(traits.columns))
    if missing_traits:
        raise ValueError(f"Trait snapshot missing columns: {missing_traits}")

    occurrence["latitude"] = pd.to_numeric(occurrence["latitude"], errors="coerce")
    occurrence["longitude"] = pd.to_numeric(occurrence["longitude"], errors="coerce")
    coordinate_ok = occurrence["latitude"].notna() & occurrence["longitude"].notna()
    source_ok = occurrence.apply(
        lambda r: source_name_matches_query(r.get("scientificName"), r.get("scientific_name_query")),
        axis=1,
    )
    occurrence = occurrence.loc[coordinate_ok & source_ok].copy().reset_index(drop=True)
    if occurrence.empty:
        raise RuntimeError("No source-name-matched coordinate records remain")

    predictor_contract = {row["id"]: row for row in contract["predictors"]}
    raster_meta: dict[str, dict] = {}
    for pid, col in EXISTING_ENV.items():
        occurrence[col] = pd.to_numeric(occurrence[col], errors="coerce")
    for pid in ["RSDS", "VPD", "SFCWIND", "GSP", "NPP"]:
        row = predictor_contract[pid]
        values, meta = sample_remote_raster(occurrence, row["url"])
        occurrence[row["column"]] = values
        raster_meta[pid] = meta

    env_columns = {row["id"]: row["column"] for row in contract["predictors"]}
    for col in env_columns.values():
        occurrence[col] = pd.to_numeric(occurrence[col], errors="coerce")

    occurrence["common9_complete"] = occurrence[list(env_columns.values())].notna().all(axis=1)
    complete = occurrence.loc[occurrence["common9_complete"]].copy()

    count_series = complete.groupby("scientific_name_query").size().sort_index()
    eligible_taxa = count_series.loc[count_series >= args.minimum_environment_records].index.tolist()
    complete = complete.loc[complete["scientific_name_query"].isin(eligible_taxa)].copy()

    agg = {col: "median" for col in env_columns.values()}
    medians = complete.groupby("scientific_name_query", as_index=False).agg(agg)
    medians["n_common9_environment_records"] = medians["scientific_name_query"].map(count_series).astype(int)
    medians = medians.rename(columns={"scientific_name_query": "taxon_name"})

    joined = traits[["taxon_name", *TRAIT_COLUMNS]].merge(medians, on="taxon_name", how="inner")
    joined = joined.dropna(subset=[*TRAIT_COLUMNS, *env_columns.values()]).copy()
    joined = joined.sort_values("taxon_name").reset_index(drop=True)
    n_taxa = len(joined)
    if n_taxa < 5:
        raise RuntimeError(f"Too few taxa for common-nine atlas: {n_taxa}")
    if n_taxa > 9:
        raise RuntimeError("Exact permutation implementation is capped at 9 taxa")

    permutation_index = np.asarray(list(itertools.permutations(range(n_taxa))), dtype=np.int32)
    rows: list[dict] = []
    for trait_col in TRAIT_COLUMNS:
        x = joined[trait_col].to_numpy(dtype=float)
        x_rank = normalized_rank(x)
        for pid, env_col in env_columns.items():
            y = joined[env_col].to_numpy(dtype=float)
            y_rank = normalized_rank(y)
            rho = float(x_rank @ y_rank)
            perm_rho = y_rank[permutation_index] @ x_rank
            p = float(np.mean(np.abs(perm_rho) >= abs(rho) - 1e-12))
            loo = []
            for j in range(n_taxa):
                keep = np.ones(n_taxa, dtype=bool)
                keep[j] = False
                loo.append(float(spearmanr(x[keep], y[keep]).statistic))
            all_pos = all(v > 0 for v in loo)
            all_neg = all(v < 0 for v in loo)
            rows.append({
                "trait": clean_trait(trait_col),
                "environment": pid,
                "environment_block": predictor_contract[pid]["block"],
                "n_taxa": n_taxa,
                "spearman_rho": rho,
                "exact_two_sided_p": p,
                "loo_rho_min": float(min(loo)),
                "loo_rho_max": float(max(loo)),
                "loo_sign_stable": bool(all_pos or all_neg),
                "loo_direction": "positive" if all_pos else "negative" if all_neg else "mixed",
            })

    qvals = bh_adjust([r["exact_two_sided_p"] for r in rows])
    for row, q in zip(rows, qvals):
        row["bh_q_63"] = float(q)
        row["status"] = (
            "bh_supported" if q < 0.05 else
            "raw_exploratory_lead" if row["exact_two_sided_p"] <= 0.05 else
            "not_bh_supported"
        )

    strongest = sorted(rows, key=lambda r: (r["exact_two_sided_p"], -abs(r["spearman_rho"])))[:10]
    summary = {
        "bh_supported_rows": sum(r["status"] == "bh_supported" for r in rows),
        "raw_p_le_0_05_rows": sum(r["exact_two_sided_p"] <= 0.05 for r in rows),
        "stable_sign_rows": sum(r["loo_sign_stable"] for r in rows),
        "top10_raw_rows": strongest,
    }

    result = {
        "contract_version": "chapter2_exploratory_trait_environment_atlas_common9_v1",
        "status_date": "2026-09-01",
        "scope": "EAzami-first retrospective exploratory current atlas; seven frozen continuous traits x nine frozen common environmental predictors; Azami outcomes not used for selection",
        "source_occurrence_artifact": {
            "run_id": 32716015605,
            "artifact_id": 9516784077,
            "table": args.occurrences.name,
            "n_rows_read": int(len(pd.read_csv(args.occurrences, usecols=["scientific_name_query"]))),
            "n_rows_after_source_and_coordinate_recheck": int(len(occurrence)),
            "n_rows_common9_complete": int(len(complete)),
        },
        "minimum_environment_records_per_taxon": args.minimum_environment_records,
        "taxon_counts_before_gate": {str(k): int(v) for k, v in count_series.items()},
        "included_taxa": joined["taxon_name"].tolist(),
        "n_taxa": n_taxa,
        "trait_axes": [clean_trait(x) for x in TRAIT_COLUMNS],
        "environment_axes": list(env_columns.keys()),
        "environment_blocks": {pid: predictor_contract[pid]["block"] for pid in env_columns},
        "n_tests": len(rows),
        "exact_permutations_per_row": math.factorial(n_taxa),
        "multiplicity": f"Benjamini-Hochberg across all {len(rows)} successful continuous endpoint x environment rows",
        "raster_metadata_extension": raster_meta,
        "rows": rows,
        "summary": summary,
        "claim_boundary": [
            "This is an exploratory small-taxon atlas and all rows remain visible regardless of support.",
            "The shared nine-variable environment universe is a measurement alignment with Azami, not an Azami-derived hypothesis set.",
            "Species-level trait and environment medians do not estimate within-population plasticity or selection.",
            "Univariate current environment associations do not identify independent causal drivers or historical origin.",
            "Cross-chapter concordance is evaluated only after this EAzami atlas is frozen."
        ]
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_taxon_medians.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(args.out_csv, index=False)
    joined.to_csv(args.out_taxon_medians, index=False)
    print(json.dumps({
        "n_taxa": n_taxa,
        "included_taxa": result["included_taxa"],
        "n_tests": len(rows),
        "exact_permutations_per_row": math.factorial(n_taxa),
        **summary,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
