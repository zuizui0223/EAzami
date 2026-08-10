#!/usr/bin/env python3
"""Topology-only colour-history screen using the exact Figure 1 sample labels.

Chang et al. 2026 Figure 1 panel C displays the six var. takaoense samples as a
pectinate sample topology:

    (((((NH_BP, TJ_BP), FC_BP), LT_W), FB_W), WY_W)

The same figure directly labels FC/TJ/NH as BP and WY/FB/LT as W. This script
uses only that printed topology and the previously source-backed broader
Sinocirsium/East Asian topology fragments. No branch lengths are invented.

The analysis answers a narrow parsimony question:

* when is a W->C transition required at the minimum number of changes?
* how many extra changes are needed by a no-regain history?

It does not identify a causal mutation, exclude introgression or estimate a
transition rate.
"""

from __future__ import annotations

import argparse
import csv
import json
from itertools import product
from pathlib import Path
from typing import Mapping, Sequence

C, W = "C", "W"
DEFAULT_OUTPUT = Path("analysis/chang2026_takaoense_sample_colour_history.csv")
DEFAULT_SUMMARY = Path(
    "data/evidence/generated/chang2026_takaoense_sample_colour_history_summary.json"
)

# Exact six-sample branching transcribed from Figure 1 panel C. The order is not
# treated as a ladderized display only: visible connecting branches define the
# nested topology. Support is deliberately not converted to branch lengths.
TAKAOENSE_SIX = (
    (
        (
            (
                ("NH_3835_BP", "TJ_3807_BP"),
                "FC_3559_BP",
            ),
            "LT_3839_W",
        ),
        "FB_3629_W",
    ),
    "WY_3560_W",
)

TAKAOENSE_STATES = {
    "NH_3835_BP": C,
    "TJ_3807_BP": C,
    "FC_3559_BP": C,
    "LT_3839_W": W,
    "FB_3629_W": W,
    "WY_3560_W": W,
}

ALBESCENS_PLUS_TAKAOENSE = (
    ("albescens_BT_W", "albescens_KZ_W"),
    TAKAOENSE_SIX,
)
ALBESCENS_TAKAOENSE_STATES = {
    **TAKAOENSE_STATES,
    "albescens_BT_W": W,
    "albescens_KZ_W": W,
}

# Source-backed taxon relationships used in the existing East Asian screen:
# broad C. japonicum is sister to the ((albescens,takaoense),(australe,fukienense))
# grouping within Sinocirsium.
SINOCIRSIUM_SAMPLE_AWARE = (
    "japonicum_C",
    (
        ALBESCENS_PLUS_TAKAOENSE,
        ("australe_C", "fukienense_C"),
    ),
)
SINOCIRSIUM_STATES = {
    **ALBESCENS_TAKAOENSE_STATES,
    "japonicum_C": C,
    "australe_C": C,
    "fukienense_C": C,
}

ARENICOLA = ("brevicaule_W", "irumtiense_C")
TAIWAN_NIPPONOCIRSIUM = (
    "morii_C",
    ("pengii_C", ("kawakamii_W", "tatakaense_C")),
)
FULL_EAST_ASIA_SAMPLE_AWARE = (
    SINOCIRSIUM_SAMPLE_AWARE,
    (ARENICOLA, TAIWAN_NIPPONOCIRSIUM),
)
FULL_STATES = {
    **SINOCIRSIUM_STATES,
    "brevicaule_W": W,
    "irumtiense_C": C,
    "morii_C": C,
    "pengii_C": C,
    "kawakamii_W": W,
    "tatakaense_C": C,
}


def fitch(tree, states: Mapping[str, set[str]]) -> tuple[set[str], int]:
    if isinstance(tree, str):
        return set(states[tree]), 0
    left_states, left_cost = fitch(tree[0], states)
    right_states, right_cost = fitch(tree[1], states)
    shared = left_states & right_states
    if shared:
        return shared, left_cost + right_cost
    return left_states | right_states, left_cost + right_cost + 1


def internal_nodes(tree, prefix: str = "n"):
    nodes: list[tuple[str, str, str]] = []
    counter = [0]

    def walk(subtree):
        if isinstance(subtree, str):
            return subtree
        counter[0] += 1
        name = f"{prefix}{counter[0]}"
        left = walk(subtree[0])
        right = walk(subtree[1])
        nodes.append((name, left, right))
        return name

    return walk(tree), nodes


