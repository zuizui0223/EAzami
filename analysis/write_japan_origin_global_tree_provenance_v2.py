#!/usr/bin/env python3
"""Write provenance for the 294-tip concatenated Japan-origin nuclear tree."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--concat-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = json.loads(args.concat_summary.read_text(encoding="utf-8"))
    references = summary.get("reference_tips", [])
    if not references:
        raise ValueError("concat summary has no reference_tips")

    provenance = {
        "tree_sha256": hashlib.sha256(args.tree.read_bytes()).hexdigest(),
        "analysis_name": "EAzami 294-tip deduplicated global public Cirsium origin compatibility tree",
        "branch_length_interpretation": (
            "IQ-TREE maximum-likelihood substitutions per site on concatenated "
            "Compositae1061-compatible coding-sequence alignment"
        ),
        "rooting_definition": (
            "OUTGROUP_lett and OUTGROUP_sunf define the root; OUTGROUP_saff is "
            "retained as an optional near-Cardueae reference"
        ),
        "required_outgroup_tips": ["OUTGROUP_lett", "OUTGROUP_sunf"],
        "required_reference_tips": references,
        "support_metric_definition": (
            "IQ-TREE ultrafast bootstrap 1000 plus SH-aLRT 1000; ASTRAL-III "
            "species tree is retained as a coalescent sensitivity"
        ),
        "source_or_pipeline_provenance": (
            "294 unique public biological samples / 295 unique SRRs from Moreyra "
            "2025 plus deduplicated Chang 2025/2026; original Compositae1061 "
            "reference; strict frozen-241 current occupancy >=0.80 and zero-current-"
            "paralog admission; HybPiper 2.3.4; MAFFT; IQ-TREE; ASTRAL-III 5.7.8"
        ),
        "topology_uncertainty_status": "bootstrap_plus_gene_tree_astral_sensitivity",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(provenance, indent=2) + chr(10), encoding="utf-8")
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
