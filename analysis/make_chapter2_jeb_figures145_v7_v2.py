#!/usr/bin/env python3
"""Layout-v2 renderer for V7 Figures 1, 4 and 5.

Scientific validation and Figure 1 are delegated to the frozen v1 generator.
This renderer changes only Figure 4/5 composition after visual QA; numerical
values, source artifacts, decisions and claim ceilings are unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import make_chapter2_jeb_figures145_v7 as base


def make_figure4_v2(contract: dict, hist: dict, rank: dict, claims: dict, out: Path, dpi: int) -> dict:
    fig, axs = plt.subplots(2, 2, figsize=(8.2, 6.8))
    fig.subplots_adjust(hspace=0.50, wspace=0.34, top=0.90, bottom=0.11, left=0.10, right=0.98)

    ax = axs[0, 0]
    ax.set_xlim(0.82, 0.70)
    ax.set_ylim(-0.6, 1.1)
    ax.hlines(0, 0.82, 0.70, color=base.LIGHT, lw=5)
    ax.hlines(0, 0.79, 0.74, color=base.BLUE, lw=8)
    ax.plot([0.79, 0.74], [0, 0], "|", color=base.DARK, ms=14, mew=1.2)
    ax.text(0.765, 0.20, "central 0.79–0.74 Ma", ha="center", fontsize=8, fontweight="bold")
    ax.text(0.765, -0.30, "94 chronology pairs × 4 palaeolocation regions = 376 scenarios", ha="center", fontsize=7.4)
    ax.set_yticks([])
    ax.set_xlabel("Ma before present")
    ax.set_title("Only one orientation event reaches the full historical gate")
    base.panel(ax, "a")

    ax = axs[0, 1]
    regions = ["Taiwan", "Ryukyu", "Southern Japan", "East-Asia core"]
    keys = ["taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor"]
    counts = np.array([contract["figure4"]["region_rank1_counts"][k] for k in keys])
    pct = 100 * counts / 94
    bars = ax.bar(np.arange(4), pct, color=[base.MID, base.GREEN, base.BLUE, base.PURPLE], width=0.66)
    ax.axhline(75, color=base.RED, ls="--", lw=1)
    for b, c, p in zip(bars, counts, pct):
        ax.text(b.get_x()+b.get_width()/2, p+1.8, f"{c}/94", ha="center", fontsize=7)
    ax.set_xticks(np.arange(4), regions, rotation=18, ha="right")
    ax.set_ylim(0, 84)
    ax.set_ylabel("Ranked first across chronology grid (%)")
    ax.set_title("Southern Japan leads descriptively, not dominantly")
    ax.text(0.02, 0.95, "75% dominance gate", transform=ax.transAxes, color=base.RED, fontsize=6.5, va="top")
    ax.text(
        0.98, 0.82,
        "Pairwise ordering\nS. Japan > Taiwan 61/94\n> Ryukyu 61/94; > core 64/94",
        transform=ax.transAxes, ha="right", va="top", fontsize=6.3, color=base.MID,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.90, pad=2.0),
    )
    base.panel(ax, "b")

    ax = axs[1, 0]
    ax.axis("off")
    ax.set_title("Central chronology has a coherent but descriptive trajectory", pad=10)
    traj = [("BIO1", "↓", "4/4"), ("BIO4", "↓", "4/4"), ("BIO15", "↓", "4/4"), ("BIO12", "↑", "3/4")]
    for i, (bio, arrow, n) in enumerate(traj):
        y = 0.82 - i*0.20
        ax.add_patch(Rectangle((0.08, y-0.06), 0.22, 0.12, transform=ax.transAxes, facecolor=base.PALE, edgecolor=base.LIGHT))
        ax.text(0.19, y, bio, transform=ax.transAxes, ha="center", va="center", fontweight="bold")
        ax.text(0.48, y, arrow, transform=ax.transAxes, ha="center", va="center", fontsize=18, color=base.BLUE if arrow == "↑" else base.ORANGE)
        ax.text(0.72, y, n + " regions", transform=ax.transAxes, va="center", fontsize=8)
    ax.text(0.50, 0.03, "Direction at 0.79–0.74 Ma only; not robust historical-trigger evidence.", transform=ax.transAxes, ha="center", fontsize=6.6, color=base.MID)
    base.panel(ax, "c")

    ax = axs[1, 1]
    labels = ["Overall", "Taiwan", "Ryukyu", "S. Japan", "E-Asia core"]
    vals = [26.3, 21.3, 9.6, 43.6, 30.9]
    nums = ["99/376", "20/94", "9/94", "41/94", "29/94"]
    bars = ax.barh(np.arange(5)[::-1], vals, color=[base.DARK, base.MID, base.GREEN, base.BLUE, base.PURPLE], height=0.55)
    ax.axvline(75, color=base.RED, ls="--", lw=1)
    for b, v, n in zip(bars, vals, nums):
        ax.text(v+1.5, b.get_y()+b.get_height()/2, f"{n} ({v:.1f}%)", va="center", fontsize=6.6)
    ax.set_yticks(np.arange(5)[::-1], labels)
    ax.set_xlim(0, 86)
    ax.set_xlabel("Scenarios matching current U→D regime (%)")
    ax.set_title("Current BIO15↑ + BIO1↓ regime does not persist at origin")
    ax.text(0.02, -0.23, "Central chronology fails in 4/4 regions because BIO15 decreases, opposite the current U→D direction.", transform=ax.transAxes, fontsize=6.4, color=base.MID)
    base.panel(ax, "d")

    fig.suptitle("Figure 4. Bounded orientation history: tendency versus uncertainty", fontsize=11.5)
    return base.save(fig, out, "figure4_v7_bounded_history", dpi)


def make_figure5_v2(contract: dict, hist: dict, out: Path, dpi: int) -> dict:
    fig = plt.figure(figsize=(8.6, 6.7))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.45, 0.75], width_ratios=[1.65, 0.78, 0.78], hspace=0.42, wspace=0.34)

    ax = fig.add_subplot(gs[:, 0])
    ax.axis("off")
    display = [
        "Configuration diversity\nresolved",
        "Repeated minimum histories\nresolved for three traits",
        "Relative evolutionary depth\nresolved with topology + coverage bounds",
        "Present orientation ecology\nscale / history / transition linked",
        "Shared localized history\npartial",
        "Calendar-linked trait events\nsparse",
        "Recurring historical cause\nnot identified",
    ]
    widths = [0.94, 0.92, 0.89, 0.86, 0.82, 0.78, 0.74]
    colors = [base.BLUE, base.BLUE, base.BLUE, base.GREEN, base.MID, base.ORANGE, base.RED]
    for i, (txt, w, col) in enumerate(zip(display, widths, colors)):
        y = 0.91 - i*0.125
        x = 0.5 - w/2
        ax.add_patch(Rectangle((x, y-0.049), w, 0.098, transform=ax.transAxes, facecolor=col, alpha=0.82, edgecolor="white"))
        ax.text(0.5, y, txt, transform=ax.transAxes, ha="center", va="center", fontsize=6.8, linespacing=1.12, color="white" if col not in {base.ORANGE} else base.DARK, fontweight="bold")
    ax.text(0.5, 0.015, "Increasing historical specificity → fewer directly identifiable links", transform=ax.transAxes, ha="center", fontsize=7, color=base.MID)
    ax.set_title("Identifiability narrows from assembly to cause", pad=10)
    base.panel(ax, "a")

    ax = fig.add_subplot(gs[0, 1])
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 0.10), 0.90, 0.80, transform=ax.transAxes, facecolor=base.PALE, edgecolor=base.DARK, lw=0.8))
    ax.text(0.5, 0.68, "0 / 324", transform=ax.transAxes, ha="center", fontsize=22, fontweight="bold", color=base.RED)
    ax.text(0.5, 0.49, "robust climate\nevent-level classes", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.25, "17 BIOCLIM variables\n6 dated lineage contexts\n15,472 scenario × variable tests", transform=ax.transAxes, ha="center", fontsize=6.6, color=base.MID)
    ax.set_title("Broader climate diagnostic")
    base.panel(ax, "b")

    ax = fig.add_subplot(gs[0, 2])
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 0.10), 0.90, 0.80, transform=ax.transAxes, facecolor=base.PALE, edgecolor=base.DARK, lw=0.8))
    ax.text(0.5, 0.68, "0 / 21", transform=ax.transAxes, ha="center", fontsize=22, fontweight="bold", color=base.RED)
    ax.text(0.5, 0.49, "robust sea-level\nevent-metric classes", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.27, "3 representative clades\n× 7 metrics", transform=ax.transAxes, ha="center", fontsize=7, color=base.MID)
    ax.set_title("Global eustatic diagnostic")
    base.panel(ax, "c")

    ax = fig.add_subplot(gs[1, 1:])
    ax.axis("off")
    ax.add_patch(Rectangle((0.02, 0.10), 0.96, 0.80, transform=ax.transAxes, facecolor="#F7F7F7", edgecolor=base.DARK, lw=1.0))
    ax.text(0.5, 0.68, "Phenotypic assembly is identifiable farther", transform=ax.transAxes, ha="center", fontsize=9.7, fontweight="bold", color=base.BLUE)
    ax.text(0.5, 0.49, "than one recurring coarse historical cause", transform=ax.transAxes, ha="center", fontsize=9.7, fontweight="bold", color=base.RED)
    ax.text(0.5, 0.24, "0/324 and 0/21 bound the tested coarse explanations.\nThey do not imply environmental irrelevance or reconstruct local land connectivity.", transform=ax.transAxes, ha="center", fontsize=6.3, color=base.MID, linespacing=1.25)
    base.panel(ax, "d")

    fig.suptitle("Figure 5. Historical identifiability ceiling", fontsize=11.5, y=0.98)
    return base.save(fig, out, "figure5_v7_identifiability_ceiling", dpi)


def main() -> int:
    a = base.args()
    contract = base.load_json(a.contract)
    radiation = base.load_json(base.EVID / "japan_cirsium_origin_meta_analysis_v1.json")
    scaffold = base.load_json(base.EVID / "japan38_comp1061_primary_tree_acceptance_v1.json")
    seed = base.load_csv(base.EVID / "japan38_nmns_capitulum_trait_seed_v1.csv")
    extension = base.load_csv(base.EVID / "japan38_nmns_capitulum_trait_seed_extension_v2.csv")
    combos = base.load_json(base.EVID / "japan38_authority_module_combinations_v1.json")
    hist = base.load_json(base.EVID / "chapter2_historical_differentiation_final_summary_v1.json")
    rank = base.load_json(base.EVID / "chapter2_orientation_origin_region_ranking_result_v1.json")
    claims = base.load_json(base.EVID / "chapter2_current_claims_h1_h4_v1.json")
    rows = base.validate_all(contract, radiation, scaffold, seed, extension, combos, hist, rank, claims)
    base.style()
    dpi = int(contract["output"]["png_dpi"])
    outputs = {
        "figure1": base.make_figure1(contract, rows, scaffold, combos, a.output_dir, dpi),
        "figure4": make_figure4_v2(contract, hist, rank, claims, a.output_dir, dpi),
        "figure5": make_figure5_v2(contract, hist, a.output_dir, dpi),
    }
    manifest = {
        "version": "chapter2_jeb_v7_figures145_manifest_v2",
        "status": "ok",
        "layout_revision": "figure4 annotation separation + figure5 wrapped identifiability hierarchy",
        "scientific_values_changed": False,
        "outputs": outputs,
        "claim_boundary": "Frozen evidence display only; no historical climatic causation, adaptation, selection, ancestral-area probability or environmental-irrelevance claim."
    }
    (a.output_dir / "figures145_v7_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
