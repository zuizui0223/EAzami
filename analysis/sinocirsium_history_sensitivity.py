#!/usr/bin/env python3
"""Parsimony sensitivity for Sinocirsium colour histories.

Uses the published macro-topology from Chang et al. 2026:
  japonicum basal; Taiwanese sister pairs albescens-takaoense and australe-fukienense.

Population-aware takaoense coding is represented by one white and one bluish-purple tip.
This is a topology-level diagnostic only: internal relationships among takaoense samples
are weak/variable in the published study, so alternative population histories remain open.
"""

import csv
from itertools import product
from pathlib import Path

C, W = "C", "W"

# Rooted binary topology:
# (japonicum, ((albescens, (takaoense_W, takaoense_C)), (australe, fukienense)))
TREE = (
    "japonicum",
    (
        ("albescens", ("takaoense_W", "takaoense_C")),
        ("australe", "fukienense"),
    ),
)

TIP_STATES = {
    "japonicum": C,
    "albescens": W,
    "takaoense_W": W,
    "takaoense_C": C,
    "australe": C,
    "fukienense": C,
}


def internal_nodes(tree, prefix="n"):
    nodes = []
    counter = [0]
    def walk(t):
        if isinstance(t, str):
            return t
        counter[0] += 1
        name = f"{prefix}{counter[0]}"
        l = walk(t[0]); r = walk(t[1])
        nodes.append((name, l, r))
        return name
    root = walk(tree)
    return root, nodes


def enumerate_histories(root_state=C):
    root, nodes = internal_nodes(TREE)
    node_names = [n for n, _, _ in nodes]
    # root is included among node_names; fix it to requested state.
    variable = [n for n in node_names if n != root]
    rows = []
    for vals in product([C, W], repeat=len(variable)):
        states = dict(TIP_STATES)
        states[root] = root_state
        states.update(dict(zip(variable, vals)))
        losses = regains = 0
        for parent, left, right in nodes:
            for child in (left, right):
                ps, cs = states[parent], states[child]
                if ps == C and cs == W:
                    losses += 1
                elif ps == W and cs == C:
                    regains += 1
        total = losses + regains
        rows.append((total, losses, regains, states))
    m = min(r[0] for r in rows)
    return [r for r in rows if r[0] == m]


def main():
    out = []
    for root_state in (C, W):
        histories = enumerate_histories(root_state)
        combos = sorted(set((h[1], h[2]) for h in histories))
        for losses, regains in combos:
            n = sum(1 for h in histories if (h[1], h[2]) == (losses, regains))
            out.append({
                "root_state": root_state,
                "minimum_total_changes": histories[0][0],
                "losses_C_to_W": losses,
                "regains_W_to_C": regains,
                "n_equally_parsimonious_assignments": n,
                "interpretation": (
                    "Under a coloured root, both repeated white losses and shared white ancestry + a coloured takaoense regain can be equally parsimonious."
                    if root_state == C else
                    "A white root requires multiple coloured gains and is disfavoured by the basal coloured japonicum tip under the published macro-topology."
                ),
            })
    path = Path("analysis/sinocirsium_history_sensitivity.csv")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out[0].keys())
        writer.writeheader(); writer.writerows(out)
    for row in out:
        print(row)


if __name__ == "__main__":
    main()
