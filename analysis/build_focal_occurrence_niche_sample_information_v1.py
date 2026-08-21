#!/usr/bin/env python3
"""Build focal full-occurrence niche summaries and niche-only sampling information scores.

Primary purpose:
- download public GBIF occurrences for declared focal Japanese Cirsium taxa;
- apply explicit coordinate-quality and spatial-thinning rules;
- extract the same four CHELSA v2.1 predictors used by Azami;
- summarize taxon niche geometry in pooled environmental PCA space;
- rank public occurrence strata for niche/geographic information gain;
- use existing region-level anchors only to position already-existing P003/P004 slots.

This script does NOT infer adaptation, ancestry, ancestral states, or exact collection sites.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
import rasterio
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

GBIF_API = "https://api.gbif.org/v1"
BAD_GEOSPATIAL_ISSUES = {
    "ZERO_COORDINATE",
    "COUNTRY_COORDINATE_MISMATCH",
    "COORDINATE_INVALID",
    "GEODETIC_DATUM_INVALID",
}
OCCURRENCE_COLUMNS = [
    "scientific_name_query",
    "gbif_match_key",
    "gbif_match_scientific_name",
    "gbif_key",
    "acceptedScientificName",
    "scientificName",
    "basisOfRecord",
    "year",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "stateProvince",
    "locality",
    "island",
    "datasetKey",
    "issues",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--request-timeout", type=float, default=60.0)
    p.add_argument("--request-sleep", type=float, default=0.05)
    return p.parse_args()


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def robust_unit(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce").astype(float)
    finite = x[np.isfinite(x)]
    if finite.empty:
        return pd.Series(np.zeros(len(x)), index=x.index, dtype=float)
    lo, hi = float(finite.min()), float(finite.quantile(0.95))
    if not math.isfinite(hi) or hi <= lo + 1e-12:
        hi = float(finite.max())
    if not math.isfinite(hi) or hi <= lo + 1e-12:
        return pd.Series(np.zeros(len(x)), index=x.index, dtype=float)
    return ((x - lo) / (hi - lo)).clip(0.0, 1.0).fillna(0.0)


def gbif_match(session: requests.Session, name: str, timeout: float) -> dict[str, Any]:
    r = session.get(f"{GBIF_API}/species/match", params={"name": name}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    key = data.get("usageKey") or data.get("speciesKey")
    if not key:
        raise RuntimeError(f"GBIF species match returned no key for {name}: {data}")
    return {
        "query_name": name,
        "usage_key": int(key),
        "matched_name": data.get("scientificName") or data.get("canonicalName") or "",
        "status": data.get("status", ""),
        "confidence": data.get("confidence"),
        "match_type": data.get("matchType", ""),
    }


def fetch_occurrences(
    session: requests.Session,
    *,
    name: str,
    taxon_key: int,
    country: str,
    page_size: int,
    max_records: int,
    timeout: float,
    sleep_s: float,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    total = None
    while offset < max_records:
        limit = min(page_size, max_records - offset)
        params = {
            "taxon_key": taxon_key,
            "country": country,
            "has_coordinate": "true",
            "occurrence_status": "PRESENT",
            "limit": limit,
            "offset": offset,
        }
        r = session.get(f"{GBIF_API}/occurrence/search", params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        total = int(data.get("count", 0))
        results = data.get("results", [])
        if not results:
            break
        for item in results:
            rows.append(
                {
                    "scientific_name_query": name,
                    "gbif_match_key": taxon_key,
                    "gbif_match_scientific_name": "",
                    "gbif_key": item.get("key"),
                    "acceptedScientificName": item.get("acceptedScientificName", ""),
                    "scientificName": item.get("scientificName", ""),
                    "basisOfRecord": item.get("basisOfRecord", ""),
                    "year": item.get("year"),
                    "decimalLatitude": item.get("decimalLatitude"),
                    "decimalLongitude": item.get("decimalLongitude"),
                    "coordinateUncertaintyInMeters": item.get("coordinateUncertaintyInMeters"),
                    "stateProvince": item.get("stateProvince", ""),
                    "locality": item.get("locality", ""),
                    "island": item.get("island", ""),
                    "datasetKey": item.get("datasetKey", ""),
                    "issues": "|".join(item.get("issues", []) or []),
                }
            )
        offset += len(results)
        if offset >= total or len(results) < limit:
            break
        if sleep_s > 0:
            time.sleep(sleep_s)
    frame = pd.DataFrame(rows, columns=OCCURRENCE_COLUMNS)
    meta = {
        "gbif_count": int(total or 0),
        "records_downloaded": int(len(frame)),
        "truncated_at_max_records": bool(total is not None and total > len(frame) and len(frame) >= max_records),
    }
    return frame, meta


def clean_and_thin(raw: pd.DataFrame, cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    if raw.empty:
        return raw.copy(), {
            "n_downloaded": 0,
            "n_valid_geography": 0,
            "n_strict_coordinate": 0,
            "n_primary_thinned": 0,
            "primary_quality_mode": "insufficient",
        }
    x = raw.copy()
    x["latitude"] = pd.to_numeric(x["decimalLatitude"], errors="coerce")
    x["longitude"] = pd.to_numeric(x["decimalLongitude"], errors="coerce")
    x["coordinate_uncertainty_m"] = pd.to_numeric(x["coordinateUncertaintyInMeters"], errors="coerce")
    b = cfg["japan_bounds"]
    geo = (
        x["latitude"].between(float(b["lat_min"]), float(b["lat_max"]))
        & x["longitude"].between(float(b["lon_min"]), float(b["lon_max"]))
    )
    bad = x["issues"].fillna("").map(
        lambda s: bool(BAD_GEOSPATIAL_ISSUES.intersection(set(s.split("|"))))
    )
    x = x.loc[geo & ~bad].copy()
    max_unc = float(cfg["max_coordinate_uncertainty_m_primary"])
    x["strict_coordinate_quality"] = x["coordinate_uncertainty_m"].notna() & (
        x["coordinate_uncertainty_m"] <= max_unc
    )
    strict_n = int(x["strict_coordinate_quality"].sum())
    if strict_n >= 10:
        primary = x.loc[x["strict_coordinate_quality"]].copy()
        mode = "strict_le_10km"
    else:
        primary = x.copy()
        mode = "inclusive_missing_uncertainty_fallback"
    thin = float(cfg["spatial_thin_degrees"])
    primary["thin_lat"] = np.floor(primary["latitude"] / thin).astype(int)
    primary["thin_lon"] = np.floor(primary["longitude"] / thin).astype(int)
    primary["uncertainty_sort"] = primary["coordinate_uncertainty_m"].fillna(1e12)
    primary["year_sort"] = pd.to_numeric(primary["year"], errors="coerce").fillna(-1)
    primary = primary.sort_values(
        ["scientific_name_query", "thin_lat", "thin_lon", "uncertainty_sort", "year_sort"],
        ascending=[True, True, True, True, False],
    )
    primary = primary.drop_duplicates(["scientific_name_query", "thin_lat", "thin_lon"], keep="first")
    primary = primary.drop(columns=["uncertainty_sort"])
    meta = {
        "n_downloaded": int(len(raw)),
        "n_valid_geography": int(len(x)),
        "n_strict_coordinate": strict_n,
        "n_primary_thinned": int(len(primary)),
        "primary_quality_mode": mode,
    }
    return primary.reset_index(drop=True), meta


def sample_chelsa(frame: pd.DataFrame, predictors: dict[str, str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    out = frame.copy()
    coords = list(zip(out["longitude"].astype(float), out["latitude"].astype(float)))
    metadata: dict[str, Any] = {}
    for pid, url in predictors.items():
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
                scale = float(src.scales[0]) if src.scales else 1.0
                offset = float(src.offsets[0]) if src.offsets else 0.0
                out[f"chelsa_{pid}"] = raw * scale + offset
                metadata[pid] = {
                    "url": url,
                    "crs": str(src.crs),
                    "scale": scale,
                    "offset": offset,
                    "nodata": nodata,
                }
    return out, metadata


def choose_k(features: np.ndarray, planned: int) -> tuple[int, dict[str, float]]:
    n = len(features)
    if n < 4:
        return 1, {}
    max_k = min(6, n - 1)
    scores: dict[str, float] = {}
    best_k, best_score = 2, -1.0
    for k in range(2, max_k + 1):
        labels = KMeans(n_clusters=k, random_state=20260821, n_init=20).fit_predict(features)
        if len(set(labels)) < 2:
            continue
        s = float(silhouette_score(features, labels))
        scores[str(k)] = s
        if s > best_score:
            best_k, best_score = k, s
    if not scores:
        return min(max(planned, 1), n), {}
    return best_k, scores


def anchor_frame(config: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for taxon in config["taxa"]:
        for a in taxon.get("analysis_region_anchors", []):
            rows.append(
                {
                    "scientific_name_query": taxon["scientific_name"],
                    "anchor_name": a["name"],
                    "anchor_type": a["anchor_type"],
                    "latitude": float(a["latitude"]),
                    "longitude": float(a["longitude"]),
                }
            )
    return pd.DataFrame(rows)


def line_bridge_relevance(lat: float, lon: float, anchors: pd.DataFrame) -> float:
    if len(anchors) != 2:
        return 0.0
    a = anchors.iloc[0]
    b = anchors.iloc[1]
    ax, ay = float(a["longitude"]), float(a["latitude"])
    bx, by = float(b["longitude"]), float(b["latitude"])
    px, py = lon, lat
    dx, dy = bx - ax, by - ay
    denom = dx * dx + dy * dy
    if denom <= 1e-12:
        return 0.0
    t = ((px - ax) * dx + (py - ay) * dy) / denom
    if t <= 0 or t >= 1:
        return 0.0
    return float(4 * t * (1 - t))


def select_distinct_candidates(frame: pd.DataFrame, n: int, min_distance_km: float = 50.0) -> pd.DataFrame:
    chosen = []
    used_clusters: set[int] = set()
    for _, row in frame.sort_values("niche_information_score", ascending=False).iterrows():
        cluster = int(row["cluster_id"])
        if cluster in used_clusters:
            continue
        if any(
            haversine_km(
                float(row["latitude"]), float(row["longitude"]),
                float(old["latitude"]), float(old["longitude"])
            ) < min_distance_km
            for old in chosen
        ):
            continue
        chosen.append(row)
        used_clusters.add(cluster)
        if len(chosen) >= n:
            break
    if not chosen:
        return frame.head(0).copy()
    return pd.DataFrame(chosen)


def main() -> None:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "EAzami/1.0 public-niche-sampling-audit"})

    all_primary = []
    taxon_meta: dict[str, Any] = {}
    match_rows = []
    for taxon in config["taxa"]:
        name = taxon["scientific_name"]
        match = gbif_match(session, name, args.request_timeout)
        match_rows.append(match)
        raw, gbif_meta = fetch_occurrences(
            session,
            name=name,
            taxon_key=match["usage_key"],
            country=config["gbif"]["country"],
            page_size=int(config["gbif"]["page_size"]),
            max_records=int(config["gbif"]["max_records_per_taxon"]),
            timeout=args.request_timeout,
            sleep_s=args.request_sleep,
        )
        raw["gbif_match_scientific_name"] = match["matched_name"]
        primary, clean_meta = clean_and_thin(raw, config["gbif"])
        if not primary.empty:
            all_primary.append(primary)
        taxon_meta[name] = {**gbif_meta, **clean_meta, "gbif_match": match}

    if not all_primary:
        raise SystemExit("No focal occurrence records survived cleaning.")
    occ = pd.concat(all_primary, ignore_index=True)
    occ, raster_meta = sample_chelsa(occ, config["chelsa"]["predictors"])
    env_cols = [f"chelsa_{k}" for k in config["chelsa"]["predictors"]]
    occ["environment_complete"] = occ[env_cols].notna().all(axis=1)
    occ = occ.loc[occ["environment_complete"]].copy()
    if len(occ) < 10:
        raise SystemExit("Too few environment-complete occurrences for pooled niche PCA.")

    scaler = StandardScaler().fit(occ[env_cols])
    env_z = scaler.transform(occ[env_cols])
    pca = PCA(n_components=min(3, len(env_cols), len(occ))).fit(env_z)
    pcs = pca.transform(env_z)
    for i in range(pcs.shape[1]):
        occ[f"PC{i+1}"] = pcs[:, i]

    anchors = anchor_frame(config)
    if not anchors.empty:
        anchors, _ = sample_chelsa(anchors, config["chelsa"]["predictors"])
        anchor_env_z = scaler.transform(anchors[env_cols])
        anchor_pcs = pca.transform(anchor_env_z)
        for i in range(anchor_pcs.shape[1]):
            anchors[f"PC{i+1}"] = anchor_pcs[:, i]

    summary_rows = []
    candidate_rows = []
    slot_rows = []
    config_by_taxon = {t["scientific_name"]: t for t in config["taxa"]}
    pc_cols = [f"PC{i+1}" for i in range(pcs.shape[1])]

    for name, group0 in occ.groupby("scientific_name_query", sort=True):
        group = group0.copy().reset_index(drop=True)
        taxcfg = config_by_taxon[name]
        planned = int(taxcfg["planned_populations"])
        n = len(group)
        env_feature = group[pc_cols].to_numpy(float)
        geo_scaler = StandardScaler().fit(group[["latitude", "longitude"]])
        geo_feature = geo_scaler.transform(group[["latitude", "longitude"]])
        joint = np.hstack([env_feature, 0.65 * geo_feature])

        if n >= 4:
            best_k, sil = choose_k(joint, planned)
            labels = KMeans(n_clusters=best_k, random_state=20260821, n_init=30).fit_predict(joint)
        else:
            best_k, sil = 1, {}
            labels = np.zeros(n, dtype=int)
        group["cluster_id"] = labels

        env_centroid = env_feature.mean(axis=0)
        group["niche_edge_raw"] = np.linalg.norm(env_feature - env_centroid, axis=1)
        latc, lonc = float(group["latitude"].mean()), float(group["longitude"].mean())
        group["geographic_edge_raw"] = [
            haversine_km(latc, lonc, float(r.latitude), float(r.longitude))
            for r in group.itertuples()
        ]
        cluster_sizes = group.groupby("cluster_id").size().to_dict()
        group["cluster_rarity_raw"] = group["cluster_id"].map(
            lambda c: 1.0 / math.sqrt(cluster_sizes[int(c)])
        )
        group["niche_edge"] = robust_unit(group["niche_edge_raw"])
        group["geographic_edge"] = robust_unit(group["geographic_edge_raw"])
        group["cluster_rarity"] = robust_unit(group["cluster_rarity_raw"])

        tax_anchors = anchors.loc[anchors["scientific_name_query"].eq(name)].copy() if not anchors.empty else anchors.head(0)
        if not tax_anchors.empty:
            anchor_geo = geo_scaler.transform(tax_anchors[["latitude", "longitude"]])
            anchor_joint = np.hstack([tax_anchors[pc_cols].to_numpy(float), 0.65 * anchor_geo])
            d = np.sqrt(((joint[:, None, :] - anchor_joint[None, :, :]) ** 2).sum(axis=2))
            group["coverage_gain_raw"] = d.min(axis=1)
            group["nearest_anchor"] = [tax_anchors.iloc[i]["anchor_name"] for i in d.argmin(axis=1)]
            group["distance_to_nearest_anchor_km"] = [
                min(
                    haversine_km(
                        float(r.latitude), float(r.longitude),
                        float(a.latitude), float(a.longitude)
                    )
                    for a in tax_anchors.itertuples()
                )
                for r in group.itertuples()
            ]
            group["bridge_relevance"] = [
                line_bridge_relevance(float(r.latitude), float(r.longitude), tax_anchors)
                for r in group.itertuples()
            ]
            group["coverage_gain"] = robust_unit(group["coverage_gain_raw"])
            group["niche_information_score"] = (
                0.45 * group["coverage_gain"]
                + 0.25 * group["niche_edge"]
                + 0.15 * group["cluster_rarity"]
                + 0.15 * group["bridge_relevance"]
            )
        else:
            group["coverage_gain_raw"] = np.nan
            group["coverage_gain"] = np.nan
            group["nearest_anchor"] = ""
            group["distance_to_nearest_anchor_km"] = np.nan
            group["bridge_relevance"] = 0.0
            group["niche_information_score"] = (
                0.55 * group["niche_edge"]
                + 0.25 * group["geographic_edge"]
                + 0.20 * group["cluster_rarity"]
            )

        group["morph_linkage_required"] = bool(taxcfg["morph_linkage_required"])
        group["slot_assignment"] = taxcfg["slot_assignment"]
        group["role"] = taxcfg["role"]
        group["candidate_rank"] = group["niche_information_score"].rank(
            method="first", ascending=False
        ).astype(int)
        candidate_rows.append(group.sort_values("candidate_rank").head(25))

        cluster_gap = max(0, best_k - planned) if planned > 0 else None
        summary_rows.append(
            {
                "taxon": name,
                "role": taxcfg["role"],
                "planned_populations": planned,
                "gbif_match_name": taxon_meta[name]["gbif_match"]["matched_name"],
                "gbif_count": taxon_meta[name]["gbif_count"],
                "records_downloaded": taxon_meta[name]["records_downloaded"],
                "valid_geography": taxon_meta[name]["n_valid_geography"],
                "strict_coordinate_records": taxon_meta[name]["n_strict_coordinate"],
                "primary_thinned_environment_complete": n,
                "primary_quality_mode": taxon_meta[name]["primary_quality_mode"],
                "silhouette_best_k": best_k,
                "silhouette_scores": json.dumps(sil, sort_keys=True),
                "planned_vs_niche_cluster_gap": cluster_gap,
                "morph_linkage_required": bool(taxcfg["morph_linkage_required"]),
                "sampling_decision_boundary": (
                    "niche_only_no_new_count"
                    if taxcfg["slot_assignment"] != "P003_P004_intermediate_only"
                    else "position_existing_P003_P004_only"
                ),
            }
        )

        if taxcfg["slot_assignment"] == "P003_P004_intermediate_only":
            eligible = group.loc[group["distance_to_nearest_anchor_km"].fillna(0) >= 45].copy()
            chosen = select_distinct_candidates(eligible, n=2, min_distance_km=50)
            for slot, (_, r) in zip(["P003", "P004"], chosen.iterrows()):
                slot_rows.append(
                    {
                        "population_slot": slot,
                        "taxon": name,
                        "gbif_key_reference": r["gbif_key"],
                        "public_occurrence_latitude": round(float(r["latitude"]), 5),
                        "public_occurrence_longitude": round(float(r["longitude"]), 5),
                        "stateProvince": safe_text(r["stateProvince"]),
                        "island": safe_text(r["island"]),
                        "locality": safe_text(r["locality"]),
                        "cluster_id": int(r["cluster_id"]),
                        "niche_information_score": round(float(r["niche_information_score"]), 6),
                        "coverage_gain": round(float(r["coverage_gain"]), 6),
                        "niche_edge": round(float(r["niche_edge"]), 6),
                        "bridge_relevance": round(float(r["bridge_relevance"]), 6),
                        "decision": "candidate_stratum_for_field_verification_not_collection_coordinate",
                    }
                )

    summary = pd.DataFrame(summary_rows)
    candidates = pd.concat(candidate_rows, ignore_index=True) if candidate_rows else pd.DataFrame()
    slots = pd.DataFrame(slot_rows)

    output_occ_cols = [
        "scientific_name_query", "gbif_key", "acceptedScientificName", "scientificName",
        "basisOfRecord", "year", "latitude", "longitude", "coordinate_uncertainty_m",
        "stateProvince", "locality", "island", "issues", *env_cols, *pc_cols,
        "cluster_id", "niche_edge", "geographic_edge", "cluster_rarity",
        "coverage_gain", "nearest_anchor", "distance_to_nearest_anchor_km",
        "bridge_relevance", "niche_information_score", "candidate_rank",
        "morph_linkage_required", "slot_assignment", "role",
    ]
    occ.to_csv(out_dir / "focal_occurrences_environment_complete.csv", index=False)
    candidates[output_occ_cols].to_csv(out_dir / "focal_niche_sampling_candidates.csv", index=False)
    summary.to_csv(out_dir / "focal_niche_sampling_summary.csv", index=False)
    slots.to_csv(out_dir / "p003_p004_niche_stratum_candidates.csv", index=False)
    anchors.to_csv(out_dir / "analysis_region_anchors_with_environment.csv", index=False)
    pd.DataFrame(match_rows).to_csv(out_dir / "gbif_taxon_matches.csv", index=False)

    result = {
        "contract_version": "focal_occurrence_niche_sample_information_v1",
        "status_date": config["status_date"],
        "gbif_query_scope": config["gbif"],
        "chelsa": {
            "version": config["chelsa"]["version"],
            "baseline": config["chelsa"]["baseline"],
            "raster_metadata": raster_meta,
        },
        "pooled_environment_pca_variance_explained": [float(x) for x in pca.explained_variance_ratio_],
        "taxon_summary": summary.to_dict(orient="records"),
        "p003_p004_candidates": slots.to_dict(orient="records"),
        "scoring_components_computed": config["scoring"]["candidate_components"],
        "scoring_components_pending": config["scoring"]["not_computed_here"],
        "decision_rule": config["scoring"]["rule"],
        "claim_boundary": config["claim_boundary"],
    }
    (out_dir / "focal_occurrence_niche_sample_information_v1.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
