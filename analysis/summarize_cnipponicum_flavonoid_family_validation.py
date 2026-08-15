#!/usr/bin/env python3
"""Summarize first-pass family discrimination for C. nipponicum candidates.

Evidence layers:
- unrooted ML-tree patristic distance to curated positive vs negative references;
- reciprocal BLASTP to the reviewed Arabidopsis reference proteome.

The IQ-TREE outputs are unrooted. We therefore do not use rooted
candidate+positive common-ancestor membership as an orthology criterion.
Neither layer alone or together is called exact one-to-one orthology.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from pathlib import Path

from Bio import Phylo

RBH_FIELDS = [
    "qseqid", "sseqid", "pident", "length", "qlen", "slen",
    "evalue", "bitscore", "stitle",
]

EXPECTED_TITLE_PATTERNS = {
    "DFR": [r"dihydroflavonol 4-reductase", r"dihydroflavanol 4-reductase"],
    "ANS": [r"leucoanthocyanidin dioxygenase", r"anthocyanidin synthase"],
    "FLS": [r"flavonol synthase"],
    "CHS": [r"chalcone synthase"],
}


def read_rbh(path: Path):
    rows = []
    with path.open(encoding="utf-8", newline="") as h:
        for r in csv.DictReader(h, delimiter="\t", fieldnames=RBH_FIELDS):
            x = dict(r)
            for k in ["pident", "length", "qlen", "slen", "evalue", "bitscore"]:
                x[k] = float(x[k])
            rows.append(x)
    return rows


def accession_from_sseqid(s: str) -> str:
    parts = s.split("|")
    if len(parts) >= 2 and parts[0] in {"sp", "tr"}:
        return parts[1]
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-manifest", required=True)
    ap.add_argument("--rbh", required=True)
    ap.add_argument("--tree-dir", required=True)
    ap.add_argument("--arabidopsis-proteome-sha256", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    manifest = json.loads(Path(args.input_manifest).read_text(encoding="utf-8"))
    rbh = read_rbh(Path(args.rbh))
    byq = {}
    for r in rbh:
        byq.setdefault(r["qseqid"], []).append(r)
    for q in byq:
        byq[q].sort(key=lambda x: (-x["bitscore"], x["evalue"], -x["pident"]))

    families = {}
    for family, fm in manifest["families"].items():
        candidate = fm["candidate"]
        tree_path = Path(args.tree_dir) / f"{family}.aln.faa.treefile"
        if not tree_path.exists():
            raise FileNotFoundError(tree_path)
        tree = Phylo.read(str(tree_path), "newick")
        terminals = {t.name for t in tree.get_terminals()}
        if candidate not in terminals:
            raise ValueError(f"{family} candidate absent from tree")

        roles = json.loads(Path(fm["roles_file"]).read_text(encoding="utf-8"))
        positives = sorted(k for k,v in roles.items() if v == "positive")
        negatives = sorted(k for k,v in roles.items() if v == "negative")
        if not set(positives + negatives + [candidate]) <= terminals:
            raise ValueError(f"{family} tree/ref mismatch")

        pos_dist = {x: tree.distance(candidate, x) for x in positives}
        neg_dist = {x: tree.distance(candidate, x) for x in negatives}
        nearest_pos = min(pos_dist, key=pos_dist.get)
        nearest_neg = min(neg_dist, key=neg_dist.get)
        mean_pos = statistics.mean(pos_dist.values())
        mean_neg = statistics.mean(neg_dist.values())

        rr = byq.get(candidate, [])
        top = rr[0] if rr else None
        if top:
            title_match = any(re.search(p, top["stitle"], re.I) for p in EXPECTED_TITLE_PATTERNS[family])
            reciprocal = {
                "top_subject_id": top["sseqid"],
                "top_accession": accession_from_sseqid(top["sseqid"]),
                "top_title": top["stitle"],
                "top_pident": top["pident"],
                "top_evalue": top["evalue"],
                "top_bitscore": top["bitscore"],
                "expected_family_keyword_match": title_match,
                "reported_hits": len(rr),
            }
        else:
            reciprocal = {
                "reported_hits": 0,
                "expected_family_keyword_match": False,
            }

        nearest_positive_closer = pos_dist[nearest_pos] < neg_dist[nearest_neg]
        mean_positive_closer = mean_pos < mean_neg
        reciprocal_consistent = bool(reciprocal.get("expected_family_keyword_match"))
        if nearest_positive_closer and mean_positive_closer and reciprocal_consistent:
            status = "family_consistent_first_pass"
        else:
            status = "family_assignment_requires_manual_phylogenetic_review"

        families[family] = {
            "candidate": candidate,
            "treefile": str(tree_path),
            "tree_interpretation": "unrooted_ml_tree_patristic_distance_only",
            "positive_references": positives,
            "negative_references": negatives,
            "positive_reference_distances": pos_dist,
            "negative_reference_distances": neg_dist,
            "nearest_positive_reference": nearest_pos,
            "nearest_positive_distance": pos_dist[nearest_pos],
            "nearest_negative_reference": nearest_neg,
            "nearest_negative_distance": neg_dist[nearest_neg],
            "nearest_positive_to_negative_distance_ratio": pos_dist[nearest_pos] / neg_dist[nearest_neg],
            "mean_positive_distance": mean_pos,
            "mean_negative_distance": mean_neg,
            "mean_positive_to_negative_distance_ratio": mean_pos / mean_neg,
            "nearest_positive_closer_than_nearest_negative": nearest_positive_closer,
            "mean_positive_distance_smaller_than_mean_negative": mean_positive_closer,
            "reciprocal_arabidopsis": reciprocal,
            "first_pass_status": status,
        }

    status_counts = {}
    for x in families.values():
        status_counts[x["first_pass_status"]] = status_counts.get(x["first_pass_status"], 0) + 1

    result = {
        "contract_version": "cnipponicum_flavonoid_family_validation_v2",
        "families_tested": sorted(families),
        "arabidopsis_reference_proteome_query": "proteome:UP000006548 AND reviewed:true",
        "arabidopsis_reference_proteome_sha256": args.arabidopsis_proteome_sha256,
        "family_results": families,
        "status_counts": dict(sorted(status_counts.items())),
        "decision_rule": "For an unrooted ML tree, require both nearest-positive and mean-positive patristic distances to be smaller than their negative-reference counterparts, plus an expected-family reciprocal top hit in the reviewed Arabidopsis proteome. No rooted sister-clade criterion is applied.",
        "interpretation": "This first-pass gate asks whether each top C. nipponicum candidate is consistently more similar to curated functional positives than curated related negatives in the unrooted ML distance structure, and whether reciprocal similarity to reviewed Arabidopsis proteins returns the expected family label.",
        "next_gate": "Candidates passing this screen still require broader multi-species family/clade sampling, domain architecture where informative, copy-number/homeolog review, and W/C-lineage comparison before exact orthology/function or evolutionary-mechanism claims.",
        "claim_boundary": "family_consistent_first_pass is not one-to-one orthology. Unrooted ML patristic-distance discrimination and reciprocal BLAST annotation are screening evidence only; they do not demonstrate biochemical function or causal involvement in flower colour.",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
