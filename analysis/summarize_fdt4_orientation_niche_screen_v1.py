#!/usr/bin/env python3
"""Descriptive orientation × present-day niche screen for FDT4 Phase 1.

This deliberately does NOT fit a phylogenetic association model. It converts the
live GBIF+CHELSA occurrence output to one centroid per taxon, joins the frozen
orientation state, and ranks environmental axes by the absolute U-vs-D centroid
contrast. The output is only a candidate-axis screen for the later branch-wise
phylogenetic/niche-history analysis.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--occurrences", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def normalize_tip(taxon: str) -> str:
    return taxon.replace(" ", "_").replace(".", "")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    occ = pd.read_csv(args.occurrences)
    orient = pd.read_csv(args.orientation)
    orient = orient.loc[orient["analysis_state"].isin(["U", "D"])].copy()
    state_by_taxon = dict(zip(orient["accepted_taxon"], orient["analysis_state"]))

    env_cols = [c for c in ["chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15", "PC1", "PC2", "PC3"] if c in occ.columns]
    if not env_cols:
        raise SystemExit("No expected CHELSA/PCA columns found")

    centroids = occ.groupby("scientific_name_query", as_index=False)[env_cols].mean()
    centroids["orientation_state"] = centroids["scientific_name_query"].map(state_by_taxon)
    centroids = centroids.loc[centroids["orientation_state"].isin(["U", "D"])].copy()
    centroids.to_csv(args.out_dir / "fdt4_japan_orientation_taxon_niche_centroids_v1.csv", index=False)

    contrasts = []
    for col in env_cols:
        u = centroids.loc[centroids.orientation_state.eq("U"), col].dropna().astype(float)
        d = centroids.loc[centroids.orientation_state.eq("D"), col].dropna().astype(float)
        if len(u) < 2 or len(d) < 2:
            continue
        pooled = np.concatenate([u.to_numpy(), d.to_numpy()])
        sd = float(np.std(pooled, ddof=1)) if len(pooled) > 1 else float("nan")
        delta = float(d.mean() - u.mean())
        zdelta = delta / sd if np.isfinite(sd) and sd > 0 else float("nan")
        contrasts.append({
            "axis": col,
            "n_U_taxa": int(len(u)),
            "n_D_taxa": int(len(d)),
            "mean_U": float(u.mean()),
            "mean_D": float(d.mean()),
            "D_minus_U": delta,
            "standardized_centroid_difference": zdelta,
            "absolute_standardized_difference": abs(zdelta) if np.isfinite(zdelta) else None,
            "claim_scope": "descriptive_tip_centroid_screen_not_phylogenetically_corrected"
        })
    contrasts.sort(key=lambda x: -1 if x["absolute_standardized_difference"] is None else -x["absolute_standardized_difference"])
    with (args.out_dir / "fdt4_japan_orientation_niche_axis_screen_v1.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(contrasts[0].keys()) if contrasts else ["axis"])
        writer.writeheader()
        writer.writerows(contrasts)

    result = {
        "contract_version": "fdt4_japan_orientation_niche_screen_v1",
        "taxa_joined": int(len(centroids)),
        "upward_taxa": int(centroids.orientation_state.eq("U").sum()),
        "downward_taxa": int(centroids.orientation_state.eq("D").sum()),
        "axes_screened": [x["axis"] for x in contrasts],
        "ranked_axes": contrasts,
        "decision": "Use the ranked axes only to prioritize later phylogenetic branch-wise niche-shift tests; do not interpret the uncorrected tip-centroid contrast as adaptation or evolutionary coupling."
    }
    (args.out_dir / "fdt4_japan_orientation_niche_screen_v1.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")


if __name__ == "__main__":
    main()
