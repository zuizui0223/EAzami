#!/usr/bin/env python3
"""Generate the four active JEB figures from frozen Chapter 2 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
TIME = EVID / "chapter2_time_axis_compute"
PROV = EVID / "chapter2_provenance_sensitivity_compute"

BLUE = "#2F5D8A"
GOLD = "#C58A1C"
DARK = "#222222"
MID = "#6F7782"
LIGHT = "#D9DDE3"
PALE = "#F4F5F7"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures")
    return p.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def style() -> None:
    plt.rcParams.update(
        {
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
        }
    )


def panel_label(ax, label: str) -> None:
    ax.text(-0.12, 1.07, label, transform=ax.transAxes, fontweight="bold", fontsize=11, va="top")


def save(fig, out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    png = out_dir / f"{stem}.png"
    pdf = out_dir / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)
    return [png, pdf]


def figure1(out_dir: Path) -> list[Path]:
    src = EVID / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv"
    d = pd.read_csv(src)
    rows = d[d["target_id"].str.contains("module_integration_contrast")].copy()
    assert len(rows) == 4
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), gridspec_kw={"width_ratios": [1.65, 1]})

    ax = axes[0]
    y_base = {"complete18_min5": 1.0, "complete18_min2": 0.0}
    offsets = {"within_taxon": 0.11, "among_taxon": -0.11}
    colors = {"within_taxon": BLUE, "among_taxon": GOLD}
    labels = {"within_taxon": "Within taxa", "among_taxon": "Among taxa"}
    for _, r in rows.iterrows():
        y = y_base[r["scope"]] + offsets[r["scale"]]
        x = float(r["value"])
        lo, hi = float(r["ci95_low"]), float(r["ci95_high"])
        ax.errorbar(
            x,
            y,
            xerr=[[x - lo], [hi - x]],
            fmt="o",
            color=colors[r["scale"]],
            markerfacecolor="white" if r["scale"] == "among_taxon" else colors[r["scale"]],
            markeredgecolor=colors[r["scale"]],
            capsize=3,
            lw=1.5,
            label=labels[r["scale"]] if r["scope"] == "complete18_min5" else None,
        )
        ax.text(hi + 0.006, y, f"{x:.3f}", va="center", fontsize=7.5)
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_yticks([0, 1], [">=2 observations", ">=5 observations"])
    ax.set_xlim(-0.005, 0.205)
    ax.set_xlabel("Registered-module contrast")
    ax.set_title("Contemporary integration by scale")
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.01, 0.50))
    panel_label(ax, "a")

    ax = axes[1]
    sim = d[(d["target_id"] == "capitulum_cross_scale_association_matrix_similarity") & (d["scope"] == "complete18_min5")].iloc[0]
    x, lo, hi = float(sim["value"]), float(sim["ci95_low"]), float(sim["ci95_high"])
    ax.errorbar(
        x,
        0,
        xerr=[[x - lo], [hi - x]],
        fmt="D",
        color=BLUE,
        markerfacecolor=BLUE,
        capsize=4,
        lw=1.6,
    )
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_xlim(-0.02, 0.5)
    ax.set_ylim(-0.55, 0.55)
    ax.set_yticks([])
    ax.set_xlabel("Spearman rho")
    ax.set_title("Within/among matrix similarity")
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    ax.text(x, 0.16, f"rho = {x:.3f}", ha="center", fontweight="bold")
    ax.text(0.5, -0.38, "Partial cross-scale alignment", transform=ax.transAxes, ha="center", color=MID)
    panel_label(ax, "b")
    fig.suptitle("Figure 1. Present-day capitulum integration is scale dependent", y=1.02, fontsize=11)
    return save(fig, out_dir, "figure1_present_integration")


def figure2(out_dir: Path) -> list[Path]:
    hist = read_json(EVID / "japan38_multitrait_history_summary_v1.json")
    sticky = read_json(EVID / "jpn24_stickiness_extension_parsimony_v1.json")
    orient = read_json(EVID / "jpn34_orientation_extension_parsimony_v1.json")
    sens = read_json(PROV / "japan38_all_continuous_history_summary_v1.json")

    rec = {
        "Orientation": {
            "lo": orient["orientation"]["ufboot1000_steps_min"],
            "med": orient["orientation"]["ufboot1000_steps_median"],
            "hi": orient["orientation"]["ufboot1000_steps_max"],
            "ml": orient["orientation"]["ml_minimum_unordered_steps"],
        },
        "Phyllary": {
            "lo": hist["minimum_change_history"]["phyllary_posture"]["ufboot1000_steps_min"],
            "med": hist["minimum_change_history"]["phyllary_posture"]["ufboot1000_steps_median"],
            "hi": hist["minimum_change_history"]["phyllary_posture"]["ufboot1000_steps_max"],
            "ml": hist["minimum_change_history"]["phyllary_posture"]["ml_minimum_unordered_steps"],
        },
        "Stickiness": {
            "lo": sticky["stickiness"]["ufboot1000_steps_min"],
            "med": sticky["stickiness"]["ufboot1000_steps_median"],
            "hi": sticky["stickiness"]["ufboot1000_steps_max"],
            "ml": sticky["stickiness"]["ml_minimum_unordered_steps"],
        },
    }
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.45), gridspec_kw={"width_ratios": [1.1, 1.3, 1.4]})

    ax = axes[0]
    names = list(rec)
    ypos = np.arange(len(names))[::-1]
    for y, name in zip(ypos, names):
        x = rec[name]
        ax.hlines(y, x["lo"], x["hi"], color=BLUE, lw=4)
        ax.plot(x["med"], y, "o", color=BLUE, mfc="white", ms=6, mew=1.4)
        ax.plot(x["ml"], y, "D", color=DARK, ms=4)
        ax.text(x["hi"] + 0.14, y, f"{x['lo']}-{x['hi']}", va="center", fontsize=7.5)
    ax.set_yticks(ypos, names)
    ax.set_xlim(0, 6.8)
    ax.set_xlabel("Minimum unordered changes")
    ax.set_title("Recurrence across 1,000 topologies")
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    ax.plot([], [], "D", color=DARK, ms=4, label="ML")
    ax.plot([], [], "o", color=BLUE, mfc="white", label="UFBoot median")
    ax.legend(frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(0.02, 0.90))
    panel_label(ax, "a")

    ax = axes[1]
    forced = [
        ("Orientation\nJPN36", hist["transition_identifiability"]["orientation"]["highest_terminal_forced_edge_ufboot_fraction"], BLUE, "o"),
        ("Phyllary\nJPN36", hist["transition_identifiability"]["phyllary_posture"]["JPN_36_ufboot_forced_fraction"], BLUE, "o"),
        ("Stickiness\nJPN06", hist["transition_identifiability"]["stickiness"]["JPN_06_ufboot_forced_fraction"], GOLD, "s"),
        ("Stickiness\nJPN36", hist["transition_identifiability"]["stickiness"]["JPN_36_ufboot_forced_fraction"], GOLD, "s"),
    ]
    y = np.arange(len(forced))[::-1]
    for yy, (label, value, color, marker) in zip(y, forced):
        ax.hlines(yy, 0, value, color=LIGHT, lw=2)
        ax.plot(value, yy, marker=marker, color=color, mfc="white", mew=1.5, ms=7)
        ax.text(value + 0.025, yy, f"{value:.3f}", va="center", fontsize=7.5)
    ax.set_yticks(y, [z[0] for z in forced])
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Fraction of topologies forcing edge")
    ax.set_title("Example edge identifiability")
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    ax.text(0.02, -0.30, "Stickiness placement audit predates JPN24 extension", transform=ax.transAxes, fontsize=6.8, color=MID)
    panel_label(ax, "b")

    ax = axes[2]
    ax.axis("off")
    items = [
        ("Original families", "0/8 corrected\nat >=2 and >=5", "Not supported"),
        ("JPN29 excluded >=2", f"{sens['n2_history_classes'].get('two_sided_not_supported', 0)}/8", "Not supported"),
        ("JPN29 excluded >=5", "5 concepts remain", "NOT EVALUABLE"),
    ]
    for i, (name, value, decision) in enumerate(items):
        y0 = 0.78 - i * 0.31
        face = PALE if decision != "NOT EVALUABLE" else "white"
        line_style = "-" if decision != "NOT EVALUABLE" else "--"
        rect = plt.Rectangle((0.02, y0 - 0.14), 0.96, 0.24, facecolor=face, edgecolor=DARK, lw=1.1, linestyle=line_style, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.06, y0 + 0.035, name, transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.06, y0 - 0.055, value, transform=ax.transAxes, va="center", fontsize=7.5)
        ax.text(0.95, y0 - 0.01, decision, transform=ax.transAxes, ha="right", va="center", color=MID, fontsize=7.3, fontweight="bold")
    ax.set_title("Continuous state-structure families")
    panel_label(ax, "c")
    fig.suptitle("Figure 2. Recurrence count and transition placement are distinct", y=1.02, fontsize=11)
    return save(fig, out_dir, "figure2_recurrence_identifiability")


def figure3(out_dir: Path) -> list[Path]:
    original = read_json(TIME / "japan38_branch_change_reconstruction_null_v1.json")
    sensitivity = read_json(PROV / "japan38_branch_change_provenance_sensitivity_v1.json")
    topology = read_json(TIME / "japan38_continuous_branch_change_topology_sensitivity_v1.json")
    orig_null = pd.read_csv(TIME / "japan38_branch_change_reconstruction_null_distribution_v1.csv")["null_global_mean_rho"].to_numpy()
    sens_null = pd.read_csv(PROV / "japan38_branch_change_provenance_sensitivity_null_distribution_v1.csv")["null_global_mean_rho"].to_numpy()
    assert len(orig_null) == len(sens_null) == 9999
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.4), gridspec_kw={"width_ratios": [1.2, 1.2, 0.9]})
    lo = min(float(orig_null.min()), float(sens_null.min()))
    hi = max(float(orig_null.max()), float(sens_null.max()))
    bins = np.linspace(lo, hi, 32)
    panels = [
        (axes[0], orig_null, original, "Original frozen panel\n8 concepts, 14 branches"),
        (axes[1], sens_null, sensitivity, "JPN29-excluded sensitivity\n7 concepts, 12 branches"),
    ]
    for idx, (ax, vals, result, title) in enumerate(panels):
        obs = result["observed_global_mean_pairwise_branch_change_rho"]
        p = result["one_sided_reconstruction_null_p"]
        ax.hist(vals, bins=bins, color=LIGHT, edgecolor="white", linewidth=0.35)
        ax.axvline(obs, color=BLUE, lw=2.2, label=f"Observed rho={obs:.3f}")
        ax.axvline(float(np.median(vals)), color=GOLD, lw=1.7, ls="--", label=f"Null median={np.median(vals):.3f}")
        ax.set_xlim(lo, hi)
        ax.set_xlabel("Null mean pairwise rho")
        ax.set_ylabel("Permutation count" if idx == 0 else "")
        ax.set_title(title)
        ax.text(0.97, 0.94, f"P={p:.4f}\nFAIL", transform=ax.transAxes, ha="right", va="top", fontweight="bold")
        ax.legend(frameon=False, fontsize=6.8, loc="upper left")
        panel_label(ax, "a" if idx == 0 else "b")

    ax = axes[2]
    g = topology["global_mean_pairwise_rho_distribution"]
    ax.errorbar(
        g["median"],
        0,
        xerr=[[g["median"] - g["q05"]], [g["q95"] - g["median"]]],
        fmt="o",
        color=BLUE,
        mfc="white",
        mew=1.5,
        capsize=4,
        lw=1.5,
    )
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_xlim(-0.02, 0.23)
    ax.set_ylim(-0.7, 0.7)
    ax.set_yticks([])
    ax.set_xlabel("Equal-branch mean rho")
    ax.set_title("Topology sign diagnostic")
    ax.text(0.5, 0.70, "1,000/1,000 positive", transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.62, "DIAGNOSTIC ONLY", transform=ax.transAxes, ha="center", fontweight="bold", color=MID)
    ax.text(0.5, 0.24, "Includes JPN29\nNo topology-specific null", transform=ax.transAxes, ha="center", fontsize=7.2)
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    panel_label(ax, "c")
    fig.suptitle("Figure 3. Observed continuous coupling does not exceed reconstruction geometry", y=1.02, fontsize=11)
    return save(fig, out_dir, "figure3_reconstruction_nulls")


def figure4(out_dir: Path) -> list[Path]:
    topo = read_json(TIME / "japan38_latest_module_overlap_topology_sensitivity_v2.json")
    ml = read_json(TIME / "japan38_latest_module_transition_overlap_v2.json")
    dist = topo["bootstrap_topology_sensitivity"]["pairwise_spearman_distributions"]
    ml_pairs = ml["pairwise_overlap"]
    specs = [
        ("Orientation–phyllary", "orientation__phyllary", "orientation__phyllary"),
        ("Orientation–stickiness", "orientation__stickiness", "orientation__stickiness"),
        ("Phyllary–stickiness", "phyllary__stickiness", "phyllary__stickiness"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(8.7, 3.5), gridspec_kw={"width_ratios": [1.55, 1]})
    ax = axes[0]
    y = np.arange(len(specs))[::-1]
    for yy, (label, dk, mk) in zip(y, specs):
        d = dist[dk]
        median = d["median"]
        ax.hlines(yy, d["q05"], d["q95"], color=BLUE, lw=4)
        ax.plot(median, yy, "o", color=BLUE, mfc="white", mew=1.5, ms=7)
        mlval = ml_pairs[mk]["spearman_transition_excess_over_branch_prior"]
        ax.plot(mlval, yy, "D", color=GOLD, ms=5)
        ax.text(d["q95"] + 0.025, yy, f"{100*d['fraction_positive']:.1f}% positive", va="center", fontsize=7.3)
    ax.axvline(0, color=DARK, lw=0.9)
    ax.set_yticks(y, [s[0] for s in specs])
    ax.set_xlim(-0.48, 0.48)
    ax.set_xlabel("Transition-overlap Spearman rho")
    ax.set_title("Equal-branch topology q05–median–q95")
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    ax.plot([], [], "o", color=BLUE, mfc="white", label="Topology median")
    ax.plot([], [], "D", color=GOLD, label="ML branch-length excess")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    panel_label(ax, "a")

    ax = axes[1]
    ax.axis("off")
    stages = [
        ("Repeated state", BLUE, True),
        ("Independent origin", MID, False),
        ("Equivalent function", MID, False),
        ("Repeated ecology", MID, False),
        ("Fitness consequence", MID, False),
        ("Adaptive convergence", MID, False),
    ]
    for i, (label, color, reached) in enumerate(stages):
        y0 = 0.92 - i * 0.155
        ax.add_patch(
            plt.Rectangle(
                (0.10, y0 - 0.07),
                0.80,
                0.10,
                facecolor=PALE if reached else "white",
                edgecolor=color,
                lw=1.2,
                ls="-" if reached else "--",
                transform=ax.transAxes,
            )
        )
        ax.text(0.50, y0 - 0.02, label, transform=ax.transAxes, ha="center", va="center", fontweight="bold" if reached else "normal", color=color)
        if i < len(stages) - 1:
            ax.annotate("", xy=(0.50, y0 - 0.115), xytext=(0.50, y0 - 0.075), xycoords=ax.transAxes, arrowprops={"arrowstyle": "->", "color": MID, "lw": 0.8})
    ax.text(0.5, 0.02, "Current evidence reaches recurrence only", transform=ax.transAxes, ha="center", fontsize=7.5, fontweight="bold")
    ax.set_title("Claim boundary")
    panel_label(ax, "b")
    fig.suptitle("Figure 4. Shared discrete transition localization is topology dependent", y=1.02, fontsize=11)
    return save(fig, out_dir, "figure4_discrete_overlap")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    style()
    outputs: list[Path] = []
    outputs += figure1(args.output_dir)
    outputs += figure2(args.output_dir)
    outputs += figure3(args.output_dir)
    outputs += figure4(args.output_dir)
    manifest = {
        "contract_version": "chapter2_jeb_figure_manifest_v1",
        "renderer": f"matplotlib_{matplotlib.__version__}",
        "outputs": {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(outputs)},
        "claim_boundary": "Static displays of frozen results. Scientific FAIL and not_evaluable outcomes remain explicit; figures do not establish independence, convergence, adaptation or absolute rates.",
    }
    manifest_path = args.output_dir / "figure_manifest_v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
