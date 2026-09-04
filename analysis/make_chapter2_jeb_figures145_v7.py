#!/usr/bin/env python3
"""Generate JEB V7 Figures 1, 4 and 5 from frozen Chapter 2 evidence.

Figure 1 is descriptive radiation/configuration context; Figure 4 is the bounded
orientation history and present-regime persistence falsification; Figure 5 is
the historical-identifiability ceiling. No figure promotes sensitivity-grid
fractions to probabilities or reconstructed present-niche branches to observed
ancestral environments.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"

DARK = "#252525"
MID = "#777777"
LIGHT = "#D9DDE2"
PALE = "#F4F5F6"
BLUE = "#4C78A8"
ORANGE = "#F2A541"
GREEN = "#5A9367"
PURPLE = "#8A6FB0"
RED = "#B05A5A"


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, default=EVID / "chapter2_jeb_v7_figures145_contract_v1.json")
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v7")
    return p.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.titlesize": 9.5,
        "axes.labelsize": 8.0,
        "axes.linewidth": 0.8,
        "axes.edgecolor": DARK,
        "text.color": DARK,
        "xtick.color": DARK,
        "ytick.color": DARK,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def panel(ax, letter: str) -> None:
    ax.text(-0.07, 1.04, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom")


def save(fig, out: Path, stem: str, dpi: int) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    png = out / f"{stem}.png"
    pdf = out / f"{stem}.pdf"
    fig.savefig(png, dpi=dpi, bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)
    if png.stat().st_size < 20_000 or pdf.stat().st_size < 8_000:
        raise RuntimeError(f"unexpectedly small output for {stem}")
    return {
        "png": {"path": str(png), "bytes": png.stat().st_size, "sha256": sha256(png)},
        "pdf": {"path": str(pdf), "bytes": pdf.stat().st_size, "sha256": sha256(pdf)},
    }


def known_orientation(x: str) -> bool:
    return x not in {"unknown", "source_conflict_index_downward_detail_erect"}


def known(x: str) -> bool:
    return x != "unknown"


def validate_all(contract: dict, radiation: dict, scaffold: dict, seed: list[dict[str, str]], extension: list[dict[str, str]], combos: dict, hist: dict, rank: dict, claims: dict) -> list[dict[str, str]]:
    f1 = contract["figure1"]
    dom = radiation["dominant_main_radiation"]
    assert dom["japanese_species_sampled"] == f1["sampled_japanese_concepts"] == 38
    assert dom["species_in_main_radiation"] == f1["dominant_radiation_concepts"] == 36
    assert scaffold["current_qc_loci"] == f1["scaffold_qc_loci"] == 236
    assert scaffold["rootable_loci"] == f1["scaffold_rootable_loci"] == 176
    assert scaffold["alignment_length_bp"] == f1["alignment_length_bp"] == 161654
    assert scaffold["branch_length_semantics"].startswith("substitutions/site")
    assert len(seed) == f1["base_authority_rows"] == 22
    assert len(extension) == f1["extension_rows"] == 2
    ids = [r["paper_japan_member_id"] for r in seed + extension]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate authority row after extension")
    assert combos["n_dominant_orientation_stickiness_combinations"] == f1["dominant_orientation_stickiness_combinations"] == 4
    assert combos["n_dominant_seed_concepts"] == 20
    assert combos["n_secondary_seed_concepts"] == 2

    rows = sorted(seed + extension, key=lambda r: int(r["paper_japan_member_id"].split("_")[1]))
    final_counts = {
        "orientation": sum(known_orientation(r["orientation_state"]) for r in rows),
        "phyllary": sum(known(r["phyllary_posture"]) for r in rows),
        "stickiness": sum(known(r["stickiness_state"]) for r in rows),
    }
    assert final_counts == f1["resolved_trait_counts_after_extensions"] == {"orientation": 20, "phyllary": 10, "stickiness": 13}
    assert set(f1["secondary_ids_in_base_authority_panel"]) == {"JPN_06", "JPN_15"}

    f4 = contract["figure4"]
    oh = hist["orientation_historical_environment"]
    assert oh["chronology_pairs"] == f4["chronology_pairs"] == 94
    assert oh["paleolocation_regions"] == f4["regions"] == 4
    assert oh["region_by_chronology_scenarios"] == f4["scenarios"] == 376
    assert oh["central_pair_ma"] == f4["central_pair_ma"] == [0.79, 0.74]
    assert oh["central_pair_tendency"] == "BIO1, BIO4 and BIO15 decrease in all four regions; BIO12 increases in three of four"
    assert rank["classification"] == "relative_ordering_present_but_not_dominant"
    for region, count in f4["region_rank1_counts"].items():
        assert rank["region_rank_summary"][region]["rank1_count"] == count
    assert rank["pairwise_ordering"]["taiwan_minus_southern_japan"]["count_a_lt_b"] == f4["southern_japan_pairwise_win_counts"]["taiwan"] == 61
    assert rank["pairwise_ordering"]["ryukyu_corridor_minus_southern_japan"]["count_a_lt_b"] == f4["southern_japan_pairwise_win_counts"]["ryukyu_corridor"] == 61
    assert rank["pairwise_ordering"]["southern_japan_minus_east_asia_core_corridor"]["count_a_gt_b"] == f4["southern_japan_pairwise_win_counts"]["east_asia_core_corridor"] == 64
    h4 = claims["historical_persistence"]["h4"]
    assert h4["classification"] == f4["classification"] == "historical_regime_persistence_not_supported"
    assert h4["n_scenarios"] == 376
    assert h4["overall_match"] == f4["present_regime_historical_match"]["overall"]
    for region in ("taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor"):
        assert h4["per_region"][region] == f4["present_regime_historical_match"][region]

    f5 = contract["figure5"]
    climate = hist["lineage_level_climate_context"]
    sea = hist["global_sea_level_context"]
    assert climate["n_bioclim_variables"] == f5["bioclim_variables"] == 17
    assert climate["n_dated_lineage_contexts"] == f5["dated_lineage_contexts"] == 6
    assert climate["tested_scenario_variable_combinations"] == f5["scenario_variable_combinations"] == 15472
    assert climate["robust_event_level_classes"] == f5["robust_climate_event_classes"] == 0
    assert claims["historical_persistence"]["broader_climate_classes_robust"] == "0/324"
    assert sea["n_representative_groups"] == f5["sea_level_clade_groups"] == 3
    assert sea["n_event_metric_classes"] == f5["sea_level_event_metric_classes"] == 21
    assert sea["robust_event_metric_classes"] == f5["robust_sea_level_event_metric_classes"] == 0
    assert claims["historical_persistence"]["sea_level_classes_robust"] == "0/21"
    assert hist["calendar_identifiability"]["trait_transitions_with_calendar_paleolocation_environment_gate"] == 1
    return rows


def short_taxon(name: str) -> str:
    return name.replace("Cirsium ", "C. ")


def orientation_code(x: str) -> tuple[str, str]:
    if x == "downward_or_nodding": return "D", ORANGE
    if x == "upward_or_erect": return "U", BLUE
    if x == "upward_or_ascending": return "U/A", BLUE
    if x.startswith("source_conflict_"): return "!", RED
    return "·", LIGHT


def phyllary_code(x: str) -> tuple[str, str]:
    table = {
        "appressed": ("App", GREEN),
        "appressed_or_ascending": ("App/Asc", GREEN),
        "ascending": ("Asc", GREEN),
        "ascending_or_recurved": ("Asc/Rec", GREEN),
        "spreading": ("Spr", PURPLE),
        "spreading_or_recurved": ("Spr/Rec", PURPLE),
        "unknown": ("·", LIGHT),
    }
    return table.get(x, (x[:7], MID))


def stickiness_code(x: str) -> tuple[str, str]:
    if x == "sticky": return "Sticky", PURPLE
    if x == "nonsticky_or_nearly_nonsticky": return "Non", GREEN
    return "·", LIGHT


def make_figure1(contract: dict, rows: list[dict[str, str]], scaffold: dict, combos: dict, out: Path, dpi: int) -> dict:
    f1 = contract["figure1"]
    fig = plt.figure(figsize=(8.0, 8.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.85, 2.15], width_ratios=[1.0, 1.35], hspace=0.32, wspace=0.30)

    ax = fig.add_subplot(gs[0, 0])
    ax.barh([0], [36], color=BLUE, height=0.48, label="dominant radiation")
    ax.barh([0], [2], left=[36], color=LIGHT, edgecolor=MID, height=0.48, label="secondary histories")
    ax.text(18, 0, "36", ha="center", va="center", color="white", fontsize=17, fontweight="bold")
    ax.text(37, 0, "2", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, 38)
    ax.set_yticks([])
    ax.set_xlabel("Sampled Japanese taxon concepts")
    ax.set_title("Most sampled Japanese diversity lies in one radiation")
    ax.text(0.5, -0.30, "36 / 38 = 94.7% in the published dominant radiation", transform=ax.transAxes, ha="center", fontsize=7.2)
    panel(ax, "a")

    ax = fig.add_subplot(gs[0, 1])
    ax.axis("off")
    ax.add_patch(Rectangle((0.03, 0.12), 0.94, 0.76, transform=ax.transAxes, facecolor=PALE, edgecolor=DARK, lw=0.8))
    ax.text(0.07, 0.77, "Accepted common-locus nuclear scaffold", transform=ax.transAxes, fontweight="bold", fontsize=9.4)
    ax.text(0.07, 0.60, f"{scaffold['current_qc_loci']} QC loci   •   {scaffold['rootable_loci']} rootable", transform=ax.transAxes, fontsize=9)
    ax.text(0.07, 0.44, f"{scaffold['alignment_length_bp']:,} bp concatenated alignment", transform=ax.transAxes, fontsize=9)
    ax.text(0.07, 0.27, "Branch lengths = substitutions/site, not time", transform=ax.transAxes, fontsize=7.5, color=MID)
    ax.text(0.07, 0.16, "Context panel only; no topology is invented where a submission Newick is not frozen in-repo.", transform=ax.transAxes, fontsize=6.5, color=MID)

    ax = fig.add_subplot(gs[1, 0])
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xticks([0, 1, 2], ["Orientation", "Phyllary", "Stickiness"])
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", pad=7)
    labels = []
    secondary = set(f1["secondary_ids_in_base_authority_panel"])
    for i, r in enumerate(rows):
        cells = [orientation_code(r["orientation_state"]), phyllary_code(r["phyllary_posture"]), stickiness_code(r["stickiness_state"])]
        for j, (code, color) in enumerate(cells):
            ax.add_patch(Rectangle((j - 0.46, i - 0.42), 0.92, 0.84, facecolor=color, alpha=0.78, edgecolor="white", lw=0.6))
            ax.text(j, i, code, ha="center", va="center", fontsize=5.4, color="white" if color not in {LIGHT, GREEN} else DARK, fontweight="bold" if code not in {"·"} else "normal")
        star = " *" if r["paper_japan_member_id"] in secondary else ""
        labels.append(f"{r['paper_japan_member_id'].replace('JPN_', 'J')}: {short_taxon(r['paper_taxon_concept'])}{star}")
    ax.set_yticks(np.arange(len(rows)), labels, fontsize=5.5)
    ax.set_title("Authority-backed state matrix (missing/conflict retained)", pad=27)
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.text(0.0, -0.055, "* secondary-history comparator in the frozen base authority panel; ! = unresolved source conflict; · = unknown", transform=ax.transAxes, fontsize=6.2, color=MID)
    panel(ax, "b")

    ax = fig.add_subplot(gs[1, 1])
    cover = f1["resolved_trait_counts_after_extensions"]
    traits = ["Orientation", "Phyllary", "Stickiness"]
    vals = [cover["orientation"], cover["phyllary"], cover["stickiness"]]
    bars = ax.barh(np.arange(3)[::-1], vals, color=[BLUE, GREEN, PURPLE], height=0.55)
    ax.set_yticks(np.arange(3)[::-1], traits)
    ax.set_xlim(0, 38)
    ax.set_xlabel("Resolved authority-backed concepts")
    ax.set_title("Observed diversity before historical reconstruction")
    for b, v in zip(bars, vals):
        ax.text(v + 0.7, b.get_y() + b.get_height()/2, f"{v}/38", va="center", fontsize=8, fontweight="bold")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    combo_y = -1.15
    ax.text(0, combo_y, "Dominant-radiation orientation × stickiness combinations:", fontsize=7.4, fontweight="bold", transform=ax.transData)
    combos_list = combos["dominant_orientation_stickiness_combinations"]
    pretty = [x.replace("downward_or_nodding", "D").replace("upward_or_erect", "U").replace("upward_or_ascending", "U/A").replace("nonsticky_or_nearly_nonsticky", "nonsticky") for x in combos_list]
    for k, txt in enumerate(pretty):
        ax.text(0, combo_y - 0.36 - 0.34*k, f"• {txt}", fontsize=6.8, transform=ax.transData)
    ax.set_ylim(-2.7, 2.65)
    ax.text(0.5, -0.10, "Four named combinations demonstrate state diversity; they do not test correlated evolution.", transform=ax.transAxes, ha="center", fontsize=6.4, color=MID)
    panel(ax, "c")

    fig.suptitle("Figure 1. Multiple capitulum configurations occur within one young radiation", fontsize=11.5, y=0.995)
    fig.subplots_adjust(top=0.93, bottom=0.08, left=0.22, right=0.98)
    return save(fig, out, "figure1_v7_diversity_context", dpi)


def make_figure4(contract: dict, hist: dict, rank: dict, claims: dict, out: Path, dpi: int) -> dict:
    f4 = contract["figure4"]
    fig, axs = plt.subplots(2, 2, figsize=(8.1, 6.7))
    fig.subplots_adjust(hspace=0.47, wspace=0.34, top=0.90, bottom=0.10, left=0.10, right=0.98)

    ax = axs[0, 0]
    ax.set_xlim(0.82, 0.70)
    ax.set_ylim(-0.6, 1.1)
    ax.hlines(0, 0.82, 0.70, color=LIGHT, lw=5)
    ax.hlines(0, 0.79, 0.74, color=BLUE, lw=8)
    ax.plot([0.79, 0.74], [0, 0], "|", color=DARK, ms=14, mew=1.2)
    ax.text(0.765, 0.20, "central 0.79–0.74 Ma", ha="center", fontsize=8, fontweight="bold")
    ax.text(0.765, -0.30, "94 chronology pairs × 4 palaeolocation regions = 376 scenarios", ha="center", fontsize=7.4)
    ax.set_yticks([])
    ax.set_xlabel("Ma before present")
    ax.set_title("Only one orientation event reaches the full historical gate")
    panel(ax, "a")

    ax = axs[0, 1]
    regions = ["Taiwan", "Ryukyu", "Southern Japan", "East-Asia core"]
    keys = ["taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor"]
    counts = np.array([f4["region_rank1_counts"][k] for k in keys])
    pct = 100 * counts / 94
    bars = ax.bar(np.arange(4), pct, color=[MID, GREEN, BLUE, PURPLE], width=0.66)
    ax.axhline(75, color=RED, ls="--", lw=1)
    for b, c, p in zip(bars, counts, pct):
        ax.text(b.get_x()+b.get_width()/2, p+2, f"{c}/94", ha="center", fontsize=7)
    ax.set_xticks(np.arange(4), regions, rotation=18, ha="right")
    ax.set_ylim(0, 84)
    ax.set_ylabel("Ranked first across chronology grid (%)")
    ax.set_title("Southern Japan leads descriptively, not dominantly")
    ax.text(0.02, 0.95, "75% dominance gate", transform=ax.transAxes, color=RED, fontsize=6.5, va="top")
    ax.text(0.98, 0.04, "Southern Japan > Taiwan 61/94\n> Ryukyu 61/94\n> East-Asia core 64/94", transform=ax.transAxes, ha="right", fontsize=6.5, color=MID)
    panel(ax, "b")

    ax = axs[1, 0]
    ax.axis("off")
    ax.set_title("Central chronology has a coherent but descriptive trajectory", pad=10)
    traj = [("BIO1", "↓", "4/4"), ("BIO4", "↓", "4/4"), ("BIO15", "↓", "4/4"), ("BIO12", "↑", "3/4")]
    for i, (bio, arrow, n) in enumerate(traj):
        y = 0.82 - i*0.20
        ax.add_patch(Rectangle((0.08, y-0.06), 0.22, 0.12, transform=ax.transAxes, facecolor=PALE, edgecolor=LIGHT))
        ax.text(0.19, y, bio, transform=ax.transAxes, ha="center", va="center", fontweight="bold")
        ax.text(0.48, y, arrow, transform=ax.transAxes, ha="center", va="center", fontsize=18, color=BLUE if arrow == "↑" else ORANGE)
        ax.text(0.72, y, n + " regions", transform=ax.transAxes, va="center", fontsize=8)
    ax.text(0.50, 0.03, "Direction at 0.79–0.74 Ma only; not robust historical-trigger evidence.", transform=ax.transAxes, ha="center", fontsize=6.6, color=MID)
    panel(ax, "c")

    ax = axs[1, 1]
    labels = ["Overall", "Taiwan", "Ryukyu", "S. Japan", "E-Asia core"]
    vals = [26.3, 21.3, 9.6, 43.6, 30.9]
    nums = ["99/376", "20/94", "9/94", "41/94", "29/94"]
    bars = ax.barh(np.arange(5)[::-1], vals, color=[DARK, MID, GREEN, BLUE, PURPLE], height=0.55)
    ax.axvline(75, color=RED, ls="--", lw=1)
    for b, v, n in zip(bars, vals, nums):
        ax.text(v+1.5, b.get_y()+b.get_height()/2, f"{n} ({v:.1f}%)", va="center", fontsize=6.6)
    ax.set_yticks(np.arange(5)[::-1], labels)
    ax.set_xlim(0, 86)
    ax.set_xlabel("Scenarios matching current U→D regime (%)")
    ax.set_title("Current BIO15↑ + BIO1↓ regime does not persist at origin")
    ax.text(0.02, -0.23, "Central chronology fails in 4/4 regions because BIO15 decreases, opposite the current U→D direction.", transform=ax.transAxes, fontsize=6.4, color=MID)
    panel(ax, "d")

    fig.suptitle("Figure 4. Bounded orientation history: tendency versus uncertainty", fontsize=11.5)
    return save(fig, out, "figure4_v7_bounded_history", dpi)


def make_figure5(contract: dict, hist: dict, out: Path, dpi: int) -> dict:
    f5 = contract["figure5"]
    fig = plt.figure(figsize=(8.0, 6.8))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.5, 0.75], width_ratios=[1.45, 0.8, 0.8], hspace=0.42, wspace=0.33)

    ax = fig.add_subplot(gs[:, 0])
    ax.axis("off")
    steps = f5["identifiability_steps"]
    widths = np.linspace(0.96, 0.55, len(steps))
    colors = [BLUE, BLUE, BLUE, GREEN, MID, ORANGE, RED]
    for i, (txt, w, col) in enumerate(zip(steps, widths, colors)):
        y = 0.91 - i*0.125
        x = 0.5 - w/2
        ax.add_patch(Rectangle((x, y-0.047), w, 0.094, transform=ax.transAxes, facecolor=col, alpha=0.82, edgecolor="white"))
        ax.text(0.5, y, txt, transform=ax.transAxes, ha="center", va="center", fontsize=6.6, color="white" if col != ORANGE else DARK, fontweight="bold" if i in {0,1,2,3,6} else "normal")
    ax.text(0.5, 0.015, "Increasing historical specificity → fewer directly identifiable links", transform=ax.transAxes, ha="center", fontsize=7, color=MID)
    ax.set_title("Identifiability narrows from assembly to cause", pad=10)
    panel(ax, "a")

    ax = fig.add_subplot(gs[0, 1])
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 0.10), 0.90, 0.80, transform=ax.transAxes, facecolor=PALE, edgecolor=DARK, lw=0.8))
    ax.text(0.5, 0.67, "0 / 324", transform=ax.transAxes, ha="center", fontsize=24, fontweight="bold", color=RED)
    ax.text(0.5, 0.48, "robust climate\nevent-level classes", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.25, "17 BIOCLIM variables\n6 dated lineage contexts\n15,472 scenario × variable tests", transform=ax.transAxes, ha="center", fontsize=6.7, color=MID)
    ax.set_title("Broader climate diagnostic")
    panel(ax, "b")

    ax = fig.add_subplot(gs[0, 2])
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 0.10), 0.90, 0.80, transform=ax.transAxes, facecolor=PALE, edgecolor=DARK, lw=0.8))
    ax.text(0.5, 0.67, "0 / 21", transform=ax.transAxes, ha="center", fontsize=24, fontweight="bold", color=RED)
    ax.text(0.5, 0.48, "robust sea-level\nevent-metric classes", transform=ax.transAxes, ha="center", fontsize=8)
    ax.text(0.5, 0.27, "3 representative clades\n× 7 metrics", transform=ax.transAxes, ha="center", fontsize=7, color=MID)
    ax.set_title("Global eustatic diagnostic")
    panel(ax, "c")

    ax = fig.add_subplot(gs[1, 1:])
    ax.axis("off")
    ax.add_patch(Rectangle((0.02, 0.12), 0.96, 0.78, transform=ax.transAxes, facecolor="#F7F7F7", edgecolor=DARK, lw=1.0))
    ax.text(0.5, 0.70, "Phenotypic assembly is identifiable farther", transform=ax.transAxes, ha="center", fontsize=11, fontweight="bold", color=BLUE)
    ax.text(0.5, 0.50, "than one recurring coarse historical cause", transform=ax.transAxes, ha="center", fontsize=11, fontweight="bold", color=RED)
    ax.text(0.5, 0.27, "0/324 and 0/21 bound the tested coarse explanations; they do not imply environmental irrelevance or reconstruct local land connectivity.", transform=ax.transAxes, ha="center", fontsize=6.6, color=MID, wrap=True)
    panel(ax, "d")

    fig.suptitle("Figure 5. Historical identifiability ceiling", fontsize=11.5, y=0.98)
    return save(fig, out, "figure5_v7_identifiability_ceiling", dpi)


def main() -> int:
    a = args()
    contract = load_json(a.contract)
    radiation = load_json(EVID / "japan_cirsium_origin_meta_analysis_v1.json")
    scaffold = load_json(EVID / "japan38_comp1061_primary_tree_acceptance_v1.json")
    seed = load_csv(EVID / "japan38_nmns_capitulum_trait_seed_v1.csv")
    extension = load_csv(EVID / "japan38_nmns_capitulum_trait_seed_extension_v2.csv")
    combos = load_json(EVID / "japan38_authority_module_combinations_v1.json")
    hist = load_json(EVID / "chapter2_historical_differentiation_final_summary_v1.json")
    rank = load_json(EVID / "chapter2_orientation_origin_region_ranking_result_v1.json")
    claims = load_json(EVID / "chapter2_current_claims_h1_h4_v1.json")
    rows = validate_all(contract, radiation, scaffold, seed, extension, combos, hist, rank, claims)
    style()
    dpi = int(contract["output"]["png_dpi"])
    outputs = {
        "figure1": make_figure1(contract, rows, scaffold, combos, a.output_dir, dpi),
        "figure4": make_figure4(contract, hist, rank, claims, a.output_dir, dpi),
        "figure5": make_figure5(contract, hist, a.output_dir, dpi),
    }
    manifest = {
        "version": "chapter2_jeb_v7_figures145_manifest_v1",
        "status": "ok",
        "contract": str(a.contract),
        "outputs": outputs,
        "claim_boundary": "Figures are displays of frozen evidence. Descriptive diversity is not transition history; sensitivity-grid ranks are not probabilities; no figure establishes historical climatic causation, adaptation, selection, or environmental irrelevance."
    }
    manifest_path = a.output_dir / "figures145_v7_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
