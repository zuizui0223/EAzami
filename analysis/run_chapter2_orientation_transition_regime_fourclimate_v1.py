#!/usr/bin/env python3
"""Exact EAzami Chapter2 CTMC U->D × Brownian environmental branch shifts.

NEW USER-REQUESTED POST-RESULT EXPOSURES:
CHELSA v2.1 BIO18 (warmest quarter precipitation), BIO05 (max temp warmest
month), CHELSA original rsds_mean, and WorldClim v2.1 30s elevation.
Reuses EXACT original occurrence assets, original manuscript U/D crosswalk,
source 6 AU-accepted nuclear multilocus trees, same 12 and 13 taxa panels,
q MLE per topology/map, exact posterior P(U,D)-P(D,U), squared-change
Brownian branch states, and count-preserving complete permutations.

This is the ORIGINAL EAzami U/D phylogenetic transition workflow, NOT a
new S1 image-angle PGLS or a PIC posthoc substitution. Baseline original
BIO15/BIO1 9-taxon branch values must reproduce BEFORE applying new axes.

As the new four axes were chosen after looking at original S1/S2 results,
there is no predeclared directional 4D vector. PRIMARY new diagnostic is
unsigned four-axis Euclidean branchwise alignment, with exact conditional
permutation rank; axis effects are signed descriptive, two-sided absolute
ranks and max-|standardized effect| FWER reported. Region-preserving null
and lat/lon-residual diagnostics are separate and cannot rescue the primary.

Inputs are original GBIF sample sites. Never equate present-day climate with
ancestral or transition-time environments or infer adaptation/fitness.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio

from analysis import run_chapter2_orientation_transition_regime_hypothesis_v1 as h

AXES=("chelsa_bio18","chelsa_bio05","chelsa_rsds_mean","elevation_m")
ORIGINAL=("chelsa_bio15","chelsa_bio01")
SOURCE_SHA={
 "chelsa_bio18":"68b0b1cb905cdf6972364e947e137f714a68d287f38863b1516161a2a4bbd7ec",
 "chelsa_bio05":"90078d99eeb0b08dd1a115a5ffa60b7c19e5849686854db950283cbac9d3817d",
 "elevation_m":"1d57ce9fd3584cea6a227396bc75ef88522fd5346e8487c17370885c0499716e",
 "chelsa_rsds_mean":"cc1ad14a70a1a940be3d01d918d4c3f7e35db95b86b12af9be5487e1bbc1fc7d",
}
SRC_FILENAMES={
 "chelsa_bio18":"CHELSA_bio18_1981-2010_V.2.1.tif",
 "chelsa_bio05":"CHELSA_bio05_1981-2010_V.2.1.tif",
 "elevation_m":"wc2.1_30s_elev.tif",
}
CELL_SIZE_DEG=5
SOURCE_N_JP=693
SOURCE_N_TW=55
PANELS={"n5_primary":("5",12,7,5,792),
        "n3_sensitivity":("3",13,7,6,1716),
        "n10_strict":("10",9,5,4,126)}
EPS=1e-12

def sha256_file(path):
    sh=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(4<<20),b""):
            sh.update(chunk)
    return sh.hexdigest()

def positive_raster(path,expected):
    actual=sha256_file(path)
    if actual!=expected:
        raise ValueError(f"Original CHELSA/DEM raster changed at {path.name}: {actual}")
    return actual

def sample_raster(path,frame):
    with rasterio.open(path) as src:
        if src.crs is None or src.crs.to_epsg()!=4326 or src.count!=1:
            raise ValueError("Four-axis sampling expects authentic single-band WGS84 TIFF")
        if not(20000<=src.width<=50000 and 10000<=src.height<=26000):
            raise ValueError("The source climate grid cannot be identified as 30 arc seconds")
        coords=list(zip(frame.longitude.to_numpy(float),frame.latitude.to_numpy(float)))
        raw=np.array([float(item[0]) for item in src.sample(coords,masked=False)],float)
        if src.nodata is not None:
            raw[np.isclose(raw,float(src.nodata))]=np.nan
        values=raw*float(src.scales[0])+float(src.offsets[0])
        return values,{"source_file":Path(path).name,"source_sha256":sha256_file(path),
          "n_original_occurrence_locations":len(coords),
          "source_complete":int(np.isfinite(values).sum()),
          "width":src.width,"height":src.height,
          "scale":float(src.scales[0]),"offset":float(src.offsets[0]),
          "source_nodata":None if src.nodata is None else float(src.nodata)}

def sample_original_rsds_cache(frame,root,source_metadata):
    import glob
    meta=json.loads(Path(source_metadata).read_text())["chelsa_rsds_mean"]
    grid=json.loads((Path(root)/"grid.json").read_text())
    if (meta["source_sha256"]!=SOURCE_SHA["chelsa_rsds_mean"]
        or grid["source_sha256"]!=SOURCE_SHA["chelsa_rsds_mean"]
        or grid["resampling"]!="none"
        or len(grid["tiles"])!=316):
        raise ValueError("Archived original S1/S2 RSDS grid identity drift")
    for name,digest in grid["cache_sha256"].items():
        if sha256_file(Path(root)/name)!=digest:
            raise ValueError("Frozen original RSDS one-km tile digest mismatch "+name)
    from rasterio.transform import rowcol
    lat=frame.latitude.to_numpy(float);lon=frame.longitude.to_numpy(float)
    # Original affine transform (full, not rounded 5-degree proxy).
    affine=grid["transform"]
    a,b,c,d,e,f=map(float,affine)
    det=a*e-b*d
    if abs(det)<1e-15:raise ValueError("Original raster has singular affine transform")
    col=np.floor((e*(lon-c)-b*(lat-f))/det).astype(int)
    row=np.floor((-d*(lon-c)+a*(lat-f))/det).astype(int)
    keys=np.array([f"{int(i)}_{int(j)}" for i,j in zip(
        np.floor((lat+90)/5),np.floor((lon+180)/5))])
    out=np.full(len(frame),np.nan,dtype=float)
    opened={}
    try:
        for key in sorted(set(keys)):
            if key not in grid["tiles"]:continue
            tile=grid["tiles"][key]
            name=tile["file"]
            if name not in opened:opened[name]=np.load(Path(root)/name)
            idx=np.flatnonzero(keys==key)
            ar=opened[name][key]
            iy=row[idx]-int(tile["row_off"]);ix=col[idx]-int(tile["col_off"])
            mask=(iy>=0)&(ix>=0)&(iy<ar.shape[0])&(ix<ar.shape[1])
            vv=ar[iy[mask],ix[mask]].astype(float)
            if grid["nodata"] is not None:vv[vv==float(grid["nodata"])]=np.nan
            out[idx[mask]]=vv
    finally:
        for v in opened.values():v.close()
    out=out*float(grid["scale"])+float(grid["offset"])
    return out,{"source_file":"S1_S2_verified_316tile_cache",
      "source_sha256":SOURCE_SHA["chelsa_rsds_mean"],
      "n_original_occurrence_locations":len(frame),
      "source_complete":int(np.isfinite(out).sum()),
      "cache_tiles_verified":316,
      "same_unresampled_S1_S2_shortwave_radiation":True}

def prepare_occurrences(japan,taiwan,rasters,rsds_cache,rsds_contract):
    jp=pd.read_csv(japan);tw=pd.read_csv(taiwan)
    if len(jp)!=SOURCE_N_JP or len(tw)!=SOURCE_N_TW:
        raise ValueError("Original JP693 TW55 source occurrence census changed")
    required={"scientific_name_query","scientificName","latitude","longitude",*ORIGINAL}
    if not required<=set(jp) or not required<=set(tw):
        raise ValueError("Original accepted source climate and coordinate labels changed")
    occ=pd.concat([jp,tw],ignore_index=True)
    if len(occ)!=748 or not occ[["latitude","longitude"]].notna().all().all():
        raise ValueError("Original authentic coordinate quality absent")
    if not occ.latitude.between(-90,90).all() or not occ.longitude.between(-180,180).all():
        raise ValueError("Original source climate lat/lon outside coordinate range")
    if not occ[[*ORIGINAL]].apply(pd.to_numeric,errors="coerce").notna().all().all():
        raise ValueError("Original EAzami H1 environmental variables changed")
    # Preserve original state- and outcome-blind 693+55 occurrence taxon sources.
    sources={}
    for name in ("chelsa_bio18","chelsa_bio05","elevation_m"):
        path=Path(rasters)/SRC_FILENAMES[name]
        positive_raster(path,SOURCE_SHA[name])
        values,info=sample_raster(path,occ)
        occ[name]=values;sources[name]=info
    occ["chelsa_rsds_mean"],sources["chelsa_rsds_mean"]=sample_original_rsds_cache(
        occ,rsds_cache,rsds_contract)
    missing={k:int(occ[k].isna().sum()) for k in AXES}
    for axis in AXES:
        s=occ[axis]
        if not s.notna().mean()>=.95:
            raise ValueError(f"Original EAzami source incomplete for {axis}: {s.notna().mean():.3f}")
    # Same four exposures on the SAME original occurrence subset.
    complete=occ.dropna(subset=AXES).copy()
    n_by=complete.groupby("scientific_name_query").size().to_dict()
    return occ,complete,{
        "n_original_Japan_occurrences":len(jp),"n_original_Taiwan_occurrences":len(tw),
        "n_original_occurrences":len(occ),
        "n_four_axis_complete_original_occurrences":len(complete),
        "n_complete_by_original_taxon":{str(k):int(v) for k,v in n_by.items()},
        "missing_by_axis":missing,"original_four_climate_source":sources,
        "trait_or_state_values_not_used_to_select_observations":True,
    }

def panel_assets(raw_trees,taxa,env):
    assets=[]
    zenv={field:h.zscore(env[field].to_numpy(float)) for field in AXES}
    for tree in raw_trees:
        tr=h.prune_to_panel(tree,taxa)
        edge_matrix=[]
        for field in AXES:
            values={h.normalize_tip(t):float(z) for t,z in zip(taxa,zenv[field])}
            _,delta=h.brownian_internal_values(tr,values)
            edge_matrix.append(delta)
        assets.append((tr,edge_matrix))
    return assets

def score_map(tree,tip_states,edge_deltas):
    q=h.fit_symmetric_q(tree,tip_states)
    likelihood,joint=h.ctmc_likelihood_and_edge_joint(tree,tip_states,q,need_joint=True)
    if joint is None:raise ValueError("Missing CTMC exact posterior joint on genuine nuclear tree")
    signed={i:float(v[0,1]-v[1,0]) for i,v in joint.items()}
    total=sum(float(v[0,1]+v[1,0]) for v in joint.values())
    if not np.isfinite(total) or total<=EPS:raise ValueError("Zero expected U/D transition mass")
    n=len(AXES)
    values=np.array([sum(signed[i]*d[i] for i in signed)/total for d in edge_deltas])
    if values.shape!=(n,) or not np.isfinite(values).all():raise ValueError("Invalid Brownian branchwise concordance")
    return values,{"fitted_symmetric_ctmc_q":q,
        "exact_CTMC_observed_tip_likelihood":likelihood,
        "posterior_expected_transition_change_mass":float(total),
        "unit":"environment within-panel standardized axes per conditional transition mass"}

def full_null(taxa,observed_states,assets,*,region_map=None):
    norm=[h.normalize_tip(t) for t in taxa]
    n_D=sum(observed_states[t] for t in norm)
    def assignments():
        for combo in itertools.combinations(range(len(taxa)),n_D):
            state={t:(1 if i in combo else 0) for i,t in enumerate(norm)}
            if region_map:
                ok=all(sum(state[norm[i]] for i,t in enumerate(taxa) if t in vals)==cnt
                       for vals,cnt in region_map.values())
                if not ok:continue
            yield state
    matrix=[];rates=[];ids=[];observed=-1
    for k,state in enumerate(assignments()):
        by=[]
        diag=[]
        for tr,delta in assets:
            ans,d=score_map(tr,state,delta)
            by.append(ans);diag.append(d)
        med=np.median(np.vstack(by),axis=0)
        matrix.append(med)
        rates.append(diag)
        ids.append("".join("D" if state[name] else "U" for name in norm))
        if all(state[t]==observed_states[t] for t in norm):
            if observed!=-1:raise ValueError("Original tip states duplicated among exhaustive assignments")
            observed=k
        if (k+1)%300==0:print(f"CTMC_BROWNIAN_U_D_ORIGINAL_MAPS_COMPLETED {k+1}",flush=True)
    if observed<0:raise ValueError("Source historical U/D states not present in null")
    M=np.vstack(matrix)
    y=M[observed]
    norm4=np.linalg.norm(M,axis=1)
    score=float(norm4[observed])
    def rank(a,obs):
        n=int(np.count_nonzero(a>=obs-1e-12))
        return {"n_maps_at_least_as_extreme":n,"n_count_preserving_maps":len(a),
                "exact_finite_state_map_fraction":n/len(a),"not_independent_biological_p_value":True}
    axis_ranks={axis:rank(np.abs(M[:,i]),abs(float(y[i])))
                for i,axis in enumerate(AXES)}
    # Multiple-testing maxT standardized by COMPLETE finite-null SD; preserve
    # between-axis correlations and same U/D count.
    div=M.std(axis=0,ddof=0)
    if np.min(div)<1e-12:raise ValueError("Four axis conditional null has degenerate axis")
    maximum=np.max(np.abs(M/div),axis=1)
    maxT={axis:rank(maximum,abs(float(y[i]/div[i])))
          for i,axis in enumerate(AXES)}
    return {
       "n_taxa":len(taxa),"n_source_U":len(taxa)-n_D,"n_source_D":n_D,
       "taxa_order":taxa,
       "n_six_AU_accepted_nuclear_topologies":len(assets),
       "n_state_maps":len(matrix),
       "observed_original_U_D_map":ids[observed],
       "observed_mean_Brownian_branch_shifts_x_CTMC_posterior":dict(zip(AXES,map(float,y))),
       "observed_source_topology_4axis_effects":[v.tolist() for v in
          [score_map(tr,observed_states,d)[0] for tr,d in assets]],
       "null_4axis_joint_norm":rank(norm4,score),
       "observed_4axis_joint_norm":score,
       "null_axes_abs_exact_two_sided_conditional_ranks":axis_ranks,
       "null_axes_maxT_family_adjusted_conditional_ranks":maxT,
       "directions_not_chosen_to_make_transition_test_significant":True,
       "source_six_original_topologies_fixed_while_UD_tip_assignments_vary":True,
       "ctmc_rate_reestimated_per_state_map_and_topology":True,
       "camera_head_angle_S1_not_used_as_flora_U_D_state":True,
       "not_transition_time_climate_or_adaptive_gain":True,
    }

def run(args):
    contract=json.loads(Path(args.original_contract).read_text())
    coverage=json.loads(Path(args.coverage).read_text())
    legacy=json.loads(Path(args.legacy).read_text())
    if contract["version"]!="chapter2_orientation_transition_regime_hypothesis_contract_v1":
        raise ValueError("Original H1 EAzami method contract changed")
    if coverage["version"]!="chapter2_orientation_occurrence_coverage_audit_result_v1":
        raise ValueError("Original EAzami panel inclusion contract changed")
    original_4,complete,source=prepare_occurrences(args.japan,args.taiwan,args.rasters,args.rsds_cache,args.rsds_metadata)
    cross=pd.read_csv(args.orientation)
    trees=h.read_trees(Path(args.trees),6)
    n10=coverage["threshold_summaries"]["10"]["taxa"]
    states10=h.panel_state_map(cross,n10)
    original_counts,original_env=h.build_panel_environment(original_4,n10)
    original_assets=h.prepare_topology_assets(trees,n10,original_env)
    baseline=h.method_check(contract,legacy,h.observed_topology_stats(original_assets,states10))
    if baseline["status"]!="pass":
        raise ValueError("Original unchanged H1 BIO15/BIO1 CTMC method NOT reproduced")
    summary={}
    for panel_name,(source_key,n,u,d,expected) in PANELS.items():
        taxa=coverage["threshold_summaries"][source_key]["taxa"]
        if len(taxa)!=n:raise ValueError("Original H1 taxon panels drift")
        states=h.panel_state_map(cross,taxa)
        if (len(taxa)-sum(states.values()),sum(states.values()))!=(u,d):
            raise ValueError("Original source literature U/D panel frequencies drift")
        count=complete.groupby("scientific_name_query").size()
        if any(int(count.get(t,0))<int(source_key) for t in taxa):
            raise ValueError(f"New four-climate source is missing original EAzami occurrence support: {panel_name}")
        env=complete.groupby("scientific_name_query")[list(AXES)].mean().loc[taxa]
        assets=panel_assets(trees,taxa,env)
        result=full_null(taxa,states,assets)
        if result["n_state_maps"]!=expected:
            raise ValueError("EAzami count-preserving exhaustive null census changed")
        # Robustness only: maintain observed JP/TW U/D counts, so broad
        # geographic state differences cannot drive the entire result.
        if panel_name=="n5_primary":
            jp=set(coverage["threshold_summaries"]["5"]["taxa"])-{
                "Cirsium japonicum var. australe","Cirsium kawakamii",
                "Cirsium morii","Cirsium tatakaense"}
            tw={"Cirsium japonicum var. australe","Cirsium kawakamii",
                "Cirsium morii","Cirsium tatakaense"}
            region_map={"JP":(jp,3),"TW":(tw,2)}
            regional=full_null(taxa,states,assets,region_map=region_map)
            if regional["n_state_maps"]!=336:
                raise ValueError("Original EAzami Japan3D Taiwan2D conditional null not 336")
            result["region_frequency_preserving_exact_null_336"]={
                "n_maps":336,
                "observed_four_axis_norm":regional["observed_4axis_joint_norm"],
                "rank":regional["null_4axis_joint_norm"],
                "axis_ranks":regional["null_axes_abs_exact_two_sided_conditional_ranks"],
                "axis_maxT":regional["null_axes_maxT_family_adjusted_conditional_ranks"],
            }
        summary[panel_name]=result
    out={
      "schema":"EAzami_ch2_true_original_six_AU_nuclear_CTMC_Brownian_UD_four_user_requested_axes_v1",
      "status":"REAL_ORIGINAL_EAZAMI_BRANCH_TRANSITION_CTMCM_BROWNIAN_4AXIS_RERUN",
      "method_reproduces_frozen_original_BIO15_plus_BIO1_n10":baseline,
      "new_user_requested_four_axes_posthoc_not_original_predeclared_H1":list(AXES),
      "original_EAzami_categorical_U_D_used_as_original_transition_response":True,
      "not_S1_photo_image_angle_response_or_S1_to_T2_PGLS":True,
      "original_AU_six_true_multilocus_nuclear_trees_not_plastid":True,
      "input_sources":{"original_H1_contract":str(args.original_contract.name),
        "published_six_AU_topologies_blob_sha":args.AU_blob_sha,
        "current_CHELSA_RSDS_caches_original_S1_S2_provenance":True,
        "climate_period":"1981-2010_CHELSA_2_1_and_WorldClim_2_1_elevation",
        "JP_occurrence_source":str(args.japan.name),
        "TW_occurrence_source":str(args.taiwan.name),
        "four_axes":source},
      "per_panel_four_environment_transition_regime_results":summary,
      "n_new_independent_U_D_biological_state_assignments":0,
      "one_sided_prediction_cannot_be_selected_posthoc":True,
      "no_claim_historical_transition_time_environment_or_selection":True,
      "no_claim_each_branch_transition_replicate_independent":True,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    for name,stat in summary.items():
        print("EAzami_TRUE_CTMC_BROWNIAN_NEW4="+json.dumps({
            "panel":name,"n":stat["n_taxa"],
            "joint4_exact_rank":stat["null_4axis_joint_norm"],
            "axis_scores":stat["observed_mean_Brownian_branch_shifts_x_CTMC_posterior"],
            "maxT":stat["null_axes_maxT_family_adjusted_conditional_ranks"],
        },sort_keys=True),flush=True)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-contract",type=Path,required=True)
    p.add_argument("--coverage",type=Path,required=True)
    p.add_argument("--legacy",type=Path,required=True)
    p.add_argument("--orientation",type=Path,required=True)
    p.add_argument("--japan",type=Path,required=True)
    p.add_argument("--taiwan",type=Path,required=True)
    p.add_argument("--trees",type=Path,required=True)
    p.add_argument("--rasters",type=Path,required=True)
    p.add_argument("--rsds-cache",type=Path,required=True)
    p.add_argument("--rsds-metadata",type=Path,required=True)
    p.add_argument("--AU-blob-sha",dest="AU_blob_sha",required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.AU_blob_sha!="d7f8c0b96ee9c257c815db06a5a0aa9fdae4841e":
        raise ValueError("Original EAzami 6 selected AU topologies Git blob changed")
    run(args)
if __name__=="__main__":
    main()
