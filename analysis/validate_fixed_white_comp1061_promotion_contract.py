#!/usr/bin/env python3
"""Validate the predeclared fixed-white Comp1061 promotion contract.

This validator does not claim that new samples exist.  It locks the procedure
that future C. boninense / C. wulongense data must satisfy before either taxon
can become a species-level rate-tree tip.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

EXPECTED_A1 = {"Cirsium boninense", "Cirsium wulongense"}
EXPECTED_LOCI = 153
EXPECTED_LOCI_SHA256 = "1106051eca8bfa699f16e05d92024573cb358d7dbd151b89768e76c3d56cde82"
EXPECTED_PRIMARY_TREE_SHA256 = "c80b66c1e19c91287d3fa243360ae1f4ab6a28613e2d8f1914c23565788bcac5"
EXPECTED_ROOT = "OUTGROUP_saff"


def load_json(path: Path) -> dict[str, object]:
    x = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(x, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return x


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {k: str(v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(handle)
            if any(str(v or "").strip() for v in row.values())
        ]


def validate(
    contract_path: Path,
    atlas_path: Path,
    tree_path: Path,
    panel_path: Path,
    priority_path: Path,
) -> dict[str, object]:
    c = load_json(contract_path)
    atlas = load_json(atlas_path)
    tree = load_json(tree_path)
    panel = read_csv(panel_path)
    priority = read_csv(priority_path)

    if c.get("contract_version") != "fixed_white_comp1061_promotion_contract_v1":
        raise ValueError("Unexpected promotion contract version")

    source = c["source_state"]
    if atlas.get("rate_fit_eligible_unique_taxa") != 20:
        raise ValueError("Promotion contract assumes the frozen current 20-taxon atlas")
    if atlas.get("rate_fit_eligible_state_counts") != {"C": 17, "W": 3}:
        raise ValueError("Current atlas state counts drifted from C=17/W=3")
    if atlas.get("readiness_blockers") != ["minimum_white_tips"]:
        raise ValueError("Current atlas must remain blocked only by minimum_white_tips")
    if source.get("current_eligible_taxa") != 20 or source.get("current_state_counts") != {"C": 17, "W": 3}:
        raise ValueError("Promotion source state disagrees with current atlas")

    if tree.get("contract_version") != "flower_colour_rate_tree_contract_v0_2":
        raise ValueError("Promotion contract requires current rate-tree contract v0.2")
    if tree.get("empirical_branch_length_tree_ready") is not True:
        raise ValueError("Current tree gate must be ready before white-tip expansion")
    compatibility = tree["compatibility_reanalysis_route"]
    if compatibility.get("focal_taxa") != 20:
        raise ValueError("Current accepted tree must have 20 focal taxa")
    if set(compatibility.get("focal_taxa_accepted_names", [])) != set(atlas.get("rate_fit_eligible_taxa", [])):
        raise ValueError("Current tree/atlas taxon join is not exact")
    if compatibility.get("tree_loci") != EXPECTED_LOCI:
        raise ValueError("Current tree locus count drifted")
    if compatibility.get("tree_loci_sha256") != EXPECTED_LOCI_SHA256:
        raise ValueError("Current frozen locus SHA256 drifted")
    if compatibility.get("primary_tree_sha256") != EXPECTED_PRIMARY_TREE_SHA256:
        raise ValueError("Current primary tree SHA256 drifted")
    if compatibility.get("root_outgroup") != EXPECTED_ROOT:
        raise ValueError("Current root outgroup drifted")

    a1_panel = [row for row in panel if row.get("decision_tier") == "A1"]
    if len(a1_panel) != 2 or {row["taxon"] for row in a1_panel} != EXPECTED_A1:
        raise ValueError("Sampling panel A1 must remain boninense + wulongense")
    for row in a1_panel:
        if row.get("preferred_target_set") != "Compositae1061":
            raise ValueError(f"{row['taxon']}: preferred target set drifted")
        if int(row.get("minimum_individuals", "0")) < 2:
            raise ValueError(f"{row['taxon']}: fewer than two minimum individuals")
        if row.get("voucher_required") != "yes" or row.get("flower_colour_link_required") != "yes":
            raise ValueError(f"{row['taxon']}: voucher/colour linkage was weakened")

    priority_a1 = {row["taxon"]: row for row in priority if row.get("candidate_id") in {"WREC01", "WREC02"}}
    if set(priority_a1) != EXPECTED_A1:
        raise ValueError("Public-recovery priority lost an A1 species")
    for taxon, row in priority_a1.items():
        if row.get("rate_fit_tip_promotion_allowed") != "false":
            raise ValueError(f"{taxon}: public recovery priority prematurely permits promotion")

    a1 = c["a1_panel"]
    if set(a1.get("taxa", [])) != EXPECTED_A1:
        raise ValueError("Promotion contract A1 taxa drifted")
    if a1.get("minimum_individuals_per_taxon") != 2 or a1.get("ideal_individuals_per_taxon") != 3:
        raise ValueError("Promotion contract replicate counts drifted")
    if a1.get("preferred_target_set") != "Compositae1061":
        raise ValueError("Promotion contract target set drifted")
    if a1.get("voucher_required") is not True or a1.get("flower_colour_link_required") is not True:
        raise ValueError("Promotion contract must require voucher and flower-colour linkage")
    if a1.get("current_public_homologous_tip_count") != 0 or a1.get("current_promotion_allowed") is not False:
        raise ValueError("A1 taxa must not be represented as already promoted")

    recovery = c["individual_recovery_gate"]
    if recovery.get("frozen_locus_count") != EXPECTED_LOCI:
        raise ValueError("Individual gate must use all 153 frozen loci")
    if recovery.get("frozen_locus_sha256") != EXPECTED_LOCI_SHA256:
        raise ValueError("Individual gate frozen locus SHA256 drifted")
    fraction = recovery.get("minimum_clean_recovered_fraction")
    if fraction != 0.8:
        raise ValueError("Individual clean-recovery fraction must remain 0.8")
    expected_min = math.ceil(EXPECTED_LOCI * fraction)
    if expected_min != 123 or recovery.get("minimum_clean_recovered_loci") != expected_min:
        raise ValueError("Individual clean-recovery locus threshold must remain ceil(0.8*153)=123")
    if recovery.get("posthoc_locus_addition_allowed") is not False or recovery.get("posthoc_locus_removal_allowed") is not False:
        raise ValueError("Future white samples must not trigger post hoc locus reselection")
    if "Mask only the affected new individual" not in recovery.get("paralog_handling", ""):
        raise ValueError("Paralog handling must mask the individual, not delete the locus")
    mapping = recovery["mapping_contract"]
    if mapping != {
        "target_reference": "original public Compositae1061 HybPiper reference",
        "hybpiper_version": "2.3.4",
        "read_mapper": "BWA",
        "sequence_type": "DNA",
    }:
        raise ValueError("White-tip mapping contract drifted from the empirical recovery lane")

    replicate = c["replicate_identity_gate"]
    if replicate.get("minimum_passing_individuals_per_promoted_taxon") != 2:
        raise ValueError("At least two passing individuals must be required")
    linkage = set(replicate.get("required_linkage", []))
    required_linkage = {
        "accepted taxon concept",
        "voucher or unambiguous herbarium identifier",
        "flower-colour record linked to the sequenced individual",
        "locality",
        "collection or specimen provenance",
        "raw sequencing accession after deposition",
    }
    if not required_linkage.issubset(linkage):
        raise ValueError("Replicate identity linkage was weakened")
    placement_rule = replicate.get("placement_concordance_rule", "")
    if "all topology candidates retained" not in placement_rule or "stop condition" not in placement_rule:
        raise ValueError("Replicate placement rule must remain topology-sensitive and fail closed")

    representative = c["species_representative_rule"]
    if representative.get("selection_order") != [
        "highest clean recovered frozen-153 locus count",
        "highest non-gap aligned base count across the frozen-153 matrix",
        "lexicographically smallest immutable sample ID",
    ]:
        raise ValueError("Species representative QC selection order drifted")
    if representative.get("trait_or_topology_preference_allowed") is not False:
        raise ValueError("Representative choice cannot use trait/topology preference")
    if representative.get("one_rate_tree_tip_per_species") is not True:
        raise ValueError("Final macro tree must retain one tip per promoted species")
    if representative.get("replicates_are_not_independent_macroevolutionary_transitions") is not True:
        raise ValueError("Replicates cannot count as independent transitions")

    expanded = c["expanded_tree_gate"]
    if expanded.get("target_focal_taxa") != 22:
        raise ValueError("Expanded final tree must contain 22 focal taxa")
    if expanded.get("target_state_counts") != {"C": 17, "W": 5}:
        raise ValueError("Expanded state target must remain C=17/W=5")
    if expanded.get("target_tree_tip_count_with_root") != 23:
        raise ValueError("Expanded tree must contain 22 focal taxa plus the sole root")
    if expanded.get("root_outgroup") != EXPECTED_ROOT:
        raise ValueError("Expanded tree root drifted")
    if "same frozen 153 loci" not in expanded.get("locus_policy", ""):
        raise ValueError("Expanded tree must retain the same frozen 153 loci")
    if expanded.get("rate_fit_unlock_requires_expanded_tree_reacceptance") is not True:
        raise ValueError("Expanded tree reacceptance must remain load-bearing")
    if "exactly the same accepted taxon names" not in expanded.get("tip_join_policy", ""):
        raise ValueError("Expanded atlas/tree exact tip join must remain required")

    decision = c["decision"]
    if decision.get("sampling_or_public_data_recovery_may_proceed") is not True:
        raise ValueError("Promotion contract should permit data acquisition")
    if decision.get("current_a1_species_promoted") != 0:
        raise ValueError("No A1 species is currently promoted")
    if decision.get("current_rate_fit_execution_allowed") is not False:
        raise ValueError("Rate fitting must remain blocked")

    return {
        "contract_version": c["contract_version"],
        "a1_taxa": sorted(EXPECTED_A1),
        "current_state_counts": {"C": 17, "W": 3},
        "current_tree_focal_taxa": 20,
        "frozen_loci": EXPECTED_LOCI,
        "minimum_clean_recovered_loci_per_individual": expected_min,
        "minimum_passing_individuals_per_taxon": 2,
        "target_state_counts": {"C": 17, "W": 5},
        "target_focal_taxa": 22,
        "target_tree_tips_with_root": 23,
        "current_rate_fit_execution_allowed": False,
        "next_gate": "recover_or_generate_homologous_A1_nuclear_data",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--atlas", type=Path, required=True)
    p.add_argument("--tree-contract", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--priority", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(validate(a.contract, a.atlas, a.tree_contract, a.panel, a.priority), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
