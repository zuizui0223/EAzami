#!/usr/bin/env python3
"""Coverage-match Chapter 2 relative-depth histories to phyllary n=10.

This is a post-result missing-state sensitivity. The admitted 36-tip topology is
never pruned for coverage matching. Instead, selected observed orientation or
stickiness states are reset to the full state universe, exactly mimicking extra
missing trait observations while preserving the same topology and relative-depth
denominator.

Topology x mask combinations are deterministic sensitivity evaluations, not
independent biological replicates. No P value is computed from them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import statistics
import sys
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

TOL = 1e-12


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nearest_rank(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("nearest_rank requires non-empty values")
    ordered = sorted(float(v) for v in values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
    return float(ordered[idx])


def summary(values: list[float]) -> dict:
    vals = [float(v) for v in values]
    if not vals or not all(math.isfinite(v) for v in vals):
        raise ValueError("summary requires finite non-empty values")
    return {
        "n": len(vals),
        "min": min(vals),
        "q05": nearest_rank(vals, 0.05),
        "median": float(statistics.median(vals)),
        "q95": nearest_rank(vals, 0.95),
        "max": max(vals),
    }


def direction_class(fraction: float) -> str:
    if fraction >= 0.95:
        return "robust"
    if fraction >= 0.80:
        return "stable"
    return "mixed"


def topology_indices() -> list[int]:
    indices = [1 + round(k * 999 / 199) for k in range(200)]
    if len(indices) != 200 or len(set(indices)) != 200:
        raise AssertionError(f"topology selection is not 200 unique indices: {indices}")
    if indices[0] != 1 or indices[-1] != 1000:
        raise AssertionError("topology selection must include 1 and 1000")
    return indices


def resolved_exact_groups(trait_states: dict[str, set[str]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for concept, states in trait_states.items():
        if len(states) != 1:
            continue
        state = next(iter(states))
        groups.setdefault(state, []).append(concept)
    return {state: sorted(ids) for state, ids in sorted(groups.items())}


def orientation_masks(groups: dict[str, list[str]]) -> list[tuple[str, ...]]:
    if set(groups) != {"D", "U"}:
        raise AssertionError(f"unexpected orientation states: {groups}")
    if len(groups["U"]) != 14 or len(groups["D"]) != 6:
        raise AssertionError(f"orientation source state-count drift: {groups}")
    candidates: list[tuple[str, tuple[str, ...]]] = []
    prefix = "orientation|20260903|"
    for u in itertools.combinations(groups["U"], 7):
        for d in itertools.combinations(groups["D"], 3):
            mask = tuple(sorted((*u, *d)))
            digest = hashlib.sha256((prefix + ",".join(mask)).encode("utf-8")).hexdigest()
            candidates.append((digest, mask))
    if len(candidates) != 68640:
        raise AssertionError(f"orientation candidate mask drift: {len(candidates)}")
    candidates.sort(key=lambda x: (x[0], x[1]))
    selected = [mask for _, mask in candidates[:256]]
    if len(set(selected)) != 256:
        raise AssertionError("orientation selected masks are not unique")
    return selected


def stickiness_masks(
    groups: dict[str, list[str]], sticky_n: int, nonsticky_n: int
) -> list[tuple[str, ...]]:
    if set(groups) != {"nonsticky", "sticky"}:
        raise AssertionError(f"unexpected stickiness states: {groups}")
    if len(groups["sticky"]) != 7 or len(groups["nonsticky"]) != 6:
        raise AssertionError(f"stickiness source state-count drift: {groups}")
    masks = [
        tuple(sorted((*sticky, *nonsticky)))
        for sticky in itertools.combinations(groups["sticky"], sticky_n)
        for nonsticky in itertools.combinations(groups["nonsticky"], nonsticky_n)
    ]
    if len(masks) != len(set(masks)):
        raise AssertionError("stickiness masks are not unique")
    return masks


def masked_state_map(
    original: dict[str, set[str]], universe: set[str], retained: tuple[str, ...]
) -> dict[str, set[str]]:
    keep = set(retained)
    return {
        concept: (set(states) if concept in keep else set(universe))
        for concept, states in original.items()
    }


def lower_depth_and_steps(tree, state_map: dict[str, set[str]], universe: set[str]) -> tuple[int, float]:
    counts = DEPTH.descendant_counts(tree)
    tip_count = counts[tree.root]
    if tip_count != 36:
        raise AssertionError(f"coverage sensitivity expected 36 admitted tips, got {tip_count}")

    def relative_depth(child):
        return (tip_count - counts[child]) / (tip_count - 1)

    steps, depth_sum = DEPTH.solve_secondary_bound(
        tree, state_map, universe, relative_depth, maximize=False
    )
    if steps <= 0:
        raise AssertionError("state-balanced mask unexpectedly has zero minimum steps")
    value = float(depth_sum / steps)
    if not 0.0 <= value <= 1.0:
        raise AssertionError(f"relative depth outside [0,1]: {value}")
    return int(steps), value


def mask_distribution(
    tree,
    original: dict[str, set[str]],
    universe: set[str],
    masks: list[tuple[str, ...]],
) -> dict:
    depths: list[float] = []
    steps: list[int] = []
    for mask in masks:
        state_map = masked_state_map(original, universe, mask)
        n_steps, lower = lower_depth_and_steps(tree, state_map, universe)
        steps.append(n_steps)
        depths.append(lower)
    return {
        "lower_depth": summary(depths),
        "minimum_steps": summary([float(x) for x in steps]),
    }


def comparison_fraction(rows: list[dict], key: str) -> dict:
    values = [bool(row["comparisons"][key]) for row in rows]
    fraction = sum(values) / len(values)
    return {
        "comparison": key,
        "n_topologies": len(values),
        "count": int(sum(values)),
        "fraction": fraction,
        "direction_class": direction_class(fraction),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "bootstrap_index",
        "phyllary_steps",
        "phyllary_lower_depth",
        "orientation_depth_q05",
        "orientation_depth_median",
        "orientation_steps_median",
        "stickiness_5_5_depth_q05",
        "stickiness_5_5_depth_median",
        "stickiness_5_5_steps_median",
        "stickiness_6_4_depth_q05",
        "stickiness_6_4_depth_median",
        "stickiness_6_4_steps_median",
        "phyllary_deeper_than_orientation_median",
        "phyllary_deeper_than_orientation_q05",
        "phyllary_deeper_than_stickiness_5_5_median",
        "phyllary_deeper_than_stickiness_5_5_q05",
        "phyllary_deeper_than_stickiness_6_4_median",
        "phyllary_deeper_than_stickiness_6_4_q05",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            o = row["orientation_matched"]
            s55 = row["stickiness_5_5_matched"]
            s64 = row["stickiness_6_4_matched"]
            c = row["comparisons"]
            writer.writerow({
                "bootstrap_index": row["bootstrap_index"],
                "phyllary_steps": row["phyllary_observed"]["minimum_steps"],
                "phyllary_lower_depth": row["phyllary_observed"]["lower_depth"],
                "orientation_depth_q05": o["lower_depth"]["q05"],
                "orientation_depth_median": o["lower_depth"]["median"],
                "orientation_steps_median": o["minimum_steps"]["median"],
                "stickiness_5_5_depth_q05": s55["lower_depth"]["q05"],
                "stickiness_5_5_depth_median": s55["lower_depth"]["median"],
                "stickiness_5_5_steps_median": s55["minimum_steps"]["median"],
                "stickiness_6_4_depth_q05": s64["lower_depth"]["q05"],
                "stickiness_6_4_depth_median": s64["lower_depth"]["median"],
                "stickiness_6_4_steps_median": s64["minimum_steps"]["median"],
                "phyllary_deeper_than_orientation_median": c["phyllary_lt_orientation_median"],
                "phyllary_deeper_than_orientation_q05": c["phyllary_lt_orientation_q05"],
                "phyllary_deeper_than_stickiness_5_5_median": c["phyllary_lt_stickiness_5_5_median"],
                "phyllary_deeper_than_stickiness_5_5_q05": c["phyllary_lt_stickiness_5_5_q05"],
                "phyllary_deeper_than_stickiness_6_4_median": c["phyllary_lt_stickiness_6_4_median"],
                "phyllary_deeper_than_stickiness_6_4_q05": c["phyllary_lt_stickiness_6_4_q05"],
            })


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sensitivity-contract", type=Path, required=True)
    p.add_argument("--source-contract", type=Path, required=True)
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--bootstrap-trees", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--base-trait-seed", type=Path, required=True)
    p.add_argument("--trait-extension", type=Path, required=True)
    p.add_argument("--output-json", type=Path, required=True)
    p.add_argument("--output-csv", type=Path, required=True)
    args = p.parse_args()

    sensitivity = read_json(args.sensitivity_contract)
    if sensitivity.get("status") != "frozen_before_coverage_matched_result_inspection":
        raise ValueError("coverage-matched sensitivity contract is not frozen")
    if sensitivity["target_resolved_concepts"] != 10:
        raise ValueError("coverage target drift")

    source = read_json(args.source_contract)
    if source.get("status") != "frozen_with_audited_runtime_and_provenance_amendment_before_result_admission":
        raise ValueError("source relative-depth contract is not frozen")
    runtime = sensitivity["runtime"]
    observed_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    if observed_python != runtime["python"]:
        raise ValueError(f"Python drift: {observed_python} != {runtime['python']}")
    if Bio.__version__ != runtime["biopython"]:
        raise ValueError(f"Biopython drift: {Bio.__version__} != {runtime['biopython']}")

    frozen = source["frozen_inputs"]
    if DEPTH.sha256(args.tree) != frozen["ml_tree_sha256"]:
        raise ValueError("ML tree hash differs from frozen source contract")
    if DEPTH.sha256(args.bootstrap_trees) != frozen["ufboot_sha256"]:
        raise ValueError("UFBoot hash differs from frozen source contract")
    source_hashes = {
        "concept_map_canonical_lf_sha256": DEPTH.canonical_text_sha256(args.concept_map),
        "base_trait_seed_canonical_lf_sha256": DEPTH.canonical_text_sha256(args.base_trait_seed),
        "authority_extension_canonical_lf_sha256": DEPTH.canonical_text_sha256(args.trait_extension),
    }
    for key, observed in source_hashes.items():
        if observed != frozen[key]:
            raise ValueError(f"{key} differs from frozen source contract")

    merged = DEPTH.merge_trait_rows(args.base_trait_seed, args.trait_extension, source)
    trait_states = DEPTH.trait_states_from_rows(merged)
    concept_map, allowed = DEPTH.BASE.concept_info(args.concept_map)

    orientation_groups = resolved_exact_groups(trait_states["orientation"])
    stickiness_groups = resolved_exact_groups(trait_states["stickiness"])
    o_masks = orientation_masks(orientation_groups)
    s55_masks = stickiness_masks(stickiness_groups, 5, 5)
    s64_masks = stickiness_masks(stickiness_groups, 6, 4)
    if len(s55_masks) != 126 or len(s64_masks) != 105:
        raise AssertionError(
            f"stickiness mask count drift: 5/5={len(s55_masks)} 6/4={len(s64_masks)}"
        )

    phyl_universe = DEPTH.BASE.STATE_UNIVERSE["phyllary"]
    phyl_resolved = [
        concept for concept, states in trait_states["phyllary"].items()
        if set(states) != set(phyl_universe)
    ]
    if len(phyl_resolved) != 10:
        raise AssertionError(f"phyllary resolved coverage drift: {len(phyl_resolved)}")

    selected = topology_indices()
    selected_set = set(selected)
    raw_lines = [
        line.strip()
        for line in args.bootstrap_trees.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(raw_lines) != 1000:
        raise AssertionError(f"expected 1000 UFBoot trees, found {len(raw_lines)}")

    rows: list[dict] = []
    for bootstrap_index in selected:
        raw = raw_lines[bootstrap_index - 1]
        tree, diagnostic = DEPTH.prepare_tree(
            Phylo.read(StringIO(raw), "newick"), concept_map, allowed, trait_states
        )
        if tree is None or not diagnostic["trait_asr_ready"]:
            raise AssertionError(f"selected topology blocked at {bootstrap_index}: {diagnostic}")

        phyl_steps, phyl_lower = lower_depth_and_steps(
            tree, trait_states["phyllary"], phyl_universe
        )
        if phyl_steps != 3:
            raise AssertionError(
                f"phyllary minimum-step drift at topology {bootstrap_index}: {phyl_steps}"
            )

        orientation = mask_distribution(
            tree,
            trait_states["orientation"],
            DEPTH.BASE.STATE_UNIVERSE["orientation"],
            o_masks,
        )
        stickiness_5_5 = mask_distribution(
            tree,
            trait_states["stickiness"],
            DEPTH.BASE.STATE_UNIVERSE["stickiness"],
            s55_masks,
        )
        stickiness_6_4 = mask_distribution(
            tree,
            trait_states["stickiness"],
            DEPTH.BASE.STATE_UNIVERSE["stickiness"],
            s64_masks,
        )

        comparisons = {
            "phyllary_lt_orientation_median": phyl_lower < orientation["lower_depth"]["median"] - TOL,
            "phyllary_lt_orientation_q05": phyl_lower < orientation["lower_depth"]["q05"] - TOL,
            "phyllary_lt_stickiness_5_5_median": phyl_lower < stickiness_5_5["lower_depth"]["median"] - TOL,
            "phyllary_lt_stickiness_5_5_q05": phyl_lower < stickiness_5_5["lower_depth"]["q05"] - TOL,
            "phyllary_lt_stickiness_6_4_median": phyl_lower < stickiness_6_4["lower_depth"]["median"] - TOL,
            "phyllary_lt_stickiness_6_4_q05": phyl_lower < stickiness_6_4["lower_depth"]["q05"] - TOL,
        }
        rows.append({
            "bootstrap_index": bootstrap_index,
            "phyllary_observed": {
                "minimum_steps": phyl_steps,
                "lower_depth": phyl_lower,
            },
            "orientation_matched": orientation,
            "stickiness_5_5_matched": stickiness_5_5,
            "stickiness_6_4_matched": stickiness_6_4,
            "comparisons": comparisons,
        })

    comparison_keys = list(rows[0]["comparisons"])
    comparisons = [comparison_fraction(rows, key) for key in comparison_keys]
    by_key = {x["comparison"]: x for x in comparisons}

    strict_primary = {
        "orientation": by_key["phyllary_lt_orientation_q05"],
        "stickiness_5_5": by_key["phyllary_lt_stickiness_5_5_q05"],
    }
    median_primary = {
        "orientation": by_key["phyllary_lt_orientation_median"],
        "stickiness_5_5": by_key["phyllary_lt_stickiness_5_5_median"],
    }

    if all(x["fraction"] >= 0.80 for x in strict_primary.values()):
        overall = "unequal_depth_retained_under_strict_coverage_matching"
    elif all(x["fraction"] >= 0.80 for x in median_primary.values()):
        overall = "unequal_depth_retained_against_matched_medians_but_strict_tail_overlap_remains"
    else:
        overall = "unequal_depth_materially_sensitive_to_observed_state_coverage"

    result = {
        "version": "chapter2_depth_coverage_matched_sensitivity_result_v1",
        "source_contract": str(args.sensitivity_contract.as_posix()),
        "analysis_role": sensitivity["analysis_role"],
        "input_verification": {
            "tree_run_id": frozen["tree_run_id"],
            "tree_artifact": frozen["tree_artifact"],
            "ml_tree_sha256": frozen["ml_tree_sha256"],
            "ufboot_sha256": frozen["ufboot_sha256"],
            **source_hashes,
            "python": observed_python,
            "biopython": Bio.__version__,
            "selected_topology_indices": selected,
            "orientation_masks": len(o_masks),
            "stickiness_5_5_masks": len(s55_masks),
            "stickiness_6_4_masks": len(s64_masks),
        },
        "source_state_counts": {
            "orientation": {k: len(v) for k, v in orientation_groups.items()},
            "phyllary_resolved": len(phyl_resolved),
            "stickiness": {k: len(v) for k, v in stickiness_groups.items()},
        },
        "comparison_results": comparisons,
        "overall_classification": overall,
        "selected_topology_phyllary_lower_depth": summary(
            [row["phyllary_observed"]["lower_depth"] for row in rows]
        ),
        "selected_topology_matched_median_depths": {
            "orientation": summary(
                [row["orientation_matched"]["lower_depth"]["median"] for row in rows]
            ),
            "stickiness_5_5": summary(
                [row["stickiness_5_5_matched"]["lower_depth"]["median"] for row in rows]
            ),
            "stickiness_6_4": summary(
                [row["stickiness_6_4_matched"]["lower_depth"]["median"] for row in rows]
            ),
        },
        "selected_topology_matched_step_medians": {
            "orientation": summary(
                [row["orientation_matched"]["minimum_steps"]["median"] for row in rows]
            ),
            "stickiness_5_5": summary(
                [row["stickiness_5_5_matched"]["minimum_steps"]["median"] for row in rows]
            ),
            "stickiness_6_4": summary(
                [row["stickiness_6_4_matched"]["minimum_steps"]["median"] for row in rows]
            ),
        },
        "interpretation_rules": sensitivity["interpretation_rules"],
        "claim_boundary": sensitivity["claim_boundary"],
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_csv(args.output_csv, rows)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
