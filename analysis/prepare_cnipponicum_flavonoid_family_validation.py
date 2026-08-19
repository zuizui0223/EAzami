#!/usr/bin/env python3
"""Prepare small family-discrimination alignments for top C. nipponicum candidates.

The input candidate IDs are frozen from the validated BLASTP screen. Reference
proteins are downloaded from explicit UniProt accessions and checksummed. These
family sets are for discrimination among close functional families, not for
claiming one-to-one orthology.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

FAMILY_QUERY = {
    "DFR": "DFR_TT3",
    "ANS": "ANS_TT18",
    "FLS": "FLS1",
    "CHS": "CHS_TT4",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_fasta(path: Path) -> dict[str, str]:
    seqs: dict[str, list[str]] = {}
    current = None
    with path.open(encoding="utf-8", errors="replace") as h:
        for line in h:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current = line[1:].split()[0]
                seqs[current] = []
            elif current is not None:
                seqs[current].append(line)
    return {k: "".join(v) for k, v in seqs.items()}


def parse_uniprot_fasta(raw: bytes) -> tuple[str, str]:
    text = raw.decode("utf-8")
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if not lines or not lines[0].startswith(">"):
        raise ValueError("UniProt response is not FASTA")
    header = lines[0][1:]
    seq = "".join(lines[1:]).upper()
    if not seq:
        raise ValueError("empty UniProt sequence")
    return header, seq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proteome", required=True)
    ap.add_argument("--top-candidates", default="data/evidence/cnipponicum_flavonoid_top_candidates_v1.csv")
    ap.add_argument("--references", default="data/evidence/cnipponicum_flavonoid_family_reference_panel_v1.csv")
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    proteome = parse_fasta(Path(args.proteome))

    with Path(args.top_candidates).open(encoding="utf-8-sig", newline="") as h:
        top = {r["query_id"]: r for r in csv.DictReader(h)}
    with Path(args.references).open(encoding="utf-8-sig", newline="") as h:
        refs = list(csv.DictReader(h))
    refs_by_family: dict[str, list[dict]] = defaultdict(list)
    for r in refs:
        refs_by_family[r["family"]].append(r)

    candidate_records = []
    materialized_refs = []
    family_outputs = {}
    combined_candidates = []

    for family, query_id in FAMILY_QUERY.items():
        if query_id not in top:
            raise ValueError(f"frozen top candidate missing for {query_id}")
        subject = top[query_id]["top_subject"]
        if subject not in proteome:
            raise ValueError(f"C. nipponicum protein missing: {subject}")
        cn_seq = proteome[subject]
        cn_name = f"CNIP_{family}_{subject}"
        combined_candidates.append(f">{cn_name}\n{cn_seq}\n")
        candidate_records.append({
            "family": family,
            "query_id": query_id,
            "candidate_name": cn_name,
            "subject_id": subject,
            "sequence_length": len(cn_seq),
            "sequence_sha256": sha256(cn_seq.encode()),
        })

        records = [f">{cn_name}\n{cn_seq}\n"]
        roles = {cn_name: "candidate"}
        for r in refs_by_family.get(family, []):
            with urllib.request.urlopen(r["official_fasta_url"], timeout=60) as resp:
                raw = resp.read()
            header, seq = parse_uniprot_fasta(raw)
            acc = r["uniprot_accession"]
            if f"|{acc}|" not in header and not header.startswith(acc + " "):
                raise ValueError(f"reference accession mismatch: {r['reference_id']} -> {header}")
            name = f"REF_{r['role'].upper()}_{r['reference_id']}"
            records.append(f">{name}\n{seq}\n")
            roles[name] = r["role"]
            materialized_refs.append({
                "family": family,
                "reference_id": r["reference_id"],
                "role": r["role"],
                "taxon": r["reference_taxon"],
                "uniprot_accession": acc,
                "function_label": r["function_label"],
                "uniprot_header": header,
                "sequence_length": len(seq),
                "raw_fasta_sha256": sha256(raw),
                "sequence_sha256": sha256(seq.encode()),
            })

        if not any(v == "positive" for v in roles.values()) or not any(v == "negative" for v in roles.values()):
            raise ValueError(f"family {family} requires positive and negative references")
        fasta_path = outdir / f"{family}.family.faa"
        fasta_bytes = "".join(records).encode()
        fasta_path.write_bytes(fasta_bytes)
        role_path = outdir / f"{family}.roles.json"
        role_path.write_text(json.dumps(roles, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        family_outputs[family] = {
            "query_id": query_id,
            "candidate": cn_name,
            "family_fasta": str(fasta_path),
            "family_fasta_sha256": sha256(fasta_bytes),
            "roles_file": str(role_path),
            "reference_count": len(records) - 1,
            "positive_references": sum(v == "positive" for v in roles.values()),
            "negative_references": sum(v == "negative" for v in roles.values()),
        }

    candidate_fasta = outdir / "cnip_top_four_candidates.faa"
    candidate_bytes = "".join(combined_candidates).encode()
    candidate_fasta.write_bytes(candidate_bytes)

    summary = {
        "contract_version": "cnipponicum_flavonoid_family_validation_inputs_v1",
        "families": family_outputs,
        "candidate_records": candidate_records,
        "reference_records": materialized_refs,
        "combined_candidate_fasta": str(candidate_fasta),
        "combined_candidate_fasta_sha256": sha256(candidate_bytes),
        "claim_boundary": "These family sets discriminate sequence placement relative to curated positive and negative references. They do not establish one-to-one orthology or biochemical function.",
    }
    (outdir / "input_manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
