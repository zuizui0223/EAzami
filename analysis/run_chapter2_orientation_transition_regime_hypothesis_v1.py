#!/usr/bin/env python3
"""Specific Chapter 2 transition-regime hypothesis test.

Tests one predeclared composite direction only:
    U->D orientation change aligns with higher BIO15 and lower BIO1.

The discrete layer is a symmetric two-state CTMC with exact edge joint
posteriors. The continuous layer is Brownian squared-change reconstruction.
For n>=5 and n>=3 panels every count-preserving tip-state map is enumerated.
No new climate variable is screened.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.optimize import minimize_scalar

AX15 = "chelsa_bio15"
AX1 = "chelsa_bio01"
EPS = 1e-12


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--coverage-audit", type=Path, required=True)
    p.add_argument("--legacy", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_tip(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", x.replace(" ", "_").replace(".", ""))


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sd = float(x.std(ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("cannot z-score zero/nonfinite variance")
    return (x - float(x.mean())) / sd


def read_trees(path: Path, n: int = 6):
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(lines) < n:
        raise ValueError(f"need {n} trees, found {len(lines)}")
    out = []
    for line in lines[:n]:
        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()
        tree = Phylo.read(StringIO(line), "newick")
        tree.root_with_outgroup({"name": "OUTGROUP_saff"})
        out.append(tree)
    return out


def prune_to_panel(tree, taxa: list[str]):
    """Return rooted panel tree while retaining substitution path lengths."""
    tr = copy.deepcopy(tree)
    keep = {normalize_tip(t) for t in taxa}
    for tip in list(tr.get_terminals()):
        if tip.name not in keep:
            tr.prune(tip)
    got = {x.name for x in tr.get_terminals()}
    if got != keep:
        raise AssertionError(("panel tips missing after prune", sorted(keep - got), sorted(got - keep)))

    # Biopython prune usually collapses bifurcating unary parents. Remove any
    # residual unary root while preserving the path length below it.
    while len(tr.root.clades) == 1 and not tr.root.is_terminal():
        child = tr.root.clades[0]
        child.branch_length = None
        tr.root = child
    return tr


def tree_structure(tree):
    nodes = list(tree.find_clades(order="preorder"))
    idx = {id(n): i for i, n in enumerate(nodes)}
    children: dict[int, list[tuple[int, float]]] = {i: [] for i in range(len(nodes))}
    parent: dict[int, tuple[int, float]] = {}
    for p in nodes:
        pi = idx[id(p)]
        for c in p.clades:
            ci = idx[id(c)]
            t = float(c.branch_length or 0.0)
            if t <= 0:
                t = 1e-10
            children[pi].append((ci, t))
            parent[ci] = (pi, t)
    root = idx[id(tree.root)]
    tips = {n.name: idx[id(n)] for n in tree.get_terminals()}
    postorder = [idx[id(n)] for n in tree.find_clades(order="postorder")]
    preorder = [idx[id(n)] for n in tree.find_clades(order="preorder")]
    return nodes, children, parent, root, tips, postorder, preorder


def brownian_internal_values(tree, tip_values: dict[str, float]):
    nodes, children, parent, root, tips, postorder, preorder = tree_structure(tree)
    n = len(nodes)
    L = np.zeros((n, n), dtype=float)
    for ci, (pi, t) in parent.items():
        w = 1.0 / max(t, 1e-10)
        L[pi, pi] += w
        L[ci, ci] += w
        L[pi, ci] -= w
        L[ci, pi] -= w
    fixed_idx = []
    fixed_vals = []
    for name, ti in tips.items():
        if name not in tip_values:
            raise AssertionError(("missing tip environmental value", name))
        fixed_idx.append(ti)
        fixed_vals.append(float(tip_values[name]))
    fixed_idx = np.array(fixed_idx, dtype=int)
    fixed_vals = np.array(fixed_vals, dtype=float)
    unknown_idx = np.array([i for i in range(n) if i not in set(fixed_idx)], dtype=int)
    x = np.zeros(n, dtype=float)
    x[fixed_idx] = fixed_vals
    if len(unknown_idx):
        Luu = L[np.ix_(unknown_idx, unknown_idx)]
        Luf = L[np.ix_(unknown_idx, fixed_idx)]
        x[unknown_idx] = np.linalg.solve(Luu, -Luf @ fixed_vals)
    edge_delta = {ci: float(x[ci] - x[pi]) for ci, (pi, _) in parent.items()}
    return x, edge_delta


def transition_matrix(q: float, t: float) -> np.ndarray:
    e = math.exp(-2.0 * q * t)
    same = 0.5 * (1.0 + e)
    diff = 0.5 * (1.0 - e)
    return np.array([[same, diff], [diff, same]], dtype=float)


def ctmc_likelihood_and_edge_joint(tree, tip_states: dict[str, int], q: float, need_joint: bool = True):
    nodes, children, parent, root, tips, postorder, preorder = tree_structure(tree)
    n = len(nodes)
    like = np.ones((n, 2), dtype=float)
    for name, ti in tips.items():
        s = int(tip_states[name])
        like[ti, :] = 0.0
        like[ti, s] = 1.0
    for ni in postorder:
        if not children[ni]:
            continue
        v = np.ones(2, dtype=float)
        for ci, t in children[ni]:
            P = transition_matrix(q, t)
            v *= P @ like[ci]
        like[ni] = v
    root_prior = np.array([0.5, 0.5], dtype=float)
    Z = float(root_prior @ like[root])
    if not np.isfinite(Z) or Z <= 0:
        return 0.0, None
    if not need_joint:
        return Z, None

    outside = np.zeros((n, 2), dtype=float)
    outside[root] = root_prior
    edge_joint = {}
    for pi in preorder:
        if not children[pi]:
            continue
        child_msgs = {}
        for ci, t in children[pi]:
            child_msgs[ci] = transition_matrix(q, t) @ like[ci]
        for ci, t in children[pi]:
            base = outside[pi].copy()
            for sj, _ in children[pi]:
                if sj != ci:
                    base *= child_msgs[sj]
            P = transition_matrix(q, t)
            outside[ci] = base @ P
            J = (base[:, None] * P) * like[ci][None, :] / Z
            edge_joint[ci] = J
    return Z, edge_joint


def fit_symmetric_q(tree, tip_states: dict[str, int]) -> float:
    def objective(logq: float) -> float:
        q = math.exp(logq)
        Z, _ = ctmc_likelihood_and_edge_joint(tree, tip_states, q, need_joint=False)
        return -math.log(max(Z, 1e-300))

    # Wide log-rate bounds accommodate small substitution branch lengths.
    opt = minimize_scalar(objective, bounds=(-10.0, 14.0), method="bounded", options={"xatol": 1e-8})
    if not opt.success:
        raise RuntimeError(f"CTMC rate optimization failed: {opt.message}")
    return float(math.exp(opt.x))


def branchwise_stats(tree, tip_states: dict[str, int], edge_d15: dict[int, float], edge_d1: dict[int, float]):
    q = fit_symmetric_q(tree, tip_states)
    Z, joint = ctmc_likelihood_and_edge_joint(tree, tip_states, q, need_joint=True)
    if joint is None:
        raise RuntimeError("missing edge joint posterior")
    numerator15 = 0.0
    numerator1 = 0.0
    change_total = 0.0
    for ci, J in joint.items():
        signed = float(J[0, 1] - J[1, 0])  # U->D minus D->U
        change = float(J[0, 1] + J[1, 0])
        numerator15 += signed * edge_d15[ci]
        numerator1 += signed * edge_d1[ci]
        change_total += change
    if change_total <= EPS:
        raise RuntimeError("zero expected transition mass")
    s15 = numerator15 / change_total
    s1 = numerator1 / change_total
    composite = (s15 - s1) / math.sqrt(2.0)
    return {
        "q": q,
        "likelihood": Z,
        "expected_changes": change_total,
        "bio15": s15,
        "bio1": s1,
        "composite": composite,
    }


def build_panel_environment(occ: pd.DataFrame, taxa: list[str]):
    counts = occ.groupby("scientific_name_query").size()
    env = occ.groupby("scientific_name_query")[[AX15, AX1]].mean().loc[taxa].copy()
    env["z15"] = zscore(env[AX15].to_numpy(float))
    env["z1"] = zscore(env[AX1].to_numpy(float))
    return counts, env


def panel_state_map(crosswalk: pd.DataFrame, taxa: list[str]):
    state_by_taxon = dict(zip(crosswalk["accepted_taxon"], crosswalk["analysis_state"]))
    out = {}
    for t in taxa:
        s = state_by_taxon.get(t)
        if s not in {"U", "D"}:
            raise AssertionError(("unresolved panel state", t, s))
        out[normalize_tip(t)] = 0 if s == "U" else 1
    return out


def prepare_topology_assets(raw_trees, taxa: list[str], env: pd.DataFrame):
    assets = []
    tip15 = {normalize_tip(t): float(env.loc[t, "z15"]) for t in taxa}
    tip1 = {normalize_tip(t): float(env.loc[t, "z1"]) for t in taxa}
    for raw in raw_trees:
        tr = prune_to_panel(raw, taxa)
        _, d15 = brownian_internal_values(tr, tip15)
        _, d1 = brownian_internal_values(tr, tip1)
        assets.append((tr, d15, d1))
    return assets


def observed_topology_stats(assets, states):
    return [branchwise_stats(tr, states, d15, d1) for tr, d15, d1 in assets]


def method_check(contract: dict, legacy: dict, stats: list[dict]):
    tol = float(contract["method_validation"]["legacy_numeric_tolerance"])
    targets = contract["method_validation"]["legacy_target_ranges"]
    for axis, key, sign in ((AX15, "bio15", +1), (AX1, "bio1", -1)):
        lo, hi = map(float, targets[axis])
        values = [float(x[key]) for x in stats]
        if not all(np.sign(v) == sign for v in values):
            raise AssertionError(("legacy direction reproduction failed", axis, values))
        for v in values:
            distance = 0.0 if lo <= v <= hi else min(abs(v - lo), abs(v - hi))
            if distance > tol:
                raise AssertionError(("legacy branchwise numeric reproduction failed", axis, v, [lo, hi], tol))
    return {
        "status": "pass",
        "new_bio15_range": [float(min(x["bio15"] for x in stats)), float(max(x["bio15"] for x in stats))],
        "legacy_bio15_range": targets[AX15],
        "new_bio1_range": [float(min(x["bio1"] for x in stats)), float(max(x["bio1"] for x in stats))],
        "legacy_bio1_range": targets[AX1],
        "expected_changes_range": [float(min(x["expected_changes"] for x in stats)), float(max(x["expected_changes"] for x in stats))],
    }


def exact_panel_test(panel_name: str, taxa: list[str], observed_states: dict[str, int], assets, expected_maps: int):
    norm_taxa = [normalize_tip(t) for t in taxa]
    d_count = sum(observed_states[t] for t in norm_taxa)
    combos = list(itertools.combinations(range(len(norm_taxa)), d_count))
    if len(combos) != expected_maps:
        raise AssertionError(("map-count drift", panel_name, len(combos), expected_maps))

    observed_stats = observed_topology_stats(assets, observed_states)
    observed = {
        "topology_composite": [float(x["composite"]) for x in observed_stats],
        "topology_bio15": [float(x["bio15"]) for x in observed_stats],
        "topology_bio1": [float(x["bio1"]) for x in observed_stats],
        "topology_expected_changes": [float(x["expected_changes"]) for x in observed_stats],
        "composite_median": float(np.median([x["composite"] for x in observed_stats])),
        "bio15_median": float(np.median([x["bio15"] for x in observed_stats])),
        "bio1_median": float(np.median([x["bio1"] for x in observed_stats])),
    }

    rows = []
    for combo in combos:
        dset = set(combo)
        states = {t: (1 if i in dset else 0) for i, t in enumerate(norm_taxa)}
        topo = observed_topology_stats(assets, states)
        comp = float(np.median([x["composite"] for x in topo]))
        s15 = float(np.median([x["bio15"] for x in topo]))
        s1 = float(np.median([x["bio1"] for x in topo]))
        assignment = "".join("D" if i in dset else "U" for i in range(len(norm_taxa)))
        rows.append({
            "panel": panel_name,
            "assignment_id": assignment,
            "observed": bool(all(states[t] == observed_states[t] for t in norm_taxa)),
            "composite_median": comp,
            "bio15_median": s15,
            "bio1_median": s1,
            "bio1_expected_direction_median": -s1,
        })
    df = pd.DataFrame(rows)
    if int(df["observed"].sum()) != 1:
        raise AssertionError(("observed assignment not unique", panel_name, int(df["observed"].sum())))

    def rank(col: str, value: float):
        count = int((df[col].astype(float) >= value - 1e-12).sum())
        return {"count_at_least_observed": count, "n_maps": int(len(df)), "exact_fraction": float(count / len(df))}

    result = {
        "n_taxa": len(taxa),
        "n_U": len(taxa) - d_count,
        "n_D": d_count,
        "taxa_order": taxa,
        "observed": observed,
        "exact_primary_rank": rank("composite_median", observed["composite_median"]),
        "secondary_axis_ranks": {
            "bio15": rank("bio15_median", observed["bio15_median"]),
            "bio1_lower_expected": rank("bio1_expected_direction_median", -observed["bio1_median"]),
        },
    }
    return result, df


def main() -> int:
    args = parse_args()
    contract = read_json(args.contract)
    coverage = read_json(args.coverage_audit)
    legacy = read_json(args.legacy)
    if contract["version"] != "chapter2_orientation_transition_regime_hypothesis_contract_v1":
        raise AssertionError("contract version drift")
    if coverage["version"] != "chapter2_orientation_occurrence_coverage_audit_result_v1":
        raise AssertionError("coverage source version drift")
    if legacy["contract_version"] != "fdt4_branchwise_niche_transition_concordance_v1":
        raise AssertionError("legacy source version drift")

    crosswalk = pd.read_csv(args.orientation)
    jp = pd.read_csv(args.japan_occurrences)
    tw = pd.read_csv(args.taiwan_occurrences)
    occ = pd.concat([jp, tw], ignore_index=True)
    raw_trees = read_trees(args.au_trees, 6)

    threshold_taxa = {str(k): list(v["taxa"]) for k, v in coverage["threshold_summaries"].items()}

    # Method reproduction on frozen n>=10 panel.
    taxa10 = threshold_taxa["10"]
    exp10 = contract["panels"]["n10_method_check"]
    if (len(taxa10), sum(crosswalk.set_index("accepted_taxon").loc[taxa10, "analysis_state"] == "U"), sum(crosswalk.set_index("accepted_taxon").loc[taxa10, "analysis_state"] == "D")) != (exp10["expected_n"], exp10["expected_U"], exp10["expected_D"]):
        raise AssertionError("n10 panel drift")
    _, env10 = build_panel_environment(occ, taxa10)
    states10 = panel_state_map(crosswalk, taxa10)
    assets10 = prepare_topology_assets(raw_trees, taxa10, env10)
    stats10 = observed_topology_stats(assets10, states10)
    reproduction = method_check(contract, legacy, stats10)

    all_frames = []
    panel_results = {}
    for key, threshold_key in (("n5_primary", "5"), ("n3_sensitivity", "3")):
        spec = contract["panels"][key]
        taxa = threshold_taxa[threshold_key]
        state_series = crosswalk.set_index("accepted_taxon").loc[taxa, "analysis_state"]
        if (len(taxa), int((state_series == "U").sum()), int((state_series == "D").sum())) != (spec["expected_n"], spec["expected_U"], spec["expected_D"]):
            raise AssertionError(("panel drift", key))
        counts, env = build_panel_environment(occ, taxa)
        if any(int(counts.get(t, 0)) < int(spec["threshold"]) for t in taxa):
            raise AssertionError(("occurrence threshold drift", key))
        states = panel_state_map(crosswalk, taxa)
        assets = prepare_topology_assets(raw_trees, taxa, env)
        result, frame = exact_panel_test(key, taxa, states, assets, int(spec["exact_state_maps"]))
        panel_results[key] = result
        all_frames.append(frame)

    n5 = panel_results["n5_primary"]
    comp_top = n5["observed"]["topology_composite"]
    p = n5["exact_primary_rank"]["exact_fraction"]
    if all(x > 0 for x in comp_top) and p <= 0.05:
        classification = "repeated_u_to_d_transition_regime_concordance_supported"
    elif all(x > 0 for x in comp_top):
        classification = "u_to_d_transition_regime_directional_but_not_exceptional"
    else:
        classification = "u_to_d_transition_regime_direction_not_repeated"

    out = {
        "version": "chapter2_orientation_transition_regime_hypothesis_result_v1",
        "analysis_role": contract["analysis_role"],
        "hypothesis": contract["hypothesis"],
        "classification": classification,
        "method_reproduction_n10": reproduction,
        "panels": panel_results,
        "claim_ceiling": contract["claim_ceiling"],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    pd.concat(all_frames, ignore_index=True).to_csv(args.out_csv, index=False)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
