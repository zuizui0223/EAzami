#!/usr/bin/env python3
"""Summarize BLASTP candidate retrieval against the C. nipponicum proteome.

This is a homology screen, not an orthology or function assignment.
"""
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


def read_manifest(path: str):
    with Path(path).open(encoding="utf-8-sig", newline="") as h:
        return {r["query_id"]: r for r in csv.DictReader(h)}


def read_hits(path: str):
    out = []
    with Path(path).open(encoding="utf-8", newline="") as h:
        for row in csv.DictReader(h, delimiter="\t", fieldnames=FIELDS):
            x = dict(row)
            x["qseqid_raw"] = x["qseqid"]
            x["qseqid"] = x["qseqid"].split("|", 1)[0]
            for k in ["pident", "length", "qlen", "slen", "qstart", "qend", "sstart", "send", "evalue", "bitscore"]:
                x[k] = float(x[k])
            qspan = abs(x["qend"] - x["qstart"]) + 1
            sspan = abs(x["send"] - x["sstart"]) + 1
            x["qcov"] = qspan / x["qlen"] if x["qlen"] else 0.0
            x["scov"] = sspan / x["slen"] if x["slen"] else 0.0
            out.append(x)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/evidence/cnipponicum_flavonoid_reference_queries_v1.csv")
    ap.add_argument("--blast", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--candidates", required=True)
    args = ap.parse_args()

    manifest = read_manifest(args.manifest)
    hits = read_hits(args.blast)
    unknown = sorted({h["qseqid"] for h in hits} - set(manifest))
    if unknown:
        raise ValueError(f"BLAST query IDs not in frozen manifest after normalization: {unknown}")
    byq = defaultdict(list)
    for h in hits:
        byq[h["qseqid"]].append(h)
    for q in byq:
        byq[q].sort(key=lambda x: (-x["bitscore"], x["evalue"], -x["pident"]))

    summary_queries = {}
    candidate_rows = []
    for q, meta in manifest.items():
        qhits = byq.get(q, [])
        top = qhits[0] if qhits else None
        second = qhits[1] if len(qhits) > 1 else None
        if top:
            ratio = second["bitscore"] / top["bitscore"] if second else None
            near = [h for h in qhits if h["bitscore"] >= 0.8 * top["bitscore"]]
            summary_queries[q] = {
                "gene_family": meta["gene_family"],
                "module": meta["module"],
                "reference_accession": meta["uniprot_accession"],
                "candidate_class": meta["candidate_class"],
                "hit_count_reported": len(qhits),
                "top_subject": top["sseqid"],
                "top_pident": top["pident"],
                "top_qcov": top["qcov"],
                "top_scov": top["scov"],
                "top_evalue": top["evalue"],
                "top_bitscore": top["bitscore"],
                "second_to_top_bitscore_ratio": ratio,
                "candidates_within_80pct_top_bitscore": len(near),
                "retrieval_status": "candidate_homolog_retrieved",
                "interpretation": meta["claim_boundary"],
            }
            for rank, h in enumerate(qhits, 1):
                candidate_rows.append({
                    "query_id": q,
                    "gene_family": meta["gene_family"],
                    "module": meta["module"],
                    "reference_accession": meta["uniprot_accession"],
                    "candidate_class": meta["candidate_class"],
                    "rank": rank,
                    "subject_id": h["sseqid"],
                    "pident": h["pident"],
                    "alignment_length": int(h["length"]),
                    "query_length": int(h["qlen"]),
                    "subject_length": int(h["slen"]),
                    "qcov": h["qcov"],
                    "scov": h["scov"],
                    "evalue": h["evalue"],
                    "bitscore": h["bitscore"],
                    "within_80pct_top_bitscore": h["bitscore"] >= 0.8 * top["bitscore"],
                })
        else:
            summary_queries[q] = {
                "gene_family": meta["gene_family"],
                "module": meta["module"],
                "reference_accession": meta["uniprot_accession"],
                "candidate_class": meta["candidate_class"],
                "hit_count_reported": 0,
                "retrieval_status": "no_hit_under_screen_settings",
                "interpretation": "No BLAST hit under this screen is not gene absence; reference distance, family divergence, assembly/annotation and search settings remain alternatives.",
            }

    with Path(args.candidates).open("w", encoding="utf-8", newline="") as h:
        fields = list(candidate_rows[0].keys()) if candidate_rows else [
            "query_id", "gene_family", "module", "reference_accession", "candidate_class", "rank", "subject_id",
            "pident", "alignment_length", "query_length", "subject_length", "qcov", "scov", "evalue", "bitscore", "within_80pct_top_bitscore"
        ]
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(candidate_rows)

    recovered = sum(v["retrieval_status"] == "candidate_homolog_retrieved" for v in summary_queries.values())
    controls = {q: summary_queries[q] for q in ["CHS_TT4", "FLS1", "DFR_TT3", "ANS_TT18"]}
    family_ambiguous = [
        q for q,v in summary_queries.items()
        if manifest[q]["candidate_class"] == "family_candidate_not_orthology_proven"
        and v["retrieval_status"] == "candidate_homolog_retrieved"
    ]
    result = {
        "contract_version": "cnipponicum_flavonoid_blast_candidate_retrieval_v1",
        "query_count": len(manifest),
        "raw_blast_alignment_rows": len(hits),
        "queries_with_candidate_hit": recovered,
        "queries_without_hit_under_settings": len(manifest) - recovered,
        "blast_screen_settings": {
            "evalue": 1e-5,
            "max_target_seqs": 20,
            "ranking": "bitscore desc, then evalue, then percent identity",
            "coverage_definition": "aligned query/subject coordinate span divided by full query/subject length; BLAST alignment length is not used because it includes gaps",
        },
        "queries": summary_queries,
        "positive_control_and_enzyme_queries": controls,
        "large_family_queries_requiring_clade_or_domain_validation": family_ambiguous,
        "next_gate": "For enzyme candidates and especially MYB/bHLH/WD40/UGT/GST/MATE families, validate domain architecture and infer family/clade trees with multiple plant references before calling orthology or anthocyanin function. Then compare validated Cirsium candidates across colour systems.",
        "claim_boundary": "BLASTP top hits are sequence-homology candidates. They are not one-to-one ortholog assignments, gene-function proofs, pathway activity measurements, or evidence that a white/coloured evolutionary transition was caused by that locus.",
    }
    Path(args.summary).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
