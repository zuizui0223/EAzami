#!/usr/bin/env python3
"""Rank sampling/data gaps by a transparent proxy for expected information gain.

This is NOT a formal Bayesian EIG calculation. It is a deterministic decision-sensitivity
score intended for the current stage, before exact full-tree posterior distributions are
available. The score rewards data that can change colour-transition direction/count,
resolve within-lineage polymorphism, test introgression/ancestral polymorphism, or fill
an actual nuclear-placement gap. It penalizes high technical complexity where the same
question can be answered by an easier comparison.

Formal EIG should replace this proxy once exact published trees/branch lengths and a
probabilistic ancestral-state/population-history model are available.
"""

import csv
from pathlib import Path

WEIGHTS = {
    "direction": 4.0,
    "transition_count": 3.0,
    "within_lineage": 3.0,
    "introgression": 2.5,
    "mechanism": 2.5,
    "nuclear_gap": 2.0,
    "cross_region": 1.5,
    "replicate": 1.5,
    "technical_penalty": -1.0,
}

CANDIDATES = [
    {
        "candidate": "takaoense_white_vs_coloured_population_sampling",
        "direction": 0.75, "transition_count": 1, "within_lineage": 1,
        "introgression": 1, "mechanism": 1, "nuclear_gap": 0,
        "cross_region": 0, "replicate": 1, "technical_penalty": 0,
        "action": "sample paired white and bluish-purple populations/individuals",
        "notes": "Population-aware coding changes minimum transition count; same-lineage contrast is best causal design and can distinguish mutation vs ancestral polymorphism/introgression.",
    },
    {
        "candidate": "C_pendulum_Japan_white_vs_purple",
        "direction": 0.5, "transition_count": 0.75, "within_lineage": 1,
        "introgression": 0.5, "mechanism": 1, "nuclear_gap": 0.5,
        "cross_region": 0.5, "replicate": 1, "technical_penalty": 0,
        "action": "paired Japanese white and purple populations",
        "notes": "Independent within-species white polymorphism; exact Moreyra placement remains to verify, but mechanistic information is high.",
    },
    {
        "candidate": "C_pendulum_China_bridge",
        "direction": 0.75, "transition_count": 0.5, "within_lineage": 0.5,
        "introgression": 1, "mechanism": 0.25, "nuclear_gap": 0.5,
        "cross_region": 1, "replicate": 0.5, "technical_penalty": 0,
        "action": "sample Chinese/NE Asian coloured populations",
        "notes": "Tests whether Japanese white populations are nested within a broader coloured background and whether geography changes the inferred white origin.",
    },
    {
        "candidate": "C_sieboldii_Japan_white_vs_purple",
        "direction": 0.5, "transition_count": 0.75, "within_lineage": 1,
        "introgression": 0.5, "mechanism": 1, "nuclear_gap": 0.5,
        "cross_region": 0.5, "replicate": 1, "technical_penalty": 0,
        "action": "paired Japanese white and purple populations",
        "notes": "Independent within-species replicate; value depends on relocating stable white populations and verifying nuclear placement.",
    },
    {
        "candidate": "C_sieboldii_Zhejiang_bridge",
        "direction": 0.75, "transition_count": 0.5, "within_lineage": 0.5,
        "introgression": 1, "mechanism": 0.25, "nuclear_gap": 0.5,
        "cross_region": 1, "replicate": 0.5, "technical_penalty": 0,
        "action": "verify taxonomy/locality and sample Zhejiang populations",
        "notes": "Can convert a Japan-only story into a transregional within-species history and test whether white is geographically derived.",
    },
    {
        "candidate": "Arenicola_brevicaule_irumtiense_population_genomics",
        "direction": 0.25, "transition_count": 0.25, "within_lineage": 0,
        "introgression": 1, "mechanism": 1, "nuclear_gap": 0,
        "cross_region": 0.25, "replicate": 1, "technical_penalty": 0,
        "action": "sample multiple brevicaule and irumtiense populations for gene flow, colour haplotypes and mechanistic comparison",
        "notes": "Published sister-clade context (Nipponocirsium) already favours a coloured ancestral context, so Arenicola is no longer a high-value topology-gap target. Its remaining value is population history, introgression and replicated white-mechanism tests.",
    },
    {
        "candidate": "C_kawakamii_vs_C_tatakaense_population_genomics",
        "direction": 0.5, "transition_count": 0.5, "within_lineage": 0,
        "introgression": 1, "mechanism": 1, "nuclear_gap": 0,
        "cross_region": 0, "replicate": 1, "technical_penalty": 1,
        "action": "matched polyploid population sampling plus pigment/RNA data",
        "notes": "White-loss direction is already relatively strong; extra value is testing repeated mechanism and gene flow, but polyploid handling raises technical cost.",
    },
    {
        "candidate": "C_pengii_additional_population_sampling",
        "direction": 0.5, "transition_count": 0.25, "within_lineage": 0,
        "introgression": 0.5, "mechanism": 0.25, "nuclear_gap": 0,
        "cross_region": 0, "replicate": 0.5, "technical_penalty": 0,
        "action": "limited basal-coloured anchor sampling",
        "notes": "Species-level position already orients the kawakamii loss; dense sampling adds less information than focal white/coloured contrasts.",
    },
    {
        "candidate": "C_shansiense_nuclear_placement",
        "direction": 0.25, "transition_count": 0.25, "within_lineage": 0,
        "introgression": 0, "mechanism": 0, "nuclear_gap": 1,
        "cross_region": 0.5, "replicate": 0.25, "technical_penalty": 0,
        "action": "first recover existing modern nuclear placement; RAD only if still absent",
        "notes": "Useful backbone taxon but currently coloured and not known to sit next to a white transition, so information gain for the colour question is modest.",
    },
    {
        "candidate": "C_leducii_nuclear_placement",
        "direction": 0.25, "transition_count": 0.25, "within_lineage": 0,
        "introgression": 0, "mechanism": 0, "nuclear_gap": 1,
        "cross_region": 0.5, "replicate": 0.25, "technical_penalty": 0,
        "action": "first recover existing modern nuclear placement; RAD only if still absent",
        "notes": "Backbone value but weak direct leverage on currently identified white/regain candidates.",
    },
]


def score(row):
    return sum(row[k] * w for k, w in WEIGHTS.items())


def main():
    rows = []
    for row in CANDIDATES:
        out = dict(row)
        out["proxy_eig_score"] = round(score(row), 3)
        rows.append(out)
    rows.sort(key=lambda r: r["proxy_eig_score"], reverse=True)
    for i, row in enumerate(rows, 1):
        row["rank"] = i

    out_path = Path("analysis/proxy_information_gain_priority.csv")
    fields = ["rank", "candidate", "proxy_eig_score", "direction", "transition_count",
              "within_lineage", "introgression", "mechanism", "nuclear_gap",
              "cross_region", "replicate", "technical_penalty", "action", "notes"]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row["rank"], row["candidate"], row["proxy_eig_score"])


if __name__ == "__main__":
    main()
