#!/usr/bin/env python3
"""Public sea-level process sensitivity for the dated Taiwan orientation branch.

Sea level is treated only as a range-reorganization/exposure-opportunity axis.
No local land-bridge threshold is assumed and no sea-level statistic is treated
as a selective pressure on capitulum orientation.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import numpy as np
import pandas as pd

YOUNG_KA = 470.0
OLD_KA = 790.0
WIDTH_KA = OLD_KA - YOUNG_KA


def load_noaa(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line.startswith("age_calkaBP\t"))
    text = "\n".join(lines[header_i:])
    df = pd.read_csv(io.StringIO(text), sep="\t")
    df["age_calkaBP"] = pd.to_numeric(df["age_calkaBP"], errors="coerce")
    df["SeaLev_longPC1"] = pd.to_numeric(df["SeaLev_longPC1"], errors="coerce")
    return df.dropna(subset=["age_calkaBP", "SeaLev_longPC1"]).sort_values("age_calkaBP").reset_index(drop=True)


def stats(df: pd.DataFrame, young: float, old: float) -> dict:
    w = df[(df.age_calkaBP >= young) & (df.age_calkaBP <= old)].copy()
    if len(w) < 250:
        raise ValueError(f"insufficient points in {young}-{old} ka: {len(w)}")
    y = w.SeaLev_longPC1.to_numpy(float)
    return {
        "young_ka": float(young),
        "old_ka": float(old),
        "n_points": int(len(y)),
        "mean_m": float(np.mean(y)),
        "sd_m": float(np.std(y, ddof=1)),
        "range_m": float(np.max(y) - np.min(y)),
        "minimum_m": float(np.min(y)),
        "maximum_m": float(np.max(y)),
        "mean_abs_1k_change_m": float(np.mean(np.abs(np.diff(y)))),
        "max_abs_1k_change_m": float(np.max(np.abs(np.diff(y)))),
        "endpoint_abs_change_m": float(abs(y[-1] - y[0])),
    }


def percentile(vals, obs):
    vals = np.asarray(vals, float)
    return float((np.sum(vals <= obs) + 0.5) / (len(vals) + 1.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--noaa", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    df = load_noaa(args.noaa)
    if float(df.age_calkaBP.max()) < OLD_KA:
        raise ValueError("NOAA long stack does not cover event window")
    obs = stats(df, YOUNG_KA, OLD_KA)
    max_start = float(df.age_calkaBP.max()) - WIDTH_KA
    starts = np.arange(0.0, max_start + 1e-9, 1.0)
    null = [stats(df, float(s), float(s + WIDTH_KA)) for s in starts]
    keys = ["sd_m", "range_m", "mean_abs_1k_change_m", "max_abs_1k_change_m", "endpoint_abs_change_m"]
    pcts = {k: percentile([x[k] for x in null], obs[k]) for k in keys}
    result = {
        "contract_version": "chapter2_taiwan_orientation_sealevel_process_v1",
        "event_window_ma": [0.47, 0.79],
        "source": {
            "dataset": "Spratt and Lisiecki 2016 global sea-level stack",
            "dataset_doi": "10.25921/rd66-5820",
            "publication_doi": "10.5194/cp-12-1079-2016",
            "series": "SeaLev_longPC1",
            "coverage_ka": [0, 798],
        },
        "estimand_role": "generic sea-level-driven range-reorganization opportunity; not local connectivity and not selection",
        "event_window": obs,
        "duration_matched_percentiles": pcts,
        "n_matched_windows": int(len(null)),
        "decision_rule": "Report magnitude/variability percentiles descriptively. No land-bridge or fragmentation claim without an independently sourced local bathymetric/geological threshold.",
        "claim_boundary": [
            "global sea level is not a local Ryukyu/Taiwan connectivity model",
            "sea-level variability is an exposure-opportunity context, not a selective agent",
            "overlapping duration-matched windows are a descriptive temporal reference, not independent replicates",
            "one dated orientation branch cannot identify a general distribution-trigger mechanism",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
