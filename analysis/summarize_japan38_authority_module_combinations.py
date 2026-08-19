#!/usr/bin/env python3
"""Summarize source-backed capitulum module combinations before the nuclear tree.

This is a descriptive state-combination audit. It does not count transitions or
infer correlated evolution because branch structure is deliberately absent.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


SECONDARY_IDS = {"JPN_06": "dipsacolepis_secondary_candidate", "JPN_15": "lineare_replicated_exception"}
UNKNOWN = {"unknown", "source_conflict_index_downward_detail_erect"}


def build(seed: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {
        "paper_japan_member_id", "paper_taxon_concept", "orientation_state",
        "phyllary_posture", "stickiness_state"
    }
    if required.difference(seed.columns):
        raise ValueError("Authority seed incomplete")
    if seed["paper_japan_member_id"].duplicated().any():
        raise ValueError("Duplicate paper concept")

    frame = seed.copy()
    frame["origin_role"] = frame["paper_japan_member_id"].map(SECONDARY_IDS).fillna("dominant_main_japanese_radiation")
    frame["orientation_known"] = ~frame["orientation_state"].isin(UNKNOWN)
    frame["phyllary_known"] = ~frame["phyllary_posture"].eq("unknown")
    frame["stickiness_known"] = ~frame["stickiness_state"].eq("unknown")

    dominant = frame.loc[frame["origin_role"].eq("dominant_main_japanese_radiation")]
    secondary = frame.loc[~frame["origin_role"].eq("dominant_main_japanese_radiation")]

    def counts(part: pd.DataFrame, column: str, known_col: str) -> dict[str, int]:
        return {
            str(k): int(v)
            for k, v in part.loc[part[known_col], column].value_counts().sort_index().items()
        }

    complete_os = frame.loc[frame["orientation_known"] & frame["stickiness_known"]].copy()
    complete_os["orientation_stickiness_combination"] = (
        complete_os["orientation_state"] + " + " + complete_os["stickiness_state"]
    )
    combo_counts = (
        complete_os.groupby(["origin_role", "orientation_stickiness_combination"])
        .size().rename("n_taxa").reset_index()
    )

    dominant_complete = complete_os.loc[complete_os["origin_role"].eq("dominant_main_japanese_radiation")]
    secondary_complete = complete_os.loc[~complete_os["origin_role"].eq("dominant_main_japanese_radiation")]

    summary = {
        "contract_version": "japan38_authority_module_combinations_v1",
        "n_authority_seed_concepts": int(len(frame)),
        "n_dominant_seed_concepts": int(len(dominant)),
        "n_secondary_seed_concepts": int(len(secondary)),
        "dominant_orientation_counts": counts(dominant, "orientation_state", "orientation_known"),
        "dominant_phyllary_counts": counts(dominant, "phyllary_posture", "phyllary_known"),
        "dominant_stickiness_counts": counts(dominant, "stickiness_state", "stickiness_known"),
        "secondary_orientation_counts": counts(secondary, "orientation_state", "orientation_known"),
        "secondary_phyllary_counts": counts(secondary, "phyllary_posture", "phyllary_known"),
        "secondary_stickiness_counts": counts(secondary, "stickiness_state", "stickiness_known"),
        "dominant_orientation_stickiness_combinations": sorted(
            dominant_complete["orientation_stickiness_combination"].unique().tolist()
        ),
        "secondary_orientation_stickiness_combinations": sorted(
            secondary_complete["orientation_stickiness_combination"].unique().tolist()
        ),
        "n_dominant_orientation_stickiness_combinations": int(
            dominant_complete["orientation_stickiness_combination"].nunique()
        ),
        "n_secondary_orientation_stickiness_combinations": int(
            secondary_complete["orientation_stickiness_combination"].nunique()
        ),
        "descriptive_result": (
            "The current authority-backed dominant-radiation sample contains both upward/erect and "
            "downward/nodding orientation states and both sticky and non-sticky involucres. The two "
            "secondary-history comparators are both upward/erect but differ in stickiness. Thus origin "
            "history does not map to one observed capitulum-state combination in this source-backed sample."
        ),
        "claim_boundary": (
            "State diversity only. Without the accepted tree and complete taxon coverage, this does not "
            "estimate transition counts, correlated evolution, convergence, selection or adaptation."
        ),
    }
    return combo_counts, summary


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--seed", required=True)
    p.add_argument("--out-dir", required=True)
    args=p.parse_args()
    seed=pd.read_csv(args.seed, dtype=str, keep_default_na=False)
    table, summary=build(seed)
    out=Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out/"japan38_orientation_stickiness_combinations_v1.csv", index=False)
    (out/"japan38_authority_module_combinations_v1.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
