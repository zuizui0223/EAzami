#!/usr/bin/env python3
"""Summarize the empirical four-tip public-candidate placement pilot.

The quartet contains one frozen 294-baseline sample and one independent public
candidate for each of two taxa:

* baseline *C. nipponicum* var. *yoshinoi* + EA01/PUBEA001;
* baseline *C. sairamense* + EA02/PUBEA002.

Every gene tree and the concatenated tree are inferred from the exact same
four-way strict-locus intersection.  This script classifies each resolved
unrooted quartet into one of the three possible bipartitions.  It is an
empirical sanity check of same-taxon placement, not a substitute for the full
294-tip promotion gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluate_east_asia_public_augmentation_tree_pair import NewickParser, split_set

TIPS = (
    "MRY_YOSHINOI",
    "PUBEA001",
    "MRY_SAIRAMENSE",
    "PUBEA002",
)
TIP_SET = set(TIPS)

TOPOLOGIES = {
    "same_taxon_pairs": frozenset({"MRY_YOSHINOI", "PUBEA001"}),
    "baseline_vs_candidates": frozenset({"MRY_YOSHINOI", "MRY_SAIRAMENSE"}),
    "crossed_pairs": frozenset({"MRY_YOSHINOI", "PUBEA002"}),
}


def canonical_pair(pair: frozenset[str]) -> frozenset[str]:
    other = TIP_SET - set(pair)
    left = tuple(sorted(pair))
    right = tuple(sorted(other))
    return pair if left <= right else frozenset(other)


CANONICAL_TOPOLOGIES = {name: canonical_pair(pair) for name, pair in TOPOLOGIES.items()}


def classify_newick(text: str) -> str:
    root = NewickParser(text).parse()
    splits = split_set(root, TIP_SET)
    quartet_splits = [split for split in splits if len(split) == 2]
    if not quartet_splits:
        return "unresolved"
    if len(quartet_splits) != 1:
        raise ValueError(f"expected at most one quartet split, observed {quartet_splits}")
    observed = canonical_pair(quartet_splits[0])
    for name, expected in CANONICAL_TOPOLOGIES.items():
        if observed == expected:
            return name
    raise ValueError(f"unexpected quartet split: {sorted(observed)}")


def read_loci(path: Path) -> list[str]:
    loci = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not loci or len(loci) != len(set(loci)):
        raise ValueError("common-locus list is empty or duplicated")
    return loci


def summarize(common_loci: Path, gene_tree_dir: Path, concat_tree: Path, output: Path) -> dict[str, object]:
    loci = read_loci(common_loci)
    counts = {name: 0 for name in (*TOPOLOGIES, "unresolved")}
    missing: list[str] = []
    per_locus: list[dict[str, str]] = []
    for locus in loci:
        path = gene_tree_dir / f"{locus}.treefile"
        if not path.is_file() or not path.stat().st_size:
            missing.append(locus)
            continue
        topology = classify_newick(path.read_text(encoding="utf-8"))
        counts[topology] += 1
        per_locus.append({"locus": locus, "topology": topology})

    if missing:
        raise ValueError(f"missing {len(missing)} gene trees; first={missing[:5]}")
    if not concat_tree.is_file() or not concat_tree.stat().st_size:
        raise ValueError("concatenated tree is missing")
    concat_topology = classify_newick(concat_tree.read_text(encoding="utf-8"))
    resolved = sum(counts[name] for name in TOPOLOGIES)
    same = counts["same_taxon_pairs"]
    alternative = counts["baseline_vs_candidates"] + counts["crossed_pairs"]
    informative = same + alternative

    out: dict[str, object] = {
        "contract_version": "public_candidate_empirical_quartet_v1",
        "tips": list(TIPS),
        "taxon_pairs": {
            "Cirsium nipponicum var. yoshinoi": ["MRY_YOSHINOI", "PUBEA001"],
            "Cirsium sairamense": ["MRY_SAIRAMENSE", "PUBEA002"],
        },
        "common_strict_loci": len(loci),
        "gene_trees": len(per_locus),
        "gene_tree_topology_counts": counts,
        "resolved_gene_trees": resolved,
        "same_taxon_pair_gene_tree_fraction_all": same / len(loci),
        "same_taxon_pair_fraction_resolved": same / resolved if resolved else None,
        "same_taxon_pair_fraction_informative": same / informative if informative else None,
        "concatenated_topology": concat_topology,
        "concatenated_same_taxon_pairs": concat_topology == "same_taxon_pairs",
        "pilot_same_taxon_signal": (
            "consistent" if concat_topology == "same_taxon_pairs" and same > alternative
            else "conflicting_or_weak"
        ),
        "full_294_tip_promotion_allowed_from_this_pilot": False,
        "claim_boundary": (
            "This quartet is a real-read same-taxon placement sanity check. It does not test shared-294 RF, "
            "full-panel ASTRAL stability, assay-wide topology distortion, or authorize EA01/EA02 promotion."
        ),
        "per_locus": per_locus,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in out.items() if key != "per_locus"}, indent=2, ensure_ascii=False))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--common-loci", type=Path, required=True)
    parser.add_argument("--gene-tree-dir", type=Path, required=True)
    parser.add_argument("--concat-tree", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.common_loci, args.gene_tree_dir, args.concat_tree, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
