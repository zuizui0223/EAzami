#!/usr/bin/env python3
"""Exploratory two-state Mk analysis for focal East Asian Cirsium clades.

This analysis uses published *topologies* already encoded in the project, with equal
branch lengths scaled across several values because the exact published Newick trees
and branch lengths have not yet been recovered. It is therefore a sensitivity screen,
not a final ancestral-state reconstruction.

States:
    C = anthocyanin-coloured
    W = white

Models:
    ER  : q(C->W) == q(W->C)
    ARD : q(C->W) and q(W->C) estimated separately

The implementation uses a standard two-state continuous-time Markov chain and
Felsenstein pruning. Rates are estimated by grid search so the script has no external
Python dependencies.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

STATES = ("C", "W")


def tip(state):
    return ("tip", state)


def node(*children):
    # each child is (subtree, branch_length)
    return ("node", list(children))


TREES = {
    "Nipponocirsium": node(
        (tip("C"), 1.0),  # C. pengii
        (node((tip("W"), 1.0), (tip("C"), 1.0)), 1.0),  # kawakamii, tatakaense
    ),
    "Sinocirsium_population_aware": node(
        (
            node(
                (tip("W"), 1.0),  # albescens
                (node((tip("W"), 1.0), (tip("C"), 1.0)), 1.0),  # takaoense W/C
            ),
            1.0,
        ),
        (node((tip("C"), 1.0), (tip("C"), 1.0)), 1.0),  # australe, fukienense
    ),
    "Arenicola_pair": node((tip("W"), 1.0), (tip("C"), 1.0)),
}


def transition_matrix(q_cw: float, q_wc: float, t: float):
    s = q_cw + q_wc
    decay = math.exp(-s * t)
    pi_c = q_wc / s
    pi_w = q_cw / s
    return (
        (pi_c + pi_w * decay, pi_w * (1.0 - decay)),
        (pi_c * (1.0 - decay), pi_w + pi_c * decay),
    )


def prune(tree, q_cw: float, q_wc: float, branch_scale: float):
    if tree[0] == "tip":
        return (1.0, 0.0) if tree[1] == "C" else (0.0, 1.0)

    like = [1.0, 1.0]
    for child, length in tree[1]:
        child_like = prune(child, q_cw, q_wc, branch_scale)
        p = transition_matrix(q_cw, q_wc, length * branch_scale)
        for parent_state in (0, 1):
            contribution = (
                p[parent_state][0] * child_like[0]
                + p[parent_state][1] * child_like[1]
            )
            like[parent_state] *= contribution
    return tuple(like)


def log_likelihood(tree, q_cw, q_wc, branch_scale, root_mode="equilibrium"):
    like = prune(tree, q_cw, q_wc, branch_scale)
    if root_mode == "C":
        prior = (1.0, 0.0)
    elif root_mode == "W":
        prior = (0.0, 1.0)
    else:
        s = q_cw + q_wc
        prior = (q_wc / s, q_cw / s)
    total = prior[0] * like[0] + prior[1] * like[1]
    return math.log(max(total, 1e-300))


def log_grid(lo=0.01, hi=10.0, n=100):
    a, b = math.log(lo), math.log(hi)
    return [math.exp(a + (b - a) * i / (n - 1)) for i in range(n)]


def fit_er(trees, branch_scale, rates):
    best = (-math.inf, None)
    for q in rates:
        ll = sum(log_likelihood(t, q, q, branch_scale) for t in trees)
        if ll > best[0]:
            best = (ll, q)
    return best


def fit_ard(trees, branch_scale, rates):
    best = (-math.inf, None, None)
    for q_cw in rates:
        for q_wc in rates:
            ll = sum(log_likelihood(t, q_cw, q_wc, branch_scale) for t in trees)
            if ll > best[0]:
                best = (ll, q_cw, q_wc)
    return best


def main():
    rates = log_grid()
    scales = (0.25, 0.5, 1.0, 2.0)
    analyses = {
        "Nipponocirsium_only": [TREES["Nipponocirsium"]],
        "Sinocirsium_only": [TREES["Sinocirsium_population_aware"]],
        "Arenicola_only": [TREES["Arenicola_pair"]],
        "Taiwan_two_clades_composite": [
            TREES["Nipponocirsium"],
            TREES["Sinocirsium_population_aware"],
        ],
        "all_three_focal_clades_composite": list(TREES.values()),
    }

    rows = []
    for label, trees in analyses.items():
        for scale in scales:
            ll_er, q_er = fit_er(trees, scale, rates)
            ll_ard, q_cw, q_wc = fit_ard(trees, scale, rates)
            aic_er = -2.0 * ll_er + 2.0 * 1
            aic_ard = -2.0 * ll_ard + 2.0 * 2
            rows.append(
                {
                    "analysis": label,
                    "branch_scale": scale,
                    "logLik_ER": round(ll_er, 6),
                    "q_ER": round(q_er, 6),
                    "AIC_ER": round(aic_er, 6),
                    "logLik_ARD": round(ll_ard, 6),
                    "q_C_to_W": round(q_cw, 6),
                    "q_W_to_C": round(q_wc, 6),
                    "AIC_ARD": round(aic_ard, 6),
                    "delta_AIC_ARD_minus_ER": round(aic_ard - aic_er, 6),
                }
            )

    out = Path("analysis/mk_rate_sensitivity.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
