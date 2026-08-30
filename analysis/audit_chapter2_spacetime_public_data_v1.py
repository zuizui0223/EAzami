#!/usr/bin/env python3
"""Audit Azami and EAzami for a Chapter 2 space × time public-data synthesis.

This is a discovery and admission audit, not a claim-generating meta-analysis.  It
identifies machine-readable tables and explicit result statements relevant to two
cross-scale questions:

1. capitulum orientation × precipitation amount (BIO12) / seasonality (BIO15);
2. flower colour × solar radiation.

The audit records repository SHAs, candidate files, schemas, checksums and short
source contexts.  It fails closed: a new statistical model is not run until one
input table is uniquely identified and frozen in a subsequent analysis contract.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

TEXT_SUFFIXES = {".md", ".txt", ".csv", ".tsv", ".json", ".py", ".r", ".R", ".yml", ".yaml"}
SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "__pycache__", "archive", "vendor"}
MAX_BYTES = 20_000_000

TERM_GROUPS: dict[str, list[str]] = {
    "orientation": [
        r"\borientation\b", r"head[_ -]?direction", r"capitulum[_ -]?angle",
        r"\bnodding\b", r"\bdownward\b", r"\bupward\b", r"頭花.*向", r"向き",
    ],
    "precipitation_amount": [
        r"\bbio0?12\b", r"annual[_ -]?precip", r"precipitation[_ -]?amount",
        r"total[_ -]?precip", r"降水量", r"年降水",
    ],
    "precipitation_seasonality": [
        r"\bbio0?15\b", r"precipitation[_ -]?seasonality", r"seasonal.*precip",
        r"降水季節性", r"降水.*変動",
    ],
    "flower_colour": [
        r"flower[_ -]?colou?r", r"petal[_ -]?colou?r", r"\bCIELAB\b", r"\blightness\b",
        r"\bchroma\b", r"\bpigment", r"anthocyan", r"lab[_ -]?l", r"花色",
    ],
    "solar_radiation": [
        r"\brsds\b", r"solar[_ -]?radiation", r"shortwave", r"irradiance",
        r"\bsrad\b", r"photosynthetically[_ -]?active", r"\bPAR\b", r"\bUV\b", r"日射",
    ],
    "phylogeny": [
        r"\bPGLS\b", r"phylogen", r"UFBoot", r"ASTRAL", r"gene[_ -]?tree",
        r"topolog", r"ancestral[_ -]?state", r"event[_ -]?depth", r"系統",
    ],
    "spatial_model": [
        r"\bINLA\b", r"spatial[_ -]?(?:random|effect|model|field)", r"Moran",
        r"geograph", r"within[_ -]?species", r"among[_ -]?species", r"空間",
    ],
}

COLUMN_ALIASES: dict[str, list[re.Pattern[str]]] = {
    "taxon": [re.compile(x, re.I) for x in [r"^species$", r"scientific.*name", r"accepted.*taxon", r"paper.*concept", r"taxon"]],
    "latitude": [re.compile(x, re.I) for x in [r"^lat(?:itude)?$", r"decimalLatitude"]],
    "longitude": [re.compile(x, re.I) for x in [r"^lon(?:gitude)?$", r"decimalLongitude"]],
    "orientation": [re.compile(x, re.I) for x in [r"orientation", r"head.*direction", r"capitulum.*angle", r"nodding", r"downward"]],
    "bio12": [re.compile(x, re.I) for x in [r"bio0?12", r"annual.*precip", r"precip.*amount", r"total.*precip"]],
    "bio15": [re.compile(x, re.I) for x in [r"bio0?15", r"precip.*season", r"season.*precip"]],
    "solar": [re.compile(x, re.I) for x in [r"rsds", r"solar", r"shortwave", r"irradiance", r"srad", r"(^|_)par($|_)"]],
    "colour": [re.compile(x, re.I) for x in [r"flower.*colou?r", r"petal.*colou?r", r"lightness", r"(^|_)L\*?($|_)", r"lab.*l", r"chroma", r"pigment", r"anthocyan"]],
}


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--azami-root", type=Path, required=True)
    p.add_argument("--eazami-root", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--max-contexts-per-group-file", type=int, default=3)
    return p.parse_args()


def git_sha(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unavailable"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def path_role(rel: str) -> str:
    x = rel.casefold()
    if any(k in x for k in ("data/evidence", "results", "result", "output")):
        return "machine_or_frozen_result"
    if any(k in x for k in ("analysis/", "scripts/", "src/", "tests/")) or x.endswith((".py", ".r")):
        return "analysis_code"
    if any(k in x for k in ("manuscript", "discussion", "README", "docs/")):
        return "narrative_or_contract"
    if any(k in x for k in ("config", "workflow", ".github/")):
        return "configuration"
    return "other"


def compile_groups() -> dict[str, re.Pattern[str]]:
    return {k: re.compile("|".join(f"(?:{x})" for x in v), re.I) for k, v in TERM_GROUPS.items()}


def scan_contexts(repo: str, root: Path, max_contexts: int) -> list[dict[str, Any]]:
    pats = compile_groups()
    rows: list[dict[str, Any]] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        lines = text.splitlines()
        for group, pat in pats.items():
            hits = [i for i, line in enumerate(lines) if pat.search(line)]
            for i in hits[:max_contexts]:
                lo, hi = max(0, i - 1), min(len(lines), i + 2)
                context = " ".join(x.strip() for x in lines[lo:hi] if x.strip())
                rows.append({
                    "repository": repo,
                    "path": rel,
                    "path_role": path_role(rel),
                    "term_group": group,
                    "line": i + 1,
                    "context": context[:1500],
                    "file_sha256": sha256(path),
                })
    return rows


def detect_columns(columns: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for concept, patterns in COLUMN_ALIASES.items():
        for col in columns:
            if any(p.search(str(col)) for p in patterns):
                out[concept] = str(col)
                break
    return out


def json_key_inventory(obj: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield from json_key_inventory(value, path)
    elif isinstance(obj, list):
        for i, value in enumerate(obj[:1000]):
            yield from json_key_inventory(value, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def inspect_tables(repo: str, root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    schemas: list[dict[str, Any]] = []
    json_values: list[dict[str, Any]] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() in {".csv", ".tsv"}:
            sep = "\t" if path.suffix.lower() == ".tsv" else ","
            try:
                frame = pd.read_csv(path, sep=sep, nrows=200_000, low_memory=False)
            except Exception as exc:
                schemas.append({
                    "repository": repo, "path": rel, "read_status": f"error:{type(exc).__name__}",
                    "rows_read": 0, "columns": "", "detected": "{}", "candidate_class": "none",
                    "file_sha256": sha256(path),
                })
                continue
            detected = detect_columns([str(c) for c in frame.columns])
            classes = []
            if "orientation" in detected and ({"bio12", "bio15"} & set(detected)):
                classes.append("orientation_precipitation")
            if "colour" in detected and "solar" in detected:
                classes.append("colour_solar")
            if "taxon" in detected and "orientation" in detected:
                classes.append("orientation_trait_table")
            if "taxon" in detected and "colour" in detected:
                classes.append("colour_trait_table")
            if ("latitude" in detected and "longitude" in detected) and ({"bio12", "bio15", "solar"} & set(detected)):
                classes.append("georeferenced_environment")
            schemas.append({
                "repository": repo,
                "path": rel,
                "read_status": "ok",
                "rows_read": int(len(frame)),
                "columns": " | ".join(map(str, frame.columns)),
                "detected": json.dumps(detected, sort_keys=True),
                "candidate_class": " | ".join(classes) if classes else "none",
                "file_sha256": sha256(path),
            })
        elif path.suffix.lower() == ".json":
            try:
                obj = json.loads(read_text(path))
            except Exception:
                continue
            for key, value in json_key_inventory(obj):
                low = key.casefold()
                groups = []
                if re.search(r"bio0?12|annual.*precip|precip.*amount", low):
                    groups.append("precipitation_amount")
                if re.search(r"bio0?15|precip.*season", low):
                    groups.append("precipitation_seasonality")
                if re.search(r"rsds|solar|shortwave|irradiance|srad", low):
                    groups.append("solar_radiation")
                if re.search(r"colou?r|lightness|chroma|pigment|anthocyan", low):
                    groups.append("flower_colour")
                if re.search(r"orientation|nodding|downward|upward", low):
                    groups.append("orientation")
                if groups:
                    json_values.append({
                        "repository": repo,
                        "path": rel,
                        "key_path": key,
                        "term_groups": " | ".join(sorted(set(groups))),
                        "value": str(value)[:1000],
                        "file_sha256": sha256(path),
                    })
    return schemas, json_values


def candidate_summary(schemas: pd.DataFrame) -> dict[str, Any]:
    if schemas.empty:
        return {}
    out: dict[str, Any] = {}
    for cls in ("orientation_precipitation", "colour_solar", "orientation_trait_table", "colour_trait_table", "georeferenced_environment"):
        mask = schemas["candidate_class"].fillna("").str.contains(cls, regex=False)
        q = schemas.loc[mask].sort_values(["repository", "rows_read", "path"], ascending=[True, False, True])
        out[cls] = q[["repository", "path", "rows_read", "detected", "file_sha256"]].to_dict(orient="records")
    return out


def evidence_counts(contexts: pd.DataFrame) -> dict[str, Any]:
    if contexts.empty:
        return {}
    counts = contexts.groupby(["repository", "term_group", "path_role"]).size().rename("n_contexts").reset_index()
    return counts.to_dict(orient="records")


def write_report(payload: dict[str, Any], path: Path) -> None:
    cs = payload["candidate_tables"]
    lines = [
        "# Chapter 2 space × time public-data audit v1",
        "",
        f"- Azami SHA: `{payload['repositories']['azami']['sha']}`",
        f"- EAzami SHA: `{payload['repositories']['eazami']['sha']}`",
        "",
        "## Purpose",
        "",
        "Freeze the public-data interface between **Azami = spatial breadth** and **EAzami = phylogenetic/historical depth**. The audit searches for orientation–precipitation and colour–solar evidence without treating narrative mentions as statistical results.",
        "",
        "## Candidate machine-readable tables",
        "",
    ]
    for cls, rows in cs.items():
        lines.append(f"### {cls}")
        lines.append("")
        if not rows:
            lines.append("No strict schema match found.")
        else:
            lines.append("| repository | path | rows read | detected columns |")
            lines.append("| --- | --- | ---: | --- |")
            for r in rows[:30]:
                lines.append(f"| {r['repository']} | `{r['path']}` | {r['rows_read']} | `{r['detected']}` |")
        lines.append("")
    lines.extend([
        "## Admission decision",
        "",
        payload["admission_decision"],
        "",
        "## Claim boundary",
        "",
        "This inventory identifies reusable inputs and existing result statements. It does not make a new adaptive claim. BIO12 and BIO15 must be compared in the same admitted panel and colour–solar analysis must use a directly linked colour metric and radiation layer before cross-scale consistency is evaluated.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    a = args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    repos = {"azami": a.azami_root, "eazami": a.eazami_root}
    all_contexts: list[dict[str, Any]] = []
    all_schemas: list[dict[str, Any]] = []
    all_json: list[dict[str, Any]] = []
    for name, root in repos.items():
        if not root.exists():
            raise FileNotFoundError(root)
        all_contexts.extend(scan_contexts(name, root, a.max_contexts_per_group_file))
        schemas, json_values = inspect_tables(name, root)
        all_schemas.extend(schemas)
        all_json.extend(json_values)

    contexts = pd.DataFrame(all_contexts)
    schemas = pd.DataFrame(all_schemas)
    json_values = pd.DataFrame(all_json)
    contexts.to_csv(a.out_dir / "chapter2_spacetime_text_evidence_inventory_v1.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    schemas.to_csv(a.out_dir / "chapter2_spacetime_table_schema_inventory_v1.csv", index=False)
    json_values.to_csv(a.out_dir / "chapter2_spacetime_json_value_inventory_v1.csv", index=False)

    candidates = candidate_summary(schemas)
    strict_orientation = candidates.get("orientation_precipitation", [])
    strict_colour = candidates.get("colour_solar", [])
    if strict_orientation and strict_colour:
        decision = "Strict machine-readable candidates exist for both questions. Freeze exact paths and checksums in the next model contract before fitting joint spatial/phylogenetic models."
        status = "BOTH_QUESTIONS_HAVE_STRICT_TABLE_CANDIDATES_CONTRACT_FREEZE_REQUIRED"
    elif strict_orientation:
        decision = "A strict orientation–precipitation table candidate exists, but no strict colour–solar table is yet directly linked. Proceed with BIO12/BIO15 harmonization; build or join a pinned solar layer to the admitted colour observations before fitting the colour model."
        status = "ORIENTATION_READY_COLOUR_SOLAR_JOIN_REQUIRED"
    elif strict_colour:
        decision = "A strict colour–solar table candidate exists, but orientation and both precipitation dimensions are not yet in one machine-readable table. Freeze the colour model and construct the orientation BIO12/BIO15 join."
        status = "COLOUR_READY_ORIENTATION_PRECIP_JOIN_REQUIRED"
    else:
        decision = "No single strict table directly contains the required trait and environmental variables. Use the recorded trait/environment candidates to build explicit checksum-pinned joins; do not infer results from prose hits."
        status = "EXPLICIT_JOINS_REQUIRED"

    payload = {
        "contract_version": "chapter2_spacetime_public_data_audit_v1",
        "status": status,
        "repositories": {
            name: {"root": str(root), "sha": git_sha(root)} for name, root in repos.items()
        },
        "questions": {
            "orientation_precipitation": "Compare BIO12 amount and BIO15 seasonality under the same admitted panel, including joint/partial effects and cross-scale direction.",
            "colour_solar": "Test image-derived flower colour against a pinned solar-radiation climatology; add a historical layer only if exact concept coverage permits it.",
        },
        "candidate_tables": candidates,
        "evidence_context_counts": evidence_counts(contexts),
        "n_text_contexts": int(len(contexts)),
        "n_table_schemas": int(len(schemas)),
        "n_json_values": int(len(json_values)),
        "admission_decision": decision,
        "claim_boundary": "Discovery audit only. Narrative co-occurrence of terms is not a quantitative association; cross-scale agreement can strengthen an adaptive hypothesis but cannot establish fitness or historical causation.",
    }
    (a.out_dir / "chapter2_spacetime_public_data_audit_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(payload, a.out_dir / "CHAPTER2_SPACETIME_PUBLIC_DATA_AUDIT_V1.md")
    print(json.dumps({"status": status, "repositories": payload["repositories"], "candidate_counts": {k: len(v) for k, v in candidates.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
