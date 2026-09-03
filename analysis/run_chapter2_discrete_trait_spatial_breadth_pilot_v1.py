#!/usr/bin/env python3
"""EAzami Chapter 2 spatial-breadth pilot for the three discrete history traits.

This analysis is deliberately environment-free. It joins the authority-backed
Japan38 state ontology to source-name-guarded public GBIF geography, estimates
robust taxon centroids after spatial thinning, and asks how broadly each state is
dispersed in current geographic space.

The output is an internal diagnostic for the SPACE axis. It does not infer
adaptation, historical range, or causal environment.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

GBIF_API = "https://api.gbif.org/v1"
BAD_ISSUES = {
    "ZERO_COORDINATE",
    "COUNTRY_COORDINATE_MISMATCH",
    "COORDINATE_INVALID",
    "GEODETIC_DATUM_INVALID",
}
STATE_UNIVERSE = {
    "orientation": {"U", "D"},
    "phyllary": {"appressed", "ascending", "spreading", "recurved"},
    "stickiness": {"sticky", "nonsticky"},
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=Path, required=True)
    p.add_argument("--extension", type=Path, required=True)
    p.add_argument("--min-thinned-occurrences", type=int, default=3)
    p.add_argument("--thin-degrees", type=float, default=0.1)
    p.add_argument("--max-records-per-taxon", type=int, default=3000)
    p.add_argument("--permutations", type=int, default=9999)
    p.add_argument("--seed-rng", type=int, default=20260901)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-taxa", type=Path, required=True)
    p.add_argument("--out-traits", type=Path, required=True)
    return p.parse_args()


def norm_name(v: object) -> str:
    return " ".join(str(v or "").strip().split())


def source_matches(source: object, query: object) -> bool:
    s = norm_name(source).casefold()
    q = norm_name(query).casefold()
    return bool(s and q and (s == q or s.startswith(q + " ")))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def trait_state(row: dict[str, Any], trait: str) -> set[str]:
    if trait == "orientation":
        x = str(row.get("orientation_state") or "").strip()
        if x in {"upward_or_erect", "upward_or_ascending"}:
            return {"U"}
        if x == "downward_or_nodding":
            return {"D"}
    elif trait == "phyllary":
        x = str(row.get("phyllary_posture") or "").strip()
        mapping = {
            "appressed": {"appressed"},
            "ascending": {"ascending"},
            "spreading": {"spreading"},
            "appressed_or_ascending": {"appressed", "ascending"},
            "ascending_or_recurved": {"ascending", "recurved"},
            "spreading_or_recurved": {"spreading", "recurved"},
        }
        if x in mapping:
            return mapping[x]
    elif trait == "stickiness":
        x = str(row.get("stickiness_state") or "").strip()
        if x == "sticky":
            return {"sticky"}
        if x == "nonsticky_or_nearly_nonsticky":
            return {"nonsticky"}
    return set(STATE_UNIVERSE[trait])


def fetch_occurrences(session: requests.Session, query: str, max_records: int) -> tuple[pd.DataFrame, dict]:
    m = session.get(f"{GBIF_API}/species/match", params={"name": query}, timeout=60)
    m.raise_for_status()
    match = m.json()
    key = match.get("usageKey") or match.get("speciesKey")
    if not key:
        return pd.DataFrame(), {"match_status": "no_key", "matched_name": ""}
    rows: list[dict] = []
    offset = 0
    total = 0
    while offset < max_records:
        limit = min(300, max_records - offset)
        r = session.get(
            f"{GBIF_API}/occurrence/search",
            params={
                "taxon_key": int(key),
                "country": "JP",
                "has_coordinate": "true",
                "occurrence_status": "PRESENT",
                "limit": limit,
                "offset": offset,
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        total = int(data.get("count", 0))
        got = data.get("results") or []
        if not got:
            break
        for item in got:
            rows.append({
                "scientificName": item.get("scientificName", ""),
                "lat": item.get("decimalLatitude"),
                "lon": item.get("decimalLongitude"),
                "uncertainty": item.get("coordinateUncertaintyInMeters"),
                "issues": item.get("issues") or [],
                "key": item.get("key"),
            })
        offset += len(got)
        if offset >= total or len(got) < limit:
            break
        time.sleep(0.02)
    return pd.DataFrame(rows), {
        "match_status": str(match.get("status", "")),
        "matched_name": str(match.get("scientificName") or match.get("canonicalName") or ""),
        "gbif_count": total,
        "downloaded": len(rows),
    }


def clean_thin(raw: pd.DataFrame, query: str, thin: float) -> tuple[pd.DataFrame, dict]:
    if raw.empty:
        return raw.copy(), {"source_match": 0, "valid_geo": 0, "quality_mode": "no_records"}
    x = raw.copy()
    x = x.loc[x["scientificName"].map(lambda v: source_matches(v, query))].copy()
    source_n = len(x)
    x["lat"] = pd.to_numeric(x["lat"], errors="coerce")
    x["lon"] = pd.to_numeric(x["lon"], errors="coerce")
    x["uncertainty"] = pd.to_numeric(x["uncertainty"], errors="coerce")
    valid = x["lat"].between(20.0, 46.5) & x["lon"].between(122.0, 154.5)
    bad = x["issues"].map(lambda z: bool(BAD_ISSUES.intersection(set(z if isinstance(z, list) else []))))
    x = x.loc[valid & ~bad].copy()
    valid_n = len(x)
    strict = x["uncertainty"].notna() & (x["uncertainty"] <= 10000)
    if int(strict.sum()) >= 3:
        x = x.loc[strict].copy()
        mode = "strict_known_le_10km"
    else:
        x = x.loc[x["uncertainty"].isna() | (x["uncertainty"] <= 10000)].copy()
        mode = "include_missing_uncertainty_fallback"
    if x.empty:
        return x, {"source_match": source_n, "valid_geo": valid_n, "quality_mode": mode}
    x["thin_lat"] = np.floor(x["lat"] / thin).astype(int)
    x["thin_lon"] = np.floor(x["lon"] / thin).astype(int)
    x["unc_sort"] = x["uncertainty"].fillna(1e12)
    x = x.sort_values(["thin_lat", "thin_lon", "unc_sort", "key"], na_position="last")
    x = x.drop_duplicates(["thin_lat", "thin_lon"], keep="first")
    return x.reset_index(drop=True), {
        "source_match": source_n,
        "valid_geo": valid_n,
        "quality_mode": mode,
    }


def pairwise_distances(frame: pd.DataFrame) -> list[float]:
    vals = []
    rows = list(frame.itertuples())
    for a, b in itertools.combinations(rows, 2):
        vals.append(haversine_km(float(a.centroid_lat), float(a.centroid_lon), float(b.centroid_lat), float(b.centroid_lon)))
    return vals


def spatial_stat(frame: pd.DataFrame, labels: list[str]) -> float | None:
    same, diff = [], []
    rows = list(frame.itertuples())
    for (i, a), (j, b) in itertools.combinations(enumerate(rows), 2):
        d = haversine_km(float(a.centroid_lat), float(a.centroid_lon), float(b.centroid_lat), float(b.centroid_lon))
        (same if labels[i] == labels[j] else diff).append(d)
    if not same or not diff:
        return None
    return float(np.median(diff) - np.median(same))


def main() -> int:
    args = parse_args()
    seed = pd.read_csv(args.seed, dtype=str).fillna("")
    ext = pd.read_csv(args.extension, dtype=str).fillna("")
    combined = pd.concat([seed, ext], ignore_index=True)
    combined = combined.drop_duplicates("paper_japan_member_id", keep="last")

    records = []
    for row in combined.to_dict("records"):
        rec = {
            "paper_japan_member_id": row["paper_japan_member_id"],
            "taxon_name": row["nmns_taxon_concept"],
        }
        any_single = False
        for trait in STATE_UNIVERSE:
            states = trait_state(row, trait)
            rec[f"{trait}_allowed_states"] = "|".join(sorted(states))
            rec[f"{trait}_singleton_state"] = next(iter(states)) if len(states) == 1 else ""
            any_single = any_single or len(states) == 1
        if any_single:
            records.append(rec)
    registry = pd.DataFrame(records)

    session = requests.Session()
    session.headers.update({"User-Agent": "EAzami/space-breadth-pilot public GBIF geography"})
    taxa_rows = []
    for rec in registry.to_dict("records"):
        raw, meta = fetch_occurrences(session, rec["taxon_name"], args.max_records_per_taxon)
        thin, clean = clean_thin(raw, rec["taxon_name"], args.thin_degrees)
        out = dict(rec)
        out.update(meta)
        out.update(clean)
        out["n_thinned"] = int(len(thin))
        if len(thin) >= args.min_thinned_occurrences:
            out["centroid_lat"] = float(thin["lat"].median())
            out["centroid_lon"] = float(thin["lon"].median())
            out["occupied_1deg_cells"] = int(thin.assign(c1=np.floor(thin.lat), c2=np.floor(thin.lon)).drop_duplicates(["c1", "c2"]).shape[0])
        else:
            out["centroid_lat"] = np.nan
            out["centroid_lon"] = np.nan
            out["occupied_1deg_cells"] = 0
        taxa_rows.append(out)
    taxa = pd.DataFrame(taxa_rows)

    rng = random.Random(args.seed_rng)
    trait_rows = []
    for trait in STATE_UNIVERSE:
        state_col = f"{trait}_singleton_state"
        x = taxa.loc[(taxa[state_col] != "") & (taxa["n_thinned"] >= args.min_thinned_occurrences)].copy()
        states = sorted(x[state_col].unique())
        observed_labels = x[state_col].tolist()
        obs = spatial_stat(x, observed_labels)
        perm = []
        if obs is not None and len(states) >= 2:
            for _ in range(args.permutations):
                labels = observed_labels.copy()
                rng.shuffle(labels)
                val = spatial_stat(x, labels)
                if val is not None:
                    perm.append(val)
            p = float((1 + sum(abs(v) >= abs(obs) - 1e-12 for v in perm)) / (1 + len(perm)))
        else:
            p = None
        state_summary = {}
        for state, g in x.groupby(state_col, sort=True):
            ds = pairwise_distances(g)
            state_summary[state] = {
                "n_taxa": int(len(g)),
                "taxa": g["taxon_name"].tolist(),
                "centroid_pairwise_q90_km": None if not ds else float(np.quantile(ds, 0.90)),
                "centroid_pairwise_max_km": None if not ds else float(max(ds)),
                "sum_occupied_1deg_cells": int(g["occupied_1deg_cells"].sum()),
            }
        trait_rows.append({
            "trait": trait,
            "n_singleton_state_taxa_with_spatial_support": int(len(x)),
            "states_present": "|".join(states),
            "spatial_segregation_statistic_km": obs,
            "spatial_segregation_permutation_p": p,
            "statistic_interpretation": "median_between_state_distance_minus_median_within_state_distance; positive means same-state taxon centroids are geographically closer",
            "state_breadth_json": json.dumps(state_summary, ensure_ascii=False, sort_keys=True),
        })
    trait_frame = pd.DataFrame(trait_rows)

    result = {
        "contract_version": "chapter2_discrete_trait_spatial_breadth_pilot_v1",
        "status_date": "2026-09-01",
        "scope": "internal environment-free current geography diagnostic for the same three discrete trait ontologies used by the temporal-depth analysis",
        "taxa_considered": int(len(registry)),
        "taxa_with_any_spatial_support": int((taxa["n_thinned"] >= args.min_thinned_occurrences).sum()),
        "minimum_thinned_occurrences_per_taxon": args.min_thinned_occurrences,
        "spatial_thin_degrees": args.thin_degrees,
        "permutations": args.permutations,
        "traits": trait_rows,
        "claim_boundary": [
            "Authority state is taxon-level and is not measured at each occurrence coordinate.",
            "Current GBIF geography is not historical range.",
            "Spatial segregation is descriptive structure, not adaptation or environmental causation.",
            "Ambiguous multi-state phyllary records are excluded from the singleton-state primary metric rather than forced to one state.",
            "This pilot need not appear in the final manuscript."
        ]
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_taxa.parent.mkdir(parents=True, exist_ok=True)
    args.out_traits.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    taxa.to_csv(args.out_taxa, index=False)
    trait_frame.to_csv(args.out_traits, index=False)
    print(json.dumps({
        "taxa_considered": result["taxa_considered"],
        "taxa_with_any_spatial_support": result["taxa_with_any_spatial_support"],
        "traits": trait_rows,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