def enumerate_histories(
    tree,
    tip_states: Mapping[str, str],
    root_state: str,
) -> list[tuple[int, int, int]]:
    """Return total changes, C->W losses and W->C regains for every history."""
    root, nodes = internal_nodes(tree)
    variable_nodes = [name for name, _, _ in nodes if name != root]
    histories: list[tuple[int, int, int]] = []

    for values in product((C, W), repeat=len(variable_nodes)):
        states = dict(tip_states)
        states[root] = root_state
        states.update(dict(zip(variable_nodes, values)))
        losses = 0
        regains = 0
        for parent, left, right in nodes:
            for child in (left, right):
                parent_state = states[parent]
                child_state = states[child]
                if parent_state == C and child_state == W:
                    losses += 1
                elif parent_state == W and child_state == C:
                    regains += 1
        histories.append((losses + regains, losses, regains))
    return histories


def minimum_summary(
    tree,
    tip_states: Mapping[str, str],
    root_state: str,
) -> dict[str, object]:
    histories = enumerate_histories(tree, tip_states, root_state)
    minimum = min(row[0] for row in histories)
    optimal = [row for row in histories if row[0] == minimum]
    combinations = sorted({(row[1], row[2]) for row in optimal})

    no_regain = [row for row in histories if row[2] == 0]
    if no_regain:
        no_regain_minimum: int | str = min(row[0] for row in no_regain)
        no_regain_penalty: int | str = no_regain_minimum - minimum
    else:
        no_regain_minimum = "impossible"
        no_regain_penalty = "impossible"

    return {
        "root_state": root_state,
        "minimum_changes": minimum,
        "directional_combinations": combinations,
        "n_optimal_assignments": len(optimal),
        "regain_required_at_global_minimum": all(
            regains > 0 for _, regains in combinations
        ),
        "minimum_no_regain_changes": no_regain_minimum,
        "no_regain_change_penalty": no_regain_penalty,
    }


def combo_text(values: Sequence[tuple[int, int]]) -> str:
    return "|".join(
        f"losses={losses};regains={regains}" for losses, regains in values
    )


