#!/usr/bin/env python3
"""Evaluate whether empirical flower-colour transition-rate fitting may start.

The gate combines two independent requirements:

1. the source-backed colour atlas must pass its predeclared taxon/state breadth
   gate; and
2. at least one empirical machine-readable branch-length nuclear tree route
   must satisfy provenance/tip-join/rooting/topology-uncertainty requirements.

The compatibility tree route is now complete: a frozen 153-locus Carthamus-rooted
primary tree has accepted branch lengths, and deterministic gCF/sCF plus a
preregistered 3x3 AU test retain six local topology candidates.  The tree gate
therefore passes while topology uncertainty remains explicit.  The independent
atlas minimum-white-tip gate remains load-bearing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TREE_CONTRACT_VERSION = "flower_colour_rate_tree_contract_v0_2"
EXPECTED_COMP1061_SHA256 = "77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c"
EXPECTED_COMP1061_LOCI = 1061
EXPECTED_TARGET_STATUS = "original_compatible_reference_recovered_augmented_not_recovered"
EXPECTED_PRIMARY_TREE_SHA256 = "c80b66c1e19c91287d3fa243360ae1f4ab6a28613e2d8f1914c23565788bcac5"
EXPECTED_TREE_LOCI = 153
EXPECTED_TREE_LOCI_SHA256 = "1106051eca8bfa699f16e05d92024573cb358d7dbd151b89768e76c3d56cde82"
EXPECTED_TOPOLOGY_CONCORDANCE_RUN = 32614242600
EXPECTED_ALT_TOPOLOGY_RUN = 32614839764
EXPECTED_ALT_TOPOLOGY_ARTIFACT_DIGEST = "sha256:d90f30e4fcc3a2a0296a7d0cfa13d0f3ecc008b36d28298ac9782a001e6f63c5"
EXPECTED_AU_NONREJECTED_TOPOLOGIES = 6


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

    if compatibility.get("original_comp1061_hybpiper_reference_available") is not True:
        raise ValueError("Original compatible Compositae1061 reference recovery was lost")
    if compatibility.get("original_comp1061_reference_sha256") != EXPECTED_COMP1061_SHA256:
        raise ValueError("Original compatible Compositae1061 reference SHA256 drifted")
    if compatibility.get("original_comp1061_reference_locus_count") != EXPECTED_COMP1061_LOCI:
        raise ValueError("Original compatible Compositae1061 locus count drifted")
    if compatibility.get("exact_moreyra_augmented_reference_available") is not False:
        raise ValueError("Exact Moreyra augmented reference must remain unrecovered until sourced")
    if compatibility.get("target_reference_status") != EXPECTED_TARGET_STATUS:
        raise ValueError("Compositae1061 target/reference status drifted")
    if compatibility.get("compatibility_raw_read_target_blocked") is not False:
        raise ValueError("Recovered original reference should remove the raw-read target blocker")
    if compatibility.get("target_reference_issue") != 16:
        raise ValueError("Compositae1061 target/reference provenance must point to Issue #16")

    if tree_ready:
        if compatibility.get("compatibility_branch_length_tree_available") is not True:
            raise ValueError("Tree-ready contract lost the compatibility branch-length tree")
        if compatibility.get("tree_loci") != EXPECTED_TREE_LOCI:
            raise ValueError("Frozen compatibility-tree locus count drifted")
        if compatibility.get("tree_loci_sha256") != EXPECTED_TREE_LOCI_SHA256:
            raise ValueError("Frozen compatibility-tree locus-list SHA256 drifted")
        if compatibility.get("primary_tree_sha256") != EXPECTED_PRIMARY_TREE_SHA256:
            raise ValueError("Accepted primary tree SHA256 drifted")
        if compatibility.get("root_outgroup") != "OUTGROUP_saff":
            raise ValueError("Accepted tree must retain the sole Carthamus root tip")
        if compatibility.get("topology_concordance_run_id") != EXPECTED_TOPOLOGY_CONCORDANCE_RUN:
            raise ValueError("Deterministic topology-concordance source run drifted")
        if compatibility.get("alternative_topology_run_id") != EXPECTED_ALT_TOPOLOGY_RUN:
            raise ValueError("Alternative-topology source run drifted")
        if compatibility.get("alternative_topology_artifact_digest") != EXPECTED_ALT_TOPOLOGY_ARTIFACT_DIGEST:
            raise ValueError("Alternative-topology artifact digest drifted")
        if compatibility.get("au_nonrejected_topology_count") != EXPECTED_AU_NONREJECTED_TOPOLOGIES:
            raise ValueError("AU-nonrejected topology count drifted")
        candidates = compatibility.get("au_nonrejected_candidate_ids")
        if not isinstance(candidates, list) or len(candidates) != EXPECTED_AU_NONREJECTED_TOPOLOGIES:
            raise ValueError("Tree-ready contract must preserve all six AU-nonrejected candidate IDs")
        if compatibility.get("primary_topology_is_maximum_likelihood") is not True:
            raise ValueError("Primary topology must remain the maximum-likelihood reference")
        if compatibility.get("primary_topology_uniquely_supported") is not False:
            raise ValueError("Tree contract must not overclaim a unique topology")
        if compatibility.get("topology_uncertainty_must_propagate") is not True:
            raise ValueError("Tree-ready contract must propagate topology uncertainty")
        if tree.get("remaining_tree_blockers") != []:
            raise ValueError("Tree-ready contract cannot retain a hidden tree blocker")

    execution_allowed = not blockers
    if execution_allowed and atlas.get("transition_rate_fit_ready") is not True:
        raise ValueError("Atlas gate disagrees with combined execution decision")

    return {
        "contract_version": "flower_colour_rate_fit_preconditions_v0_2",
        "atlas_contract_version": atlas.get("contract_version"),
        "tree_contract_version": tree.get("contract_version"),
        "eligible_taxa": atlas.get("rate_fit_eligible_unique_taxa"),
        "eligible_state_counts": atlas.get("rate_fit_eligible_state_counts"),
        "atlas_transition_rate_fit_ready": atlas.get("transition_rate_fit_ready"),
        "empirical_branch_length_tree_ready": tree_ready,
        "accepted_tree_route": tree.get("accepted_tree_route"),
        "primary_tree_sha256": compatibility.get("primary_tree_sha256"),
        "tree_loci": compatibility.get("tree_loci"),
        "root_outgroup": compatibility.get("root_outgroup"),
        "topology_uncertainty_completed": tree_ready,
        "au_nonrejected_topology_count": compatibility.get("au_nonrejected_topology_count"),
        "primary_topology_uniquely_supported": compatibility.get("primary_topology_uniquely_supported"),
        "execution_allowed": execution_allowed,
        "blockers": blockers,
        "comp1061_original_reference_available": True,
        "comp1061_original_reference_sha256": EXPECTED_COMP1061_SHA256,
        "comp1061_original_reference_locus_count": EXPECTED_COMP1061_LOCI,
        "moreyra_augmented_reference_available": False,
        "target_reference_status": compatibility.get("target_reference_status"),
        "next_unlocks": {
            "atlas": "add two independently supported fixed-white nuclear species tips without collapsing polymorphic taxa",
            "tree": "tree gate satisfied; retain the primary branch-length tree plus all six AU-nonrejected local topology candidates in topology-sensitive downstream inference",
        },
        "claim_limit": (
            "execution_allowed=true is only a prerequisite for empirical transition-rate modelling. "
            "It does not establish ARD over ER, rate asymmetry, ancestral state, coloured regain, "
            "or molecular anthocyanin reactivation. The primary branch-length tree is not a uniquely "
            "supported topology; topology-sensitive inference must preserve the frozen uncertainty set."
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
