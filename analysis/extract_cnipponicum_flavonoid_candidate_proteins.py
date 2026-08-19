#!/usr/bin/env python3
"""Extract frozen C. nipponicum flavonoid protein candidates by exact ID."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT = {
    "DFR": "Cn_g13756.t1",
    "ANS": "Cn_g8152.t1",
}


def parse_fasta(path: Path):
    seqs = {}
    cur = None
    chunks = []
    with path.open(encoding="utf-8", errors="replace") as h:
        for line in h:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if cur is not None:
                    seqs[cur] = "".join(chunks)
                cur = line[1:].split()[0]
                chunks = []
            else:
                chunks.append(line)
        if cur is not None:
            seqs[cur] = "".join(chunks)
    return seqs


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proteome", required=True)
    ap.add_argument("--family-validation", default="data/evidence/cnipponicum_flavonoid_family_validation_v2.json")
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    validation = json.loads(Path(args.family_validation).read_text(encoding="utf-8"))
    if validation.get("contract_version") != "cnipponicum_flavonoid_family_validation_v2":
        raise ValueError("family validation contract drift")
    expected = {}
    for fam in ["DFR", "ANS"]:
        x = validation["family_results"][fam]
        if x["first_pass_status"] != "family_consistent_first_pass":
            raise ValueError(f"{fam} not admitted to targeted SRA pilot")
        prefix = f"CNIP_{fam}_"
        if not x["candidate"].startswith(prefix):
            raise ValueError(f"candidate naming drift: {fam}")
        expected[fam] = x["candidate"][len(prefix):]
    if expected != DEFAULT:
        raise ValueError(f"frozen priority candidates drift: {expected}")

    seqs = parse_fasta(Path(args.proteome))
    records = []
    meta = []
    for fam in ["DFR", "ANS"]:
        sid = expected[fam]
        if sid not in seqs:
            raise ValueError(f"missing candidate sequence: {sid}")
        seq = seqs[sid].upper()
        rec = f">CNIP_{fam}|source={sid}|evidence=family_consistent_first_pass\n{seq}\n"
        records.append(rec)
        meta.append({
            "family": fam,
            "source_protein_id": sid,
            "query_id": f"CNIP_{fam}",
            "length_aa": len(seq),
            "sequence_sha256": sha256(seq.encode()),
        })

    out = "".join(records).encode()
    Path(args.output).write_bytes(out)
    result = {
        "contract_version": "cnipponicum_dfr_ans_targeted_sra_queries_v1",
        "query_count": 2,
        "queries": meta,
        "combined_fasta_sha256": sha256(out),
        "claim_boundary": "These are first-pass family-consistent C. nipponicum proteins used only to search for homologous translated reads in public RNA-seq. Read detection does not establish expression differences, floral expression, orthology in the target sample, or causal colour function.",
    }
    Path(args.manifest).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
