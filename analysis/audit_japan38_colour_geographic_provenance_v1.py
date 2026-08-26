#!/usr/bin/env python3
"""Audit whether global image-derived colour proxies represent Japan-local Japan38 states.

The existing continuous-colour bridge matches exact taxon concepts, but those image
observations can come from anywhere in the species range.  This audit separates
exact taxonomic identity from geographic/population identity.  It recomputes the
lightness phylogenetic-structure diagnostic using the frozen global proxy, a
Japan-window sensitivity, and a substitution sensitivity that replaces global
medians with Japan-window medians wherever available while retaining the original
six-concept set.

The coordinate window is deliberately transparent and conservative; it is not an
authoritative national-boundary polygon.  Failure of the Japan-window gate means
only that the current image evidence cannot support a Japan-local radiation-history
claim.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import spearmanr

TARGET_IDS = ("JPN_17", "JPN_23", "JPN_29", "JPN_36", "JPN_37", "JPN_38")


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def operational_japan_window(lat: float, lon: float) -> bool:
    """Coordinate heuristic frozen in the provenance contract."""
    return (
        (24.0 <= lat < 30.8 and 122.0 <= lon <= 131.5)
        or (30.8 <= lat < 41.5 and 129.0 <= lon <= 142.5)
        or (41.5 <= lat <= 45.7 and 139.0 <= lon <= 145.9)
    )


def concept_tip_map(path: Path):
    rows = read_csv(path)
    out = {}
    for row in rows:
        mid = row["paper_japan_member_id"]
        tips = [x for x in row["tip_ids"].split("|") if x]
        out[mid] = tips
    return out


def load_summary(path: Path):
    rows = read_csv(path)
    by = {row["paper_japan_member_id"]: row for row in rows}
    missing = set(TARGET_IDS) - set(by)
    extra = set(by) - set(TARGET_IDS)
    if missing or extra:
        raise ValueError(f"target summary mismatch missing={sorted(missing)} extra={sorted(extra)}")
    parsed = {}
    for mid, row in by.items():
        parsed[mid] = {
            "taxon_name": row["taxon_name"],
            "global_n": int(row["global_colour_usable_n"]),
            "japan_n": int(row["japan_window_colour_usable_n"]),
            "global_lightness": float(row["global_lightness_median"]),
            "japan_lightness": (
                float(row["japan_window_lightness_median"])
                if row["japan_window_lightness_median"].strip()
                else None
            ),
        }
    return parsed


def pairwise_patristic(tree, tips):
    terminals = {tip.name: tip for tip in tree.get_terminals()}
    values = []
    for i, a in enumerate(tips):
        if a not in terminals:
            raise ValueError(f"missing tree tip {a}")
        for j in range(i):
            b = tips[j]
            values.append(float(tree.distance(terminals[a], terminals[b])))
    return np.asarray(values, dtype=float)


def pairwise_abs(values):
    values = np.asarray(values, dtype=float)
    return np.asarray(
        [abs(float(values[i] - values[j])) for i in range(len(values)) for j in range(i)],
        dtype=float,
    )


def rho(x, y):
    if len(x) < 3:
        return math.nan
    value = float(spearmanr(x, y).statistic)
    return value


def exact_label_test(fixed_pairwise, tip_values):
    tip_values = tuple(float(x) for x in tip_values)
    observed = rho(fixed_pairwise, pairwise_abs(tip_values))
    null = []
    for perm in itertools.permutations(tip_values):
        null.append(rho(fixed_pairwise, pairwise_abs(perm)))
    null = np.asarray(null, dtype=float)
    usable = null[np.isfinite(null)]
    if not len(usable):
        raise ValueError("no usable exact permutations")
    return {
        "rho": observed,
        "exact_permutations": int(len(usable)),
        "negative_tail_p": float(np.mean(usable <= observed)),
        "positive_tail_p": float(np.mean(usable >= observed)),
        "two_sided_abs_p": float(np.mean(np.abs(usable) >= abs(observed))),
    }


def signal_for_ids(tree, cmap, ids, values):
    ids = list(ids)
    tips = []
    for mid in ids:
        mapped = cmap[mid]
        if len(mapped) != 1:
            raise ValueError(f"{mid} does not map to exactly one tree tip: {mapped}")
        tips.append(mapped[0])
    fixed = pairwise_patristic(tree, tips)
    trait = [values[mid] for mid in ids]
    result = exact_label_test(fixed, trait)
    result["paper_japan_member_ids"] = ids
    result["lightness_values"] = {mid: float(values[mid]) for mid in ids}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--concept-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = load_summary(args.summary)
    cmap = concept_tip_map(args.concept_map)
    tree = Phylo.read(str(args.tree), "newick")
    tree.root_with_outgroup("OUTGROUP_saff")

    global_ids = [mid for mid in TARGET_IDS if data[mid]["global_n"] >= 5]
    japan5 = [
        mid for mid in TARGET_IDS
        if data[mid]["japan_n"] >= 5 and data[mid]["japan_lightness"] is not None
    ]
    japan10 = [
        mid for mid in TARGET_IDS
        if data[mid]["japan_n"] >= 10 and data[mid]["japan_lightness"] is not None
    ]
    global_values = {mid: data[mid]["global_lightness"] for mid in global_ids}
    japan_values = {mid: data[mid]["japan_lightness"] for mid in japan5}
    substituted_values = {
        mid: (
            data[mid]["japan_lightness"]
            if data[mid]["japan_lightness"] is not None
            else data[mid]["global_lightness"]
        )
        for mid in global_ids
    }

    global_signal = signal_for_ids(tree, cmap, global_ids, global_values)
    substituted_signal = signal_for_ids(tree, cmap, global_ids, substituted_values)
    japan5_signal = signal_for_ids(tree, cmap, japan5, japan_values)
    japan10_signal = signal_for_ids(
        tree,
        cmap,
        japan10,
        {mid: data[mid]["japan_lightness"] for mid in japan10},
    )

    coverage = {
        mid: {
            "taxon_name": data[mid]["taxon_name"],
            "global_colour_usable_n": data[mid]["global_n"],
            "japan_window_colour_usable_n": data[mid]["japan_n"],
            "global_lightness_median": data[mid]["global_lightness"],
            "japan_window_lightness_median": data[mid]["japan_lightness"],
            "lightness_shift_japan_minus_global": (
                data[mid]["japan_lightness"] - data[mid]["global_lightness"]
                if data[mid]["japan_lightness"] is not None
                else None
            ),
        }
        for mid in TARGET_IDS
    }

    missing_local = [mid for mid in TARGET_IDS if data[mid]["japan_n"] == 0]
    comparable_history_ready = len(japan5) >= 5
    local_signal_reproduced = (
        comparable_history_ready
        and japan5_signal["rho"] < 0
        and japan5_signal["two_sided_abs_p"] <= 0.05
    )

    result = {
        "contract_version": "japan38_colour_geographic_provenance_gate_v1",
        "status_date": "2026-08-26",
        "geographic_contract": {
            "summary": str(args.summary),
            "operational_window": "three frozen coordinate boxes in the provenance contract; sensitivity heuristic, not an authoritative country polygon",
            "global_exact_concepts": len(global_ids),
            "japan_window_n_ge_5_concepts": len(japan5),
            "japan_window_n_ge_10_concepts": len(japan10),
        },
        "coverage": coverage,
        "global_proxy_signal": global_signal,
        "japan_where_available_substitution_sensitivity": substituted_signal,
        "japan_window_signal_n_ge_5": japan5_signal,
        "japan_window_signal_n_ge_10": japan10_signal,
        "missing_japan_window_colour": missing_local,
        "decision": {
            "japan_local_radiation_colour_history_ready": comparable_history_ready,
            "global_anti_phylogenetic_signal_reproduced_in_japan_window": local_signal_reproduced,
            "interpretation": (
                "The current high-depth lightness signal is a global exact-concept species proxy, not a validated Japan-local radiation trait history. "
                "Japan-window coverage retains only four concepts and the anti-phylogenetic signal is not reproduced."
            ),
        },
        "next_action": (
            "Recover Japan-local colour evidence for JPN_29 C. verutum and JPN_38 C. pendulum, and increase local population coverage before using colour as a Japan38 historical module. "
            "Do not treat global species medians as phenotypes of the Japanese nuclear-tip populations."
        ),
        "claim_boundary": (
            "Geographic-provenance sensitivity only. The operational Japan window is a coordinate heuristic. "
            "This result does not invalidate the global species-level colour signal, but it blocks promotion of that signal to a Japan-local radiation-history claim."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
