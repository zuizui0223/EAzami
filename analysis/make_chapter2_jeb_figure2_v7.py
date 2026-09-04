#!/usr/bin/env python3
"""Generate the validated JEB V7 headline Figure 2.

The figure is fail-closed against frozen V7 evidence and separates topology
robustness from missing-state coverage sensitivity. Relative lineage depth is
strictly topology-only; no displayed fraction is a probability or independent
biological replicate frequency.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"

DARK = "#242424"
BLUE = "#4C78A8"
ORANGE = "#F2A541"
GREEN = "#5A9367"
GREY = "#777777"
LIGHT = "#D9DDE2"
PALE = "#F4F5F6"
RED = "#B04A4A"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, default=EVID / "chapter2_jeb_v7_figure2_contract_v1.json")
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v7")
    return p.parse_args()


def validate(contract: dict, hist: dict, paired: dict, coverage: dict) -> None:
    exp = contract["expected"]
    rec = hist["recurrence_and_depth"]
    assert rec["orientation"]["minimum_changes_ml"] == exp["minimum_changes"]["orientation_ml"]
    assert rec["orientation"]["minimum_changes_ufboot_range"] == exp["minimum_changes"]["orientation_ufboot_range"]
    assert rec["orientation"]["minimum_changes_ufboot_median"] == exp["minimum_changes"]["orientation_ufboot_median"]
    assert rec["phyllary_posture"]["minimum_changes"] == exp["minimum_changes"]["phyllary"]
    assert rec["stickiness"]["minimum_changes"] == exp["minimum_changes"]["stickiness"]
    assert rec["orientation"]["relative_depth_median_envelope"] == exp["depth_median_envelopes"]["orientation"]
    assert rec["phyllary_posture"]["relative_depth_median_envelope"] == exp["depth_median_envelopes"]["phyllary"]
    assert rec["stickiness"]["relative_depth_median_envelope"] == exp["depth_median_envelopes"]["stickiness"]
    assert rec["shared_transition_localization"].startswith("0/3")

    assert paired["classification"] == "paired_topology_depth_ordering_reproduced_under_frozen_runtime"
    p = {(r["deeper_candidate"], r["shallower_candidate"]): r for r in paired["pairwise_results"]}
    assert p[("phyllary", "stickiness")]["fraction_prespecified_deeper_direction"] == exp["paired_topology"]["phyllary_lt_stickiness"]
    assert p[("phyllary", "orientation")]["fraction_prespecified_deeper_direction"] == exp["paired_topology"]["phyllary_lt_orientation"]
    assert p[("orientation", "stickiness")]["fraction_prespecified_deeper_direction"] == exp["paired_topology"]["orientation_lt_stickiness"]
    assert paired["complete_lower_bound_ordering"]["fraction"] == exp["paired_topology"]["complete_ordering"]

    assert coverage["overall_classification"] == "unequal_depth_retained_against_matched_medians_but_strict_tail_overlap_remains"
    c = {r["comparison"]: r for r in coverage["comparison_results"]}
    assert c["phyllary_lt_orientation_median"]["fraction"] == exp["coverage_matched"]["phyllary_lt_orientation_median"]
    assert c["phyllary_lt_stickiness_5_5_median"]["fraction"] == exp["coverage_matched"]["phyllary_lt_stickiness_median"]
    assert c["phyllary_lt_orientation_q05"]["fraction"] == exp["coverage_matched"]["phyllary_lt_orientation_q05"]
    assert c["phyllary_lt_stickiness_5_5_q05"]["fraction"] == exp["coverage_matched"]["phyllary_lt_stickiness_5_5_q05"]
    assert c["phyllary_lt_stickiness_6_4_q05"]["fraction"] == exp["coverage_matched"]["phyllary_lt_stickiness_6_4_q05"]


def setup_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.titlesize": 9.0,
        "axes.labelsize": 8.0,
        "axes.edgecolor": DARK,
        "axes.linewidth": 0.8,
        "xtick.color": DARK,
        "ytick.color": DARK,
        "text.color": DARK,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def panel(ax, letter: str) -> None:
    ax.text(-0.16, 1.04, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom")


def save(fig, outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    png = outdir / "figure2_v7_mosaic_depth.png"
    pdf = outdir / "figure2_v7_mosaic_depth.pdf"
    fig.savefig(png, dpi=600, bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": "JEB V7 Figure 2"})
    plt.close(fig)
    return {"png": str(png), "pdf": str(pdf)}


def main() -> int:
    args = parse_args()
    contract = load_json(args.contract)
    hist = load_json(EVID / "chapter2_historical_differentiation_final_summary_v1.json")
    paired = load_json(EVID / "chapter2_depth_ordering_robustness_result_v1.json")
    coverage = load_json(EVID / "chapter2_depth_coverage_matched_sensitivity_result_v1.json")
    validate(contract, hist, paired, coverage)
    setup_style()

    fig = plt.figure(figsize=(7.2, 7.35))
    gs = fig.add_gridspec(
        3, 2,
        height_ratios=[1.0, 1.03, 0.62],
        left=0.13, right=0.98, top=0.96, bottom=0.06,
        hspace=0.72, wspace=0.62,
    )
    rec = hist["recurrence_and_depth"]
    traits = ["Orientation", "Phyllary", "Stickiness"]
    cols = [BLUE, ORANGE, GREEN]
    yy = np.arange(3)[::-1]

    ax = fig.add_subplot(gs[0, 0])
    values = [(4, 6, 5, 6, 20), (3, 3, 3, 3, 10), (5, 5, 5, 5, 13)]
    for y, (lo, hi, med, ml, n), col in zip(yy, values, cols):
        ax.hlines(y, lo, hi, color=col, lw=5, zorder=2)
        ax.plot(med, y, "o", mfc="white", mec=col, mew=1.5, ms=6, zorder=3)
        ax.plot(ml, y, "D", color=DARK, ms=4, zorder=4)
        ax.text(6.18, y, f"n={n}", va="center", fontsize=7, color=GREY)
    ax.set_yticks(yy, traits)
    ax.set_xlim(2.6, 6.72)
    ax.set_xlabel("Minimum unordered changes")
    ax.set_title("Minimum changes", pad=9)
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.text(0.02, 0.02, "line = UFBoot range   ○ median   ◆ ML", transform=ax.transAxes, fontsize=6.4, color=GREY)
    panel(ax, "a")

    ax = fig.add_subplot(gs[0, 1])
    envelopes = [
        tuple(rec["orientation"]["relative_depth_median_envelope"]),
        tuple(rec["phyllary_posture"]["relative_depth_median_envelope"]),
        tuple(rec["stickiness"]["relative_depth_median_envelope"]),
    ]
    for y, (lo, hi), col in zip(yy, envelopes, cols):
        ax.hlines(y, lo, hi, color=col, lw=5)
        ax.plot([lo, hi], [y, y], "|", color=DARK, ms=10, mew=1)
        ax.text((lo + hi) / 2, y + 0.17, f"{lo:.3f}–{hi:.3f}", ha="center", fontsize=6.8)
    ax.set_yticks(yy, traits)
    ax.set_xlim(0.66, 1.035)
    ax.set_ylim(-0.35, 2.38)
    ax.set_xlabel("Relative lineage depth (1 = terminal)")
    ax.set_title("Relative-depth envelopes", pad=9)
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.text(0.02, 0.02, "lower = deeper-permissive; topology only, not time", transform=ax.transAxes, fontsize=6.3, color=GREY)
    panel(ax, "b")

    ax = fig.add_subplot(gs[1, 0])
    labels = ["P<S", "P<O", "O<S", "P<O<S"]
    vals = np.array([1.000, 0.993, 0.905, 0.898]) * 100
    bars = ax.bar(np.arange(4), vals, width=0.64, color=[ORANGE, ORANGE, BLUE, DARK], alpha=0.9)
    ax.axhline(95, color=GREY, lw=0.8, ls="--")
    ax.axhline(80, color=LIGHT, lw=0.8, ls="--")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 1.4, f"{v:.1f}%", ha="center", fontsize=6.9)
    ax.set_xticks(np.arange(4), labels)
    ax.set_ylim(0, 106)
    ax.set_ylabel("Topologies retaining ordering (%)")
    ax.set_title("Paired topology ordering", pad=9)
    ax.text(0.02, 0.02, "P=phyllary  O=orientation  S=stickiness", transform=ax.transAxes, fontsize=6.3, color=GREY)
    panel(ax, "c")

    ax = fig.add_subplot(gs[1, 1])
    groups = ["O 7U/3D", "S 5/5", "S 6/4"]
    med = np.array([97.5, 96.5, 96.5])
    q05 = np.array([10.5, 11.0, 15.5])
    gy = np.arange(3)[::-1]
    h = 0.28
    ax.barh(gy + h/2, med, height=h, color=BLUE, label="phyllary < matched median")
    ax.barh(gy - h/2, q05, height=h, color=GREY, label="phyllary < matched q05")
    for y, v in zip(gy + h/2, med):
        ax.text(v + 1.2, y, f"{v:.1f}%", va="center", fontsize=6.7)
    for y, v in zip(gy - h/2, q05):
        ax.text(v + 1.2, y, f"{v:.1f}%", va="center", fontsize=6.7)
    ax.set_yticks(gy, groups)
    ax.set_xlim(0, 108)
    ax.set_xlabel("Selected topology realizations (%)")
    ax.set_title("Coverage-matched sensitivity", pad=9)
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.legend(frameon=False, fontsize=6.2, loc="lower right")
    ax.text(0.02, 0.02, "central ordering retained; strict deep tails overlap", transform=ax.transAxes, fontsize=6.3, color=RED)
    panel(ax, "d")

    ax = fig.add_subplot(gs[2, :])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.015, 0.18), 0.17, 0.64, facecolor=PALE, edgecolor=DARK, lw=0.8))
    ax.text(0.10, 0.61, "0 / 3", ha="center", va="center", fontsize=21, fontweight="bold")
    ax.text(0.10, 0.34, "pairs pass robust\nshared localization", ha="center", va="center", fontsize=6.8)
    ax.text(0.23, 0.68, "Mosaic historical assembly", fontsize=10.5, fontweight="bold", va="center")
    ax.text(0.23, 0.48, "Repeated components retain different central depth geometry and do not repeatedly\nlocalize to one shared branch pattern.", fontsize=7.7, va="center")
    ax.text(0.23, 0.24, "Boundary: not independent origins • not rates • not coverage independence • not genetic/developmental modularity", fontsize=6.4, color=GREY, va="center")
    panel(ax, "e")

    outputs = save(fig, args.output_dir)
    manifest = {
        "version": "chapter2_jeb_v7_figure2_manifest_v1",
        "contract": str(args.contract),
        "source_versions": {
            "historical_summary": hist["result_version"],
            "paired_depth": paired["version"],
            "coverage_sensitivity": coverage["version"],
        },
        "outputs": outputs,
        "scientific_boundary": "validated central unequal-depth ordering with strict coverage-matched tail overlap; topology-only, not time or rate",
    }
    (args.output_dir / "figure2_v7_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
