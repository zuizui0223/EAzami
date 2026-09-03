#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def read_bridge(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 4:
        raise ValueError(f"expected four orientation rows, got {len(rows)}")
    out = {row["predictor"]: row for row in rows}
    expected = {"chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15"}
    if set(out) != expected:
        raise ValueError(f"predictor set changed: {sorted(out)}")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bridge", type=Path, required=True)
    p.add_argument("--result", type=Path, required=True)
    args = p.parse_args()
    bridge = read_bridge(args.bridge)
    result = json.loads(args.result.read_text(encoding="utf-8"))

    b12 = bridge["chelsa_bio12"]
    assert float(b12["beta_std_within"]) == result["orientation_scale_partition"]["BIO12_annual_precipitation"]["azami_within"]["beta_std"]
    assert float(b12["beta_std_among"]) == result["orientation_scale_partition"]["BIO12_annual_precipitation"]["azami_among"]["beta_std"]
    assert not as_bool(b12["within_fdr_significant_0_05"])
    assert as_bool(b12["among_fdr_significant_0_05"])
    assert b12["cross_scale_class"] == "among_only"

    b15 = bridge["chelsa_bio15"]
    assert float(b15["beta_std_within"]) < 0
    assert not as_bool(b15["within_fdr_significant_0_05"])
    assert not as_bool(b15["among_fdr_significant_0_05"])

    b1 = bridge["chelsa_bio01"]
    assert float(b1["beta_std_within"]) > 0
    assert as_bool(b1["within_fdr_significant_0_05"])
    assert not as_bool(b1["among_fdr_significant_0_05"])
    assert b1["cross_scale_class"] == "within_only"

    assert result["classification"] == "orientation_environment_association_is_scale_partitioned"
    print(json.dumps({
        "classification": result["classification"],
        "BIO12": {
            "within_beta": float(b12["beta_std_within"]),
            "within_q": float(b12["q_fdr_bh_within"]),
            "among_beta": float(b12["beta_std_among"]),
            "among_q": float(b12["q_fdr_bh_among"]),
            "cross_scale_class": b12["cross_scale_class"],
        },
        "BIO15": {
            "within_beta": float(b15["beta_std_within"]),
            "within_q": float(b15["q_fdr_bh_within"]),
            "among_beta": float(b15["beta_std_among"]),
            "among_q": float(b15["q_fdr_bh_among"]),
        },
        "BIO1": {
            "within_beta": float(b1["beta_std_within"]),
            "within_q": float(b1["q_fdr_bh_within"]),
            "among_beta": float(b1["beta_std_among"]),
            "among_q": float(b1["q_fdr_bh_among"]),
            "cross_scale_class": b1["cross_scale_class"],
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
