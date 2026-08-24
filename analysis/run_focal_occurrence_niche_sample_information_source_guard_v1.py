#!/usr/bin/env python3
"""Run the focal niche audit with taxonomy and local-support guards.

GBIF currently resolves some focal taxa (notably Cirsium irumtiense) as synonyms of
other focal taxa (notably C. brevicaule). A taxon-key query can therefore return
records whose accepted name is C. brevicaule but whose source scientificName is
C. irumtiense. That collapse is unacceptable for EAzami's colour-history and
population-sampling questions.

Two safeguards are applied before any sampling recommendation:
1. retain only records whose source `scientificName` matches the query taxon;
2. for the already-existing P003/P004 intermediate slots, reject isolated public
   occurrence points and require an actual intermediate bridge between the two
   declared region anchors.

These rules protect sample design; they do not redefine a taxon's biological range.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_focal_occurrence_niche_sample_information_v1 as v1  # noqa: E402

SOURCE_FILTER_COUNTS: dict[str, dict[str, int]] = {}
SLOT_SELECTION_AUDIT: dict[str, dict[str, float | int | str]] = {}
_BASE_CLEAN = v1.clean_and_thin
_BASE_SELECT = v1.select_distinct_candidates


def normalize_name(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def source_name_matches_query(source_name: object, query_name: object) -> bool:
    source = normalize_name(source_name).casefold()
    query = normalize_name(query_name).casefold()
    return bool(source and query and (source == query or source.startswith(query + " ")))


def guarded_clean_and_thin(raw: pd.DataFrame, cfg: dict):
    if raw.empty:
        return _BASE_CLEAN(raw, cfg)
    queries = [normalize_name(x) for x in raw["scientific_name_query"].dropna().unique()]
    if len(queries) != 1:
        raise ValueError(f"Expected one query taxon per GBIF packet, found {queries}")
    query = queries[0]
    mask = raw["scientificName"].map(lambda x: source_name_matches_query(x, query))
    kept = raw.loc[mask].copy()
    SOURCE_FILTER_COUNTS[query] = {
        "n_pre_source_filter": int(len(raw)),
        "n_source_taxon_match": int(mask.sum()),
        "n_source_taxon_excluded": int((~mask).sum()),
    }
    primary, meta = _BASE_CLEAN(kept, cfg)
    meta.update(SOURCE_FILTER_COUNTS[query])
    return primary, meta


def local_neighbor_counts(frame: pd.DataFrame, radius_km: float = 75.0) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype=int, index=frame.index)
    counts = []
    for _, row in frame.iterrows():
        count = 0
        for _, other in frame.iterrows():
            if row.name == other.name:
                continue
            if v1.haversine_km(
                float(row["latitude"]), float(row["longitude"]),
                float(other["latitude"]), float(other["longitude"]),
            ) <= radius_km:
                count += 1
        counts.append(count)
    return pd.Series(counts, index=frame.index, dtype=int)


def guarded_select_distinct_candidates(frame: pd.DataFrame, n: int, min_distance_km: float = 50.0) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    work = frame.copy()
    work["local_support_neighbors_75km"] = local_neighbor_counts(work, 75.0)
    work = work.loc[
        (work["local_support_neighbors_75km"] >= 1)
        & (pd.to_numeric(work["bridge_relevance"], errors="coerce").fillna(0.0) > 0.15)
    ].copy()
    if work.empty:
        return frame.head(0).copy()

    support_max = max(1.0, float(work["local_support_neighbors_75km"].quantile(0.90)))
    work["local_support_score"] = (work["local_support_neighbors_75km"].astype(float) / support_max).clip(0.0, 1.0)
    work["intermediate_slot_score"] = (
        0.45 * pd.to_numeric(work["bridge_relevance"], errors="coerce").fillna(0.0)
        + 0.30 * pd.to_numeric(work["coverage_gain"], errors="coerce").fillna(0.0)
        + 0.15 * pd.to_numeric(work["niche_edge"], errors="coerce").fillna(0.0)
        + 0.10 * work["local_support_score"]
    )

    chosen = []
    used_clusters: set[int] = set()
    for _, row in work.sort_values("intermediate_slot_score", ascending=False).iterrows():
        cluster = int(row["cluster_id"])
        if cluster in used_clusters:
            continue
        if any(
            v1.haversine_km(float(row["latitude"]), float(row["longitude"]), float(old["latitude"]), float(old["longitude"])) < min_distance_km
            for old in chosen
        ):
            continue
        chosen.append(row)
        used_clusters.add(cluster)
        key = str(row.get("gbif_key", ""))
        SLOT_SELECTION_AUDIT[key] = {
            "local_support_neighbors_75km": int(row["local_support_neighbors_75km"]),
            "local_support_score": float(row["local_support_score"]),
            "intermediate_slot_score": float(row["intermediate_slot_score"]),
            "selection_guard": "source_name_match_and_neighbor_support_and_intermediate_bridge",
        }
        if len(chosen) >= n:
            break
    if not chosen:
        return work.head(0).copy()
    return pd.DataFrame(chosen)


def append_guard_audit(out_dir: Path) -> None:
    summary_path = out_dir / "focal_niche_sampling_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    summary = pd.read_csv(summary_path)
    for column in ["n_pre_source_filter", "n_source_taxon_match", "n_source_taxon_excluded"]:
        summary[column] = summary["taxon"].map(lambda taxon: SOURCE_FILTER_COUNTS.get(str(taxon), {}).get(column, 0))
    summary.to_csv(summary_path, index=False)

    matches_path = out_dir / "gbif_taxon_matches.csv"
    if matches_path.exists():
        matches = pd.read_csv(matches_path)
        for column in ["n_pre_source_filter", "n_source_taxon_match", "n_source_taxon_excluded"]:
            matches[column] = matches["query_name"].map(lambda taxon: SOURCE_FILTER_COUNTS.get(str(taxon), {}).get(column, 0))
        matches.to_csv(matches_path, index=False)

    slots_path = out_dir / "p003_p004_niche_stratum_candidates.csv"
    if slots_path.exists():
        try:
            slots = pd.read_csv(slots_path)
        except EmptyDataError:
            # No supported P003/P004 bridge candidate is a legitimate result.
            # Preserve a machine-readable empty table instead of failing the entire niche run.
            slots = pd.DataFrame(columns=[
                "population_slot", "taxon", "gbif_key_reference",
                "local_support_neighbors_75km", "local_support_score",
                "intermediate_slot_score", "selection_guard",
            ])
        if not slots.empty:
            for column in ["local_support_neighbors_75km", "local_support_score", "intermediate_slot_score", "selection_guard"]:
                slots[column] = slots["gbif_key_reference"].map(lambda key: SLOT_SELECTION_AUDIT.get(str(key), {}).get(column, ""))
        slots.to_csv(slots_path, index=False)


if __name__ == "__main__":
    v1.clean_and_thin = guarded_clean_and_thin
    v1.select_distinct_candidates = guarded_select_distinct_candidates
    argv = sys.argv[1:]
    out_dir = None
    for i, arg in enumerate(argv):
        if arg == "--out-dir" and i + 1 < len(argv):
            out_dir = Path(argv[i + 1])
            break
        if arg.startswith("--out-dir="):
            out_dir = Path(arg.split("=", 1)[1])
            break
    if out_dir is None:
        raise SystemExit("--out-dir is required")
    v1.main()
    append_guard_audit(out_dir)
