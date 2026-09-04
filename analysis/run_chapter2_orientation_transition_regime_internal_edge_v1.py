#!/usr/bin/env python3
"""Test fixed transition-regime H1 using internal branches only."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from run_chapter2_orientation_transition_regime_hypothesis_v1 import (
    read_trees, build_panel_environment, panel_state_map, prepare_topology_assets,
    fit_symmetric_q, ctmc_likelihood_and_edge_joint, tree_structure, normalize_tip,
)

EPS = 1e-12


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--coverage-audit", type=Path, required=True)
    p.add_argument("--orientation", type=Path, required=True)
    p.add_argument("--japan-occurrences", type=Path, required=True)
    p.add_argument("--taiwan-occurrences", type=Path, required=True)
    p.add_argument("--au-trees", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def internal_branchwise_stats(tree, tip_states, edge_d15, edge_d1):
    q = fit_symmetric_q(tree, tip_states)
    Z, joint = ctmc_likelihood_and_edge_joint(tree, tip_states, q, need_joint=True)
    if joint is None:
        raise RuntimeError("missing edge joint posterior")
    _, children, _, _, _, _, _ = tree_structure(tree)
    num15 = 0.0
    num1 = 0.0
    change_total = 0.0
    scored_edges = 0
    for ci, J in joint.items():
        if not children[ci]:
            continue
        signed = float(J[0, 1] - J[1, 0])
        change = float(J[0, 1] + J[1, 0])
        num15 += signed * edge_d15[ci]
        num1 += signed * edge_d1[ci]
        change_total += change
        scored_edges += 1
    if scored_edges == 0 or change_total <= EPS:
        raise RuntimeError("zero internal-edge transition mass")
    s15 = num15 / change_total
    s1 = num1 / change_total
    return {
        "q": float(q),
        "likelihood": float(Z),
        "internal_expected_changes": float(change_total),
        "internal_edges_scored": int(scored_edges),
        "bio15": float(s15),
        "bio1": float(s1),
        "composite": float((s15 - s1) / math.sqrt(2.0)),
    }


def topology_stats(assets, states):
    return [internal_branchwise_stats(tr, states, d15, d1) for tr, d15, d1 in assets]


def exact_test(panel_name, taxa, states_obs, assets, expected_maps):
    norm = [normalize_tip(t) for t in taxa]
    nd = sum(states_obs[t] for t in norm)
    combos = list(itertools.combinations(range(len(norm)), nd))
    if len(combos) != expected_maps:
        raise AssertionError(("map count drift", panel_name, len(combos), expected_maps))
    obs_top = topology_stats(assets, states_obs)
    obs = {
        "topology_composite": [x["composite"] for x in obs_top],
        "topology_bio15": [x["bio15"] for x in obs_top],
        "topology_bio1": [x["bio1"] for x in obs_top],
        "topology_internal_expected_changes": [x["internal_expected_changes"] for x in obs_top],
        "topology_internal_edges_scored": [x["internal_edges_scored"] for x in obs_top],
        "composite_median": float(np.median([x["composite"] for x in obs_top])),
        "bio15_median": float(np.median([x["bio15"] for x in obs_top])),
        "bio1_median": float(np.median([x["bio1"] for x in obs_top])),
    }
    rows=[]
    for combo in combos:
        dset=set(combo)
        states={t:(1 if i in dset else 0) for i,t in enumerate(norm)}
        ts=topology_stats(assets, states)
        comp=float(np.median([x["composite"] for x in ts]))
        b15=float(np.median([x["bio15"] for x in ts]))
        b1=float(np.median([x["bio1"] for x in ts]))
        rows.append({
            "panel":panel_name,
            "assignment_id":"".join("D" if i in dset else "U" for i in range(len(norm))),
            "observed":all(states[t]==states_obs[t] for t in norm),
            "composite_median":comp,
            "bio15_median":b15,
            "bio1_median":b1,
            "bio1_expected_direction_median":-b1,
        })
    df=pd.DataFrame(rows)
    if int(df.observed.sum()) != 1:
        raise AssertionError("observed map not unique")
    def rank(col,val):
        n=int((df[col].astype(float) >= val-1e-12).sum())
        return {"count_at_least_observed":n,"n_maps":len(df),"exact_fraction":float(n/len(df))}
    return {
        "n_taxa":len(taxa),"n_U":len(taxa)-nd,"n_D":nd,"taxa_order":taxa,
        "observed":obs,
        "exact_primary_rank":rank("composite_median",obs["composite_median"]),
        "secondary_axis_ranks":{
            "bio15":rank("bio15_median",obs["bio15_median"]),
            "bio1_lower_expected":rank("bio1_expected_direction_median",-obs["bio1_median"]),
        },
    }, df


def main():
    a=parse_args(); c=load(a.contract); cov=load(a.coverage_audit)
    if c["version"]!="chapter2_orientation_transition_regime_internal_edge_contract_v1":
        raise AssertionError("contract version drift")
    cross=pd.read_csv(a.orientation)
    occ=pd.concat([pd.read_csv(a.japan_occurrences),pd.read_csv(a.taiwan_occurrences)],ignore_index=True)
    trees=read_trees(a.au_trees,6)
    taxa_by={str(k):list(v["taxa"]) for k,v in cov["threshold_summaries"].items()}
    results={}; frames=[]
    for name,key in (("strict_n10_primary","10"),("n5_sensitivity","5")):
        spec=c["panels"][name]; taxa=taxa_by[key]
        ss=cross.set_index("accepted_taxon").loc[taxa,"analysis_state"]
        got=(len(taxa),int((ss=="U").sum()),int((ss=="D").sum()))
        exp=(spec["expected_n"],spec["expected_U"],spec["expected_D"])
        if got!=exp: raise AssertionError(("panel drift",name,got,exp))
        counts,env=build_panel_environment(occ,taxa)
        if any(int(counts.get(t,0))<spec["threshold"] for t in taxa):
            raise AssertionError(("threshold drift",name))
        states=panel_state_map(cross,taxa)
        assets=prepare_topology_assets(trees,taxa,env)
        res,df=exact_test(name,taxa,states,assets,spec["exact_state_maps"])
        results[name]=res; frames.append(df)
    p=results["strict_n10_primary"]
    top=p["observed"]["topology_composite"]; frac=p["exact_primary_rank"]["exact_fraction"]
    if all(x>0 for x in top) and frac<=0.05:
        cls="transition_regime_concordance_supported_on_internal_edges"
    elif all(x>0 for x in top):
        cls="transition_regime_internal_edge_directional_but_not_exceptional"
    else:
        cls="transition_regime_concordance_requires_terminal_edge_contribution"
    out={"version":"chapter2_orientation_transition_regime_internal_edge_result_v1","analysis_role":c["analysis_role"],"hypothesis":c["hypothesis"],"classification":cls,"panels":results,"claim_ceiling":c["claim_ceiling"]}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    pd.concat(frames,ignore_index=True).to_csv(a.out_csv,index=False)
    print(json.dumps(out,indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
