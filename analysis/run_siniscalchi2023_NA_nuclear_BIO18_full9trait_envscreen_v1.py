#!/usr/bin/env python3
"""Test BIO18 plus all source environment axes against NINE ORIGINAL Cirsium traits.

Published *independent North American* dated Compositae1061 nuclear tree
(Siniscalchi, Ackerfield & Folk 2023 DOI 10.1086/724310), original author
nine-character categorical matrix and original 38 environmental variables:
ALL verified against the authors' immutable commit c925d4a.

Test one environmental response at a time: standardized present-day species
climate/environment ~ original qualitative flower/head trait factor, using
a Brownian-motion (lambda=1) phylogenetic GLS covariance. This is an
association model, NOT evidence that climate caused historical transitions.
Also run independence (lambda=0) comparison. BH q across the WHOLE
hypothesis family per covariance; report sparse categories, D leave-one-out,
original author's documented FNA mixed-head sensitivity, and PGLS
BIO18 conditional on BIO1/BIO15. No new data scraping or invented phenotypes.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import f as f_dist
from scipy.stats import t as t_dist

from run_siniscalchi_2023_real_nuclear_traits_v1 import acquire, HEAD, COLOUR

OUTGROUP="Cirsium_vulgare"
AMBIGUOUS_HEAD={"Cirsium_eatonii","Cirsium_joannae"}
TRAITS=("CorollaThroat","CorollaColor","Duration","GlutinousRidge",
        "Habit","HeadPosition","InnerPhyllaryColor","OuterPhyllaryPosition",
        "StyleBranchColor")
PREFLIGHT_AXES=("BIO18","BIO15","BIO1")
ENVIRONMENT=["Aridity"]+[f"BIO{x}" for x in range(1,20)]+[
    "Aspect","Elevation","Slope","Bulk","Clay","Coarse","Nitrogen","pH",
    "Sand","Silt","Carbon","NeedleLeaf","Evergreen","Deciduous",
    "Mixed","Shrubs","Herbaceous"]
DIVERSIFICATION_RATE=("DR",)  # molecular tree-derived rate, not environmental
CATALOG=ENVIRONMENT+list(DIVERSIFICATION_RATE)
EXPECTED_ENV=len(ENVIRONMENT)
EPS=1e-12


def read_rows(path,key):
    with path.open(encoding="utf-8-sig",newline="") as handle:
        rows=list(csv.DictReader(handle))
    if len({r[key] for r in rows})!=len(rows):
        raise ValueError("original botanical/clinical source contains duplicate taxon")
    return {r[key]:r for r in rows}


def source(asset_dir):
    files=acquire(asset_dir)
    phylogeny=Phylo.read(files["environmental/cirsium.phyluce95p.ultrametric.tre"],"newick")
    phylogeny.root_with_outgroup({"name":OUTGROUP})
    phylogeny.prune(OUTGROUP)
    names=[t.name for t in phylogeny.get_terminals()]
    original=read_rows(files["traits/traits.csv"],"Species")
    environment=read_rows(files["environmental/cirsium_environmental_allcombined_DR.csv"],"taxa")
    if len(names)!=62 or len(set(names))!=62 or set(names)!=(set(original)-{OUTGROUP}):
        raise ValueError("original author's real North American molecular ingroup differs from original phenotype")
    if set(names)!=(set(environment)-{OUTGROUP}):
        raise ValueError("published environmental original source table does not join all 62 real nuclear ingroup tips")
    if len(ENVIRONMENT)!=37 or len(CATALOG)!=38:
        raise ValueError("original source table has 37 environmental variables plus tree-derived DR diversification")
    for name in names:
        for axis in CATALOG:
            n=float(environment[name][axis])
            if not math.isfinite(n):
                raise ValueError("invalid original environment variable: "+name+" "+axis)
        for trait in TRAITS:
            if original[name][trait] not in ("0","1","2","3"):
                raise ValueError("invalid original morphological code: "+trait)
    return phylogeny,names,original,environment


def covariance(tree,names):
    # Cov(i,j) is shared branch length from the ingroup molecular root,
    # as under a zero-drift BM on a genuine published dated tree.
    tip={t.name:t for t in tree.get_terminals()}
    c=np.zeros((len(names),len(names)),dtype=float)
    for i,a in enumerate(names):
        c[i,i]=float(tree.distance(tip[a]))
        for j in range(i):
            co=tree.common_ancestor(tip[a],tip[names[j]])
            c[i,j]=c[j,i]=float(tree.distance(co))
    if c.diagonal().min()<=0 or not np.isfinite(c).all():
        raise ValueError("source dated tree gives invalid Brownian covariance")
    scale=float(np.mean(c.diagonal()))
    c/=scale
    jitter=0.
    for t in [0.,1e-10,1e-9,1e-8,1e-7,1e-6,1e-5]:
        try:
            chol=np.linalg.cholesky(c+t*np.eye(len(names)))
            jitter=t
            break
        except np.linalg.LinAlgError:
            continue
    else:
        raise ValueError("original phylogenetic covariance remains singular after small numerical jitter")
    return chol,jitter


def cleanvec(values):
    x=np.asarray(values,dtype=float)
    if not np.isfinite(x).all() or len(x)<7:
        raise ValueError("invalid empirical vector")
    mu=float(x.mean())
    std=float(x.std(ddof=1))
    if std<=EPS:
        return None
    return (x-mu)/std


def gls_test(y,levels,chol,extra_covariates=None):
    # Standardized modern environmental value ~ categorical qualitative trait.
    # Extra covariates can test the BIO18 partial effect of head position while
    # holding BIO1 and BIO15 (standardized) fixed.
    levels=np.asarray(levels,dtype=str)
    unique=sorted(set(levels))
    n=len(y)
    X0=np.ones((n,1))
    if extra_covariates is not None:
        cov=np.asarray(extra_covariates,dtype=float)
        if cov.shape[0]!=n or cov.ndim!=2:
            raise ValueError("covariate shape invalid")
        X0=np.column_stack([X0,cov])
    X1=np.column_stack([X0]+[(levels==l).astype(float) for l in unique[1:]])
    df1=len(unique)-1
    df2=n-X1.shape[1]
    if df1<1 or df2<3:
        return None
    w0=np.linalg.solve(chol,X0)
    w1=np.linalg.solve(chol,X1)
    v=np.linalg.solve(chol,y)
    beta0=np.linalg.lstsq(w0,v,rcond=None)[0]
    beta1=np.linalg.lstsq(w1,v,rcond=None)[0]
    rss0=float(np.sum((v-w0@beta0)**2))
    rss1=float(np.sum((v-w1@beta1)**2))
    if rss1<EPS:
        raise ValueError("phylogenetic response has near-zero residual variance")
    fstat=max(0.,((rss0-rss1)/df1)/(rss1/df2))
    p=float(f_dist.sf(fstat,df1,df2))
    out={
        "factor_levels":"|".join(unique),
        "n_levels":len(unique),
        "smallest_level_n":min(Counter(levels).values()),
        "Fstat":fstat,"df1":df1,"df2":df2,"p":p,
        "partial_r2":max(0.,(rss0-rss1)/rss0),
        "n_original_taxa":n,
    }
    if len(unique)==2:
        cov_beta=np.linalg.inv(w1.T@w1)*(rss1/df2)
        se=math.sqrt(float(cov_beta[-1,-1]))
        coeff=float(beta1[-1])
        tcrit=float(t_dist.ppf(.975,df2))
        out.update({"standardized_difference_level_1_minus_0":coeff,
                    "standardized_difference_CI95_lower":coeff-tcrit*se,
                    "standardized_difference_CI95_upper":coeff+tcrit*se,
                    "original_code0":unique[0],"original_code1":unique[1]})
    return out


def BH(rows,column,qname):
    active=[r for r in rows if math.isfinite(r[column])]
    active.sort(key=lambda r:r[column])
    smallest=1.0
    n=len(active)
    for i in reversed(range(n)):
        r=active[i]
        smallest=min(smallest,float(r[column])*n/(i+1))
        r[qname]=min(1.0,smallest)
    return n


def run(asset_dir,outdir):
    tree,names,traits,env=source(asset_dir)
    base,regularization=covariance(tree,names)
    ey={axis:cleanvec([float(env[t][axis]) for t in names]) for axis in CATALOG}
    if any(ey[axis] is None for axis in CATALOG):
        raise ValueError("a published source climate variable is constant across all 62 Cirsium species")
    original_factor={char:[traits[t][char] for t in names] for char in TRAITS}
    two_models={}
    rows=[]
    for kind,chol in (("Brownian_phylogenetic",base),("iid_nonphylogenetic",np.eye(len(names)))):
        two_models[kind]=chol
        for char in TRAITS:
            for axis in CATALOG:
                result=gls_test(ey[axis],original_factor[char],chol)
                if result is None:raise ValueError("unestimable trait/axis with source categorical state")
                rows.append({"covariance_model":kind,"character":char,"environment_axis":axis,
                    "source_original_trait_state_counts":json.dumps(dict(sorted(Counter(original_factor[char]).items()))),
                    "sparse_trait_state_under_3_taxa":result["smallest_level_n"]<3,
                    **result})
    # Original DR column is estimated tip diversification RATE, from this
    # same molecular tree. Keep its nine comparisons separate from abiotic,
    # topographic, soil, climate and vegetation environmental hypotheses.
    for row in rows:
        row["BH_q_all_9traits_x_37environment_axes"]=float("nan")
    for kind in two_models:
        family=[row for row in rows if row["covariance_model"]==kind
                and row["environment_axis"] in ENVIRONMENT]
        BH(family,"p","BH_q_all_9traits_x_37environment_axes")
        if len(family)!=len(TRAITS)*len(ENVIRONMENT):
            raise ValueError("entire 333-test morphological/environmental hypothesis family incomplete")

    head=[traits[t]["HeadPosition"] for t in names]
    bio18=ey["BIO18"]
    head_predeclared={
        "original_authors_all62":gls_test(bio18,head,base),
        "nonphylogenetic_all62":gls_test(bio18,head,np.eye(62))
    }
    head_predeclared["phylogenetic_all62"]=head_predeclared["original_authors_all62"]
    remaining=[t for t in names if t not in AMBIGUOUS_HEAD]
    if len(remaining)!=60:
        raise ValueError("FNA botanical mixed-head exclusion samples are not represented as expected")
    tr=copy.deepcopy(tree)
    for t in AMBIGUOUS_HEAD:
        tr.prune(t)
    cov2,jit2=covariance(tr,remaining)
    index={t:i for i,t in enumerate(names)}
    head_predeclared["FNA_mixed_head_excluded_60"]=gls_test(
        bio18[[index[t] for t in remaining]],
        [traits[t]["HeadPosition"] for t in remaining],cov2)
    loo=[]
    for dt in (t for t in names if traits[t]["HeadPosition"]=="1"):
        subset=[t for t in names if t!=dt]
        tr=copy.deepcopy(tree);tr.prune(dt)
        ch,_=covariance(tr,subset)
        # BIO18 z is standardised ONCE across full author cohort
        current=gls_test(bio18[[index[t] for t in subset]],
                   [traits[t]["HeadPosition"] for t in subset],ch)
        loo.append({"omitted_D_source_taxon":dt,
                    "n_remaining_D":4,
                    "BIO18_effect_standardized_D_minus_U":current["standardized_difference_level_1_minus_0"],
                    "BIO18_PGLS_p":current["p"]})
    conditional=gls_test(
        bio18,head,base,
        extra_covariates=np.column_stack([ey["BIO15"],ey["BIO1"]]))
    v=np.column_stack([ey["BIO18"],ey["BIO15"],ey["BIO1"]])
    correlations=np.corrcoef(v,rowvar=False)
    axes_focus=[]
    for ax in ("BIO18","BIO15","BIO1","BIO12","Elevation","Aridity"):
        raw_U=[float(env[t][ax]) for t in names if traits[t]["HeadPosition"]=="0"]
        raw_D=[float(env[t][ax]) for t in names if traits[t]["HeadPosition"]=="1"]
        phylo=next(r for r in rows if r["covariance_model"]=="Brownian_phylogenetic"
                and r["character"]=="HeadPosition" and r["environment_axis"]==ax)
        axes_focus.append({"axis":ax,"n_U":len(raw_U),"n_D":len(raw_D),
            "raw_current_environment_mean_U":sum(raw_U)/len(raw_U),
            "raw_current_environment_mean_D":sum(raw_D)/len(raw_D),
            "raw_D_minus_U":sum(raw_D)/len(raw_D)-sum(raw_U)/len(raw_U),
            "phylogenetic_PGLS_standardized_D_minus_U":
                  phylo["standardized_difference_level_1_minus_0"],
            "PGLS_p":phylo["p"],
            "BH_q_all_traits_env":phylo["BH_q_all_9traits_x_37environment_axes"]})
    pairwise=[]
    for a_index,a in enumerate(TRAITS):
        for b in TRAITS[a_index+1:]:
            A=[traits[t][a] for t in names]
            B=[traits[t][b] for t in names]
            av=sorted(set(A));bv=sorted(set(B))
            observed=np.array([[sum(x==ca and y==cb for x,y in zip(A,B))
                      for cb in bv] for ca in av],dtype=float)
            n=observed.sum()
            prob=observed.sum(axis=1,keepdims=True)@observed.sum(axis=0,keepdims=True)/n
            chi=float(np.sum((observed-prob)**2/prob))
            v=math.sqrt(chi/(n*min(len(av)-1,len(bv)-1)))
            pairwise.append({"morph_A":a,"morph_B":b,"nonphylogenetic_Cramers_V_descriptive_only":v,
                "states_cross_tab":json.dumps(observed.astype(int).tolist())})
    outdir.mkdir(parents=True,exist_ok=True)
    cols=list(rows[0])
    with (outdir/"NorthAmerica_original63_nine_traits_37environment_plus_DR_BrownianPGLS_and_iid.csv").open(
        "w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=cols)
        writer.writeheader();writer.writerows(rows)
    with (outdir/"source_original_nine_trait_pairwise_CramersV_descriptive.csv").open(
        "w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(pairwise[0]))
        writer.writeheader();writer.writerows(pairwise)
    top=sorted((r for r in rows if r["covariance_model"]=="Brownian_phylogenetic"
                and r["environment_axis"] in ENVIRONMENT),
        key=lambda x:x["p"])[:24]
    source_result={
        "contract":"Siniscalchi2023_real_62species_nuclear_9traits_37env_plus_separate_DR_BIO18_v2",
        "original_source_author":"Siniscalchi, Ackerfield & Folk 2023",
        "source_article_DOI":"https://doi.org/10.1086/724310",
        "immutable_source_commit":"c925d4af86160064448f794a9715f70b917a2786",
        "original_nuclear_tree_tips_including_excluded_C_vulgare":63,
        "original_NorthAmerican_ingroup_nuclear_taxa":len(names),
        "original_source_morphological_character_count":len(TRAITS),
        "original_environment_variable_count":len(ENVIRONMENT),
        "environment_variables_original_source":ENVIRONMENT,
        "separate_tip_diversification_rate_is_not_environment":"DR",
        "n_separate_DR_morphology_tests_per_covariance":len(TRAITS),
        "n_planned_environment_x_trait_tests_per_covariance":len(TRAITS)*len(ENVIRONMENT),
        "multitest":"BH across exactly 333 morphology x environmental tests per covariance. The original tree-derived DR diversification rate is NOT an environmental variable and is excluded from this FDR family. Environmental axes are correlated and some floral colour classes contain singletons.",
        "source_head_states_by_original_authors":dict(Counter(head)),
        "head_D_taxa":[t for t in names if traits[t]["HeadPosition"]=="1"],
        "nuclear_covar_model":"Brownian lambda=1 phylogenetic GLS on original author's published calibrated North American molecular tree; outgroup C. vulgare excluded",
        "nuclear_covar_regularization_diagonal_fraction":regularization,
        "fna_60taxa_covar_regularization_diagonal_fraction":jit2,
        "source_bio18_PGLS_primary":head_predeclared,
        "source_BIO18_partial_head_association_while_adjusting_BIO15_BIO1":conditional,
        "environment_variable_correlations_BIO18_BIO15_BIO1":{
            "BIO18_BIO15":float(correlations[0,1]),
            "BIO18_BIO1":float(correlations[0,2]),
            "BIO15_BIO1":float(correlations[1,2])
        },
        "leave_each_of_five_original_D_species_out_BIO18":loo,
        "head_environment_focus":axes_focus,
        "top_24_exploratory_environment_morphology_PGLS_associations":[
            {"character":r["character"],"environment_axis":r["environment_axis"],
             "p":r["p"],"BH_q":r["BH_q_all_9traits_x_37environment_axes"],
             "n_cat":r["n_levels"],"min_cat_n":r["smallest_level_n"]}
             for r in top
        ],
        "n_PGLS_discoveries_FDR_q_under_0_05":sum(r["BH_q_all_9traits_x_37environment_axes"]<.05
           for r in rows if r["covariance_model"]=="Brownian_phylogenetic"),
        "n_iid_discoveries_FDR_q_under_0_05":sum(r["BH_q_all_9traits_x_37environment_axes"]<.05
           for r in rows if r["covariance_model"]=="iid_nonphylogenetic"),
        "n_source_traits_NA_complete":len(TRAITS),
        "source_old_world53_nine_trait_match_limited_to_six_molecular_individuals":True,
        "one_continent_scope":"North America only, not global Cirsium; 5 D taxa, published taxon-level phenotype source rather than original sequenced vouchers",
        "original_BIO18_definition":"Precipitation of warmest quarter, source climate taxon mean (contemporaneous), not climate at true ancestral U->D event",
        "response_direction":"environment response ~ original categorical trait; effect is species-level association and NOT a causal trait-evolution rate modulation by environment",
        "brownian_model_assumption":"fixed BM covariance, does not test OU vs BM/phylo-lambda, underrepresents unknown sampling/trait errors",
        "not_inferred":["historical U-to-D transition-time climate","exact independent gains or losses","fitness / pollinator mechanism","white flower reactivation from pooled pink-white-purple original author colour code 2","global 294-tip/350-locus nuclear tree"]
    }
    (outdir/"NA62_nuclear_BIO18_nine_traits_38env_phylogenetic_screen.json").write_text(
        json.dumps(source_result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "real_ingroup_taxa":len(names),"morphological_traits":len(TRAITS),
        "source_environment_axes":len(ENVIRONMENT),
    "tree_derived_DR_outcome_separate_from_environment":True,
        "tests_per_model":len(TRAITS)*len(ENVIRONMENT),
        "bio18_original_authors":head_predeclared["original_authors_all62"],
        "bio18_FNA_mixed_head_excluded":head_predeclared["FNA_mixed_head_excluded_60"],
        "bio18_conditioned_on_BIO15_BIO1":conditional,
        "focused_head_contrasts":axes_focus,
        "n_phylogenetic_FDR_discoveries":source_result["n_PGLS_discoveries_FDR_q_under_0_05"]
    },indent=2))
    return source_result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asset-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    run(a.asset_dir,a.outdir)

if __name__=="__main__":
    main()
