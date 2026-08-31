#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SYSTEMS = {
    "ARENICOLA_BREVICAULE_IRUMTIENSE": {
        "white": "Cirsium brevicaule",
        "coloured": "Cirsium irumtiense",
    },
    "TAIWAN_KAWAKAMII_TATAKAENSE": {
        "white": "Cirsium kawakamii",
        "coloured": "Cirsium tatakaense",
    },
}

METRICS = {
    "corolla_lab_chroma": {"table": "primary", "status": "colour_status", "tier": "assay_anchor"},
    "corolla_lab_lightness": {"table": "primary", "status": "colour_status", "tier": "primary_colour"},
    "shape_aspect_ratio": {"table": "primary", "status": "shape_status", "tier": "primary_outline"},
    "shape_circularity": {"table": "primary", "status": "shape_status", "tier": "primary_outline"},
    "shape_solidity": {"table": "primary", "status": "shape_status", "tier": "primary_outline"},
    "shape_width_cv": {"table": "primary", "status": "shape_status", "tier": "primary_outline"},
    "visible_floret_fraction_extended": {"table": "extended", "status": None, "tier": "display_proxy"},
    "involucre_length_width_ratio": {"table": "extended", "status": "involucre_length_width_ratio_status", "tier": "architecture_proxy"},
    "involucre_apical_taper_ratio": {"table": "extended", "status": "involucre_apical_taper_ratio_status", "tier": "architecture_proxy"},
    "involucre_basal_taper_ratio": {"table": "extended", "status": "involucre_basal_taper_ratio_status", "tier": "architecture_proxy"},
    "involucre_projection_roughness": {"table": "extended", "status": "involucre_projection_roughness_status", "tier": "architecture_proxy"},
    "involucre_projection_p95": {"table": "extended", "status": "involucre_projection_p95_status", "tier": "architecture_proxy"},
    "involucre_spread_fraction": {"table": "extended", "status": "involucre_spread_fraction_status", "tier": "architecture_proxy"},
    "bract_projection_peak_density": {"table": "extended", "status": "bract_projection_peak_density_status", "tier": "architecture_proxy"},
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--primary", required=True, type=Path)
    p.add_argument("--extended", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--max-balanced-observations-per-taxon", type=int, default=16)
    p.add_argument("--neutral-min-dimension", type=float, default=300.0)
    p.add_argument("--neutral-min-sharpness", type=float, default=45.0)
    p.add_argument("--neutral-min-mask-quality", type=float, default=0.30)
    p.add_argument("--bootstrap-repeats", type=int, default=2000)
    return p.parse_args()


def obs_sort_key(value: object) -> tuple[int, str]:
    text = str(value)
    try:
        return (0, f"{int(float(text)):020d}")
    except Exception:
        return (1, text)


def rng_for(*parts: str) -> np.random.Generator:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "little"))


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    if not len(a) or not len(b):
        return float("nan")
    greater = 0
    less = 0
    for value in a:
        greater += int(np.sum(value > b))
        less += int(np.sum(value < b))
    return float((greater - less) / (len(a) * len(b)))


def bootstrap_median_difference(a: np.ndarray, b: np.ndarray, repeats: int, rng: np.random.Generator) -> tuple[float, float]:
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    diffs = np.empty(repeats, dtype=float)
    for i in range(repeats):
        diffs[i] = np.median(rng.choice(a, len(a), replace=True)) - np.median(rng.choice(b, len(b), replace=True))
    return float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))


