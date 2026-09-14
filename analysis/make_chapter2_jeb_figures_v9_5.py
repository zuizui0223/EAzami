#!/usr/bin/env python3
"""Generate the V9.5 organization-first JEB figure package from frozen evidence.

The script deliberately prioritizes the direct historical estimands used by V9.5:
recurrence, paired relative-depth ordering, shared-transition localization, and
representation-dependent ecology. It does not plot historical-climate nulls in the
main figure package.
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
BLUE = "#4C78A8"
GOLD = "#D59A2D"
TEAL = "#4C9A89"
RED = "#B65C5C"
MID = "#777777"
LIGHT = "#D9DEE3"
PALE = "#F5F6F7"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v9_5")
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
    fig.savefig(png, dpi=300, bbox_inches="tight", metadata={"Software": "EAzami V9.5"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami V9.5", "Title": stem})
    plt.close(fig)
    return [png, pdf]


def figure1(out: Path, hist: dict) -> list[Path]:
    rec = hist["recurrence_and_depth"]
    traits = ["Orientation", "Phyllary", "Stickiness"]
    keys = ["orientation", "phyllary_posture", "stickiness"]
    colors = [BLUE, GOLD, TEAL]
    y = np.arange(3)[::-1]

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), gridspec_kw={"width_ratios": [1.0, 1.2, 1.45]})

    ax = axes[0]
    coverage = [rec[k]["resolved_concepts"] for k in keys]
    ax.barh(y, coverage, color=colors, alpha=0.9)
    ax.set_yticks(y, traits)
    ax.set_xlim(0, 22)
    ax.set_xlabel("Resolved Japan38 concepts")
    ax.set_title("Trait-state coverage")
    for yy, n in zip(y, coverage):
        ax.text(n + 0.35, yy, str(n), va="center")
    panel(ax, "a")

    ax = axes[1]
    ranges = [
        (rec["orientation"]["minimum_changes_ufboot_range"][0], rec["orientation"]["minimum_changes_ufboot_range"][1], rec["orientation"]["minimum_changes_ml"]),
        (rec["phyllary_posture"]["minimum_changes"], rec["phyllary_posture"]["minimum_changes"], rec["phyllary_posture"]["minimum_changes"]),
        (rec["stickiness"]["minimum_changes"], rec["stickiness"]["minimum_changes"], rec["stickiness"]["minimum_changes"]),
    ]
    for yy, (lo, hi, ml), color in zip(y, ranges, colors):
        ax.hlines(yy, lo, hi, color=color, lw=6)
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
    for yy, (lo, hi), color in zip(y, depth, colors):
        ax.hlines(yy, lo, hi, color=color, lw=6)
        ax.plot((lo + hi) / 2, yy, "o", color=color, ms=5)
        ax.text(lo - 0.01, yy, f"{lo:.3f}", ha="right", va="center", fontsize=7)
        ax.text(hi + 0.01, yy, f"{hi:.3f}", ha="left", va="center", fontsize=7)
    ax.set_yticks(y, traits)
    ax.set_xlim(0.64, 1.03)
    ax.set_xlabel("Relative lineage depth (1 = terminal)")
    ax.set_title("Different historical layers")
    ax.text(0.5, -0.22, "Topology-based coordinate; not calendar time", transform=ax.transAxes, ha="center", color=MID, fontsize=7.2)
    panel(ax, "c")

    fig.suptitle("Figure 1. Three capitulum components repeatedly differentiate within one young radiation", fontsize=11, y=1.02)
    return save(fig, out, "figure1_repeated_components")


def figure2(out: Path, depth: dict, coverage: dict) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.6), gridspec_kw={"width_ratios": [1.45, 1.0, 1.05]})

    ax = axes[0]
    pairs = depth["pairwise_results"]
    labels = []
    med = []
    lo = []
    hi = []
    for r in pairs:
        labels.append(f"{r['deeper_candidate']} − {r['shallower_candidate']}")
        d = r["lower_bound_difference_deeper_minus_shallower"]
        med.append(d["median"])
        lo.append(d["q05"])
        hi.append(d["q95"])
    y = np.arange(len(labels))[::-1]
    ax.axvline(0, color=DARK, lw=0.8)
    for yy, m, l, h in zip(y, med, lo, hi):
        ax.hlines(yy, l, h, color=BLUE, lw=5)
        ax.plot(m, yy, "o", color=BLUE)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Paired lower-depth difference\n(negative = first trait deeper-permissive)")
    ax.set_title("Same-topology depth contrasts")
    panel(ax, "a")

    ax = axes[1]
    names = ["Phyllary <\nstickiness", "Phyllary <\norientation", "Orientation <\nstickiness", "Complete\nordering"]
    vals = [1000, 993, 905, depth["complete_lower_bound_ordering"]["count"]]
    den = [1000, 1000, 1000, 1000]
    pct = np.array(vals) / np.array(den) * 100
    ax.bar(range(4), pct, color=[TEAL, TEAL, GOLD, BLUE], alpha=0.9)
    ax.set_xticks(range(4), names)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Topology sensitivity (%)")
    ax.set_title("Central ordering is stable")
    for i, (v, d) in enumerate(zip(vals, den)):
        ax.text(i, pct[i] + 2, f"{v}/{d}", ha="center", fontsize=7.5)
    panel(ax, "b")

    ax = axes[2]
    comp = {r["comparison"]: r for r in coverage["comparison_results"]}
    labels = ["vs orientation\nmatched median", "vs stickiness\nmatched median", "vs orientation\nmatched q05", "vs stickiness\nmatched q05"]
    vals = [
        100 * comp["phyllary_lt_orientation_median"]["fraction"],
        100 * comp["phyllary_lt_stickiness_5_5_median"]["fraction"],
        100 * comp["phyllary_lt_orientation_q05"]["fraction"],
        100 * comp["phyllary_lt_stickiness_5_5_q05"]["fraction"],
    ]
    ax.barh(np.arange(4)[::-1], vals, color=[TEAL, TEAL, MID, MID], alpha=0.9)
    ax.set_yticks(np.arange(4)[::-1], labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Selected topologies (%)")
    ax.set_title("Coverage-matched sensitivity")
    ax.text(0.5, -0.25, "Central ordering retained; strict tails overlap", transform=ax.transAxes, ha="center", fontsize=7.2, color=MID)
    panel(ax, "c")

    fig.suptitle("Figure 2. Repeated histories are stratified across unequal evolutionary depths", fontsize=11, y=1.02)
    return save(fig, out, "figure2_depth_ordering")


def figure3(out: Path, fdt: dict, hist: dict) -> list[Path]:
    cm = fdt["cross_module"]
    aware = cm["branch_length_aware_ml"]
    topo = cm["topology_only_equal_branch_sensitivity"]
    pairs = ["Orientation–phyllary", "Orientation–stickiness", "Phyllary–stickiness"]
    aware_vals = [
        aware["orientation_phyllary_excess_rho"],
        aware["orientation_stickiness_excess_rho"],
        aware["phyllary_stickiness_excess_rho"],
    ]
    topo_vals = [
        topo["orientation_phyllary_ml_rho"],
        topo["orientation_stickiness_ml_rho"],
        topo["phyllary_stickiness_ml_rho"],
    ]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.7), gridspec_kw={"width_ratios": [1.55, 0.85]})
    ax = axes[0]
    x = np.arange(3)
    w = 0.34
    ax.axhline(0, color=DARK, lw=0.8)
    ax.bar(x - w/2, aware_vals, width=w, color=BLUE, label="branch-length-aware")
    ax.bar(x + w/2, topo_vals, width=w, color=GOLD, label="equal-branch topology-only")
    ax.set_xticks(x, pairs, rotation=18, ha="right")
    ax.set_ylabel("Spearman rho")
    ax.set_title("Pairwise transition-localization association")
    ax.legend(frameon=False, fontsize=7.5)
    panel(ax, "a")

    ax = axes[1]
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.08, 0.48), 0.84, 0.34, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.69, "0 / 3", transform=ax.transAxes, ha="center", va="center", fontsize=26, fontweight="bold", color=RED)
    ax.text(0.5, 0.56, "trait pairs pass the robust\nshared-localization rule", transform=ax.transAxes, ha="center", va="center", fontsize=8)
    ax.text(0.5, 0.29, "No repeated synchronized\nwhole-capitulum history", transform=ax.transAxes, ha="center", fontsize=10, fontweight="bold")
    ax.text(0.5, 0.12, hist["recurrence_and_depth"]["shared_transition_localization"], transform=ax.transAxes, ha="center", fontsize=7.2, color=MID)
    panel(ax, "b")

    fig.suptitle("Figure 3. Component changes are not repeatedly synchronized on the same branches", fontsize=11, y=1.02)
    return save(fig, out, "figure3_shared_localization")


def _parse_fraction(text: str) -> float:
    left = text.split("=")[0].strip()
    a, b = left.split("/")
    return 100 * float(a) / float(b)


def figure4(out: Path, common9: dict, claims: dict) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.7), gridspec_kw={"width_ratios": [1.0, 1.25, 1.05]})

    ax = axes[0]
    labels = ["Orientation", "Phyllary", "Stickiness"]
    vals = [34.55, 100.0, 12.55]
    cols = [BLUE, MID, TEAL]
    ax.bar(range(3), vals, color=cols, alpha=0.9)
    ax.set_xticks(range(3), labels, rotation=18)
    ax.set_ylabel("Maps at least as extreme (%)")
    ax.set_title("Common9 static state separation")
    ax.text(1, 86, "resolution-limited\n(3:1 states)", ha="center", fontsize=7.2, color=DARK)
    panel(ax, "a")

    ax = axes[1]
    h1 = claims["orientation_transition_regime"]["h1"]
    names = ["n≥5\n12 taxa", "n≥3\n13 taxa", "strict n≥10"]
    texts = [h1["n5_12_taxa_exact_rank"], h1["n3_13_taxa_exact_rank"], h1["strict_n10_exact_rank"]]
    vals = [_parse_fraction(x) for x in texts]
    ax.bar(range(3), vals, color=BLUE, alpha=0.9)
    ax.set_xticks(range(3), names)
    ax.set_ylabel("Maps at least as extreme (%)")
    ax.set_ylim(0, max(vals) * 1.55)
    ax.set_title("Orientation transition–niche concordance")
    for i, (v, t) in enumerate(zip(vals, texts)):
        ax.text(i, v + 0.2, t.split("=")[0].strip(), ha="center", fontsize=7.5)
    panel(ax, "b")

    ax = axes[2]
    ax.axis("off")
    h2 = claims["orientation_transition_regime"]["h2"]
    h3 = claims["orientation_transition_regime"]["h3"]
    lines = [
        ("Bidirectional strict floor", h2["exact_bidirectional_floor_rank"]),
        ("Both directions positive", h2["both_positive_topologies"]),
        ("Single-taxon deletions", "9/9 direction retained" if h3["forward_and_reverse_positive_all_deletions"] else "not retained"),
        ("Exact exceptionality", h3["exact_exceptionality_pass"]),
    ]
    y = 0.82
    for label, value in lines:
        ax.text(0.05, y, label, transform=ax.transAxes, fontsize=8, color=MID)
        ax.text(0.95, y, value, transform=ax.transAxes, ha="right", fontsize=8.5, fontweight="bold")
        y -= 0.17
    ax.text(0.5, 0.07, "Ecological signal depends on phenotype representation", transform=ax.transAxes, ha="center", fontsize=8.5, fontweight="bold")
    panel(ax, "c")

    fig.suptitle("Figure 4. Ecological correspondence is weak in static state space but informative for orientation transitions", fontsize=11, y=1.02)
    return save(fig, out, "figure4_representation_dependent_ecology")


def main() -> None:
    a = parse_args()
    style()
    hist = load_json("chapter2_historical_differentiation_final_summary_v1.json")
    depth = load_json("chapter2_depth_ordering_robustness_result_v1.json")
    coverage = load_json("chapter2_depth_coverage_matched_sensitivity_result_v1.json")
    common9 = load_json("chapter2_three_trait_common9_result_v1.json")
    fdt = load_json("fdt_multitrait_execution_readiness_v2.json")
    claims = load_json("chapter2_current_claims_h1_h4_v1.json")

    outputs: list[Path] = []
    outputs += figure1(a.output_dir, hist)
    outputs += figure2(a.output_dir, depth, coverage)
    outputs += figure3(a.output_dir, fdt, hist)
    outputs += figure4(a.output_dir, common9, claims)
    for p in outputs:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()
