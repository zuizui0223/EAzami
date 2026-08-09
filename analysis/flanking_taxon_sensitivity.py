#!/usr/bin/env python3
"""Simple sensitivity screen for transition-critical missing flanking taxa.

The purpose is to show which missing sister/outgroup state would change the inferred
ancestral direction for a focal white/coloured pair. This is a prioritization tool, not
formal ancestral-state inference.
"""

import csv
from pathlib import Path


def fitch(tree, states):
    if isinstance(tree, str):
        return {states[tree]}, 0
    left, right = tree
    ls, lc = fitch(left, states)
    rs, rc = fitch(right, states)
    inter = ls & rs
    if inter:
        return inter, lc + rc
    return ls | rs, lc + rc + 1


def main():
    rows = []

    # Arenicola pair is directionally unresolved without a flanking lineage.
    tree = ("flanking", ("brevicaule", "irumtiense"))
    for flank_state in ("C", "W"):
        states = {"flanking": flank_state, "brevicaule": "W", "irumtiense": "C"}
        root, steps = fitch(tree, states)
        rows.append({
            "focal_system": "Arenicola",
            "hypothetical_flanking_state": flank_state,
            "minimum_transitions": steps,
            "fitch_root_states": "|".join(sorted(root)),
            "directional_consequence": (
                "supports coloured ancestry / brevicaule loss" if flank_state == "C"
                else "supports white ancestry / irumtiense regain"
            ),
            "sampling_value": "very_high",
        })

    out = Path("analysis/flanking_taxon_sensitivity.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
