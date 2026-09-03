#!/usr/bin/env python3
"""Quantify topology-wise ordering of frozen Chapter 2 relative-depth envelopes.

This is a post-result robustness analysis. It reuses the exact frozen ML/UFBoot
ensemble and trait-state admission rules from japan38_relative_event_depth_v1.
The primary estimand is paired across the same bootstrap topology: the lower
bound of mean relative lineage depth across all globally minimum-cost histories.
Smaller D means that a trait permits a deeper mean placement.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import statistics
from io import StringIO
from pathlib import Path

import Bio
from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
DEPTH_SPEC = importlib.util.spec_from_file_location(
    "relative_depth",
    ROOT / "analysis" / "summarize_japan38_relative_event_depth_v1.py",
)
assert DEPTH_SPEC and DEPTH_SPEC.loader
DEPTH = importlib.util.module_from_spec(DEPTH_SPEC)
DEPTH_SPEC.loader.exec_module(DEPTH)

TRAITS = ("orientation", "phyllary", "stickiness")
TOL = 1e-12


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nearest_rank(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("nearest_rank requires non-empty values")
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
    return float(ordered[idx])


def summary(values: list[float]) -> dict:
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError("summary requires finite non-empty values")
    return {
        "n": len(values),
        "min": min(values),
        "q05": nearest_rank(values, 0.05),
        "median": statistics.median(values),
        "q95": nearest_rank(values, 0.95),
        "max": max(values),
    }


def cmp_fraction(values: list[float]) -> dict:
    n = len(values)
    lt = sum(v < -TOL for v in values)
    eq = sum(abs(v) <= TOL for v in values)
    gt = n - lt - eq
    return {
        "n": n,
        "fraction_negative": lt / n,
        "fraction_tied": eq / n,
        "fraction_positive": gt / n,
    }


def direction_class(fraction: float) -> str:
    if fraction >= 0.95:
        return "robust"
    if fraction >= 0.80:
        return "stable"
    return "mixed"


def validate_contract(contract: dict) -> None:
    if contract.get("status") != "frozen_followup_before_paired_result_inspection":
        raise ValueError("depth-ordering follow-up contract is not frozen")
    observed = [
        (row["deeper_candidate"], row["shallower_candidate"])
        for row in contract["pairwise_questions"]
    ]
    expected = [
        ("phyllary", "stickiness"),
        ("orientation", "stickiness"),
        ("phyllary", "orientation"),
    ]
    if observed != expected:
        raise ValueError(f"pairwise question drift: {observed!r}")


def build_bootstrap_rows(
    source_contract_path: Path,
    tree_path: Path,
    bootstrap_path: Path,
    concept_map_path: Path,
    base_trait_seed_path: Path,
    extension_path: Path,
) -> tuple[list[dict], dict]:
    source_contract = read_json(source_contract_path)
    runtime = source_contract["runtime_contract"]
    if Bio.__version__ != runtime["biopython_version"]:
        raise ValueError(
            f"Biopython drift: {Bio.__version__} != {runtime['biopython_version']}"
        )

    frozen = source_contract["frozen_inputs"]
    if DEPTH.sha256(tree_path) != frozen["ml_tree_sha256"]:
        raise ValueError("ML tree SHA-256 differs from frozen relative-depth contract")
    if DEPTH.sha256(bootstrap_path) != frozen["ufboot_sha256"]:
        raise ValueError("UFBoot SHA-256 differs from frozen relative-depth contract")

    source_hashes = {
        "concept_map_canonical_lf_sha256": DEPTH.canonical_text_sha256(concept_map_path),
        "base_trait_seed_canonical_lf_sha256": DEPTH.canonical_text_sha256(base_trait_seed_path),
        "authority_extension_canonical_lf_sha256": DEPTH.canonical_text_sha256(extension_path),
    }
    for key, observed in source_hashes.items():
        if observed != frozen[key]:
            raise ValueError(f"{key} differs from frozen relative-depth contract")

    merged = DEPTH.merge_trait_rows(
        base_trait_seed_path, extension_path, source_contract
    )
    trait_states = DEPTH.trait_states_from_rows(merged)
    concept_map, allowed = DEPTH.BASE.concept_info(concept_map_path)

    rows: list[dict] = []
    for bootstrap_index, raw in enumerate(
        (line.strip() for line in bootstrap_path.read_text(encoding="utf-8").splitlines() if line.strip()),
        start=1,
    ):
        tree, _ = DEPTH.prepare_tree(
            Phylo.read(StringIO(raw), "newick"), concept_map, allowed, trait_states
        )
        per_trait = {}
        for trait in TRAITS:
            result = DEPTH.analyze_trait(
                tree,
                trait_states[trait],
                DEPTH.BASE.STATE_UNIVERSE[trait],
            )
            lo, hi = result["mean_relative_lineage_depth_interval"]
            per_trait[trait] = {
                "minimum_steps": result["minimum_steps"],
                "lower": lo,
                "upper": hi,
                "width": result["mean_relative_lineage_depth_envelope_width"],
                "terminal_min": result["terminal_change_count_interval"][0],
                "internal_min": result["internal_change_count_interval"][0],
            }
        rows.append({"bootstrap_index": bootstrap_index, "traits": per_trait})

    if len(rows) != frozen["bootstrap_replicates"]:
        raise AssertionError(
            f"bootstrap replicate drift: {len(rows)} != {frozen['bootstrap_replicates']}"
        )
    return rows, {
        "tree_run_id": frozen["tree_run_id"],
        "tree_artifact": frozen["tree_artifact"],
        "ml_tree_sha256": frozen["ml_tree_sha256"],
        "ufboot_sha256": frozen["ufboot_sha256"],
        **source_hashes,
        "bootstrap_replicates": len(rows),
        "biopython_version": Bio.__version__,
    }


def pairwise_result(rows: list[dict], deeper: str, shallower: str) -> dict:
    lower_diffs = [
        row["traits"][deeper]["lower"] - row["traits"][shallower]["lower"]
        for row in rows
    ]
    width_diffs = [
        row["traits"][deeper]["width"] - row["traits"][shallower]["width"]
        for row in rows
    ]
    lower_cmp = cmp_fraction(lower_diffs)
    fraction_prespecified = lower_cmp["fraction_negative"]
    return {
        "deeper_candidate": deeper,
        "shallower_candidate": shallower,
        "lower_bound_difference_deeper_minus_shallower": summary(lower_diffs),
        "lower_bound_ordering": lower_cmp,
        "fraction_prespecified_deeper_direction": fraction_prespecified,
        "direction_class": direction_class(fraction_prespecified),
        "envelope_width_difference_deeper_minus_shallower": summary(width_diffs),
        "envelope_width_ordering": cmp_fraction(width_diffs),
    }


def write_topology_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "bootstrap_index",
        "trait",
        "minimum_steps",
        "lower_depth_bound",
        "upper_depth_bound",
        "depth_envelope_width",
        "terminal_change_count_lower_bound",
        "internal_change_count_lower_bound",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            for trait in TRAITS:
                x = row["traits"][trait]
                writer.writerow(
                    {
                        "bootstrap_index": row["bootstrap_index"],
                        "trait": trait,
                        "minimum_steps": x["minimum_steps"],
                        "lower_depth_bound": x["lower"],
                        "upper_depth_bound": x["upper"],
                        "depth_envelope_width": x["width"],
                        "terminal_change_count_lower_bound": x["terminal_min"],
                        "internal_change_count_lower_bound": x["internal_min"],
                    }
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--followup-contract", type=Path, required=True)
    parser.add_argument("--source-contract", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--bootstrap-trees", type=Path, required=True)
    parser.add_argument("--concept-map", type=Path, required=True)
    parser.add_argument("--base-trait-seed", type=Path, required=True)
    parser.add_argument("--trait-extension", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    followup = read_json(args.followup_contract)
    validate_contract(followup)
    rows, provenance = build_bootstrap_rows(
        args.source_contract,
        args.tree,
        args.bootstrap_trees,
        args.concept_map,
        args.base_trait_seed,
        args.trait_extension,
    )

    pairwise = [
        pairwise_result(rowset := rows, q["deeper_candidate"], q["shallower_candidate"])
        for q in followup["pairwise_questions"]
    ]
    # The assignment expression above deliberately keeps every comparison on the
    # exact same ordered topology set; assert that no accidental filtering occurred.
    assert rowset is rows

    complete_order_count = 0
    phyllary_deeper_than_stickiness = 0
    orientation_deeper_than_stickiness = 0
    for row in rows:
        p = row["traits"]["phyllary"]["lower"]
        o = row["traits"]["orientation"]["lower"]
        s = row["traits"]["stickiness"]["lower"]
        complete_order_count += int(p < o - TOL and o < s - TOL)
        phyllary_deeper_than_stickiness += int(p < s - TOL)
        orientation_deeper_than_stickiness += int(o < s - TOL)

    result = {
        "version": "chapter2_depth_ordering_robustness_result_v1",
        "source_followup_contract": str(args.followup_contract.as_posix()),
        "analysis_role": followup["analysis_role"],
        "input_verification": provenance,
        "primary_estimand": followup["primary_estimand"],
        "pairwise_results": pairwise,
        "complete_lower_bound_ordering": {
            "ordering": "phyllary < orientation < stickiness",
            "count": complete_order_count,
            "fraction": complete_order_count / len(rows),
        },
        "stickiness_shallow_contrast": {
            "phyllary_lower_bound_deeper_than_stickiness_fraction": phyllary_deeper_than_stickiness / len(rows),
            "orientation_lower_bound_deeper_than_stickiness_fraction": orientation_deeper_than_stickiness / len(rows),
        },
        "interpretation_boundary": followup["interpretation_boundary"],
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_topology_csv(args.output_csv, rows)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
