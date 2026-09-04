#!/usr/bin/env python3
"""Directional decomposition of the frozen orientation transition-regime H1.

H2 asks whether the same environmental regime is tracked reversibly:
  U->D should align with (+BIO15,-BIO1)
  D->U should align with (-BIO15,+BIO1)

No new environmental variable or taxon is screened.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import run_chapter2_orientation_transition_regime_hypothesis_v1 as base

AX15 = base.AX15
AX1 = base.AX1
EPS = 1e-12


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--robustness-result", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def directional_stats(tree, tip_states, edge_d15, edge_d1):
    q = base.fit_symmetric_q(tree, tip_states)
    Z, joint = base.ctmc_likelihood_and_edge_joint(tree, tip_states, q, need_joint=True)
    if joint is None:
        raise RuntimeError("missing edge joint posterior")

    f_mass = 0.0
    r_mass = 0.0
    f_num = 0.0
    r_num = 0.0
    for ci, J in joint.items():
        p_ud = float(J[0, 1])
        p_du = float(J[1, 0])
        projection = (float(edge_d15[ci]) - float(edge_d1[ci])) / math.sqrt(2.0)
        f_mass += p_ud
        r_mass += p_du
        f_num += p_ud * projection
        r_num += p_du * (-projection)

    if f_mass <= EPS or r_mass <= EPS:
        raise RuntimeError(("insufficient directional transition mass", f_mass, r_mass))
    forward = f_num / f_mass
    reverse = r_num / r_mass
    return {
        "q": float(q),
        "likelihood": float(Z),
        "forward_mass": float(f_mass),
        "reverse_mass": float(r_mass),
        "forward_alignment": float(forward),
        "reverse_alignment": float(reverse),
        "bidirectional_floor": float(min(forward, reverse)),
    }


def topology_directional_stats(assets, states):
    return [directional_stats(tr, states, d15, d1) for tr, d15, d1 in assets]


def median_of(stats, key):
    return float(np.median([float(x[key]) for x in stats]))


def main():
    a = parse_args()
    contract = json.loads(a.contract.read_text())
    robust = json.loads(a.robustness_result.read_text())
    taxa = list(contract["panel"]["taxa"])

    crosswalk = pd.read_csv(a.orientation)
    occ = pd.concat([
        pd.read_csv(a.japan_occurrences),
        pd.read_csv(a.taiwan_occurrences),
    ], ignore_index=True)

    counts, env = base.build_panel_environment(occ, taxa)
    if not all(int(counts.get(t, 0)) >= 10 for t in taxa):
        raise AssertionError("strict n>=10 panel drift")

    raw_trees = base.read_trees(a.au_trees, n=6)
    assets = base.prepare_topology_assets(raw_trees, taxa, env)
    observed_states = base.panel_state_map(crosswalk, taxa)

    # Fail closed: reproduce the already frozen H1 composite before H2.
    h1_stats = base.observed_topology_stats(assets, observed_states)
    h1_median = float(np.median([x["composite"] for x in h1_stats]))
    h1_target = float(robust["strict_n10"]["composite_median"])
    if abs(h1_median - h1_target) > 1e-6:
        raise AssertionError(("H1 reproduction failed", h1_median, h1_target))

    obs_topo = topology_directional_stats(assets, observed_states)
    obs_forward = median_of(obs_topo, "forward_alignment")
    obs_reverse = median_of(obs_topo, "reverse_alignment")
    obs_floor = median_of(obs_topo, "bidirectional_floor")
    forward_all_positive = all(x["forward_alignment"] > 0 for x in obs_topo)
    reverse_all_positive = all(x["reverse_alignment"] > 0 for x in obs_topo)

    norm_taxa = [base.normalize_tip(t) for t in taxa]
    d_count = sum(int(observed_states[t]) for t in norm_taxa)
    combos = list(itertools.combinations(range(len(norm_taxa)), d_count))
    expected = int(contract["panel"]["expected_count_preserving_maps"])
    if len(combos) != expected:
        raise AssertionError(("map count drift", len(combos), expected))

    rows = []
    for combo in combos:
        dset = set(combo)
        states = {t: (1 if i in dset else 0) for i, t in enumerate(norm_taxa)}
        topo = topology_directional_stats(assets, states)
        assignment = "".join("D" if i in dset else "U" for i in range(len(norm_taxa)))
        rows.append({
            "assignment_id": assignment,
            "observed": bool(all(states[t] == observed_states[t] for t in norm_taxa)),
            "forward_alignment_median": median_of(topo, "forward_alignment"),
            "reverse_alignment_median": median_of(topo, "reverse_alignment"),
            "bidirectional_floor_median": median_of(topo, "bidirectional_floor"),
        })
    df = pd.DataFrame(rows)
    if int(df["observed"].sum()) != 1:
        raise AssertionError("observed assignment not unique")

    count_floor = int((df["bidirectional_floor_median"] >= obs_floor - 1e-12).sum())
    exact_fraction = float(count_floor / len(df))

    if forward_all_positive and reverse_all_positive and exact_fraction <= 0.05:
        classification = "bidirectional_reversible_regime_supported"
    elif forward_all_positive and not reverse_all_positive:
        classification = "u_to_d_specific_directional_asymmetry"
    elif forward_all_positive and reverse_all_positive:
        classification = "bidirectional_directional_but_not_exceptional"
    else:
        classification = "directional_tracking_not_resolved"

    result = {
        "version": "chapter2_orientation_transition_directionality_result_v1",
        "analysis_role": contract["analysis_role"],
        "classification": classification,
        "h1_reproduction": {"observed": h1_median, "target": h1_target, "status": "pass"},
        "observed": {
            "forward_alignment_median": obs_forward,
            "reverse_alignment_median": obs_reverse,
            "bidirectional_floor_median": obs_floor,
            "forward_positive_6_of_6": bool(forward_all_positive),
            "reverse_positive_6_of_6": bool(reverse_all_positive),
            "topologies": obs_topo,
        },
        "exact_floor_rank": {
            "count_at_least_observed": count_floor,
            "n_maps": int(len(df)),
            "exact_fraction": exact_fraction,
        },
        "claim_boundary": contract["claim_boundary"],
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2) + "\n")
    df.to_csv(a.out_csv, index=False)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
