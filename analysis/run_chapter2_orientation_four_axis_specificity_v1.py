#!/usr/bin/env python3
"""Bounded four-axis specificity sensitivity for Chapter 2 orientation ecology."""
from __future__ import annotations

import argparse, json, re
from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd
from Bio import Phylo

AXES = ["chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15"]
TOL = 1e-12


def args():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",type=Path,required=True)
    p.add_argument("--orientation",type=Path,required=True)
    p.add_argument("--base-assignments",type=Path,required=True)
    p.add_argument("--japan-occurrences",type=Path,required=True)
    p.add_argument("--taiwan-occurrences",type=Path,required=True)
    p.add_argument("--au-trees",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    return p.parse_args()

def norm(x): return re.sub(r"[^A-Za-z0-9_]+","",x.replace(" ","_").replace(".",""))

def trees(path,n=6):
    out=[]
    for line in [x.strip() for x in path.read_text().splitlines() if x.strip()][:n]:
        if line.startswith("[") and "]" in line: line=line.split("]",1)[1].strip()
        t=Phylo.read(StringIO(line),"newick"); t.root_with_outgroup({"name":"OUTGROUP_saff"}); out.append(t)
    if len(out)!=n: raise ValueError("topology count drift")
    return out

def cov(tree,taxa):
    terminals={x.name:x for x in tree.get_terminals()}; tips=[terminals[norm(x)] for x in taxa]; root=tree.common_ancestor(tips)
    C=np.zeros((len(tips),len(tips)))
    for i,a in enumerate(tips):
        for j,b in enumerate(tips):
            if i==j: C[i,j]=tree.distance(root,a)
            else:
                m=tree.common_ancestor(a,b); C[i,j]=tree.distance(root,m) if m!=root else 0.0
    return C+np.eye(len(tips))*1e-10

def z(x):
    x=np.asarray(x,float); return (x-x.mean())/x.std(ddof=1)

def gls_beta(y,X,C,idx=1):
    inv=np.linalg.inv(C); xtvi=X.T@inv
    return float(np.linalg.solve(xtvi@X,xtvi@y)[idx])

def panel_summary(taxa,state,env,ts,extra=None):
    out={}
    for axis in AXES:
        y=z(env.loc[taxa,axis].to_numpy(float)); bs=[]; loos=[]
        if extra is None: X=np.column_stack([np.ones(len(taxa)),state])
        else: X=np.column_stack([np.ones(len(taxa)),state,*extra])
        for t in ts:
            C=cov(t,taxa); bs.append(gls_beta(y,X,C))
            for k in range(len(taxa)):
                keep=np.arange(len(taxa))!=k
                if keep.sum()>X.shape[1]: loos.append(gls_beta(y[keep],X[keep],C[np.ix_(keep,keep)]))
        s=np.sign(np.median(bs))
        out[axis]={"beta_range":[min(bs),max(bs)],"beta_median":float(np.median(bs)),"abs_beta_median":float(abs(np.median(bs))),"topology_sign_agreement":f"{sum(np.sign(x)==s for x in bs)}/{len(bs)}","loo_sign_agreement":f"{sum(np.sign(x)==s for x in loos)}/{len(loos)}" if loos else "not_evaluable"}
    ranked=sorted(AXES,key=lambda a:(-out[a]["abs_beta_median"],a))
    for i,a in enumerate(ranked,1): out[a]["absolute_effect_rank"]=i
    return out,ranked

def rank_fraction(vals,obs):
    return {"n":len(vals),"count_at_least_observed":sum(v>=obs-TOL for v in vals),"fraction":sum(v>=obs-TOL for v in vals)/len(vals)}

def main():
    a=args(); contract=json.loads(a.contract.read_text()); assert contract["version"]=="chapter2_orientation_four_axis_specificity_contract_v1"
    jp=pd.read_csv(a.japan_occurrences).assign(region="JP"); tw=pd.read_csv(a.taiwan_occurrences).assign(region="TW"); occ=pd.concat([jp,tw],ignore_index=True)
    ori=pd.read_csv(a.orientation); ori=ori[ori.analysis_state.isin(["U","D"])]
    sm=dict(zip(ori.accepted_taxon,ori.analysis_state)); counts=occ.groupby("scientific_name_query").size(); eligible=set(counts[counts>=10].index)
    taxa=sorted(eligible & set(sm)); assert len(taxa)==9
    state=np.array([1.0 if sm[t]=="D" else 0.0 for t in taxa]); assert (state==0).sum()==5 and (state==1).sum()==4
    env=occ.groupby("scientific_name_query")[["latitude","longitude",*AXES]].mean().loc[taxa]
    ts=trees(a.au_trees,6)

    full,full_rank=panel_summary(taxa,state,env,ts)
    jp_taxa=[t for t in taxa if len(set(occ.loc[occ.scientific_name_query==t,"region"]))==1 and occ.loc[occ.scientific_name_query==t,"region"].iloc[0]=="JP"]
    jp_state=np.array([1.0 if sm[t]=="D" else 0.0 for t in jp_taxa]); assert len(jp_taxa)==7
    japan,japan_rank=panel_summary(jp_taxa,jp_state,env,ts)
    lat=z(env.loc[taxa,"latitude"].to_numpy(float)); lon=z(env.loc[taxa,"longitude"].to_numpy(float))
    geo,geo_rank=panel_summary(taxa,state,env,ts,extra=[lat,lon])

    base=pd.read_csv(a.base_assignments)
    assert len(base)==126 and int(base.observed.astype(str).str.lower().eq("true").sum())==1
    rec=base[base.recurrence_profile_match.astype(str).str.lower().eq("true")].copy(); assert len(rec)==40
    obs_id=str(base.loc[base.observed.astype(str).str.lower().eq("true"),"assignment_id"].iloc[0])
    covs=[cov(t,taxa) for t in ts]
    cf={axis:[] for axis in AXES}; observed={}
    yaxis={axis:z(env.loc[taxa,axis].to_numpy(float)) for axis in AXES}
    for row in base.to_dict("records"):
        dset=set(str(row["d_taxa"]).split("|")); st=np.array([1.0 if t in dset else 0.0 for t in taxa]); aid=str(row["assignment_id"])
        for axis in AXES:
            bs=[gls_beta(yaxis[axis],np.column_stack([np.ones(9),st]),C) for C in covs]
            med=float(np.median(bs))
            if aid==obs_id: observed[axis]=med
            cf[axis].append((aid,med,bool(str(row["recurrence_profile_match"]).lower()=="true")))
    cfres={}
    for axis in AXES:
        sign=1.0 if observed[axis]>=0 else -1.0; obs=sign*observed[axis]
        allv=[sign*v for _,v,_ in cf[axis]]; recv=[sign*v for _,v,r in cf[axis] if r]
        cfres[axis]={"observed_beta_median":observed[axis],"observed_direction":"positive" if sign>0 else "negative","all_126":rank_fraction(allv,obs),"recurrence_matched_40":rank_fraction(recv,obs)}

    focal=contract["frozen_focal_axis"]
    firsts=[full_rank[0],japan_rank[0],geo_rank[0]]
    if all(x==focal for x in firsts): cls="bio15_consistently_strongest_among_four_frozen_axes"
    elif focal in firsts: cls="bio15_strong_but_not_unique_among_four_frozen_axes"
    else: cls="bio15_not_the_leading_frozen_axis"
    result={"version":"chapter2_orientation_four_axis_specificity_result_v1","classification":cls,"absolute_effect_rank_leaders":{"full9":full_rank,"japan_only7":japan_rank,"lat_lon_adjusted9":geo_rank},"panels":{"full9":full,"japan_only7":japan,"lat_lon_adjusted9":geo},"counterfactual":cfres,"interpretation_boundary":contract["claim_ceiling"]}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2))

if __name__=="__main__": main()
