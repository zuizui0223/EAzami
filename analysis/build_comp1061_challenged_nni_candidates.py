#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import json
from copy import deepcopy
from pathlib import Path

from Bio import Phylo


STATES = ("primary", "swap_first", "swap_second")


def parse_args():
    p = argparse.ArgumentParser(
        description="Build the preregistered 3x3 NNI candidate set around two challenged Comp1061 edges."
    )
    p.add_argument("--tree", required=True)
    p.add_argument("--concordance-result", required=True)
    p.add_argument("--preflight", required=True)
    p.add_argument("--outdir", required=True)
    return p.parse_args()


def terminal_names(clade):
    return frozenset(t.name for t in clade.get_terminals())


def find_exact_clade(tree, taxa):
    target = frozenset(taxa)
    matches = [c for c in tree.find_clades(order="level") if terminal_names(c) == target]
    if len(matches) != 1:
        raise ValueError(f"expected one exact clade for {sorted(target)}, found {len(matches)}")
    return matches[0]


def find_parent(tree, child):
    for clade in tree.find_clades(order="level"):
        if child in clade.clades:
            return clade
    raise ValueError("parent clade not found")


def canonical_split_side(side, all_taxa):
    side = frozenset(side)
    other = frozenset(all_taxa) - side
    a = tuple(sorted(side))
    b = tuple(sorted(other))
    if len(a) < len(b):
        return a
    if len(b) < len(a):
        return b
    return min(a, b)


def canonical_splits(tree):
    all_taxa = frozenset(t.name for t in tree.get_terminals())
    splits = set()
    for clade in tree.find_clades(order="preorder"):
        if clade is tree.root or clade.is_terminal():
            continue
        side = terminal_names(clade)
        if min(len(side), len(all_taxa - side)) < 2:
            continue
        splits.add(canonical_split_side(side, all_taxa))
    return tuple(sorted(splits))


def serialize_clade(clade):
    if clade.is_terminal():
        if not clade.name:
            raise ValueError("all terminals must be named")
        return clade.name
    return "(" + ",".join(serialize_clade(child) for child in clade.clades) + ")"


def serialize_tree(tree):
    # Candidate topology files intentionally omit inherited support labels and branch
    # lengths. IQ-TREE evaluates each candidate and re-optimizes branch lengths.
    return serialize_clade(tree.root) + ";\n"


def apply_nni_state(tree, target_taxa, state):
    if state == "primary":
        return

    node = find_exact_clade(tree, target_taxa)
    parent = find_parent(tree, node)
    if len(node.clades) != 2:
        raise ValueError(f"challenged clade {sorted(target_taxa)} is not binary")
    if len(parent.clades) != 2:
        raise ValueError(f"parent of challenged clade {sorted(target_taxa)} is not binary")

    siblings = [c for c in parent.clades if c is not node]
    if len(siblings) != 1:
        raise ValueError("expected exactly one parent-side sibling")
    sibling = siblings[0]

    if state == "swap_first":
        moving = node.clades[0]
        node.clades[0] = sibling
    elif state == "swap_second":
        moving = node.clades[1]
        node.clades[1] = sibling
    else:
        raise ValueError(f"unknown NNI state: {state}")

    parent.clades[parent.clades.index(sibling)] = moving


def split_json(split):
    return list(split)


