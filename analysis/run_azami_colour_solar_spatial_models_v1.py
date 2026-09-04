#!/usr/bin/env python3
"""Test public-image flower colour against solar radiation across spatial scales.

The analysis operates on taxon × 0.05-degree cell × source medians to reduce image
pseudoreplication. It reports univariate, climate-adjusted, within-taxon and
among-taxon associations, plus source, geographic-block and species leave-one-out
sign stability. CIELAB lightness is transformed to darkness (−L*); chroma, a* and
an explicitly named pigment metric are kept as separate outcomes. When L*, a* and
chroma coexist, a source-standardized pink-pigment composite is added as a bounded
sensitivity rather than replacing its components.

This is a spatial public-data association analysis. It does not establish adaptive
fitness, historical change, genetic control or photographic calibration.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm

ENV = [
    "worldclim21_srad_annual_mean",
    "worldclim21_bio01",
    "worldclim21_bio12",
    "worldclim21_bio15",
]
SOLAR = ENV[0]
CONTROLS = ENV[1:]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--resolution", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--min-taxon-cells", type=int, default=3)
    p.add_argument("--min-source-cells", type=int, default=30)
    p.add_argument("--min-source-taxa", type=int, default=3)
    return p.parse_args()


def zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    sd = float(s.std(ddof=1))
    if not math.isfinite(sd) or sd <= 0:
        return pd.Series(np.nan, index=s.index)
    return (s - float(s.mean())) / sd


def source_zscore(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame.groupby("source", group_keys=False)[column].apply(zscore).reindex(frame.index)


def build_metrics(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str], str]:
    d = data.copy()
    metrics: list[str] = []
    if "observed_lightness" in d:
        d["colour_darkness"] = -pd.to_numeric(d["observed_lightness"], errors="coerce")
        metrics.append("colour_darkness")
    chroma_col = "observed_chroma" if "observed_chroma" in d else "observed_chroma_derived" if "observed_chroma_derived" in d else None
    if chroma_col:
        d["colour_chroma"] = pd.to_numeric(d[chroma_col], errors="coerce")
        metrics.append("colour_chroma")
    if "observed_lab_a" in d:
        d["colour_red_axis_a"] = pd.to_numeric(d["observed_lab_a"], errors="coerce")
        metrics.append("colour_red_axis_a")
    if "observed_pigment" in d:
        d["colour_named_pigment"] = pd.to_numeric(d["observed_pigment"], errors="coerce")
        metrics.append("colour_named_pigment")
    if {"colour_darkness", "colour_chroma", "colour_red_axis_a"}.issubset(d.columns):
        components = [source_zscore(d, x) for x in ("colour_darkness", "colour_chroma", "colour_red_axis_a")]
        d["colour_pink_pigment_composite"] = pd.concat(components, axis=1).mean(axis=1, skipna=False)
        metrics.append("colour_pink_pigment_composite")
    if not metrics:
        raise RuntimeError("no normalized colour metric available")
    primary = "colour_pink_pigment_composite" if "colour_pink_pigment_composite" in metrics else "colour_red_axis_a" if "colour_red_axis_a" in metrics else "colour_darkness" if "colour_darkness" in metrics else metrics[0]
    return d, metrics, primary


def prepare_cells(data: pd.DataFrame, metrics: list[str], min_taxon_cells: int) -> pd.DataFrame:
    required = {"taxon_raw", "source", "canonical_cell_005_lat", "canonical_cell_005_lon", *ENV}
    missing = required - set(data.columns)
    if missing:
        raise KeyError(sorted(missing))
    d = data.loc[data["worldclim_environment_complete"].astype(str).str.casefold().isin({"true", "1", "yes"})].copy()
    d["source"] = d["source"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
    for col in ENV + metrics:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    group = ["taxon_raw", "source", "canonical_cell_005_lat", "canonical_cell_005_lon"]
    agg = {col: "median" for col in ENV + metrics}
    agg.update({"latitude": "median", "longitude": "median"})
    cells = d.groupby(group, dropna=False, as_index=False).agg(agg)
    cells["spatial_block_2deg"] = (
        np.floor(cells.latitude / 2).astype("Int64").astype(str)
        + "_" + np.floor(cells.longitude / 2).astype("Int64").astype(str)
    )
    counts = cells.groupby("taxon_raw").size()
    keep = set(counts[counts >= min_taxon_cells].index)
    cells = cells.loc[cells.taxon_raw.isin(keep)].copy()
    return cells


def design_matrix(frame: pd.DataFrame, predictors: list[str], include_source: bool) -> tuple[pd.DataFrame, list[str]]:
    x = pd.DataFrame(index=frame.index)
    names = []
    for col in predictors:
        name = col + "_z"
        x[name] = zscore(frame[col])
        names.append(name)
    if include_source and frame.source.nunique() > 1:
        dummies = pd.get_dummies(frame.source.astype(str), prefix="source", drop_first=True, dtype=float)
        x = pd.concat([x, dummies], axis=1)
        names.extend(dummies.columns.tolist())
    x = sm.add_constant(x, has_constant="add")
    return x, names


def fit_model(frame: pd.DataFrame, outcome: str, predictors: list[str], *, include_source: bool, weights: pd.Series | None = None, cluster: pd.Series | None = None) -> dict[str, Any]:
    needed = [outcome, *predictors]
    mask = frame[needed].notna().all(axis=1)
    f = frame.loc[mask].copy()
    if len(f) <= len(predictors) + 3:
        raise ValueError("insufficient rows")
    y = zscore(f[outcome])
    X, names = design_matrix(f, predictors, include_source)
    keep = y.notna() & X.notna().all(axis=1)
    f, y, X = f.loc[keep], y.loc[keep], X.loc[keep]
    if len(f) <= X.shape[1] + 2:
        raise ValueError("insufficient residual degrees of freedom")
    if weights is None:
        model = sm.OLS(y, X)
    else:
        w = pd.to_numeric(weights.reindex(f.index), errors="coerce").fillna(1.0)
        model = sm.WLS(y, X, weights=w)
    if cluster is not None:
        groups = cluster.reindex(f.index).astype(str)
        n_clusters = int(groups.nunique())
        if n_clusters >= 3:
            fit = model.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True})
            covariance = "cluster"
        else:
            fit = model.fit(cov_type="HC3")
            covariance = "HC3_fallback_fewer_than_3_clusters"
    else:
        n_clusters = None
        fit = model.fit(cov_type="HC3")
        covariance = "HC3"
    solar_name = SOLAR + "_z"
    beta = float(fit.params[solar_name])
    se = float(fit.bse[solar_name])
    p = float(fit.pvalues[solar_name])
    ci = [float(x) for x in fit.conf_int().loc[solar_name].tolist()]
    return {
        "n": int(len(f)),
        "n_taxa": int(f.taxon_raw.nunique()) if "taxon_raw" in f else None,
        "n_sources": int(f.source.nunique()) if "source" in f else None,
        "n_spatial_blocks": int(f.spatial_block_2deg.nunique()) if "spatial_block_2deg" in f else None,
        "n_covariance_clusters": n_clusters,
        "covariance": covariance,
        "solar_beta_standardized": beta,
        "solar_se": se,
        "solar_p": p,
        "solar_ci95": ci,
        "solar_sign": int(np.sign(beta)),
        "adjusted_r2": float(getattr(fit, "rsquared_adj", float("nan"))),
        "design_condition_number": float(np.linalg.cond(np.asarray(X, dtype=float))),
        "predictors": predictors,
        "source_fixed_effects": bool(include_source and f.source.nunique() > 1),
    }


def within_taxon_frame(cells: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = cells.copy()
    for col in columns:
        out[col] = out[col] - out.groupby("taxon_raw")[col].transform("mean")
    return out


def among_taxon_frame(cells: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    agg = {x: "mean" for x in [*ENV, *metrics, "latitude", "longitude"]}
    among = cells.groupby("taxon_raw", as_index=False).agg(agg)
    among["n_cells"] = cells.groupby("taxon_raw").size().reindex(among.taxon_raw).to_numpy()
    among["source"] = "taxon_mean"
    among["spatial_block_2deg"] = "taxon_mean"
    return among


def loo_signs(frame: pd.DataFrame, outcome: str, predictors: list[str], unit: str, include_source: bool, weights_col: str | None = None) -> dict[str, Any]:
    full = fit_model(
        frame, outcome, predictors, include_source=include_source,
        weights=frame[weights_col] if weights_col else None,
        cluster=frame["spatial_block_2deg"] if "spatial_block_2deg" in frame else None,
    )
    reference = full["solar_sign"]
    signs: list[int] = []
    failures: list[str] = []
    for value in sorted(frame[unit].dropna().astype(str).unique()):
        q = frame.loc[frame[unit].astype(str) != value].copy()
        try:
            fit = fit_model(
                q, outcome, predictors, include_source=include_source,
                weights=q[weights_col] if weights_col else None,
                cluster=q["spatial_block_2deg"] if "spatial_block_2deg" in q else None,
            )
            signs.append(fit["solar_sign"])
        except Exception as exc:
            failures.append(f"{value}:{type(exc).__name__}")
    return {
        "reference_sign": reference,
        "evaluations": len(signs),
        "sign_agreement": float(sum(x == reference for x in signs) / len(signs)) if signs else None,
        "signs": signs,
        "failures": failures,
    }


def classify(models: dict[str, Any], loo: dict[str, Any]) -> str:
    required = [models.get("adjusted_total"), models.get("within_taxon_adjusted"), models.get("among_taxon_adjusted")]
    available = [x for x in required if isinstance(x, dict) and "solar_sign" in x]
    if not available:
        return "not_evaluable"
    signs = {x["solar_sign"] for x in available}
    total = models.get("adjusted_total", {})
    stable = all(
        x.get("sign_agreement") is None or x.get("sign_agreement", 0) >= 0.8
        for x in loo.values()
    )
    any_ci = any(x["solar_ci95"][0] > 0 or x["solar_ci95"][1] < 0 for x in available)
    if len(signs) == 1 and stable and any_ci:
        return "cross_spatial_scale_direction_supported"
    if len(signs) == 1 and stable:
        return "direction_stable_threshold_unresolved"
    if len(signs) > 1:
        return "scale_or_model_sensitive"
    return "unresolved"


def main() -> int:
    a = parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    resolution = json.loads(a.resolution.read_text(encoding="utf-8"))
    raw = pd.read_csv(a.data)
    data, metrics, primary = build_metrics(raw)
    cells = prepare_cells(data, metrics, a.min_taxon_cells)
    if len(cells) < 30 or cells.taxon_raw.nunique() < 5:
        raise RuntimeError("insufficient cell/taxon coverage after frozen filters")
    among = among_taxon_frame(cells, metrics)
    results: dict[str, Any] = {}

    for metric in metrics:
        block: dict[str, Any] = {"models": {}, "leave_one_out": {}}
        specs = {
            "univariate_total": (cells, [SOLAR], True, None, cells["spatial_block_2deg"]),
            "adjusted_total": (cells, [SOLAR, *CONTROLS], True, None, cells["spatial_block_2deg"]),
            "within_taxon_adjusted": (
                within_taxon_frame(cells, [metric, *ENV]), [SOLAR, *CONTROLS], True, None, cells["taxon_raw"]
            ),
            "among_taxon_univariate": (among, [SOLAR], False, None, None),
            "among_taxon_adjusted": (among, [SOLAR, *CONTROLS], False, None, None),
            "among_taxon_adjusted_weighted": (among, [SOLAR, *CONTROLS], False, np.sqrt(among["n_cells"]), None),
        }
        for label, (frame, predictors, source_effects, weights, cluster) in specs.items():
            try:
                block["models"][label] = fit_model(
                    frame, metric, predictors, include_source=source_effects,
                    weights=weights if isinstance(weights, pd.Series) else None,
                    cluster=cluster if isinstance(cluster, pd.Series) else None,
                )
            except Exception as exc:
                block["models"][label] = {"status": "not_evaluable", "reason": f"{type(exc).__name__}: {exc}"}

        try:
            block["leave_one_out"]["source_loo_adjusted_total"] = loo_signs(cells, metric, [SOLAR, *CONTROLS], "source", True)
        except Exception as exc:
            block["leave_one_out"]["source_loo_adjusted_total"] = {"status": "not_evaluable", "reason": str(exc)}
        try:
            block["leave_one_out"]["spatial_block_loo_adjusted_total"] = loo_signs(cells, metric, [SOLAR, *CONTROLS], "spatial_block_2deg", True)
        except Exception as exc:
            block["leave_one_out"]["spatial_block_loo_adjusted_total"] = {"status": "not_evaluable", "reason": str(exc)}
        try:
            block["leave_one_out"]["taxon_loo_among_adjusted"] = loo_signs(among, metric, [SOLAR, *CONTROLS], "taxon_raw", False)
        except Exception as exc:
            block["leave_one_out"]["taxon_loo_among_adjusted"] = {"status": "not_evaluable", "reason": str(exc)}

        source_specific = {}
        for source, q in cells.groupby("source"):
            if len(q) < a.min_source_cells or q.taxon_raw.nunique() < a.min_source_taxa:
                continue
            try:
                source_specific[str(source)] = fit_model(q, metric, [SOLAR, *CONTROLS], include_source=False, cluster=q["spatial_block_2deg"])
            except Exception as exc:
                source_specific[str(source)] = {"status": "not_evaluable", "reason": str(exc)}
        block["source_specific_adjusted"] = source_specific
        block["classification"] = classify(block["models"], block["leave_one_out"])
        results[metric] = block

    cell_path = a.out_dir / "azami_colour_solar_taxon_cell_source_v1.csv"
    cells.to_csv(cell_path, index=False)
    among.to_csv(a.out_dir / "azami_colour_solar_taxon_means_v1.csv", index=False)

    payload = {
        "contract_version": "azami_colour_solar_spatial_models_v1",
        "estimand": "spatial correspondence between image-derived flower colour and WorldClim 2.1 solar radiation across total, within-taxon and among-taxon scales",
        "source_resolution": resolution,
        "primary_metric": primary,
        "metrics": metrics,
        "cell_aggregation": "median by taxon x source x 0.05-degree cell",
        "coverage": {
            "cell_source_rows": int(len(cells)),
            "taxa": int(cells.taxon_raw.nunique()),
            "sources": int(cells.source.nunique()),
            "two_degree_spatial_blocks": int(cells.spatial_block_2deg.nunique()),
            "taxa_minimum_cells": a.min_taxon_cells,
        },
        "results": results,
        "overall_classification": results[primary]["classification"],
        "claim_boundaries": [
            "The analysis uses public-image colour estimates and cannot by itself guarantee absolute colour calibration.",
            "Source fixed effects, source-specific fits and source LOO quantify but do not eliminate platform/camera bias.",
            "Within-taxon spatial association is not proof of plasticity or local adaptation; among-taxon association is not proof of historical selection.",
            "WorldClim climatology represents current spatial environment, not conditions at ancestral transitions.",
            "Cross-spatial-scale agreement can strengthen an adaptive hypothesis but does not establish fitness benefit or causal adaptation.",
        ],
    }
    (a.out_dir / "azami_colour_solar_spatial_models_v1.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"coverage": payload["coverage"], "primary_metric": primary, "overall_classification": payload["overall_classification"], "metric_classes": {k:v["classification"] for k,v in results.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
