#!/usr/bin/env python3
"""Audit functional annotation terms in the frozen C. nipponicum genome files.

This is a discovery audit only. Text matches are candidate annotations, not
orthology or causal evidence. No match means only that the supplied public
FASTA/GFF text does not expose the requested term.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

PATTERNS = {
    "ANS": [r"anthocyanidin synthase", r"leucoanthocyanidin dioxygenase", r"\bLDOX\b"],
    "UFGT": [
        r"UDP[- ]glucose.*flavonoid.*glucosyltransferase",
        r"anthocyanidin.*glucosyltransferase",
        r"flavonoid 3[- ]O[- ]glucosyltransferase",
        r"\bUFGT\b",
    ],
    "MYB_generic": [r"\bMYB\b", r"MYB[- ]related", r"MYB transcription factor"],
    "bHLH_generic": [r"\bbHLH\b", r"basic helix[- ]loop[- ]helix"],
    "WD40_generic": [r"\bWD40\b", r"WD[- ]repeat"],
    "GST_generic": [r"glutathione S[- ]transferase", r"\bGST\b"],
    "MATE_generic": [r"MATE.*transporter", r"multidrug and toxic compound extrusion", r"\bMATE\b"],
    "DFR": [r"dihydroflavonol 4[- ]reductase", r"\bDFR\b"],
    "CHS": [r"chalcone synthase", r"\bCHS\b"],
    "CHI": [r"chalcone isomerase", r"\bCHI\b"],
    "F3H": [r"flavanone 3[- ]hydroxylase", r"\bF3H\b"],
    "F3primeH": [r"flavonoid 3.?[- ]hydroxylase", r"\bF3.?H\b"],
    "FLS": [r"flavonol synthase", r"\bFLS\b"],
}


def compile_patterns():
    return {k: [re.compile(p, re.I) for p in ps] for k, ps in PATTERNS.items()}


def iter_fasta_headers(path: Path):
    with path.open(encoding="utf-8", errors="replace") as h:
        for line in h:
            if line.startswith(">"):
                yield "protein_fasta_header", line[1:].rstrip("\n")


def iter_gff_text(path: Path):
    with path.open(encoding="utf-8", errors="replace") as h:
        for line in h:
            if line.startswith("#") or not line.strip():
                continue
            yield "gff3", line.rstrip("\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protein", required=True)
    ap.add_argument("--gff", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--hits", required=True)
    args = ap.parse_args()

    protein = Path(args.protein)
    gff = Path(args.gff)
    pats = compile_patterns()
    hits = []
    source_counts = {"protein_fasta_header": 0, "gff3": 0}
    examples = {"protein_fasta_header": [], "gff3": []}

    def scan(source, text):
        source_counts[source] += 1
        if len(examples[source]) < 5:
            examples[source].append(text[:500])
        for family, regexes in pats.items():
            matched = [rx.pattern for rx in regexes if rx.search(text)]
            if matched:
                hits.append({
                    "family": family,
                    "source": source,
                    "matched_patterns": "|".join(matched),
                    "text": text[:4000],
                })

    for src, text in iter_fasta_headers(protein):
        scan(src, text)
    for src, text in iter_gff_text(gff):
        scan(src, text)

    counts = {}
    by_source = {}
    for family in PATTERNS:
        fh = [x for x in hits if x["family"] == family]
        counts[family] = len(fh)
        by_source[family] = {
            s: sum(1 for x in fh if x["source"] == s)
            for s in source_counts
        }

    with Path(args.hits).open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["family", "source", "matched_patterns", "text"])
        w.writeheader()
        w.writerows(hits)

    result = {
        "contract_version": "cnipponicum_flavonoid_annotation_term_audit_v1",
        "protein_headers_scanned": source_counts["protein_fasta_header"],
        "gff_records_scanned": source_counts["gff3"],
        "example_text": examples,
        "term_hit_counts": counts,
        "term_hit_counts_by_source": by_source,
        "total_hit_rows": len(hits),
        "interpretation_rule": "A text hit is a candidate annotation only, not an orthology assignment. Zero text hits means the public FASTA/GFF text does not expose the term; it is never evidence of genomic absence.",
        "next_gate": "If terminal/regulatory terms are not functionally exposed by FASTA/GFF headers, recover functional annotation tables or perform sequence/domain-based orthology against validated reference proteins before any presence/absence inference.",
    }
    Path(args.summary).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
