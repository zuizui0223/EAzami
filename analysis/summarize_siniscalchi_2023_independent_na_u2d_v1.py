#!/usr/bin/env python3
"""Audit and combine real independent North American nuclear U/D × niche tests.

Compares published author's 62-tip dataset and the two-taxon botanical
polymorphism exclusion without changing the East Asian fixed +BIO15/-BIO1
contrast.  No inference about actual ancient weather on historical branches.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def numeric_profile(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    states=Counter(r["orientation_state"] for r in rows)
    profiles={}
    for status in ("U","D"):
        included=[r for r in rows if r["orientation_state"]==status]
        if not included:
            raise ValueError("both states must be present in source panel")
        profiles[status]={
            "n":len(included),
            "BIO15_mean_original_author_scale": sum(float(r["bio15"]) for r in included)/len(included),
            "BIO1_mean_original_author_scale": sum(float(r["bio1"]) for r in included)/len(included),
        }
    return profiles, states


def summarise(args):
    original=read_json(args.source_manifest)
    if original["total_published_tree_tips"] != 63:
        raise ValueError("wrong molecular data source")
    result={}
    for key, root, tip_file in (
        ("author_coding",args.author_model,args.author_tips),
        ("mixed_head_excluded",args.conservative_model,args.conservative_tips),
    ):
        x=read_json(Path(root)/"result.json")
        groups,counts=numeric_profile(tip_file)
        if x["n_trees"]!=1 or x["states"]!={"U":groups["U"]["n"],"D":groups["D"]["n"]}:
            raise ValueError("real fitted Mk tip coverage disagrees with source table")
        if not x["model"]["branch_length_unit"].startswith("published calibrated chronogram"):
            raise ValueError("source calibrated age unit was silently changed")
        if any("per_substitution_length" in k for k in x["observed"]["per_tree"][0]):
            raise ValueError("Myr model was mislabeled as substitutions/site")
        if x["null"]["method"]!="monte_carlo_count_preserving" or x["null"]["draws"]<99:
            raise ValueError("exploratory fixed-count null incomplete")
        result[key]={
            "original_source_taxa":len(counts) and sum(counts.values()),
            "observed_states":x["states"],
            "within_North_America_U_D_source_means":groups,
            "raw_BIO15_D_minus_U":groups["D"]["BIO15_mean_original_author_scale"]-groups["U"]["BIO15_mean_original_author_scale"],
            "raw_BIO1_D_minus_U":groups["D"]["BIO1_mean_original_author_scale"]-groups["U"]["BIO1_mean_original_author_scale"],
            "ctmc_symmetric_q_per_Myr_conditional_on_source_date":x["observed"]["per_tree"][0]["q_symmetric_per_Myr_conditional_on_published_chronogram"],
            "endpoint_discordance_posterior_mass":x["observed"]["per_tree"][0]["endpoint_discordance_mass"],
            "branchwise_reconstructed_modern_BIO15_signed":x["observed"]["median_bio15"],
            "branchwise_reconstructed_modern_BIO1_signed":x["observed"]["median_bio1"],
            "fixed_East_Asian_contrast_composite":x["observed"]["median_composite"],
            "fixed_count_null":x["null"],
            "tip_input_sha256":x["input_sha256"]["tip_table"],
            "phylogeny_sha256":x["input_sha256"]["trees"],
        }
    a,b=result["author_coding"],result["mixed_head_excluded"]
    if a["observed_states"]!={"U":57,"D":5} or b["observed_states"]!={"U":55,"D":5}:
        raise ValueError("author-coded vs explicitly mixed-head-excluded states drift")
    all_positive = all(r["fixed_East_Asian_contrast_composite"]>0 for r in (a,b))
    all_null_lt05 = all(r["fixed_count_null"]["one_sided_rank"]<=.05 for r in (a,b))
    return {
        "version":"siniscalchi_2023_independent_na_nuclear_u2d_niche_v1",
        "research_article":"https://doi.org/10.1086/724310",
        "source_git_commit":original["immutable_commit"],
        "analyses":result,
        "fixed_direction":{"+BIO15":1,"-BIO1":-1},
        "direction_positive_in_both_panels":all_positive,
        "one_sided_fixed_count_p_le_0_05_in_both_panels":all_null_lt05,
        "scientific_boundary":[
            "This is one independently published North American 62-ingroup-tip nuclear chronogram, not the unavailable global Moreyra 2025 final-350 tree.",
            "Published author state 1 is pendent heads; two known mixed erect/nodding species are removed in a separately specified sensitivity analysis.",
            "Author CorollaColor class 2 combines white, pink and purple; it is NOT a binary flower colour gain/loss variable.",
            "Author BIO1/BIO15 are published modern taxon environment means; ancestral Brownian reconstruction is not observed historical climate.",
            "The branchwise endpoint U,D joint posterior is not a posterior on true transition event counts or individual transition dates.",
            "A count-preserving tip-label permutation is exploratory and does not fully preserve phylogenetic or spatial autocorrelation.",
            "The 5 D tip states and one continent limit power/generalization; acceptance of a positive result requires the independent global tree and regional replicate contrasts.",
            "The ML q scale uses the published calibrated chronogram; its interpretation depends on original dating uncertainty.",
            "Neither ecological selection nor adaptation nor causality is established.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("source-manifest","author-model","author-tips","conservative-model","conservative-tips"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=summarise(a)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "source_model":"Siniscalchi2023 real 62 NorthAmerican Cirsium tips",
        "author":{k:report["analyses"]["author_coding"][k] for k in (
            "observed_states","fixed_East_Asian_contrast_composite","fixed_count_null")},
        "sensitivity":{k:report["analyses"]["mixed_head_excluded"][k] for k in (
            "observed_states","fixed_East_Asian_contrast_composite","fixed_count_null")},
        "direction_positive_in_both":report["direction_positive_in_both_panels"],
    },indent=2))


if __name__=="__main__":
    main()
