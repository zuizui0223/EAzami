#!/usr/bin/env python3
"""Generate the active JEB V6 decision-level figure package.

V6 is the historical-differentiation paper. It deliberately excludes Chapter 3
and does not use present-day colour/environment results to determine the main
historical conclusion.
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

DARK = "#222222"
BLUE = "#3F6F9F"
TEAL = "#3C8476"
GOLD = "#B9872F"
RED = "#A34C4C"
MID = "#777777"
LIGHT = "#D9DEE3"
PALE = "#F5F6F7"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v6")
    return p.parse_args()


def load_json(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.titlesize": 10,
        "axes.labelsize": 8.5,
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


def panel(ax, label: str) -> None:
    ax.text(-0.10, 1.05, label, transform=ax.transAxes, fontweight="bold", fontsize=11, va="top")


def save(fig, out: Path, stem: str) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    png = out / f"{stem}.png"
    pdf = out / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)
    return [png, pdf]


def figure1(out: Path, summary: dict) -> list[Path]:
    fig, axes = plt.subplots(1, 4, figsize=(13.2, 3.5), gridspec_kw={"width_ratios": [1.0, 1.15, 1.35, 0.9]})
    rec = summary["recurrence_and_depth"]
    traits = ["Orientation", "Phyllary", "Stickiness"]
    keys = ["orientation", "phyllary_posture", "stickiness"]
    cols = [BLUE, GOLD, TEAL]
    y = np.arange(3)[::-1]

    ax = axes[0]
    cov = [rec[k]["resolved_concepts"] for k in keys]
    ax.barh(y, cov, color=cols, alpha=0.85)
    ax.set_yticks(y, traits)
    ax.set_xlim(0, 22)
    ax.set_xlabel("Resolved concepts")
    ax.set_title("Trait-state coverage")
    for yy, n in zip(y, cov):
        ax.text(n + 0.3, yy, str(n), va="center")
    panel(ax, "a")

    ax = axes[1]
    mins = [
        (4, 6, rec["orientation"]["minimum_changes_ml"]),
        (3, 3, 3),
        (5, 5, 5),
    ]
    for yy, (lo, hi, ml), c in zip(y, mins, cols):
        ax.hlines(yy, lo, hi, color=c, lw=5)
        ax.plot(ml, yy, "D", color=DARK, ms=4)
        ax.text(hi + 0.12, yy, f"{lo}–{hi}", va="center", fontsize=7.5)
    ax.set_yticks(y, traits)
    ax.set_xlim(0, 6.8)
    ax.set_xlabel("Minimum unordered changes")
    ax.set_title("Repeated differentiation")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    panel(ax, "b")

    ax = axes[2]
    depth = [tuple(rec[k]["relative_depth_median_envelope"]) for k in keys]
    for yy, (lo, hi), c in zip(y, depth, cols):
        ax.hlines(yy, lo, hi, color=c, lw=5)
        ax.plot((lo + hi) / 2, yy, "o", color=c, ms=5)
        ax.text(lo - 0.012, yy, f"{lo:.3f}", ha="right", va="center", fontsize=7)
        ax.text(hi + 0.012, yy, f"{hi:.3f}", ha="left", va="center", fontsize=7)
    ax.set_yticks(y, traits)
    ax.set_xlim(0.64, 1.03)
    ax.set_xlabel("Relative lineage depth (1 = terminal)")
    ax.set_title("Unequal historical depth")
    ax.text(0.5, -0.23, "Topology only — not calendar time", transform=ax.transAxes, ha="center", color=MID, fontsize=7.2)
    panel(ax, "c")

    ax = axes[3]
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.08, 0.50), 0.84, 0.30, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.69, "0 / 3", transform=ax.transAxes, ha="center", va="center", fontsize=22, fontweight="bold")
    ax.text(0.5, 0.57, "trait pairs pass robust\nshared localization", transform=ax.transAxes, ha="center", va="center", fontsize=8)
    ax.text(0.5, 0.28, "No simple synchronized\ncapitulum history", transform=ax.transAxes, ha="center", fontsize=9, fontweight="bold")
    ax.text(0.5, 0.12, "≠ complete independence", transform=ax.transAxes, ha="center", fontsize=7.5, color=MID)
    panel(ax, "d")

    fig.suptitle("Figure 1. Capitulum modules repeatedly differentiated at unequal evolutionary depths", fontsize=11, y=1.02)
    return save(fig, out, "figure1_recurrence_depth")


def figure2(out: Path, summary: dict) -> list[Path]:
    cal = summary["calendar_identifiability"]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.7), gridspec_kw={"width_ratios": [1.4, 1.2, 1.0]})

    ax = axes[0]
    modules = ["Orientation", "Phyllary", "Stickiness", "Colour"]
    stages = ["history", "depth", "calendar", "paleolocation", "environment"]
    mat = np.array([
        [1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [1, 0.5, 0.5, 0, 0],
    ])
    cmap = matplotlib.colors.ListedColormap(["#ECEFF2", "#D9C47E", "#5B8FA8"])
    norm = matplotlib.colors.BoundaryNorm([-0.1, 0.25, 0.75, 1.1], cmap.N)
    ax.imshow(mat, aspect="auto", cmap=cmap, norm=norm)
    ax.set_xticks(range(len(stages)), stages, rotation=35, ha="right")
    ax.set_yticks(range(len(modules)), modules)
    ax.set_title("Historical evidence funnel")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            label = "✓" if mat[i, j] == 1 else ("conditional" if mat[i, j] == 0.5 else "—")
            ax.text(j, i, label, ha="center", va="center", fontsize=8, color=DARK)
    panel(ax, "a")

    ax = axes[1]
    labels = ["Full trait-event gate", "Conditional colour envelopes", "Dated sister contrasts", "Range ages not trait ages"]
    vals = [
        cal["trait_transitions_with_calendar_paleolocation_environment_gate"],
        cal["conditional_colour_branch_envelopes"],
        cal["dated_sister_contrasts_not_transitions"],
        cal["dated_range_processes_trait_age_unlinked"],
    ]
    y = np.arange(len(labels))[::-1]
    ax.barh(y, vals, color=[BLUE, GOLD, MID, MID], alpha=0.85)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 4.5)
    ax.set_xlabel("Number of public historical items")
    ax.set_title("Calendar identifiability")
    for yy, v in zip(y, vals):
        ax.text(v + 0.08, yy, str(v), va="center")
    panel(ax, "b")

    ax = axes[2]
    ax.axis("off")
    ax.text(0.5, 0.74, "Repeated trait history", transform=ax.transAxes, ha="center", fontsize=12, fontweight="bold", color=TEAL)
    ax.text(0.5, 0.56, "≫", transform=ax.transAxes, ha="center", fontsize=20)
    ax.text(0.5, 0.39, "Repeated historical cause", transform=ax.transAxes, ha="center", fontsize=12, fontweight="bold", color=RED)
    ax.text(0.5, 0.17, "No additional machine-readable\ndated Japan38 tree recovered", transform=ax.transAxes, ha="center", fontsize=8, color=MID)
    panel(ax, "c")

    fig.suptitle("Figure 2. Calendar-time identifiability is the main historical bottleneck", fontsize=11, y=1.02)
    return save(fig, out, "figure2_calendar_identifiability")


def figure3(out: Path, summary: dict, orient: dict) -> list[Path]:
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.8))

    ax = axes[0, 0]
    ax.axis("off")
    ax.plot([0.10, 0.90], [0.52, 0.52], color=DARK, lw=2, transform=ax.transAxes)
    for x, c in [(0.10, BLUE), (0.50, RED), (0.90, BLUE)]:
        ax.plot(x, 0.52, "o", color=c, ms=8, transform=ax.transAxes)
    ax.text(0.10, 0.67, "C. morii split\n0.79 Ma\n0.43–1.18", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.50, 0.31, "candidate U→D\nstem", transform=ax.transAxes, ha="center", fontsize=8, fontweight="bold")
    ax.text(0.90, 0.67, "Japan–Taiwan core\n0.74 Ma\n0.60–0.87", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.08, "94 chronology pairs × 4 regions = 376 scenarios", transform=ax.transAxes, ha="center", fontsize=7.5, color=MID)
    ax.set_title("Bounded orientation event")
    panel(ax, "a")

    ax = axes[0, 1]
    variables = ["BIO1", "BIO4", "BIO12", "BIO15"]
    regions = ["taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor"]
    signs = np.zeros((4, 4))
    for i, var in enumerate(variables):
        for j, reg in enumerate(regions):
            delta = orient["variables"][var]["central_0_79_to_0_74_ma"][reg]["delta"]
            signs[i, j] = 1 if delta > 0 else -1 if delta < 0 else 0
    cmap = matplotlib.colors.ListedColormap(["#5B8FA8", "#EEEEEE", "#C57A57"])
    norm = matplotlib.colors.BoundaryNorm([-1.1, -0.1, 0.1, 1.1], cmap.N)
    ax.imshow(signs, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(4), ["Taiwan", "Ryukyu", "S Japan", "E Asia"], rotation=30, ha="right")
    ax.set_yticks(range(4), variables)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, "↑" if signs[i, j] > 0 else "↓", ha="center", va="center", fontsize=12)
    ax.set_title("Central 0.79→0.74 Ma tendency")
    ax.text(0.5, -0.27, "Illustrative only — does not survive full chronology envelope", transform=ax.transAxes, ha="center", fontsize=7.2, color=RED)
    panel(ax, "b")

    ax = axes[1, 0]
    gates = ["signed\ndirection", "level", "absolute\nchange", "variability"]
    fail = np.zeros((4, 4))
    ax.imshow(fail, cmap=matplotlib.colors.ListedColormap(["#E6E8EB"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(4), gates)
    ax.set_yticks(range(4), variables)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, "0", ha="center", va="center", fontweight="bold", color=RED)
    ax.set_title("Full chronology × palaeolocation robust gate")
    ax.text(0.5, -0.20, "No variable passes any robust event-class gate", transform=ax.transAxes, ha="center", fontsize=7.5)
    panel(ax, "c")

    ax = axes[1, 1]
    reg_pretty = ["Taiwan", "Ryukyu", "S Japan", "E Asia"]
    level = [orient["variables"]["BIO1"]["regional_median_percentiles"][r]["level_mean"] for r in regions]
    var = [orient["variables"]["BIO1"]["regional_median_percentiles"][r]["temporal_sd"] for r in regions]
    x = np.arange(4)
    ax.plot(x, level, "o-", label="BIO1 level", color=BLUE)
    ax.plot(x, var, "o-", label="BIO1 variability", color=GOLD)
    ax.axhline(0.05, color=LIGHT, lw=0.8)
    ax.axhline(0.95, color=LIGHT, lw=0.8)
    ax.set_xticks(x, reg_pretty, rotation=25, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Median matched-window percentile")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("Strongest sub-threshold tendency")
    ax.text(0.5, -0.28, "de Boer sea level: 94/94 chronologies; 0 robust metrics", transform=ax.transAxes, ha="center", fontsize=7.2, color=MID)
    panel(ax, "d")

    fig.suptitle("Figure 3. A clean central-date story disappears under historical uncertainty", fontsize=11, y=1.01)
    return save(fig, out, "figure3_orientation_uncertainty")


def figure4(out: Path, atlas: dict, sea: dict) -> list[Path]:
    fig, axes = plt.subplots(1, 4, figsize=(13.0, 3.6), gridspec_kw={"width_ratios": [1.0, 1.0, 1.0, 1.1]})

    ax = axes[0]
    vals = [atlas["inputs"]["n_bioclim_variables"], atlas["inputs"]["n_dated_lineage_contexts"], len(atlas["inputs"]["representative_clade_groups"])]
    labels = ["BIOCLIM\nvariables", "dated\ncontexts", "clade\ngroups"]
    ax.bar(range(3), vals, color=[BLUE, GOLD, TEAL], alpha=0.85)
    ax.set_xticks(range(3), labels)
    ax.set_title("Lineage-level atlas")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.3, str(v), ha="center")
    ax.text(0.5, -0.24, "15,472 scenario × variable tests", transform=ax.transAxes, ha="center", fontsize=7.5)
    panel(ax, "a")

    ax = axes[1]
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.10, 0.50), 0.80, 0.30, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.68, "0 / 324", transform=ax.transAxes, ha="center", fontsize=22, fontweight="bold", color=RED)
    ax.text(0.5, 0.56, "robust climate event classes", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.28, "Recurring climate\ncandidates = 0", transform=ax.transAxes, ha="center", fontsize=10, fontweight="bold")
    panel(ax, "b")

    ax = axes[2]
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.10, 0.50), 0.80, 0.30, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.68, "0 / 21", transform=ax.transAxes, ha="center", fontsize=22, fontweight="bold", color=RED)
    ax.text(0.5, 0.56, "robust sea-level event classes", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.28, "Recurring global sea-level\ncandidates = 0", transform=ax.transAxes, ha="center", fontsize=9.5, fontweight="bold")
    panel(ax, "c")

    ax = axes[3]
    ax.axis("off")
    ax.text(0.5, 0.76, "What this constrains", transform=ax.transAxes, ha="center", fontsize=10, fontweight="bold")
    ax.text(0.5, 0.58, "one universal coarse\nclimate/eustatic regime", transform=ax.transAxes, ha="center", fontsize=10, color=RED)
    ax.text(0.5, 0.36, "What remains open", transform=ax.transAxes, ha="center", fontsize=10, fontweight="bold")
    ax.text(0.5, 0.18, "local fragmentation • connectivity\nbiotic interactions • lineage-specific exposure", transform=ax.transAxes, ha="center", fontsize=8)
    panel(ax, "d")

    fig.suptitle("Figure 4. Broader dated lineage contexts do not recover one recurring coarse trigger", fontsize=11, y=1.02)
    return save(fig, out, "figure4_repeated_trigger_ceiling")


def figure5(out: Path, summary: dict) -> list[Path]:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.1), gridspec_kw={"width_ratios": [1.35, 1.0]})

    ax = axes[0]
    ax.axis("off")
    rungs = [
        (0.84, "1  Recurrence", "strong", TEAL),
        (0.68, "2  Relative depth", "strong", TEAL),
        (0.52, "3  Shared-history test", "0/3 robust", GOLD),
        (0.36, "4  Calendar event placement", "sparse: 1 full-gate event", GOLD),
        (0.20, "5  Recurring historical trigger", "not identified", RED),
    ]
    for y, left, right, c in rungs:
        ax.add_patch(plt.Rectangle((0.05, y - 0.055), 0.90, 0.10, facecolor=PALE, edgecolor=c, lw=1.5, transform=ax.transAxes))
        ax.text(0.09, y, left, transform=ax.transAxes, va="center", fontweight="bold")
        ax.text(0.91, y, right, transform=ax.transAxes, va="center", ha="right", color=c)
    ax.set_title("Evidence ladder")
    panel(ax, "a")

    ax = axes[1]
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.05, 0.55), 0.90, 0.30, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.76, "FINAL CLASSIFICATION", transform=ax.transAxes, ha="center", fontsize=8, color=MID)
    ax.text(0.5, 0.66, "Repeated differentiation\nresolved", transform=ax.transAxes, ha="center", fontsize=12, fontweight="bold", color=TEAL)
    ax.text(0.5, 0.48, "but", transform=ax.transAxes, ha="center", fontsize=9)
    ax.text(0.5, 0.36, "recurring tested historical\ntrigger not identified", transform=ax.transAxes, ha="center", fontsize=11, fontweight="bold", color=RED)
    ax.text(0.5, 0.13, "Not adaptation • not environmental irrelevance\nnot exact transition ages • not local land bridges", transform=ax.transAxes, ha="center", fontsize=7.5, color=MID)
    ax.set_title("Public-data endpoint")
    panel(ax, "b")

    fig.suptitle("Figure 5. History is substantially better resolved than historical cause", fontsize=11, y=1.02)
    return save(fig, out, "figure5_public_data_endpoint")


def main() -> None:
    a = parse_args()
    style()
    summary = load_json("chapter2_historical_differentiation_final_summary_v1.json")
    orient = load_json("chapter2_orientation_differentiation_environment_v2_summary.json")
    atlas = load_json("chapter2_lineage_differentiation_environment_atlas_v1_summary.json")
    sea = load_json("chapter2_lineage_differentiation_sealevel_v1.json")

    outputs = []
    outputs += figure1(a.output_dir, summary)
    outputs += figure2(a.output_dir, summary)
    outputs += figure3(a.output_dir, summary, orient)
    outputs += figure4(a.output_dir, atlas, sea)
    outputs += figure5(a.output_dir, summary)
    for p in outputs:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()
