#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--origin", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    return p.parse_args()


def summary(values: np.ndarray) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    return {
        "min": float(np.min(x)),
        "q05": float(np.quantile(x, 0.05)),
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "max": float(np.max(x)),
    }


def main() -> int:
    args = parse_args()
    origin = json.loads(args.origin.read_text(encoding="utf-8"))
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    rows = pd.DataFrame(origin["scenario_rows"])
    regions = contract["input"]["expected_regions"]
    n_pairs = int(contract["input"]["expected_chronology_pairs"])
    expected_rows = int(contract["input"]["expected_region_by_chronology_rows"])
    if len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} scenario rows, got {len(rows)}")
    if set(rows["region"].astype(str)) != set(regions):
        raise ValueError("Region set differs from frozen contract")
    key = ["young_ma", "old_ma"]
    groups = list(rows.groupby(key, sort=True))
    if len(groups) != n_pairs:
        raise ValueError(f"Expected {n_pairs} chronology groups, got {len(groups)}")
    for pair, part in groups:
        if len(part) != len(regions) or set(part["region"].astype(str)) != set(regions):
            raise ValueError(f"Incomplete chronology pair {pair}")

    work = rows[[*key, "region", "cosine_similarity", "cosine_null_percentile"]].copy()
    work["cosine_similarity"] = pd.to_numeric(work["cosine_similarity"], errors="raise")
    work["cosine_null_percentile"] = pd.to_numeric(work["cosine_null_percentile"], errors="raise")
    work["rank_cosine_desc"] = work.groupby(key)["cosine_similarity"].rank(method="average", ascending=False)

    rank_payload: dict[str, Any] = {}
    for region in regions:
        sub = work[work["region"].eq(region)].copy()
        ranks = sub["rank_cosine_desc"].to_numpy(float)
        rank_payload[region] = {
            "n_chronology_scenarios": int(len(sub)),
            "rank1_fraction": float(np.mean(ranks == 1.0)),
            "rank1_count": int(np.sum(ranks == 1.0)),
            "mean_rank": float(np.mean(ranks)),
            "median_rank": float(np.median(ranks)),
            "rank_quantiles": summary(ranks),
            "cosine_quantiles": summary(sub["cosine_similarity"].to_numpy(float)),
        }

    pivot = work.pivot(index=key, columns="region", values="cosine_similarity").sort_index()
    pair_rows: list[dict[str, Any]] = []
    pair_payload: dict[str, Any] = {}
    for a, b in itertools.combinations(regions, 2):
        delta = (pivot[a] - pivot[b]).to_numpy(float)
        name = f"{a}_minus_{b}"
        payload = {
            "region_a": a,
            "region_b": b,
            "n_chronology_scenarios": int(len(delta)),
            "fraction_a_gt_b": float(np.mean(delta > 0)),
            "fraction_a_eq_b": float(np.mean(delta == 0)),
            "fraction_a_lt_b": float(np.mean(delta < 0)),
            "difference_quantiles": summary(delta),
        }
        pair_payload[name] = payload
        for (young, old), value in zip(pivot.index.tolist(), delta):
            pair_rows.append({
                "young_ma": young,
                "old_ma": old,
                "region_a": a,
                "region_b": b,
                "cosine_difference_a_minus_b": float(value),
                "a_gt_b": bool(value > 0),
            })

    beats: dict[str, dict[str, float]] = {r: {} for r in regions}
    for a in regions:
        for b in regions:
            if a == b:
                continue
            delta = (pivot[a] - pivot[b]).to_numpy(float)
            beats[a][b] = float(np.mean(delta > 0))

    dominant = []
    for region in regions:
        rank1 = rank_payload[region]["rank1_fraction"]
        all_pair = all(beats[region][other] >= 0.75 for other in regions if other != region)
        if rank1 >= 0.75 and all_pair:
            dominant.append(region)

    if len(dominant) == 1:
        classification = "scenario_dominant_region"
        leading_region = dominant[0]
    else:
        majority_winners = [
            r for r in regions
            if all(beats[r][other] > 0.5 for other in regions if other != r)
        ]
        if majority_winners:
            classification = "relative_ordering_present_but_not_dominant"
            leading_region = min(
                majority_winners,
                key=lambda r: (rank_payload[r]["mean_rank"], -rank_payload[r]["rank1_fraction"]),
            )
        else:
            classification = "no_stable_regional_ordering"
            leading_region = min(regions, key=lambda r: rank_payload[r]["mean_rank"])

    scenario_rank_rows = work.sort_values([*key, "rank_cosine_desc", "region"]).to_dict(orient="records")
    result = {
        "contract_version": "chapter2_orientation_origin_region_ranking_result_v1",
        "source_origin_contract_version": origin.get("contract_version"),
        "n_chronology_scenarios": n_pairs,
        "n_region_by_chronology_rows": int(len(work)),
        "classification": classification,
        "leading_region_descriptive": leading_region,
        "scenario_dominant_regions": dominant,
        "region_rank_summary": rank_payload,
        "pairwise_ordering": pair_payload,
        "pairwise_win_fraction_matrix": beats,
        "frozen_origin_trajectory_classification": origin["cross_scenario_summary"]["classification"],
        "interpretation": (
            "This exposes scenario-wise regional ordering inside the already-frozen chronology x paleolocation envelope. "
            "It does not convert the envelope to posterior support and does not alter the origin-trajectory unresolved classification."
        ),
        "claim_boundary": contract["claim_boundary"],
    }

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "chapter2_orientation_origin_region_ranking_result_v1.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    pd.DataFrame(scenario_rank_rows).to_csv(
        out / "chapter2_orientation_origin_region_scenario_ranks_v1.csv", index=False
    )
    pd.DataFrame(pair_rows).to_csv(
        out / "chapter2_orientation_origin_region_pairwise_differences_v1.csv", index=False
    )
    print(json.dumps({
        "classification": classification,
        "leading_region_descriptive": leading_region,
        "rank1": {r: rank_payload[r]["rank1_fraction"] for r in regions},
        "pairwise_win_fraction_matrix": beats,
        "frozen_origin_trajectory_classification": origin["cross_scenario_summary"]["classification"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
