#!/usr/bin/env python3
"""Extract the de-geolocated fixed environment design for Azami-compatible v3 simulations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

PREDICTORS = [
    "chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15",
    "chelsa_rsds_mean", "chelsa_vpd_mean", "chelsa_sfcwind_mean", "chelsa_gsp", "chelsa_npp",
]
EXPECTED_SOURCE_SHA256 = "1ab84254a80493776b4c435152ed3d2a1c1e68dd0e0342da0ea081eeb5cd3d9b"
EXPECTED_DERIVED_SHA256 = "b3a01ff795f6a88f1290576be5b161119bb342c67b498fd9fa76770d419b408d"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(source: Path, out: Path) -> dict:
    source_hash = sha256(source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"source environment file SHA256 mismatch: {source_hash}")
    df = pd.read_csv(source, low_memory=False)
    required = ["obs_id", "taxon_name", "latitude", "longitude", *PREDICTORS]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"source environment design missing columns: {missing}")
    if len(df) != 1874 or df["taxon_name"].nunique() != 124:
        raise RuntimeError("unexpected complete18 environment design dimensions")
    if df[PREDICTORS].apply(pd.to_numeric, errors="coerce").isna().any().any():
        raise RuntimeError("frozen complete18 design must have finite values for all nine predictors")
    counts = df.groupby("taxon_name").size()
    if int((counts >= 5).sum()) != 42 or int((counts >= 2).sum()) != 75:
        raise RuntimeError("taxon threshold counts drifted from frozen Azami design")
    design = df[["taxon_name", *PREDICTORS]].copy()
    design.insert(0, "design_row_id", [f"AZ72_{i:04d}" for i in range(len(design))])
    out.parent.mkdir(parents=True, exist_ok=True)
    design.to_csv(out, index=False)
    derived_hash = sha256(out)
    if derived_hash != EXPECTED_DERIVED_SHA256:
        raise RuntimeError(f"derived environment design SHA256 mismatch: {derived_hash}")
    return {
        "status": "frozen_environment_design_extracted",
        "source_sha256": source_hash,
        "derived_sha256": derived_hash,
        "rows": len(design),
        "taxa": int(design["taxon_name"].nunique()),
        "taxa_min5": int((counts >= 5).sum()),
        "taxa_min2": int((counts >= 2).sum()),
        "coordinates_removed": True,
        "original_obs_id_removed": True,
        "predictors": PREDICTORS,
        "claim_boundary": "Fixed exogenous environmental design only; no observed response phenotype enters the v3 generator.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--report", type=Path)
    a = p.parse_args()
    report = extract(a.source, a.out)
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