def scenario_rows() -> list[dict[str, object]]:
    definitions = [
        {
            "scenario": "takaoense_six_samples_root_W",
            "scope": "six var. takaoense samples",
            "tree": TAKAOENSE_SIX,
            "states": TAKAOENSE_STATES,
            "root_state": W,
            "interpretation": (
                "With a white root for the six-sample variety, the three BP tips require "
                "one W->C transition and no losses."
            ),
            "caveat": (
                "Root state is assumed; Figure 1 shows morphology-associated topology but "
                "does not itself prove the causal direction."
            ),
        },
        {
            "scenario": "takaoense_six_samples_root_C",
            "scope": "six var. takaoense samples",
            "tree": TAKAOENSE_SIX,
            "states": TAKAOENSE_STATES,
            "root_state": C,
            "interpretation": (
                "A coloured root needs at least three changes; both a three-loss history "
                "and a two-loss/one-regain history are optimal."
            ),
            "caveat": "Root C is a sensitivity assumption for the within-variety sample tree.",
        },
        {
            "scenario": "albescens_plus_takaoense_root_C",
            "scope": "white var. albescens plus six var. takaoense samples",
            "tree": ALBESCENS_PLUS_TAKAOENSE,
            "states": ALBESCENS_TAKAOENSE_STATES,
            "root_state": C,
            "interpretation": (
                "With a coloured root outside the white albescens/takaoense grouping, "
                "the minimum history contains two losses and one BP regain; a no-regain "
                "history costs one additional change."
            ),
            "caveat": (
                "Treats the displayed albescens pair as the sister group to the six-sample "
                "takaoense clade and ignores branch lengths."
            ),
        },
        {
            "scenario": "sinocirsium_exact_sample_topology_root_C",
            "scope": "sample-aware Sinocirsium",
            "tree": SINOCIRSIUM_SAMPLE_AWARE,
            "states": SINOCIRSIUM_STATES,
            "root_state": C,
            "interpretation": (
                "The minimum coloured-root Sinocirsium history is one C->W loss on the "
                "albescens/takaoense lineage followed by one W->C transition leading to "
                "the BP takaoense sample clade. A no-regain history needs four losses."
            ),
            "caveat": (
                "Topology-only diagnostic; the paper reports reticulation and several short "
                "sample internodes have weak local support."
            ),
        },
        {
            "scenario": "full_east_asia_exact_takaoense_root_C",
            "scope": "sample-aware full East Asian focal topology",
            "tree": FULL_EAST_ASIA_SAMPLE_AWARE,
            "states": FULL_STATES,
            "root_state": C,
            "interpretation": (
                "The minimum coloured-root focal history has three losses and one regain. "
                "The exact takaoense sample topology removes the previous equal-parsimony "
                "four-loss/no-regain solution; a no-regain history requires six changes."
            ),
            "caveat": (
                "Combines source-backed topology fragments without branch lengths; not a "
                "substitute for the exact Chang Newick, demographic tests or introgression models."
            ),
        },
    ]

    rows: list[dict[str, object]] = []
    for definition in definitions:
        tree = definition["tree"]
        states = definition["states"]
        state_sets = {key: {value} for key, value in states.items()}
        root_states, fitch_steps = fitch(tree, state_sets)
        result = minimum_summary(tree, states, definition["root_state"])
        rows.append(
            {
                "scenario": definition["scenario"],
                "scope": definition["scope"],
                "source": "Chang_2026_Figure1_panel_C_plus_published_topology_fragments",
                "root_state_assumption": definition["root_state"],
                "minimum_fitch_changes_unconstrained_root": fitch_steps,
                "fitch_root_states": "|".join(sorted(root_states)),
                "minimum_changes_fixed_root": result["minimum_changes"],
                "optimal_directional_combinations": combo_text(
                    result["directional_combinations"]
                ),
                "n_optimal_assignments": result["n_optimal_assignments"],
                "regain_required_at_global_minimum": (
                    "yes" if result["regain_required_at_global_minimum"] else "no"
                ),
                "minimum_no_regain_changes": result["minimum_no_regain_changes"],
                "no_regain_change_penalty": result["no_regain_change_penalty"],
                "interpretation": definition["interpretation"],
                "topology_or_model_caveat": definition["caveat"],
            }
        )
    return rows


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = scenario_rows()
    write_csv(args.output, rows)

    by_scenario = {row["scenario"]: row for row in rows}
    summary = {
        "figure1_six_sample_topology": "(((((NH_BP,TJ_BP),FC_BP),LT_W),FB_W),WY_W)",
        "direct_labels": {
            "BP": ["FC-3559", "TJ-3807", "NH-3835"],
            "W": ["WY-3560", "FB-3629", "LT-3839"],
        },
        "six_sample_unconstrained_fitch_changes": by_scenario[
            "takaoense_six_samples_root_W"
        ]["minimum_fitch_changes_unconstrained_root"],
        "six_sample_fitch_root_states": by_scenario[
            "takaoense_six_samples_root_W"
        ]["fitch_root_states"],
        "sinocirsium_coloured_root_minimum": by_scenario[
            "sinocirsium_exact_sample_topology_root_C"
        ]["optimal_directional_combinations"],
        "sinocirsium_no_regain_minimum_changes": by_scenario[
            "sinocirsium_exact_sample_topology_root_C"
        ]["minimum_no_regain_changes"],
        "full_east_asia_coloured_root_minimum": by_scenario[
            "full_east_asia_exact_takaoense_root_C"
        ]["optimal_directional_combinations"],
        "full_east_asia_no_regain_minimum_changes": by_scenario[
            "full_east_asia_exact_takaoense_root_C"
        ]["minimum_no_regain_changes"],
        "current_inference": (
            "On the displayed exact sample topology and a coloured broader root, a "
            "takaoense W->C transition is required in every minimum-change history. "
            "This is topology-level support for candidate regain, not proof of a "
            "molecular restoration or exclusion of introgression/standing variation."
        ),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    for row in rows:
        print(
            row["scenario"],
            row["minimum_changes_fixed_root"],
            row["optimal_directional_combinations"],
            row["minimum_no_regain_changes"],
        )
    print(args.output)
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
