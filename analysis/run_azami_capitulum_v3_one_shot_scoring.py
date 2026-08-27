#!/usr/bin/env python3
"""Run the preregistered one-shot comparison of 14 Azami-compatible v3 families.

The scoring rules live in data/evidence/azami_capitulum_v3_scoring_contract_v1.json
and were frozen before any v3 target distance or ranking was computed.  This
script does not tune generator priors or score weights.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from compute_azami_capitulum_v3_estimands import compute
from simulate_azami_capitulum_v3_conditional import FAMILY_AXES, generate


TARGET_CLASSES = [
    "structure",
    "environment_block_r2",
    "environment_geometry",
    "environment_incremental",
]


def load_observed(space_path: Path, environment_path: Path, incremental_path: Path) -> pd.DataFrame:
    space = pd.read_csv(space_path, low_memory=False).copy()
    space["target_class"] = "structure"

    environment = pd.read_csv(environment_path, low_memory=False).copy()
    environment["target_class"] = np.where(
        environment["target_id"].astype(str).str.startswith("environment_block_r2:"),
        "environment_block_r2",
        "environment_geometry",
    )
    environment["ci95_low"] = np.nan
    environment["ci95_high"] = np.nan

    incremental = pd.read_csv(incremental_path, low_memory=False).copy()
    incremental["value"] = pd.to_numeric(incremental["partial_r2"], errors="raise")
    incremental["target_class"] = "environment_incremental"
    incremental["ci95_low"] = np.nan
    incremental["ci95_high"] = np.nan

    keep = ["target_id", "scope", "scale", "value", "ci95_low", "ci95_high", "target_class"]
    observed = pd.concat([space[keep], environment[keep], incremental[keep]], ignore_index=True)
    observed["value"] = pd.to_numeric(observed["value"], errors="raise")
    if len(observed) != 62:
        raise ValueError(f"expected 62 observed targets, found {len(observed)}")
    if observed.duplicated(["target_id", "scope", "scale"]).any():
        raise ValueError("observed target keys are not unique")
    if set(observed["target_class"]) != set(TARGET_CLASSES):
        raise ValueError("observed target classes do not match frozen scoring classes")
    return observed


def row_loss(target_class: str, model: float, observed: float, low: float, high: float, scoring: dict) -> float:
    spec = scoring["row_loss"][target_class]
    if target_class == "structure":
        half_width = abs(float(high) - float(low)) / 2.0
        scale = max(half_width, 0.05)
        return ((float(model) - float(observed)) / scale) ** 2
    if target_class in {"environment_block_r2", "environment_incremental"}:
        scale = float(spec["scale"])
        mt = np.sqrt(max(float(model), 0.0))
        ot = np.sqrt(max(float(observed), 0.0))
        return ((mt - ot) / scale) ** 2
    if target_class == "environment_geometry":
        scale = float(spec["scale"])
        return ((float(model) - float(observed)) / scale) ** 2
    raise ValueError(target_class)


def channel_scope_mask(frame: pd.DataFrame, channel: dict) -> pd.Series:
    trait_scope = channel["trait_scope"]
    environment_scope = channel["environment_scope"]
    return (
        (frame["target_class"].eq("structure") & frame["scope"].eq(trait_scope))
        | (~frame["target_class"].eq("structure") & frame["scope"].eq(environment_scope))
    )


def score_estimands(model: pd.DataFrame, observed: pd.DataFrame, scoring: dict, channel_name: str) -> dict:
    channel = scoring["score_channels"][channel_name]
    merged = observed.merge(
        model[["target_id", "scope", "scale", "value"]].rename(columns={"value": "model_value"}),
        on=["target_id", "scope", "scale"],
        how="left",
        validate="one_to_one",
    )
    if merged["model_value"].isna().any():
        missing = merged.loc[merged["model_value"].isna(), ["target_id", "scope", "scale"]]
        raise ValueError(f"model missing exact target keys: {missing.to_dict('records')}")
    use = merged[channel_scope_mask(merged, channel)].copy()
    if len(use) != 31:
        raise ValueError(f"{channel_name} must contain exactly 31 target rows; found {len(use)}")
    use["row_loss"] = [
        row_loss(r.target_class, r.model_value, r.value, r.ci95_low, r.ci95_high, scoring)
        for r in use.itertuples(index=False)
    ]
    class_means = use.groupby("target_class")["row_loss"].mean().to_dict()
    if set(class_means) != set(TARGET_CLASSES):
        raise ValueError("score channel does not contain all four target classes")
    total = float(np.mean([class_means[x] for x in TARGET_CLASSES]))
    return {
        "total": total,
        **{f"loss_{x}": float(class_means[x]) for x in TARGET_CLASSES},
    }


def add_draw_ranks(draw_scores: pd.DataFrame) -> pd.DataFrame:
    out = draw_scores.copy()
    out["rank"] = out.groupby(["channel", "seed"])["total"].rank(method="min", ascending=True)
    return out


def family_summary(draw_scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (channel, family), g in draw_scores.groupby(["channel", "family"], sort=True):
        values = g["total"].to_numpy(float)
        ranks = g["rank"].to_numpy(float)
        row = {
            "channel": channel,
            "family": family,
            "environment_mode": FAMILY_AXES[family][0],
            "scale_coefficient_architecture": FAMILY_AXES[family][1],
            "residual_architecture": FAMILY_AXES[family][2],
            "median": float(np.median(values)),
            "q25": float(np.quantile(values, 0.25)),
            "q75": float(np.quantile(values, 0.75)),
            "min": float(values.min()),
            "max": float(values.max()),
            "median_rank": float(np.median(ranks)),
            "mean_rank": float(np.mean(ranks)),
            "rank1_count": int(np.sum(ranks == 1)),
        }
        for klass in TARGET_CLASSES:
            row[f"median_loss_{klass}"] = float(np.median(g[f"loss_{klass}"].to_numpy(float)))
        rows.append(row)
    result = pd.DataFrame(rows)
    result["median_order_rank"] = result.groupby("channel")["median"].rank(method="min", ascending=True)
    return result.sort_values(["channel", "median", "family"]).reset_index(drop=True)


def pairwise_wins(draw_scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    families = sorted(draw_scores["family"].unique())
    for channel in sorted(draw_scores["channel"].unique()):
        wide = draw_scores[draw_scores["channel"].eq(channel)].pivot(index="seed", columns="family", values="total")
        for a in families:
            for b in families:
                if a == b:
                    continue
                delta = wide[a].to_numpy(float) - wide[b].to_numpy(float)
                wins = float((np.sum(delta < -1e-15) + 0.5 * np.sum(np.abs(delta) <= 1e-15)) / len(delta))
                rows.append({"channel": channel, "family_a": a, "family_b": b, "a_lower_score_fraction": wins})
    return pd.DataFrame(rows)


def _family(environment_mode: str, scale_arch: str, residual: str) -> str:
    if environment_mode == "NONE":
        return f"NULL_{residual}"
    prefix = {
        "CORE4": "CORE4",
        "PROCESS_BOTH": "PROCESS_BOTH",
        "PROCESS_AMONG_ONLY": "PROCESS_AMONG_ONLY",
    }[environment_mode]
    return f"{prefix}_{scale_arch}_{residual}"


def factor_contrasts(draw_scores: pd.DataFrame, scoring: dict) -> pd.DataFrame:
    pair_specs: list[tuple[str, str, str]] = []
    for env_mode, scale_arch in [
        ("NONE", "SHARED"),
        ("CORE4", "SHARED"), ("CORE4", "INDEPENDENT"),
        ("PROCESS_BOTH", "SHARED"), ("PROCESS_BOTH", "INDEPENDENT"),
        ("PROCESS_AMONG_ONLY", "SHARED"), ("PROCESS_AMONG_ONLY", "INDEPENDENT"),
    ]:
        pair_specs.append((
            "residual_architecture",
            _family(env_mode, scale_arch, "COUPLED"),
            _family(env_mode, scale_arch, "MODULAR"),
        ))
    for env_mode in ["CORE4", "PROCESS_BOTH", "PROCESS_AMONG_ONLY"]:
        for residual in ["COUPLED", "MODULAR"]:
            pair_specs.append((
                "scale_coefficient_architecture",
                _family(env_mode, "SHARED", residual),
                _family(env_mode, "INDEPENDENT", residual),
            ))
    for scale_arch in ["SHARED", "INDEPENDENT"]:
        for residual in ["COUPLED", "MODULAR"]:
            pair_specs += [
                ("process_both_vs_core4", _family("CORE4", scale_arch, residual), _family("PROCESS_BOTH", scale_arch, residual)),
                ("process_among_only_vs_core4", _family("CORE4", scale_arch, residual), _family("PROCESS_AMONG_ONLY", scale_arch, residual)),
                ("process_among_only_vs_process_both", _family("PROCESS_BOTH", scale_arch, residual), _family("PROCESS_AMONG_ONLY", scale_arch, residual)),
            ]

    rows = []
    for channel in sorted(draw_scores["channel"].unique()):
        wide = draw_scores[draw_scores["channel"].eq(channel)].pivot(index="seed", columns="family", values="total")
        by_name: dict[str, list[float]] = {}
        for name, baseline, alternative in pair_specs:
            values = (wide[baseline] - wide[alternative]).to_numpy(float)
            by_name.setdefault(name, []).extend(values.tolist())
        for name, values0 in by_name.items():
            values = np.asarray(values0, float)
            positive_fraction = float(np.mean(values > 0))
            rows.append({
                "channel": channel,
                "contrast": name,
                "n_paired_contrasts": len(values),
                "median_baseline_minus_alternative": float(np.median(values)),
                "q25": float(np.quantile(values, 0.25)),
                "q75": float(np.quantile(values, 0.75)),
                "positive_fraction": positive_fraction,
                "direction_consistent": bool(positive_fraction >= 0.75),
            })
    return pd.DataFrame(rows).sort_values(["channel", "contrast"]).reset_index(drop=True)


def decision(summary: pd.DataFrame, wins: pd.DataFrame, scoring: dict) -> dict:
    primary = summary[summary["channel"].eq("primary")].sort_values(["median", "family"]).reset_index(drop=True)
    sensitivity = summary[summary["channel"].eq("replication_sensitivity")].sort_values(["median", "family"]).reset_index(drop=True)
    leader = primary.iloc[0]
    leader_median = float(leader["median"])
    tie_tolerance = max(0.05 * leader_median, 0.01)
    tie_set = primary.loc[primary["median"] <= leader_median + tie_tolerance, "family"].tolist()
    leader_family = str(leader["family"])

    w = wins[(wins["channel"].eq("primary")) & wins["family_a"].eq(leader_family)]
    min_pairwise_win = float(w["a_lower_score_fraction"].min())
    sens_row = sensitivity[sensitivity["family"].eq(leader_family)].iloc[0]
    sens_best = float(sensitivity.iloc[0]["median"])
    sens_rank = int(sens_row["median_order_rank"])
    sens_within_10 = bool(float(sens_row["median"]) <= 1.10 * sens_best + 1e-15)

    robust = bool(
        len(tie_set) == 1
        and min_pairwise_win >= 0.75
        and sens_rank <= 2
        and sens_within_10
    )
    return {
        "status": "robust_leader" if robust else "no_robust_leader",
        "primary_median_leader": leader_family,
        "primary_leader_median": leader_median,
        "primary_tie_tolerance": tie_tolerance,
        "primary_tie_set": tie_set,
        "primary_min_pairwise_win_fraction": min_pairwise_win,
        "replication_sensitivity_best": str(sensitivity.iloc[0]["family"]),
        "leader_replication_sensitivity_median_rank": sens_rank,
        "leader_replication_sensitivity_within_10_percent_of_best": sens_within_10,
        "robust_leader": leader_family if robust else None,
        "no_retuning_rule": scoring["robust_leader_rule"]["failure_interpretation"],
        "claim_boundary": scoring["claim_boundary"],
    }


def run(
    design: pd.DataFrame,
    generator_contract: dict,
    estimand_contract: dict,
    scoring_contract: dict,
    observed: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    expected_families = generator_contract["model_families"]
    if set(expected_families) != set(FAMILY_AXES):
        raise ValueError("generator contract/model implementation family mismatch")
    seeds = [int(x) for x in scoring_contract["one_shot_draws"]["seeds"]]
    if len(seeds) != int(scoring_contract["one_shot_draws"]["paired_draw_count"]):
        raise ValueError("paired draw count does not match frozen seed list")

    rows = []
    for seed in seeds:
        for family in expected_families:
            observations = generate(design, family, seed, generator_contract, strict_frozen_design=True)
            estimands = compute(observations, estimand_contract)
            for channel in scoring_contract["score_channels"]:
                score = score_estimands(estimands, observed, scoring_contract, channel)
                rows.append({"seed": seed, "family": family, "channel": channel, **score})
    draw_scores = add_draw_ranks(pd.DataFrame(rows))
    expected_rows = len(seeds) * len(expected_families) * len(scoring_contract["score_channels"])
    if len(draw_scores) != expected_rows:
        raise RuntimeError(f"expected {expected_rows} draw-score rows; got {len(draw_scores)}")
    summary = family_summary(draw_scores)
    wins = pairwise_wins(draw_scores)
    factors = factor_contrasts(draw_scores, scoring_contract)
    final = decision(summary, wins, scoring_contract)
    final["paired_draw_count"] = len(seeds)
    final["model_family_count"] = len(expected_families)
    final["observed_target_count"] = len(observed)
    return draw_scores, summary, wins, factors, final


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--design", required=True, type=Path)
    p.add_argument("--space-targets", required=True, type=Path)
    p.add_argument("--environment-targets", required=True, type=Path)
    p.add_argument("--incremental-targets", required=True, type=Path)
    p.add_argument("--generator-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_generator_contract_v1.json"))
    p.add_argument("--estimand-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_estimand_contract_v1.json"))
    p.add_argument("--scoring-contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_scoring_contract_v1.json"))
    p.add_argument("--out-dir", required=True, type=Path)
    args = p.parse_args()

    generator_contract = json.loads(args.generator_contract.read_text(encoding="utf-8"))
    estimand_contract = json.loads(args.estimand_contract.read_text(encoding="utf-8"))
    scoring_contract = json.loads(args.scoring_contract.read_text(encoding="utf-8"))
    if scoring_contract["status"] != "frozen_before_any_v3_target_distance_or_ranking":
        raise ValueError("scoring contract is not in the frozen preregistered state")
    design = pd.read_csv(args.design, low_memory=False)
    observed = load_observed(args.space_targets, args.environment_targets, args.incremental_targets)
    draw_scores, summary, wins, factors, final = run(
        design, generator_contract, estimand_contract, scoring_contract, observed
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    draw_scores.to_csv(args.out_dir / "azami_capitulum_v3_one_shot_draw_scores_v1.csv", index=False)
    summary.to_csv(args.out_dir / "azami_capitulum_v3_one_shot_family_summary_v1.csv", index=False)
    wins.to_csv(args.out_dir / "azami_capitulum_v3_one_shot_pairwise_wins_v1.csv", index=False)
    factors.to_csv(args.out_dir / "azami_capitulum_v3_one_shot_factor_contrasts_v1.csv", index=False)
    (args.out_dir / "azami_capitulum_v3_one_shot_decision_v1.json").write_text(
        json.dumps(final, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(final, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
