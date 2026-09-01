#!/usr/bin/env python3
"""Generate the five active JEB V5 figures from frozen Chapter 2 evidence.

The figures are decision-level visualizations. They deliberately preserve sign
reversals, unresolved classes, and non-evaluable boundaries rather than averaging
heterogeneous evidence into a single effect.
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
BLUE = "#356B9A"
GOLD = "#C6902B"
TEAL = "#3A8573"
RED = "#A64B4B"
MID = "#707780"
LIGHT = "#DDE2E7"
PALE = "#F5F6F7"


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v5")
    return p.parse_args()


def load(name: str) -> dict:
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
    ax.text(-0.10, 1.06, label, transform=ax.transAxes, fontweight="bold", fontsize=11, va="top")


def yerr_from_records(records: list[dict], value_key: str = "difference", ci_key: str = "bootstrap_95") -> np.ndarray:
    values = [float(r[value_key]) for r in records]
    lo = [float(r[ci_key][0]) for r in records]
    hi = [float(r[ci_key][1]) for r in records]
    return np.array([
        [v - l for v, l in zip(values, lo)],
        [h - v for v, h in zip(values, hi)],
    ])


def save(fig, out: Path, stem: str) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    png = out / f"{stem}.png"
    pdf = out / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)
    return [png, pdf]


def figure1(out: Path) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.4))
    traits = ["Orientation", "Phyllary", "Stickiness"]
    coverage = [20, 10, 13]
    colors = [BLUE, GOLD, TEAL]

    ax = axes[0]
    y = np.arange(3)[::-1]
    ax.barh(y, coverage, color=colors, alpha=0.85)
    ax.set_yticks(y, traits)
    ax.set_xlim(0, 22)
    ax.set_xlabel("Resolved paper concepts")
    ax.set_title("Trait-state coverage\n(36/38 sampled concepts in dominant radiation)")
    for yy, n in zip(y, coverage):
        ax.text(n + 0.3, yy, str(n), va="center")
    panel(ax, "a")

    ax = axes[1]
    mins = [(4, 6, 6), (3, 3, 3), (5, 5, 5)]
    for yy, (name, (lo, hi, ml), color) in zip(y, zip(traits, mins, colors)):
        ax.hlines(yy, lo, hi, color=color, lw=5)
        ax.plot((lo + hi) / 2, yy, "o", mfc="white", mec=color, mew=1.5, ms=6)
        ax.plot(ml, yy, "D", color=DARK, ms=4)
        ax.text(hi + 0.12, yy, f"{lo}–{hi}", va="center", fontsize=7.5)
    ax.set_yticks(y, traits)
    ax.set_xlim(0, 6.8)
    ax.set_xlabel("Minimum unordered changes")
    ax.set_title("Repeated-history burden")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.plot([], [], "D", color=DARK, label="ML")
    ax.plot([], [], "o", mfc="white", mec=BLUE, label="UFBoot range midpoint")
    ax.legend(frameon=False, fontsize=6.8, loc="upper left")
    panel(ax, "b")

    ax = axes[2]
    depth = [(0.795, 0.994), (0.695, 1.000), (0.937, 0.954)]
    for yy, ((lo, hi), color) in zip(y, zip(depth, colors)):
        ax.hlines(yy, lo, hi, color=color, lw=5)
        ax.plot((lo + hi) / 2, yy, "o", color=color, ms=5)
        ax.text(lo - 0.015, yy, f"{lo:.3f}", ha="right", va="center", fontsize=7)
        ax.text(hi + 0.015, yy, f"{hi:.3f}", ha="left", va="center", fontsize=7)
    ax.set_yticks(y, traits)
    ax.set_xlim(0.63, 1.03)
    ax.set_xlabel("Relative lineage-depth (1 = terminal)")
    ax.set_title("Admissible historical depth")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.text(0.5, -0.22, "Topology only — not calendar time", transform=ax.transAxes, ha="center", color=MID, fontsize=7.2)
    panel(ax, "c")
    fig.suptitle("Figure 1. Capitulum modules have unequal evolutionary depth", fontsize=11, y=1.02)
    return save(fig, out, "figure1_evolutionary_depth")


def figure2(out: Path) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.4), gridspec_kw={"width_ratios": [1.25, 1.35, 1.0]})

    ax = axes[0]
    labels = ["Ori JPN36", "Phy JPN36", "Sticky JPN06", "Sticky JPN36", "Sticky JPN30", "Sticky internal"]
    vals = [0.227, 0.728, 0.995, 0.707, 0.545, 0.681]
    cols = [BLUE, GOLD, TEAL, TEAL, TEAL, TEAL]
    y = np.arange(len(labels))[::-1]
    for yy, lab, v, c in zip(y, labels, vals, cols):
        ax.hlines(yy, 0, v, color=LIGHT, lw=2)
        ax.plot(v, yy, "o", color=c, mfc="white", mew=1.5)
        ax.text(v + 0.025, yy, f"{v:.3f}", va="center", fontsize=7)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1.06)
    ax.set_xlabel("Fraction of UFBoot topologies forcing edge")
    ax.set_title("Named-edge concentration")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    panel(ax, "a")

    ax = axes[1]
    pairs = ["Ori–Phy", "Ori–Sticky", "Phy–Sticky"]
    branch = np.array([0.362, 0.202, 0.084])
    med = np.array([-0.059, -0.387, 0.184])
    q05 = np.array([-0.206, -0.392, -0.073])
    y = np.arange(3)[::-1]
    ax.axvline(0, color=DARK, lw=0.8)
    for yy, p, b, m, q in zip(y, pairs, branch, med, q05):
        ax.hlines(yy, q, m, color=LIGHT, lw=5)
        ax.plot(m, yy, "o", color=BLUE, label="equal-branch median" if yy == y[0] else None)
        ax.plot(b, yy, "D", color=GOLD, label="branch-aware" if yy == y[0] else None)
        ax.plot(q, yy, "|", color=DARK, ms=10)
    ax.set_yticks(y, pairs)
    ax.set_xlim(-0.46, 0.43)
    ax.set_xlabel("Transition-localization correlation")
    ax.set_title("Shared-history diagnostic")
    ax.legend(frameon=False, fontsize=6.8, loc="lower right")
    panel(ax, "b")

    ax = axes[2]
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.08, 0.52), 0.84, 0.28, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.69, "0 / 3", transform=ax.transAxes, ha="center", va="center", fontsize=22, fontweight="bold")
    ax.text(0.5, 0.58, "trait pairs pass the robust\nshared-localization rule", transform=ax.transAxes, ha="center", va="center", fontsize=8)
    ax.text(0.5, 0.30, "Simple synchronized-history\nmodel not supported", transform=ax.transAxes, ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(0.5, 0.12, "≠ complete trait independence", transform=ax.transAxes, ha="center", color=MID)
    ax.set_title("Decision")
    panel(ax, "c")
    fig.suptitle("Figure 2. One present capitulum does not imply one transition history", fontsize=11, y=1.02)
    return save(fig, out, "figure2_shared_history_boundary")


def figure3(out: Path) -> list[Path]:
    origin = load("chapter2_orientation_origin_envelope_result_v1.json")
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.7))

    ax = axes[0, 0]
    ax.axvline(0, color=DARK, lw=0.8)
    labels = ["Azami BIO12\namong taxa", "EAzami BIO15\nD−U", "EAzami BIO1\nD−U"]
    vals = [0.304359, 1.325, -0.971]
    cols = [BLUE, TEAL, GOLD]
    y = np.arange(3)[::-1]
    for yy, v, c in zip(y, vals, cols):
        ax.plot(v, yy, "o", color=c, ms=7)
        ax.hlines(yy, 0, v, color=c, lw=2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Standardized effect (different estimands)")
    ax.set_title("Present environmental correspondence")
    panel(ax, "a")

    ax = axes[0, 1]
    ax.axis("off")
    ax.plot([0.12, 0.88], [0.52, 0.52], color=DARK, lw=2, transform=ax.transAxes)
    for x in [0.12, 0.50, 0.88]:
        ax.plot(x, 0.52, "o", color=BLUE if x != 0.5 else RED, ms=8, transform=ax.transAxes)
    ax.text(0.12, 0.67, "C. morii split\n0.79 Ma\n(0.43–1.18)", ha="center", transform=ax.transAxes, fontsize=8)
    ax.text(0.50, 0.31, "candidate U→D\nstem", ha="center", transform=ax.transAxes, fontsize=8, fontweight="bold")
    ax.text(0.88, 0.67, "Japan–Taiwan core split\n0.74 Ma\n(0.60–0.87)", ha="center", transform=ax.transAxes, fontsize=8)
    ax.text(0.5, 0.08, "94 admissible age pairs; cross-study scenario envelope, not joint posterior", ha="center", transform=ax.transAxes, fontsize=7, color=MID)
    ax.set_title("Public chronology boundary")
    panel(ax, "b")

    ax = axes[1, 0]
    regions = ["taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor"]
    pretty = ["Taiwan", "Ryukyu", "S Japan", "E Asia core"]
    y = np.arange(4)[::-1]
    ax.axvline(0, color=DARK, lw=0.8)
    for yy, r, lab in zip(y, regions, pretty):
        s = origin["region_summaries"][r]["cosine_similarity"]
        ax.hlines(yy, s["q05"], s["q95"], color=LIGHT, lw=5)
        ax.plot(s["median"], yy, "o", color=BLUE)
    ax.set_yticks(y, pretty)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Cosine: Azami state vector vs historical trajectory")
    ax.set_title("Chronology × palaeolocation envelope")
    panel(ax, "c")

    ax = axes[1, 1]
    ax.axis("off")
    c = origin["cross_scenario_summary"]["cosine_similarity"]
    ax.add_patch(plt.Rectangle((0.06, 0.48), 0.88, 0.34, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.72, "376 scenarios", transform=ax.transAxes, ha="center", fontsize=15, fontweight="bold")
    ax.text(0.5, 0.60, f"q05 {c['q05']:.3f}   median {c['median']:.3f}   q95 {c['q95']:.3f}", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.32, "Origin trajectory unresolved", transform=ax.transAxes, ha="center", fontsize=12, fontweight="bold", color=RED)
    ax.text(0.5, 0.17, "Present hydric correspondence\n≠ identified historical hydric origin", transform=ax.transAxes, ha="center", fontsize=8)
    ax.set_title("Historical decision")
    panel(ax, "d")
    fig.suptitle("Figure 3. Orientation: present hydric correspondence does not identify origin", fontsize=11, y=1.01)
    return save(fig, out, "figure3_orientation_state_trajectory")


def figure4(out: Path) -> list[Path]:
    image = load("chapter2_four_taxon_azami_measurement_result_v1.json")
    rsds = load("chapter2_colour_rsds_focal_concordance_result_v1.json")
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.7))
    systems = ["ARENICOLA_BREVICAULE_IRUMTIENSE", "TAIWAN_KAWAKAMII_TATAKAENSE"]
    pretty = ["Arenicola", "Taiwan"]

    ax = axes[0, 0]
    ax.axis("off")
    for x0, name, white, coloured, age in [
        (0.28, "Arenicola", "C. brevicaule\nwhite", "C. irumtiense\ncoloured", "~0.93 Ma"),
        (0.72, "Taiwan", "C. kawakamii\nwhite", "C. tatakaense\ncoloured", "~0.35 Ma"),
    ]:
        ax.plot([x0-0.12, x0+0.12], [0.58, 0.58], color=DARK, lw=1.6, transform=ax.transAxes)
        ax.plot(x0, 0.58, "o", color=MID, transform=ax.transAxes)
        ax.text(x0-0.12, 0.70, white, ha="center", transform=ax.transAxes, fontsize=8)
        ax.text(x0+0.12, 0.70, coloured, ha="center", transform=ax.transAxes, fontsize=8)
        ax.text(x0, 0.37, f"{name}\nsplit context {age}", ha="center", transform=ax.transAxes, fontsize=8)
    ax.text(0.5, 0.10, "Lineage split ≠ exact colour-transition date", transform=ax.transAxes, ha="center", color=MID, fontsize=7.5)
    ax.set_title("Dated sister-system natural experiments")
    panel(ax, "a")

    ax = axes[0, 1]
    x = np.arange(2)
    chroma_rec = [image["systems"][s]["contrasts_white_minus_coloured"]["corolla_lab_chroma"] for s in systems]
    light_rec = [image["systems"][s]["contrasts_white_minus_coloured"]["corolla_lab_lightness"] for s in systems]
    chroma = [r["difference"] for r in chroma_rec]
    lightness = [r["difference"] for r in light_rec]
    w = 0.32
    ax.axhline(0, color=DARK, lw=0.8)
    ax.bar(x-w/2, chroma, width=w, color=BLUE, label="Chroma")
    ax.bar(x+w/2, lightness, width=w, color=GOLD, label="Lightness")
    ax.errorbar(x-w/2, chroma, yerr=yerr_from_records(chroma_rec), fmt="none", ecolor=DARK, elinewidth=0.9, capsize=2.5, zorder=3)
    ax.errorbar(x+w/2, lightness, yerr=yerr_from_records(light_rec), fmt="none", ecolor=DARK, elinewidth=0.9, capsize=2.5, zorder=3)
    ax.set_xticks(x, ["Arenicola\nn=7/8", "Taiwan\nn=3/3"])
    ax.set_ylabel("White − coloured")
    ax.set_title("Repeated white-state phenotype direction")
    ax.legend(frameon=False)
    ax.text(0.98, 0.03, "95% bootstrap intervals; n=white/coloured usable", transform=ax.transAxes, ha="right", fontsize=6.6, color=MID)
    panel(ax, "b")

    ax = axes[1, 0]
    obs_rec = [rsds["systems"][s]["observation_level"] for s in systems]
    cell_rec = [rsds["systems"][s]["spatial_0_05_degree_cell_sensitivity"] for s in systems]
    obs = [r["delta_rsds_white_minus_coloured_raw"] for r in obs_rec]
    cells = [r["delta_rsds_white_minus_coloured_raw"] for r in cell_rec]
    obs_yerr = np.array([
        [v - r["delta_rsds_bootstrap_95_raw"][0] for v, r in zip(obs, obs_rec)],
        [r["delta_rsds_bootstrap_95_raw"][1] - v for v, r in zip(obs, obs_rec)],
    ])
    cell_yerr = np.array([
        [v - r["delta_rsds_bootstrap_95_raw"][0] for v, r in zip(cells, cell_rec)],
        [r["delta_rsds_bootstrap_95_raw"][1] - v for v, r in zip(cells, cell_rec)],
    ])
    ax.axhline(0, color=DARK, lw=0.8)
    ax.bar(x-w/2, obs, width=w, color=BLUE, label="Observation median")
    ax.bar(x+w/2, cells, width=w, color=TEAL, label="0.05° cells")
    ax.errorbar(x-w/2, obs, yerr=obs_yerr, fmt="none", ecolor=DARK, elinewidth=0.9, capsize=2.5, zorder=3)
    ax.errorbar(x+w/2, cells, yerr=cell_yerr, fmt="none", ecolor=DARK, elinewidth=0.9, capsize=2.5, zorder=3)
    ax.set_xticks(x, pretty)
    ax.set_ylabel("RSDS white − coloured\n(stored raster units)")
    ax.set_title("Pair-level current radiation context")
    ax.legend(frameon=False, fontsize=7)
    ax.text(0.03, 0.04, "Azami expected direction:\nRSDS >0 with chroma <0", transform=ax.transAxes, fontsize=7, color=MID)
    panel(ax, "c")

    ax = axes[1, 1]
    ax.axis("off")
    within = rsds["chapter_summary"]["pooled_within_taxon_secondary"]
    ax.add_patch(plt.Rectangle((0.06, 0.54), 0.88, 0.27, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
    ax.text(0.5, 0.72, "Pair-level concordance = 1 / 2", transform=ax.transAxes, ha="center", fontsize=12, fontweight="bold")
    ax.text(0.5, 0.61, "Arenicola concordant · Taiwan reversed", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.37, f"Within-taxon secondary beta = {within['beta_std']:.3f}", transform=ax.transAxes, ha="center", fontsize=10)
    ax.text(0.5, 0.27, f"two-sided P={within['permutation_p_two_sided']:.4f}; expected-negative P={within['permutation_p_expected_negative']:.4f}", transform=ax.transAxes, ha="center", fontsize=7.5)
    ax.text(0.5, 0.10, "Lineage- and scale-dependent current correspondence", transform=ax.transAxes, ha="center", fontsize=9, fontweight="bold", color=RED)
    ax.set_title("Hierarchical scale diagnostic")
    panel(ax, "d")
    fig.suptitle("Figure 4. Repeated white phenotype does not imply one current RSDS rule", fontsize=11, y=1.01)
    return save(fig, out, "figure4_colour_rsds_natural_experiment")


def figure5(out: Path) -> list[Path]:
    image = load("chapter2_four_taxon_azami_measurement_result_v1.json")
    final = load("chapter2_final_integrated_evidence_v3.json")
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.9))
    systems = ["ARENICOLA_BREVICAULE_IRUMTIENSE", "TAIWAN_KAWAKAMII_TATAKAENSE"]
    pretty = ["Arenicola", "Taiwan"]
    metrics = ["shape_circularity", "shape_solidity", "visible_floret_fraction_extended"]
    mpretty = ["Circularity", "Solidity", "Visible floret\nfraction"]
    x = np.arange(3)
    w = 0.34

    ax = axes[0, 0]
    ax.axhline(0, color=DARK, lw=0.8)
    for j, (s, name, c) in enumerate(zip(systems, pretty, [BLUE, GOLD])):
        recs = [image["systems"][s]["contrasts_white_minus_coloured"][m] for m in metrics]
        vals = [r["difference"] for r in recs]
        xpos = x + (j-0.5)*w
        ax.bar(xpos, vals, width=w, color=c, label=name)
        ax.errorbar(xpos, vals, yerr=yerr_from_records(recs), fmt="none", ecolor=DARK, elinewidth=0.9, capsize=2.5, zorder=3)
    ax.set_xticks(x, mpretty)
    ax.set_ylabel("White − coloured")
    ax.set_title("Coarse directions repeated in both white lineages")
    ax.legend(frameon=False)
    ax.text(0.98, 0.03, "95% bootstrap intervals", transform=ax.transAxes, ha="right", fontsize=6.8, color=MID)
    panel(ax, "a")

    ax = axes[0, 1]
    ax.axis("off")
    negatives = [
        "aspect ratio", "width-profile CV", "involucre L/W", "apical taper",
        "basal taper", "projection roughness", "projection p95", "spread fraction", "bract peak density"
    ]
    for i, label in enumerate(negatives):
        y = 0.88 - i * 0.09
        tag = "heterogeneous / low information"
        ax.text(0.05, y, label, transform=ax.transAxes, fontsize=7.4)
        ax.text(0.95, y, tag, transform=ax.transAxes, fontsize=6.8, ha="right", color=MID)
    ax.text(0.5, 0.04, "No universal fine-geometry syndrome", transform=ax.transAxes, ha="center", fontweight="bold", color=RED)
    ax.set_title("Fine-geometry negative evidence")
    panel(ax, "b")

    ax = axes[1, 0]
    ax.axis("off")
    ax.text(0.5, 0.86, "Whole-capitulum constraints", transform=ax.transAxes, ha="center", fontweight="bold", fontsize=10)
    blocks = [
        ("Discrete history", "0/3 trait pairs share robust\ntransition localization"),
        ("Present integration", "within-vs-among matrix\nrho = 0.3663"),
        ("White sister systems", "3 coarse non-colour\ndirections repeat"),
    ]
    for i, (head, body) in enumerate(blocks):
        y = 0.64 - i * 0.23
        ax.add_patch(plt.Rectangle((0.08, y-0.08), 0.84, 0.16, facecolor=PALE, edgecolor=DARK, transform=ax.transAxes))
        ax.text(0.13, y+0.02, head, transform=ax.transAxes, fontweight="bold", fontsize=8)
        ax.text(0.55, y, body, transform=ax.transAxes, va="center", fontsize=7.5)
    panel(ax, "c")

    ax = axes[1, 1]
    ax.axis("off")
    ax.text(0.5, 0.88, "Rejected extremes", transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.12, 0.68, "Complete\nindependence", transform=ax.transAxes, ha="center", color=MID)
    ax.text(0.88, 0.68, "One synchronized\nuniversal syndrome", transform=ax.transAxes, ha="center", color=MID)
    ax.annotate("", xy=(0.78, 0.68), xytext=(0.22, 0.68), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="<->", color=DARK, lw=1.5))
    ax.add_patch(plt.Rectangle((0.20, 0.39), 0.60, 0.23, facecolor="#E8F0EC", edgecolor=TEAL, lw=1.5, transform=ax.transAxes))
    ax.text(0.5, 0.505, "Partial coordinated remodelling\nwithin modular, lineage-dependent\nhistories", transform=ax.transAxes, ha="center", va="center", fontsize=7.2, fontweight="bold", linespacing=1.12)
    ax.text(0.5, 0.23, "Public-data ceiling", transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.12, "direct exposure → mechanism → reproductive fitness", transform=ax.transAxes, ha="center", fontsize=8)
    ax.set_title("Final process model")
    panel(ax, "d")
    fig.suptitle("Figure 5. Partial coordinated remodelling is nested within a modular historical mosaic", fontsize=11, y=1.01)
    return save(fig, out, "figure5_whole_capitulum_synthesis")


def main() -> int:
    a = args()
    style()
    outputs = []
    for fn in (figure1, figure2, figure3, figure4, figure5):
        outputs.extend(fn(a.output_dir))
    for p in outputs:
        if not p.exists() or p.stat().st_size < 3000:
            raise RuntimeError(f"Missing/small figure: {p}")
        print(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p, p.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
