#!/usr/bin/env python3
"""Prioritize East Asian Cirsium RAD-seq sampling from the phylogeny-gap audit.

This is a decision-support script. Scores are not inferential statistics.
Transition-critical rows are always promoted to Tier A.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

SCORE_COLUMNS = [
    "transition_information_score",
    "phylogeny_gap_score",
    "reticulation_ploidy_score",
    "geographic_backbone_score",
    "replication_need_score",
]


def as_bool(x) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def assign_tier(row) -> str:
    if as_bool(row.get("transition_critical", False)):
        return "A"
    total = row["priority_total"]
    if total >= 6:
        return "B"
    return "C"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/schema/phylogeny_gap_audit.csv",
        help="Gap-audit CSV",
    )
    parser.add_argument(
        "--output",
        default="analysis/radseq_sampling_priority.csv",
        help="Ranked output CSV",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    missing = [c for c in SCORE_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing score columns: {missing}")

    for col in SCORE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if ((df[col] < 0) | (df[col] > 2)).any():
            raise SystemExit(f"{col} must be scored 0, 1 or 2")

    df["priority_total"] = df[SCORE_COLUMNS].sum(axis=1)
    df["radseq_tier"] = df.apply(assign_tier, axis=1)
    tier_order = pd.Categorical(df["radseq_tier"], ["A", "B", "C"], ordered=True)
    df = df.assign(_tier=tier_order).sort_values(
        ["_tier", "priority_total", "transition_information_score"],
        ascending=[True, False, False],
    ).drop(columns="_tier")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} prioritized rows to {out}")
    print(df[["accepted_taxon", "population_id", "radseq_tier", "priority_total"]].to_string(index=False))


if __name__ == "__main__":
    main()
