#!/usr/bin/env python3
"""Exact-only source join: Moreyra nuclear samples x 20-tip orientation evidence.

The output audits SOURCE COVERAGE ONLY, not global orientation prevalence.
No synonym expansion, genus inference, image classifier labels, or phylogenetic
transition estimates are allowed at this gate.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def audit(source_parts: Path, orientation_path: Path):
    files = sorted(source_parts.glob("part_*.csv"))
    if len(files) != 8:
        raise ValueError("expected exactly eight frozen Moreyra source parts")
    source = [row for f in files for row in read_csv(f)]
    if not source or not set(["tree_code", "biosample", "sra_link_status", "scope_class"]).issubset(source[0]):
        raise ValueError("Moreyra source schema mismatch")
    used = [
        row for row in source if row["tree_code"].startswith("Cirsium")
        and row["sra_link_status"] == "linked_runinfo"
        and row["scope_class"] != "source_conflict_target_vs_outside"
    ]
    if len(used) < 20:
        raise ValueError("global nuclear source coverage has unexpectedly collapsed")
    biological_samples = {r["biosample"] for r in used}
    if "" in biological_samples:
        raise ValueError("unidentified BioSample in linked row")

    crosswalk = read_csv(orientation_path)
    if not crosswalk or not set(["accepted_taxon", "analysis_state", "source_basis", "source_url"]).issubset(crosswalk[0]):
        raise ValueError("orientation crosswalk schema mismatch")
    lookup = {}
    for row in crosswalk:
        if row["accepted_taxon"] in lookup:
            raise ValueError("duplicate orientation concept")
        if row["analysis_state"] not in {"U", "D", "?"}:
            raise ValueError("invalid orientation evidence state")
        lookup[row["accepted_taxon"]] = row
    labelled = defaultdict(list)
    for row in used:
        labelled[row["tree_code"]].append(row)

    result_rows = []
    for name in sorted(labelled):
        candidates = labelled[name]
        ev = lookup.get(name)
        if ev is None:
            status, resolved = "not_in_available_orientation_crosswalk", ""
        elif ev["analysis_state"] == "?":
            status, resolved = "explicitly_ambiguous_in_crosswalk", ""
        else:
            status, resolved = "exact_source_label_resolved_U_D", ev["analysis_state"]
        result_rows.append({
            "nuclear_tree_code": name,
            "moreyra_sample_rows": len(candidates),
            "biosamples": "|".join(sorted(set(x["biosample"] for x in candidates))),
            "region_classes": "|".join(sorted(set(x.get("region_class", "") for x in candidates))),
            "source_label_match": "yes" if ev else "no",
            "resolved_orientation": resolved,
            "join_status": status,
            "orientation_source_url": ev["source_url"] if ev else "",
            "orientation_source_basis": ev["source_basis"] if ev else "",
            "interpretation_limit": "exact label join, NOT accepted-taxonomy/same-voucher/global phenotype validation",
        })
    count = Counter(x["join_status"] for x in result_rows)
    resolved = [x for x in result_rows if x["resolved_orientation"] in {"U", "D"}]
    report = {
        "version": "moreyra_orientation_exact_source_overlap_audit_v1",
        "source": "eight frozen moreyra2025_cirsium_reconciliation_v1 parts and 20-tip East-Asian orientation crosswalk",
        "moreyra_linked_cirsium_rows": len(used),
        "moreyra_distinct_biosamples": len(biological_samples),
        "moreyra_distinct_tree_codes": len(labelled),
        "east_asia_orientation_crosswalk_rows": len(crosswalk),
        "exact_label_hits": sum(x["source_label_match"] == "yes" for x in result_rows),
        "exact_source_label_resolved_U_D": len(resolved),
        "resolved_U": sum(x["resolved_orientation"] == "U" for x in resolved),
        "resolved_D": sum(x["resolved_orientation"] == "D" for x in resolved),
        "exact_source_label_resolved_names": [
            {"tree_code": x["nuclear_tree_code"], "state": x["resolved_orientation"]} for x in resolved
        ],
        "exact_but_ambiguous_names": [
            x["nuclear_tree_code"] for x in result_rows if x["join_status"] == "explicitly_ambiguous_in_crosswalk"
        ],
        "missing_crosswalk_state": count["not_in_available_orientation_crosswalk"],
        "can_execute_global_nuclear_U_D_climate_analysis": False,
        "claim_limit": (
            "Exact overlap with a 20-tip East-Asian source is only a lower bound on "
            "available source-supported global orientation. Unmatched labels are NOT "
            "biologically U or D or global trait-data absence. Species synonymy and "
            "nuclear-tip/source-taxonomy crosswalk remain separate gates. No global "
            "tree ensemble or climate join was available at this audit."
        ),
    }
    return report, result_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-parts", type=Path, default=Path("data/evidence/moreyra2025_cirsium_reconciliation_v1"))
    parser.add_argument("--orientation", type=Path, default=Path("data/evidence/orientation_comp1061_20tip_source_crosswalk_v1.csv"))
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    report, rows = audit(args.source_parts, args.orientation)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (args.outdir / "source_overlap.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
