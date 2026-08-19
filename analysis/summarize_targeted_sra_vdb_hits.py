#!/usr/bin/env python3
"""Summarize targeted tblastn_vdb hits without treating read counts as expression."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

FIELDS = [
    "qseqid", "sseqid", "pident", "length", "qlen", "slen",
    "qstart", "qend", "sstart", "send", "evalue", "bitscore",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--sample-id", required=True)
    ap.add_argument("--morph", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    hits = []
    p = Path(args.hits)
    if p.exists() and p.stat().st_size:
        with p.open(encoding="utf-8", newline="") as h:
            for row in csv.DictReader(h, delimiter="\t", fieldnames=FIELDS):
                x = dict(row)
                for k in ["pident", "length", "qlen", "slen", "qstart", "qend", "sstart", "send", "evalue", "bitscore"]:
                    x[k] = float(x[k])
                x["qcov_local"] = (abs(x["qend"] - x["qstart"]) + 1) / x["qlen"] if x["qlen"] else 0
                hits.append(x)

    byq = defaultdict(list)
    for x in hits:
        q = x["qseqid"].split("|", 1)[0]
        byq[q].append(x)

    queries = {}
    for q in ["CNIP_DFR", "CNIP_ANS"]:
        hh = byq.get(q, [])
        hh.sort(key=lambda x: (-x["bitscore"], x["evalue"], -x["pident"]))
        if hh:
            best = hh[0]
            queries[q] = {
                "alignment_rows": len(hh),
                "unique_subject_read_ids": len({x["sseqid"] for x in hh}),
                "best_pident": best["pident"],
                "best_aligned_aa": int(best["length"]),
                "best_query_local_coverage": best["qcov_local"],
                "best_evalue": best["evalue"],
                "best_bitscore": best["bitscore"],
                "detected_under_screen": True,
            }
        else:
            queries[q] = {
                "alignment_rows": 0,
                "unique_subject_read_ids": 0,
                "detected_under_screen": False,
            }

    result = {
        "contract_version": "targeted_takaoense_sra_vdb_screen_v1",
        "sample_id": args.sample_id,
        "run": args.run,
        "morph": args.morph,
        "queries": queries,
        "total_alignment_rows": len(hits),
        "detected_queries": sum(x["detected_under_screen"] for x in queries.values()),
        "interpretation": "This is a targeted translated-read detectability screen against one public young-leaf RNA-seq run. Alignment counts are not normalized expression estimates and cannot be interpreted as colour-associated differential expression.",
        "claim_boundary": "A detected homologous read supports assay-level recoverability only. A non-detection is not genomic absence or pathway loss. This pilot does not establish floral expression, exact orthology in the RNA-seq sample, genotype, or causal involvement in white/coloured phenotype.",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
