#!/usr/bin/env python3
"""Fit two-state Mk U/D histories on three REAL 45-tip nuclear trees (no invented traits).

Data: 39 original Japan38 + 5 exact Moreyra BioSamples; the source outgroup
(Carthamus) is used to root each empirical molecular phylogeny but is NOT
given a Cirsium head state. Undescribed/ambiguous tips have likelihood [1,1],
NOT an imputed U state. Uniform ingroup root prior is fixed for both ER and ARD.

Full rigor boundaries:
* edge P(parent=U, child=D | tip states, fitted model) is NOT the probability
  of one historical state-change event occurring along that branch.
* no palaeoclimate, contemporaneous niche or selection effect is estimated.
* reference-projected 176-locus 45-tip pilot is NOT the complete 294-tip global
  Moreyra species tree, and three ML models are topology sensitivities, not
  independent biological replicates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Bio import Phylo
from scipy.optimize import minimize, minimize_scalar

OUTGROUP = "OUTGROUP_saff"
PINNED = {
    "ModelFinder_TIM3_F_R3": "191e6a502e23685d95e767580d41a9e1eca82db0495c93d58d34bcc3abedf8f6",
    "Fixed_GTR_F_G4": "b37f50b1422b016263a78c412c88a600d338bbd399a8255c1fc89b399cdd9a00",
    "FastTree_GTR_gamma": "c1bd01900fff5c23825642a41ba0c2a24080ca5537422fcb241477a88ea6b9e2",
}
EU_D = "GLB_SRR30887186_Cirsium_erisithales"
NA_D = "GLB_SRR30887231_Cirsium_vinaceum"
REGION_NODES = {
    "NA_three_taxa": [
        "GLB_SRR30887153_Cirsium_ownbeyi",
        "GLB_SRR30887180_Cirsium_flodmanii", NA_D,
    ],
    "EU_two_taxa": [
        "GLB_SRR30887156_Cirsium_oleraceum", EU_D,
    ],
}
STATES = {"U": 0, "D": 1}
COLORS = {"Japan38_2025_moreyra": "#537DA3", "North_America": "#C88147", "West_Palearctic": "#689479"}
EPS = 1e-14


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h))
    if len(rows) != 45 or len({r["tip_id"] for r in rows}) != 45:
        raise ValueError("45 original nuclear tips (including source outgroup) required")
    by_tip = {r["tip_id"]: r for r in rows}
    if OUTGROUP not in by_tip or by_tip[OUTGROUP]["head_orientation"] not in {"?", ""}:
        raise ValueError("original outgroup cannot be assigned a Cirsium head state")
    by_tip.pop(OUTGROUP)
    counts = Counter(r["head_orientation"] for r in by_tip.values())
    if counts != Counter({"U": 17, "D": 7, "?": 20}):
        raise ValueError("source botanical U/D/missing state registry drift: " + repr(counts))
    if by_tip[NA_D]["head_orientation"] != "D" or by_tip[EU_D]["head_orientation"] != "D":
        raise ValueError("two independent non-Japanese D candidate traits changed")
    for r in by_tip.values():
        if r["head_orientation"] not in {"U", "D", "?"}:
            raise ValueError("unapproved source morphology class")
        if r["head_orientation"] != "?" and not r["head_source_url"]:
            raise ValueError("resolved head lacks explicit botanical source URL")
    return by_tip


def load_tree(path: Path, expected_hash: str, names: set[str]):
    if sha(path) != expected_hash:
        raise ValueError("published real nuclear topology SHA256 mismatch: " + str(path))
    tree = Phylo.read(path, "newick")
    observed = [x.name for x in tree.get_terminals()]
    if len(observed) != 45 or len(set(observed)) != 45 or set(observed) != names | {OUTGROUP}:
        raise ValueError("real molecular tree tips and frozen S1 registry do not join")
    tree.root_with_outgroup({"name": OUTGROUP})
    tree.prune(OUTGROUP)
    if len(tree.root.clades) == 1:
        tree.root = tree.root.clades[0]
        tree.root.branch_length = None
    if {x.name for x in tree.get_terminals()} != names or len(names) != 44:
        raise ValueError("ingroup tree source tip loss")
    for n in tree.find_clades():
        if n is not tree.root and (n.branch_length is None or
                                   not math.isfinite(float(n.branch_length)) or
                                   float(n.branch_length) < 0):
            raise ValueError("missing or negative empirical molecular branch length")
    return tree


def build_layout(tree):
    nodes = list(tree.find_clades(order="preorder"))
    by_id = {id(node): i for i, node in enumerate(nodes)}
    children = [[] for _ in nodes]
    parents = {}
    tip_id = {}
    for node in nodes:
        i = by_id[id(node)]
        if node.is_terminal():
            tip_id[node.name] = i
        else:
            for child in node.clades:
                j = by_id[id(child)]
                length = max(1e-10, float(child.branch_length or 0))
                children[i].append((j, length))
                parents[j] = i
    order_post = [by_id[id(n)] for n in tree.find_clades(order="postorder")]
    return nodes, children, parents, tip_id, order_post


def transmat(q_ud: float, q_du: float, length: float):
    if q_ud <= 0 or q_du <= 0:
        raise ValueError("finite positive Mk transition rates required")
    total = q_ud + q_du
    # expm1 for low expected changes on short internal branches.
    change = -math.expm1(-total * length)
    return np.array([
        [1.0 - q_ud / total * change, q_ud / total * change],
        [q_du / total * change, 1.0 - q_du / total * change]
    ], dtype=float)


def mk(tree, panel, q_ud: float, q_du: float, posterior=False):
    nodes, children, parent, tip_id, post = build_layout(tree)
    emissions = np.ones((len(nodes), 2), dtype=float)
    for taxon, idx in tip_id.items():
        st = panel[taxon]["head_orientation"]
        if st in STATES:
            emissions[idx] = (1., 0.) if st == "U" else (0., 1.)
    inside = emissions.copy()
    child_msgs = {}
    matrices = {}
    for idx in post:
        for ci, length in children[idx]:
            p = transmat(q_ud, q_du, length)
            matrices[(idx, ci)] = p
            v = p @ inside[ci]
            child_msgs[(idx, ci)] = v
            inside[idx] *= v
    prior = np.array([.5, .5], dtype=float)
    likelihood = float(prior @ inside[0])
    if likelihood <= 0 or not math.isfinite(likelihood):
        return float("-inf"), None
    log_likelihood = math.log(likelihood)
    if not posterior:
        return log_likelihood, None
    outside = np.zeros((len(nodes), 2), dtype=float)
    outside[0] = prior
    edge_joint = {}
    for idx in range(len(nodes)):
        for ci, _ in children[idx]:
            base = outside[idx].copy()
            for sibling, _ in children[idx]:
                if sibling != ci:
                    base *= child_msgs[(idx, sibling)]
            J = base[:, None] * matrices[(idx, ci)] * inside[ci][None, :] / likelihood
            if abs(float(J.sum()) - 1.) > 5e-6:
                raise AssertionError("posterior propagation normalization failure")
            edge_joint[ci] = J
            outside[ci] = base @ matrices[(idx, ci)]
    node_posterior = outside * inside / likelihood
    if max(abs(row.sum()-1) for row in node_posterior) > 5e-6:
        raise AssertionError("node posterior normalization failure")
    return log_likelihood, {
        "nodes": nodes, "edge_joint": edge_joint,
        "node_posterior": node_posterior,
        "tip_indices": tip_id,
    }


def fit_one(tree, panel, model: str):
    if model not in {"ER", "ARD"}:
        raise ValueError("unsupported Mk model")
    # Per-substitution rates: use broad bounds to allow very short real
    # Compositae1061 branches without constraining the fit a priori.
    low, high = -12., 17.
    objective = lambda z: -mk(
        tree, panel,
        math.exp(float(z[0])),
        math.exp(float(z[0] if model == "ER" else z[1])),
        posterior=False,
    )[0]
    if model == "ER":
        opt = minimize_scalar(lambda z: objective([z]), method="bounded",
                              bounds=(low, high), options={"xatol": 1e-8})
        if not opt.success:
            raise RuntimeError("ER Mk optimization did not converge")
        best = (float(opt.fun), [float(opt.x)])
    else:
        # Multiple starts protect the asymmetric low-state-count likelihood
        # from local optima and boundary degeneracy.
        starts = [
            [math.log(20.), math.log(20.)],
            [math.log(200.), math.log(200.)],
            [math.log(1000.), math.log(100.)],
            [math.log(100.), math.log(1000.)],
            [math.log(10000.), math.log(100.)],
        ]
        fits = [minimize(objective, x0, method="L-BFGS-B",
                         bounds=[(low, high)] * 2,
                         options={"maxiter": 350, "ftol": 1e-12})
                for x0 in starts]
        solutions = [f for f in fits if math.isfinite(float(f.fun))]
        if not solutions:
            raise RuntimeError("ARD Mk finite MLE not found")
        best_f = min(solutions, key=lambda f: f.fun)
        best = (float(best_f.fun), list(best_f.x))
    log_lik = -best[0]
    q_ud = math.exp(best[1][0])
    q_du = math.exp(best[1][0 if model == "ER" else 1])
    log_lik_check, post = mk(tree, panel, q_ud, q_du, posterior=True)
    if abs(log_lik - log_lik_check) > 1e-6:
        raise ValueError("fitted model posterior inconsistent with likelihood")
    return {"model": model, "n_params": 1 if model == "ER" else 2,
            "log_likelihood": log_lik,
            "q_UD_per_substitution": q_ud, "q_DU_per_substitution": q_du,
            "near_parameter_bounds": (any(abs(v - low) < .01 or abs(v - high) < .01
                                         for v in best[1])),
            "post": post}


def fitch_minimum(tree, panel):
    def recurse(node):
        if node.is_terminal():
            s = panel[node.name]["head_orientation"]
            return ({s} if s in {"U", "D"} else {"U", "D"}), 0
        children = [recurse(c) for c in node.clades]
        group, cost = set(children[0][0]), children[0][1]
        for st, steps in children[1:]:
            cost += steps
            shared = group & st
            if shared:
                group = shared
            else:
                group |= st
                cost += 1
        return group, cost
    return recurse(tree.root)[1]


def extract(tree, fitted, tree_name, panel_name, panel):
    result = []
    diag = fitted["post"]
    nodes = diag["nodes"]
    idx = {id(node): i for i, node in enumerate(nodes)}
    for label, tips in REGION_NODES.items():
        ancestor = tree.common_ancestor(tips)
        i = idx[id(ancestor)]
        descendants = [x.name for x in ancestor.get_terminals()]
        if not set(tips) <= set(descendants):
            raise ValueError("external continental MRCA names lost")
        row = diag["node_posterior"][i]
        result.append({
            "tree_model": tree_name, "trait_panel": panel_name,
            "Mk_model": fitted["model"], "target": label,
            "target_type": "regional_MRCA_node",
            "n_descendants": len(descendants),
            "P_node_U": float(row[0]),
            "P_node_D": float(row[1]),
            "P_parent_U_child_D": "",
            "P_parent_D_child_U": "",
            "scientific_boundary": "posterior on MRCA state; not actual transition count",
        })
    for taxon, species_label in [(NA_D, "Cirsium vinaceum D"), (EU_D, "Cirsium erisithales D")]:
        tip_index = diag["tip_indices"][taxon]
        joint = diag["edge_joint"][tip_index]
        result.append({
            "tree_model": tree_name, "trait_panel": panel_name,
            "Mk_model": fitted["model"], "target": species_label,
            "target_type": "observed_D_terminal_edge",
            "n_descendants": 1,
            "P_node_U": float(diag["node_posterior"][tip_index][0]),
            "P_node_D": float(diag["node_posterior"][tip_index][1]),
            "P_parent_U_child_D": float(joint[0, 1]),
            "P_parent_D_child_U": float(joint[1, 0]),
            "scientific_boundary": "conditional edge endpoint joint; not posterior on a dated unique evolutionary event",
        })
    return result


def run(trees: dict[str, Path], trait_csv: Path, output_dir: Path):
    base = load_rows(trait_csv)
    names = set(base)
    all_stats, all_edges = [], []
    samples = {
        "all_source_states": base,
        "omit_West_Palearctic_cultivated_D": {
            tip: ({**r, "head_orientation": "?"} if tip == EU_D else dict(r))
            for tip, r in base.items()
        },
        "omit_North_American_D": {
            tip: ({**r, "head_orientation": "?"} if tip == NA_D else dict(r))
            for tip, r in base.items()
        },
    }
    for tree_name, file in trees.items():
        tree = load_tree(file, PINNED[tree_name], names)
        for panel_name, states in samples.items():
            n = Counter(r["head_orientation"] for r in states.values())
            if n["D"] < 2 or n["U"] < 2:
                raise ValueError("one-state panel invalid for Mk")
            results = [fit_one(tree, states, model) for model in ("ER", "ARD")]
            for result in results:
                k = result["n_params"]
                N = n["U"] + n["D"]
                aic = 2*k - 2*result["log_likelihood"]
                aicc = aic + 2*k*(k+1) / (N-k-1)
                all_stats.append({
                    "molecular_topology": tree_name, "trait_panel": panel_name,
                    "Mk_model": result["model"], "n_resolved_U": n["U"],
                    "n_resolved_D": n["D"], "n_source_missing": n["?"],
                    "n_ingroup_molecular_tips": 44, "Fitch_minimum_steps": fitch_minimum(tree, states),
                    "fitted_log_likelihood": result["log_likelihood"],
                    "AIC": aic, "AICc_n_resolved_taxon_tips_approx": aicc,
                    "q_UD_per_substitution": result["q_UD_per_substitution"],
                    "q_DU_per_substitution": result["q_DU_per_substitution"],
                    "root_P_U": float(result["post"]["node_posterior"][0][0]),
                    "root_P_D": float(result["post"]["node_posterior"][0][1]),
                    "rate_at_optimizer_boundary": result["near_parameter_bounds"],
                    "source_ML_tree_SHA256": PINNED[tree_name],
                })
                all_edges.extend(extract(tree, result, tree_name, panel_name, states))
    for panel_name in samples:
        for tree_name in trees:
            m = {r["Mk_model"]: r for r in all_stats if r["trait_panel"] == panel_name
                 and r["molecular_topology"] == tree_name}
            d = m["ARD"]["AICc_n_resolved_taxon_tips_approx"] - m["ER"]["AICc_n_resolved_taxon_tips_approx"]
            for row in (m["ER"], m["ARD"]):
                row["delta_AICc_ARD_minus_ER"] = d
                row["AICc_favored"] = "ER" if d >= 0 else "ARD"
    primary = [r for r in all_stats if r["trait_panel"]=="all_source_states"]
    primary_er = [r for r in primary if r["Mk_model"]=="ER"]
    primary_ard = [r for r in primary if r["Mk_model"]=="ARD"]
    res = {
        "version": "real_global45_multitopology_ER_ARD_mk_original_S1_botanical_orientation_v1",
        "contributing_source": "2025 Moreyra public 39 Japanese + 5 NA and West Palearctic Moreyra S1 original molecular individuals; botanical U/D independently sourced",
        "molecular_scope": "genuine real 45-tip Compositae1061 source 176-locus projected sensitivity phylograms, 3 alternative molecular ML models",
        "source_trait_table_SHA256": sha(trait_csv),
        "source_trees_SHA256": PINNED,
        "root_prior": {"U": 0.5, "D": 0.5},
        "inference_panel": {
            "n_source_molecular_ingroup": 44,
            "U": 17, "D": 7, "source_unresolved": 20,
            "multiple_missing_trait_states_not_imputed": True,
            "observed_state_is_same_sequenced_voucher": False,
            "regional_resolved_sample_counts": dict(sorted(Counter(
                r["geographic_panel"]+":"+r["head_orientation"] for r in base.values()
                if r["head_orientation"] in {"U","D"}
            ).items())),
        },
        "model_comparison": {
            "rooted_on_real_Carthamus_before_removing_unphenotyped_outgroup": True,
            "ER_loglik_AICc": [r["AICc_n_resolved_taxon_tips_approx"] for r in primary_er],
            "ARD_loglik_AICc": [r["AICc_n_resolved_taxon_tips_approx"] for r in primary_ard],
            "delta_AICc_ARD_minus_ER_by_topology": {
                r["molecular_topology"]: r["delta_AICc_ARD_minus_ER"] for r in primary_er
            },
            "Fitch_minimum_changes_by_topology": {
                r["molecular_topology"]: r["Fitch_minimum_steps"] for r in primary_er
            },
            "root_P_U_ER_range": [min(r["root_P_U"] for r in primary_er), max(r["root_P_U"] for r in primary_er)],
            "root_P_U_ARD_range": [min(r["root_P_U"] for r in primary_ard), max(r["root_P_U"] for r in primary_ard)],
            "ARD_better_by_AICc_in_all_three": all(r["delta_AICc_ARD_minus_ER"] < 0 for r in primary_er),
            "ER_better_by_AICc_in_all_three": all(r["delta_AICc_ARD_minus_ER"] >= 0 for r in primary_er),
        },
        "three_nonindependent_tree_estimators": list(trees),
        "sensitivity_cases": list(samples),
        "not_estimated": [
            "exact number of U->D evolutionary events or their calendar times",
            "actual palaeoclimatic exposures when orientation was gained or lost",
            "U/D fitness payoff and selection", "complete 294-tip Moreyra 350-locus world tree",
            "causal link to rainfall or pollination",
            "an independent replication per observed molecular tip",
        ],
        "interpretation_caveats": [
            "The 39 Japanese molecular samples represent a geographically unbalanced radiation; three source molecular trees share exactly the same alignment and are alternatives, not independent replicates.",
            "Some Moreyra original source plant material was cultivated. Head shape is an independently recorded species concept rather than this sequenced specimen.",
            "AICc uses n=number of taxon-level resolved source states as an approximation; biological nonindependence and model misspecification remain.",
            "Some real molecular terminal branch lengths and 20 unscored traits prevent directional ancestral-state or adaptation claims without additional independent observations.",
            "Equal root-state prior is fixed rather than estimated from Cirsium ancestors.",
            "Cross-region U/D contrasts are sister states; their path may include multiple hidden reversals even when endpoint joint appears high.",
        ]
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir/"fitted_mk_ER_vs_ARD_by_tree_and_source_sensitivity.csv").open("w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(all_stats[0]))
        writer.writeheader()
        writer.writerows(all_stats)
    with (output_dir/"external_MRCA_and_D_tip_Mk_posteriors.csv").open("w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(all_edges[0]))
        writer.writeheader()
        writer.writerows(all_edges)
    (output_dir/"real_world45_Mk_multitopology_result.json").write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    plot(results=all_stats, output_dir=output_dir)
    print(json.dumps({
        "real_molecular_tips":45,
        "trait_U_D_unknown":[17,7,20],
        "Mk_AICc_delta_ARD_minus_ER": res["model_comparison"]["delta_AICc_ARD_minus_ER_by_topology"],
        "Mk_root_ER_range_U":res["model_comparison"]["root_P_U_ER_range"],
        "sensitivity_omits_cultivated_West_D": True,
        "fitch_minimum":res["model_comparison"]["Fitch_minimum_changes_by_topology"],
        "historical_transition_count_identified":False,
    },indent=2))
    return res


def plot(results, output_dir):
    z = [x for x in results if x["trait_panel"] == "all_source_states" and x["Mk_model"] == "ER"]
    fig, (a,b) = plt.subplots(1, 2, figsize=(10.8, 4.2))
    names = [x["molecular_topology"].replace("_", " ") for x in z]
    y = np.arange(len(z))
    a.barh(y, [x["delta_AICc_ARD_minus_ER"] for x in z], color="#667C93", height=.55)
    a.axvline(0,color="#1D2D3A",lw=.9)
    a.set_yticks(y,names);a.invert_yaxis()
    a.set_xlabel("ARD minus ER AICc  (positive = ER favored)")
    a.set_title("Model comparison on same 176-locus DNA")
    b.barh(y,[x["root_P_U"] for x in z],color="#337FA0",height=.55)
    b.set_yticks(y,[""] * len(y))
    b.set_xlim(0,1)
    b.set_xlabel("Posterior P(ancestral ingroup U | ER Mk)")
    b.set_title("Root uncertainty under equal U/D prior")
    fig.suptitle("Crosscontinental Cirsium (39 Japan + 5 external)  |  Mk on real 45-tip nuclear trees",fontsize=10)
    fig.tight_layout()
    fig.savefig(output_dir/"world45_real_nuclear_U_D_Mk_model_and_root_sensitivity.png",dpi=190,bbox_inches="tight")
    plt.close(fig)

    # All leave-one-regional-D-out results must be shown, not only the primary
    # model that appears to favor asymmetric rates on every molecular tree.
    panels = [
        ("all_source_states", "All observed U/D states"),
        ("omit_West_Palearctic_cultivated_D", "West-Palearctic D set unknown"),
        ("omit_North_American_D", "North-American D set unknown"),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    colors = {"ModelFinder_TIM3_F_R3": "#457F9A",
              "Fixed_GTR_F_G4": "#A67349",
              "FastTree_GTR_gamma": "#74927B"}
    offsets = {"ModelFinder_TIM3_F_R3": -.18,
               "Fixed_GTR_F_G4": 0.,
               "FastTree_GTR_gamma": .18}
    for j, (panel, label) in enumerate(panels):
        for source_name in colors:
            item = next(x for x in results if x["trait_panel"] == panel
                        and x["molecular_topology"] == source_name and x["Mk_model"] == "ER")
            value = float(item["delta_AICc_ARD_minus_ER"])
            ax.plot(value, j+offsets[source_name], "o", ms=8,
                    color=colors[source_name],
                    label=source_name.replace("_"," ") if j==0 else None)
    ax.axvline(0,color="#394C59",lw=1.1,linestyle="--")
    ax.set_yticks(range(3),[s[1] for s in panels])
    ax.set_ylim(2.55,-.45)
    ax.set_xlim(-3.6,2.5)
    ax.set_xlabel("ARD AICc minus ER AICc    ← ARD favored    |    ER favored →")
    ax.set_title("Single regional D taxon determines apparent asymmetric Mk preference",
                 loc="left", fontsize=10)
    ax.grid(axis="x",color="#B0B7BF",alpha=.2)
    ax.legend(frameon=False,loc="lower left",fontsize=8)
    for spine in ("top","right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_dir/"world45_real_nuclear_ARD_vs_ER_holdout_falsification.png",
                dpi=200,bbox_inches="tight")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--primary",type=Path,required=True)
    p.add_argument("--fixed",type=Path,required=True)
    p.add_argument("--fasttree",type=Path,required=True)
    p.add_argument("--traits",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    run({
        "ModelFinder_TIM3_F_R3":a.primary,
        "Fixed_GTR_F_G4":a.fixed,
        "FastTree_GTR_gamma":a.fasttree,
    },a.traits,a.outdir)


if __name__=="__main__":
    main()
