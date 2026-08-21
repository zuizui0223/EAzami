#!/usr/bin/env python3
"""Audit whether named white morphs have public locality records usable in focal niche design.

This is deliberately conservative. A GBIF parent-species match is not enough: the
record-level source scientificName must retain the queried infraspecific/form name.
The resulting coordinates are public evidence strata, never proposed collection sites.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_focal_occurrence_niche_sample_information_v1 as niche  # noqa: E402

RANK_MAP = {"forma": "f.", "form": "f.", "f": "f.", "f.": "f.", "variety": "var.", "var": "var.", "var.": "var."}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--morph-config", type=Path, required=True)
    p.add_argument("--parent-config", type=Path, required=True)
    p.add_argument("--parent-niche-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--request-timeout", type=float, default=60.0)
    return p.parse_args()


def normalize_tokens(value: object) -> list[str]:
    text = " ".join(str(value or "").replace("×", " ").split()).casefold()
    tokens = []
    for token in text.split():
        bare = token.strip("(),;")
        tokens.append(RANK_MAP.get(bare, bare))
    return tokens


def canonical_morph_prefix(value: object) -> str:
    tokens = normalize_tokens(value)
    if len(tokens) < 2:
        return " ".join(tokens)
    for i, token in enumerate(tokens[2:], start=2):
        if token in {"f.", "var."} and i + 1 < len(tokens):
            return " ".join(tokens[: i + 2])
    return " ".join(tokens[:2])


def source_name_matches_query(source_name: object, query_name: object) -> bool:
    source = " ".join(normalize_tokens(source_name))
    prefix = canonical_morph_prefix(query_name)
    return bool(prefix and source and (source == prefix or source.startswith(prefix + " ")))


def clean_exact_form(raw: pd.DataFrame, query: str, cfg: dict) -> tuple[pd.DataFrame, dict]:
    if raw.empty:
        return raw.copy(), {"query": query, "pre_filter": 0, "exact_source_match": 0, "primary_thinned": 0}
    mask = raw["scientificName"].map(lambda x: source_name_matches_query(x, query))
    exact = raw.loc[mask].copy()
    parent_cfg = {
        "japan_bounds": cfg["japan_bounds"],
        "max_coordinate_uncertainty_m_primary": cfg["max_coordinate_uncertainty_m"],
        "spatial_thin_degrees": cfg["spatial_thin_degrees"],
    }
    primary, meta = niche.clean_and_thin(exact, parent_cfg)
    return primary, {
        "query": query,
        "pre_filter": int(len(raw)),
        "exact_source_match": int(mask.sum()),
        "source_name_excluded": int((~mask).sum()),
        "primary_thinned": int(len(primary)),
        "gbif_clean_meta": meta,
    }


def fit_parent_projection(parent_occ: pd.DataFrame, parent_summary: pd.DataFrame, env_cols: list[str]):
    scaler = StandardScaler().fit(parent_occ[env_cols])
    pca = PCA(n_components=min(3, len(env_cols), len(parent_occ))).fit(scaler.transform(parent_occ[env_cols]))
    parent_pc = pca.transform(scaler.transform(parent_occ[env_cols]))
    models = {}
    for taxon, group0 in parent_occ.groupby("scientific_name_query"):
        group = group0.copy()
        idx = group.index.to_numpy()
        pc = parent_pc[idx]
        geo_scaler = StandardScaler().fit(group[["latitude", "longitude"]])
        geo = geo_scaler.transform(group[["latitude", "longitude"]])
        joint = np.hstack([pc, 0.65 * geo])
        row = parent_summary.loc[parent_summary["taxon"].eq(taxon)]
        k = int(row.iloc[0]["silhouette_best_k"]) if len(row) else 1
        k = max(1, min(k, len(group)))
        km = KMeans(n_clusters=k, random_state=20260821, n_init=30).fit(joint)
        models[taxon] = {"scaler": scaler, "pca": pca, "geo_scaler": geo_scaler, "kmeans": km, "k": k}
    return models


def main() -> None:
    args = parse_args()
    morph_cfg = json.loads(args.morph_config.read_text(encoding="utf-8"))
    parent_cfg = json.loads(args.parent_config.read_text(encoding="utf-8"))
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    parent_occ = pd.read_csv(args.parent_niche_dir / "focal_occurrences_environment_complete.csv")
    parent_summary = pd.read_csv(args.parent_niche_dir / "focal_niche_sampling_summary.csv")
    env_cols = [f"chelsa_{key}" for key in parent_cfg["chelsa"]["predictors"]]
    if not set(env_cols).issubset(parent_occ.columns):
        raise ValueError("Parent niche output lacks expected CHELSA columns")
    parent_occ = parent_occ.reset_index(drop=True)
    models = fit_parent_projection(parent_occ, parent_summary, env_cols)

    session = requests.Session()
    session.headers.update({"User-Agent": "EAzami/1.0 white-morph-niche-audit"})
    all_occ = []
    query_audit = []
    summary_rows = []

    gbif_cfg = {
        "country": morph_cfg["country"],
        "page_size": int(morph_cfg["page_size"]),
        "max_records": int(morph_cfg["max_records_per_query"]),
        "japan_bounds": parent_cfg["gbif"]["japan_bounds"],
        "max_coordinate_uncertainty_m": float(morph_cfg["max_coordinate_uncertainty_m"]),
        "spatial_thin_degrees": float(morph_cfg["spatial_thin_degrees"]),
    }

    for item in morph_cfg["morphs"]:
        parent = item["parent_taxon"]
        packets = []
        item_audit = []
        for query in item["queries"]:
            match = niche.gbif_match(session, query, args.request_timeout)
            raw, gbif_meta = niche.fetch_occurrences(
                session,
                name=query,
                taxon_key=match["usage_key"],
                country=gbif_cfg["country"],
                page_size=gbif_cfg["page_size"],
                max_records=gbif_cfg["max_records"],
                timeout=args.request_timeout,
                sleep_s=0.02,
            )
            primary, audit = clean_exact_form(raw, query, gbif_cfg)
            audit.update({"parent_taxon": parent, "gbif_match": match, "gbif_meta": gbif_meta})
            item_audit.append(audit)
            if not primary.empty:
                primary["morph_query"] = query
                packets.append(primary)
        query_audit.extend(item_audit)

        if packets:
            morph = pd.concat(packets, ignore_index=True).drop_duplicates("gbif_key")
            morph, _ = niche.sample_chelsa(morph, parent_cfg["chelsa"]["predictors"])
            morph = morph.loc[morph[env_cols].notna().all(axis=1)].copy()
        else:
            morph = pd.DataFrame()

        clusters = []
        if not morph.empty and parent in models:
            model = models[parent]
            pc = model["pca"].transform(model["scaler"].transform(morph[env_cols]))
            geo = model["geo_scaler"].transform(morph[["latitude", "longitude"]])
            joint = np.hstack([pc, 0.65 * geo])
            morph["parent_niche_cluster"] = model["kmeans"].predict(joint)
            for i in range(pc.shape[1]):
                morph[f"PC{i+1}"] = pc[:, i]
            clusters = sorted(int(x) for x in morph["parent_niche_cluster"].unique())
            morph["parent_taxon"] = parent
            morph["morph_class"] = item["morph_class"]
            all_occ.append(morph)

        n_cells = int(len(morph))
        capable = n_cells >= int(morph_cfg["min_independent_cells_for_projection"])
        if parent == "Cirsium sieboldii":
            decision = (
                "public_white_morph_localities_projectable_but_second_pair_still_requires_P013_P014_field_placement"
                if capable
                else "public_white_morph_locality_insufficient_keep_plus30_conditional_untriggered"
            )
        else:
            decision = (
                "white_morph_localities_projectable_require_flowering_overlap_for_Aim2_matched_pair"
                if capable
                else "public_form_records_insufficient_use_regional_prior_and_field_verification"
            )
        summary_rows.append({
            "parent_taxon": parent,
            "morph_class": item["morph_class"],
            "manual_region_prior": item["manual_region_prior"],
            "environment_complete_thinned_form_records": n_cells,
            "parent_niche_clusters_represented": "|".join(map(str, clusters)),
            "n_parent_niche_clusters_represented": len(clusters),
            "public_morph_locality_decision_capable": capable,
            "phenology_guard": item["phenology_guard"],
            "sampling_decision": decision,
            "automatic_new_population_addition": 0,
        })

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "white_morph_niche_linkage_summary.csv", index=False)
    pd.DataFrame(query_audit).to_json(out / "white_morph_gbif_query_audit.json", orient="records", indent=2, force_ascii=False)
    if all_occ:
        pd.concat(all_occ, ignore_index=True).to_csv(out / "white_morph_occurrences_projected.csv", index=False)
    else:
        pd.DataFrame(columns=["parent_taxon", "morph_class"]).to_csv(out / "white_morph_occurrences_projected.csv", index=False)

    result = {
        "contract_version": "white_morph_niche_linkage_v1",
        "status_date": morph_cfg["status_date"],
        "summary": summary.to_dict(orient="records"),
        "decision_rule": morph_cfg["decision_rule"],
        "claim_boundary": morph_cfg["claim_boundary"],
        "global_decision": "do_not_expand_core190_from_public_morph_records_alone",
    }
    (out / "white_morph_niche_linkage_v1.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
