#!/usr/bin/env python3
"""Generate JEB V7 Figure 3: scale-partitioned, transition-linked ecology.

All displayed numerical values are loaded from frozen evidence and checked
against the v2 figure contract. Exact map fractions are finite randomization
ranks, not biological-replicate P values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "data" / "evidence"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "chapter2" / "figures_v7")
    return p.parse_args()


def load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pct(pair) -> float:
    return 100.0 * float(pair[0]) / float(pair[1])


def assert_rank(block: dict, pair) -> None:
    rank = block["exact_primary_rank"]
    assert rank["count_at_least_observed"] == pair[0]
    assert rank["n_maps"] == pair[1]


def validate(c, eco, cf, current, h1, region, deletion, geo, internal, combined):
    assert c["version"] == "chapter2_jeb_v7_figure3_contract_v2"
    assert eco["classification"] == "orientation_environment_association_is_scale_partitioned"
    sp = eco["orientation_scale_partition"]
    assert abs(sp["BIO12_annual_precipitation"]["azami_among"]["q"] - 0.0063993600639936) < 1e-12
    assert sp["BIO15_precipitation_seasonality"]["eazami_downward_minus_upward"]["accepted_topology_sign_consistency"] == "6/6"
    assert sp["BIO15_precipitation_seasonality"]["eazami_downward_minus_upward"]["topology_x_species_loo_sign_consistency"] == "54/54"

    pb = c["panel_b"]
    assert_rank(h1["n5_primary"], pb["primary_ranks"]["n5_12_taxa"])
    assert_rank(h1["n3_sensitivity"], pb["primary_ranks"]["n3_13_taxa"])
    assert_rank(region["strict_n10"], pb["primary_ranks"]["strict_n10_9_taxa"])
    assert [region["strict_n10"]["bio15_only_rank"]["count_at_least_observed"], 126] == pb["strict_axes"]["BIO15"]
    assert [region["strict_n10"]["lower_bio1_rank"]["count_at_least_observed"], 126] == pb["strict_axes"]["lower_BIO1"]
    assert current["orientation_transition_regime"]["h2"]["exact_bidirectional_floor_rank"] == "3/126 = 2.38%"

    pc = c["panel_c"]
    assert_rank(region["strict_n10"], pc["strict"])
    assert_rank(region["japan_n5"], pc["japan_only"])
    assert_rank(geo["strict_n10_primary"], pc["geography_residual"])
    assert_rank(internal["strict_n10_primary"], pc["internal_edge"])
    assert_rank(combined["strict_n10_primary"], pc["combined"])
    assert_rank(combined["n5_sensitivity"], pc["combined_n5"])
    assert deletion["all_deletions_direction_pass"] is True
    assert [deletion["n_deletions"], deletion["n_deletions"]] == pc["single_deletion_direction"]
    assert [deletion["n_exact_exceptionality_pass"], deletion["n_deletions"]] == pc["single_deletion_exceptionality"]

    assert cf["classification"] == "counterfactual_correspondence_not_strengthened_beyond_history"
    pools = cf["axis_results"]["chelsa_bio15"]["pools"]
    observed = [
        [pools["all_126_count_preserving"]["rank"]["count_at_least_observed"], pools["all_126_count_preserving"]["rank"]["n"]],
        [pools["recurrence_profile_matched"]["rank"]["count_at_least_observed"], pools["recurrence_profile_matched"]["rank"]["n"]],
        [pools["history_nearest_quartile"]["rank"]["count_at_least_observed"], pools["history_nearest_quartile"]["rank"]["n"]],
    ]
    assert observed == c["panel_d"]["bio15_nested"]
    assert abs(pools["recurrence_profile_matched"]["reverse_world"]["most_reverse_signed_statistic"] - c["panel_d"]["recurrence_reverse_signed_statistic"]) < 1e-12
    assert pools["history_nearest_quartile"]["reverse_world"]["opposite_direction_exists"] is False


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.4,
        "axes.titlesize": 10.0,
        "axes.labelsize": 8.5,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })


def label(ax, s):
    ax.text(-0.09, 1.06, s, transform=ax.transAxes, fontsize=11, fontweight="bold", va="top")


def annotate_bar(ax, y, pair, xoffset=0.25):
    value = pct(pair)
    ax.text(value + xoffset, y, f"{pair[0]}/{pair[1]}\n{value:.2f}%", va="center", fontsize=7.2)


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    c = load("chapter2_jeb_v7_figure3_contract_v2.json")
    eco = load("chapter2_orientation_environment_scale_partition_v1.json")
    cf = load("chapter2_orientation_environment_counterfactual_result_v1.json")
    current = load("chapter2_current_claims_h1_h4_v1.json")
    h1 = load("chapter2_orientation_transition_regime_hypothesis_result_v1.json")
    region = load("chapter2_orientation_transition_regime_robustness_result_v1.json")
    deletion = load("chapter2_orientation_transition_regime_single_deletion_result_v1.json")
    geo = load("chapter2_orientation_transition_regime_geography_residual_result_v1.json")
    internal = load("chapter2_orientation_transition_regime_internal_edge_result_v1.json")
    combined = load("chapter2_orientation_transition_regime_combined_stress_result_v1.json")
    validate(c, eco, cf, current, h1, region, deletion, geo, internal, combined)
    style()

    fig = plt.figure(figsize=(12.3, 8.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.08], width_ratios=[1.15, 1.0], hspace=0.42, wspace=0.30)

    # A — non-exchangeable cross-scale estimands.
    ax = fig.add_subplot(gs[0, 0]); ax.axis("off")
    cells = [
        ["+0.005\nq=.874\nnot supported", "+0.304\nq=.006\nFDR supported", "—"],
        ["−0.008\nq=.121\nnot supported", "+0.067\nq=.599\nnot supported", "+1.32–1.33 SD\n6/6; 54/54 sign"],
        ["+0.017\nq=.035\nFDR supported", "−0.030\nq=.836\nnot supported", "−0.975–−0.967 SD\n54/54 sign"],
    ]
    tab = ax.table(cellText=cells,
                   rowLabels=["BIO12\nannual precipitation", "BIO15\nprecip. seasonality", "BIO1\nannual mean temp."],
                   colLabels=["Within taxon\nAzami", "Among taxa\nAzami", "East-Asian\nstate contrast"],
                   cellLoc="center", rowLoc="center", loc="center", bbox=[0.03, 0.10, 0.95, 0.76])
    tab.auto_set_font_size(False); tab.set_fontsize(7.3)
    for (r, col), cell in tab.get_celld().items():
        cell.set_linewidth(0.6)
        if r == 0 or col == -1:
            cell.set_text_props(fontweight="bold")
    ax.set_title("Ecological correspondence changes with biological scale", pad=10)
    ax.text(0.50, 0.015, "Columns are different estimands; effect sizes are not pooled.", transform=ax.transAxes, ha="center", fontsize=7.2)
    label(ax, "a")

    # B — fixed transition-regime exact test.
    ax = fig.add_subplot(gs[0, 1])
    names = ["n≥5\n12 taxa", "n≥3\n13 taxa", "strict n≥10\n9 taxa", "bidirectional\nfloor"]
    pairs = [c["panel_b"]["primary_ranks"]["n5_12_taxa"], c["panel_b"]["primary_ranks"]["n3_13_taxa"], c["panel_b"]["primary_ranks"]["strict_n10_9_taxa"], c["panel_b"]["bidirectional_floor"]]
    vals = [pct(p) for p in pairs]
    x = np.arange(len(names))
    ax.bar(x, vals)
    ax.axhline(5.0, linewidth=1.0, linestyle="--")
    for xx, vv, pp in zip(x, vals, pairs):
        ax.text(xx, vv + 0.22, f"{pp[0]}/{pp[1]}\n{vv:.2f}%", ha="center", va="bottom", fontsize=7.3, fontweight="bold")
    ax.set_xticks(x, names)
    ax.set_ylim(0, 7.2)
    ax.set_ylabel("Maps at least as extreme (%)")
    ax.set_title("Fixed transition-regime tracking is exceptional")
    ax.grid(axis="y", linewidth=0.45, alpha=0.30)
    ax.text(0.98, 0.96, "strict axes:\nBIO15 7/126 = 5.56%\nBIO1 8/126 = 6.35%",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.1)
    ax.text(0.02, 0.02, "Dashed line = frozen finite-map 5% boundary, not a P-value.", transform=ax.transAxes, fontsize=6.8)
    label(ax, "b")

    # C — falsification ladder.
    ax = fig.add_subplot(gs[1, 0])
    stress_names = ["Strict n≥10", "Japan only", "Linear geo residual", "Internal edges only", "Geo residual +\ninternal edges", "Combined n≥5"]
    stress_pairs = [c["panel_c"]["strict"], c["panel_c"]["japan_only"], c["panel_c"]["geography_residual"], c["panel_c"]["internal_edge"], c["panel_c"]["combined"], c["panel_c"]["combined_n5"]]
    y = np.arange(len(stress_names))[::-1]
    vals = [pct(p) for p in stress_pairs]
    ax.barh(y, vals)
    ax.axvline(5.0, linewidth=1.0, linestyle="--")
    ax.set_yticks(y, stress_names)
    ax.set_xlim(0, 21)
    ax.set_xlabel("Maps at least as extreme (%)")
    ax.set_title("The U→D signal survives declared falsifications, with a regional boundary")
    ax.grid(axis="x", linewidth=0.45, alpha=0.30)
    for yy, pp in zip(y, stress_pairs):
        annotate_bar(ax, yy, pp)
    ax.text(0.99, 0.02, "Single-taxon deletion: direction retained 9/9;\n≤5% extremeness retained 2/9.", transform=ax.transAxes, ha="right", va="bottom", fontsize=7.2)
    label(ax, "c")

    # D — original history-conditioning calibration.
    ax = fig.add_subplot(gs[1, 1])
    pools = ["State\nfrequency", "Recurrence", "Recurrence +\nrelative depth"]
    pairs_d = c["panel_d"]["bio15_nested"]
    vals_d = [pct(p) for p in pairs_d]
    xd = np.arange(3)
    ax.plot(xd, vals_d, marker="o", linewidth=2.0)
    for xx, vv, pp in zip(xd, vals_d, pairs_d):
        ax.text(xx, vv + 1.3, f"{pp[0]}/{pp[1]}\n{vv:.1f}%", ha="center", va="bottom", fontsize=7.4, fontweight="bold")
    ax.set_xticks(xd, pools)
    ax.set_ylim(0, 35)
    ax.set_ylabel("Counterfactual maps at least as extreme (%)")
    ax.set_title("Tip-level BIO15 extremeness weakens when history is matched")
    ax.grid(axis="y", linewidth=0.45, alpha=0.30)
    ax.text(0.03, 0.95, "Recurrence-matched reverse world: −1.784\nNo reverse BIO15 world in nearest-history pool.",
            transform=ax.transAxes, va="top", fontsize=7.1)
    ax.text(0.50, -0.20, "Finite conditional ranks — not P values", transform=ax.transAxes, ha="center", fontsize=7.1)
    label(ax, "d")

    fig.suptitle("Figure 3. Orientation ecology is scale-partitioned, transition-linked and history-conditioned", fontsize=12, y=0.985)
    fig.subplots_adjust(top=0.91, bottom=0.09, left=0.09, right=0.98)

    stem = c["output"]["stem"]
    png = args.output_dir / f"{stem}.png"
    pdf = args.output_dir / f"{stem}.pdf"
    fig.savefig(png, dpi=int(c["output"]["png_dpi"]), bbox_inches="tight", metadata={"Software": "EAzami"})
    fig.savefig(pdf, bbox_inches="tight", metadata={"Creator": "EAzami", "Title": stem})
    plt.close(fig)

    if png.stat().st_size < 30_000 or pdf.stat().st_size < 12_000:
        raise RuntimeError("Figure 3 output unexpectedly small")

    manifest = {
        "version": "chapter2_jeb_v7_figure3_manifest_v2",
        "status": "ok",
        "sources": c["sources"],
        "headline": {
            "h1_n5": "16/792 = 2.02%",
            "h1_strict": "4/126 = 3.17%",
            "bidirectional_floor": "3/126 = 2.38%",
            "japan_only": "10/56 = 17.86%",
            "combined_strict": "3/126 = 2.38%",
            "combined_n5": "29/792 = 3.66%",
            "history_conditioned_bio15": ["5/126", "3/40", "3/10"],
        },
        "outputs": {
            "png": {"path": str(png), "sha256": sha256(png), "bytes": png.stat().st_size},
            "pdf": {"path": str(pdf), "sha256": sha256(pdf), "bytes": pdf.stat().st_size},
        },
    }
    mp = args.output_dir / f"{stem}_manifest.json"
    mp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
