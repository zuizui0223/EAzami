#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

SYSTEMS = {
    "ARENICOLA_BREVICAULE_IRUMTIENSE": ("Cirsium brevicaule", "Cirsium irumtiense"),
    "TAIWAN_KAWAKAMII_TATAKAENSE": ("Cirsium kawakamii", "Cirsium tatakaense"),
}
SEED = 20260901
BOOTSTRAPS = 10000
PERMUTATIONS = 9999
CELL_DEGREES = 0.05


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--cohort", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    return p.parse_args()


def finite_array(series: pd.Series) -> np.ndarray:
    return pd.to_numeric(series, errors="coerce").dropna().to_numpy(float)


def median_diff_with_bootstrap(
    white: np.ndarray,
    coloured: np.ndarray,
    rng: np.random.Generator,
    n_boot: int = BOOTSTRAPS,
) -> dict[str, float | int | list[float]]:
    white = white[np.isfinite(white)]
    coloured = coloured[np.isfinite(coloured)]
    if len(white) == 0 or len(coloured) == 0:
        return {
            "n_white": int(len(white)),
            "n_coloured": int(len(coloured)),
            "median_white": float("nan"),
            "median_coloured": float("nan"),
            "difference_white_minus_coloured": float("nan"),
            "bootstrap_95": [float("nan"), float("nan")],
        }
    observed = float(np.median(white) - np.median(coloured))
    simulated = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        simulated[i] = float(
            np.median(rng.choice(white, size=len(white), replace=True))
            - np.median(rng.choice(coloured, size=len(coloured), replace=True))
        )
    return {
        "n_white": int(len(white)),
        "n_coloured": int(len(coloured)),
        "median_white": float(np.median(white)),
        "median_coloured": float(np.median(coloured)),
        "difference_white_minus_coloured": observed,
        "bootstrap_95": [float(np.quantile(simulated, 0.025)), float(np.quantile(simulated, 0.975))],
    }


def spatial_cell(frame: pd.DataFrame, degrees: float = CELL_DEGREES) -> pd.Series:
    lat = pd.to_numeric(frame["latitude"], errors="coerce").to_numpy(float)
    lon = pd.to_numeric(frame["longitude"], errors="coerce").to_numpy(float)
    ilat = np.floor((lat + 90.0) / degrees).astype(int)
    ilon = np.floor((lon + 180.0) / degrees).astype(int)
    return pd.Series([f"{a}:{b}" for a, b in zip(ilat, ilon)], index=frame.index)


def cell_medians(frame: pd.DataFrame, value_column: str, usable_colour_only: bool) -> pd.DataFrame:
    work = frame.copy()
    if usable_colour_only:
        work = work[work["colour_status"].eq("usable")].copy()
    work[value_column] = pd.to_numeric(work[value_column], errors="coerce")
    work = work[work[value_column].notna()].copy()
    if work.empty:
        return pd.DataFrame(columns=["taxon_name", "cell_id", value_column])
    work["cell_id"] = spatial_cell(work)
    return (
        work.groupby(["taxon_name", "cell_id"], as_index=False)[value_column]
        .median()
        .sort_values(["taxon_name", "cell_id"])
        .reset_index(drop=True)
    )


def standardized_within_taxon_slope(frame: pd.DataFrame, rng: np.random.Generator) -> dict[str, float | int]:
    work = frame[
        frame["colour_status"].eq("usable")
        & pd.to_numeric(frame["corolla_lab_chroma"], errors="coerce").notna()
        & pd.to_numeric(frame["chelsa_rsds_mean"], errors="coerce").notna()
    ].copy()
    work["corolla_lab_chroma"] = pd.to_numeric(work["corolla_lab_chroma"], errors="coerce")
    work["chelsa_rsds_mean"] = pd.to_numeric(work["chelsa_rsds_mean"], errors="coerce")
    if len(work) < 4 or work["taxon_name"].nunique() < 2:
        return {
            "n_observations": int(len(work)),
            "n_taxa": int(work["taxon_name"].nunique()),
            "beta_std": float("nan"),
            "permutation_p_two_sided": float("nan"),
            "permutation_p_expected_negative": float("nan"),
        }

    y = (work["corolla_lab_chroma"] - work.groupby("taxon_name")["corolla_lab_chroma"].transform("mean")).to_numpy(float)
    x = (work["chelsa_rsds_mean"] - work.groupby("taxon_name")["chelsa_rsds_mean"].transform("mean")).to_numpy(float)
    sx = float(np.std(x, ddof=0))
    sy = float(np.std(y, ddof=0))
    if not math.isfinite(sx) or not math.isfinite(sy) or sx <= 0 or sy <= 0:
        return {
            "n_observations": int(len(work)),
            "n_taxa": int(work["taxon_name"].nunique()),
            "beta_std": float("nan"),
            "permutation_p_two_sided": float("nan"),
            "permutation_p_expected_negative": float("nan"),
        }
    x = x / sx
    y = y / sy
    denominator = float(np.dot(x, x))
    observed = float(np.dot(x, y) / denominator)
    taxa = work["taxon_name"].astype(str).to_numpy()
    groups = [np.flatnonzero(taxa == taxon) for taxon in np.unique(taxa)]
    exceed_abs = 0
    expected_negative = 0
    for _ in range(PERMUTATIONS):
        perm = x.copy()
        for idx in groups:
            perm[idx] = rng.permutation(perm[idx])
        simulated = float(np.dot(perm, y) / denominator)
        if abs(simulated) >= abs(observed) - 1e-15:
            exceed_abs += 1
        if simulated <= observed + 1e-15:
            expected_negative += 1
    return {
        "n_observations": int(len(work)),
        "n_taxa": int(work["taxon_name"].nunique()),
        "beta_std": observed,
        "permutation_p_two_sided": float((exceed_abs + 1) / (PERMUTATIONS + 1)),
        "permutation_p_expected_negative": float((expected_negative + 1) / (PERMUTATIONS + 1)),
    }


