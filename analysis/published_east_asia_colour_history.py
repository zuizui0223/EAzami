#!/usr/bin/env python3
"""Minimum flower-colour transitions on published East Asian Cirsium topologies.

Only topology/state statements supported by Chang et al. (2025, 2026) are used.
No branch lengths are invented. Two Chang-2026 codings are compared:

1. taxon level: colour-polymorphic var. takaoense is coded {W,C};
2. population aware: one white and one coloured takaoense tip are retained
   inside a monophyletic takaoense lineage.

C = anthocyanin-coloured corolla (pink/pale-purple/bluish-purple)
W = white corolla

This is a parsimony diagnostic, not a demographic or causal-mechanism test.
"""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path
from typing import Mapping, Sequence

C, W = "C", "W"
OUTPUT = Path("analysis/published_east_asia_colour_history.csv")


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


def minimum_directional_histories(
    tree,
    tip_states: Mapping[str, str],
    root_state: str,
) -> tuple[int, list[tuple[int, int]], int]:
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

    minimum = min(row[0] for row in histories)
    best = [row for row in histories if row[0] == minimum]
    combinations = sorted({(row[1], row[2]) for row in best})
    return minimum, combinations, len(best)


def combo_text(combinations: Sequence[tuple[int, int]]) -> str:
    return "|".join(
        f"losses={losses};regains={regains}" for losses, regains in combinations
    )


def scenario_rows() -> list[dict[str, object]]:
    nipponocirsium_2025 = (
        "lineare",
        (
            ("kujuense", ("suffultum", "nipponicum_incomptum")),
            ("pengii", ("kawakamii", "tatakaense")),
        ),
    )
    nipponocirsium_states = {
        "lineare": C,
        "kujuense": C,
        "suffultum": C,
        "nipponicum_incomptum": C,
        "pengii": C,
        "kawakamii": W,
        "tatakaense": C,
    }

    arenicola = ("brevicaule", "irumtiense")
    taiwan_nipponocirsium = (
        "morii",
        ("pengii", ("kawakamii", "tatakaense")),
    )
    arenicola_plus_nipponocirsium = (arenicola, taiwan_nipponocirsium)
    sister_context_states = {
        "brevicaule": W,
        "irumtiense": C,
        "morii": C,
        "pengii": C,
        "kawakamii": W,
        "tatakaense": C,
    }

    sinocirsium_taxon_level = (
        "japonicum",
        (("albescens", "takaoense"), ("australe", "fukienense")),
    )
    full_taxon_level = (
        sinocirsium_taxon_level,
        (arenicola, taiwan_nipponocirsium),
    )
    taxon_level_states = {
        "japonicum": {C},
        "albescens": {W},
        "takaoense": {W, C},
        "australe": {C},
        "fukienense": {C},
        "brevicaule": {W},
        "irumtiense": {C},
        "morii": {C},
        "pengii": {C},
        "kawakamii": {W},
        "tatakaense": {C},
    }

    sinocirsium_population = (
        "japonicum",
        (
            ("albescens", ("takaoense_W", "takaoense_C")),
            ("australe", "fukienense"),
        ),
    )
    full_population = (
        sinocirsium_population,
        (arenicola, taiwan_nipponocirsium),
    )
    population_states = {
        "japonicum": C,
        "albescens": W,
        "takaoense_W": W,
        "takaoense_C": C,
        "australe": C,
        "fukienense": C,
        "brevicaule": W,
        "irumtiense": C,
        "morii": C,
        "pengii": C,
        "kawakamii": W,
        "tatakaense": C,
    }

    definitions = [
        (
            "chang2025_nipponocirsium_species_level",
            "Chang_2025",
            nipponocirsium_2025,
            {key: {value} for key, value in nipponocirsium_states.items()},
            nipponocirsium_states,
            "Published species-level Japanese/Taiwanese Nipponocirsium topology; C. lineare retained as the root reference.",
        ),
        (
            "chang2026_arenicola_plus_taiwan_nipponocirsium",
            "Chang_2026",
            arenicola_plus_nipponocirsium,
            {key: {value} for key, value in sister_context_states.items()},
            sister_context_states,
            "Published sister-clade context around Arenicola; excludes Sinocirsium to isolate the direction relevant to C. brevicaule/C. irumtiense.",
        ),
        (
            "chang2026_full_taxon_level_takaoense_ambiguous",
            "Chang_2026",
            full_taxon_level,
            taxon_level_states,
            None,
            "Published taxon-level topology with var. takaoense coded as polymorphic {W,C}; directional histories are not enumerated for an ambiguous tip.",
        ),
        (
            "chang2026_full_population_aware_takaoense",
            "Chang_2026",
            full_population,
            {key: {value} for key, value in population_states.items()},
            population_states,
            "Population-aware sensitivity: white and bluish-purple takaoense morphs are retained as sister tips inside the published monophyletic variety; exact within-variety sample branching remains uncertain.",
        ),
    ]

    interpretations = {
        "chang2025_nipponocirsium_species_level": (
            "A coloured root requires one C->W transition on C. kawakamii; a white root requires additional coloured gains."
        ),
        "chang2026_arenicola_plus_taiwan_nipponocirsium": (
            "The coloured sister context requires two independent C->W losses, on C. brevicaule and C. kawakamii; regain in C. irumtiense is not required."
        ),
        "chang2026_full_taxon_level_takaoense_ambiguous": (
            "Collapsing polymorphic takaoense to one ambiguous taxon yields three minimum changes and hides the transition occurring within the variety."
        ),
        "chang2026_full_population_aware_takaoense": (
            "The full published context reconstructs a coloured root and four minimum changes. Four parallel losses and three losses plus one regain are equally parsimonious; regain remains possible but is not required."
        ),
    }

    rows: list[dict[str, object]] = []
    for scenario, source, tree, state_sets, fixed_states, caveat in definitions:
        root_states, steps = fitch(tree, state_sets)
        if fixed_states is None:
            c_minimum = "not_enumerated_ambiguous_tip"
            c_combos = "not_enumerated_ambiguous_tip"
            w_minimum = "not_enumerated_ambiguous_tip"
            w_combos = "not_enumerated_ambiguous_tip"
            n_c = ""
            n_w = ""
        else:
            c_minimum, c_values, n_c = minimum_directional_histories(
                tree, fixed_states, C
            )
            w_minimum, w_values, n_w = minimum_directional_histories(
                tree, fixed_states, W
            )
            c_combos = combo_text(c_values)
            w_combos = combo_text(w_values)

        rows.append(
            {
                "scenario": scenario,
                "source": source,
                "minimum_fitch_changes": steps,
                "fitch_root_states": "|".join(sorted(root_states)),
                "minimum_changes_if_root_C": c_minimum,
                "root_C_directional_combinations": c_combos,
                "n_root_C_optimal_assignments": n_c,
                "minimum_changes_if_root_W": w_minimum,
                "root_W_directional_combinations": w_combos,
                "n_root_W_optimal_assignments": n_w,
                "interpretation": interpretations[scenario],
                "topology_or_coding_caveat": caveat,
            }
        )
    return rows


def main() -> int:
    rows = scenario_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
