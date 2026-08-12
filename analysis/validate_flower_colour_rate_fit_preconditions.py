#!/usr/bin/env python3
"""Evaluate whether empirical flower-colour transition-rate fitting may start.

This gate intentionally combines two independent requirements:

1. the source-backed colour atlas must pass its predeclared taxon/state breadth
   gate; and
2. at least one empirical machine-readable branch-length nuclear tree route
   must satisfy provenance/tip-join requirements.

Passing the gate is necessary, not sufficient, for interpreting ER/ARD/Mk rate
asymmetry. Model adequacy, polymorphism and sampling-bias sensitivity remain
required downstream.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TREE_CONTRACT_VERSION = "flower_colour_rate_tree_contract_v0_1"


def load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def evaluate(atlas: dict[str, object], tree: dict[str, object]) -> dict[str, object]:
    if tree.get("contract_version") != TREE_CONTRACT_VERSION:
        raise ValueError("Unsupported flower-colour tree contract version")

    conditions = atlas.get("readiness_conditions")
    if not isinstance(conditions, dict):
        raise ValueError("Atlas summary lacks readiness_conditions")

    required_atlas_conditions = (
        "minimum_taxon_tips",
        "minimum_white_tips",
        "minimum_coloured_tips",
        "minimum_phylogeny_contexts",
        "all_eligible_are_taxon_level",
        "no_polymorphic_or_unknown_eligible",
    )
    missing = [name for name in required_atlas_conditions if name not in conditions]
    if missing:
        raise ValueError(f"Atlas summary lacks required conditions: {missing}")

    blockers: list[str] = []
    for name in required_atlas_conditions:
        if conditions[name] is not True:
            blockers.append(f"atlas_{name}")

    tree_ready = tree.get("empirical_branch_length_tree_ready") is True
    tree_execution = tree.get("rate_fit_execution_allowed") is True
    if tree_ready != tree_execution:
        raise ValueError(
            "Tree contract empirical_branch_length_tree_ready and "
            "rate_fit_execution_allowed must agree at this precondition layer"
        )
    if not tree_ready:
        blockers.append("branch_length_tree_unavailable")

    published = tree.get("published_tree_route")
    compatibility = tree.get("compatibility_reanalysis_route")
    if not isinstance(published, dict) or not isinstance(compatibility, dict):
        raise ValueError("Tree contract must retain published and compatibility routes")

    if compatibility.get("exact_compositae1061_hybpiper_target_reference_available") is not False:
        raise ValueError(
            "v0.1 source contract must preserve the current unresolved exact Compositae1061 target-reference status"
        )
    if compatibility.get("target_reference_issue") != 16:
        raise ValueError("Compositae1061 target-reference blocker must point to Issue #16")

    execution_allowed = not blockers
    if execution_allowed and atlas.get("transition_rate_fit_ready") is not True:
        raise ValueError("Atlas gate disagrees with combined execution decision")

    return {
        "contract_version": "flower_colour_rate_fit_preconditions_v0_1",
        "atlas_contract_version": atlas.get("contract_version"),
        "eligible_taxa": atlas.get("rate_fit_eligible_unique_taxa"),
        "eligible_state_counts": atlas.get("rate_fit_eligible_state_counts"),
        "atlas_transition_rate_fit_ready": atlas.get("transition_rate_fit_ready"),
        "empirical_branch_length_tree_ready": tree_ready,
        "accepted_tree_route": tree.get("accepted_tree_route"),
        "execution_allowed": execution_allowed,
        "blockers": blockers,
        "moreyra_exact_target_reference_status": compatibility.get("target_reference_status"),
        "next_unlocks": {
            "atlas": "add independently supported fixed-white nuclear tips without collapsing polymorphic taxa",
            "tree": "recover a published branch-length tree ensemble or complete a clearly labelled compatibility reanalysis",
        },
        "claim_limit": (
            "execution_allowed=true is only a prerequisite for empirical transition-rate modelling. "
            "It does not establish ARD over ER, rate asymmetry, ancestral state, coloured regain, "
            "or molecular anthocyanin reactivation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas-summary", type=Path, required=True)
    parser.add_argument("--tree-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = evaluate(load_json(args.atlas_summary), load_json(args.tree_contract))
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
