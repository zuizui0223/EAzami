#!/usr/bin/env python3
"""Select regional Moreyra source specimens without looking at head U/D states.

This staged geographic wave expands a real 45-tip Compositae1061 tree toward
an actual globally representative sample *without the previous shape-
ascertainment bias*. State/colour columns are not consulted until the exact
DNA sample roster is frozen. No molecular tree from this stage alone.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from audit_global_nuclear_294_orientation_join_v3 import rebuild_panel_and_join

SEED="real-world45-next-traitblind-geography-20261025-v1"
ALREADY_ADDED={
    "SAMN44017948", # vinaceum
    "SAMN44017849", # flodmanii
    "SAMN44017895", # ownbeyi
    "SAMN44017845", # erisithales
    "SAMN44017893", # oleraceum
}
REGIONS=("North_America","West_Palearctic","Continental_East_Central_Asia")
COUNTRY_RULES={
    "North_America": (
      "usa","u.s.a.","united states","mexico","canada",
    ),
    "West_Palearctic": (
      "spain","france","italy","netherlands","germany","austria",
      "greece","turkey","türkiye","czech","poland","portugal",
      "romania","serbia","croatia","bulgaria","switzerland","hungary",
      "ukraine","united kingdom","england","wales",
    ),
    "Continental_East_Central_Asia": (
      "china","mongolia","kazakhstan","kyrgyz","tajik","uzbekistan",
      "russia","nepal","tibet","himalaya",
    ),
}
CULTIVATED_WORDS=("botanical garden","botanic garden","bot. garden",
                  "cultivated","garden-grown","hort.")

def region(source_location: str):
    text=" ".join(str(source_location).lower().split())
    hits=[name for name in REGIONS if any(
        re.search(r"(?<![a-z])"+re.escape(word)+r"(?![a-z])",text)
        for word in COUNTRY_RULES[name]
    )]
    return hits[0] if len(hits)==1 else ""

def candidate_token(row):
    label=row["analysis_taxon_label"]
    return hashlib.sha256((SEED+"|"+row["biosample"]+"|"+label).encode()).hexdigest()

def build(n_each=3):
    if n_each<1 or n_each>8:
        raise ValueError("one-to-eight source samples per geographic cohort")
    _,source_rows,_=rebuild_panel_and_join()
    options=defaultdict(list)
    for r in source_rows:
        # All selection criteria below are molecular/geography/taxonomy only.
        # DO NOT use orientation_state_candidate or evidence_source fields.
        if r["biosample"] in ALREADY_ADDED:
            continue
        if r["name_review_required"]!="false":
            continue
        if not re.fullmatch(r"Cirsium [a-z][a-z-]+(?: var\. [a-z][a-z-]+)?",
                            r["analysis_taxon_label"]):
            continue
        if not r["source_studies"].startswith("Moreyra2025"):
            continue
        if len(r["run_accessions"].split("|"))!=1:
            continue
        locality=r["location"]+" "+r["region"]
        if any(z in locality.casefold() for z in CULTIVATED_WORDS):
            continue
        area=region(locality)
        if not area:
            continue
        if "japan" in locality.casefold():
            continue
        options[area].append(r)
    chosen=[]
    seen_taxa=set()
    for area in REGIONS:
        count=0
        for r in sorted(options[area],key=candidate_token):
            if r["analysis_taxon_label"] in seen_taxa:
                continue
            seen_taxa.add(r["analysis_taxon_label"])
            chosen.append({
                "source_region":area,
                "taxon_source_label":r["analysis_taxon_label"],
                "biosample":r["biosample"],
                "SRR":r["run_accessions"],
                "source_location":r["location"],
                "source_region_text":r["region"],
                "source_studies":r["source_studies"],
                "source_assay":r["assay"],
                "source_name_review":"false",
                "trait_selection_allowed":"false",
                "source_phenotype_before_selection":"NOT_OPENED",
                "source_tree_tip_provisional":f"GLB2_{r['run_accessions']}_{r['analysis_taxon_label'].replace(' ','_')}",
            })
            count+=1
            if count>=n_each:break
        if count<n_each:
            raise ValueError("not enough source-vouchered traitblind continental source species in "+area)
    if len(chosen)!=3*n_each or len({r["SRR"] for r in chosen})!=len(chosen):
        raise ValueError("selected source runs or species not unique")
    receipt={
        "version":"real_Cirsium_world45_nuclear_geographically_balanced_trait_blind_expansion_v1",
        "seed":SEED,
        "full_public_moreyra_chang_source_biosamples":294,
        "frozen_previous_real_world45_tips":45,
        "existing_five_outside_Japan_excluded":sorted(ALREADY_ADDED),
        "target_new_source_individuals":len(chosen),
        "target_result_tip_ceiling_after_nucleotide_QC":45+len(chosen),
        "design":[{"region":area,"n":sum(x["source_region"]==area for x in chosen)}
                  for area in REGIONS],
        "selection_used_head_colour_morphology_information":False,
        "selection_parameters":{
            "one_exact_source_preserving_taxon_per_new_BioSample":True,
            "source_taxon_name_review_flag_required_false":True,
            "source_replicated_biosamples_excluded":True,
            "source_cultivated_locality_excluded":True,
            "do_not_count_extra_original_Japan38_tips":True,
            "two_region_shape_ascertainment_from_original_world45_not_undone":True,
        },
        "new_run_accessions":[r["SRR"] for r in chosen],
        "true_nuclear_fastq_recovered":False,
        "new_nuclear_tree_inferred":False,
        "shape_state_assessed_only_after_freeze":True,
        "claim_limit":"Geographic molecular source selection. No morphological state entered algorithm; no new gene trees, species accepted name joins, event counts, adaptive or environmental inference."
    }
    return receipt,chosen

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,required=True)
    ap.add_argument("--per-region",type=int,default=3)
    args=ap.parse_args()
    info,chosen=build(args.per_region)
    args.outdir.mkdir(parents=True,exist_ok=True)
    with (args.outdir/"prospective_world54_source_molecular_intake.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(chosen[0]))
        w.writeheader();w.writerows(chosen)
    (args.outdir/"traitblind_3region_moreyra_sample_freeze.json").write_text(
        json.dumps(info,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
    )
    print(json.dumps({"n_sources":len(chosen),"region_counts":info["design"],
        "selected":[{"SRR":x["SRR"],"taxon":x["taxon_source_label"],
                     "region":x["source_region"]} for x in chosen]},indent=2))
if __name__=="__main__":main()
