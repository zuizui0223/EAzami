#!/usr/bin/env python3
"""Validate a branch-length nuclear tree before flower-colour rate fitting.

This is deliberately independent from ER/ARD/Mk fitting. It establishes that a
machine-readable nuclear tree is real, has branch lengths, has explicit
provenance/rooting/support semantics, can be joined one-to-one to the frozen
source-backed colour atlas, and—when reference/outgroup tips are declared—keeps
the focal taxa monophyletic relative to those references. A valid tree does not
by itself unlock rate fitting; the independent atlas state/breadth gate must
also pass.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ALLOWED_ROUTES = {"published_exact", "compatibility_reanalysis", "independent_reanalysis"}
ALLOWED_MAPPING = {"exact", "reviewed_synonym", "reviewed_infraspecific_mapping"}


def clean(x: object) -> str:
    return str(x or "").strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(f)]


class NewickParser:
    def __init__(self, text: str):
        self.s = text.strip()
        self.i = 0
        self.tips: list[str] = []
        self.edge_lengths: list[float] = []
        self.missing_edge_lengths = 0
        self.clades: list[frozenset[str]] = []

    def skip_ws(self) -> None:
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def label(self) -> str:
        self.skip_ws()
        if self.i < len(self.s) and self.s[self.i] in "'\"":
            q = self.s[self.i]; self.i += 1; out = []
            while self.i < len(self.s):
                c = self.s[self.i]; self.i += 1
                if c == q:
                    if self.i < len(self.s) and self.s[self.i] == q:
                        out.append(q); self.i += 1; continue
                    break
                out.append(c)
            return "".join(out).strip()
        start = self.i
        while self.i < len(self.s) and self.s[self.i] not in ":,();":
            self.i += 1
        return self.s[start:self.i].strip()

    def branch_length(self, *, required: bool) -> None:
        self.skip_ws()
        if self.i >= len(self.s) or self.s[self.i] != ":":
            if required:
                self.missing_edge_lengths += 1
            return
        self.i += 1; self.skip_ws(); start = self.i
        while self.i < len(self.s) and self.s[self.i] not in ",();":
            self.i += 1
        raw = self.s[start:self.i].strip()
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid Newick branch length {raw!r}") from exc
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Branch length must be finite and >=0, observed {value}")
        self.edge_lengths.append(value)

    def subtree(self, *, is_root: bool = False) -> set[str]:
        self.skip_ws()
        if self.i >= len(self.s):
            raise ValueError("Unexpected end of Newick")
        if self.s[self.i] == "(":
            self.i += 1
            descendants = set(self.subtree())
            while True:
                self.skip_ws()
                if self.i < len(self.s) and self.s[self.i] == ",":
                    self.i += 1; descendants.update(self.subtree()); continue
                break
            self.skip_ws()
            if self.i >= len(self.s) or self.s[self.i] != ")":
                raise ValueError("Unbalanced Newick parentheses")
            self.i += 1
            _ = self.label()  # optional internal support/node label
            self.branch_length(required=not is_root)
            self.clades.append(frozenset(descendants))
            return descendants
        lab = self.label()
        if not lab:
            raise ValueError("Leaf tip has empty label")
        self.tips.append(lab)
        self.branch_length(required=True)
        return {lab}

    def parse(self) -> tuple[list[str], list[float], int]:
        self.subtree(is_root=True)
        self.skip_ws()
        if self.i < len(self.s) and self.s[self.i] == ";":
            self.i += 1
        self.skip_ws()
        if self.i != len(self.s):
            raise ValueError(f"Unexpected trailing Newick content at offset {self.i}")
        if len(self.tips) != len(set(self.tips)):
            raise ValueError("Tree contains duplicate tip labels")
        return self.tips, self.edge_lengths, self.missing_edge_lengths


def eligible_atlas_taxa(path: Path) -> tuple[set[str], dict[str, str]]:
    rows = read_csv(path)
    eligible = [r for r in rows if r.get("rate_fit_eligible", "").lower() == "yes"]
    taxa = {r.get("accepted_taxon", "") for r in eligible}
    if len(taxa) != len(eligible):
        raise ValueError("Eligible atlas rows must be unique taxon-level records")
    states = {r["accepted_taxon"]: r["binary_colour_code"].upper() for r in eligible}
    if any(v not in {"C", "W"} for v in states.values()):
        raise ValueError("Eligible atlas taxa must have fixed C/W states")
    return taxa, states


def validate_mapping(path: Path, eligible: set[str], tree_tips: set[str]) -> dict[str, str]:
    rows = read_csv(path)
    required = {"tree_tip", "accepted_taxon", "mapping_status"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Tip map requires columns {sorted(required)}")
    mapping: dict[str, str] = {}
    seen_tips: set[str] = set()
    for row in rows:
        tip, taxon, status = row["tree_tip"], row["accepted_taxon"], row["mapping_status"]
        if status not in ALLOWED_MAPPING:
            raise ValueError(f"Unaccepted mapping_status {status!r} for {tip}")
        if tip in seen_tips or taxon in mapping:
            raise ValueError("Tip map must be one-to-one")
        seen_tips.add(tip); mapping[taxon] = tip
    missing_taxa = sorted(eligible - set(mapping))
    if missing_taxa:
        raise ValueError(f"Eligible atlas taxa missing from tip map: {missing_taxa}")
    missing_tree = sorted({mapping[t] for t in eligible} - tree_tips)
    if missing_tree:
        raise ValueError(f"Mapped tips absent from tree: {missing_tree}")
    return mapping


def validate_provenance(path: Path, tree_sha: str) -> dict[str, object]:
    p = json.loads(path.read_text(encoding="utf-8"))
    if p.get("tree_route") not in ALLOWED_ROUTES:
        raise ValueError("tree_route must be published_exact, compatibility_reanalysis, or independent_reanalysis")
    if p.get("tree_sha256") != tree_sha:
        raise ValueError("Provenance tree_sha256 does not match tree bytes")
    for key in ("analysis_name", "branch_length_interpretation", "rooting_definition", "support_metric_definition", "source_or_pipeline_provenance"):
        if not clean(p.get(key)):
            raise ValueError(f"Tree provenance lacks {key}")
    if p.get("topology_uncertainty_status") not in {"ensemble_available", "bootstrap_or_gene_tree_sensitivity", "single_tree_with_explicit_limitation"}:
        raise ValueError("Tree provenance lacks an accepted topology_uncertainty_status")
    outgroups = p.get("required_outgroup_tips", [])
    if outgroups is None:
        outgroups = []
    if not isinstance(outgroups, list) or any(not isinstance(x, str) or not clean(x) for x in outgroups):
        raise ValueError("required_outgroup_tips must be a list of non-empty strings")
    if len(outgroups) != len(set(outgroups)):
        raise ValueError("required_outgroup_tips contains duplicates")
    p["required_outgroup_tips"] = [clean(x) for x in outgroups]
    return p


def validate(tree: Path, atlas: Path, tip_map: Path, provenance: Path) -> dict[str, object]:
    tree_sha = sha256(tree)
    parser = NewickParser(tree.read_text(encoding="utf-8"))
    tips, lengths, missing = parser.parse()
    tree_tip_set = set(tips)
    if missing:
        raise ValueError(f"Tree has {missing} non-root edges without branch lengths")
    if not lengths or not any(x > 0 for x in lengths):
        raise ValueError("Tree has no positive empirical branch lengths")
    eligible, states = eligible_atlas_taxa(atlas)
    mapping = validate_mapping(tip_map, eligible, tree_tip_set)
    prov = validate_provenance(provenance, tree_sha)

    focal_tips = {mapping[t] for t in eligible}
    required_outgroups = set(prov.get("required_outgroup_tips", []))
    focal_monophyly_checked = bool(required_outgroups)
    if required_outgroups:
        missing_outgroups = sorted(required_outgroups - tree_tip_set)
        if missing_outgroups:
            raise ValueError(f"Required outgroup/reference tips absent from tree: {missing_outgroups}")
        overlap = sorted(required_outgroups & focal_tips)
        if overlap:
            raise ValueError(f"Declared outgroup tips overlap focal atlas tips: {overlap}")
        unexpected_extra = sorted(tree_tip_set - focal_tips - required_outgroups)
        if unexpected_extra:
            raise ValueError(f"Tree contains undeclared extra tips outside focal atlas/outgroups: {unexpected_extra}")
        if frozenset(focal_tips) not in parser.clades:
            raise ValueError("Eligible focal taxa are not monophyletic relative to declared outgroup/reference tips")

    matched = len(eligible)
    return {
        "contract_version": "colour_atlas_branch_length_tree_acceptance_v1",
        "tree_sha256": tree_sha,
        "tree_route": prov["tree_route"],
        "tree_tip_count": len(tips),
        "eligible_atlas_taxa": matched,
        "eligible_state_counts": {"C": sum(v == "C" for v in states.values()), "W": sum(v == "W" for v in states.values())},
        "eligible_taxa_all_mapped": matched == len(mapping),
        "required_outgroup_tips": sorted(required_outgroups),
        "focal_monophyly_checked": focal_monophyly_checked,
        "focal_monophyly_passed": True if focal_monophyly_checked else None,
        "branch_length_edge_count": len(lengths),
        "branch_length_min": min(lengths),
        "branch_length_max": max(lengths),
        "branch_length_interpretation": prov["branch_length_interpretation"],
        "rooting_definition": prov["rooting_definition"],
        "support_metric_definition": prov["support_metric_definition"],
        "topology_uncertainty_status": prov["topology_uncertainty_status"],
        "tree_gate_ready": True,
        "claim_limit": "Tree acceptance validates branch-length/provenance/tip-join integrity and, when declared reference tips are present, focal monophyly relative to those references. It does not imply the colour-state breadth gate passes or that ARD is supported over ER."
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--atlas", type=Path, required=True)
    ap.add_argument("--tip-map", type=Path, required=True)
    ap.add_argument("--provenance", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    out = validate(a.tree, a.atlas, a.tip_map, a.provenance)
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
