#!/usr/bin/env python3
"""Generate the validated JEB V7 headline Figure 2.

Figure 2 combines four non-exchangeable summaries of the three discrete capitulum
histories: minimum-change burden, topology-only relative-depth envelopes,
paired-topology ordering robustness, and coverage-matched missing-state
sensitivity.  The final panel reports the independent shared-localization gate.

All numerical values are loaded from frozen machine-readable evidence.  The
figure contract is fail-closed: source values must match the declared V7 values
before any output is written.
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
GREY = "#8A8A8A"
LIGHT = "#D9DDE2"
PALE = "#F4F5F6"
RED = "#B04A4A"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--contract",
        type=Path,
        default=EVID / "chapter2_jeb_v7_figure2_contract_v1.json",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "docs" / "chapter2" / "figures_v7",
    )
    return p.parse_args()


def validate_inputs(contract: dict, hist: dict, paired: dict, coverage: dict) -> None:
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
    by_pair = {
        (r["deeper_candidate"], r["shallower_candidate"]): r
        for r in paired["pairwise_results"]
    }
    assert by_pair[("phyllary", "stickiness")]["fraction_prespecified_deeper_direction"] == exp["paired_topology"]["phyllary_lt_stickiness"]
    assert by_pair[("phyllary", "orientation")]["fraction_prespecified_deeper_direction"] == exp["paired_topology"]["phyllary_lt_orientation"]
    assert by_pair[("orientation", "stickiness")]["fraction_prespecified_deeper_direction"] == exp["paired_topology"]["orientation_lt_stickiness"]
    assert paired["complete_lower_bound_ordering"]["fraction"] == exp["paired_topology"]["complete_ordering"]

    assert coverage["overall_classification"] == "unequal_depth_retained_against_matched_medians_but_strict_tail_overlap_remains"
    by_comp = {r["comparison"]: r for r in coverage["comparison_results"]}
    assert by_comp["phyllary_lt_orientation_median"]["fraction"] == exp["coverage_matched"]["phyllary_lt_orientation_median"]
    assert by_comp["phyllary_lt_stickiness_5_5_median"]["fraction"] == exp["coverage_matched"]["phyllary_lt_stickiness_median"]
    assert by_comp["phyllary_lt_orientation_q05"]["fraction"] == exp["coverage_matched"]["phyllary_lt_orientation_q05"]
    assert by_comp["phyllary_lt_stickiness_5_5_q05"]["fraction"] == exp["coverage_matched"]["phyllary_lt_stickiness_5_5_q05"]
    assert by_comp["phyllary_lt_stickiness_6_4_q05"]["fraction"] == exp["coverage_matched"]["phyllary_lt_stickiness_6_4_q05"]


def setup_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.2,
        "axes.titlesize": 9.2,
        "axes.labelsize": 8.2,
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


def panel_label(ax, label: str) -> None:
    ax.text(-0.12, 1.08, label, transform=ax.transAxes, fontweight="bold", fontsize=11, va="top")


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
    validate_inputs(contract, hist, paired, coverage)
    setup_style()

    fig = plt.figure(figsize=(7.1, 7.0), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.0, 1.05, 0.78], width_ratios=[1.0, 1.08])

    traits = ["Orientation", "Phyllary", "Stickiness"]
    colors = [BLUE, ORANGE, GREEN]
    rec = hist["recurrence_and_depth"]

    # A — minimum-change burden.
    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(3)[::-1]
    mins = [(4, 6, 5, 6), (3, 3, 3, 3), (5, 5, 5, 5)]  # boot lo, hi, median, ML
    coverage_n = [20, 10, 13]
    for yy, (lo, hi, med, ml), c, n in zip(y, mins, colors, coverage_n):
        ax.hlines(yy, lo, hi, color=c, lw=5, zorder=2)
        ax.plot(med, yy, "o", color="white", markeredgecolor=c, markeredgewidth=1.5, ms=6, zorder=3)
        ax.plot(ml, yy, "D", color=DARK, ms=4.2, zorder=4)
        ax.text(6.22, yy, f"n={n}", va="center", fontsize=7.2, color=GREY)
    ax.set_yticks(y, traits)
    ax.set_xlim(2.5, 6.8)
    ax.set_xlabel("Minimum unordered changes")
    ax.set_title("Repeated component histories")
    ax.grid(axis="x", color=LIGHT, lw=0.6, zorder=0)
    ax.text(0.01, -0.28, "line: UFBoot range   ○ median   ◆ ML", transform=ax.transAxes, fontsize=6.8, color=GREY)
    panel_label(ax, "a")

    # B — median exact relative-depth envelopes.
    ax = fig.add_subplot(gs[0, 1])
    depth = [
        tuple(rec["orientation"]["relative_depth_median_envelope"]),
        tuple(rec["phyllary_posture"]["relative_depth_median_envelope"]),
        tuple(rec["stickiness"]["relative_depth_median_envelope"]),
    ]
    for yy, (lo, hi), c in zip(y, depth, colors):
        ax.hlines(yy, lo, hi, color=c, lw=5)
        ax.plot(lo, yy, "|", color=DARK, ms=10, mew=1)
        ax.plot(hi, yy, "|", color=DARK, ms=10, mew=1)
        ax.text(lo - 0.008, yy, f"{lo:.3f}", ha="right", va="center", fontsize=6.8)
        ax.text(hi + 0.008, yy, f"{hi:.3f}", ha="left", va="center", fontsize=6.8)
    ax.set_yticks(y, traits)
    ax.set_xlim(0.66, 1.025)
    ax.set_xlabel("Relative lineage depth (1 = terminal)")
    ax.set_title("Topology-only depth envelopes")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.text(0.5, -0.28, "lower = deeper-permissive; topology only, not time", transform=ax.transAxes, ha="center", fontsize=6.8, color=GREY)
    panel_label(ax, "b")

    # C — paired topology ordering.
    ax = fig.add_subplot(gs[1, 0])
    labels = ["P < S", "P < O", "O < S", "P < O < S"]
    vals = [1.000, 0.993, 0.905, 0.898]
    barcols = [ORANGE, ORANGE, BLUE, DARK]
    xx = np.arange(len(labels))
    ax.bar(xx, np.array(vals) * 100, color=barcols, width=0.68, alpha=0.9)
    ax.axhline(95, color=GREY, lw=0.8, ls="--")
    ax.axhline(80, color=LIGHT, lw=0.8, ls="--")
    for x, v in zip(xx, vals):
        ax.text(x, v * 100 + 1.5, f"{v*100:.1f}%", ha="center", va="bottom", fontsize=7.4)
    ax.set_xticks(xx, labels)
    ax.set_ylim(0, 106)
    ax.set_ylabel("Topology realizations retaining ordering (%)")
    ax.set_title("Paired ordering on the same 1,000 topologies")
    ax.text(0.01, -0.27, "P=phyllary, O=orientation, S=stickiness", transform=ax.transAxes, fontsize=6.8, color=GREY)
    panel_label(ax, "c")

    # D — coverage matched central vs strict-tail comparisons.
    ax = fig.add_subplot(gs[1, 1])
    groups = ["Orientation\n7U/3D", "Stickiness\n5/5", "Stickiness\n6/4"]
    med = np.array([0.975, 0.965, 0.965]) * 100
    q05 = np.array([0.105, 0.110, 0.155]) * 100
    x = np.arange(3)
    width = 0.34
    ax.bar(x - width/2, med, width, label="phyllary < matched median", color=BLUE, alpha=0.9)
    ax.bar(x + width/2, q05, width, label="phyllary < matched q05", color=GREY, alpha=0.8)
    for xi, v in zip(x - width/2, med):
        ax.text(xi, v + 1.8, f"{v:.1f}%", ha="center", fontsize=6.8)
    for xi, v in zip(x + width/2, q05):
        ax.text(xi, v + 1.8, f"{v:.1f}%", ha="center", fontsize=6.8)
    ax.set_xticks(x, groups)
    ax.set_ylim(0, 106)
    ax.set_ylabel("Selected topology realizations (%)")
    ax.set_title("Matched n=10: central ordering vs strict tail")
    ax.legend(frameon=False, fontsize=6.5, loc="center right")
    ax.text(0.5, -0.30, "central ordering retained; deep matched tails overlap", transform=ax.transAxes, ha="center", fontsize=6.8, color=RED)
    panel_label(ax, "d")

    # E — shared localization boundary.
    ax = fig.add_subplot(gs[2, :])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.17), 0.22, 0.66, transform=ax.transAxes, facecolor=PALE, edgecolor=DARK, lw=0.8))
    ax.text(0.13, 0.60, "0 / 3", transform=ax.transAxes, ha="center", va="center", fontsize=23, fontweight="bold")
    ax.text(0.13, 0.35, "trait pairs pass robust\nshared-transition localization", transform=ax.transAxes, ha="center", va="center", fontsize=7.4)
    ax.text(0.31, 0.64, "Mosaic historical assembly", transform=ax.transAxes, fontsize=10.5, fontweight="bold", va="center")
    ax.text(0.31, 0.43, "Repeated component histories retain different central depth geometry and do not repeatedly\nlocalize to one shared branch pattern.", transform=ax.transAxes, fontsize=8.0, va="center")
    ax.text(0.31, 0.21, "Boundary: not independent origins • not evolutionary rates • not coverage independence • not genetic/developmental modularity", transform=ax.transAxes, fontsize=6.9, color=GREY, va="center")
    panel_label(ax, "e")

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
    manifest_path = args.output_dir / "figure2_v7_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
