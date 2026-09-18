#!/usr/bin/env python3
"""Audit the public-data evidence available for Chapter 2 space-time synthesis.

The audit searches frozen Azami handoff/evidence files for spatial effects that can
be compared with EAzami phylogeny-aware results. It does not infer an effect from a
keyword hit. Candidate records are preserved verbatim with source file, row/path and
numeric fields so scientific admission can be reviewed without silent cherry-picking.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

QUESTION_PATTERNS = {
    "orientation_precipitation_amount": {
        "trait": [r"orientation", r"head[_ -]?direction", r"nodding", r"capitulum[_ -]?angle"],
        "environment": [r"bio12", r"annual[_ -]?precip", r"precipitation[_ -]?amount", r"rainfall[_ -]?amount", r"total[_ -]?precip"],
    },
    "orientation_precipitation_seasonality": {
        "trait": [r"orientation", r"head[_ -]?direction", r"nodding", r"capitulum[_ -]?angle"],
        "environment": [r"bio15", r"precipitation[_ -]?seasonality", r"rainfall[_ -]?seasonality"],
    },
    "colour_solar_exposure": {
        "trait": [r"colou?r", r"lightness", r"pigment", r"chroma", r"cielab", r"anthocyan"],
        "environment": [r"rsds", r"solar", r"shortwave", r"irradiance", r"radiation", r"uv[-_ ]?b?"],
    },
    "colour_temperature": {
        "trait": [r"colou?r", r"lightness", r"pigment", r"chroma", r"cielab", r"anthocyan"],
        "environment": [r"bio0?1", r"temperature", r"temp[_ -]?pc", r"thermal"],
    },
    "orientation_wind": {
        "trait": [r"orientation", r"head[_ -]?direction", r"nodding", r"capitulum[_ -]?angle"],
        "environment": [r"wind", r"sfcwind", r"wind[_ -]?exposure"],
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--azami-path", type=Path, action="append", default=[])
    p.add_argument("--azami-root", type=Path, default=Path("data/evidence/source"))
    p.add_argument("--eazami-ecology", type=Path, required=True)
    p.add_argument("--space-time-contract", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def question_hits(blob: str) -> list[str]:
    low = blob.casefold()
    hits = []
    for name, patterns in QUESTION_PATTERNS.items():
        trait_hit = any(re.search(p, low) for p in patterns["trait"])
        env_hit = any(re.search(p, low) for p in patterns["environment"])
        if trait_hit and env_hit:
            hits.append(name)
    return hits


def numeric_fields(record: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, value in record.items():
        if isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            out[str(key)] = number
    return out


def flatten_json(value: Any, prefix: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from flatten_json(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from flatten_json(child, f"{prefix}[{index}]")
    else:
        yield prefix, value


def audit_csv(path: Path) -> list[dict[str, Any]]:
    frame = pd.read_csv(path)
    out = []
    for index, row in frame.iterrows():
        record = {str(k): row[k] for k in frame.columns}
        blob = " | ".join(f"{k}={text(v)}" for k, v in record.items())
        for question in question_hits(blob):
            out.append(
                {
                    "question": question,
                    "source_file": str(path),
                    "source_type": "csv_row",
                    "source_locator": str(index + 2),
                    "record_text": blob,
                    "numeric_fields_json": json.dumps(numeric_fields(record), ensure_ascii=False, sort_keys=True),
                }
            )
    return out


def audit_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    leaves = list(flatten_json(payload))
    out = []
    # Search local path-value windows rather than the entire document so unrelated
    # trait and environment words cannot manufacture a candidate association.
    for index, (json_path, value) in enumerate(leaves):
        lo = max(0, index - 4)
        hi = min(len(leaves), index + 5)
        window = leaves[lo:hi]
        blob = " | ".join(f"{p}={text(v)}" for p, v in window)
        for question in question_hits(blob):
            local = {p: v for p, v in window}
            out.append(
                {
                    "question": question,
                    "source_file": str(path),
                    "source_type": "json_window",
                    "source_locator": json_path,
                    "record_text": blob,
                    "numeric_fields_json": json.dumps(numeric_fields(local), ensure_ascii=False, sort_keys=True),
                }
            )
    return out


def audit_text(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    for index, line in enumerate(lines):
        lo = max(0, index - 2)
        hi = min(len(lines), index + 3)
        blob = " | ".join(text(x) for x in lines[lo:hi])
        for question in question_hits(blob):
            out.append(
                {
                    "question": question,
                    "source_file": str(path),
                    "source_type": "text_window",
                    "source_locator": str(index + 1),
                    "record_text": blob,
                    "numeric_fields_json": "{}",
                }
            )
    return out


def collect_files(args: argparse.Namespace) -> list[Path]:
    paths = [p for p in args.azami_path if p.exists()]
    if args.azami_root.exists():
        for suffix in ("*.csv", "*.json", "*.md", "*.txt"):
            paths.extend(args.azami_root.rglob(suffix))
    # Preserve deterministic order and exact path identity.
    return sorted(set(p.resolve() for p in paths))


def eazami_summary(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    orientation = payload.get("orientation", {})
    axes = orientation.get("axes", {})
    if not axes:
        axes = {k: v for k, v in orientation.items() if str(k).startswith("chelsa_") and isinstance(v, dict)}
    return {
        "orientation_status": orientation.get("status"),
        "orientation_n_taxa": orientation.get("n_taxa"),
        "orientation_n_U": orientation.get("n_U"),
        "orientation_n_D": orientation.get("n_D"),
        "bio12_available": "chelsa_bio12" in axes,
        "bio15": axes.get("chelsa_bio15", orientation.get("chelsa_bio15", {})),
        "bio01": axes.get("chelsa_bio01", orientation.get("chelsa_bio01", {})),
        "phyllary_status": payload.get("phyllary_posture", {}).get("status"),
        "stickiness_status": payload.get("stickiness", {}).get("status"),
    }


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    contract = json.loads(args.space_time_contract.read_text(encoding="utf-8"))
    files = collect_files(args)
    candidate_rows: list[dict[str, Any]] = []
    unreadable: list[dict[str, str]] = []

    for path in files:
        try:
            if path.suffix.casefold() == ".csv":
                candidate_rows.extend(audit_csv(path))
            elif path.suffix.casefold() == ".json":
                candidate_rows.extend(audit_json(path))
            else:
                candidate_rows.extend(audit_text(path))
        except Exception as exc:
            unreadable.append({"source_file": str(path), "error": repr(exc)})

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        candidates = pd.DataFrame(
            columns=[
                "question",
                "source_file",
                "source_type",
                "source_locator",
                "record_text",
                "numeric_fields_json",
            ]
        )
    candidates = candidates.drop_duplicates().sort_values(
        ["question", "source_file", "source_locator"], kind="stable"
    )
    candidates.to_csv(args.out_dir / "chapter2_space_time_azami_candidate_records_v1.csv", index=False)

    counts = {question: int((candidates["question"] == question).sum()) for question in QUESTION_PATTERNS}
    sources = {
        question: sorted(candidates.loc[candidates["question"] == question, "source_file"].unique().tolist())
        for question in QUESTION_PATTERNS
    }
    eazami = eazami_summary(args.eazami_ecology)

    payload = {
        "contract_version": "chapter2_space_time_public_data_audit_v1",
        "source_contract": contract["contract_version"],
        "azami_files_scanned": len(files),
        "azami_candidate_counts": counts,
        "azami_candidate_source_files": sources,
        "unreadable_files": unreadable,
        "eazami_current_state": eazami,
        "provisional_cross_scale_status": {
            "orientation_precipitation": "domain_concordant_axis_distinct_pending_BIO12_BIO15_partition",
            "colour_solar": "pending_spatial_effect_admission_and_temporal_colour_coverage_audit",
        },
        "admission_rule": "A keyword candidate is not a result. A spatial effect enters the concordance ledger only after its estimand, sign, uncertainty, unit, data scale and source-bias controls are recovered from a structured source record or reproducible analysis.",
        "claim_boundary": "This audit locates evidence; it does not combine spatial and phylogenetic estimates or label any trait adaptive.",
    }
    (args.out_dir / "chapter2_space_time_public_data_audit_v1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
