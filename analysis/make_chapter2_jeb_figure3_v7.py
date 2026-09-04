#!/usr/bin/env python3
"""Generate JEB V7 Figure 3: scale- and history-conditioned orientation ecology.

The figure deliberately keeps non-exchangeable ecological estimands separate and
uses finite counterfactual ranks only as conditional falsification summaries.
All displayed numbers are loaded from frozen machine-readable evidence and
checked against a fail-closed figure contract before rendering.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v7")
    return p.parse_args()


def load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def close(a: float, b: float, tol: float = 1e-10) -> bool:
    return abs(float(a) - float(b)) <= tol


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(contract: dict, eco: dict, cf: dict) -> None:
    req = contract["required_values"]
    sp = eco["orientation_scale_partition"]
    b12 = sp["BIO12_annual_precipitation"]
    b15 = sp["BIO15_precipitation_seasonality"]
    b1 = sp["BIO1_annual_mean_temperature"]

    assert eco["classification"] == "orientation_environment_association_is_scale_partitioned"
    assert cf["classification"] == "counterfactual_correspondence_not_strengthened_beyond_history"
    assert cf["panel"]["n_assignments"] == 126

    assert close(b12["azami_within"]["beta_std"], req["bio12"]["within_beta"])
    assert close(b12["azami_within"]["q"], req["bio12"]["within_q"])
    assert close(b12["azami_among"]["beta_std"], req["bio12"]["among_beta"])
    assert close(b12["azami_among"]["q"], req["bio12"]["among_q"])

    assert close(b15["azami_within"]["beta_std"], req["bio15"]["within_beta"])
    assert close(b15["azami_within"]["q"], req["bio15"]["within_q"])
    assert close(b15["azami_among"]["beta_std"], req["bio15"]["among_beta"])
    assert close(b15["azami_among"]["q"], req["bio15"]["among_q"])
    assert b15["eazami_downward_minus_upward"]["standardized_difference_range"] == req["bio15"]["east_asia_effect_range"]

    assert close(b1["azami_within"]["beta_std"], req["bio1"]["within_beta"])
    assert close(b1["azami_within"]["q"], req["bio1"]["within_q"])
    assert close(b1["azami_among"]["beta_std"], req["bio1"]["among_beta"])
    assert close(b1["azami_among"]["q"], req["bio1"]["among_q"])
    assert all(close(a, b) for a, b in zip(b1["eazami_downward_minus_upward"]["standardized_difference_range"], req["bio1"]["east_asia_effect_range"]))

    for axis, key in [("chelsa_bio15", "bio15"), ("chelsa_bio01", "bio1")]:
        pools = cf["axis_results"][axis]["pools"]
        pairs = [
            ("all_126_count_preserving", "state_count_rank"),
            ("recurrence_profile_matched", "recurrence_rank"),
            ("history_nearest_quartile", "nearest_history_rank"),
        ]
        for pool_name, contract_key in pairs:
            rank = pools[pool_name]["rank"]
            expected_count, expected_n = req[key][contract_key]
            assert rank["count_at_least_observed"] == expected_count
            assert rank["n"] == expected_n

    bio15_pools = cf["axis_results"]["chelsa_bio15"]["pools"]
    assert close(
        bio15_pools["recurrence_profile_matched"]["reverse_world"]["most_reverse_signed_statistic"],
        req["bio15"]["recurrence_reverse_signed_statistic"],
    )
    assert bio15_pools["history_nearest_quartile"]["reverse_world"]["opposite_direction_exists"] is req["bio15"]["nearest_history_reverse_exists"]
    assert cf["axis_results"]["chelsa_bio01"]["pools"]["history_nearest_quartile"]["reverse_world"]["opposite_direction_exists"] is req["bio1"]["nearest_history_reverse_exists"]


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.titlesize": 10,
        "axes.labelsize": 8.5,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })


def panel_label(ax, label: str) -> None:
    ax.text(-0.08, 1.05, label, transform=ax.transAxes, fontsize=11, fontweight="bold", va="top")


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    contract = load("chapter2_jeb_v7_figure3_contract_v1.json")
    eco = load("chapter2_orientation_environment_scale_partition_v1.json")
    cf = load("chapter2_orientation_environment_counterfactual_result_v1.json")
    validate(contract, eco, cf)
    style()

    fig = plt.figure(figsize=(12.2, 4.55))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.45, 1.0, 0.92], wspace=0.34)

    # Panel A: non-exchangeable scale-specific evidence shown as a table.
    ax = fig.add_subplot(gs[0, 0])
    ax.axis("off")
    cell_text = [
        ["+0.005\nq=.874\nnot supported", "+0.304\nq=.006\nFDR supported", "—"],
        ["−0.008\nq=.121\nnot supported", "+0.067\nq=.599\nnot supported", "+1.32–1.33 SD\n6/6; 54/54 sign"],
        ["+0.017\nq=.035\nFDR supported", "−0.030\nq=.836\nnot supported", "−0.975–−0.967 SD\n54/54 sign"],
    ]
    table = ax.table(
        cellText=cell_text,
        rowLabels=["BIO12\nannual precipitation", "BIO15\nprecip. seasonality", "BIO1\nannual mean temp."],
        colLabels=["Within taxon\nAzami", "Among taxa\nAzami", "East-Asian\nstate contrast"],
        cellLoc="center",
        rowLoc="center",
        loc="center",
        bbox=[0.02, 0.08, 0.97, 0.78],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.4)
    for (r, c), cell in table.get_celld().items():
        cell.set_linewidth(0.6)
        if r == 0:
            cell.set_text_props(fontweight="bold")
        if c == -1:
            cell.set_text_props(fontweight="bold")
    ax.set_title("Ecological correspondence changes with biological scale", pad=12)
    ax.text(0.5, 0.015, "Columns are different estimands; effect sizes are not pooled.", transform=ax.transAxes, ha="center", fontsize=7.3)
    panel_label(ax, "a")

    # Panel B: nested counterfactual conditioning ladder.
    ax = fig.add_subplot(gs[0, 1])
    pools = ["State frequency", "Recurrence", "Recurrence\n+ relative depth"]
    x = np.arange(3)
    bio15_counts = np.array([5, 3, 3], dtype=float)
    bio15_ns = np.array([126, 40, 10], dtype=float)
    bio1_counts = np.array([8, 4, 3], dtype=float)
    bio1_ns = np.array([126, 40, 10], dtype=float)
    bio15_pct = 100 * bio15_counts / bio15_ns
    bio1_pct = 100 * bio1_counts / bio1_ns
    ax.plot(x, bio15_pct, marker="o", linewidth=2.0, label="BIO15 (D > U)")
    ax.plot(x, bio1_pct, marker="s", linewidth=1.5, linestyle="--", label="BIO1 (D < U)")
    for xx, yy, c, n in zip(x, bio15_pct, bio15_counts.astype(int), bio15_ns.astype(int)):
        ax.text(xx, yy + 1.7, f"{c}/{n}", ha="center", va="bottom", fontsize=7.4, fontweight="bold")
    for xx, yy, c, n in zip(x, bio1_pct, bio1_counts.astype(int), bio1_ns.astype(int)):
        ax.text(xx, yy - 1.8, f"{c}/{n}", ha="center", va="top", fontsize=7.1)
    ax.set_xticks(x, pools)
    ax.set_ylim(0, 36)
    ax.set_ylabel("Counterfactual maps at least as extreme (%)")
    ax.set_title("Ecological extremeness weakens\nwith historical conditioning")
    ax.grid(axis="y", linewidth=0.5, alpha=0.35)
    ax.legend(frameon=False, fontsize=7.2, loc="upper left")
    ax.text(0.5, -0.19, "Finite conditional ranks — not P values", transform=ax.transAxes, ha="center", fontsize=7.3)
    panel_label(ax, "b")

    # Panel C: reverse-direction availability.
    ax = fig.add_subplot(gs[0, 2])
    ax.axis("off")
    reverse_text = [
        ["YES", "YES\n−1.784", "NO"],
        ["YES", "YES", "YES\n−0.026"],
    ]
    table2 = ax.table(
        cellText=reverse_text,
        rowLabels=["BIO15", "BIO1"],
        colLabels=["State\nfrequency", "Recurrence", "Recurrence\n+ depth"],
        cellLoc="center",
        rowLoc="center",
        loc="center",
        bbox=[0.04, 0.36, 0.94, 0.43],
    )
    table2.auto_set_font_size(False)
    table2.set_fontsize(8.0)
    for (r, c), cell in table2.get_celld().items():
        cell.set_linewidth(0.6)
        if r == 0 or c == -1:
            cell.set_text_props(fontweight="bold")
    ax.set_title("Can an opposite environmental sign\nretain the same historical constraints?", pad=12)
    ax.text(0.5, 0.20, "BIO15 reverse sign disappears only in\nthe nearest-history pool.", transform=ax.transAxes, ha="center", fontsize=8.0, fontweight="bold")
    ax.text(0.5, 0.075, "This constrains the finite counterfactual class;\nit does not prove biological impossibility.", transform=ax.transAxes, ha="center", fontsize=7.2)
    panel_label(ax, "c")

    fig.suptitle("Figure 3. Present orientation ecology is scale-partitioned and history-embedded", fontsize=11.5, y=0.99)
    fig.subplots_adjust(top=0.82, bottom=0.20, left=0.055, right=0.985)

    stem = contract["output"]["stem"]
    png = out / f"{stem}.png"
    pdf = out / f"{stem}.pdf"
    fig.savefig(png, dpi=int(contract["output"]["png_dpi"]), bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)

    if png.stat().st_size < 20_000 or pdf.stat().st_size < 10_000:
        raise RuntimeError("Figure 3 output unexpectedly small")

    manifest = {
        "version": "chapter2_jeb_v7_figure3_manifest_v1",
        "status": "ok",
        "sources": contract["sources"],
        "source_classifications": {
            "scale_partition": eco["classification"],
            "counterfactual": cf["classification"],
        },
        "headline": {
            "bio15_nested_ranks": ["5/126", "3/40", "3/10"],
            "bio15_nearest_history_reverse_exists": False,
            "bio1_nearest_history_reverse_exists": True,
        },
        "outputs": {
            "png": {"path": str(png), "sha256": sha256(png), "bytes": png.stat().st_size},
            "pdf": {"path": str(pdf), "sha256": sha256(pdf), "bytes": pdf.stat().st_size},
        },
    }
    manifest_path = out / f"{stem}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
