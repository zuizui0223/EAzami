#!/usr/bin/env python3
"""Inventory and selectively recover reusable public Azami GitHub Actions artifacts.

The inventory covers every currently non-expired artifact returned by GitHub. A
bounded download plan then prioritizes artifacts whose names indicate trait,
environment, spatial, continuous-phenotype or result content. Large raw-image,
model-weight and cache artifacts are inventoried but not downloaded. Extracted
content is restricted to analysis-friendly file types and is never interpreted as
an admitted dataset until the downstream schema/provenance audit passes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

POSITIVE = {
    "orientation": 8,
    "head-direction": 8,
    "head_direction": 8,
    "phenotype": 7,
    "trait": 6,
    "continuous": 6,
    "all-continuous": 9,
    "environment": 7,
    "climate": 5,
    "bio12": 10,
    "bio15": 10,
    "rsds": 10,
    "solar": 10,
    "radiation": 7,
    "colour": 8,
    "color": 8,
    "pigment": 8,
    "lightness": 7,
    "chroma": 7,
    "spatial": 6,
    "global-cirsium": 7,
    "global_cirsium": 7,
    "result": 4,
    "evidence": 4,
    "analysis": 3,
    "figure": 2,
    "data": 2,
}
NEGATIVE = {
    "raw-image": -20,
    "raw_image": -20,
    "images": -12,
    "weights": -15,
    "checkpoint": -15,
    "model-cache": -15,
    "model_cache": -15,
    "docker": -15,
    "cache": -8,
    "node-modules": -20,
}
TEXT_EXT = {
    ".csv", ".tsv", ".json", ".jsonl", ".parquet", ".feather", ".xlsx",
    ".xls", ".rds", ".rda", ".rdata", ".md", ".txt", ".nwk", ".tree",
    ".tre", ".newick", ".r", ".py", ".yml", ".yaml", ".toml",
}
MAX_MEMBER_BYTES = 300 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repository", default="zuizui0223/azami")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--token-env", default="GH_TOKEN")
    p.add_argument("--max-total-mb", type=float, default=1200.0)
    p.add_argument("--max-artifact-mb", type=float, default=300.0)
    p.add_argument("--min-score", type=int, default=2)
    p.add_argument("--max-artifacts", type=int, default=40)
    return p.parse_args()


def score(name: str) -> tuple[int, list[str]]:
    low = name.casefold()
    hits: list[str] = []
    value = 0
    for term, weight in POSITIVE.items():
        if term in low:
            value += weight
            hits.append(f"+{term}:{weight}")
    for term, weight in NEGATIVE.items():
        if term in low:
            value += weight
            hits.append(f"{term}:{weight}")
    return value, hits


def get_all_artifacts(session: requests.Session, repository: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repository}/actions/artifacts"
        response = session.get(url, params={"per_page": 100, "page": page}, timeout=60)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("artifacts", [])
        if not isinstance(rows, list):
            raise RuntimeError("GitHub artifacts response has no list")
        out.extend(x for x in rows if isinstance(x, dict))
        if len(rows) < 100:
            break
        page += 1
        if page > 100:
            raise RuntimeError("artifact pagination exceeded safety bound")
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_member(member: zipfile.ZipInfo) -> bool:
    path = Path(member.filename)
    if member.is_dir() or member.file_size > MAX_MEMBER_BYTES:
        return False
    if path.is_absolute() or ".." in path.parts:
        return False
    return path.suffix.casefold() in TEXT_EXT


def download(session: requests.Session, repository: str, artifact_id: int, dest: Path) -> None:
    url = f"https://api.github.com/repos/{repository}/actions/artifacts/{artifact_id}/zip"
    with session.get(url, stream=True, timeout=120, allow_redirects=True) as response:
        response.raise_for_status()
        with dest.open("wb") as out:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    out.write(chunk)


def main() -> int:
    a = parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    token = os.environ.get(a.token_env, "").strip()
    session = requests.Session()
    session.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "EAzami-public-artifact-audit/1.0",
    })
    if token:
        session.headers["Authorization"] = f"Bearer {token}"

    artifacts = get_all_artifacts(session, a.repository)
    inventory: list[dict[str, Any]] = []
    for item in artifacts:
        name = str(item.get("name", ""))
        value, hits = score(name)
        run = item.get("workflow_run") if isinstance(item.get("workflow_run"), dict) else {}
        inventory.append({
            "artifact_id": int(item.get("id")),
            "name": name,
            "size_bytes": int(item.get("size_in_bytes") or 0),
            "size_mb": float(item.get("size_in_bytes") or 0) / 1024 / 1024,
            "expired": bool(item.get("expired")),
            "created_at": str(item.get("created_at", "")),
            "expires_at": str(item.get("expires_at", "")),
            "digest": str(item.get("digest", "")),
            "workflow_run_id": run.get("id"),
            "head_branch": run.get("head_branch"),
            "head_sha": run.get("head_sha"),
            "relevance_score": value,
            "score_terms": " | ".join(hits),
        })

    inventory.sort(key=lambda x: (x["expired"], -x["relevance_score"], -x["artifact_id"]))
    with (a.out_dir / "azami_public_artifact_inventory_v1.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(inventory[0]) if inventory else ["artifact_id"])
        writer.writeheader()
        writer.writerows(inventory)

    max_total = int(a.max_total_mb * 1024 * 1024)
    max_one = int(a.max_artifact_mb * 1024 * 1024)
    selected: list[dict[str, Any]] = []
    used = 0
    for item in inventory:
        size = int(item["size_bytes"])
        if item["expired"] or item["relevance_score"] < a.min_score or size > max_one:
            continue
        if len(selected) >= a.max_artifacts or used + size > max_total:
            continue
        selected.append(item)
        used += size

    extracted_root = a.out_dir / "extracted"
    downloads = a.out_dir / "downloads"
    extracted_root.mkdir(exist_ok=True)
    downloads.mkdir(exist_ok=True)
    extraction_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for item in selected:
        aid = int(item["artifact_id"])
        zip_path = downloads / f"{aid}.zip"
        try:
            download(session, a.repository, aid, zip_path)
            archive_sha = sha256(zip_path)
            target = extracted_root / f"artifact_{aid}__{re.sub(r'[^A-Za-z0-9._-]+', '_', item['name'])}"
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path) as zf:
                for member in zf.infolist():
                    if not safe_member(member):
                        continue
                    rel = Path(member.filename)
                    out = target / rel
                    out.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, out.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
                    extraction_rows.append({
                        "artifact_id": aid,
                        "artifact_name": item["name"],
                        "workflow_run_id": item["workflow_run_id"],
                        "head_sha": item["head_sha"],
                        "archive_sha256": archive_sha,
                        "member_path": member.filename,
                        "member_size_bytes": member.file_size,
                        "extracted_path": str(out.relative_to(a.out_dir)),
                        "member_sha256": sha256(out),
                    })
        except Exception as exc:
            failures.append({"artifact_id": aid, "name": item["name"], "error": f"{type(exc).__name__}: {exc}"})
        finally:
            zip_path.unlink(missing_ok=True)

    fields = [
        "artifact_id", "artifact_name", "workflow_run_id", "head_sha", "archive_sha256",
        "member_path", "member_size_bytes", "extracted_path", "member_sha256",
    ]
    with (a.out_dir / "azami_public_artifact_extraction_manifest_v1.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(extraction_rows)

    payload = {
        "contract_version": "azami_public_artifact_inventory_v1",
        "status_date_utc": datetime.now(timezone.utc).isoformat(),
        "repository": a.repository,
        "all_artifacts_inventory_count": len(inventory),
        "nonexpired_count": sum(not x["expired"] for x in inventory),
        "selection_contract": {
            "min_relevance_score": a.min_score,
            "max_total_mb": a.max_total_mb,
            "max_artifact_mb": a.max_artifact_mb,
            "max_artifacts": a.max_artifacts,
            "large_raw_image_model_and_cache_artifacts": "inventoried_but_not_downloaded",
        },
        "selected_artifacts": selected,
        "selected_total_mb": used / 1024 / 1024,
        "successfully_extracted_artifact_ids": sorted({x["artifact_id"] for x in extraction_rows}),
        "extracted_analysis_files": len(extraction_rows),
        "failures": failures,
        "claim_boundary": "Artifact-name relevance is a recovery rule, not scientific admission. Downstream schema, provenance, duplicate and model-contract checks are required before any extracted file can support a result.",
    }
    (a.out_dir / "azami_public_artifact_inventory_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "inventory": len(inventory), "selected": len(selected), "selected_mb": round(used / 1024 / 1024, 3),
        "extracted_files": len(extraction_rows), "failures": len(failures),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
