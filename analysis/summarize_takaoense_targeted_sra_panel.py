#!/usr/bin/env python3
"""Aggregate six targeted SRA-BLAST summaries without differential-expression claims."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="data/evidence/takaoense_dfr_ans_targeted_sra_panel_v1.csv")
    ap.add_argument("--summary-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with Path(args.panel).open(encoding="utf-8-sig", newline="") as h:
        panel = list(csv.DictReader(h))
    if len(panel) != 6 or Counter(r["morph"] for r in panel) != Counter({"W": 3, "BP": 3}):
        raise ValueError("frozen 3W/3BP panel drift")
    if len({r["run"] for r in panel}) != 6 or len({r["sample_id"] for r in panel}) != 6:
        raise ValueError("duplicate sample/run in targeted panel")

    rows = []
    detect_by_query_morph = defaultdict(lambda: Counter())
    for r in panel:
        p = Path(args.summary_dir) / f"{r['sample_id']}_dfr_ans_vdb_summary.json"
        if not p.exists():
            raise FileNotFoundError(p)
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("contract_version") != "targeted_takaoense_sra_vdb_screen_v1":
            raise ValueError(f"summary contract drift: {p}")
        if (d["sample_id"], d["run"], d["morph"]) != (r["sample_id"], r["run"], r["morph"]):
            raise ValueError(f"sample identity drift: {p}")
        row = {
            "sample_id": r["sample_id"],
            "morph": r["morph"],
            "run": r["run"],
            "queries_detected": d["detected_queries"],
            "DFR_detected": d["queries"]["CNIP_DFR"]["detected_under_screen"],
            "ANS_detected": d["queries"]["CNIP_ANS"]["detected_under_screen"],
            "DFR_alignment_rows": d["queries"]["CNIP_DFR"]["alignment_rows"],
            "ANS_alignment_rows": d["queries"]["CNIP_ANS"]["alignment_rows"],
            "DFR_best_pident": d["queries"]["CNIP_DFR"].get("best_pident"),
            "ANS_best_pident": d["queries"]["CNIP_ANS"].get("best_pident"),
            "DFR_best_local_qcov": d["queries"]["CNIP_DFR"].get("best_query_local_coverage"),
            "ANS_best_local_qcov": d["queries"]["CNIP_ANS"].get("best_query_local_coverage"),
        }
        rows.append(row)
        for q, key in [("DFR", "CNIP_DFR"), ("ANS", "CNIP_ANS")]:
            if d["queries"][key]["detected_under_screen"]:
                detect_by_query_morph[q][r["morph"]] += 1

    result = {
        "contract_version": "takaoense_targeted_dfr_ans_sra_panel_v1",
        "samples": len(rows),
        "morph_counts": dict(sorted(Counter(r["morph"] for r in rows).items())),
        "sample_results": rows,
        "detected_samples_by_query_and_morph": {
            q: {m: detect_by_query_morph[q].get(m, 0) for m in ["W", "BP"]}
            for q in ["DFR", "ANS"]
        },
        "intended_use": "assay-level targeted recoverability and alignment-quality audit before targeted coding/genealogy recovery",
        "forbidden_use": [
            "differential expression inference from raw hit counts",
            "flower-specific expression inference from young-leaf RNA",
            "gene absence from a run with no detected read",
            "causal white-versus-coloured mechanism inference",
        ],
        "next_gate": "If both DFR and ANS are recoverable across enough runs, use a targeted read-recovery/alignment method with explicit depth/quality and orthology controls to reconstruct coding haplotypes; keep expression and floral mechanism as separate assays.",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
