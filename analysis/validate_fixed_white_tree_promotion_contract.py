#!/usr/bin/env python3
"""Validate fixed-white promotion from the current 20-tip tree to the final W>=5 tree.

This is an execution-design validator, not evidence that new sequencing exists.
The active v0.2 contract freezes external sample intake, sample-level recovery,
replicate placement, representative selection and expanded-tree reacceptance
before the two A1 fixed-white taxa are observed in the homologous Comp1061 matrix.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = ROOT / "analysis" / "cirsium_flower_colour_atlas_v0_3_readiness.json"
DEFAULT_TREE = ROOT / "data" / "evidence" / "flower_colour_rate_tree_contract_v0_2.json"
DEFAULT_PANEL = ROOT / "sampling" / "FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv"
DEFAULT_PRIORITY = ROOT / "data" / "evidence" / "fixed_white_a1_priority_v2.csv"
EXPECTED_INTAKE = "sampling/FIXED_WHITE_A1_SAMPLE_INTAKE_V0_1.csv"
EXPECTED_INTAKE_VALIDATOR = "analysis/validate_fixed_white_a1_sample_intake.py"
EXPECTED_RECOVERY_EVALUATOR = "analysis/evaluate_fixed_white_a1_recovery_qc.py"
EXPECTED_RECOVERY_COLUMNS = [
    "immutable_sample_id",
    "taxon",
    "frozen_loci",
    "recovered_frozen_loci",
    "paralog_warning_frozen_loci",
    "clean_recovered_frozen_loci",
    "non_gap_aligned_bp",
]

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
    atlas_path: Path = DEFAULT_ATLAS,
    tree_path: Path = DEFAULT_TREE,
    panel_path: Path = DEFAULT_PANEL,
    priority_path: Path = DEFAULT_PRIORITY,
) -> dict[str, object]:
    c = load_json(contract_path)
    atlas = load_json(atlas_path)
    tree = load_json(tree_path)
    panel = read_csv(panel_path)
    priority = read_csv(priority_path)

    if c.get("contract_version") != "fixed_white_tree_promotion_v0_2":
        raise ValueError("contract version drift")

    source = c["source_state"]
    if atlas.get("rate_fit_eligible_unique_taxa") != 20:
        raise ValueError("promotion contract assumes the frozen current 20-taxon atlas")
    if atlas.get("rate_fit_eligible_state_counts") != {"C": 17, "W": 3}:
        raise ValueError("current atlas state counts drifted from C=17/W=3")
    if atlas.get("readiness_blockers") != ["minimum_white_tips"]:
        raise ValueError("current atlas must remain blocked only by minimum_white_tips")
    if source.get("current_eligible_taxa") != 20 or source.get("current_state_counts") != {"C": 17, "W": 3}:
        raise ValueError("promotion source state disagrees with current atlas")
    if source.get("current_rate_blocker") != "minimum_white_tips":
        raise ValueError("promotion source blocker drifted")

    if tree.get("contract_version") != "flower_colour_rate_tree_contract_v0_2":
        raise ValueError("promotion contract requires current rate-tree contract v0.2")
    if tree.get("empirical_branch_length_tree_ready") is not True:
        raise ValueError("current tree gate must be ready before white-tip expansion")
    compatibility = tree["compatibility_reanalysis_route"]
    if compatibility.get("focal_taxa") != 20:
        raise ValueError("current accepted tree must have 20 focal taxa")
    if set(compatibility.get("focal_taxa_accepted_names", [])) != set(atlas.get("rate_fit_eligible_taxa", [])):
        raise ValueError("current tree/atlas taxon join is not exact")
    if compatibility.get("tree_loci") != EXPECTED_LOCI:
        raise ValueError("current tree locus count drifted")
    if compatibility.get("tree_loci_sha256") != EXPECTED_LOCI_SHA256:
        raise ValueError("current frozen locus SHA256 drifted")
    if compatibility.get("primary_tree_sha256") != EXPECTED_PRIMARY_TREE_SHA256:
        raise ValueError("current primary tree SHA256 drifted")
    if compatibility.get("root_outgroup") != EXPECTED_ROOT:
        raise ValueError("current root outgroup drifted")
    if source.get("current_tree_loci") != EXPECTED_LOCI or source.get("current_tree_loci_sha256") != EXPECTED_LOCI_SHA256:
        raise ValueError("promotion source locus contract drifted")
    if source.get("current_primary_tree_sha256") != EXPECTED_PRIMARY_TREE_SHA256:
        raise ValueError("promotion source primary tree drifted")
    if source.get("root_outgroup") != EXPECTED_ROOT:
        raise ValueError("promotion source root drifted")

    a1_panel = [row for row in panel if row.get("decision_tier") == "A1"]
    if len(a1_panel) != 2 or {row["taxon"] for row in a1_panel} != EXPECTED_A1:
        raise ValueError("sampling panel A1 must remain boninense + wulongense")
    for row in a1_panel:
        if row.get("preferred_target_set") != "Compositae1061":
            raise ValueError(f"{row['taxon']}: preferred target set drifted")
        if int(row.get("minimum_individuals", "0")) < 2:
            raise ValueError(f"{row['taxon']}: fewer than two minimum individuals")
        if row.get("voucher_required") != "yes" or row.get("flower_colour_link_required") != "yes":
            raise ValueError(f"{row['taxon']}: voucher/colour linkage was weakened")

    priority_a1 = {row["taxon"]: row for row in priority if row.get("candidate_id") in {"WREC01", "WREC02"}}
    if set(priority_a1) != EXPECTED_A1:
        raise ValueError("public-recovery priority lost an A1 species")
    for taxon, row in priority_a1.items():
        if row.get("rate_fit_tip_promotion_allowed") != "false":
            raise ValueError(f"{taxon}: public recovery priority prematurely permits promotion")

    a1 = c["a1_panel"]
    if set(a1.get("taxa", [])) != EXPECTED_A1:
        raise ValueError("promotion contract A1 taxa drifted")
    if a1.get("minimum_individuals_per_taxon") != 2 or a1.get("ideal_individuals_per_taxon") != 3:
        raise ValueError("promotion contract replicate counts drifted")
    if a1.get("preferred_target_set") != "Compositae1061":
        raise ValueError("promotion contract target set drifted")
    if a1.get("voucher_required") is not True or a1.get("flower_colour_link_required") is not True:
        raise ValueError("promotion contract must require voucher and flower-colour linkage")
    if a1.get("sample_intake_manifest") != EXPECTED_INTAKE:
        raise ValueError("promotion contract lost canonical A1 intake manifest")
    if a1.get("sample_intake_validator") != EXPECTED_INTAKE_VALIDATOR:
        raise ValueError("promotion contract lost canonical A1 intake validator")
    if a1.get("current_available_external_samples") != {
        "Cirsium boninense": 0,
        "Cirsium wulongense": 0,
    }:
        raise ValueError("contract must not claim external A1 samples before they are acquired")
    if a1.get("current_public_homologous_tip_count") != 0 or a1.get("current_promotion_allowed") is not False:
        raise ValueError("A1 taxa must not be represented as already promoted")

    recovery = c["individual_recovery_gate"]
    if recovery.get("frozen_locus_count") != EXPECTED_LOCI:
        raise ValueError("individual gate must use all 153 frozen loci")
    if recovery.get("frozen_locus_sha256") != EXPECTED_LOCI_SHA256:
        raise ValueError("individual gate frozen locus SHA256 drifted")
    if recovery.get("recovery_qc_evaluator") != EXPECTED_RECOVERY_EVALUATOR:
        raise ValueError("individual gate lost canonical recovery evaluator")
    if recovery.get("recovery_qc_required_columns") != EXPECTED_RECOVERY_COLUMNS:
        raise ValueError("individual recovery QC schema drifted")
    fraction = recovery.get("minimum_clean_recovered_fraction")
    if fraction != 0.8:
        raise ValueError("individual clean-recovery fraction must remain 0.8")
    expected_min = math.ceil(EXPECTED_LOCI * fraction)
    if expected_min != 123 or recovery.get("minimum_clean_recovered_loci") != expected_min:
        raise ValueError("individual clean-recovery locus threshold must remain ceil(0.8*153)=123")
    if recovery.get("posthoc_locus_addition_allowed") is not False or recovery.get("posthoc_locus_removal_allowed") is not False:
        raise ValueError("future white samples must not trigger post hoc locus reselection")
    if "Mask only the affected new individual" not in recovery.get("paralog_handling", ""):
        raise ValueError("paralog handling must mask the individual, not delete the locus")
    if "missing/gaps" not in recovery.get("unrecovered_locus_handling", ""):
        raise ValueError("unrecovered loci must remain missing rather than trigger locus replacement")
    mapping = recovery["mapping_contract"]
    if mapping != {
        "target_reference": "original public Compositae1061 HybPiper reference",
        "hybpiper_version": "2.3.4",
        "read_mapper": "BWA",
        "sequence_type": "DNA",
    }:
        raise ValueError("white-tip mapping contract drifted from the empirical recovery lane")

    replicate = c["replicate_identity_gate"]
    if replicate.get("minimum_passing_individuals_per_promoted_taxon") != 2:
        raise ValueError("at least two passing individuals must be required")
    if replicate.get("minimum_sample_tips_in_replicate_expanded_tree", 0) < 24:
        raise ValueError("replicate-expanded placement tree must contain at least 24 focal sample tips")
    if "never counted as multiple white macroevolutionary tips" not in replicate.get("state_counting_rule", ""):
        raise ValueError("pseudo-replication guard missing")
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
        raise ValueError("replicate identity linkage was weakened")
    placement_rule = replicate.get("placement_concordance_rule", "")
    if "all topology candidates retained" not in placement_rule or "stop condition" not in placement_rule:
        raise ValueError("replicate placement rule must remain topology-sensitive and fail closed")

    representative = c["species_representative_rule"]
    if representative.get("applies_only_after_replicate_identity_gate_passes") is not True:
        raise ValueError("representative selection occurs before the placement gate")
    if representative.get("selection_order") != [
        "highest clean recovered frozen-153 locus count",
        "highest non-gap aligned base count across the frozen-153 matrix",
        "lexicographically smallest immutable sample ID",
    ]:
        raise ValueError("species representative QC selection order drifted")
    if representative.get("trait_or_topology_preference_allowed") is not False:
        raise ValueError("representative choice cannot use trait/topology preference")
    forbidden = "|".join(representative.get("forbidden_criteria", [])).lower()
    if "er versus ard" not in forbidden or "arenicola" not in forbidden:
        raise ValueError("hypothesis-aware representative selection guard missing")
    if representative.get("one_rate_tree_tip_per_species") is not True:
        raise ValueError("final macro tree must retain one tip per promoted species")
    if representative.get("replicates_are_not_independent_macroevolutionary_transitions") is not True:
        raise ValueError("replicates cannot count as independent transitions")

    expanded = c["expanded_tree_gate"]
    if expanded.get("target_focal_taxa") != 22:
        raise ValueError("expanded final tree must contain 22 focal taxa")
    if expanded.get("target_state_counts") != {"C": 17, "W": 5}:
        raise ValueError("expanded state target must remain C=17/W=5")
    if expanded.get("target_tree_tip_count_with_root") != 23:
        raise ValueError("expanded tree must contain 22 focal taxa plus the sole root")
    if expanded.get("root_outgroup") != EXPECTED_ROOT:
        raise ValueError("expanded tree root drifted")
    if "same frozen 153 loci" not in expanded.get("locus_policy", ""):
        raise ValueError("expanded tree must retain the same frozen 153 loci")
    if "do not graft" not in expanded.get("tree_inference_policy", ""):
        raise ValueError("final branch-length tree must be re-inferred, not grafted")
    if expanded.get("must_pass_branch_length_acceptance") is not True or expanded.get("must_pass_rate_fit_preconditions") is not True:
        raise ValueError("expanded final gates missing")
    if expanded.get("rate_fit_unlock_requires_expanded_tree_reacceptance") is not True:
        raise ValueError("expanded tree reacceptance must remain load-bearing")
    if "exactly the same accepted taxon names" not in expanded.get("tip_join_policy", ""):
        raise ValueError("expanded atlas/tree exact tip join must remain required")

    decision = c["decision"]
    if decision.get("sampling_or_public_data_recovery_may_proceed") is not True:
        raise ValueError("promotion contract should permit data acquisition")
    if decision.get("current_a1_species_promoted") != 0:
        raise ValueError("no A1 species is currently promoted")
    if decision.get("current_rate_fit_execution_allowed") is not False:
        raise ValueError("rate fitting must remain blocked")
    if "mandatory intake slots" not in decision.get("next_data_requirement", ""):
        raise ValueError("next data requirement must route through canonical intake slots")

    return {
        "contract_version": c["contract_version"],
        "a1_taxa": sorted(EXPECTED_A1),
        "current_taxa": 20,
        "current_state_counts": {"C": 17, "W": 3},
        "current_tree_focal_taxa": 20,
        "external_samples_available": 0,
        "sample_intake_manifest": EXPECTED_INTAKE,
        "placement_min_sample_tips": replicate["minimum_sample_tips_in_replicate_expanded_tree"],
        "frozen_loci": EXPECTED_LOCI,
        "minimum_clean_recovered_loci_per_individual": expected_min,
        "minimum_passing_individuals_per_taxon": 2,
        "recovery_qc_evaluator": EXPECTED_RECOVERY_EVALUATOR,
        "final_taxa": 22,
        "final_states": {"C": 17, "W": 5},
        "target_tree_tips_with_root": 23,
        "current_rate_fit_execution_allowed": False,
        "next_gate": "populate_mandatory_A1_intake_slots",
        "valid": True,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("contract", type=Path)
    p.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    p.add_argument("--tree-contract", type=Path, default=DEFAULT_TREE)
    p.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    p.add_argument("--priority", type=Path, default=DEFAULT_PRIORITY)
    a = p.parse_args()
    result = validate(a.contract, a.atlas, a.tree_contract, a.panel, a.priority)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
