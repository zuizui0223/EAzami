#!/usr/bin/env python3
"""Materialize and checksum the frozen reviewed UniProt query panel."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from pathlib import Path


def sha256_bytes(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def parse_fasta(raw: str) -> tuple[str, str]:
    lines = [x.strip() for x in raw.splitlines() if x.strip()]
    if not lines or not lines[0].startswith(">"):
        raise ValueError("not FASTA")
    header = lines[0][1:]
    seq = "".join(lines[1:]).replace(" ", "").upper()
    if not seq or any(c not in "ABCDEFGHIKLMNPQRSTVWXYZUO" for c in seq):
        raise ValueError("unexpected protein sequence alphabet")
    return header, seq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/evidence/cnipponicum_flavonoid_reference_queries_v1.csv")
    ap.add_argument("--fasta", required=True)
    ap.add_argument("--summary", required=True)
    args = ap.parse_args()

    with Path(args.manifest).open(encoding="utf-8-sig", newline="") as h:
        rows = list(csv.DictReader(h))
    if len(rows) != 11:
        raise ValueError(f"expected 11 frozen queries, got {len(rows)}")
    if len({r['query_id'] for r in rows}) != len(rows):
        raise ValueError("duplicate query_id")
    if len({r['uniprot_accession'] for r in rows}) != len(rows):
        raise ValueError("duplicate UniProt accession")

    output = []
    evidence = []
    for row in rows:
        with urllib.request.urlopen(row["official_fasta_url"], timeout=60) as resp:
            raw_bytes = resp.read()
        raw = raw_bytes.decode("utf-8")
        header, seq = parse_fasta(raw)
        acc = row["uniprot_accession"]
        if f"|{acc}|" not in header and not header.startswith(acc + " "):
            raise ValueError(f"UniProt accession mismatch for {row['query_id']}: {header}")
        out_header = (
            f">{row['query_id']}|uniprot={acc}|family={row['gene_family']}|"
            f"class={row['candidate_class']}"
        )
        record = out_header + "\n" + seq + "\n"
        output.append(record)
        evidence.append({
            "query_id": row["query_id"],
            "gene_family": row["gene_family"],
            "module": row["module"],
            "uniprot_accession": acc,
            "uniprot_header": header,
            "sequence_length_aa": len(seq),
            "raw_uniprot_fasta_sha256": sha256_bytes(raw_bytes),
            "normalized_record_sha256": sha256_bytes(record.encode()),
            "candidate_class": row["candidate_class"],
            "reference_role": row["reference_role"],
        })

    combined = "".join(output).encode()
    Path(args.fasta).write_bytes(combined)
    result = {
        "contract_version": "cnipponicum_flavonoid_reference_queries_v1",
        "query_count": len(rows),
        "query_ids": [r["query_id"] for r in rows],
        "combined_query_fasta_sha256": sha256_bytes(combined),
        "records": evidence,
        "claim_boundary": "Reviewed Arabidopsis proteins are candidate-retrieval anchors. Sequence similarity to C. nipponicum does not by itself establish one-to-one orthology or anthocyanin function in Cirsium.",
    }
    Path(args.summary).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
