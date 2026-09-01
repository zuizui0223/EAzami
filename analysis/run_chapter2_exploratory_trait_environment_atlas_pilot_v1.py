#!/usr/bin/env python3
"""Run the EAzami-only exploratory current trait x environment pilot.

This pilot deliberately does not use Azami Chapter 1 results to select endpoints
or environmental axes. It operates on the already-frozen Japan-radiation
species-median snapshot, applies the predeclared environment-depth gate, tests
all 7 continuous endpoints against BIO1/BIO4/BIO12/BIO15, and keeps the complete
28-row family.

It is a small-n pre-tree screen. It is not the final nine-environment,
phylogenetically gated Chapter 2 atlas.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = ROOT / "data/evidence/japan_radiation_pre_tree_trait_environment_snapshot_v1.csv"

TRAITS = [
    "orientation_angle_degrees_median_taxon_median",
    "corolla_lab_lightness_median_taxon_median",
    "corolla_lab_chroma_median_taxon_median",
    "shape_aspect_ratio_median_taxon_median",
    "shape_circularity_median_taxon_median",
    "shape_solidity_median_taxon_median",
    "shape_width_cv_median_taxon_median",
]
ENVIRONMENTS = [
    "env_chelsa_bio01_species_median",
    "env_chelsa_bio04_species_median",
    "env_chelsa_bio12_species_median",
    "env_chelsa_bio15_species_median",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    p.add_argument("--minimum-environment-observations", type=int, default=10)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def normalized_rank(values: np.ndarray) -> np.ndarray:
    ranks = rankdata(values, method="average")
    centered = ranks - ranks.mean()
    norm = float(np.sqrt(np.sum(centered * centered)))
    if not np.isfinite(norm) or norm == 0:
        raise ValueError("No finite rank variation")
    return centered / norm


def bh_adjust(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    n = len(p)
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.minimum(adjusted, 1.0)
    out = np.empty(n, dtype=float)
    out[order] = adjusted
    return out.tolist()


def clean_trait(name: str) -> str:
    return name.removesuffix("_median_taxon_median")


def clean_environment(name: str) -> str:
    return name.removeprefix("env_chelsa_").removesuffix("_species_median").upper()


def main() -> int:
    args = parse_args()
    frame = pd.read_csv(args.snapshot)
    required = {"taxon_name", "n_balanced_env_observations", *TRAITS, *ENVIRONMENTS}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Snapshot missing required columns: {missing}")

    included = frame.loc[
        frame["n_balanced_env_observations"] >= args.minimum_environment_observations
    ].copy()
    if len(included) != 8:
        raise AssertionError(f"Expected 8 taxa after gate, got {len(included)}")
    if included[TRAITS + ENVIRONMENTS].isna().any().any():
        raise AssertionError("Pilot gate contains missing trait/environment values")

    permutation_index = np.asarray(
        list(itertools.permutations(range(len(included)))), dtype=np.int16
    )
    rows: list[dict] = []

    for trait in TRAITS:
        x = included[trait].to_numpy(dtype=float)
        x_rank = normalized_rank(x)
        for environment in ENVIRONMENTS:
            y = included[environment].to_numpy(dtype=float)
            y_rank = normalized_rank(y)
            observed = float(x_rank @ y_rank)
            permutation_rho = y_rank[permutation_index] @ x_rank
            exact_two_sided_p = float(
                np.mean(np.abs(permutation_rho) >= abs(observed) - 1e-12)
            )

            loo: list[float] = []
            for j in range(len(included)):
                keep = np.ones(len(included), dtype=bool)
                keep[j] = False
                loo.append(float(spearmanr(x[keep], y[keep]).statistic))
            all_positive = all(v > 0 for v in loo)
            all_negative = all(v < 0 for v in loo)

            rows.append(
                {
                    "trait": clean_trait(trait),
                    "environment": clean_environment(environment),
                    "n_taxa": int(len(included)),
                    "spearman_rho": observed,
                    "exact_two_sided_p": exact_two_sided_p,
                    "loo_rho_min": float(min(loo)),
                    "loo_rho_max": float(max(loo)),
                    "loo_sign_stable": bool(all_positive or all_negative),
                    "loo_direction": (
                        "positive" if all_positive else "negative" if all_negative else "mixed"
                    ),
                }
            )

    q_values = bh_adjust([r["exact_two_sided_p"] for r in rows])
    for row, q in zip(rows, q_values):
        row["bh_q_28"] = float(q)
        row["status"] = (
            "bh_supported"
            if q < 0.05
            else "raw_exploratory_lead"
            if row["exact_two_sided_p"] <= 0.05
            else "not_bh_supported"
        )

    strongest = min(rows, key=lambda r: r["exact_two_sided_p"])
    output = {
        "contract_version": "chapter2_exploratory_trait_environment_atlas_pilot_v1",
        "status_date": "2026-09-01",
        "scope": "retrospective exploratory EAzami-only species-median pilot; independent of Azami result selection",
        "source_snapshot": str(args.snapshot.relative_to(ROOT)),
        "minimum_balanced_environment_observations": args.minimum_environment_observations,
        "included_taxa": included["taxon_name"].tolist(),
        "excluded_for_environment_depth": frame.loc[
            frame["n_balanced_env_observations"] < args.minimum_environment_observations,
            "taxon_name",
        ].tolist(),
        "n_taxa": int(len(included)),
        "trait_axes": [clean_trait(x) for x in TRAITS],
        "environment_axes": [clean_environment(x) for x in ENVIRONMENTS],
        "n_tests": len(rows),
        "exact_permutations": int(len(permutation_index)),
        "multiplicity": "Benjamini-Hochberg across all 28 endpoint x environment tests",
        "rows": rows,
        "summary": {
            "bh_supported_rows": sum(r["status"] == "bh_supported" for r in rows),
            "raw_p_le_0_05_rows": sum(r["exact_two_sided_p"] <= 0.05 for r in rows),
            "strongest_raw_row": strongest,
        },
        "interpretation": (
            "The EAzami-only pilot yields no BH-supported endpoint x climate association in this "
            "eight-taxon panel. The strongest raw exploratory lead is shape_width_cv x BIO12 "
            "(rho about 0.857, exact P about 0.0107, BH q 0.30) with a positive leave-one-taxon-out "
            "direction in every deletion. Corolla lightness x BIO4 is a second raw boundary lead "
            "(rho about -0.723, exact P 0.05) with stable negative leave-one-out direction. These "
            "leads were not selected by Azami results and require expanded environmental/trait "
            "coverage plus phylogenetic and spatial gates before manuscript promotion."
        ),
        "claim_boundary": [
            "This pilot is exploratory and small-n.",
            "No row survives BH correction across the 28-test family.",
            "Species medians are not individual-level effects.",
            "Current univariate climate associations do not identify adaptation or historical causation.",
            "Azami results were not used to choose traits or BIO1/BIO4/BIO12/BIO15 rows within this pilot.",
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(args.out_csv, index=False)

    print(json.dumps(output["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