def fingerprint_sha256(splits):
    payload = json.dumps([split_json(s) for s in splits], separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    args = parse_args()
    tree_path = Path(args.tree)
    result_path = Path(args.concordance_result)
    preflight_path = Path(args.preflight)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    result = json.loads(result_path.read_text())
    preflight = json.loads(preflight_path.read_text())

    if result["contract_version"] != "full20_comp1061_topology_concordance_result_v1":
        raise ValueError("unexpected topology-concordance result version")
    if result["source"]["workflow_run_id"] != preflight["source_concordance_result"]["workflow_run_id"]:
        raise ValueError("concordance result run does not match preflight")
    if result["source"]["artifact_digest"] != preflight["source_concordance_result"]["artifact_digest"]:
        raise ValueError("concordance artifact digest does not match preflight")
    if result["decision"]["alternative_topology_sensitivity_required"] is not True:
        raise ValueError("source result does not require alternative-topology sensitivity")

    edges = preflight["challenged_edges"]
    if len(edges) != 2:
        raise ValueError("preflight must contain exactly two challenged edges")
    flagged = [tuple(x["split"]) for x in result["uncertainty_flag"]["flagged_splits"]]
    declared = [tuple(x["split"]) for x in edges]
    if set(flagged) != set(declared):
        raise ValueError(f"preflight challenged edges differ from frozen result: {flagged} vs {declared}")

    primary = Phylo.read(str(tree_path), "newick")
    primary_taxa = tuple(sorted(t.name for t in primary.get_terminals()))
    if len(primary_taxa) != preflight["candidate_contract"]["tip_count"]:
        raise ValueError("primary tree tip count differs from preflight")
    if preflight["candidate_contract"]["root_outgroup"] not in primary_taxa:
        raise ValueError("frozen root outgroup is absent")

    primary_splits = canonical_splits(primary)
    if len(primary_splits) != preflight["candidate_contract"]["nontrivial_splits_per_tree"]:
        raise ValueError(f"unexpected primary split count: {len(primary_splits)}")

    # The preflight order determines which child is swap_first vs swap_second.
    for edge in edges:
        node = find_exact_clade(primary, edge["split"])
        parent = find_parent(primary, node)
        if len(node.clades) != 2 or len(parent.clades) != 2:
            raise ValueError(f"challenged edge is not an exact binary NNI edge: {edge['id']}")
        if tuple(t.name for t in node.get_terminals()) != tuple(edge["split"]):
            raise ValueError(f"challenged split child order changed for {edge['id']}")

    candidate_rows = []
    candidate_newicks = []
    seen_fingerprints = set()

    expected_count = preflight["candidate_contract"]["candidate_count"]
    for index, state_pair in enumerate(itertools.product(STATES, repeat=2), start=1):
        candidate = deepcopy(primary)
        state_by_edge = {}
        for edge, state in zip(edges, state_pair):
            apply_nni_state(candidate, edge["split"], state)
            state_by_edge[edge["id"]] = state

        taxa = tuple(sorted(t.name for t in candidate.get_terminals()))
        if taxa != primary_taxa:
            raise ValueError("candidate taxon set changed")

        splits = canonical_splits(candidate)
        if len(splits) != len(primary_splits):
            raise ValueError(
                f"candidate {index} has {len(splits)} nontrivial splits, expected {len(primary_splits)}"
            )

        fp = fingerprint_sha256(splits)
        if fp in seen_fingerprints:
            raise ValueError(f"duplicate candidate topology fingerprint at candidate {index}")
        seen_fingerprints.add(fp)

        newick = serialize_tree(candidate)
        removed = sorted(set(primary_splits) - set(splits))
        added = sorted(set(splits) - set(primary_splits))
        expected_changed_edges = sum(state != "primary" for state in state_pair)
        if len(removed) != expected_changed_edges or len(added) != expected_changed_edges:
            raise ValueError(
                f"candidate {index} changes {len(removed)}/{len(added)} splits, "
                f"expected {expected_changed_edges} NNI changes"
            )

        for edge, state in zip(edges, state_pair):
            focal = canonical_split_side(edge["split"], primary_taxa)
            if state == "primary" and focal not in splits:
                raise ValueError(f"candidate {index} lost primary split for {edge['id']}")
            if state != "primary" and focal in splits:
                raise ValueError(f"candidate {index} retained challenged primary split for {edge['id']}")

        candidate_id = f"T{index:02d}__" + "__".join(
            f"{edge['id']}-{state}" for edge, state in zip(edges, state_pair)
        )
        candidate_rows.append(
            {
                "index": index,
                "candidate_id": candidate_id,
                "states": state_by_edge,
                "tree_sha256": sha256_text(newick),
                "split_fingerprint_sha256": fp,
                "removed_primary_splits": [split_json(s) for s in removed],
                "added_splits": [split_json(s) for s in added],
            }
        )
        candidate_newicks.append(newick.rstrip())
        (outdir / f"{candidate_id}.nwk").write_text(newick)

    if len(candidate_rows) != expected_count:
        raise ValueError(f"generated {len(candidate_rows)} candidates, expected {expected_count}")
    if len(seen_fingerprints) != expected_count:
        raise ValueError("candidate topologies are not all unique")

    candidate_set_text = "\n".join(candidate_newicks) + "\n"
    (outdir / "candidate_trees.nwk").write_text(candidate_set_text)

    manifest = {
        "contract_version": "full20_comp1061_alt_topology_candidates_v1",
        "source_primary_tree_sha256": preflight["source_primary_tree"]["sha256"],
        "source_concordance_run_id": preflight["source_concordance_result"]["workflow_run_id"],
        "source_concordance_artifact_digest": preflight["source_concordance_result"]["artifact_digest"],
        "candidate_count": len(candidate_rows),
        "tip_count": len(primary_taxa),
        "nontrivial_splits_per_tree": len(primary_splits),
        "primary_split_fingerprint_sha256": fingerprint_sha256(primary_splits),
        "candidate_set_sha256": hashlib.sha256(candidate_set_text.encode()).hexdigest(),
        "candidate_order": [x["candidate_id"] for x in candidate_rows],
        "candidates": candidate_rows,
        "data_driven_candidate_filtering_applied": False,
        "rate_fit_execution_allowed": False,
    }
    (outdir / "candidate_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
