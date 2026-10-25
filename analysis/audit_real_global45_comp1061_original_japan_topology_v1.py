#!/usr/bin/env python3
"""Compare genuinely re-inferred 45-tip 176-nuclear-locus topology with original Japan38.

All 40 originally sequenced Japan38+reference tips must be present unchanged.
Additional five are source-authenticated Moreyra 2025 vouchers, NOT invented
generic-range taxon tips. Per-locus parsimony/phylogeny comparisons are performed
only on shared nuclear tips. Never require the added-world tree to preserve a
favoured Japanese monophyly hypothesis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from copy import deepcopy
from itertools import combinations
from pathlib import Path

from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"data/evidence"
OUTGROUP="OUTGROUP_saff"
FIVE=EVID/"global_5taxa_comp1061_real_target_capture_bridge_v1.csv"
OLDTREE=EVID/"japan38_comp1061_primary_tree_v1.nwk"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def names(tree):
    n=[t.name for t in tree.get_terminals()]
    if any(t is None for t in n) or len(n)!=len(set(n)):
        raise ValueError("duplicate or absent molecular tip identity")
    return set(n)


def canonical_unrooted_splits(tree):
    alltips=names(tree)
    splits=set()
    for clade in tree.find_clades():
        taxa={t.name for t in clade.get_terminals()}
        if len(taxa)<2 or len(alltips-taxa)<2:
            continue
        complement=alltips-taxa
        side=taxa if len(taxa)<len(complement) else complement
        if len(taxa)==len(complement):
            side=min((taxa,complement),key=lambda a:tuple(sorted(a)))
        splits.add(frozenset(side))
    return splits


def diagnose(newtree:Path, orig:Path=OLDTREE):
    older=Phylo.read(orig,"newick")
    actual=Phylo.read(newtree,"newick")
    b=names(older)
    n=names(actual)
    r=read_csv(FIVE)
    expected={"GLB_"+x["SRR"]+"_"+x["source_taxon"].replace(" ","_") for x in r}
    if len(b)!=40 or OUTGROUP not in b or len(n)!=45:
        raise ValueError("must receive true original 40-tip and new 45-tip trees")
    if n!=b|expected:
        raise ValueError("new ML tree leaf names violate source-authorized sample identities")
    pruned=deepcopy(actual)
    for tip in sorted(expected):
        pruned.prune(tip)
    if names(pruned)!=b:
        raise ValueError("five specimen pruning failed")
    origsplit=canonical_unrooted_splits(older)
    newsplit=canonical_unrooted_splits(pruned)
    if not origsplit or not newsplit:
        raise ValueError("empty reference topology split set")
    rf=len(origsplit^newsplit)
    union=len(origsplit|newsplit)
    common=len(origsplit&newsplit)
    if union<common or rf==0 and common==0:
        raise ValueError("nonsensical source topology split statistics")
    bytip={}
    tipobj={t.name:t for t in actual.get_terminals()}
    for x in r:
        tip="GLB_"+x["SRR"]+"_"+x["source_taxon"].replace(" ","_")
        target=tipobj[tip]
        dist=sorted(((actual.distance(target,tipobj[t]),t) for t in n if t!=tip and t!=OUTGROUP))
        nearest=[{"tip":y,"patristic_substitutions_per_site":float(d)} for d,y in dist[:5]]
        parent=actual.get_path(target)[-2] if len(actual.get_path(target))>=2 else actual.root
        sistertips=sorted({s.name for c in parent.clades if c!=target for s in c.get_terminals()})
        bytip[tip]={
            "source_taxon":x["source_taxon"],"region":x["region"],
            "head_state_source_not_same_voucher":x["head_state_source_only"],
            "n_immediate_sister_subtree_tips":len(sistertips),
            "immediate_sister_subtree_ingroup_names":sistertips[:12],
            "nearest_5_patristic_tips":nearest,
            "reported_parent_branch_internal_support":parent.name or "",
        }
    return {
        "version":"real_45tip_176locus_J38_topology_reinferrence_audit_v1",
        "input_new_tree_path":str(newtree),
        "input_new_tree_sha256":hashlib.sha256(newtree.read_bytes()).hexdigest(),
        "baseline_original_tree_sha256":hashlib.sha256(orig.read_bytes()).hexdigest(),
        "n_original_tip_names":len(b),
        "n_new_real_worldwide_tip_names":len(expected),
        "n_total_tree_tip_names":len(n),
        "unrooted_baseline_splits":len(origsplit),
        "unrooted_restricted_expanded_splits":len(newsplit),
        "identical_original_taxon_splits":common,
        "RF_distance_sum_symmetric_split_diff":rf,
        "RF_Jaccard_overlap":common/union,
        "region_totals_new_samples":dict(Counter(x["region"] for x in r)),
        "new_sample_topological_placement":bytip,
        "restriction_vs_full_tree":"Pruned added five tips only for topology benchmark. This is NOT a constraint that original Japan tips must remain monophyletic or keep original support.",
        "interpretation_boundary":"Actual ML topology and patristic neighbors are conditional on reference-projected nuclear 176-locus source QC; no dates, no ancestral-area test, no complete world-tree and no requirement of preserved historical Japanese radiation monophyly.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--real-45-tree",type=Path,required=True)
    p.add_argument("--original-40-tree",type=Path,default=OLDTREE)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=diagnose(a.real_45_tree,a.original_40_tree)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("n_original_tip_names","n_new_real_worldwide_tip_names",
        "unrooted_baseline_splits","unrooted_restricted_expanded_splits","identical_original_taxon_splits",
        "RF_distance_sum_symmetric_split_diff","RF_Jaccard_overlap")},indent=2))
if __name__=="__main__":main()
