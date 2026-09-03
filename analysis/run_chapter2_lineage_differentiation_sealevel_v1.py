#!/usr/bin/env python3
"""Global sea-level context across three representative Cirsium lineage divergences.

This is a lineage-level range-reorganization diagnostic. It does not reconstruct
local land bridges and it does not assign lineage-divergence ages to capitulum
trait changes.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DYNAMIC_METRICS = (
    "window_sd_m",
    "window_range_m",
    "endpoint_abs_change_m",
    "mean_abs_1k_change_m",
    "max_abs_1k_change_m",
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def load_source(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    header_i = None
    for i, line in enumerate(lines):
        if line.startswith("age_calkaBP\t") and i + 1 < len(lines):
            try:
                float(lines[i + 1].split("\t")[0])
                header_i = i
                break
            except Exception:
                pass
    if header_i is None:
        raise ValueError("numeric age_calkaBP data header not found")
    df = pd.read_csv(io.StringIO("\n".join(lines[header_i:])), sep="\t")
    for c in ("age_calkaBP", "sealev"):
        if c not in df.columns:
            raise ValueError(f"missing required source column {c}")
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return (
        df.dropna(subset=["age_calkaBP", "sealev"])
        .sort_values("age_calkaBP")
        .drop_duplicates("age_calkaBP")
        .reset_index(drop=True)
    )


def one_kyr_series(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    lo = float(df.age_calkaBP.min())
    hi = float(df.age_calkaBP.max())
    ages = np.arange(np.ceil(lo), np.floor(hi) + 1e-9, 1.0)
    vals = np.interp(ages, df.age_calkaBP.to_numpy(float), df.sealev.to_numpy(float))
    return ages, vals


def age_grid(event: dict[str, Any], n: int) -> np.ndarray:
    low = float(event["lower_ma"]) * 1000.0
    high = float(event["upper_ma"]) * 1000.0
    central = float(event["central_ma"]) * 1000.0
    return np.sort(np.unique(np.concatenate([np.linspace(low, high, n), [central]])))


def interp(ages: np.ndarray, vals: np.ndarray, x: np.ndarray | float) -> np.ndarray:
    return np.interp(np.asarray(x, dtype=float), ages, vals)


def window_metrics(ages: np.ndarray, vals: np.ndarray, center: float, width: float) -> dict[str, float]:
    half = width / 2.0
    grid = np.arange(center - half, center + half + 1e-9, 1.0)
    y = interp(ages, vals, grid)
    d = np.diff(y)
    return {
        "window_mean_m": float(np.mean(y)),
        "window_sd_m": float(np.std(y, ddof=0)),
        "window_range_m": float(np.max(y) - np.min(y)),
        "endpoint_abs_change_m": float(abs(y[-1] - y[0])),
        "mean_abs_1k_change_m": float(np.mean(np.abs(d))),
        "max_abs_1k_change_m": float(np.max(np.abs(d))),
    }


def percentile(value: float, bg: np.ndarray) -> float:
    a = np.asarray(bg, dtype=float)
    a = a[np.isfinite(a)]
    return float((np.sum(a < value) + 0.5 * np.sum(a == value) + 0.5) / (len(a) + 1.0))


def qsum(x: np.ndarray | list[float]) -> dict[str, float]:
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    return {
        "min": float(np.min(a)),
        "q05": float(np.quantile(a, 0.05)),
        "median": float(np.median(a)),
        "q95": float(np.quantile(a, 0.95)),
        "max": float(np.max(a)),
    }


def tail_class(q: dict[str, float]) -> str:
    if q["q95"] <= 0.10:
        return "robust_low"
    if q["q05"] >= 0.90:
        return "robust_high"
    return "unresolved"


def high_class(q: dict[str, float]) -> str:
    return "robust_high" if q["q05"] >= 0.90 else "unresolved"


def consistent(classes: list[str], high_only: bool = False) -> str:
    if high_only:
        return "robust_high" if classes and set(classes) == {"robust_high"} else "unresolved"
    return classes[0] if classes and len(set(classes)) == 1 and classes[0] in {"robust_low", "robust_high"} else "unresolved"


def background_window_metrics(
    ages: np.ndarray,
    vals: np.ndarray,
    lo: float,
    hi: float,
    width: float,
) -> dict[str, np.ndarray]:
    half = width / 2.0
    centers = np.arange(lo + half, hi - half + 1e-9, 1.0)
    rows = [window_metrics(ages, vals, float(c), width) for c in centers]
    keys = list(rows[0])
    return {k: np.asarray([r[k] for r in rows], dtype=float) for k in keys}


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    df = load_source(args.source)
    ages, vals = one_kyr_series(df)
    if ages.min() > 1.0 or ages.max() < 3600.0:
        raise ValueError(f"source coverage insufficient: {ages.min()}-{ages.max()} ka")

    events = contract["representative_events"]
    n_age = int(contract["age_uncertainty"]["grid_points_per_interval"])
    windows = [float(x) for x in contract["short_windows_ka"]]
    backgrounds = contract["background_horizons"]

    # background caches
    state_bg: dict[str, np.ndarray] = {}
    window_bg: dict[tuple[str, float], dict[str, np.ndarray]] = {}
    for bg_id, bg in backgrounds.items():
        lo = float(bg["min_ma"]) * 1000.0
        hi = float(bg["max_ma"]) * 1000.0
        centers = np.arange(lo, hi + 1e-9, 1.0)
        state_bg[bg_id] = interp(ages, vals, centers)
        for w in windows:
            window_bg[(bg_id, w)] = background_window_metrics(ages, vals, lo, hi, w)

    scenario_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    final_classes: dict[tuple[str, str], str] = {}

    for event in events:
        eid = event["context_id"]
        eg = age_grid(event, n_age)

        # sea-level state at node age
        state_classes = []
        for bg_id in backgrounds:
            pcts = np.asarray([percentile(float(interp(ages, vals, a)), state_bg[bg_id]) for a in eg])
            q = qsum(pcts)
            cls = tail_class(q)
            state_classes.append(cls)
            scenario_rows.append({
                "context_id": eid,
                "clade_group": event["clade_group"],
                "background": bg_id,
                "metric": "sea_level_state_m",
                "window_ka": None,
                **{f"percentile_{k}": v for k, v in q.items()},
                "scenario_class": cls,
            })
        cls = consistent(state_classes)
        final_classes[(eid, "sea_level_state_m")] = cls
        event_rows.append({
            "context_id": eid,
            "clade_group": event["clade_group"],
            "metric": "sea_level_state_m",
            "robust_class": cls,
        })

        # fixed-window metrics
        metrics = ["window_mean_m", *DYNAMIC_METRICS]
        for metric in metrics:
            per_window_classes = []
            for w in windows:
                per_bg = []
                half = w / 2.0
                if np.any(eg - half < ages.min()) or np.any(eg + half > ages.max()):
                    raise ValueError(f"source window coverage insufficient for {eid} {w}")
                event_values = np.asarray([window_metrics(ages, vals, float(a), w)[metric] for a in eg])
                for bg_id in backgrounds:
                    bgdist = window_bg[(bg_id, w)][metric]
                    pcts = np.asarray([percentile(v, bgdist) for v in event_values])
                    q = qsum(pcts)
                    c = tail_class(q) if metric == "window_mean_m" else high_class(q)
                    per_bg.append(c)
                    scenario_rows.append({
                        "context_id": eid,
                        "clade_group": event["clade_group"],
                        "background": bg_id,
                        "metric": metric,
                        "window_ka": w,
                        **{f"percentile_{k}": v for k, v in q.items()},
                        "scenario_class": c,
                    })
                per_window_classes.append(consistent(per_bg, high_only=(metric != "window_mean_m")))
            c = consistent(per_window_classes, high_only=(metric != "window_mean_m"))
            final_classes[(eid, metric)] = c
            event_rows.append({
                "context_id": eid,
                "clade_group": event["clade_group"],
                "metric": metric,
                "robust_class": c,
            })

    recurring = []
    all_metrics = ["sea_level_state_m", "window_mean_m", *DYNAMIC_METRICS]
    for metric in all_metrics:
        high = [e["clade_group"] for e in events if final_classes[(e["context_id"], metric)] == "robust_high"]
        low = [e["clade_group"] for e in events if final_classes[(e["context_id"], metric)] == "robust_low"]
        if len(high) >= 2:
            recurring.append({
                "metric": metric,
                "class": "robust_high",
                "n_of_3_representative_groups": len(high),
                "groups": high,
            })
        if len(low) >= 2:
            recurring.append({
                "metric": metric,
                "class": "robust_low",
                "n_of_3_representative_groups": len(low),
                "groups": low,
            })

    result = {
        "contract_version": contract["contract_version"],
        "analysis_scope": contract["analysis_scope"],
        "source": contract["source"],
        "representative_events": events,
        "n_representative_groups": len(events),
        "background_horizons": backgrounds,
        "short_windows_ka": windows,
        "event_metric_classes": event_rows,
        "recurring_context_candidates": recurring,
        "decision": (
            "one_or_more_recurring_global_sea_level_context_candidates_detected"
            if recurring
            else "no_recurring_global_sea_level_context_survives_age_background_window_gates"
        ),
        "claim_boundary": contract["claim_boundary"],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(scenario_rows).to_csv(args.out_csv, index=False)
    print(json.dumps({
        "decision": result["decision"],
        "n_event_metric_robust": int(sum(r["robust_class"] != "unresolved" for r in event_rows)),
        "n_recurring_context_candidates": len(recurring),
        "recurring_context_candidates": recurring,
        "event_metric_classes": event_rows,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
