#!/usr/bin/env python3
"""Materialize the frozen Moreyra Cirsium reconciliation from repo shards.

The source Actions artifact is time-limited.  This helper validates the compact
repository copy against its manifest and recreates one ordinary CSV for the
existing Japan-origin v2 panel builder.  It does not redo NCBI/source recovery.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

DEFAULT_SOURCE = Path("data/evidence/moreyra2025_cirsium_reconciliation_v1")
EXPECTED_CONTRACT = "moreyra2025_cirsium_reconciliation_v1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_part(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    if not fields or not rows:
        raise ValueError(f"empty reconciliation shard: {path}")
    return fields, rows


def materialize(source: Path, output: Path) -> dict[str, object]:
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("contract_version") != EXPECTED_CONTRACT:
        raise ValueError("unexpected Moreyra reconciliation contract")
    expected_fields = list(manifest.get("columns") or [])
    if not expected_fields:
        raise ValueError("manifest columns missing")
    expected_parts = manifest.get("parts")
    if not isinstance(expected_parts, list) or not expected_parts:
        raise ValueError("manifest parts missing")

    all_rows: list[dict[str, str]] = []
    observed_files = {p.name for p in source.glob("part_*.csv")}
    declared_files = {str(item["file"]) for item in expected_parts}
    if observed_files != declared_files:
        raise ValueError(
            f"reconciliation shard set drift: missing={sorted(declared_files-observed_files)} "
            f"extra={sorted(observed_files-declared_files)}"
        )

    for item in expected_parts:
        path = source / str(item["file"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"SHA256 drift for {path}")
        fields, rows = read_part(path)
        if fields != expected_fields:
            raise ValueError(f"column drift for {path}")
        if len(rows) != int(item["rows"]):
            raise ValueError(f"row-count drift for {path}")
        all_rows.extend(rows)

    if len(all_rows) != int(manifest["rows"]):
        raise ValueError("total frozen reconciliation row count drift")
    if any(not row["tree_code"].startswith("Cirsium") for row in all_rows):
        raise ValueError("non-Cirsium row leaked into compact reconciliation")
    if any(row["sra_link_status"] != "linked_runinfo" for row in all_rows):
        raise ValueError("unlinked row leaked into compact reconciliation")
    conflicts = [r for r in all_rows if r["scope_class"] == "source_conflict_target_vs_outside"]
    if len(conflicts) != 1 or conflicts[0]["tree_code"] != "Cirsium yuki-uenoanum":
        raise ValueError("expected preserved source-conflict row is missing/drifted")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=expected_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)
    observed_sha = sha256(output)
    expected_sha = str(manifest["combined_canonical_csv_sha256"])
    if observed_sha != expected_sha:
        raise ValueError(
            f"materialized canonical CSV hash drift: {observed_sha} != {expected_sha}"
        )
    return {
        "contract_version": EXPECTED_CONTRACT,
        "rows": len(all_rows),
        "parts": len(expected_parts),
        "sha256": observed_sha,
        "source_artifact_id": manifest["source_artifact_id"],
        "source_workflow_run": manifest["source_workflow_run"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = materialize(args.source, args.output)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
