#!/usr/bin/env python3
"""Inventory Azami tables for a reproducible flower-colour × solar analysis.

The script reads table schemas rather than assuming a particular Azami output. It
scores whether each table contains colour metrics, solar exposure, coordinates,
taxon identity, observation date and image/source controls. No statistical result
is inferred during discovery.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

PATTERNS = {
    "colour_lightness": [r"(^|_)lstar($|_)", r"lightness", r"cielab[_ -]?l", r"flower[_ -]?l"],
    "colour_chroma": [r"(^|_)cstar($|_)", r"chroma", r"saturation"],
    "colour_hue_pigment": [r"pigment", r"anthocyan", r"hue", r"cielab[_ -]?a", r"cielab[_ -]?b", r"flower[_ -]?colou?r"],
    "solar": [r"rsds", r"shortwave", r"solar", r"irradiance", r"radiation", r"uvb?($|_)"],
    "latitude": [r"(^|_)lat(itude)?($|_)", r"decimal[_ -]?latitude"],
    "longitude": [r"(^|_)lon(gitude)?($|_)", r"decimal[_ -]?longitude"],
    "taxon": [r"taxon", r"species", r"scientific[_ -]?name", r"accepted[_ -]?name"],
    "date": [r"date", r"month", r"year", r"observed[_ -]?on", r"event[_ -]?date"],
    "image_source": [r"source", r"dataset", r"platform", r"inat", r"gbif", r"image[_ -]?id", r"photo[_ -]?id", r"license"],
    "orientation": [r"orientation", r"head[_ -]?direction", r"nodding", r"capitulum[_ -]?angle"],
    "precipitation": [r"bio12", r"bio15", r"precip", r"rainfall"],
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--max-files", type=int, default=20000)
    p.add_argument("--max-size-mb", type=float, default=500.0)
    return p.parse_args()


def canonical(column: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", str(column).casefold()).strip("_")
    return value


def matching_columns(columns: Iterable[str], family: str) -> list[str]:
    out = []
    for original in columns:
        value = canonical(original)
        if any(re.search(pattern, value) for pattern in PATTERNS[family]):
            out.append(str(original))
    return sorted(set(out))


def candidate_paths(root: Path, max_files: int, max_bytes: int) -> list[Path]:
    extensions = {".csv", ".tsv", ".txt", ".parquet", ".feather", ".json", ".jsonl"}
    paths = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in extensions:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size <= 0 or size > max_bytes:
            continue
        paths.append(path)
        if len(paths) >= max_files:
            break
    return sorted(paths)


def read_schema(path: Path) -> tuple[list[str], int | None, str]:
    suffix = path.suffix.casefold()
    if suffix == ".csv":
        frame = pd.read_csv(path, nrows=20)
        return list(frame.columns), None, "csv"
    if suffix in {".tsv", ".txt"}:
        frame = pd.read_csv(path, sep="\t", nrows=20)
        return list(frame.columns), None, "tsv"
    if suffix == ".parquet":
        frame = pd.read_parquet(path)
        return list(frame.columns), int(len(frame)), "parquet"
    if suffix == ".feather":
        frame = pd.read_feather(path)
        return list(frame.columns), int(len(frame)), "feather"
    if suffix == ".jsonl":
        frame = pd.read_json(path, lines=True, nrows=20)
        return list(frame.columns), None, "jsonl"
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list) and payload and isinstance(payload[0], dict):
            columns = sorted({str(k) for row in payload[:100] if isinstance(row, dict) for k in row})
            return columns, len(payload), "json_records"
        if isinstance(payload, dict):
            columns = sorted(str(k) for k in payload)
            return columns, None, "json_object"
    raise ValueError(f"unsupported or non-tabular {path}")


def score(families: dict[str, list[str]]) -> tuple[int, str]:
    colour = bool(families["colour_lightness"] or families["colour_chroma"] or families["colour_hue_pigment"])
    solar = bool(families["solar"])
    coords = bool(families["latitude"] and families["longitude"])
    taxon = bool(families["taxon"])
    date = bool(families["date"])
    source = bool(families["image_source"])
    points = 0
    points += 6 if colour else 0
    points += 6 if solar else 0
    points += 4 if coords else 0
    points += 4 if taxon else 0
    points += 2 if date else 0
    points += 2 if source else 0
    if colour and solar and taxon:
        readiness = "direct_colour_solar_model_candidate"
    elif colour and coords and taxon:
        readiness = "colour_coordinates_ready_for_public_solar_join"
    elif colour and taxon:
        readiness = "colour_taxon_only_needs_geographic_join"
    elif solar and coords:
        readiness = "environment_table_needs_colour_join"
    else:
        readiness = "not_ready"
    return points, readiness


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = int(args.max_size_mb * 1024 * 1024)
    rows = []
    unreadable = []
    for path in candidate_paths(args.root, args.max_files, max_bytes):
        try:
            columns, n_rows, format_name = read_schema(path)
        except Exception as exc:
            unreadable.append({"path": str(path), "error": repr(exc)})
            continue
        families = {family: matching_columns(columns, family) for family in PATTERNS}
        points, readiness = score(families)
        if points == 0:
            continue
        rows.append(
            {
                "path": str(path),
                "format": format_name,
                "size_bytes": int(path.stat().st_size),
                "n_rows_if_known": n_rows,
                "n_columns": len(columns),
                "score": points,
                "readiness": readiness,
                "all_columns_json": json.dumps(columns, ensure_ascii=False),
                **{f"{family}_columns": " | ".join(values) for family, values in families.items()},
            }
        )
    inventory = pd.DataFrame(rows)
    if inventory.empty:
        inventory = pd.DataFrame(
            columns=[
                "path", "format", "size_bytes", "n_rows_if_known", "n_columns", "score", "readiness",
                "all_columns_json", *[f"{family}_columns" for family in PATTERNS]
            ]
        )
    inventory = inventory.sort_values(["score", "path"], ascending=[False, True], kind="stable")
    inventory.to_csv(args.out_dir / "azami_colour_solar_input_inventory_v1.csv", index=False)
    ready_counts = inventory["readiness"].value_counts().to_dict() if len(inventory) else {}
    top = inventory.head(25).to_dict(orient="records") if len(inventory) else []
    payload = {
        "contract_version": "azami_colour_solar_input_discovery_v1",
        "root": str(args.root),
        "candidate_tables": int(len(inventory)),
        "readiness_counts": {str(k): int(v) for k, v in ready_counts.items()},
        "top_candidates": top,
        "unreadable_files": unreadable,
        "decision_rule": {
            "direct_model": "colour metric + solar exposure + taxon in one table",
            "public_join": "colour metric + coordinates + taxon; source-balanced solar/UV extraction still required",
            "source_controls": "date and image/source identifiers are required before a result enters the main concordance ledger"
        },
        "claim_boundary": "Schema discovery does not establish a colour-solar association and does not certify that a candidate table is source-balanced or taxonomically exact."
    }
    (args.out_dir / "azami_colour_solar_input_discovery_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
