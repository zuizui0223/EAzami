#!/usr/bin/env python3
"""Resolve a row-level Azami flower-colour table without filename cherry-picking.

Every tabular file under the supplied public repository/artifact roots is scored by
a frozen schema rule. A table is admissible only when it contains a taxon, valid
coordinates and at least one direct flower-colour metric (CIELAB lightness/chroma,
CIELAB a/b from which chroma is derived, or an explicitly named pigment metric).
Synthetic, fixture, archived and result-summary files are retained in the inventory
but excluded from primary selection. Byte-identical copies are collapsed.

The highest-scoring candidate is selected only if it is uniquely separated from the
next non-identical candidate and passes minimum row/taxon coverage. Otherwise the
result is ``not_evaluable_ambiguous_input`` and no colour–solar model is run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

TABULAR_SUFFIXES = {".csv", ".tsv", ".parquet", ".feather", ".xlsx", ".xls", ".json"}
EXCLUDE_PATH_TERMS = {
    "test", "tests", "fixture", "fixtures", "example", "examples", "synthetic",
    "simulation", "permutation", "null", "archive", "legacy", "deprecated",
    "summary", "aggregate", "coefficient", "model_output", "model-output",
}

COLUMN_PATTERNS: dict[str, list[str]] = {
    "taxon": [r"^scientific_name$", r"scientific_name_query", r"accepted_taxon", r"paper_taxon_concept", r"^species$", r"taxon"],
    "latitude": [r"^latitude$", r"^lat$", r"decimalLatitude", r"decimal_latitude"],
    "longitude": [r"^longitude$", r"^lon$", r"^lng$", r"decimalLongitude", r"decimal_longitude"],
    "source": [r"^source$", r"data_source", r"platform", r"provider", r"dataset"],
    "image_id": [r"image_id", r"photo_id", r"observation_id", r"occurrence_id", r"gbifid", r"inat.*id", r"yamap.*id"],
    "lightness": [r"flower.*light", r"petal.*light", r"cielab.*(?:^|_)l(?:$|_)", r"lab.*(?:^|_)l(?:$|_)", r"^l_star$", r"^lstar$", r"^lightness$", r"mean_l(?:$|_)"],
    "lab_a": [r"flower.*lab.*a", r"petal.*lab.*a", r"cielab.*(?:^|_)a(?:$|_)", r"^a_star$", r"^astar$", r"^lab_a$", r"mean_a(?:$|_)"],
    "lab_b": [r"flower.*lab.*b", r"petal.*lab.*b", r"cielab.*(?:^|_)b(?:$|_)", r"^b_star$", r"^bstar$", r"^lab_b$", r"mean_b(?:$|_)"],
    "chroma": [r"flower.*chroma", r"petal.*chroma", r"^chroma$", r"^c_star$", r"^cstar$", r"cielab.*chroma"],
    "pigment": [r"flower.*pigment", r"petal.*pigment", r"pigment_score", r"pigmentation", r"anthocyanin.*index", r"colour_intensity", r"color_intensity"],
    "solar": [r"^rsds$", r"solar.*radiation", r"shortwave", r"irradiance", r"^srad$"],
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, action="append", required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--min-rows", type=int, default=100)
    p.add_argument("--min-taxa", type=int, default=5)
    p.add_argument("--score-margin", type=int, default=5)
    p.add_argument("--max-file-mb", type=float, default=1000)
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_table(path: Path, nrows: int | None = None) -> pd.DataFrame:
    suffix = path.suffix.casefold()
    if suffix == ".csv":
        return pd.read_csv(path, nrows=nrows, low_memory=False)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t", nrows=nrows, low_memory=False)
    if suffix == ".parquet":
        frame = pd.read_parquet(path)
        return frame.head(nrows) if nrows else frame
    if suffix == ".feather":
        frame = pd.read_feather(path)
        return frame.head(nrows) if nrows else frame
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, nrows=nrows)
    if suffix == ".json":
        try:
            frame = pd.read_json(path)
        except ValueError:
            frame = pd.read_json(path, lines=True)
        return frame.head(nrows) if nrows else frame
    raise ValueError(suffix)


def normalize_col(name: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).casefold()).strip("_")


def first_match(columns: list[str], patterns: list[str]) -> str | None:
    normalized = {col: normalize_col(col) for col in columns}
    for pattern in patterns:
        rx = re.compile(pattern, re.I)
        for original, normed in normalized.items():
            if rx.search(normed):
                return original
    return None


def detect(columns: list[str]) -> dict[str, str]:
    return {key: match for key, pats in COLUMN_PATTERNS.items() if (match := first_match(columns, pats)) is not None}


def excluded_path(path: Path) -> tuple[bool, list[str]]:
    low_parts = [x.casefold() for x in path.parts]
    hits = sorted({term for term in EXCLUDE_PATH_TERMS if any(term in part for part in low_parts)})
    return bool(hits), hits


def numeric_fraction(series: pd.Series) -> float:
    return float(pd.to_numeric(series, errors="coerce").notna().mean()) if len(series) else 0.0


def inspect(path: Path, root_index: int, max_bytes: int) -> dict[str, Any]:
    rel = path.as_posix()
    row: dict[str, Any] = {
        "root_index": root_index,
        "path": rel,
        "size_bytes": path.stat().st_size,
        "sha256": "",
        "read_status": "",
        "columns": [],
        "detected": {},
        "n_sample_rows": 0,
        "estimated_rows": None,
        "n_valid_coordinate_rows_sample": 0,
        "n_taxa_sample": 0,
        "score": -10_000,
        "excluded_primary": True,
        "exclusion_reasons": [],
    }
    if path.stat().st_size > max_bytes:
        row["read_status"] = "too_large"
        row["exclusion_reasons"] = ["file_size_exceeds_contract"]
        return row
    try:
        row["sha256"] = sha256(path)
        sample = read_table(path, nrows=20_000)
    except Exception as exc:
        row["read_status"] = f"error:{type(exc).__name__}:{exc}"
        row["exclusion_reasons"] = ["unreadable"]
        return row
    row["read_status"] = "ok"
    row["columns"] = [str(c) for c in sample.columns]
    found = detect(row["columns"])
    row["detected"] = found
    row["n_sample_rows"] = int(len(sample))
    path_excluded, path_hits = excluded_path(path)
    reasons: list[str] = []
    if path_excluded:
        reasons.append("excluded_path_terms:" + "|".join(path_hits))
    for required in ("taxon", "latitude", "longitude"):
        if required not in found:
            reasons.append(f"missing_{required}")
    colour_direct = [x for x in ("pigment", "lightness", "chroma") if x in found]
    has_ab = "lab_a" in found and "lab_b" in found
    if not colour_direct and not has_ab:
        reasons.append("missing_direct_flower_colour_metric")
    if len(sample) < 2:
        reasons.append("too_few_sample_rows")

    valid = pd.Series(True, index=sample.index)
    if "latitude" in found and "longitude" in found:
        lat = pd.to_numeric(sample[found["latitude"]], errors="coerce")
        lon = pd.to_numeric(sample[found["longitude"]], errors="coerce")
        valid = lat.between(-90, 90) & lon.between(-180, 180)
        row["n_valid_coordinate_rows_sample"] = int(valid.sum())
        if valid.mean() < 0.5:
            reasons.append("less_than_half_valid_coordinates")
    if "taxon" in found:
        taxa = sample.loc[valid, found["taxon"]].dropna().astype(str).str.strip()
        row["n_taxa_sample"] = int(taxa[taxa.ne("")].nunique())

    metric_numeric: dict[str, float] = {}
    for metric in ("pigment", "lightness", "chroma", "lab_a", "lab_b"):
        if metric in found:
            metric_numeric[metric] = numeric_fraction(sample.loc[valid, found[metric]])
            if metric_numeric[metric] < 0.5:
                reasons.append(f"{metric}_less_than_half_numeric")
    row["metric_numeric_fraction"] = metric_numeric

    score = 0
    score += 20 if all(x in found for x in ("taxon", "latitude", "longitude")) else 0
    score += 18 if "pigment" in found else 0
    score += 15 if "lightness" in found else 0
    score += 12 if "chroma" in found else 0
    score += 10 if has_ab else 0
    score += 5 if "source" in found else 0
    score += 4 if "image_id" in found else 0
    score += 3 if "solar" in found else 0
    score += min(10, int(math.log10(max(len(sample), 1)) * 2))
    score += min(10, row["n_taxa_sample"])
    score -= 40 if path_excluded else 0
    score -= 20 * sum(r.startswith("missing_") for r in reasons)
    row["score"] = score
    row["excluded_primary"] = bool(reasons)
    row["exclusion_reasons"] = reasons
    return row


def normalize_selected(path: Path, detected: dict[str, str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    data = read_table(path)
    out = pd.DataFrame({
        "taxon_raw": data[detected["taxon"]].astype(str).str.strip(),
        "latitude": pd.to_numeric(data[detected["latitude"]], errors="coerce"),
        "longitude": pd.to_numeric(data[detected["longitude"]], errors="coerce"),
    })
    if "source" in detected:
        out["source"] = data[detected["source"]].fillna("unknown").astype(str)
    else:
        out["source"] = "unknown"
    if "image_id" in detected:
        out["image_id"] = data[detected["image_id"]].fillna("").astype(str)
    else:
        out["image_id"] = [f"row_{i}" for i in range(len(out))]
    metric_map: dict[str, str] = {}
    for metric in ("pigment", "lightness", "chroma", "lab_a", "lab_b", "solar"):
        if metric in detected:
            col = f"observed_{metric}"
            out[col] = pd.to_numeric(data[detected[metric]], errors="coerce")
            metric_map[metric] = col
    if "chroma" not in metric_map and {"lab_a", "lab_b"}.issubset(metric_map):
        out["observed_chroma_derived"] = np.sqrt(out[metric_map["lab_a"]] ** 2 + out[metric_map["lab_b"]] ** 2)
        metric_map["chroma"] = "observed_chroma_derived"
    valid = (
        out["taxon_raw"].notna() & out["taxon_raw"].ne("")
        & out["latitude"].between(-90, 90)
        & out["longitude"].between(-180, 180)
    )
    colour_cols = [metric_map[x] for x in ("pigment", "lightness", "chroma") if x in metric_map]
    if not colour_cols:
        raise RuntimeError("selected table has no normalized colour metric")
    valid &= out[colour_cols].notna().any(axis=1)
    out = out.loc[valid].copy()
    out["canonical_cell_005_lat"] = np.floor(out.latitude / 0.05).astype(int)
    out["canonical_cell_005_lon"] = np.floor(out.longitude / 0.05).astype(int)
    out = out.sort_values(["taxon_raw", "canonical_cell_005_lat", "canonical_cell_005_lon", "image_id"])
    out = out.drop_duplicates(["taxon_raw", "canonical_cell_005_lat", "canonical_cell_005_lon", "image_id"], keep="first")
    primary = "pigment" if "pigment" in metric_map else "lightness" if "lightness" in metric_map else "chroma"
    direction = "higher_is_more_pigmented" if primary != "lightness" else "multiply_by_minus_one_for_pigmentation_intensity"
    manifest = {
        "normalized_metric_columns": metric_map,
        "primary_metric": primary,
        "primary_direction_rule": direction,
        "normalized_rows": int(len(out)),
        "normalized_taxa": int(out.taxon_raw.nunique()),
        "sources": {str(k): int(v) for k, v in out.source.value_counts().items()},
    }
    return out, manifest


def main() -> int:
    a = parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = int(a.max_file_mb * 1024 * 1024)
    rows: list[dict[str, Any]] = []
    for root_index, root in enumerate(a.root, 1):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.casefold() in TABULAR_SUFFIXES:
                rows.append(inspect(path, root_index, max_bytes))
    inventory = pd.DataFrame(rows)
    if inventory.empty:
        raise RuntimeError("no tabular files found")
    inventory["columns_json"] = inventory["columns"].map(json.dumps)
    inventory["detected_json"] = inventory["detected"].map(lambda x: json.dumps(x, sort_keys=True))
    inventory["exclusion_reasons_json"] = inventory["exclusion_reasons"].map(json.dumps)
    inventory.drop(columns=["columns", "detected", "exclusion_reasons"], errors="ignore").to_csv(a.out_dir / "azami_colour_table_candidate_inventory_v1.csv", index=False)

    eligible = [x for x in rows if not x["excluded_primary"]]
    # Collapse byte-identical copies; prefer the shortest path as canonical.
    by_sha: dict[str, dict[str, Any]] = {}
    copies: dict[str, list[str]] = {}
    for row in eligible:
        sha = row["sha256"]
        copies.setdefault(sha, []).append(row["path"])
        if sha not in by_sha or (row["score"], -len(row["path"])) > (by_sha[sha]["score"], -len(by_sha[sha]["path"])):
            by_sha[sha] = row
    unique = sorted(by_sha.values(), key=lambda x: (-x["score"], -x["n_valid_coordinate_rows_sample"], x["path"]))

    status = "not_evaluable_no_admissible_input"
    selected: dict[str, Any] | None = None
    if unique:
        top = unique[0]
        second_score = unique[1]["score"] if len(unique) > 1 else -10_000
        if top["score"] - second_score >= a.score_margin:
            selected = top
            status = "selected_unique_public_colour_observation_table"
        else:
            status = "not_evaluable_ambiguous_input"

    normalized_manifest: dict[str, Any] | None = None
    if selected is not None:
        normalized, normalized_manifest = normalize_selected(Path(selected["path"]), selected["detected"])
        if len(normalized) < a.min_rows or normalized.taxon_raw.nunique() < a.min_taxa:
            status = "not_evaluable_selected_table_below_coverage_gate"
            selected = None
            normalized_manifest = None
        else:
            normalized.to_csv(a.out_dir / "azami_colour_observations_normalized_v1.csv", index=False)

    payload = {
        "contract_version": "azami_colour_observation_resolution_v1",
        "status": status,
        "roots": [str(x) for x in a.root],
        "files_inspected": len(rows),
        "admissible_nonidentical_candidates": len(unique),
        "selection_rule": {
            "minimum_rows": a.min_rows,
            "minimum_taxa": a.min_taxa,
            "minimum_score_margin": a.score_margin,
            "byte_identical_copies_collapsed": True,
            "excluded_path_terms": sorted(EXCLUDE_PATH_TERMS),
        },
        "selected": ({
            "path": selected["path"],
            "sha256": selected["sha256"],
            "score": selected["score"],
            "detected_columns": selected["detected"],
            "byte_identical_copies": copies[selected["sha256"]],
        } if selected else None),
        "normalized": normalized_manifest,
        "ranked_candidates": [
            {
                "path": x["path"], "sha256": x["sha256"], "score": x["score"],
                "n_valid_coordinate_rows_sample": x["n_valid_coordinate_rows_sample"],
                "n_taxa_sample": x["n_taxa_sample"], "detected_columns": x["detected"],
                "byte_identical_copies": copies[x["sha256"]],
            }
            for x in unique[:50]
        ],
        "claim_boundary": "Schema-based resolution only. Selection does not establish that the colour metric is unbiased, calibrated or biologically adaptive; those properties are evaluated by the subsequent source, spatial and phylogenetic sensitivity models.",
    }
    (a.out_dir / "azami_colour_observation_resolution_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "files_inspected": len(rows), "admissible_candidates": len(unique), "selected": payload["selected"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