def main() -> int:
    args = parse_args()
    manifest = pd.read_csv(args.manifest, dtype=str, keep_default_na=False)
    primary = pd.read_csv(args.primary, low_memory=False)
    extended = pd.read_csv(args.extended, low_memory=False)

    for frame, name in ((primary, "primary"), (extended, "extended")):
        if "annotation_unit_id" not in frame:
            raise ValueError(f"{name} table missing annotation_unit_id")
        if frame["annotation_unit_id"].duplicated().any():
            raise ValueError(f"{name} annotation_unit_id must be unique")

    joined = manifest.merge(primary, on="annotation_unit_id", how="inner", validate="one_to_one", suffixes=("", "_primary"))
    ext_keep = [c for c in extended.columns if c == "annotation_unit_id" or c not in joined.columns]
    joined = joined.merge(extended[ext_keep], on="annotation_unit_id", how="inner", validate="one_to_one")

    # Trait-neutral image-quality gate. No colour, outline, architecture endpoint,
    # or known white/coloured state enters this gate.
    for column in ("min_dimension", "sharpness", "mask_quality"):
        joined[column] = pd.to_numeric(joined[column], errors="coerce")
    joined["neutral_quality_gate"] = (
        joined["min_dimension"].ge(args.neutral_min_dimension)
        & joined["sharpness"].ge(args.neutral_min_sharpness)
        & joined["mask_quality"].ge(args.neutral_min_mask_quality)
    )

    passing = joined[joined["neutral_quality_gate"]].copy()
    passing["_photo_numeric"] = pd.to_numeric(passing["photo_id"], errors="coerce")
    passing = passing.sort_values(
        ["taxon_name", "obs_id", "mask_quality", "sharpness", "_photo_numeric"],
        ascending=[True, True, False, False, True],
    )
    best = passing.groupby(["taxon_name", "obs_id"], as_index=False, sort=False).head(1).copy()

    counts = best.groupby("taxon_name")["obs_id"].nunique().to_dict()
    expected_taxa = sorted({taxon for system in SYSTEMS.values() for taxon in system.values()})
    if set(counts) != set(expected_taxa):
        missing = sorted(set(expected_taxa) - set(counts))
        raise RuntimeError(f"neutral quality gate leaves no observation for taxa: {missing}")
    balanced_n = min(args.max_balanced_observations_per_taxon, min(int(counts[t]) for t in expected_taxa))
    if balanced_n <= 0:
        raise RuntimeError("balanced observation count is zero")

    selected_parts: list[pd.DataFrame] = []
    for taxon in expected_taxa:
        part = best[best["taxon_name"].eq(taxon)].copy()
        ordered_obs = sorted(part["obs_id"].astype(str).unique(), key=obs_sort_key)[:balanced_n]
        selected_parts.append(part[part["obs_id"].astype(str).isin(ordered_obs)])
    selected = pd.concat(selected_parts, ignore_index=True).drop(columns=["_photo_numeric"], errors="ignore")
    selected["balanced_pilot_selected"] = True

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    selected.to_csv(out / "chapter2_four_taxon_balanced_image_measurements_v1.csv", index=False, encoding="utf-8-sig")

    contrast_rows: list[dict[str, object]] = []
    metric_sources = {"primary": primary, "extended": extended}
    for system_id, roles in SYSTEMS.items():
        white_taxon = roles["white"]
        coloured_taxon = roles["coloured"]
        for metric, spec in METRICS.items():
            if metric not in selected.columns:
                continue
            work = selected[selected["taxon_name"].isin([white_taxon, coloured_taxon])].copy()
            values = pd.to_numeric(work[metric], errors="coerce")
            usable = values.notna()
            status_column = spec["status"]
            if status_column:
                if status_column not in work.columns:
                    continue
                usable &= work[status_column].astype(str).eq("usable")
            work = work[usable].copy()
            work[metric] = pd.to_numeric(work[metric], errors="coerce")
            white = work[work["taxon_name"].eq(white_taxon)][metric].dropna().to_numpy(float)
            coloured = work[work["taxon_name"].eq(coloured_taxon)][metric].dropna().to_numpy(float)
            if len(white) and len(coloured):
                white_median = float(np.median(white))
                coloured_median = float(np.median(coloured))
                diff = white_median - coloured_median
                ci_low, ci_high = bootstrap_median_difference(
                    white,
                    coloured,
                    args.bootstrap_repeats,
                    rng_for(system_id, metric, "bootstrap"),
                )
                delta = cliffs_delta(white, coloured)
                direction = "white_higher" if diff > 0 else "white_lower" if diff < 0 else "equal"
            else:
                white_median = coloured_median = diff = ci_low = ci_high = delta = float("nan")
                direction = "not_evaluable"
            contrast_rows.append({
                "system_id": system_id,
                "white_taxon": white_taxon,
                "coloured_taxon": coloured_taxon,
                "metric": metric,
                "metric_tier": spec["tier"],
                "n_white_usable": int(len(white)),
                "n_coloured_usable": int(len(coloured)),
                "white_median": white_median,
                "coloured_median": coloured_median,
                "white_minus_coloured_median": diff,
                "bootstrap_low_95": ci_low,
                "bootstrap_high_95": ci_high,
                "cliffs_delta_white_vs_coloured": delta,
                "direction": direction,
                "inference_class": "observation_level_public_image_pilot_not_independent_evolutionary_replication",
            })

    contrasts = pd.DataFrame(contrast_rows)
    contrasts.to_csv(out / "chapter2_four_taxon_pairwise_image_contrasts_v1.csv", index=False, encoding="utf-8-sig")

    chroma = contrasts[contrasts["metric"].eq("corolla_lab_chroma")].set_index("system_id")
    chroma_assay_gate = bool(
        set(SYSTEMS).issubset(chroma.index)
        and all(
            chroma.loc[system_id, "n_white_usable"] >= 3
            and chroma.loc[system_id, "n_coloured_usable"] >= 3
            and chroma.loc[system_id, "white_minus_coloured_median"] < 0
            for system_id in SYSTEMS
        )
    )

    repeated: dict[str, object] = {}
    for metric in METRICS:
        part = contrasts[contrasts["metric"].eq(metric)]
        if len(part) != len(SYSTEMS):
            continue
        dirs = part["direction"].tolist()
        sufficient = bool((part["n_white_usable"] >= 3).all() and (part["n_coloured_usable"] >= 3).all())
        same = sufficient and dirs[0] == dirs[1] and dirs[0] in {"white_higher", "white_lower"}
        repeated[metric] = {
            "same_direction_across_two_sister_systems": bool(same),
            "direction": dirs[0] if same else "heterogeneous_or_not_evaluable",
            "system_directions": dict(zip(part["system_id"], dirs)),
            "minimum_usable_per_role": int(min(part["n_white_usable"].min(), part["n_coloured_usable"].min())),
            "interpretation_allowed": bool(chroma_assay_gate or metric == "corolla_lab_chroma"),
        }

    architecture_repeated = [
        metric for metric, payload in repeated.items()
        if METRICS[metric]["tier"] in {"architecture_proxy", "primary_outline", "display_proxy"}
        and payload["same_direction_across_two_sister_systems"]
        and payload["interpretation_allowed"]
    ]

    report = {
        "contract_version": "chapter2_four_taxon_azami_measurement_pilot_v1",
        "balanced_observations_per_taxon": int(balanced_n),
        "neutral_quality_gate": {
            "min_dimension": args.neutral_min_dimension,
            "min_sharpness": args.neutral_min_sharpness,
            "min_mask_quality": args.neutral_min_mask_quality,
            "selection_uses_trait_values": False,
            "best_photo_per_observation": "highest mask_quality then sharpness; photo id only tie-break",
        },
        "neutral_passing_observations_before_balancing": {k: int(v) for k, v in counts.items()},
        "colour_assay_gate": {
            "criterion": "white lineage has lower Azami-compatible corolla Lab chroma in both dated sister systems with >=3 usable observations per role",
            "passed": chroma_assay_gate,
        },
        "repeated_direction_metrics": repeated,
        "architecture_or_outline_repeated_direction_metrics_after_assay_gate": architecture_repeated,
        "interpretation": (
            "If the chroma assay gate passes, repeated same-direction architecture/outline metrics are public-image hypothesis generators for broader head remodelling. "
            "They are not reconstructed correlated transitions and are not adaptation evidence."
        ),
        "claim_boundary": [
            "observations within a taxon are not independent macroevolutionary transitions",
            "image-derived architecture metrics are not homologous to the published botanical phyllary measurements",
            "public-image sampling and photography can induce residual bias despite balancing and trait-neutral image-quality selection",
            "same-direction sister contrasts do not establish correlated evolution, a white-flower syndrome, common developmental mechanism, selection or adaptation",
        ],
    }
    (out / "chapter2_four_taxon_azami_measurement_pilot_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
