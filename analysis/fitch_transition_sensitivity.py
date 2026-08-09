#!/usr/bin/env python3
"""Minimal transition-count sensitivity for focal published East Asian Cirsium topologies.

This is a deliberately simple Fitch-parsimony screen, not a replacement for formal
ML/Bayesian ancestral-state reconstruction. Its purpose is to show how species-level
coding versus population-aware coding changes the minimum number of colour transitions.
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


SCENARIOS = {
    "Nipponocirsium_published_topology": {
        "tree": ("pengii", ("kawakamii", "tatakaense")),
        "states": {
            "pengii": {"C"},
            "kawakamii": {"W"},
            "tatakaense": {"C"},
        },
        "interpretation": "one minimum transition; coloured Fitch root makes kawakamii white loss the parsimonious direction",
    },
    "Sinocirsium_species_level_ambiguous_takaoense": {
        "tree": (("albescens", "takaoense"), ("australe", "fukienense")),
        "states": {
            "albescens": {"W"},
            "takaoense": {"W", "C"},
            "australe": {"C"},
            "fukienense": {"C"},
        },
        "interpretation": "species-level polymorphic tip collapses information and needs only one minimum transition",
    },
    "Sinocirsium_population_aware_takaoense": {
        "tree": (("albescens", ("takaoense_W", "takaoense_C")), ("australe", "fukienense")),
        "states": {
            "albescens": {"W"},
            "takaoense_W": {"W"},
            "takaoense_C": {"C"},
            "australe": {"C"},
            "fukienense": {"C"},
        },
        "interpretation": "population-aware coding raises the minimum to two transitions; direction still requires population history/outgroups",
    },
    "Arenicola_pair": {
        "tree": ("brevicaule", "irumtiense"),
        "states": {
            "brevicaule": {"W"},
            "irumtiense": {"C"},
        },
        "interpretation": "one minimum transition but direction is unresolved from a two-tip pair",
    },
}


def main():
    rows = []
    for scenario, cfg in SCENARIOS.items():
        root_set, steps = fitch(cfg["tree"], cfg["states"])
        rows.append({
            "scenario": scenario,
            "minimum_transitions": steps,
            "fitch_root_states": "|".join(sorted(root_set)),
            "interpretation": cfg["interpretation"],
        })

    out = Path("analysis/fitch_transition_sensitivity.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
