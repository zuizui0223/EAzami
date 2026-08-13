#!/usr/bin/env python3
"""Generate a source-aware preliminary hypothesis screen from the regional master table.

This script does NOT perform formal ancestral-state reconstruction. It summarizes
which current systems support repeated white-flower evolution, which are merely
candidate regain systems, and which observations are blocked by missing data.
"""

from pathlib import Path
import pandas as pd

INPUT = Path("data/regional_master_taxa_seed.csv")
OUTPUT = Path("analysis/preliminary_hypothesis_screen.csv")


def classify(row):
    state = str(row.get("flower_colour_state", "unknown"))
    role = str(row.get("transition_role", ""))
    group = str(row.get("subsection_or_group", ""))

    if "polymorphic" in state:
        strength = "high_information"
        hypothesis = "within_lineage_white_coloured_transition"
    elif state == "white" and "candidate" in role:
        strength = "strong_candidate"
        hypothesis = "independent_white_origin"
    elif state == "white" and role == "core_white_lineage":
        strength = "direction_unresolved"
        hypothesis = "white_coloured_sister_transition"
    elif "coloured" in state or "purple" in state or "pink" in state or "red" in state:
        strength = "context"
        hypothesis = "coloured_reference"
    else:
        strength = "data_gap"
        hypothesis = "colour_or_phylogeny_gap"

    return pd.Series({
        "preliminary_hypothesis": hypothesis,
        "evidence_strength": strength,
        "group": group,
    })


def main():
    df = pd.read_csv(INPUT)
    out = pd.concat([df[[
        "accepted_taxon", "region", "flower_colour_state", "nuclear_phylogeny_status",
        "transition_role", "radseq_priority"
    ]], df.apply(classify, axis=1)], axis=1)

    # Comparative priority: polymorphism > white in nuclear-resolved clade > unresolved sister pair > context > gaps.
    rank = {
        "high_information": 1,
        "strong_candidate": 2,
        "direction_unresolved": 3,
        "context": 4,
        "data_gap": 5,
    }
    out["priority_rank"] = out["evidence_strength"].map(rank)
    out = out.sort_values(["priority_rank", "group", "accepted_taxon"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)

    print("Current qualitative inference:")
    print("- repeated white-flower evolution: supported as the leading hypothesis")
    print("- true regain/reactivation: not yet demonstrated")
    print("- strongest mechanistic tests: within-lineage white/coloured polymorphisms")
    print("- strongest directional white-loss replicate: Taiwan Nipponocirsium")
    print(f"Wrote {len(out)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
