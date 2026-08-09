#!/usr/bin/env python3
"""Summarize the regional master taxon seed for Chapter 2 planning.

This script is descriptive only. It does not infer evolutionary transitions.
"""
from pathlib import Path
import pandas as pd

INFILE = Path("data/regional_master_taxa_seed.csv")
OUTFILE = Path("analysis/master_taxa_priority_summary.csv")


def main():
    df = pd.read_csv(INFILE)
    required = {
        "accepted_taxon", "region", "flower_colour_state",
        "nuclear_phylogeny_status", "transition_role", "radseq_priority"
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"Missing columns: {missing}")

    # Preserve unknowns explicitly; never interpret unknown as coloured/white.
    df["colour_known"] = ~df["flower_colour_state"].fillna("unknown").eq("unknown")
    df["is_white_candidate"] = df["flower_colour_state"].fillna("").str.contains("white", case=False)
    df["is_polymorphic_candidate"] = df["flower_colour_state"].fillna("").str.contains("polymorphic|variable", case=False, regex=True)
    df["nuclear_gap"] = df["nuclear_phylogeny_status"].fillna("").str.contains("no_verified|not_verified|gap", case=False, regex=True)

    out = df[[
        "accepted_taxon", "region", "flower_colour_state", "colour_known",
        "is_white_candidate", "is_polymorphic_candidate", "nuclear_phylogeny_status",
        "nuclear_gap", "transition_role", "radseq_priority"
    ]].sort_values(["radseq_priority", "is_white_candidate", "is_polymorphic_candidate"], ascending=[True, False, False])

    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTFILE, index=False)

    print(f"taxa={len(df)}")
    print(f"colour_known={int(df['colour_known'].sum())}")
    print(f"white_or_white-containing={int(df['is_white_candidate'].sum())}")
    print(f"polymorphic_or_variable={int(df['is_polymorphic_candidate'].sum())}")
    print(f"nuclear_gap={int(df['nuclear_gap'].sum())}")
    print("\nRAD priorities:")
    print(df["radseq_priority"].fillna("NA").value_counts().to_string())
    print(f"\nWrote {OUTFILE}")


if __name__ == "__main__":
    main()
