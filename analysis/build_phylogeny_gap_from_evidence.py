#!/usr/bin/env python3
"""Build a first-pass phylogeny-gap table from flower-colour and published nuclear-coverage evidence.

This script does not infer phylogeny. It merges evidence streams and assigns conservative
flags that guide manual RAD-seq prioritization. Existing nuclear transcriptomic coverage
prevents a taxon from being labelled a species-level phylogeny gap, but population-level
replication can still be high priority for transition history.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def normalize_taxon(x: str) -> str:
    return " ".join(str(x).strip().split())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--colour", default="data/schema/flower_colour_records.csv")
    ap.add_argument("--coverage", default="data/evidence/published_nuclear_phylogeny_coverage_seed.csv")
    ap.add_argument("--output", default="analysis/phylogeny_gap_joined.csv")
    args = ap.parse_args()

    colour = pd.read_csv(args.colour)
    coverage = pd.read_csv(args.coverage)

    if "accepted_taxon" not in colour.columns:
        raise SystemExit("Colour atlas must contain accepted_taxon")
    if "taxon" not in coverage.columns:
        raise SystemExit("Coverage table must contain taxon")

    colour["taxon_key"] = colour["accepted_taxon"].map(normalize_taxon)
    coverage["taxon_key"] = coverage["taxon"].map(normalize_taxon)

    # Collapse colour evidence conservatively to taxon-level states while retaining polymorphism.
    state_col = "colour_state" if "colour_state" in colour.columns else "flower_colour_state"
    if state_col not in colour.columns:
        raise SystemExit("Colour atlas must contain colour_state or flower_colour_state")

    def collapse_states(series: pd.Series) -> str:
        vals = sorted({str(v).strip() for v in series.dropna() if str(v).strip()})
        if not vals:
            return "unknown"
        if len(vals) == 1:
            return vals[0]
        return "polymorphic:" + "|".join(vals)

    csum = (
        colour.groupby("taxon_key", as_index=False)
        .agg(
            accepted_taxon=("accepted_taxon", "first"),
            atlas_colour_state=(state_col, collapse_states),
            colour_evidence_n=(state_col, "count"),
        )
    )

    keep = [
        "taxon_key", "nuclear_phylogenomic_coverage", "individuals_reported",
        "source_year", "source_doi", "ncbi_bioproject", "ploidy_or_chromosome_note",
        "radseq_role", "notes"
    ]
    merged = csum.merge(coverage[keep], on="taxon_key", how="left")

    merged["published_nuclear_covered"] = (
        merged["nuclear_phylogenomic_coverage"].fillna("no").astype(str).str.lower().eq("yes")
    )
    merged["species_level_phylogeny_gap"] = ~merged["published_nuclear_covered"]

    state = merged["atlas_colour_state"].fillna("unknown").astype(str).str.lower()
    merged["colour_transition_interest"] = (
        state.str.contains("white") | state.str.contains("polymorphic")
    )

    # Existing coverage + transition interest means population/history follow-up, not tree repetition.
    merged["recommended_action"] = "backbone/colour curation"
    merged.loc[merged["species_level_phylogeny_gap"], "recommended_action"] = "RAD-seq backbone candidate"
    merged.loc[
        merged["published_nuclear_covered"] & merged["colour_transition_interest"],
        "recommended_action",
    ] = "population RAD-seq / gene-flow / mechanism"
    merged.loc[
        merged["species_level_phylogeny_gap"] & merged["colour_transition_interest"],
        "recommended_action",
    ] = "Tier-A candidate: resolve placement before transition inference"

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.sort_values(
        ["colour_transition_interest", "species_level_phylogeny_gap", "accepted_taxon"],
        ascending=[False, False, True],
    ).to_csv(out, index=False)
    print(f"Wrote {len(merged)} rows to {out}")


if __name__ == "__main__":
    main()