def main() -> int:
    args = parse_args()
    cohort = pd.read_csv(args.cohort, dtype={"obs_id": str}, low_memory=False)
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    required = {
        "obs_id", "taxon_name", "system_id", "pair_role", "latitude", "longitude",
        "colour_status", "corolla_lab_chroma", "chelsa_rsds_mean",
    }
    missing = sorted(required.difference(cohort.columns))
    if missing:
        raise ValueError(f"cohort missing columns: {missing}")
    if cohort["obs_id"].duplicated().any():
        raise ValueError("cohort obs_id must be unique")
    if len(cohort) != int(contract["input_cohort"]["n_observations"]):
        raise ValueError("cohort row count differs from frozen contract")
    if set(cohort["system_id"]) != set(SYSTEMS):
        raise ValueError("unexpected sister-system set")
    rsds = pd.to_numeric(cohort["chelsa_rsds_mean"], errors="coerce")
    if float(rsds.notna().mean()) < float(contract["environment_source"]["minimum_coverage"]):
        raise RuntimeError("RSDS coverage below frozen threshold")

    rng = np.random.default_rng(SEED)
    rows: list[dict[str, object]] = []
    system_payload: dict[str, object] = {}
    concordant_count = 0
    cell_concordant_count = 0

    rsds_cells = cell_medians(cohort, "chelsa_rsds_mean", usable_colour_only=False)
    chroma_cells = cell_medians(cohort, "corolla_lab_chroma", usable_colour_only=True)

    for system_id, (white_taxon, coloured_taxon) in SYSTEMS.items():
        part = cohort[cohort["system_id"].eq(system_id)].copy()
        if set(part["taxon_name"]) != {white_taxon, coloured_taxon}:
            raise ValueError(f"taxa do not match frozen system {system_id}")

        white_all = part[part["taxon_name"].eq(white_taxon)]
        coloured_all = part[part["taxon_name"].eq(coloured_taxon)]
        rsds_stats = median_diff_with_bootstrap(
            finite_array(white_all["chelsa_rsds_mean"]),
            finite_array(coloured_all["chelsa_rsds_mean"]),
            rng,
        )
        white_colour = white_all[white_all["colour_status"].eq("usable")]
        coloured_colour = coloured_all[coloured_all["colour_status"].eq("usable")]
        chroma_stats = median_diff_with_bootstrap(
            finite_array(white_colour["corolla_lab_chroma"]),
            finite_array(coloured_colour["corolla_lab_chroma"]),
            rng,
        )
        delta_rsds = float(rsds_stats["difference_white_minus_coloured"])
        delta_chroma = float(chroma_stats["difference_white_minus_coloured"])
        concordant = bool(delta_rsds > 0 and delta_chroma < 0)
        concordant_count += int(concordant)

        sys_rsds_cells = rsds_cells[rsds_cells["taxon_name"].isin([white_taxon, coloured_taxon])]
        sys_chroma_cells = chroma_cells[chroma_cells["taxon_name"].isin([white_taxon, coloured_taxon])]
        cell_rsds = median_diff_with_bootstrap(
            finite_array(sys_rsds_cells.loc[sys_rsds_cells["taxon_name"].eq(white_taxon), "chelsa_rsds_mean"]),
            finite_array(sys_rsds_cells.loc[sys_rsds_cells["taxon_name"].eq(coloured_taxon), "chelsa_rsds_mean"]),
            rng,
        )
        cell_chroma = median_diff_with_bootstrap(
            finite_array(sys_chroma_cells.loc[sys_chroma_cells["taxon_name"].eq(white_taxon), "corolla_lab_chroma"]),
            finite_array(sys_chroma_cells.loc[sys_chroma_cells["taxon_name"].eq(coloured_taxon), "corolla_lab_chroma"]),
            rng,
        )
        cell_concordant = bool(
            float(cell_rsds["difference_white_minus_coloured"]) > 0
            and float(cell_chroma["difference_white_minus_coloured"]) < 0
        )
        cell_concordant_count += int(cell_concordant)
        within = standardized_within_taxon_slope(part, rng)

        system_payload[system_id] = {
            "white_taxon": white_taxon,
            "coloured_taxon": coloured_taxon,
            "observation_level": {
                "rsds": rsds_stats,
                "chroma": chroma_stats,
                "azami_direction_concordant": concordant,
            },
            "spatial_0_05_degree_cell_sensitivity": {
                "rsds": cell_rsds,
                "chroma": cell_chroma,
                "azami_direction_concordant": cell_concordant,
            },
            "within_taxon_secondary": within,
        }
        rows.append({
            "system_id": system_id,
            "white_taxon": white_taxon,
            "coloured_taxon": coloured_taxon,
            "n_white_coordinates": rsds_stats["n_white"],
            "n_coloured_coordinates": rsds_stats["n_coloured"],
            "median_rsds_white": rsds_stats["median_white"],
            "median_rsds_coloured": rsds_stats["median_coloured"],
            "delta_rsds_white_minus_coloured": delta_rsds,
            "delta_rsds_bootstrap_low95": rsds_stats["bootstrap_95"][0],
            "delta_rsds_bootstrap_high95": rsds_stats["bootstrap_95"][1],
            "n_white_chroma": chroma_stats["n_white"],
            "n_coloured_chroma": chroma_stats["n_coloured"],
            "median_chroma_white": chroma_stats["median_white"],
            "median_chroma_coloured": chroma_stats["median_coloured"],
            "delta_chroma_white_minus_coloured": delta_chroma,
            "delta_chroma_bootstrap_low95": chroma_stats["bootstrap_95"][0],
            "delta_chroma_bootstrap_high95": chroma_stats["bootstrap_95"][1],
            "azami_direction_concordant": concordant,
            "n_white_rsds_cells_0_05deg": cell_rsds["n_white"],
            "n_coloured_rsds_cells_0_05deg": cell_rsds["n_coloured"],
            "delta_rsds_cell_median": cell_rsds["difference_white_minus_coloured"],
            "n_white_chroma_cells_0_05deg": cell_chroma["n_white"],
            "n_coloured_chroma_cells_0_05deg": cell_chroma["n_coloured"],
            "delta_chroma_cell_median": cell_chroma["difference_white_minus_coloured"],
            "cell_sensitivity_concordant": cell_concordant,
            "within_taxon_beta_std": within["beta_std"],
            "within_taxon_perm_p_two_sided": within["permutation_p_two_sided"],
            "within_taxon_perm_p_expected_negative": within["permutation_p_expected_negative"],
        })

    if concordant_count == 2:
        classification = contract["classification"]["two_system"]
    elif concordant_count == 1:
        classification = contract["classification"]["one_system"]
    else:
        classification = contract["classification"]["zero_system"]

    pooled_within = standardized_within_taxon_slope(cohort, rng)
    payload = {
        "contract_version": "chapter2_colour_rsds_focal_concordance_result_v1",
        "source_contract_version": contract["contract_version"],
        "azami_reference": contract["azami_reference"],
        "n_observations": int(len(cohort)),
        "n_taxa": int(cohort["taxon_name"].nunique()),
        "rsds_coverage": float(rsds.notna().mean()),
        "systems": system_payload,
        "primary_concordant_systems": int(concordant_count),
        "spatial_cell_concordant_systems": int(cell_concordant_count),
        "classification": classification,
        "locality_robust_two_system_direction": bool(concordant_count == 2 and cell_concordant_count == 2),
        "pooled_within_taxon_secondary": pooled_within,
        "interpretation": (
            "This is a present-state focal replication of the frozen Azami colour-RSDS direction. "
            "It is not a test of the historical radiative environment at the colour transition."
        ),
        "claim_boundary": contract["claim_boundary"],
    }

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(out / "chapter2_four_taxon_colour_rsds_enriched_cohort_v1.csv", index=False)
    pd.DataFrame(rows).to_csv(out / "chapter2_colour_rsds_focal_system_contrasts_v1.csv", index=False)
    (out / "chapter2_colour_rsds_focal_concordance_result_v1.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
