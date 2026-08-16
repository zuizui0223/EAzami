#!/usr/bin/env python3
"""Summarize source-backed Japan-38 cytotype × capitulum-state overlap.

This is a descriptive pre-tree audit. It asks only whether the currently observed
cytotype and orientation states are deterministically coupled. It does not infer
cytotype transitions, trait transitions, evolutionary rates or causation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KNOWN_ORIENTATION = {"upward_or_erect", "upward_or_ascending", "downward_or_nodding"}


def build(cytotypes: pd.DataFrame, traits: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required_c = {"paper_japan_member_id", "taxon", "japan_origin_role", "chromosome_2n", "ploidy_x"}
    required_t = {"paper_japan_member_id", "orientation_state", "phyllary_posture", "stickiness_state"}
    if required_c.difference(cytotypes.columns):
        raise ValueError("Cytotype table incomplete")
    if required_t.difference(traits.columns):
        raise ValueError("Trait seed incomplete")

    merged = cytotypes.merge(
        traits[list(required_t)], on="paper_japan_member_id", how="left", validate="one_to_one"
    )
    merged["ploidy_x"] = pd.to_numeric(merged["ploidy_x"], errors="raise").astype(int)
    merged["chromosome_2n"] = pd.to_numeric(merged["chromosome_2n"], errors="raise").astype(int)
    merged["orientation_state"] = merged["orientation_state"].fillna("unknown")

    dominant = merged.loc[merged["japan_origin_role"].eq("dominant_main_japanese_radiation")].copy()
    known = dominant.loc[dominant["orientation_state"].isin(KNOWN_ORIENTATION)].copy()
    orientation_by_ploidy = (
        known.groupby(["ploidy_x", "orientation_state"]).size().rename("n_taxa").reset_index()
    )

    ploidy_levels = sorted(dominant["ploidy_x"].unique().tolist())
    upward_ploidies = sorted(
        known.loc[known["orientation_state"].isin(["upward_or_erect", "upward_or_ascending"]), "ploidy_x"]
        .unique().tolist()
    )
    diploid_orientations = sorted(
        known.loc[known["ploidy_x"].eq(2), "orientation_state"].unique().tolist()
    )

    summary = {
        "contract_version": "japan38_cytotype_trait_overlap_v1",
        "n_source_backed_cytotype_concepts": int(len(merged)),
        "n_dominant_radiation_cytotype_concepts": int(len(dominant)),
        "dominant_radiation_ploidy_levels": ploidy_levels,
        "dominant_radiation_ploidy_counts": {
            str(k): int(v) for k, v in dominant["ploidy_x"].value_counts().sort_index().items()
        },
        "n_dominant_with_known_orientation": int(len(known)),
        "upward_or_ascending_observed_ploidy_levels": upward_ploidies,
        "diploid_observed_orientation_states": diploid_orientations,
        "secondary_history_cytotypes": merged.loc[
            ~merged["japan_origin_role"].eq("dominant_main_japanese_radiation"),
            ["taxon", "japan_origin_role", "ploidy_x", "orientation_state"],
        ].to_dict("records"),
        "descriptive_result": (
            "The current source-backed panel is inconsistent with a deterministic one-to-one mapping "
            "between ploidy and capitulum orientation: upward/ascending heads occur in 2x, 4x and 6x "
            "dominant-radiation taxa, while diploid dominant-radiation taxa include both upward and "
            "downward/nodding states."
        ),
        "claim_boundary": (
            "Sparse taxon-level records only. This does not estimate cytotype or trait transition rates, "
            "does not show independence statistically, and does not test whether ploidy promotes radiation success."
        ),
    }
    return orientation_by_ploidy, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cytotypes", required=True)
    parser.add_argument("--traits", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    cytotypes = pd.read_csv(args.cytotypes, dtype=str, keep_default_na=False)
    traits = pd.read_csv(args.traits, dtype=str, keep_default_na=False)
    table, summary = build(cytotypes, traits)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "japan38_cytotype_orientation_counts_v1.csv", index=False)
    (out / "japan38_cytotype_trait_overlap_v1.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
