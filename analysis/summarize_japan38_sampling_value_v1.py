#!/usr/bin/env python3
"""Convert Japan38 transition-identifiability output into sampling decisions.

The input Sankoff diagnostic separates repeated-state lower bounds from transition
localization. This companion keeps sampling objectives separate instead of forcing
one opaque score:

1. transition localization: missing states that robustly reduce optional-change edges;
2. ancestral-state discrimination: missing states whose possible outcomes can reduce
   the current root-state set;
3. step-count falsification: missing states whose possible outcomes can change the
   current minimum-step conclusion;
4. observed-state validation: already coded terminal taxa that repeatedly carry a
   forced transition across bootstrap topologies.

Taxon/sample identity is an execution gate, not a numerical weight. Low/critical
identity conflicts are blocked; medium/high conflicts are flagged for resolution
before a trait value is joined to the historical analysis.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

IDENTITY_ORDER = {"pass": 0, "caution": 1, "block": 2}
CONFLICT_ORDER = {"none": 0, "medium": 1, "high": 2, "critical": 3}
TRAIT_COLUMNS = {
    "orientation": "orientation_state",
    "phyllary": "phyllary_posture",
    "stickiness": "stickiness_state",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def conflict_index(rows):
    out = {}
    for row in rows:
        code = (row.get("tree_code") or "").strip()
        if not code:
            continue
        priority = (row.get("priority") or "medium").strip().lower()
        out[code] = {**row, "priority": priority}
    return out


def identity_index(audit_rows, conflict_rows):
    conflicts = conflict_index(conflict_rows)
    out = {}
    for row in audit_rows:
        mid = row["paper_japan_member_id"]
        codes = [x for x in (row.get("tree_codes") or "").split("|") if x]
        matched = [conflicts[x] for x in codes if x in conflicts]
        highest = "none"
        for item in matched:
            priority = item.get("priority", "medium")
            if CONFLICT_ORDER.get(priority, 1) > CONFLICT_ORDER[highest]:
                highest = priority
        confidence = (
            row.get("paper_japan_membership_confidence") or ""
        ).strip().lower()
        origin = (row.get("sample_origin_class") or "").strip().lower()
        if (
            confidence.startswith("low")
            or highest == "critical"
            or "metadata_conflict" in origin
        ):
            gate = "block"
        elif (
            confidence == "medium"
            or highest in {"high", "medium"}
            or "name_conflict" in origin
        ):
            gate = "caution"
        else:
            gate = "pass"
        out[mid] = {
            "paper_taxon_concept": row.get("paper_taxon_concept") or "",
            "identity_gate": gate,
            "paper_japan_membership_confidence": row.get(
                "paper_japan_membership_confidence"
            )
            or "",
            "sample_origin_class": row.get("sample_origin_class") or "",
            "current_name_status": row.get("current_name_status") or "",
            "taxonomic_conflict_priority": highest,
            "matched_taxonomic_conflicts": [
                {
                    "tree_code": x.get("tree_code"),
                    "conflict_type": x.get("conflict_type"),
                    "priority": x.get("priority"),
                }
                for x in matched
            ],
        }
    return out


def candidate_metrics(candidate, baseline_steps, baseline_root_count, identity):
    scenarios = candidate["hypothetical_states"]
    step_changes = [
        s for s in scenarios if s["minimum_steps"] != baseline_steps
    ]
    root_reductions = [
        s for s in scenarios if s["root_state_count"] < baseline_root_count
    ]
    root_expansions = [
        s for s in scenarios if s["root_state_count"] > baseline_root_count
    ]
    return {
        "paper_japan_member_id": candidate["paper_japan_member_id"],
        "paper_taxon_concept": candidate.get("paper_taxon_concept", ""),
        **identity,
        "robust_transition_localization_gain": candidate[
            "worst_case_ambiguous_edge_reduction"
        ],
        "best_case_transition_localization_gain": candidate[
            "best_case_ambiguous_edge_reduction"
        ],
        "unweighted_scenario_mean_localization_gain": candidate[
            "mean_ambiguous_edge_reduction"
        ],
        "enumerated_state_count": len(scenarios),
        "states_reducing_root_state_count": len(root_reductions),
        "states_expanding_root_state_count": len(root_expansions),
        "minimum_root_state_count_across_scenarios": min(
            s["root_state_count"] for s in scenarios
        ),
        "maximum_root_state_count_across_scenarios": max(
            s["root_state_count"] for s in scenarios
        ),
        "states_changing_minimum_steps": len(step_changes),
        "minimum_step_range": candidate["minimum_step_range"],
        "maximum_absolute_step_delta": max(
            abs(s["minimum_steps"] - baseline_steps) for s in scenarios
        ),
        "forced_change_edge_count_range": [
            min(s["forced_change_edges"] for s in scenarios),
            max(s["forced_change_edges"] for s in scenarios),
        ],
    }


def rank_missing(metrics):
    transition = sorted(
        metrics,
        key=lambda x: (
            IDENTITY_ORDER[x["identity_gate"]],
            -x["robust_transition_localization_gain"],
            -x["best_case_transition_localization_gain"],
            x["paper_japan_member_id"],
        ),
    )
    root = sorted(
        metrics,
        key=lambda x: (
            IDENTITY_ORDER[x["identity_gate"]],
            -x["states_reducing_root_state_count"],
            x["minimum_root_state_count_across_scenarios"],
            -x["states_changing_minimum_steps"],
            x["paper_japan_member_id"],
        ),
    )
    steps = sorted(
        metrics,
        key=lambda x: (
            IDENTITY_ORDER[x["identity_gate"]],
            -x["states_changing_minimum_steps"],
            -x["maximum_absolute_step_delta"],
            -x["robust_transition_localization_gain"],
            x["paper_japan_member_id"],
        ),
    )
    return transition, root, steps


def first_pass(rows, predicate):
    for row in rows:
        if row["identity_gate"] == "pass" and predicate(row):
            return row
    return None


def trait_shortlist(transition, root, steps):
    primary = first_pass(
        transition, lambda x: x["robust_transition_localization_gain"] > 0
    )
    objective = "transition_localization"
    if primary is None:
        primary = first_pass(
            root, lambda x: x["states_reducing_root_state_count"] > 0
        )
        objective = "ancestral_state_discrimination"
    if primary is None:
        primary = first_pass(
            steps, lambda x: x["states_changing_minimum_steps"] > 0
        )
        objective = "minimum_step_falsification"
    if primary is None:
        primary = first_pass(transition, lambda x: True)
        objective = "coverage_only"

    pass_candidates = []
    seen = set()
    for row in transition + root + steps:
        if (
            row["identity_gate"] != "pass"
            or row["paper_japan_member_id"] in seen
        ):
            continue
        seen.add(row["paper_japan_member_id"])
        pass_candidates.append(row)
    caution = [r for r in transition if r["identity_gate"] == "caution"]
    return {
        "primary_objective": objective,
        "primary": primary,
        "identity_pass_alternates": [
            r for r in pass_candidates if r is not primary
        ][:4],
        "analytically_high_but_identity_caution": caution[:3],
    }


def validation_targets(ident, identity, trait_seed, min_fraction):
    seed = {r["paper_japan_member_id"]: r for r in trait_seed}
    by_trait = {}
    aggregate = defaultdict(
        lambda: {
            "traits": {},
            "sum_forced_fraction": 0.0,
            "max_forced_fraction": 0.0,
        }
    )
    for trait, boot in ident["bootstrap_identifiability"].items():
        rows = []
        for edge in boot["top_forced_edge_frequencies"]:
            eid = edge["edge_id"]
            if "|" in eid or edge["fraction"] < min_fraction:
                continue
            info = identity.get(eid, {"identity_gate": "caution"})
            state_col = TRAIT_COLUMNS[trait]
            item = {
                "paper_japan_member_id": eid,
                "paper_taxon_concept": info.get("paper_taxon_concept", ""),
                "bootstrap_forced_change_fraction": edge["fraction"],
                "current_source_backed_state": seed.get(eid, {}).get(
                    state_col, "unknown"
                ),
                **info,
            }
            rows.append(item)
            agg = aggregate[eid]
            agg["paper_japan_member_id"] = eid
            agg["paper_taxon_concept"] = info.get("paper_taxon_concept", "")
            agg["identity_gate"] = info.get("identity_gate", "caution")
            agg["traits"][trait] = edge["fraction"]
            agg["sum_forced_fraction"] += edge["fraction"]
            agg["max_forced_fraction"] = max(
                agg["max_forced_fraction"], edge["fraction"]
            )
        rows.sort(
            key=lambda x: (
                -x["bootstrap_forced_change_fraction"],
                IDENTITY_ORDER[x["identity_gate"]],
                x["paper_japan_member_id"],
            )
        )
        by_trait[trait] = rows
    cross = sorted(
        aggregate.values(),
        key=lambda x: (
            -len(x["traits"]),
            -x["sum_forced_fraction"],
            -x["max_forced_fraction"],
            x["paper_japan_member_id"],
        ),
    )
    return by_trait, cross


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--identifiability", type=Path, required=True)
    p.add_argument("--membership-audit", type=Path, required=True)
    p.add_argument("--name-conflicts", type=Path, required=True)
    p.add_argument("--trait-seed", type=Path, required=True)
    p.add_argument("--min-validation-fraction", type=float, default=0.10)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    ident = json.loads(a.identifiability.read_text(encoding="utf-8"))
    audit = read_csv(a.membership_audit)
    conflicts = read_csv(a.name_conflicts)
    traits = read_csv(a.trait_seed)
    identity = identity_index(audit, conflicts)

    missing = {}
    shortlists = {}
    for trait, block in ident["trait_completion_priorities"].items():
        baseline = ident["ml_minimum_reconstructions"][trait]
        baseline_steps = baseline["minimum_steps"]
        baseline_root_count = len(baseline["minimum_root_state_set"])
        metrics = [
            candidate_metrics(
                candidate,
                baseline_steps,
                baseline_root_count,
                identity.get(
                    candidate["paper_japan_member_id"],
                    {"identity_gate": "caution"},
                ),
            )
            for candidate in block["candidates"]
        ]
        transition, root, steps = rank_missing(metrics)
        missing[trait] = {
            "baseline_minimum_steps": baseline_steps,
            "baseline_root_state_set": baseline["minimum_root_state_set"],
            "baseline_optional_change_edges": block[
                "baseline_ambiguous_change_edges"
            ],
            "transition_localization_ranked": transition,
            "ancestral_state_discrimination_ranked": root,
            "minimum_step_falsification_ranked": steps,
        }
        shortlists[trait] = trait_shortlist(transition, root, steps)

    observed, cross = validation_targets(
        ident, identity, traits, a.min_validation_fraction
    )
    result = {
        "contract_version": "japan38_sampling_value_v1",
        "source_contract": ident.get("contract_version"),
        "missing_state_sampling": missing,
        "operational_shortlist": shortlists,
        "observed_state_validation_targets": observed,
        "cross_module_validation_targets": cross,
        "identity_gate_rule": (
            "Identity pass/caution/block is applied before operational ranking. "
            "Critical or low-confidence metadata conflicts block; medium/high "
            "taxonomic conflicts require resolution before joining a new trait state."
        ),
        "decision_rule": (
            "Do not collapse sampling value to one scalar. Prefer robust transition-"
            "localization gain when available; otherwise target ancestral-state "
            "discrimination, then minimum-step falsification. Scenario counts "
            "enumerate possible states and are not probabilities."
        ),
        "claim_boundary": (
            "Sampling priorities are topology-conditioned design decisions. They do "
            "not estimate trait-state probabilities, biological importance, adaptation, "
            "or causal fitness effects. Already coded high-leverage states are "
            "validation targets, not missing-state targets."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
