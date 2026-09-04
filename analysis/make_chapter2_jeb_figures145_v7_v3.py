#!/usr/bin/env python3
"""Final layout renderer for V7 Figures 1, 4 and 5.

Delegates frozen validation and Figures 1/4 to prior renderers; only wraps the
Figure 5 interpretation statement more tightly after visual QA. Scientific
values and claim boundaries are unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import make_chapter2_jeb_figures145_v7 as base
import make_chapter2_jeb_figures145_v7_v2 as v2


def make_figure5_v3(contract: dict, hist: dict, out: Path, dpi: int) -> dict:
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
        ax.text(0.5, y, txt, transform=ax.transAxes, ha="center", va="center", fontsize=6.8, linespacing=1.12, color="white" if col != base.ORANGE else base.DARK, fontweight="bold")
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
    ax.add_patch(Rectangle((0.02, 0.08), 0.96, 0.84, transform=ax.transAxes, facecolor="#F7F7F7", edgecolor=base.DARK, lw=1.0))
    ax.text(0.5, 0.72, "Phenotypic assembly is", transform=ax.transAxes, ha="center", fontsize=8.8, fontweight="bold", color=base.BLUE)
    ax.text(0.5, 0.59, "identifiable farther", transform=ax.transAxes, ha="center", fontsize=8.8, fontweight="bold", color=base.BLUE)
    ax.text(0.5, 0.43, "than one recurring coarse", transform=ax.transAxes, ha="center", fontsize=8.8, fontweight="bold", color=base.RED)
    ax.text(0.5, 0.30, "historical cause", transform=ax.transAxes, ha="center", fontsize=8.8, fontweight="bold", color=base.RED)
    ax.text(0.5, 0.145, "0/324 and 0/21 bound tested coarse explanations;\nnot environmental irrelevance or local land connectivity.", transform=ax.transAxes, ha="center", fontsize=5.9, color=base.MID, linespacing=1.2)
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
        "figure4": v2.make_figure4_v2(contract, hist, rank, claims, a.output_dir, dpi),
        "figure5": make_figure5_v3(contract, hist, a.output_dir, dpi),
    }
    manifest = {
        "version": "chapter2_jeb_v7_figures145_manifest_v3",
        "status": "ok",
        "layout_revision": "final visual-QA layout; Figure 5 conclusion wrapped within panel",
        "scientific_values_changed": False,
        "outputs": outputs,
        "claim_boundary": "Frozen evidence display only; no historical climatic causation, adaptation, selection, ancestral-area probability or environmental-irrelevance claim."
    }
    (a.output_dir / "figures145_v7_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
