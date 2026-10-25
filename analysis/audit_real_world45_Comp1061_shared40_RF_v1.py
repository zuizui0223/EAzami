#!/usr/bin/env python3
"""Empirical 45-tip versus original 40-tip shared nuclear backbone RF audit.

Compare true source Compositae1061 nuclear trees on the common original
Japan38+Carduus/Carthamus-root tip set. This is a topology-sensitivity
diagnostic, not a filter to cherry-pick placements or a global species tree.
"""
from __future__ import annotations

import argparse,hashlib,json
from pathlib import Path
from Bio import Phylo


def splits(tree, keep:set[str]):
    x=tree
    names={z.name for z in x.get_terminals()}
    if not keep<=names:raise ValueError("shared source tree tip names are missing")
    for tip in list(x.get_terminals()):
        if tip.name not in keep:
            x.prune(tip)
    if {z.name for z in x.get_terminals()}!=keep:
        raise ValueError("pruned tree loses accepted common molecular tips")
    out=set()
    for node in x.find_clades(order="preorder"):
        if node is x.root:continue
        group={z.name for z in node.get_terminals()}
        other=keep-group
        if min(len(group),len(other))<2:continue
        canonical=tuple(sorted(group))
        reverse=tuple(sorted(other))
        out.add(min(canonical,reverse,key=lambda t:(len(t),t)))
    return out


def compare(baseline:Path,pilot:Path):
    t1=Phylo.read(baseline,"newick")
    t2=Phylo.read(pilot,"newick")
    shared={x.name for x in t1.get_terminals()}
    all45={x.name for x in t2.get_terminals()}
    if len(shared)!=40 or "OUTGROUP_saff" not in shared:
        raise ValueError("baseline must be the frozen 39 Japan38 + saff reference")
    if len(all45)!=45 or shared-all45:
        raise ValueError("global 45-tip tree does not contain all 40 original source molecular tips")
    if len(all45-shared)!=5:
        raise ValueError("global tree does not contain exactly five new source molecules")
    # Biopython prune mutates trees, but original file SHA remains frozen.
    a=splits(t1,shared)
    b=splits(t2,shared)
    common=a&b
    RF=len(a-b)+len(b-a)
    return {
        "version":"global45_real_nuclear_176locus_Japan38_shared40_RF_sensitivity_v1",
        "original_tree_SHA256":hashlib.sha256(baseline.read_bytes()).hexdigest(),
        "real_global45_tree_SHA256":hashlib.sha256(pilot.read_bytes()).hexdigest(),
        "original_frozen_taxa":len(shared),
        "original_taxon_labels_preserved":True,
        "added_continental_molecular_tip_count":5,
        "baseline_nontrivial_unrooted_splits":len(a),
        "new_shared_taxon_nontrivial_unrooted_splits":len(b),
        "shared_splits_preserved":len(common),
        "RF_unrooted":RF,
        "RF_fraction_of_max_possible":RF/(2*(len(shared)-3)),
        "baseline_only_critical_splits":[list(x) for x in sorted(a-b) if len(x)<=5],
        "pilot_only_critical_splits":[list(x) for x in sorted(b-a) if len(x)<=5],
        "model_note":"RF compares original 40 source molecular tips on the same 176-locus alignment, with five newly recovered NA/European tips added. A different topology must be reported, not hidden.",
        "accepted_294_tip_moreyra350_worldwide_tree_completed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--pilot",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=compare(a.baseline,a.pilot)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:d[k] for k in ["RF_unrooted","RF_fraction_of_max_possible","shared_splits_preserved","baseline_nontrivial_unrooted_splits"]},indent=2))
if __name__=="__main__":
    main()
