#!/usr/bin/env python3
"""Actual 53-tip molecular missing-locus sensitivity: 176 loci vs matched 74.

Both trees are re-inferred on SAME 53 molecular individuals with SAME IQ-TREE
TIM3+F+R3 model. Balanced panel is chosen before seeing head states or
molecular tree shape, by minimum source base-coverage only. Do not interpret
model changes as an independently replicated evolutionary process.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from Bio import Phylo

from audit_real_world53_ML_FastTree_S1_UD_sensitivity_v1 import group, splits, NA6, EU5, KAM_REPS
from annotate_real_world53_original_S1_nine_traits_Mk_v1 import fitted_models, model_phylo

ORIGINAL_SHA="5828ccd9f4f0b083f804f87bfa7407a20ad5eb52647e92eb5a26e812bd6807a7"
EXPECTED_COHORT_SHA="9179394190a3ab499a122439bca9c8bbe74e205a315440e4f7442b5ee225b237"
EPS=1e-8


def digest(p:Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def eval_tree(name,tree_file,traits,allowed):
    molecular=Phylo.read(tree_file,"newick")
    tips={tip.name for tip in molecular.get_terminals()}
    if len(tips)!=53 or "OUTGROUP_saff" not in tips or tips!=allowed:
        raise ValueError("molecular original input tips changed")
    ingroup,states=model_phylo(molecular,traits)
    original={r["tip_id"]:r for r in traits}
    stateCounts={s:sum(r["head_orientation"]==s for r in states.values()) for s in ("U","D","?")}
    if stateCounts!={"U":19,"D":9,"?":24}:
        raise ValueError("this sensitivity must not reassign species-level floral phenotype states")
    scores=fitted_models(ingroup,states)
    main={fit["Mk_model"]:fit for fit in scores if fit["case"]=="all_source_vouchers"}
    if len(scores)!=6 or set(main)!={"ER","ARD"}:
        raise ValueError("full missing-aware ER/ARD source model was not executed")
    if sum(x["head_orientation"] in {"U","D"} for x in states.values())!=28:
        raise ValueError("observed head state tally changed")
    return {
        "algorithm_panel":name,
        "original_source_nuclear_molecular_tree_SHA256":digest(tree_file),
        "source_original_Moreyra_S1_trait_rows":len(traits),
        "head_taxon_source_counts":stateCounts,
        "North_America_six_real_ingroup_specimens":group(molecular,NA6),
        "West_Palearctic_five_real_ingroup_specimens":group(molecular,EU5),
        "Kamchatka_two_same_named_taxon_molecular_samples":group(molecular,KAM_REPS),
        "Fitch_head_minimum_steps":main["ER"]["Fitch_minimum_states_on_fixed_tree"],
        "head_ER_Mk":{
            "log_likelihood":main["ER"]["log_likelihood"],
            "AICc_approx":main["ER"]["AICc_approx_unique_binomial_n"],
            "root_P_U":main["ER"]["root_P_U"],
        },
        "head_ARD_Mk":{
            "log_likelihood":main["ARD"]["log_likelihood"],
            "AICc_approx":main["ARD"]["AICc_approx_unique_binomial_n"],
            "root_P_U":main["ARD"]["root_P_U"],
        },
        "delta_AICc_ARD_minus_ER":main["ARD"]["AICc_approx_unique_binomial_n"]-
                main["ER"]["AICc_approx_unique_binomial_n"],
        "unrooted_nontrivial_splits":len(splits(molecular,tips)),
    }, molecular


def run(full:Path,balanced:Path,phenotype:Path,contract:Path,outdir:Path):
    if digest(full)!=ORIGINAL_SHA:
        raise ValueError("validated real 53-tip full 176-locus source Newick drift")
    contract_data=json.loads(contract.read_text(encoding="utf-8"))
    if (contract_data["old_alignment_SHA256"]!=EXPECTED_COHORT_SHA or
        contract_data["retained_loci"]!=74 or
        contract_data["retained_aligned_bp"]!=61240 or
        contract_data["trait_source_or_taxonomic_orientation_used_to_select_loci"] is not False):
        raise ValueError("source molecular coverage-only locus selection not pre-frozen")
    with phenotype.open(encoding="utf-8",newline="") as h:
        state_rows=list(csv.DictReader(h))
    if len(state_rows)!=53 or len({r["tip_id"] for r in state_rows})!=53:
        raise ValueError("original S1 molecular-tip/morphology sample coverage drift")
    all_ids={r["tip_id"] for r in state_rows}
    source_analytic,fulltree=eval_tree("original_all176_original_loci",full,state_rows,all_ids)
    balanced_analytic,newtree=eval_tree("coverage_blind_all13_ge40pct_74loci",balanced,state_rows,all_ids)
    old_splits=splits(fulltree,all_ids)
    balanced_splits=splits(newtree,all_ids)
    rf=len(old_splits.symmetric_difference(balanced_splits))
    summary={
        "version":"world53_176vs74_all13ge40pct_molecular_occupancy_phylogenetic_sensitivity_v1",
        "full_original_tree_source_sha256":ORIGINAL_SHA,
        "full_source_alignment_sha256":EXPECTED_COHORT_SHA,
        "same_53_source_molecular_tips_in_both":True,
        "same_IQTREE_substitution_model_TIM3_F_R3":True,
        "only_high_occupancy_74_gene_subset_changes":True,
        "original_nuclear_loci":176,
        "balanced_nuclear_loci":74,
        "balanced_alignment_columns":61240,
        "balanced_selection_looked_at_heads_or_flowers":False,
        "unrooted_53tip_RF":rf,
        "max_RF_for_two_53tip_fully_bifurcating_trees":100,
        "shared_unrooted_nontrivial_bipartitions":len(old_splits & balanced_splits),
        "original_unrooted_split_count":len(old_splits),
        "balanced_unrooted_split_count":len(balanced_splits),
        "two_real_same_SRA_derived_ML_trees":[source_analytic,balanced_analytic],
        "scientific_limits":[
            "Both IQ-TREE analyses reuse same 53 original biological sample sequences; changing loci creates a molecular missingness sensitivity, not an independent population replication.",
            "U/D source states were taken from taxonomic floral descriptions and not directly observed on sequenced voucher heads.",
            "Rooted source topology is not the dated ancestral world tree; Mk rates are per substitution/site and endpoint posteriors are not unique historical event counts.",
            "The 13 external samples each have at least 40% unambiguous data in all 74 retained whole original nuclear loci; Japanese original source coverage varies.",
            "A stable North American regional clade is not sufficient evidence of global origins, selection, pollinator mechanisms or ecological adaptation.",
            "Full 294-BioSample 350-gene Moreyra accepted species tree has not been jointly inferred or replaced by this 53-tip analysis."
        ],
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"world53_all176_vs_matched74_molecular_and_U_D_topology_result.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    rows=[]
    for x in summary["two_real_same_SRA_derived_ML_trees"]:
        rows.append({
            "tree":x["algorithm_panel"],"n_loci":176 if "all176" in x["algorithm_panel"] else 74,
            "Fitch_head_minimum_steps":x["Fitch_head_minimum_steps"],
            "ARD_minus_ER_AICc":x["delta_AICc_ARD_minus_ER"],
            "root_P_U_ER":x["head_ER_Mk"]["root_P_U"],
            "NA_six_exclusive":x["North_America_six_real_ingroup_specimens"]["clade_exclusive"],
            "EU_five_exclusive":x["West_Palearctic_five_real_ingroup_specimens"]["clade_exclusive"],
            "Kamchatka_same_species_sisters":x["Kamchatka_two_same_named_taxon_molecular_samples"]["clade_exclusive"],
            "original_source_molecule_sha256":x["original_source_nuclear_molecular_tree_SHA256"],
        })
    with (outdir/"world53_176vs74_nuclear_root_and_U_D_sensitivity.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    print(json.dumps({
        "full_loci":176,"balanced_loci":74,"balanced_aligned_bp":61240,
        "actual_53tip_unrooted_RF":rf,
        "comparison":[{k:r[k] for k in (
            "tree","Fitch_head_minimum_steps","ARD_minus_ER_AICc","NA_six_exclusive",
            "EU_five_exclusive","Kamchatka_same_species_sisters")} for r in rows],
    },indent=2),flush=True)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full-tree",type=Path,required=True)
    p.add_argument("--balanced-tree",type=Path,required=True)
    p.add_argument("--traits",type=Path,required=True)
    p.add_argument("--balanced-contract",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    run(args.full_tree,args.balanced_tree,args.traits,args.balanced_contract,args.outdir)


if __name__=="__main__":
    main()
