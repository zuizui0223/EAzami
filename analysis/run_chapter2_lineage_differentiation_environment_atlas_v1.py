#!/usr/bin/env python3
"""Explore historical climate context of dated East-Asian Cirsium lineage divergences.

This analysis is intentionally above the capitulum-trait level. It asks whether
predeclared dated lineage divergences repeatedly occupy unusual climate states,
short-window climate changes, or climate variability. It uses every BIOCLIM
variable supplied by the PALEO-PGEM-Series public record (BIO1 and BIO4-19),
propagates node-age and regional sensitivity scenarios, and treats nested
Nipponocirsium nodes as non-independent diagnostics.

Nothing here dates a capitulum-trait transition or tests natural selection.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Series:
    age_ka: np.ndarray
    value: np.ndarray

    def interp(self, ages: np.ndarray | float) -> np.ndarray:
        return np.interp(np.asarray(ages, dtype=float), self.age_ka, self.value)


def quantiles(x: np.ndarray) -> dict[str, float]:
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return {k: float("nan") for k in ("min", "q05", "median", "q95", "max")}
    return {
        "min": float(np.min(a)),
        "q05": float(np.quantile(a, 0.05)),
        "median": float(np.median(a)),
        "q95": float(np.quantile(a, 0.95)),
        "max": float(np.max(a)),
    }


def empirical_percentile(value: float, background: np.ndarray) -> float:
    bg = np.asarray(background, dtype=float)
    bg = bg[np.isfinite(bg)]
    if len(bg) == 0 or not np.isfinite(value):
        return float("nan")
    return float((np.sum(bg < value) + 0.5 * np.sum(bg == value) + 0.5) / (len(bg) + 1.0))


def tail_class(q: dict[str, float]) -> str:
    if np.isfinite(q["q95"]) and q["q95"] <= 0.10:
        return "robust_low"
    if np.isfinite(q["q05"]) and q["q05"] >= 0.90:
        return "robust_high"
    return "unresolved"


def high_class(q: dict[str, float]) -> str:
    if np.isfinite(q["q05"]) and q["q05"] >= 0.90:
        return "robust_high"
    return "unresolved"


def age_grid(event: dict[str, Any], n: int) -> np.ndarray:
    low = float(event["lower_ma"]) * 1000.0
    high = float(event["upper_ma"]) * 1000.0
    central = float(event["central_ma"]) * 1000.0
    vals = np.linspace(low, high, n)
    vals = np.unique(np.concatenate([vals, [central]])).astype(float)
    return np.sort(vals)


def window_std(series: Series, center_ka: float, width_ka: float) -> float:
    half = width_ka / 2.0
    ages = np.arange(center_ka - half, center_ka + half + 1e-9, 1.0)
    vals = series.interp(ages)
    return float(np.std(vals, ddof=0))


def load_series(series_dir: Path, variables: list[str], regions: list[str]) -> dict[tuple[str, str], Series]:
    files = sorted(series_dir.rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No regional series CSVs under {series_dir}")
    df = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
    required = {"variable", "region", "age_ka", "regional_median"}
    if not required.issubset(df.columns):
        raise ValueError(f"regional series missing columns {sorted(required - set(df.columns))}")
    df["variable"] = df["variable"].astype(str).str.upper()
    out: dict[tuple[str, str], Series] = {}
    for var in variables:
        for region in regions:
            sub = df[(df.variable == var) & (df.region == region)].copy()
            if sub.empty:
                raise ValueError(f"missing regional series for {var} {region}")
            sub = sub.sort_values("age_ka").drop_duplicates("age_ka")
            ages = sub.age_ka.to_numpy(float)
            vals = sub.regional_median.to_numpy(float)
            ok = np.isfinite(ages) & np.isfinite(vals)
            ages, vals = ages[ok], vals[ok]
            if len(ages) < 4900 or np.min(ages) > 1.0 or np.max(ages) < 4900.0:
                raise ValueError(f"short/invalid PALEO-PGEM series for {var} {region}")
            out[(var, region)] = Series(ages, vals)
    return out


def background_univariate(
    series: Series,
    min_ka: float,
    max_ka: float,
    width_ka: float | None,
    metric: str,
) -> np.ndarray:
    if metric == "level":
        centers = np.arange(min_ka, max_ka + 1e-9, 1.0)
        return series.interp(centers)
    if width_ka is None:
        raise ValueError("window width required")
    half = width_ka / 2.0
    centers = np.arange(min_ka + half, max_ka - half + 1e-9, 1.0)
    if metric == "absolute_change":
        return np.abs(series.interp(centers - half) - series.interp(centers + half))
    if metric == "local_variability":
        return np.asarray([window_std(series, c, width_ka) for c in centers], dtype=float)
    raise ValueError(metric)


def event_univariate_value(series: Series, age_ka: float, width_ka: float | None, metric: str) -> float:
    if metric == "level":
        return float(series.interp(age_ka))
    if width_ka is None:
        raise ValueError("window width required")
    half = width_ka / 2.0
    if metric == "absolute_change":
        return float(abs(series.interp(age_ka - half) - series.interp(age_ka + half)))
    if metric == "local_variability":
        return window_std(series, age_ka, width_ka)
    raise ValueError(metric)


def pca_model(
    series_map: dict[tuple[str, str], Series],
    variables: list[str],
    region: str,
    min_ka: float,
    max_ka: float,
) -> dict[str, Any]:
    ages = np.arange(min_ka, max_ka + 1e-9, 1.0)
    X = np.column_stack([series_map[(v, region)].interp(ages) for v in variables])
    mu = np.mean(X, axis=0)
    sd = np.std(X, axis=0, ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
        raise ValueError(f"nonfinite PCA scale for region={region}")
    Z = (X - mu) / sd
    _, s, vt = np.linalg.svd(Z, full_matrices=False)
    eig = (s ** 2) / max(len(Z) - 1, 1)
    frac = eig / np.sum(eig)
    k = int(np.searchsorted(np.cumsum(frac), 0.95) + 1)
    loadings = vt[:k].T
    scales = np.sqrt(eig[:k])
    return {
        "ages": ages,
        "mu": mu,
        "sd": sd,
        "loadings": loadings,
        "scales": scales,
        "k": k,
        "explained": float(np.sum(frac[:k])),
    }


def raw_vector(
    series_map: dict[tuple[str, str], Series], variables: list[str], region: str, ages: np.ndarray | float
) -> np.ndarray:
    a = np.atleast_1d(np.asarray(ages, dtype=float))
    return np.column_stack([series_map[(v, region)].interp(a) for v in variables])


def whiten(model: dict[str, Any], X: np.ndarray) -> np.ndarray:
    Z = (X - model["mu"]) / model["sd"]
    return (Z @ model["loadings"]) / model["scales"]


def multivariate_values(
    series_map: dict[tuple[str, str], Series],
    variables: list[str],
    region: str,
    model: dict[str, Any],
    centers: np.ndarray,
    metric: str,
    width_ka: float | None,
) -> np.ndarray:
    k = float(model["k"])
    if metric == "state_distance":
        W = whiten(model, raw_vector(series_map, variables, region, centers))
        return np.linalg.norm(W, axis=1) / np.sqrt(k)
    if width_ka is None:
        raise ValueError("window width required")
    half = width_ka / 2.0
    if metric == "displacement":
        W0 = whiten(model, raw_vector(series_map, variables, region, centers - half))
        W1 = whiten(model, raw_vector(series_map, variables, region, centers + half))
        return np.linalg.norm(W1 - W0, axis=1) / np.sqrt(k)
    if metric == "variability":
        vals = []
        for c in centers:
            ages = np.arange(c - half, c + half + 1e-9, 1.0)
            W = whiten(model, raw_vector(series_map, variables, region, ages))
            local = W - np.mean(W, axis=0, keepdims=True)
            vals.append(float(np.sqrt(np.mean(np.sum(local * local, axis=1))) / np.sqrt(k)))
        return np.asarray(vals, dtype=float)
    raise ValueError(metric)


def consistent_class(classes: list[str], high_only: bool = False) -> str:
    if not classes:
        return "unresolved"
    uniq = set(classes)
    if high_only:
        return "robust_high" if uniq == {"robust_high"} else "unresolved"
    if len(uniq) == 1 and next(iter(uniq)) in {"robust_low", "robust_high"}:
        return next(iter(uniq))
    return "unresolved"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series-dir", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-long-csv", type=Path, required=True)
    ap.add_argument("--out-event-csv", type=Path, required=True)
    args = ap.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    variables = list(contract["paleoclimate"]["available_bioclim_variables_used"])
    regions = list(contract["regions"])
    backgrounds = contract["backgrounds"]
    windows = [float(x) for x in contract["short_windows_ka"]]
    events = contract["events"]
    n_age = int(contract["age_uncertainty"]["grid_points_per_interval"])

    series_map = load_series(args.series_dir, variables, regions)

    # Cache background distributions for the univariate screen.
    uni_bg: dict[tuple[str, str, str, str, float | None], np.ndarray] = {}
    for bg_id, bg in backgrounds.items():
        lo, hi = float(bg["min_ma"]) * 1000.0, float(bg["max_ma"]) * 1000.0
        for region in regions:
            for var in variables:
                ser = series_map[(var, region)]
                uni_bg[(bg_id, region, var, "level", None)] = background_univariate(ser, lo, hi, None, "level")
                for w in windows:
                    for metric in ("absolute_change", "local_variability"):
                        uni_bg[(bg_id, region, var, metric, w)] = background_univariate(ser, lo, hi, w, metric)

    long_rows: list[dict[str, Any]] = []
    scenario_class: dict[tuple[str, str, str, str, float | None, str], str] = {}
    # key above: event, region, variable, metric, width, background
    for event in events:
        ages = age_grid(event, n_age)
        for region in event["region_scenarios"]:
            for bg_id, bg in backgrounds.items():
                lo, hi = float(bg["min_ma"]) * 1000.0, float(bg["max_ma"]) * 1000.0
                for var in variables:
                    ser = series_map[(var, region)]
                    specs = [("level", None)] + [
                        (metric, w) for w in windows for metric in ("absolute_change", "local_variability")
                    ]
                    for metric, width in specs:
                        if metric != "level":
                            half = float(width) / 2.0
                            usable_ages = ages[(ages - half >= lo) & (ages + half <= hi)]
                        else:
                            usable_ages = ages[(ages >= lo) & (ages <= hi)]
                        if len(usable_ages) != len(ages):
                            raise ValueError(
                                f"event age grid outside background for {event['context_id']} {bg_id} {metric} {width}"
                            )
                        bgdist = uni_bg[(bg_id, region, var, metric, width)]
                        pcts = np.asarray(
                            [
                                empirical_percentile(
                                    event_univariate_value(ser, age, width, metric), bgdist
                                )
                                for age in usable_ages
                            ],
                            dtype=float,
                        )
                        q = quantiles(pcts)
                        cls = tail_class(q)
                        scenario_class[(event["context_id"], region, var, metric, width, bg_id)] = cls
                        long_rows.append(
                            {
                                "layer": "univariate",
                                "context_id": event["context_id"],
                                "clade_group": event["clade_group"],
                                "group_representative": bool(event["group_representative"]),
                                "region": region,
                                "background": bg_id,
                                "variable": var,
                                "metric": metric,
                                "window_ka": width,
                                "n_age_scenarios": int(len(usable_ages)),
                                "percentile_min": q["min"],
                                "percentile_q05": q["q05"],
                                "percentile_median": q["median"],
                                "percentile_q95": q["q95"],
                                "percentile_max": q["max"],
                                "scenario_tail_class": cls,
                            }
                        )

    # Event-level univariate classes: regions and both background horizons must agree.
    event_uni_rows: list[dict[str, Any]] = []
    event_final_uni: dict[tuple[str, str, str], str] = {}
    for event in events:
        eid = event["context_id"]
        for var in variables:
            # level
            classes = [
                scenario_class[(eid, region, var, "level", None, bg_id)]
                for region in event["region_scenarios"]
                for bg_id in backgrounds
            ]
            cls = consistent_class(classes)
            event_final_uni[(eid, var, "level")] = cls
            event_uni_rows.append(
                {
                    "layer": "univariate_event",
                    "context_id": eid,
                    "clade_group": event["clade_group"],
                    "group_representative": bool(event["group_representative"]),
                    "variable": var,
                    "metric": "level",
                    "robust_class": cls,
                }
            )
            for metric in ("absolute_change", "local_variability"):
                window_classes = []
                for w in windows:
                    c = consistent_class(
                        [
                            scenario_class[(eid, region, var, metric, w, bg_id)]
                            for region in event["region_scenarios"]
                            for bg_id in backgrounds
                        ]
                    )
                    window_classes.append(c)
                cls = consistent_class(window_classes)
                event_final_uni[(eid, var, metric)] = cls
                event_uni_rows.append(
                    {
                        "layer": "univariate_event",
                        "context_id": eid,
                        "clade_group": event["clade_group"],
                        "group_representative": bool(event["group_representative"]),
                        "variable": var,
                        "metric": metric,
                        "robust_class": cls,
                    }
                )

    # Multivariate all-climate diagnostics.
    pca_cache: dict[tuple[str, str], dict[str, Any]] = {}
    mv_scenario_class: dict[tuple[str, str, str, float | None, str], str] = {}
    mv_pca_info: list[dict[str, Any]] = []
    for bg_id, bg in backgrounds.items():
        lo, hi = float(bg["min_ma"]) * 1000.0, float(bg["max_ma"]) * 1000.0
        for region in regions:
            model = pca_model(series_map, variables, region, lo, hi)
            pca_cache[(bg_id, region)] = model
            mv_pca_info.append(
                {
                    "background": bg_id,
                    "region": region,
                    "n_pcs_95pct": int(model["k"]),
                    "explained_variance": float(model["explained"]),
                }
            )

    mv_bg_cache: dict[tuple[str, str, str, float | None], np.ndarray] = {}
    for bg_id, bg in backgrounds.items():
        lo, hi = float(bg["min_ma"]) * 1000.0, float(bg["max_ma"]) * 1000.0
        for region in regions:
            model = pca_cache[(bg_id, region)]
            centers = np.arange(lo, hi + 1e-9, 1.0)
            mv_bg_cache[(bg_id, region, "state_distance", None)] = multivariate_values(
                series_map, variables, region, model, centers, "state_distance", None
            )
            for w in windows:
                half = w / 2.0
                centers_w = np.arange(lo + half, hi - half + 1e-9, 1.0)
                for metric in ("displacement", "variability"):
                    mv_bg_cache[(bg_id, region, metric, w)] = multivariate_values(
                        series_map, variables, region, model, centers_w, metric, w
                    )

    for event in events:
        ages = age_grid(event, n_age)
        for region in event["region_scenarios"]:
            for bg_id, bg in backgrounds.items():
                lo, hi = float(bg["min_ma"]) * 1000.0, float(bg["max_ma"]) * 1000.0
                model = pca_cache[(bg_id, region)]
                specs = [("state_distance", None)] + [
                    (metric, w) for w in windows for metric in ("displacement", "variability")
                ]
                for metric, width in specs:
                    if width is None:
                        usable = ages[(ages >= lo) & (ages <= hi)]
                    else:
                        half = float(width) / 2.0
                        usable = ages[(ages - half >= lo) & (ages + half <= hi)]
                    if len(usable) != len(ages):
                        raise ValueError(f"multivariate event ages outside background {event['context_id']}")
                    values = multivariate_values(
                        series_map, variables, region, model, usable, metric, width
                    )
                    bgdist = mv_bg_cache[(bg_id, region, metric, width)]
                    pcts = np.asarray([empirical_percentile(v, bgdist) for v in values], dtype=float)
                    q = quantiles(pcts)
                    cls = high_class(q)
                    mv_scenario_class[(event["context_id"], region, metric, width, bg_id)] = cls
                    long_rows.append(
                        {
                            "layer": "multivariate",
                            "context_id": event["context_id"],
                            "clade_group": event["clade_group"],
                            "group_representative": bool(event["group_representative"]),
                            "region": region,
                            "background": bg_id,
                            "variable": "ALL17_PCA95_WHITENED",
                            "metric": metric,
                            "window_ka": width,
                            "n_age_scenarios": int(len(usable)),
                            "percentile_min": q["min"],
                            "percentile_q05": q["q05"],
                            "percentile_median": q["median"],
                            "percentile_q95": q["q95"],
                            "percentile_max": q["max"],
                            "scenario_tail_class": cls,
                        }
                    )

    mv_event_rows: list[dict[str, Any]] = []
    mv_event_final: dict[tuple[str, str], str] = {}
    for event in events:
        eid = event["context_id"]
        classes = [
            mv_scenario_class[(eid, region, "state_distance", None, bg_id)]
            for region in event["region_scenarios"]
            for bg_id in backgrounds
        ]
        cls = consistent_class(classes, high_only=True)
        mv_event_final[(eid, "state_distance")] = cls
        mv_event_rows.append(
            {
                "layer": "multivariate_event",
                "context_id": eid,
                "clade_group": event["clade_group"],
                "group_representative": bool(event["group_representative"]),
                "variable": "ALL17_PCA95_WHITENED",
                "metric": "state_distance",
                "robust_class": cls,
            }
        )
        for metric in ("displacement", "variability"):
            wclasses = []
            for w in windows:
                wclasses.append(
                    consistent_class(
                        [
                            mv_scenario_class[(eid, region, metric, w, bg_id)]
                            for region in event["region_scenarios"]
                            for bg_id in backgrounds
                        ],
                        high_only=True,
                    )
                )
            cls = consistent_class(wclasses, high_only=True)
            mv_event_final[(eid, metric)] = cls
            mv_event_rows.append(
                {
                    "layer": "multivariate_event",
                    "context_id": eid,
                    "clade_group": event["clade_group"],
                    "group_representative": bool(event["group_representative"]),
                    "variable": "ALL17_PCA95_WHITENED",
                    "metric": metric,
                    "robust_class": cls,
                }
            )

    reps = [e for e in events if e["group_representative"]]
    if len(reps) != 3 or len({e["clade_group"] for e in reps}) != 3:
        raise ValueError("contract must define exactly three representative clade groups")

    recurring: list[dict[str, Any]] = []
    for var in variables:
        for metric in ("level", "absolute_change", "local_variability"):
            classes = [(e["clade_group"], event_final_uni[(e["context_id"], var, metric)]) for e in reps]
            high = [g for g, c in classes if c == "robust_high"]
            low = [g for g, c in classes if c == "robust_low"]
            if len(high) >= 2:
                recurring.append(
                    {
                        "layer": "univariate",
                        "variable": var,
                        "metric": metric,
                        "class": "robust_high",
                        "n_of_3_representative_groups": len(high),
                        "groups": high,
                    }
                )
            if len(low) >= 2:
                recurring.append(
                    {
                        "layer": "univariate",
                        "variable": var,
                        "metric": metric,
                        "class": "robust_low",
                        "n_of_3_representative_groups": len(low),
                        "groups": low,
                    }
                )
    for metric in ("state_distance", "displacement", "variability"):
        high = [e["clade_group"] for e in reps if mv_event_final[(e["context_id"], metric)] == "robust_high"]
        if len(high) >= 2:
            recurring.append(
                {
                    "layer": "multivariate",
                    "variable": "ALL17_PCA95_WHITENED",
                    "metric": metric,
                    "class": "robust_high",
                    "n_of_3_representative_groups": len(high),
                    "groups": high,
                }
            )

    event_df = pd.DataFrame(event_uni_rows + mv_event_rows)
    long_df = pd.DataFrame(long_rows)
    result = {
        "contract_version": contract["contract_version"],
        "analysis_scope": contract["analysis_scope"],
        "variables": variables,
        "n_variables": len(variables),
        "n_events": len(events),
        "representative_events": [e["context_id"] for e in reps],
        "representative_clade_groups": [e["clade_group"] for e in reps],
        "backgrounds": backgrounds,
        "short_windows_ka": windows,
        "pca_info": mv_pca_info,
        "event_univariate_classes": event_uni_rows,
        "event_multivariate_classes": mv_event_rows,
        "recurring_context_candidates": recurring,
        "decision": (
            "one_or_more_recurring_lineage_differentiation_context_candidates_detected"
            if recurring
            else "no_recurring_lineage_differentiation_context_survives_age_region_background_gates"
        ),
        "claim_boundary": contract["claim_boundary"],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    long_df.to_csv(args.out_long_csv, index=False)
    event_df.to_csv(args.out_event_csv, index=False)
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "n_variables": len(variables),
                "n_events": len(events),
                "representative_clade_groups": result["representative_clade_groups"],
                "n_recurring_candidates": len(recurring),
                "recurring_context_candidates": recurring,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
