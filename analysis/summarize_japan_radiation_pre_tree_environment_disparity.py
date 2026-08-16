#!/usr/bin/env python3
"""Descriptive pre-tree environmental-space comparison for Japanese Cirsium.

Uses four species-median CHELSA descriptors already frozen by Azami. The result
is a current environmental-position comparison, not a full niche model and not
an adaptive-radiation test by itself.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ENV = [
    "env_chelsa_bio01_species_median",
    "env_chelsa_bio04_species_median",
    "env_chelsa_bio12_species_median",
    "env_chelsa_bio15_species_median",
]


def distance(a: pd.Series, b: pd.Series) -> float:
    return float(np.linalg.norm(a.to_numpy(dtype=float)-b.to_numpy(dtype=float)))


def build(frame: pd.DataFrame, secondary_taxon: str="Cirsium lineare") -> dict:
    required={"taxon_name","japan_origin_role","n_azami_balanced_observations",*ENV}
    if required.difference(frame.columns):
        raise ValueError("Environment snapshot incomplete")
    data=frame.copy()
    for c in ENV:
        data[c]=pd.to_numeric(data[c],errors="raise")
    matrix=data.set_index("taxon_name")[ENV]
    if secondary_taxon not in matrix.index:
        raise ValueError("Secondary comparator missing")
    dominant=data.loc[data["japan_origin_role"].eq("dominant_main_japanese_radiation"),"taxon_name"].tolist()
    if len(dominant)<3:
        raise ValueError("Too few dominant-radiation taxa")
    dom=matrix.loc[dominant]
    mu=dom.mean(); sd=dom.std(ddof=0)
    if sd.le(0).any():
        raise ValueError("Zero environmental variance")
    z=(matrix-mu)/sd
    secondary_centroid=distance(z.loc[secondary_taxon],pd.Series(0.0,index=ENV))
    loo={}
    for taxon in dominant:
        rest=dom.drop(index=taxon)
        zloo=(dom.loc[taxon]-rest.mean())/rest.std(ddof=0)
        loo[taxon]=float(np.linalg.norm(zloo.to_numpy(dtype=float)))
    within=[(a,b,distance(z.loc[a],z.loc[b])) for a,b in combinations(dominant,2)]
    secpairs=[(t,distance(z.loc[secondary_taxon],z.loc[t])) for t in dominant]
    max_within=max(within,key=lambda x:x[2]); max_loo=max(loo.items(),key=lambda x:x[1])
    line_row=data.loc[data["taxon_name"].eq(secondary_taxon)].iloc[0]
    return {
        "contract_version":"japan_radiation_pre_tree_environment_disparity_v1",
        "analysis_scope":"descriptive_species_median_CHELSA_environment_space",
        "environment_variables":ENV,
        "n_taxa":int(len(matrix)),
        "n_dominant_radiation_taxa":int(len(dominant)),
        "secondary_history_comparator":secondary_taxon,
        "secondary_balanced_observation_count":int(line_row["n_azami_balanced_observations"]),
        "secondary_distance_to_dominant_centroid":secondary_centroid,
        "largest_dominant_leave_one_out_distance":{"taxon":max_loo[0],"distance":max_loo[1]},
        "within_dominant_pairwise":{
            "n_pairs":len(within),
            "median_distance":float(np.median([x[2] for x in within])),
            "maximum":{"taxon_a":max_within[0],"taxon_b":max_within[1],"distance":max_within[2]},
        },
        "secondary_to_dominant_pairwise":{
            "minimum_distance":float(min(x[1] for x in secpairs)),
            "median_distance":float(np.median([x[1] for x in secpairs])),
            "maximum_distance":float(max(x[1] for x in secpairs)),
        },
        "descriptive_result":(
            "The replicated secondary-history comparator is not uniquely isolated in the current four-variable "
            "environmental-position space. The largest dominant-radiation leave-one-out displacement and "
            "largest within-dominant pairwise distance exceed the corresponding secondary-history distances."
        ),
        "claim_boundary":(
            "Species medians from the Azami public-image occurrence context are not complete niche distributions. "
            "C. lineare has only three balanced observations. This result does not estimate niche evolutionary rate, "
            "ecological opportunity, selection or adaptation."
        ),
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--snapshot",required=True); p.add_argument("--out",required=True)
    a=p.parse_args(); frame=pd.read_csv(a.snapshot); summary=build(frame)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
