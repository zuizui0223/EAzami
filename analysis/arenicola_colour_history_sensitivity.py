#!/usr/bin/env python3
"""Topology-only flower-colour history sensitivity for Ryukyu Arenicola.

This analysis deliberately separates three questions that had previously been
collapsed into one Fitch-parsimony sentence:

1. The two-tip C. brevicaule (white) / C. irumtiense (coloured) contrast alone
   cannot polarize the transition: a coloured MRCA with one loss and a white
   MRCA with one regain each cost one change.
2. The published sister-clade context (Arenicola sister to Nipponocirsium,
   whose sampled basal/crown tips are predominantly coloured) can polarize the
   node under equal-cost parsimony.
3. Historical treatment of C. irumtiense as C. brevicaule var. irumtiense is a
   taxonomic statement, not an ancestor-descendant constraint, and therefore is
   never used as a tree edge or root prior.

No branch lengths are invented. This is an exact discrete topology diagnostic,
not an Mk likelihood analysis and not evidence of molecular anthocyanin regain.
"""

from __future__ import annotations

import argparse
import csv
import json
from itertools import product
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_EVIDENCE = Path("data/evidence/arenicola_flower_colour_history_evidence_v1.csv")
DEFAULT_OUTPUT = Path("analysis/arenicola_colour_history_sensitivity_v1.csv")
DEFAULT_SUMMARY = Path("analysis/arenicola_colour_history_sensitivity_v1.json")
STATES = ("C", "W")
TIP_RECORDS = {
    "brevicaule": "A01",
    "irumtiense": "A02",
    "morii": "A03",
    "pengii": "A04",
    "kawakamii": "A05",
    "tatakaense": "A06",
}
EXPECTED_TIP_STATES = {
    "brevicaule": "W",
    "irumtiense": "C",
    "morii": "C",
    "pengii": "C",
    "kawakamii": "W",
    "tatakaense": "C",
}
OUTPUT_FIELDS = (
    "analysis_context",
    "topology_variant",
    "constraint",
    "minimum_changes",
    "delta_from_unconstrained",
    "optimal_assignment_count",
    "optimal_root_states",
    "optimal_arenicola_mrca_states",
    "optimal_transition_signatures",
    "interpretation",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def load_tip_states(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    by_id = {row.get("record_id", ""): row for row in rows}
    missing = [record for record in TIP_RECORDS.values() if record not in by_id]
    if missing:
        raise ValueError("Missing source-backed tip records: " + "|".join(missing))
    states: dict[str, str] = {}
    for tip, record_id in TIP_RECORDS.items():
        row = by_id[record_id]
        state = row.get("state_or_fact", "")
        if row.get("evidence_type") != "tip_flower_colour":
            raise ValueError(f"{record_id} is not tip_flower_colour evidence")
        if state not in STATES:
            raise ValueError(f"{record_id} has unsupported state {state!r}")
        states[tip] = state
    if states != EXPECTED_TIP_STATES:
        raise ValueError(f"Frozen Arenicola/Nipponocirsium tip states drifted: {states}")
    return states


def edges(children: Mapping[str, Sequence[str]]) -> list[tuple[str, str]]:
    return [(parent, child) for parent, child_nodes in children.items() for child in child_nodes]


def internal_nodes(children: Mapping[str, Sequence[str]]) -> list[str]:
    return list(children)


def enumerate_optima(
    children: Mapping[str, Sequence[str]],
    tip_states: Mapping[str, str],
    *,
    root: str,
    constraints: Mapping[str, str] | None = None,
) -> dict[str, object]:
    constraints = dict(constraints or {})
    internals = internal_nodes(children)
    unknown_constraints = sorted(set(constraints) - set(internals))
    if unknown_constraints:
        raise ValueError("Constraints reference non-internal nodes: " + "|".join(unknown_constraints))
    if any(value not in STATES for value in constraints.values()):
        raise ValueError("All constraints must be C or W")

    edge_list = edges(children)
    candidates: list[tuple[int, dict[str, str]]] = []
    for values in product(STATES, repeat=len(internals)):
        assignment = dict(zip(internals, values))
        assignment.update(tip_states)
        if any(assignment[node] != state for node, state in constraints.items()):
            continue
        cost = sum(assignment[parent] != assignment[child] for parent, child in edge_list)
        candidates.append((cost, assignment))
    if not candidates:
        raise ValueError("No assignments satisfy the requested constraints")

    minimum = min(cost for cost, _ in candidates)
    optimum = [assignment for cost, assignment in candidates if cost == minimum]

    def node_states(node: str) -> str:
        return "|".join(sorted({assignment[node] for assignment in optimum}))

    signatures = set()
    for assignment in optimum:
        changes = []
        for parent, child in edge_list:
            if assignment[parent] != assignment[child]:
                changes.append(
                    f"{parent}:{assignment[parent]}>{child}:{assignment[child]}"
                )
        signatures.add(";".join(changes) if changes else "none")

    return {
        "minimum_changes": minimum,
        "optimal_assignment_count": len(optimum),
        "optimal_root_states": node_states(root),
        "optimal_arenicola_mrca_states": (
            node_states("AREN_MRCA") if "AREN_MRCA" in internals else node_states(root)
        ),
        "optimal_transition_signatures": " || ".join(sorted(signatures)),
    }


def pair_tree() -> tuple[dict[str, tuple[str, str]], str, dict[str, str]]:
    return (
        {"AREN_MRCA": ("brevicaule", "irumtiense")},
        "AREN_MRCA",
        {"brevicaule": "W", "irumtiense": "C"},
    )


def full_tree(core_variant: str) -> tuple[dict[str, tuple[str, str]], str]:
    # Chang 2026 places morii as the earliest Nipponocirsium lineage and Chang
    # 2025 places pengii basal to the kawakamii/tatakaense pair. Two alternative
    # three-taxon resolutions are retained as a topology sensitivity; all keep
    # source-backed morii as the basal Nipponocirsium tip.
    if core_variant == "published_pengii_basal":
        core = {
            "NIPP_CORE": ("pengii", "NIPP_CROWN"),
            "NIPP_CROWN": ("kawakamii", "tatakaense"),
        }
    elif core_variant == "alternative_kawakamii_basal":
        core = {
            "NIPP_CORE": ("kawakamii", "NIPP_CROWN"),
            "NIPP_CROWN": ("pengii", "tatakaense"),
        }
    elif core_variant == "alternative_tatakaense_basal":
        core = {
            "NIPP_CORE": ("tatakaense", "NIPP_CROWN"),
            "NIPP_CROWN": ("pengii", "kawakamii"),
        }
    else:
        raise ValueError(f"Unknown topology variant: {core_variant}")
    children = {
        "ROOT": ("AREN_MRCA", "NIPP_MRCA"),
        "AREN_MRCA": ("brevicaule", "irumtiense"),
        "NIPP_MRCA": ("morii", "NIPP_CORE"),
        **core,
    }
    return children, "ROOT"


def interpretation(context: str, constraint: str, result: Mapping[str, object], delta: int) -> str:
    aren = str(result["optimal_arenicola_mrca_states"])
    if context == "Arenicola_pair_only":
        if constraint == "unconstrained":
            return (
                "The two extant sister species alone do not polarize the colour change: "
                "C and W are equally parsimonious at the Arenicola MRCA."
            )
        if constraint == "AREN_MRCA=C":
            return "Coloured MRCA requires one C->W loss on the brevicaule lineage."
        if constraint == "AREN_MRCA=W":
            return "White MRCA requires one W->C regain on the irumtiense lineage."
    if constraint == "unconstrained":
        return (
            f"With the published coloured-rich Nipponocirsium sister context, equal-cost "
            f"parsimony selects Arenicola MRCA={aren}; this is topology-conditioned, not "
            "a molecular regain/loss demonstration."
        )
    if constraint == "AREN_MRCA=C":
        return "Tests the white-loss history explicitly; delta is relative to the unconstrained sister-context optimum."
    if constraint == "AREN_MRCA=W":
        return (
            "Tests the irumtiense-regain history explicitly. A positive delta means it needs "
            "extra topology-level changes under the current sister context, but it remains a live biological hypothesis."
        )
    if constraint == "ROOT=C":
        return "Conditions the Arenicola+Nipponocirsium parent on a coloured state."
    if constraint == "ROOT=W":
        return (
            "White deep-root sensitivity. Under this external prior the preferred Arenicola "
            "MRCA can switch to W, demonstrating why independent root/branch-length evidence matters."
        )
    return f"Topology-only scenario; delta={delta}."


def scenario_rows(tip_states: Mapping[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    pair_children, pair_root, pair_tips = pair_tree()
    pair_base = enumerate_optima(pair_children, pair_tips, root=pair_root)
    pair_scenarios = [
        ("unconstrained", {}),
        ("AREN_MRCA=C", {"AREN_MRCA": "C"}),
        ("AREN_MRCA=W", {"AREN_MRCA": "W"}),
    ]
    for label, constraints in pair_scenarios:
        result = enumerate_optima(pair_children, pair_tips, root=pair_root, constraints=constraints)
        delta = int(result["minimum_changes"]) - int(pair_base["minimum_changes"])
        rows.append(
            {
                "analysis_context": "Arenicola_pair_only",
                "topology_variant": "brevicaule_sister_irumtiense",
                "constraint": label,
                **result,
                "delta_from_unconstrained": delta,
                "interpretation": interpretation("Arenicola_pair_only", label, result, delta),
            }
        )

    variants = (
        "published_pengii_basal",
        "alternative_kawakamii_basal",
        "alternative_tatakaense_basal",
    )
    full_scenarios = [
        ("unconstrained", {}),
        ("AREN_MRCA=C", {"AREN_MRCA": "C"}),
        ("AREN_MRCA=W", {"AREN_MRCA": "W"}),
        ("ROOT=C", {"ROOT": "C"}),
        ("ROOT=W", {"ROOT": "W"}),
    ]
    for variant in variants:
        children, root = full_tree(variant)
        base = enumerate_optima(children, tip_states, root=root)
        for label, constraints in full_scenarios:
            result = enumerate_optima(children, tip_states, root=root, constraints=constraints)
            delta = int(result["minimum_changes"]) - int(base["minimum_changes"])
            rows.append(
                {
                    "analysis_context": "Arenicola_plus_Nipponocirsium",
                    "topology_variant": variant,
                    "constraint": label,
                    **result,
                    "delta_from_unconstrained": delta,
                    "interpretation": interpretation(
                        "Arenicola_plus_Nipponocirsium", label, result, delta
                    ),
                }
            )
    return rows


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: Sequence[Mapping[str, object]], evidence: Path) -> dict[str, object]:
    pair_free = next(
        row for row in rows
        if row["analysis_context"] == "Arenicola_pair_only" and row["constraint"] == "unconstrained"
    )
    primary = {
        str(row["constraint"]): row
        for row in rows
        if row["analysis_context"] == "Arenicola_plus_Nipponocirsium"
        and row["topology_variant"] == "published_pengii_basal"
    }
    alternative_free = [
        row for row in rows
        if row["analysis_context"] == "Arenicola_plus_Nipponocirsium"
        and row["constraint"] == "unconstrained"
    ]
    return {
        "analysis_version": "arenicola_colour_history_sensitivity_v1",
        "evidence_file": str(evidence),
        "state_coding": {"C": "coloured (light purple/bluish-purple/purple)", "W": "white"},
        "pair_only": {
            "minimum_changes": pair_free["minimum_changes"],
            "optimal_arenicola_mrca_states": pair_free["optimal_arenicola_mrca_states"],
            "conclusion": "brevicaule-irumtiense alone is directionally unresolved: one loss and one regain are tied",
        },
        "published_sister_context": {
            "unconstrained_minimum_changes": primary["unconstrained"]["minimum_changes"],
            "unconstrained_arenicola_mrca": primary["unconstrained"]["optimal_arenicola_mrca_states"],
            "force_coloured_arenicola_cost": primary["AREN_MRCA=C"]["minimum_changes"],
            "force_white_arenicola_cost": primary["AREN_MRCA=W"]["minimum_changes"],
            "white_ancestor_penalty_changes": primary["AREN_MRCA=W"]["delta_from_unconstrained"],
            "force_white_deep_root_arenicola_mrca": primary["ROOT=W"]["optimal_arenicola_mrca_states"],
        },
        "nipp_core_resolution_sensitivity": {
            "variants_tested": [row["topology_variant"] for row in alternative_free],
            "unconstrained_arenicola_states": sorted({str(row["optimal_arenicola_mrca_states"]) for row in alternative_free}),
            "unconstrained_minimum_changes": sorted({int(row["minimum_changes"]) for row in alternative_free}),
        },
        "classification_history_rule": (
            "Historical treatment as C. brevicaule var. irumtiense is not encoded as ancestry. "
            "Reciprocal monophyly implies both extant species descend from an unsampled MRCA."
        ),
        "working_inference": (
            "Equal-cost parsimony on the current published sister context prefers a coloured "
            "Arenicola MRCA and a white loss in C. brevicaule by one change over forcing a "
            "white Arenicola MRCA. However, the pair alone is exactly ambiguous, and a white "
            "deep-root prior reverses the preferred Arenicola state. Therefore irumtiense "
            "colour regain remains an explicit competing hypothesis rather than a rejected one."
        ),
        "claim_limit": (
            "No machine-readable published branch-length tree is yet used here. Do not convert "
            "these parsimony costs into posterior probabilities or claim anthocyanin reactivation. "
            "A full Mk/stochastic-mapping analysis requires recovered branch lengths/topology "
            "and a broader source-backed flower-colour atlas; population ancestry and floral "
            "molecular data are required for demonstrated regain."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tip_states = load_tip_states(args.evidence)
    rows = scenario_rows(tip_states)
    write_csv(args.output, rows)
    summary = build_summary(rows, args.evidence)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("pair_only_states=" + summary["pair_only"]["optimal_arenicola_mrca_states"])
    print("published_sister_context_arenicola_mrca=" + summary["published_sister_context"]["unconstrained_arenicola_mrca"])
    print("published_sister_context_white_ancestor_penalty=" + str(summary["published_sister_context"]["white_ancestor_penalty_changes"]))
    print("working_inference=" + summary["working_inference"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
