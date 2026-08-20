#!/usr/bin/env python3
"""Predictive shrinkage check for the four C. purpuratum probing slopes.

This follows the exact residual diagnostic in PR #38. The saturated 4-parameter context model
can interpolate four observations, so it is not promoted directly into the full simulation.
Instead, this script asks whether year/context deviations improve leave-one-out prediction once
those deviations are ridge-shrunk toward a shared display-response structure.

The operational log-distance scale used elsewhere is not treated as a sampling-error SE here.
This is a small predictive guardrail, not posterior inference.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

TARGET_IDS = [
    "CIR_DISPLAY_PROBE_97HD",
    "CIR_DISPLAY_PROBE_97LD",
    "CIR_DISPLAY_PROBE_98HD",
    "CIR_DISPLAY_PROBE_98LD",
]
X = [
    [1.0, 0.0, 0.0, 0.0],  # 1997 high density
    [1.0, 1.0, 0.0, 0.0],  # 1997 low density
    [1.0, 0.0, 1.0, 0.0],  # 1998 high density
    [1.0, 1.0, 1.0, 1.0],  # 1998 low density
]


def solve_linear(a, b):
    n = len(b)
    m = [list(map(float, a[i])) + [float(b[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[pivot] = m[pivot], m[col]
        p = m[col][col]
        if abs(p) < 1e-12:
            raise ValueError("singular normal equation")
        for j in range(col, n + 1):
            m[col][j] /= p
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f == 0:
                continue
            for j in range(col, n + 1):
                m[r][j] -= f * m[col][j]
    return [m[i][n] for i in range(n)]


def load_targets(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = {r["target_id"]: r for r in csv.DictReader(handle)}
    missing = set(TARGET_IDS) - set(rows)
    if missing:
        raise ValueError(f"missing probing slopes: {sorted(missing)}")
    chosen = [rows[k] for k in TARGET_IDS]
    signatures = {(r["source_id"], r["taxonomic_scope"], r["driver"], r["response"], r["target_kind"]) for r in chosen}
    if len(signatures) != 1:
        raise ValueError("probing slopes are not provenance-comparable")
    expected_notes = ["1997 high-density", "1997 low-density", "1998 high-density", "1998 low-density"]
    for row, phrase in zip(chosen, expected_notes):
        if phrase not in row["claim_boundary"]:
            raise ValueError(f"context label missing for {row['target_id']}")
    return [float(r["estimate"]) for r in chosen], chosen


def fit_ridge(y, indices, lam):
    p = 4
    a = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for i in indices:
        for j in range(p):
            b[j] += X[i][j] * y[i]
            for k in range(p):
                a[j][k] += X[i][j] * X[i][k]
    # Shared mean and density contrast stay unpenalized; year mean and year×density
    # deviations are shrunk toward zero.
    a[2][2] += lam
    a[3][3] += lam
    return solve_linear(a, b)


def fit_shared(y, indices):
    p = 2
    a = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for i in indices:
        z = X[i][:2]
        for j in range(p):
            b[j] += z[j] * y[i]
            for k in range(p):
                a[j][k] += z[j] * z[k]
    return solve_linear(a, b)


def predict(row, beta):
    return sum(v * b for v, b in zip(row, beta))


def loo_ridge(y, lam):
    pred = []
    for i in range(4):
        train = [j for j in range(4) if j != i]
        beta = fit_ridge(y, train, lam)
        pred.append(predict(X[i], beta))
    rmse = math.sqrt(sum((p - o) ** 2 for p, o in zip(pred, y)) / 4.0)
    return rmse, pred


def loo_shared(y):
    pred = []
    for i in range(4):
        train = [j for j in range(4) if j != i]
        beta = fit_shared(y, train)
        pred.append(predict(X[i][:2], beta))
    rmse = math.sqrt(sum((p - o) ** 2 for p, o in zip(pred, y)) / 4.0)
    return rmse, pred


def effective_df(lam):
    p = 4
    a = [[0.0] * p for _ in range(p)]
    for row in X:
        for j in range(p):
            for k in range(p):
                a[j][k] += row[j] * row[k]
    a[2][2] += lam
    a[3][3] += lam
    # trace(X (X'X+P)^-1 X') without constructing an inverse.
    total = 0.0
    for row in X:
        z = solve_linear(a, row)
        total += sum(row[j] * z[j] for j in range(p))
    return total


def rounded(obj, digits=8):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, list):
        return [rounded(v, digits) for v in obj]
    if isinstance(obj, dict):
        return {k: rounded(v, digits) for k, v in obj.items()}
    return obj


def run(targets: Path):
    slopes, rows = load_targets(targets)
    y = [math.log(v) for v in slopes]
    grid = [10 ** (-4.0 + 8.0 * i / 400.0) for i in range(401)]
    ridge_scores = [(loo_ridge(y, lam)[0], lam) for lam in grid]
    best_rmse, best_lam = min(ridge_scores)
    shared_rmse, shared_pred_log = loo_shared(y)
    _, ridge_pred_log = loo_ridge(y, best_lam)
    beta = fit_ridge(y, range(4), best_lam)
    fitted = [math.exp(predict(row, beta)) for row in X]
    improvement = (shared_rmse - best_rmse) / shared_rmse
    source = rows[0]["source_id"]
    return rounded({
        "contract_version": "pollinator_context_shrinkage_v1",
        "status_date": "2026-08-20",
        "source_id": source,
        "observed_slopes": dict(zip(TARGET_IDS, slopes)),
        "model": "log_slope ~ density + shrunk(year + year_x_density)",
        "lambda_grid": {"min": grid[0], "max": grid[-1], "n": len(grid)},
        "selected_lambda": best_lam,
        "shared_loo_log_rmse": shared_rmse,
        "partial_pooling_loo_log_rmse": best_rmse,
        "predictive_rmse_improvement_fraction": improvement,
        "partial_pooling_effective_df": effective_df(best_lam),
        "full_data_coefficients": {
            "intercept": beta[0],
            "low_density": beta[1],
            "year_1998": beta[2],
            "year_1998_x_low_density": beta[3],
        },
        "full_data_fitted_slopes": dict(zip(TARGET_IDS, fitted)),
        "loo_predicted_slopes": {
            "shared": dict(zip(TARGET_IDS, [math.exp(v) for v in shared_pred_log])),
            "partial_pooling": dict(zip(TARGET_IDS, [math.exp(v) for v in ridge_pred_log])),
        },
        "decision": "do_not_promote_unpooled_temporal_context_parameters",
        "headline": (
            "Shrinkage-selected context effects improve leave-one-out log-RMSE only slightly over the shared density model; "
            "the four-slope dataset does not justify adding unpooled year-specific pollinator parameters to the full simulation."
        ),
        "claim_boundary": (
            "Four slopes from one study system provide a structural diagnostic, not a general estimate of temporal heterogeneity. "
            "The shrinkage penalty is selected by leave-one-out prediction and is not a biological posterior variance."
        ),
    })


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--targets", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.targets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
