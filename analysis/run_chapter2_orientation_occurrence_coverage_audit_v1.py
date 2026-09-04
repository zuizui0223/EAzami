#!/usr/bin/env python3
"""Audit orientation occurrence coverage at frozen n>=10/5/3 gates.

Uses only already-frozen thinned, environment-complete occurrence artifacts.
No new occurrence source, taxon alias or environmental variable is introduced.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if contract["version"] != "chapter2_orientation_occurrence_coverage_audit_contract_v1":
        raise AssertionError("contract version drift")

    cross = pd.read_csv(args.orientation)
    cross = cross[cross["analysis_state"].isin(["U", "D"])].copy()
    states = dict(zip(cross["accepted_taxon"], cross["analysis_state"]))

    jp = pd.read_csv(args.japan_occurrences).assign(source_region="JP")
    tw = pd.read_csv(args.taiwan_occurrences).assign(source_region="TW")
    occ = pd.concat([jp, tw], ignore_index=True)

    counts = occ.groupby("scientific_name_query").size().to_dict()
    region_map = occ.groupby("scientific_name_query")["source_region"].agg(lambda x: "+".join(sorted(set(x)))).to_dict()

    rows = []
    for taxon in sorted(states):
        n = int(counts.get(taxon, 0))
        rows.append({
            "taxon": taxon,
            "state": states[taxon],
            "occurrence_n": n,
            "source_region": region_map.get(taxon, "none"),
            "eligible_n10": n >= 10,
            "eligible_n5": n >= 5,
            "eligible_n3": n >= 3,
        })
    df = pd.DataFrame(rows)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)

    summaries = {}
    n10_taxa = set(df.loc[df["eligible_n10"], "taxon"])
    for threshold in contract["thresholds"]:
        col = f"eligible_n{threshold}"
        g = df[df[col]].copy()
        state_counts = g["state"].value_counts().to_dict()
        added = sorted(set(g["taxon"]) - n10_taxa)
        rule = contract["secondary_model_evaluability_rule"]
        evaluable = (
            len(g) >= rule["minimum_total_taxa"]
            and int(state_counts.get("U", 0)) >= rule["minimum_taxa_per_state"]
            and int(state_counts.get("D", 0)) >= rule["minimum_taxa_per_state"]
            and (threshold == 10 or bool(added))
        )
        summaries[str(threshold)] = {
            "n_taxa": int(len(g)),
            "n_U": int(state_counts.get("U", 0)),
            "n_D": int(state_counts.get("D", 0)),
            "taxa": g["taxon"].tolist(),
            "added_vs_n10": added,
            "secondary_specificity_sensitivity_evaluable": bool(evaluable if threshold != 10 else False),
        }

    relaxed = [k for k in ("5", "3") if summaries[k]["secondary_specificity_sensitivity_evaluable"]]
    if relaxed:
        classification = "relaxed_existing_coverage_materially_expands_state_diverse_panel"
    else:
        classification = "relaxed_existing_coverage_does_not_enable_meaningful_specificity_expansion"

    payload = {
        "version": "chapter2_orientation_occurrence_coverage_audit_result_v1",
        "classification": classification,
        "threshold_summaries": summaries,
        "taxa_with_any_frozen_occurrences": int((df["occurrence_n"] > 0).sum()),
        "resolved_orientation_taxa_in_crosswalk": int(len(df)),
        "zero_occurrence_taxa": df.loc[df["occurrence_n"] == 0, "taxon"].tolist(),
        "interpretation_boundary": contract["claim_ceiling"],
    }
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
