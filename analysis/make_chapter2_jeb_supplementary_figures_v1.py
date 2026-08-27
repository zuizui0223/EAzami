#!/usr/bin/env python3
"""Generate the five Chapter 2 JEB supplementary figures from frozen evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze_japan_origin_global_tree import NewickParser

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"
TIME = EVID / "chapter2_time_axis_compute"
PROV = EVID / "chapter2_provenance_sensitivity_compute"

BLUE = "#2F5D8A"
GOLD = "#C58A1C"
RED = "#9B4B4B"
DARK = "#222222"
MID = "#6F7782"
LIGHT = "#D9DDE3"
PALE = "#F4F5F7"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "docs" / "chapter2" / "figures" / "supplementary",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.3,
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
    ax.text(-0.11, 1.06, label, transform=ax.transAxes, fontweight="bold", fontsize=11, va="top")


def save(fig, out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    png = out_dir / f"{stem}.png"
    pdf = out_dir / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)
    return [png, pdf]


def short_taxon(text: str) -> str:
    parts = text.replace("Cirsium ", "").split()
    if not parts:
        return "Cirsium"
    keep = [parts[0]]
    if len(parts) >= 3 and parts[1] in {"var.", "subsp."}:
        keep.extend(parts[1:3])
    return "C. " + " ".join(keep)


def figure_s1(out_dir: Path) -> list[Path]:
    root = NewickParser((EVID / "japan38_comp1061_primary_tree_v1.nwk").read_text(encoding="utf-8")).parse()
    mapping = pd.read_csv(EVID / "japan38_comp1061_concept_map_v1.csv")
    tip_to_row: dict[str, pd.Series] = {}
    for _, row in mapping.iterrows():
        for tip in str(row["tip_ids"]).split("|"):
            tip_to_row[tip] = row

    tips = []

    def collect(node) -> None:
        if node.is_tip:
            tips.append(node)
            return
        for child in node.children:
            collect(child)

    collect(root)
    y_pos = {node: float(i) for i, node in enumerate(tips)}
    x_pos: dict[object, float] = {}

    def place(node, parent_x: float = 0.0) -> float:
        x = parent_x + float(node.length or 0.0)
        x_pos[node] = x
        if node.is_tip:
            return y_pos[node]
        ys = [place(child, x) for child in node.children]
        y_pos[node] = float(np.mean(ys))
        return y_pos[node]

    place(root)
    max_x = max(x_pos.values())
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    for node in list(x_pos):
        if node.is_tip:
            continue
        child_y = [y_pos[c] for c in node.children]
        ax.vlines(x_pos[node], min(child_y), max(child_y), color=MID, lw=0.55)
        for child in node.children:
            ax.hlines(y_pos[child], x_pos[node], x_pos[child], color=MID, lw=0.55)

    replicate_seen: dict[str, int] = {}
    for node in tips:
        if node.name == "OUTGROUP_saff":
            label, color, marker, fill = "OUTGROUP  Carthamus tinctorius", MID, "o", MID
        else:
            row = tip_to_row[node.name]
            member = str(row["paper_japan_member_id"])
            replicate_seen[member] = replicate_seen.get(member, 0) + 1
            suffix = chr(96 + replicate_seen[member]) if int(row["n_biological_samples"]) > 1 else ""
            label = f"{member}{suffix}  {short_taxon(str(row['paper_taxon_concept']))}"
            color, marker, fill = DARK, "o", DARK
            if member == "JPN_20":
                color, marker, fill = GOLD, "s", "white"
            elif member == "JPN_29":
                color, marker, fill = GOLD, "o", "white"
            elif member == "JPN_31":
                color, marker, fill = RED, "x", RED
        ax.plot(x_pos[node], y_pos[node], marker=marker, ms=3.2, color=color, mfc=fill, mew=0.9)
        ax.text(max_x + max_x * 0.018, y_pos[node], label, va="center", fontsize=5.3, color=color)

    ax.plot([], [], "s", color=GOLD, mfc="white", label="JPN20: two samples; not collapsed")
    ax.plot([], [], "o", color=GOLD, mfc="white", label="JPN29: identity/provenance warning")
    ax.plot([], [], "x", color=RED, label="JPN31: excluded from primary trait history")
    ax.legend(frameon=False, fontsize=6.7, loc="center", bbox_to_anchor=(0.39, 0.48), ncol=1)
    ax.set_xlim(-max_x * 0.015, max_x * 1.55)
    ax.set_ylim(-1.2, len(tips) + 1.0)
    ax.set_yticks([])
    ax.set_xlabel("Branch length (substitutions per site; not absolute time)")
    ax.set_title("Figure S1. Frozen Japan38 Comp1061 phylogram and admission exceptions")
    ax.text(
        0.99,
        0.01,
        "236/241 QC loci | 176 rootable loci | 1,000 UFBoot",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.7,
        color=MID,
    )
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    return save(fig, out_dir, "figure_s1_tree_admission")


UNIT_LABELS = {
    "orientation_image_vertical_angle": "Orientation angle",
    "corolla_lab_lightness": "Corolla L*",
    "corolla_lab_chroma": "Corolla chroma",
    "corolla_hue": "Corolla hue",
    "capitulum_outline_aspect_ratio": "Outline aspect ratio",
    "capitulum_outline_circularity": "Outline circularity",
    "capitulum_outline_solidity": "Outline solidity",
    "capitulum_width_profile_cv": "Width-profile CV",
}


def plot_state_rows(
    ax,
    data: pd.DataFrame,
    scopes: list[tuple[str, str, str]],
    title: str,
    *,
    legend_loc: str = "lower right",
) -> None:
    units = list(UNIT_LABELS)
    y = np.arange(len(units))[::-1]
    offsets = np.linspace(0.15, -0.15, len(scopes)) if len(scopes) > 1 else [0.0]
    colors = [BLUE, GOLD, MID]
    for offset, (scope, label, marker), color in zip(offsets, scopes, colors):
        subset = data[data["scope"] == scope].set_index("unit_id")
        for yy, unit in zip(y, units):
            row = subset.loc[unit]
            x = float(row["rho_patristic_vs_trait_distance"])
            lo, hi = float(row["loo_min_rho"]), float(row["loo_max_rho"])
            ax.hlines(yy + offset, lo, hi, color=color, lw=1.35, alpha=0.9)
            ax.plot(x, yy + offset, marker=marker, color=color, mfc="white", mew=1.2, ms=5.2)
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_yticks(y, [UNIT_LABELS[u] for u in units])
    ax.set_xlim(-1.0, 1.0)
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.set_xlabel("Patristic distance vs trait-distance Spearman rho")
    ax.set_title(title)
    for (scope, label, marker), color in zip(scopes, colors):
        ax.plot([], [], marker=marker, color=color, mfc="white", label=label)
    ax.legend(frameon=False, fontsize=7, loc=legend_loc)


def figure_s2(out_dir: Path) -> list[Path]:
    original = pd.read_csv(TIME / "continuous_primary_phylogenetic_structure_v1.csv")
    sensitivity = pd.read_csv(PROV / "continuous_primary_phylogenetic_structure_v1.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.4), sharey=True)
    plot_state_rows(
        axes[0],
        original,
        [("nobs_ge_2", ">=2 observations", "o"), ("nobs_ge_5", ">=5 observations", "s")],
        "Original frozen families",
    )
    panel_label(axes[0], "a")
    plot_state_rows(
        axes[1],
        sensitivity,
        [("nobs_ge_2", "JPN29 excluded, >=2", "o")],
        "Fixed identity-provenance sensitivity",
        legend_loc="upper right",
    )
    axes[1].text(
        0.98,
        0.04,
        ">=5 family: NOT EVALUABLE\n5 concepts < frozen minimum of 6",
        transform=axes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=7.3,
        fontweight="bold",
        color=MID,
        bbox={"boxstyle": "square,pad=0.3", "fc": "white", "ec": MID, "ls": "--"},
    )
    panel_label(axes[1], "b")
    fig.suptitle("Figure S2. Continuous state-structure estimates and leave-one-out ranges", y=1.02, fontsize=11)
    fig.text(0.5, 0.005, "All evaluable rows are two_sided_not_supported after family correction; intervals show leave-one-concept-out rho ranges.", ha="center", fontsize=7.2, color=MID)
    return save(fig, out_dir, "figure_s2_continuous_state_structure")


def figure_s3(out_dir: Path) -> list[Path]:
    source = read_json(TIME / "japan38_continuous_branch_change_topology_sensitivity_v1.json")
    d = source["global_mean_pairwise_rho_distribution"]
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    y = 0.0
    ax.hlines(y, d["min"], d["max"], color=MID, lw=1.2)
    ax.hlines(y, d["q05"], d["q95"], color=BLUE, lw=6)
    ax.hlines(y, d["q25"], d["q75"], color="white", lw=2.0)
    ax.plot(d["median"], y, "o", color=BLUE, mfc="white", mew=1.5, ms=7, label="Topology median")
    ml = source["ml_equal_branch"]["global_mean_pairwise_rho"]
    ax.plot(ml, y + 0.12, "D", color=GOLD, ms=5, label="Equal-branch ML")
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_xlim(-0.02, 0.28)
    ax.set_ylim(-0.45, 0.45)
    ax.set_yticks([])
    ax.set_xlabel("Equal-branch mean pairwise rho")
    ax.set_title("Figure S3. Equal-branch continuous topology diagnostic")
    ax.grid(axis="x", color=LIGHT, lw=0.7)
    ax.legend(frameon=False, loc="lower right", fontsize=7)
    ax.text(0.02, 0.86, "1,000/1,000 positive", transform=ax.transAxes, fontweight="bold")
    ax.text(0.02, 0.71, "DIAGNOSTIC ONLY | includes JPN29 | no topology-specific null", transform=ax.transAxes, color=MID, fontsize=7.2)
    return save(fig, out_dir, "figure_s3_equal_branch_topology")


def figure_s4(out_dir: Path) -> list[Path]:
    source = read_json(EVID / "japan7_source_balanced_lightness_history_v1.json")
    pairwise = pd.DataFrame(source["pairwise_values"])
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    ax.scatter(pairwise["patristic_distance"], pairwise["absolute_lightness_difference"], s=25, facecolors="white", edgecolors=BLUE, linewidths=1.2)
    ax.set_xlabel("Patristic distance (substitutions/site)")
    ax.set_ylabel("Absolute corolla L* difference")
    ax.set_title("Source-balanced Japan7 pairwise distances")
    ax.grid(color=LIGHT, lw=0.6)
    ax.text(0.04, 0.93, "rho = +0.2675\nnegative-tail P = 0.7579\nFAIL", transform=ax.transAxes, va="top", fontweight="bold")
    panel_label(ax, "a")

    ax = axes[1]
    primary = [source["primary_signal"]["rho"]]
    concept = list(source["concept_leave_one_out"]["rho_by_omitted_concept"].values())
    sparse = [row["rho"] for row in source["sparse_observation_leave_one_out"]["cases"]]
    groups = [(1, primary, GOLD, "Primary"), (2, concept, BLUE, "Concept LOO"), (3, sparse, MID, "Observation LOO")]
    for x, values, color, label in groups:
        offsets = np.linspace(-0.12, 0.12, len(values)) if len(values) > 1 else [0.0]
        ax.scatter(np.asarray(offsets) + x, values, s=26, facecolors="white", edgecolors=color, linewidths=1.2, label=label)
    ax.axhline(0, color=DARK, lw=0.8)
    ax.set_xticks([1, 2, 3], ["Primary", "Concept\nLOO", "Observation\nLOO"])
    ax.set_ylabel("Patristic vs L* distance rho")
    ax.set_ylim(-0.15, 0.75)
    ax.set_title("Direction-stability checks")
    ax.grid(axis="y", color=LIGHT, lw=0.6)
    ax.text(0.5, 0.04, "All leave-one-out directions positive", transform=ax.transAxes, ha="center", fontsize=7.2, color=MID)
    panel_label(ax, "b")
    fig.suptitle("Figure S4. Source-balanced lightness does not replicate the preregistered negative direction", y=1.02, fontsize=11)
    return save(fig, out_dir, "figure_s4_lightness_nonreplication")


def figure_s5(out_dir: Path) -> list[Path]:
    source = read_json(EVID / "hmm2_population_aware_transition_test_v1.json")
    stage_b = source["stage_B_minimum_transition_count"]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.4), gridspec_kw={"width_ratios": [1, 1.35]})
    ax = axes[0]
    values = [stage_b["takaoense_species_tip_minimum"], stage_b["takaoense_population_sample_minimum"]]
    bars = ax.bar([0, 1], values, color=[LIGHT, BLUE], edgecolor=[MID, BLUE], width=0.62)
    ax.set_xticks([0, 1], ["One species tip", "Morph-linked\nsamples retained"])
    ax.set_ylabel("Minimum unordered changes")
    ax.set_ylim(0, 2.6)
    ax.set_yticks([0, 1, 2])
    ax.set_title("C. japonicum var. takaoense")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.08, str(value), ha="center", fontweight="bold")
    panel_label(ax, "a")

    ax = axes[1]
    labels = ["W/C multiplicity documented", "Morph-linked genealogy testable", "Replicated rate testable"]
    numerators = [4, 1, 0]
    denominators = [4, 4, 4]
    ypos = np.arange(3)[::-1]
    ax.barh(ypos, denominators, color=PALE, edgecolor=LIGHT, height=0.55)
    ax.barh(ypos, numerators, color=[BLUE, GOLD, MID], height=0.55)
    ax.set_yticks(ypos, labels)
    ax.set_xlim(0, 4)
    ax.set_xticks(range(5))
    ax.set_xlabel("Reviewed polymorphic systems")
    ax.set_title("Information-resolution ladder")
    for yy, num, den in zip(ypos, numerators, denominators):
        ax.text(den - 0.08, yy, f"{num}/{den}", ha="right", va="center", fontweight="bold")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    panel_label(ax, "b")
    fig.suptitle("Figure S5. Species-tip compression can erase a recent transition", y=1.02, fontsize=11)
    fig.text(0.5, 0.005, "Single-system minimum-count result; not a general transition-rate estimate.", ha="center", fontsize=7.2, color=MID)
    return save(fig, out_dir, "figure_s5_species_tip_compression")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    style()
    outputs: list[Path] = []
    outputs += figure_s1(args.output_dir)
    outputs += figure_s2(args.output_dir)
    outputs += figure_s3(args.output_dir)
    outputs += figure_s4(args.output_dir)
    outputs += figure_s5(args.output_dir)
    manifest = {
        "contract_version": "chapter2_jeb_supplementary_figure_manifest_v1",
        "renderer": f"matplotlib_{matplotlib.__version__}",
        "outputs": {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(outputs)},
        "claim_boundary": "Supplementary displays of frozen evidence. They preserve identity warnings, scientific FAIL, not_evaluable, substitutions/site and single-system boundaries.",
    }
    manifest_path = args.output_dir / "supplementary_figure_manifest_v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
