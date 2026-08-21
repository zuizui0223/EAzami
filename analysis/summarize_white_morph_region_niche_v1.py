#!/usr/bin/env python3
"""Aggregate white-morph public occurrences to region x parent-niche-cluster evidence.

Exact coordinates remain in the workflow artifact for reproducibility but are not used as
collection sites. The repository-facing decision layer uses region and cluster only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--morph-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def clean_region(value: object) -> str:
    text = " ".join(str(value or "").split())
    return text if text and text.lower() != "nan" else "region_not_reported"


def main():
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.morph_dir / "white_morph_occurrences_projected.csv"
    occ = pd.read_csv(path)
    if occ.empty or "parent_taxon" not in occ.columns:
        region = pd.DataFrame(columns=["parent_taxon","morph_class","stateProvince","parent_niche_cluster","n_records"])
    else:
        occ["stateProvince"] = occ["stateProvince"].map(clean_region)
        region = (
            occ.groupby(["parent_taxon","morph_class","stateProvince","parent_niche_cluster"], dropna=False)
            .agg(n_records=("gbif_key", "nunique"))
            .reset_index()
            .sort_values(["parent_taxon","n_records","stateProvince"], ascending=[True,False,True])
        )
    region.to_csv(args.out_dir / "white_morph_region_niche_summary.csv", index=False)

    pend = region.loc[region["parent_taxon"].eq("Cirsium pendulum")]
    sieb = region.loc[region["parent_taxon"].eq("Cirsium sieboldii")]
    pend_clusters = sorted({int(x) for x in pend["parent_niche_cluster"].dropna()}) if len(pend) else []
    pend_regions = sorted(set(pend["stateProvince"])) if len(pend) else []
    sieb_clusters = sorted({int(x) for x in sieb["parent_niche_cluster"].dropna()}) if len(sieb) else []

    decision = {
        "contract_version": "white_morph_region_niche_summary_v1",
        "pendulum": {
            "regions_with_exact_form_records": pend_regions,
            "parent_niche_clusters": pend_clusters,
            "design_implication": (
                "Use the two existing white slots P009/P010 to capture different verified white-morph niche contexts where feasible; pair coloured P011/P012 only where flowering periods overlap."
                if len(pend_clusters) >= 2
                else "Public exact-form coverage is insufficient to stratify both white slots by niche context."
            ),
            "new_population_addition": 0,
        },
        "sieboldii": {
            "regions_with_exact_form_records": sorted(set(sieb["stateProvince"])) if len(sieb) else [],
            "parent_niche_clusters": sieb_clusters,
            "design_implication": "Keep the second W/C pair (+30 individuals) conditional and untriggered until a verified white-morph locality can be placed relative to P013/P014.",
            "new_population_addition": 0,
        },
        "global_decision": "refine_existing_slots_before_adding_new_populations",
    }
    (args.out_dir / "white_morph_region_niche_decision_v1.json").write_text(
        json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
