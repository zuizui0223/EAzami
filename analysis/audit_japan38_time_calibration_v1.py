#!/usr/bin/env python3
"""Audit which published time anchors are safe to map onto the Japan38 compatibility tree.

This deliberately distinguishes lineage-split anchors from reconstructed range events.
It does not produce a chronogram.  The purpose is to fail closed before any FDT5/FDT6
absolute-time analysis is attempted.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from Bio import Phylo

DOMINANT_RADIATION_EXCEPTIONS={"JPN_06","JPN_15"}
TA01_PAIR=("JPN_15","JPN_35")


def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))

def load_map(path):
    rows=read_csv(path);by={r["paper_japan_member_id"]:[x for x in r["tip_ids"].split("|") if x] for r in rows}
    rev={tip:mid for mid,tips in by.items() for tip in tips}
    if len(by)!=38 or len(rev)!=39:raise ValueError(f"expected 38 concepts / 39 biological tips, got {len(by)} / {len(rev)}")
    return rows,by,rev

def descendants(clade):return {x.name for x in clade.get_terminals()}

def mrca_for_tips(tree,tips):return tree.common_ancestor(*[{"name":x} for x in tips])

def main():
    p=argparse.ArgumentParser();p.add_argument("--tree",type=Path,required=True);p.add_argument("--concept-map",type=Path,required=True);p.add_argument("--events",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    tree=Phylo.read(str(a.tree),"newick");rows,by,rev=load_map(a.concept_map);events={r["event_id"]:r for r in read_csv(a.events)}
    names={x.name for x in tree.get_terminals()};expected=set(rev)|{"OUTGROUP_saff"}
    if names!=expected:raise ValueError(f"tree-tip mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}")
    tree.prune(target="OUTGROUP_saff")

    # Published 36/38 dominant-radiation membership is a hypothesis to compare with,
    # never a topology constraint on the independent compatibility tree.
    dominant_ids=sorted(set(by)-DOMINANT_RADIATION_EXCEPTIONS)
    dominant_tips=[tip for mid in dominant_ids for tip in by[mid]]
    dom=mrca_for_tips(tree,dominant_tips);dom_desc=descendants(dom)
    dom_extra=sorted({rev[x] for x in dom_desc-set(dominant_tips)})
    dominant_monophyletic=(dom_desc==set(dominant_tips))

    # TA01 is the only current source-interval lineage-split anchor whose endpoint
    # concepts are both directly represented on this Japan38 tree.
    ta01_tips=[by[mid][0] for mid in TA01_PAIR]
    anchor=mrca_for_tips(tree,ta01_tips);anchor_desc=descendants(anchor)
    anchor_concepts=sorted({rev[x] for x in anchor_desc})
    outside_anchor=sorted(set(by)-set(anchor_concepts))

    ta04_present=any("brevicaule" in r["paper_taxon_concept"] for r in rows) and any("irumtiense" in r["paper_taxon_concept"] for r in rows)
    result={
      "contract_version":"japan38_time_calibration_audit_v1",
      "tree_branch_length_unit":"substitutions_per_site",
      "paper_concepts":38,
      "biological_tips":39,
      "dominant_radiation_membership_hypothesis":{
        "source_claim":"36/38 paper concepts in one dominant Japanese radiation",
        "predeclared_secondary_history_concepts":sorted(DOMINANT_RADIATION_EXCEPTIONS),
        "compatibility_tree_monophyletic":dominant_monophyletic,
        "extra_concepts_inside_mrca":dom_extra,
        "ev01_may_be_used_as_direct_crown_calibration":False,
        "reason":"EV01 is a reconstructed range/opportunity event, and the published 36/38 membership is not monophyletic on the independent compatibility tree."
      },
      "directly_mappable_interval_anchor":{
        "event_id":"TA01",
        "endpoint_concepts":list(TA01_PAIR),
        "endpoint_tips":ta01_tips,
        "point_age_ma":float(events["TA01"]["point_age_ma"]),
        "young_bound_ma":float(events["TA01"]["young_bound_ma"]),
        "old_bound_ma":float(events["TA01"]["old_bound_ma"]),
        "mrca_biological_tips":len(anchor_desc),
        "mrca_paper_concepts":len(anchor_concepts),
        "paper_concepts_outside_mrca":outside_anchor,
        "eligible_for_sensitivity_calibration":True,
        "eligible_as_ecological_event_window":False
      },
      "other_anchors":{
        "TA02":"clade membership not frozen at exact Japan38 concept level; chronology context only",
        "TA03":"clade membership not frozen at exact Japan38 concept level; chronology context only",
        "TA04":"endpoint taxa absent from Japan38 tree" if not ta04_present else "endpoints present"
      },
      "readiness":{
        "relative_branch_length_history_ready":True,
        "single_anchor_chronogram_sensitivity_ready":True,
        "confirmatory_absolute_time_tree_ready":False,
        "fdt6_event_correspondence_ready":False,
        "fdt5_absolute_time_disparity_ready":False
      },
      "next_allowed_step":"Run TA01-only age-bound x smoothing-model sensitivity as a chronology scaffold; do not promote ecological-event matching unless node-age/topology identifiability improves.",
      "claim_boundary":"This audit identifies safe calibration mappings only. It does not convert substitutions/site to time and does not treat biogeographic event ages as node ages."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))

if __name__=="__main__":main()
