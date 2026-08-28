#!/usr/bin/env python3
"""Bound the relative lineage depth of Japan38 minimum-change histories.

The raw UFBoot trees contain topology but no branch lengths.  This analysis
therefore defines depth only from descendant clade size.  It uses dynamic
programming to obtain exact lower and upper envelopes across all globally
minimum-cost Sankoff reconstructions.  Equally parsimonious histories are not
enumerated, sampled, or assigned equal probability.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import sys
from io import StringIO
from pathlib import Path

import Bio
from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
BASE_SPEC = importlib.util.spec_from_file_location(
    "japan38_parsimony_base",
    ROOT / "analysis" / "summarize_japan38_multitrait_parsimony_v1.py",
)
assert BASE_SPEC and BASE_SPEC.loader
BASE = importlib.util.module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(BASE)

DIAG_SPEC = importlib.util.spec_from_file_location(
    "japan38_transition_diagnostics",
    ROOT / "analysis" / "summarize_japan38_transition_identifiability_v1.py",
)
assert DIAG_SPEC and DIAG_SPEC.loader
DIAG = importlib.util.module_from_spec(DIAG_SPEC)
DIAG_SPEC.loader.exec_module(DIAG)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_trait_rows(base_path: Path, extension_path: Path, contract: dict) -> list[dict]:
    base = BASE.read_csv(base_path)
    extension = BASE.read_csv(extension_path)
    base_ids = {row["paper_japan_member_id"] for row in base}
    extension_by = {row["paper_japan_member_id"]: row for row in extension}
    expected = contract["frozen_inputs"]["required_extension_concepts"]
    if set(extension_by) != set(expected):
        raise ValueError(
            f"trait extension concept drift expected={sorted(expected)} "
            f"observed={sorted(extension_by)}"
        )
    overlap = base_ids & set(extension_by)
    if overlap:
        raise ValueError(f"trait extension duplicates base concepts: {sorted(overlap)}")
    for concept, required in expected.items():
        for field, value in required.items():
            observed = extension_by[concept].get(field, "")
            if observed != value:
                raise ValueError(
                    f"trait extension drift {concept}.{field}: "
                    f"expected={value!r} observed={observed!r}"
                )
    return base + extension


def trait_states_from_rows(rows: list[dict]) -> dict[str, dict[str, set[str]]]:
    by = {row["paper_japan_member_id"]: row for row in rows}
    return {
        trait: {
            concept: BASE.trait_state(row, trait)
            for concept, row in by.items()
        }
        for trait in BASE.STATE_UNIVERSE
    }


def prepare_tree(raw_tree, concept_map, allowed, trait_states):
    raw_tree.root_with_outgroup("OUTGROUP_saff")
    tree, diagnostic = BASE.prepare_trait_tree(
        raw_tree, concept_map, allowed, trait_states
    )
    if not diagnostic["trait_asr_ready"]:
        raise ValueError(f"trait tree blocked: {diagnostic}")
    return tree, diagnostic


def descendant_counts(tree) -> dict:
    counts = {}

    def walk(node):
        if node.is_terminal():
            counts[node] = 1
            return 1
        total = sum(walk(child) for child in node.clades)
        counts[node] = total
        return total

    walk(tree.root)
    return counts


def solve_secondary_bound(tree, state_map, universe, edge_weight, maximize: bool):
    """Lexicographically minimize steps, then minimize/maximize edge weight.

    For a fixed parent state, child subproblems are independent.  Selecting the
    minimum-cost child state and then the requested secondary extreme therefore
    yields the exact bound among histories attaining the global Sankoff optimum.
    """

    states = tuple(sorted(universe))
    inf = 10**9
    down = {}

    def better(candidate, incumbent):
        if incumbent is None:
            return candidate
        if candidate[0] != incumbent[0]:
            return candidate if candidate[0] < incumbent[0] else incumbent
        if maximize:
            return candidate if candidate[1] > incumbent[1] else incumbent
        return candidate if candidate[1] < incumbent[1] else incumbent

    for node in tree.find_clades(order="postorder"):
        if node.is_terminal():
            allowed = set(state_map.get(node.name, set(universe)))
            down[node] = {
                state: ((0, 0.0) if state in allowed else (inf, 0.0))
                for state in states
            }
            continue
        node_values = {}
        for parent_state in states:
            total_cost = 0
            total_secondary = 0.0
            for child in node.clades:
                chosen = None
                for child_state in states:
                    child_cost, child_secondary = down[child][child_state]
                    changed = parent_state != child_state
                    candidate = (
                        child_cost + int(changed),
                        child_secondary
                        + (float(edge_weight(child)) if changed else 0.0),
                    )
                    chosen = better(candidate, chosen)
                assert chosen is not None
                total_cost += chosen[0]
                total_secondary += chosen[1]
            node_values[parent_state] = (total_cost, total_secondary)
        down[node] = node_values

    best = None
    for state in states:
        best = better(down[tree.root][state], best)
    assert best is not None and best[0] < inf
    return best


def analyze_trait(tree, state_map, universe) -> dict:
    counts = descendant_counts(tree)
    tip_count = counts[tree.root]
    if tip_count < 2:
        raise ValueError("relative lineage depth requires at least two tips")

    def relative_depth(child):
        return (tip_count - counts[child]) / (tip_count - 1)

    depth_min = solve_secondary_bound(
        tree, state_map, universe, relative_depth, maximize=False
    )
    depth_max = solve_secondary_bound(
        tree, state_map, universe, relative_depth, maximize=True
    )
    terminal_min = solve_secondary_bound(
        tree, state_map, universe, lambda child: child.is_terminal(), maximize=False
    )
    terminal_max = solve_secondary_bound(
        tree, state_map, universe, lambda child: child.is_terminal(), maximize=True
    )
    internal_min = solve_secondary_bound(
        tree, state_map, universe, lambda child: not child.is_terminal(), maximize=False
    )
    internal_max = solve_secondary_bound(
        tree, state_map, universe, lambda child: not child.is_terminal(), maximize=True
    )

    costs = {
        depth_min[0], depth_max[0], terminal_min[0], terminal_max[0],
        internal_min[0], internal_max[0]
    }
    if len(costs) != 1:
        raise AssertionError(f"secondary-bound optimum mismatch: {sorted(costs)}")
    steps = costs.pop()
    if steps <= 0:
        raise ValueError("event-depth mean is undefined for a zero-step trait")

    terminal_interval = [int(round(terminal_min[1])), int(round(terminal_max[1]))]
    internal_interval = [int(round(internal_min[1])), int(round(internal_max[1]))]
    if terminal_interval[0] + internal_interval[1] != steps:
        raise AssertionError("terminal/internal lower-upper complement drift")
    if terminal_interval[1] + internal_interval[0] != steps:
        raise AssertionError("terminal/internal upper-lower complement drift")

    mean_min = depth_min[1] / steps
    mean_max = depth_max[1] / steps
    if not (0.0 <= mean_min <= mean_max <= 1.0):
        raise AssertionError(
            f"relative lineage-depth bounds outside [0,1]: {mean_min}, {mean_max}"
        )

    diagnostic = DIAG.sankoff_diagnostics(tree, state_map, universe)
    if diagnostic["minimum_steps"] != steps:
        raise AssertionError("event-depth and transition-diagnostic optima disagree")
    forced_edges = []
    for edge in diagnostic["forced_change_edges"]:
        descendants = edge["edge_id"].split("|") if edge["edge_id"] else []
        d = len(descendants)
        forced_edges.append(
            {
                "edge_id": edge["edge_id"],
                "descendant_tip_count": d,
                "edge_class": "terminal" if d == 1 else "internal",
                "relative_lineage_depth": (tip_count - d) / (tip_count - 1),
            }
        )

    return {
        "admitted_tip_count": tip_count,
        "minimum_steps": steps,
        "mean_relative_lineage_depth_interval": [mean_min, mean_max],
        "mean_relative_lineage_depth_envelope_width": mean_max - mean_min,
        "terminal_change_count_interval": terminal_interval,
        "internal_change_count_interval": internal_interval,
        "forced_change_edges": forced_edges,
    }


def nearest_rank(values, p):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))]


def summarize(values) -> dict:
    vals = [float(value) for value in values]
    if not vals or not all(math.isfinite(value) for value in vals):
        raise ValueError("summary requires finite non-empty values")
    return {
        "n": len(vals),
        "min": min(vals),
        "q05": nearest_rank(vals, 0.05),
        "median": statistics.median(vals),
        "q95": nearest_rank(vals, 0.95),
        "max": max(vals),
    }


def validate_expected_steps(contract: dict, ml: dict, bootstrap_rows: dict) -> None:
    for trait, expected in contract["admitted_discrete_traits"].items():
        frozen = expected["minimum_steps_expected"]
        if ml[trait]["minimum_steps"] != frozen["ml"]:
            raise AssertionError(
                f"{trait} ML steps drift: {ml[trait]['minimum_steps']} != {frozen['ml']}"
            )
        observed = [row["minimum_steps"] for row in bootstrap_rows[trait]]
        if min(observed) != frozen["ufboot_min"] or max(observed) != frozen["ufboot_max"]:
            raise AssertionError(
                f"{trait} UFBoot step range drift: {min(observed)}-{max(observed)}"
            )


def bootstrap_summary(rows: list[dict]) -> dict:
    metrics = {
        "minimum_steps": [row["minimum_steps"] for row in rows],
        "mean_relative_lineage_depth_lower_bound": [
            row["mean_relative_lineage_depth_interval"][0] for row in rows
        ],
        "mean_relative_lineage_depth_upper_bound": [
            row["mean_relative_lineage_depth_interval"][1] for row in rows
        ],
        "mean_relative_lineage_depth_envelope_width": [
            row["mean_relative_lineage_depth_envelope_width"] for row in rows
        ],
        "terminal_change_count_lower_bound": [
            row["terminal_change_count_interval"][0] for row in rows
        ],
        "terminal_change_count_upper_bound": [
            row["terminal_change_count_interval"][1] for row in rows
        ],
        "internal_change_count_lower_bound": [
            row["internal_change_count_interval"][0] for row in rows
        ],
        "internal_change_count_upper_bound": [
            row["internal_change_count_interval"][1] for row in rows
        ],
    }
    total = len(rows)
    forced_edge_counts = {}
    for row in rows:
        for edge in row["forced_change_edges"]:
            edge_key = edge["edge_id"]
            forced_edge_counts[edge_key] = forced_edge_counts.get(edge_key, 0) + 1
    return {
        "metric_summaries": {
            metric: summarize(values) for metric, values in metrics.items()
        },
        "fraction_trees_requiring_terminal_change_in_every_minimum_history": (
            sum(row["terminal_change_count_interval"][0] >= 1 for row in rows)
            / total
        ),
        "fraction_trees_requiring_internal_change_in_every_minimum_history": (
            sum(row["internal_change_count_interval"][0] >= 1 for row in rows)
            / total
        ),
        "fraction_trees_permitting_an_all_terminal_minimum_history": (
            sum(
                row["terminal_change_count_interval"][1] == row["minimum_steps"]
                for row in rows
            )
            / total
        ),
        "fraction_trees_permitting_an_all_internal_minimum_history": (
            sum(
                row["internal_change_count_interval"][1] == row["minimum_steps"]
                for row in rows
            )
            / total
        ),
        "forced_change_edge_frequencies": [
            {
                "edge_id": edge_id,
                "count": count,
                "fraction": count / total,
            }
            for edge_id, count in sorted(
                forced_edge_counts.items(), key=lambda item: (-item[1], item[0])
            )
        ],
    }


def write_csv(path: Path, ml: dict, bootstrap: dict) -> None:
    rows = []
    for trait, result in ml.items():
        rows.extend(
            [
                {
                    "tree_layer": "ML",
                    "trait": trait,
                    "metric": "mean_relative_lineage_depth_lower_bound",
                    "n": 1,
                    "min": result["mean_relative_lineage_depth_interval"][0],
                    "q05": result["mean_relative_lineage_depth_interval"][0],
                    "median": result["mean_relative_lineage_depth_interval"][0],
                    "q95": result["mean_relative_lineage_depth_interval"][0],
                    "max": result["mean_relative_lineage_depth_interval"][0],
                },
                {
                    "tree_layer": "ML",
                    "trait": trait,
                    "metric": "mean_relative_lineage_depth_upper_bound",
                    "n": 1,
                    "min": result["mean_relative_lineage_depth_interval"][1],
                    "q05": result["mean_relative_lineage_depth_interval"][1],
                    "median": result["mean_relative_lineage_depth_interval"][1],
                    "q95": result["mean_relative_lineage_depth_interval"][1],
                    "max": result["mean_relative_lineage_depth_interval"][1],
                },
            ]
        )
    for trait, summary in bootstrap.items():
        for metric, values in summary["metric_summaries"].items():
            rows.append(
                {"tree_layer": "UFBoot1000", "trait": trait, "metric": metric, **values}
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        fields = ["tree_layer", "trait", "metric", "n", "min", "q05", "median", "q95", "max"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--bootstrap-trees", type=Path, required=True)
    parser.add_argument("--concept-map", type=Path, required=True)
    parser.add_argument("--base-trait-seed", type=Path, required=True)
    parser.add_argument("--trait-extension", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    contract = read_json(args.contract)
    if contract["status"] != "frozen_with_audited_runtime_and_provenance_amendment_before_result_admission":
        raise ValueError("relative event-depth contract is not frozen")
    runtime = contract["runtime_contract"]
    observed_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    if observed_python not in runtime["accepted_python_major_minor"]:
        raise ValueError("Python major/minor differs from frozen runtime contract")
    if Bio.__version__ != runtime["biopython_version"]:
        raise ValueError("Biopython version differs from frozen runtime contract")
    observed_tree_hash = sha256(args.tree)
    observed_ufboot_hash = sha256(args.bootstrap_trees)
    frozen_inputs = contract["frozen_inputs"]
    if observed_tree_hash != frozen_inputs["ml_tree_sha256"]:
        raise ValueError("ML tree SHA-256 differs from frozen contract")
    if observed_ufboot_hash != frozen_inputs["ufboot_sha256"]:
        raise ValueError("UFBoot SHA-256 differs from frozen contract")
    observed_source_hashes = {
        "concept_map_sha256": sha256(args.concept_map),
        "base_trait_seed_sha256": sha256(args.base_trait_seed),
        "authority_extension_sha256": sha256(args.trait_extension),
    }
    for key, observed in observed_source_hashes.items():
        if observed != frozen_inputs[key]:
            raise ValueError(f"{key} differs from frozen contract")

    rows = merge_trait_rows(args.base_trait_seed, args.trait_extension, contract)
    trait_states = trait_states_from_rows(rows)
    concept_map, allowed = BASE.concept_info(args.concept_map)

    ml_tree, tree_diagnostic = prepare_tree(
        Phylo.read(str(args.tree), "newick"), concept_map, allowed, trait_states
    )
    ml = {
        trait: analyze_trait(ml_tree, trait_states[trait], universe)
        for trait, universe in BASE.STATE_UNIVERSE.items()
    }

    observed_coverage = {
        trait: sum(
            trait_states[trait].get(concept, set(universe)) != set(universe)
            for concept in {tip.name for tip in ml_tree.get_terminals()}
        )
        for trait, universe in BASE.STATE_UNIVERSE.items()
    }
    expected_coverage = {
        trait: values["resolved_concepts"]
        for trait, values in contract["admitted_discrete_traits"].items()
    }
    if observed_coverage != expected_coverage:
        raise AssertionError(
            f"resolved-concept coverage drift expected={expected_coverage} "
            f"observed={observed_coverage}"
        )

    bootstrap_rows = {trait: [] for trait in BASE.STATE_UNIVERSE}
    bootstrap_total = 0
    jpn20_monophyletic = 0
    for raw in args.bootstrap_trees.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        bootstrap_total += 1
        tree, diagnostic = prepare_tree(
            Phylo.read(StringIO(line), "newick"), concept_map, allowed, trait_states
        )
        if diagnostic["replicate_monophyly"]:
            jpn20_monophyletic += 1
        for trait, universe in BASE.STATE_UNIVERSE.items():
            bootstrap_rows[trait].append(
                analyze_trait(tree, trait_states[trait], universe)
            )

    if bootstrap_total != frozen_inputs["bootstrap_replicates"]:
        raise AssertionError(
            f"bootstrap replicate drift: {bootstrap_total} != "
            f"{frozen_inputs['bootstrap_replicates']}"
        )
    validate_expected_steps(contract, ml, bootstrap_rows)
    bootstrap = {
        trait: bootstrap_summary(rows_for_trait)
        for trait, rows_for_trait in bootstrap_rows.items()
    }

    result = {
        "contract_version": "japan38_relative_event_depth_v1",
        "source_contract": str(args.contract.as_posix()),
        "input_verification": {
            "tree_run_id": frozen_inputs["tree_run_id"],
            "tree_artifact": frozen_inputs["tree_artifact"],
            "ml_tree_sha256": observed_tree_hash,
            "ufboot_sha256": observed_ufboot_hash,
            **observed_source_hashes,
            "bootstrap_trees_total": bootstrap_total,
            "jpn20_monophyletic_trees": jpn20_monophyletic,
            "tree_diagnostic": tree_diagnostic,
            "runtime": {
                "accepted_python_major_minor": runtime["accepted_python_major_minor"],
                "ci_python_major_minor": runtime["ci_python_major_minor"],
                "biopython_version": Bio.__version__,
            },
        },
        "trait_scope": {
            "completed_discrete_histories": [
                "orientation", "phyllary", "stickiness"
            ],
            "resolved_concepts": observed_coverage,
            "excluded_from_discrete_history": contract["trait_scope_boundary"]["not_a_fourth_discrete_history"],
        },
        "estimand": contract["estimand"],
        "ml_relative_event_depth": ml,
        "ufboot1000_relative_event_depth": bootstrap,
        "ecological_hypothesis_layer": contract["ecological_hypothesis_layer"],
        "legacy_provenance_boundary": contract["legacy_provenance_boundary"],
        "interpretation": (
            "Relative lineage-depth envelopes describe where globally minimum-cost histories can or must place changes on the admitted topologies. "
            "They are deterministic bounds, not event probabilities, calendar ages, rates, independent-origin counts, convergence, adaptation, or ecological causation."
        ),
        "claim_ceiling": contract["claim_ceiling"],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_csv(args.output_csv, ml, bootstrap)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
