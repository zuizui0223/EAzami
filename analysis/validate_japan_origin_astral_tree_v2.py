#!/usr/bin/env python3
"""Validate the deduplicated Japan-origin ASTRAL sensitivity tree.

This gate checks artifact completeness only. It deliberately does not encode a
preferred Japanese or Ryukyu topology as an acceptance criterion.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def leaf_tips(text: str) -> list[str]:
    """Return unquoted safe leaf labels from an ASTRAL Newick tree."""
    return re.findall(r"(?<=[(,])\s*([A-Za-z0-9_]+)\s*(?=[:),])", text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--species-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.species_map.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or not {"species_id", "analysis_taxon_label", "tip_ids"} <= set(rows[0]):
        raise ValueError("species map is empty or incomplete")

    focal = {row["species_id"] for row in rows}
    seen_list = leaf_tips(args.tree.read_text(encoding="utf-8"))
    seen = set(seen_list)
    required_outgroups = {"OUTGROUP_lett", "OUTGROUP_sunf"}
    optional = {"OUTGROUP_saff"}
    allowed = focal | required_outgroups | optional

    if required_outgroups - seen:
        raise ValueError(f"ASTRAL required outgroups missing: {sorted(required_outgroups - seen)}")
    if focal - seen:
        raise ValueError(f"ASTRAL missing {len(focal - seen)} mapped source-label taxa")
    if seen - allowed:
        raise ValueError(f"ASTRAL unexpected tips: {sorted(seen - allowed)[:10]}")
    if len(seen_list) != len(seen):
        raise ValueError("ASTRAL output has duplicate tip labels")

    out = {
        "contract_version": "japan_origin_astral_tree_acceptance_v2",
        "tree_sha256": hashlib.sha256(args.tree.read_bytes()).hexdigest(),
        "mapped_source_label_taxa": len(focal),
        "tree_tips": len(seen),
        "required_outgroups_present": True,
        "tree_artifact_accepted": True,
        "rooting_status": (
            "ASTRAL output is treated as unrooted; root downstream with "
            "OUTGROUP_lett/OUTGROUP_sunf before biogeographic interpretation."
        ),
        "claim_limit": (
            "ASTRAL sensitivity does not by itself establish dispersal direction, "
            "Japanese monophyly or Arenicola origin."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + chr(10), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
