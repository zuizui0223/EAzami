#!/usr/bin/env python3
"""Evaluate one paired baseline-vs-augmentation tree comparison.

The trees must come from the same frozen locus set.  The evaluator quantifies
unrooted RF change on the 294 shared focal tips and records the candidate's
nearest baseline-tip neighbourhood without turning one tree into an automatic
promotion decision.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import deque
from pathlib import Path
from typing import Iterable, Mapping

EXPECTED_CONTRACT = "east_asia_public_tree_augmentation_v1"


class Node:
    __slots__ = ("name", "children", "parent")
    def __init__(self, name: str = ""):
        self.name = name
        self.children: list[Node] = []
        self.parent: Node | None = None
    @property
    def is_tip(self) -> bool:
        return not self.children


class NewickParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.i = 0
    def ws(self) -> None:
        while self.i < len(self.text) and self.text[self.i].isspace():
            self.i += 1
    def label(self) -> str:
        self.ws()
        if self.i >= len(self.text) or self.text[self.i] in ",():;":
            return ""
        if self.text[self.i] in "'\"":
            quote = self.text[self.i]
            self.i += 1
            out: list[str] = []
            while self.i < len(self.text):
                char = self.text[self.i]
                self.i += 1
                if char == quote:
                    if self.i < len(self.text) and self.text[self.i] == quote:
                        out.append(quote)
                        self.i += 1
                        continue
                    break
                out.append(char)
            return "".join(out).strip()
        start = self.i
        while self.i < len(self.text) and self.text[self.i] not in ",():;":
            self.i += 1
        return self.text[start:self.i].strip()
    def skip_length(self) -> None:
        self.ws()
        if self.i >= len(self.text) or self.text[self.i] != ":":
            return
        self.i += 1
        while self.i < len(self.text) and self.text[self.i] not in ",();":
            self.i += 1
    def subtree(self) -> Node:
        self.ws()
        if self.i >= len(self.text):
            raise ValueError("unexpected end of Newick")
        if self.text[self.i] == "(":
            self.i += 1
            node = Node()
            while True:
                child = self.subtree()
                child.parent = node
                node.children.append(child)
                self.ws()
                if self.i >= len(self.text):
                    raise ValueError("unclosed Newick group")
                if self.text[self.i] == ",":
                    self.i += 1
                    continue
                if self.text[self.i] == ")":
                    self.i += 1
                    break
                raise ValueError(f"unexpected Newick character {self.text[self.i]!r}")
            node.name = self.label()
            self.skip_length()
            return node
        name = self.label()
        if not name:
            raise ValueError(f"missing tip label near offset {self.i}")
        node = Node(name)
        self.skip_length()
        return node
    def parse(self) -> Node:
        root = self.subtree()
        self.ws()
        if self.i < len(self.text) and self.text[self.i] == ";":
            self.i += 1
        self.ws()
        if self.i != len(self.text):
            raise ValueError(f"trailing Newick text near offset {self.i}")
        return root


def clean(value: object) -> str:
    return str(value or "").strip()


def load_contract(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract_version") != EXPECTED_CONTRACT:
        raise ValueError("unexpected augmentation contract")
    return data


def candidate_contract(contract: Mapping[str, object], candidate_id: str) -> dict[str, object]:
    rows = contract.get("candidates")
    if not isinstance(rows, list):
        raise ValueError("contract candidates missing")
    hits = [row for row in rows if isinstance(row, dict) and clean(row.get("candidate_id")) == candidate_id]
    if len(hits) != 1:
        raise ValueError(f"expected one contract row for {candidate_id}")
    return hits[0]


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    required = {"tip_id", "analysis_taxon_label"}
    if not rows or not required <= set(rows[0]):
        raise ValueError(f"manifest missing {sorted(required - set(rows[0]) if rows else required)}")
    if len({row["tip_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate manifest tip_id")
    return rows


def tip_index(root: Node) -> dict[str, Node]:
    out: dict[str, Node] = {}
    def walk(node: Node) -> None:
        if node.is_tip:
            if node.name in out:
                raise ValueError(f"duplicate tree tip: {node.name}")
            out[node.name] = node
            return
        for child in node.children:
            walk(child)
    walk(root)
    return out


def descendants(node: Node) -> set[str]:
    if node.is_tip:
        return {node.name}
    out: set[str] = set()
    for child in node.children:
        out.update(descendants(child))
    return out


def canonical_split(side: set[str], all_tips: set[str]) -> frozenset[str]:
    other = all_tips - side
    if len(side) < len(other):
        return frozenset(side)
    if len(other) < len(side):
        return frozenset(other)
    a = tuple(sorted(side))
    b = tuple(sorted(other))
    return frozenset(side if a <= b else other)


def split_set(root: Node, shared: set[str]) -> set[frozenset[str]]:
    if len(shared) < 4:
        raise ValueError("RF comparison requires at least four shared tips")
    idx = tip_index(root)
    missing = sorted(shared - set(idx))
    if missing:
        raise ValueError(f"shared tips absent from tree: {missing[:8]}")
    splits: set[frozenset[str]] = set()
    def walk(node: Node) -> set[str]:
        if node.is_tip:
            return {node.name} if node.name in shared else set()
        desc: set[str] = set()
        for child in node.children:
            cdesc = walk(child)
            if 2 <= len(cdesc) <= len(shared) - 2:
                splits.add(canonical_split(cdesc, shared))
            desc.update(cdesc)
        return desc
    observed = walk(root)
    if observed != shared:
        raise ValueError("internal RF traversal lost shared tips")
    return splits


def neighbors(node: Node) -> list[Node]:
    out = list(node.children)
    if node.parent is not None:
        out.append(node.parent)
    return out


def nearest_shared_tips(root: Node, candidate_tip: str, shared: set[str]) -> tuple[int, list[str]]:
    idx = tip_index(root)
    if candidate_tip not in idx:
        raise ValueError(f"candidate tip absent from augmented tree: {candidate_tip}")
    start = idx[candidate_tip]
    queue = deque([(start, 0)])
    seen = {start}
    found: list[str] = []
    best: int | None = None
    while queue:
        node, dist = queue.popleft()
        if best is not None and dist > best:
            break
        if node.is_tip and node.name in shared:
            best = dist
            found.append(node.name)
            continue
        for nxt in neighbors(node):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, dist + 1))
    if best is None or not found:
        raise ValueError("no shared baseline neighbour found")
    return best, sorted(found)


def evaluate(
    baseline_tree: Path,
    augmented_tree: Path,
    baseline_manifest: Path,
    contract_path: Path,
    candidate_id: str,
    output: Path,
) -> dict[str, object]:
    contract = load_contract(contract_path)
    candidate = candidate_contract(contract, candidate_id)
    rows = read_manifest(baseline_manifest)
    expected_n = int(contract["baseline"]["biological_tips"])  # type: ignore[index]
    if len(rows) != expected_n:
        raise ValueError(f"baseline manifest has {len(rows)} tips, expected {expected_n}")
    shared = {row["tip_id"] for row in rows}
    taxon_by_tip = {row["tip_id"]: row["analysis_taxon_label"] for row in rows}
    candidate_tip = clean(candidate["tip_id"])
    candidate_taxon = clean(candidate["scientific_name"])

    baseline_root = NewickParser(baseline_tree.read_text(encoding="utf-8")).parse()
    augmented_root = NewickParser(augmented_tree.read_text(encoding="utf-8")).parse()
    baseline_idx = tip_index(baseline_root)
    augmented_idx = tip_index(augmented_root)
    if candidate_tip in baseline_idx:
        raise ValueError("candidate tip already occurs in baseline tree")
    missing_baseline = sorted(shared - set(baseline_idx))
    missing_augmented = sorted(shared - set(augmented_idx))
    if missing_baseline or missing_augmented:
        raise ValueError(
            f"baseline focal tips missing from trees: baseline={missing_baseline[:4]} augmented={missing_augmented[:4]}"
        )
    if candidate_tip not in augmented_idx:
        raise ValueError("candidate tip absent from augmented tree")

    base_splits = split_set(baseline_root, shared)
    aug_splits = split_set(augmented_root, shared)
    rf = len(base_splits.symmetric_difference(aug_splits))
    denom = len(base_splits) + len(aug_splits)
    normalized = rf / denom if denom else 0.0
    distance, nearest = nearest_shared_tips(augmented_root, candidate_tip, shared)
    nearest_taxa = sorted({taxon_by_tip[tip] for tip in nearest})
    same_taxon_tips = sorted(tip for tip in shared if taxon_by_tip[tip] == candidate_taxon)
    expected_same = bool(candidate.get("baseline_exact_taxon_expected"))
    if expected_same and not same_taxon_tips:
        raise ValueError(f"contract expects a baseline {candidate_taxon} tip, but none exists")
    if not expected_same and same_taxon_tips:
        raise ValueError(f"contract expects {candidate_taxon} to be new, but baseline already contains it")

    result: dict[str, object] = {
        "contract_version": "east_asia_public_augmentation_tree_pair_evaluation_v1",
        "candidate_id": candidate_id,
        "candidate_tip": candidate_tip,
        "candidate_taxon": candidate_taxon,
        "shared_baseline_focal_tips": len(shared),
        "baseline_nontrivial_splits": len(base_splits),
        "augmented_pruned_nontrivial_splits": len(aug_splits),
        "unrooted_rf_distance_on_shared_baseline_tips": rf,
        "normalized_rf_distance_on_shared_baseline_tips": normalized,
        "exact_shared_tip_backbone_invariance": rf == 0,
        "candidate_nearest_baseline_topological_distance_edges": distance,
        "candidate_nearest_baseline_tip_ids": nearest,
        "candidate_nearest_baseline_taxa": nearest_taxa,
        "baseline_exact_taxon_tip_ids": same_taxon_tips,
        "same_taxon_among_nearest_baseline_tips": bool(set(nearest) & set(same_taxon_tips)),
        "placement_interpretation": (
            "EA01 is a same-taxon replicate and should reproduce the existing yoshinoi neighbourhood; "
            "EA02 is a new continental taxon and its neighbourhood must be compared across mapping/tree sensitivities."
        ),
        "tree_tip_promotion_allowed_from_this_pair_alone": False,
        "new_china_sampling_freeze_allowed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-tree", type=Path, required=True)
    parser.add_argument("--augmented-tree", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--candidate-id", choices=("EA01", "EA02"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evaluate(
        args.baseline_tree,
        args.augmented_tree,
        args.baseline_manifest,
        args.contract,
        args.candidate_id,
        args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
