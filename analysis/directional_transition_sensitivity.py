#!/usr/bin/env python3
"""Directional parsimony sensitivity for focal East Asian Cirsium flower-colour systems.

For each published focal topology, calculate the minimum number of total changes,
C->W losses and W->C regains conditional on an explicitly fixed root state.
This is a screening analysis only; it does not replace likelihood/Bayesian ancestral-state
reconstruction with branch lengths and a complete taxon sample.
"""

import csv
from pathlib import Path

C, W = "C", "W"

SCENARIOS = {
    "Nipponocirsium_published_topology": {
        "tree": ("pengii", ("kawakamii", "tatakaense")),
        "tips": {"pengii": C, "kawakamii": W, "tatakaense": C},
    },
    "Sinocirsium_population_aware_takaoense": {
        "tree": (("albescens", ("takaoense_W", "takaoense_C")), ("australe", "fukienense")),
        "tips": {
            "albescens": W,
            "takaoense_W": W,
            "takaoense_C": C,
            "australe": C,
            "fukienense": C,
        },
    },
    "Arenicola_pair": {
        "tree": ("brevicaule", "irumtiense"),
        "tips": {"brevicaule": W, "irumtiense": C},
    },
}


def directional_dp(tree, tips):
    """Return minimum (total, C_to_W, W_to_C) for each state at the node."""
    if isinstance(tree, str):
        observed = tips[tree]
        other = W if observed == C else C
        return {observed: (0, 0, 0), other: (10**9, 0, 0)}

    left, right = tree
    ld = directional_dp(left, tips)
    rd = directional_dp(right, tips)
    out = {}

    for state in (C, W):
        candidates = []
        for ls, lv in ld.items():
            for rs, rv in rd.items():
                total = lv[0] + rv[0]
                c2w = lv[1] + rv[1]
                w2c = lv[2] + rv[2]
                for child_state in (ls, rs):
                    if child_state != state:
                        total += 1
                        if state == C and child_state == W:
                            c2w += 1
                        elif state == W and child_state == C:
                            w2c += 1
                candidates.append((total, c2w, w2c))
        min_total = min(x[0] for x in candidates)
        # Among equally parsimonious reconstructions retain the range later; here store
        # the lexicographically smallest directional decomposition for reproducibility.
        out[state] = min((x for x in candidates if x[0] == min_total), key=lambda x: (x[2], x[1]))
    return out


def main():
    rows = []
    for scenario, cfg in SCENARIOS.items():
        result = directional_dp(cfg["tree"], cfg["tips"])
        for root_state in (C, W):
            total, c2w, w2c = result[root_state]
            rows.append({
                "scenario": scenario,
                "root_state": root_state,
                "minimum_total_changes": total,
                "minimum_C_to_W_losses": c2w,
                "minimum_W_to_C_regains": w2c,
            })

    out = Path("analysis/directional_transition_sensitivity.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
