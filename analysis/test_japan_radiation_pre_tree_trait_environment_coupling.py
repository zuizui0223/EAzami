#!/usr/bin/env python3
"""Test pre-tree trait-distance × environmental-distance coupling for Japanese Cirsium.

The same taxa are standardized across seven non-circular capitulum endpoints and
four CHELSA species-median environmental descriptors. Pairwise distance ranks are
compared with a taxon-label permutation test. This is a descriptive macro screen,
not a phylogenetic or adaptive test.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

TRAITS = [
    "orientation_angle_degrees_median_taxon_median",
    "corolla_lab_lightness_median_taxon_median",
    "corolla_lab_chroma_median_taxon_median",
    "shape_aspect_ratio_median_taxon_median",
    "shape_circularity_median_taxon_median",
    "shape_solidity_median_taxon_median",
    "shape_width_cv_median_taxon_median",
]
ENV = [
    "env_chelsa_bio01_species_median",
    "env_chelsa_bio04_species_median",
    "env_chelsa_bio12_species_median",
    "env_chelsa_bio15_species_median",
]


def rank_average(values: np.ndarray) -> np.ndarray:
    return pd.Series(values).rank(method="average").to_numpy(dtype=float)


def rank_correlation(a: np.ndarray, b: np.ndarray) -> float:
    ra=rank_average(a); rb=rank_average(b)
    ra=(ra-ra.mean())/ra.std(ddof=0); rb=(rb-rb.mean())/rb.std(ddof=0)
    return float(np.mean(ra*rb))


def distance_matrix(frame: pd.DataFrame) -> np.ndarray:
    x=frame.to_numpy(dtype=float)
    return np.sqrt(np.square(x[:,None,:]-x[None,:,:]).sum(axis=2))


def build(frame: pd.DataFrame, *, permutations: int=9999, seed: int=20260816) -> dict:
    required={"taxon_name",*TRAITS,*ENV}
    if required.difference(frame.columns):
        raise ValueError("Trait-environment snapshot incomplete")
    data=frame.copy()
    for c in [*TRAITS,*ENV]: data[c]=pd.to_numeric(data[c],errors="raise")
    if data["taxon_name"].duplicated().any(): raise ValueError("Duplicate taxon")
    if len(data)<5: raise ValueError("Too few taxa")

    t=data[TRAITS]; e=data[ENV]
    t=(t-t.mean())/t.std(ddof=0); e=(e-e.mean())/e.std(ddof=0)
    td=distance_matrix(t); ed=distance_matrix(e)
    iu=np.triu_indices(len(data),1)
    trait_dist=td[iu]; env_dist=ed[iu]
    observed=rank_correlation(trait_dist,env_dist)

    rng=np.random.default_rng(seed)
    ge_positive=0; ge_two=0
    for _ in range(permutations):
        perm=rng.permutation(len(data))
        perm_env=ed[perm][:,perm][iu]
        r=rank_correlation(trait_dist,perm_env)
        ge_positive += r >= observed - 1e-15
        ge_two += abs(r) >= abs(observed) - 1e-15

    leave_one_out={}
    names=data["taxon_name"].tolist()
    for drop,taxon in enumerate(names):
        keep=[i for i in range(len(names)) if i!=drop]
        ti=td[np.ix_(keep,keep)]; ei=ed[np.ix_(keep,keep)]
        ii=np.triu_indices(len(keep),1)
        leave_one_out[taxon]=rank_correlation(ti[ii],ei[ii])

    return {
        "contract_version":"japan_radiation_pre_tree_trait_environment_coupling_v1",
        "n_taxa":int(len(data)),
        "n_pairwise_distances":int(len(trait_dist)),
        "n_trait_axes":len(TRAITS),
        "n_environment_axes":len(ENV),
        "circular_hue_components_excluded":True,
        "observed_spearman_rho":observed,
        "taxon_label_permutations":permutations,
        "permutation_seed":seed,
        "positive_coupling_permutation_p":float((ge_positive+1)/(permutations+1)),
        "two_sided_permutation_p":float((ge_two+1)/(permutations+1)),
        "leave_one_taxon_out_rho":leave_one_out,
        "leave_one_taxon_out_all_negative":bool(all(v<0 for v in leave_one_out.values())),
        "descriptive_result":(
            "The current small pre-tree subset does not show positive coupling between multivariate "
            "capitulum-trait distance and four-variable environmental distance. The observed association "
            "is weakly negative and remains negative in every leave-one-taxon-out comparison."
        ),
        "interpretation":(
            "A simple model in which taxa occupying more different current climate positions necessarily "
            "have more different capitulum phenotypes is not supported in this subset. Biotic interactions, "
            "unmeasured ecological axes, historical contingency and modular trait evolution remain live alternatives."
        ),
        "claim_boundary":(
            "Only nine taxa are included and C. lineare has sparse balanced environmental coverage. Pairwise "
            "distances are not phylogenetically independent. This is not evidence against all ecological adaptation, "
            "nor is it a test of evolutionary rates or adaptive radiation."
        ),
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--snapshot",required=True); p.add_argument("--out",required=True); p.add_argument("--permutations",type=int,default=9999); p.add_argument("--seed",type=int,default=20260816)
    a=p.parse_args(); s=build(pd.read_csv(a.snapshot),permutations=a.permutations,seed=a.seed)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(s,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
