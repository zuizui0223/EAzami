#!/usr/bin/env python3
"""Existing-data parsimony screen for the Arenicola + Nipponocirsium sister relationship.

Published topology source: Chang et al. 2026, with Arenicola sister to Nipponocirsium.
Nipponocirsium states used here are source-backed: morii pink/coloured; pengii and tatakaense
bluish-purple/coloured; kawakamii white. Arenicola: brevicaule white, irumtiense coloured.

This is a topology-only parsimony diagnostic, not a substitute for full Mk/stochastic mapping.
"""

import csv
from pathlib import Path


def fitch(tree, states):
    if isinstance(tree, str):
        return set(states[tree]), 0
    left, right = tree
    ls, lc = fitch(left, states)
    rs, rc = fitch(right, states)
    inter = ls & rs
    if inter:
        return inter, lc + rc
    return ls | rs, lc + rc + 1


def main():
    # Simplified published topology: Arenicola sister to Nipponocirsium;
    # within Nipponocirsium, morii basal and pengii basal to kawakamii+tatakaense.
    tree = (("brevicaule", "irumtiense"),
            ("morii", ("pengii", ("kawakamii", "tatakaense"))))
    states = {
        "brevicaule": {"W"},
        "irumtiense": {"C"},
        "morii": {"C"},
        "pengii": {"C"},
        "kawakamii": {"W"},
        "tatakaense": {"C"},
    }
    root_states, steps = fitch(tree, states)

    rows = [
        {
            "analysis": "Arenicola_plus_Nipponocirsium_published_context",
            "minimum_transitions": steps,
            "fitch_root_states": "|".join(sorted(root_states)),
            "interpretation": (
                "The combined sister-clade context reconstructs a coloured root under Fitch parsimony. "
                "The minimum-history interpretation is therefore two independent C->W losses: one on "
                "C. brevicaule and one on C. kawakamii. A W->C regain on C. irumtiense is not required by "
                "the currently published sister-clade context."
            ),
        }
    ]
    out = Path("analysis/arenicola_sister_context.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(rows[0])


if __name__ == "__main__":
    main()
