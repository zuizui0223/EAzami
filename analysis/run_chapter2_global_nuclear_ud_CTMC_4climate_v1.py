#!/usr/bin/env python3
"""Global EAzami original CTMC/Brownian U->D evolution across genuine NUCLEAR trees.

Independent region A: Siniscalchi et al. (2023) full authored North-American
63-tip multilocus nuclear phylogeny with independently published U/D states
(5 D, 58 U). Because 7 original terminals refer to infra-specific name
concepts, no binomial proxy climate value is assigned to those seven tips.
Native-ish North America original georeferenced GBIF source observations are
strictly matched to each remaining unique BINOMIAL taxon. The SAME authentic
CHELSA v2.1 BIO18, BIO05, RSDS and WorldClim v2.1 elevation pixel sources as
EAzami Japan+Taiwan 12-tip (six accepted AU multilocus nuclear trees) are used.

The original *method* is reused verbatim: symmetric 2-state CTMC q fitted
for each sampled tip-state map, exact posterior edge J(U,D)-J(D,U), Brownian
squared-change ancestral niche branch deltas, 4-axis 2-sided Euclidean norm
and axis-wise |shift|/maxT. Original EAzami 12-tip 792-map exact analysis is
read from its pinned archived result. In North America choose(n, n_D) may
have millions of maps, so a fixed-seed uniformly count-preserving Monte Carlo
null is used, including the observed source mapping in the tally.

This is NOT one (fake) stitched global phylogeny. The two evidence lanes are
distinct source studies; worldwide phylogenetic species-level inference awaits
the Moreyra 2025 350 nuclear-locus AUTHOR TREE with genuine global tip coverage.
No S1 photographic continuous image angle is relabeled as botanical U/D.

Source rank and missing environmental exposure safeguards are fail-closed.
All individual GBIF coordinates and IDs remain transient local data inside
a GitHub runner. Public outputs contain only counts, ecological summaries
and each authentic author's published scientific names and U/D labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import random
import time
from pathlib import Path
from urllib.request import urlopen
import numpy as np
import pandas as pd
import requests
from Bio import Phylo

from analysis import run_chapter2_orientation_transition_regime_hypothesis_v1 as h
from analysis import run_chapter2_orientation_transition_regime_fourclimate_v1 as env

NA_SOURCE_REPO="carol-siniscalchi/cirsium"
NA_SOURCE_COMMIT="c925d4af86160064448f794a9715f70b917a2786"
NA_TREE="traits/cirsium.phyluce95p.ultrametric.tre"
NA_STATES="traits/traits.csv"
NA_TREE_BLOB="6417a38793427bc7c8562dc0e2cab59b74d8c316"
NA_STATES_BLOB="fa127f0587b676e6e004ea121424d26069586bcb"
NA_AUTHOR_TIPS=63
NA_AUTHOR_D=5
SOURCE_EXACT_SPECIES=56
GBIF="https://api.gbif.org/v1"
COUNTRIES=frozenset({"US","CA","MX"})
AXES=env.AXES
SOURCE_MAX=300
MIN_SOURCE_OCC=5
MIN_SOURCE_CELL=2
SEED=20261024
MONTE_CARLO=1999
SOURCE_TIP_NOISE_NOT_PARAMETERIZED=True

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def original_na_sources(tree_path=None,state_path=None):
    def read(path,expected):
        if path is not None:
            raw=Path(path).read_bytes()
        else:
            url=f"https://raw.githubusercontent.com/{NA_SOURCE_REPO}/{NA_SOURCE_COMMIT}/{NA_TREE if expected==NA_TREE_BLOB else NA_STATES}"
            with urlopen(url,timeout=90) as s:raw=s.read()
        if git_blob(raw)!=expected:raise ValueError("Published NA nuclear tree or true U/D states source SHA drift")
        return raw
    tree=Phylo.read(io.StringIO(read(tree_path,NA_TREE_BLOB).decode("utf-8-sig")),"newick")
    rows=list(csv.DictReader(io.StringIO(read(state_path,NA_STATES_BLOB).decode("utf-8-sig"))))
    tips={x.name for x in tree.get_terminals()}
    named={r["Species"]:r for r in rows}
    if len(tips)!=NA_AUTHOR_TIPS or len(rows)!=63 or set(named)!=tips:
        raise ValueError("Author NA63 nuclear phylogeny and phenotype tip identities disagree")
    states={k:int(r["HeadPosition"]) for k,r in named.items()}
    if set(states.values())!={0,1} or sum(states.values())!=NA_AUTHOR_D:
        raise ValueError("Source author complete NA63 state census does not match 58U 5D")
    source=[]
    for tip in sorted(tips):
        tokens=tip.split("_")
        full=" ".join(tokens)
        species_rank=len(tokens)==2 and tokens[0]=="Cirsium"
        source.append({"author_original_nuclear_tip":tip,
            "author_original_botanical_U_D":"D" if states[tip] else "U",
            "author_exact_binomial_species_concept":species_rank,
            "GBIF_exact_species_query":full if species_rank else None,
            "infraspecific_name_not_collapsed":not species_rank})
    if len([x for x in source if x["author_exact_binomial_species_concept"]])!=SOURCE_EXACT_SPECIES:
        raise ValueError("Original seven author infraspecific tips changed")
    return tree,source,states

def gbif_get(session,path,params,attempts=3):
    problem="unavailable"
    for n in range(attempts):
        try:
            r=session.get(GBIF+path,params=params,timeout=(8,34))
            if r.status_code==429 or r.status_code>=500:
                problem="HTTP_"+str(r.status_code);time.sleep(1+2*n);continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException,ValueError) as exc:
            problem=type(exc).__name__;time.sleep(1+n)
    raise RuntimeError("GBIF_AUTHOR_TAXON_SOURCE_UNREACHABLE "+problem+" at "+path)

def exact_taxon_match(source,response):
    expected=source["GBIF_exact_species_query"]
    if not expected:return None
    original=" ".join(str(response.get("scientificName","")).split()[:2])
    if not (response.get("matchType")=="EXACT"
       and response.get("rank")=="SPECIES"
       and int(response.get("confidence",0))>=90
       and original==expected):
        return None
    return int(response.get("usageKey",0) or 0) or None

def occurrence_row(row,source_name,taxon_key):
    try:
        la=float(row.get("decimalLatitude"))
        lo=float(row.get("decimalLongitude"))
    except (TypeError,ValueError):return None
    if not (np.isfinite(la) and np.isfinite(lo) and abs(la)<=90 and abs(lo)<=180):return None
    if str(row.get("countryCode","")).upper() not in COUNTRIES:
        return None
    if str(row.get("species","")).split()[:2] != source_name.split():
        return None
    # GBIF speciesKey can be taxonomic backbone representation; insist that
    # reported accepted species string actually agrees with original author.
    if row.get("speciesKey") not in (None,taxon_key):
        return None
    return {"source_name":source_name,"_latitude":la,"_longitude":lo,
            "_gbif_key":str(row["key"]),
            "_continent":"North America",
            "_source":"GBIF geolocated HUMAN_OBSERVATION"}

def get_na_source_sites(authors,session):
    ledger=[]
    observations=[]
    for taxon in authors:
        tip=taxon["author_original_nuclear_tip"]
        species=taxon["GBIF_exact_species_query"]
        if not species:
            ledger.append({**taxon,"gbif_status":"INFRASPECIFIC_SKIP_NO_ALIAS",
                           "n_original_GBIF_country_filtered":0})
            continue
        match=gbif_get(session,"/species/match",{"name":species,"rank":"SPECIES","strict":"true"})
        key=exact_taxon_match(taxon,match)
        if not key:
            ledger.append({**taxon,"gbif_status":"NO_STRICT_GBIF_SPECIES_MATCH",
                           "n_original_GBIF_country_filtered":0,
                           "GBIF_match_type":match.get("matchType")})
            continue
        records=gbif_get(session,"/occurrence/search",{
            "taxonKey":key,
            "hasCoordinate":"true",
            "basisOfRecord":"HUMAN_OBSERVATION",
            "limit":SOURCE_MAX,"offset":0})
        seen=set()
        selected=[]
        for rec in records.get("results",[]):
            item=occurrence_row(rec,species,key)
            if item and item["_gbif_key"] not in seen:
                seen.add(item["_gbif_key"])
                selected.append(item)
        observations.extend(selected)
        ledger.append({**taxon,
          "gbif_status":"STRICT_AUTHOR_SPECIES_GBIF_SOURCE_QUERY",
          "strict_species_taxon_key":key,
          "n_original_GBIF_country_filtered":len(selected),
          "GBIF_first300_returned":len(records.get("results",[])),
          "GBIF_total_potential_records":int(records.get("count",0)),
          "truncated_first_300_NOT_full_source_census":int(records.get("count",0))>SOURCE_MAX,
          "n_original_2023_author_U_D_evidence":1,
        })
        time.sleep(.05)
    if len(ledger)!=NA_AUTHOR_TIPS:
        raise ValueError("NA63 source lost an authored tip")
    if len(set(x["_gbif_key"] for x in observations))!=len(observations):
        raise ValueError("Same GBIF occurrence reused across authored taxon concepts")
    return pd.DataFrame(observations),ledger

def new_climate_for_source(frame,rasters,rsds_cache,rsds_metadata):
    if len(frame)<100:
        raise ValueError("Not enough genuine GBIF observation coordinates for NA climatic phylogeny")
    site=frame.rename(columns={"_latitude":"latitude","_longitude":"longitude"}).copy()
    evid={}
    for name in ("chelsa_bio18","chelsa_bio05","elevation_m"):
        filename=env.SRC_FILENAMES[name]
        source=Path(rasters)/filename
        env.positive_raster(source,env.SOURCE_SHA[name])
        vals,metadata=env.sample_raster(source,site)
        site[name]=vals
        evid[name]=metadata
    site["chelsa_rsds_mean"],evid["chelsa_rsds_mean"]=env.sample_original_rsds_cache(
        site,rsds_cache,rsds_metadata)
    site["_grid_cell5"]=(np.floor((site.latitude+90)/5).astype(int)*72+
                         np.floor((site.longitude+180)/5).astype(int))
    return site,evid

def make_eligible(tips,rows,tree,*,min_occ=MIN_SOURCE_OCC,min_cell=MIN_SOURCE_CELL):
    complete=rows.dropna(subset=list(AXES))
    group=complete.groupby("source_name")
    source={}
    states={}
    for tip in tips:
        species=tip["GBIF_exact_species_query"]
        if not species:
            continue
        if species not in group.groups:continue
        s=group.get_group(species)
        if len(s)<min_occ or s["_grid_cell5"].nunique()<min_cell:continue
        source[tip["author_original_nuclear_tip"]] = {
            "taxon_name":species,"n_original_geo_records":len(s),
            "n_unique_5degree_cells":int(s["_grid_cell5"].nunique()),
            **{a:float(s[a].mean()) for a in AXES},
        }
        states[tip["author_original_nuclear_tip"]]=int(tip["author_original_botanical_U_D"]=="D")
    n_D=sum(states.values())
    if len(states)<30 or n_D<2 or len(states)-n_D<15:
        return None,{"status":"BLOCKED_AUTHENTIC_NUCLEAR_UD_OR_GBIF_FOUR_SOURCE_TOO_SHALLOW",
                     "n_original_scorable_species":len(states),
                     "n_original_nodding_authored_D":n_D,
                     "n_authored_upright_U":len(states)-n_D,
                     "min_original_sites":min_occ,
                     "min_cells":min_cell,
                     "n_all_original_authored":63,
                     "not_recast_unknown_or_dropped_D_as_U":True,
                     "source_kept":["source_tip","n_source_coordinates","n_original_spatial_cells","BIO18","BIO5","RSDS","elevation"],
                     "tip_ledger":sorted(source)}
    tr=Phylo.read(io.StringIO(Phylo.write(tree,io.StringIO(),"newick")),"newick") if False else tree
    pruned=h.prune_to_panel(tr,sorted(states))
    assets=[]
    for axis in AXES:
        tipvals={k:float(v[axis]) for k,v in source.items()}
        z=h.zscore(np.array([tipvals[t] for t in sorted(states)],float))
        shifted={k:float(v) for k,v in zip(sorted(states),z)}
        _,d=h.brownian_internal_values(pruned,shifted)
        assets.append(d)
    from math import comb
    report={"status":"ELIGIBLE_GENUINE_NA_NUCLEAR_U_D_CTMC_BROWNIAN",
            "n_original_scorable_species":len(states),
            "n_original_nodding_authored_D":n_D,
            "n_authored_upright_U":len(states)-n_D,
            "all_state_assignments_not_exhaustively_enumerated":comb(len(states),n_D),
            "n_exact_species_matched_author_phylogeny":len(source),
            "mean_n_gbif_source_records_per_tip":float(np.mean([v["n_original_geo_records"] for v in source.values()])),
            "min_original_sites":min_occ,"min_cells":min_cell,
            "no_infraspecific_tip_invented":True,
            "root_is_NA_author_original_multilocus_ultrametric_tree":True,
            "tip_summary":[{"nuclear_author_tip":k,"source_species":v["taxon_name"],
                 "author_botanical_U_D":"D" if states[k] else "U",
                 "n_source_GBIF_records":v["n_original_geo_records"],
                 "n_5degree_cells":v["n_unique_5degree_cells"],
                 **{a:v[a] for a in AXES}} for k,v in sorted(source.items())]}
    return (pruned,assets,states),report

def monte_carlo_null(tree,deltas,states,*,draws,seed):
    if draws<999:raise ValueError("At least 999 sampled count-conditioned NA U/D maps required")
    keys=sorted(states)
    nd=sum(states.values())
    obs,hdiag=env.score_map(tree,states,deltas)
    if not np.isfinite(obs).all() or len(obs)!=4:raise ValueError("Observed transition vector invalid")
    gen=np.random.default_rng(seed)
    null=[]
    for i in range(draws):
        D=set(int(x) for x in gen.choice(len(keys),size=nd,replace=False))
        alternative={k:int(j in D) for j,k in enumerate(keys)}
        v,diagnostics=env.score_map(tree,alternative,deltas)
        null.append(v)
        if (i+1)%250==0:print("NA_GLOBAL_REAL_NUCLEAR_CTMC_MAPS="+str(i+1),flush=True)
    M=np.vstack([obs,*null])
    scores=np.linalg.norm(M,axis=1)
    null_sd=M.std(axis=0,ddof=0)
    if (null_sd<1e-12).any():raise ValueError("Four-source null no climate variation")
    maxt=np.max(abs(M/null_sd),axis=1)
    def fraction(values,v):
        count=int(np.count_nonzero(values>=v-1e-12))
        return {"at_least_original":count,"total":len(values),
             "finite_conditioned_fraction":count/len(values),
             "sampled_conditional_Monte_Carlo_NOT_exact_enumeration":True}
    return {
        "method":"same_EAzami_symmetric_CTMC_ML_q_per_state_map_exact_edge_posterior_Brownian_environment_NA_genuine_nuclear",
        "n_nuclear_taxa":len(keys),"original_n_U":len(keys)-nd,"original_n_D":nd,
        "n_fixed_seed_uniform_count_preserving_random_state_maps":draws,
        "n_total_including_original_map":len(M),
        "original_branch_transition_environment_shift":dict(zip(AXES,obs.tolist())),
        "original_map_q_ML":hdiag["fitted_symmetric_ctmc_q"],
        "original_total_edge_transition_posterior_mass":hdiag["posterior_expected_transition_change_mass"],
        "four_axis_direction_unsigned_norm":fraction(scores,scores[0]),
        "per_axis_absolute_two_sided_fractions":{
             axis:fraction(abs(M[:,j]),abs(obs[j])) for j,axis in enumerate(AXES)},
        "maxT_4axis_family_adjusted_fractions":{
            axis:fraction(maxt,abs(obs[j]/null_sd[j])) for j,axis in enumerate(AXES)},
        "random_seed":seed,
        "montecarlo_resolution_finite":1/(draws+1),
        "cannot_claim_independent_evolutionary_events_or_global_species_tree":True}

def aggregate_eastasia_and_na(na_result,old_h1,source_counts):
    # The EAzami Japanese/Taiwan node posteriors are sourced from the prior
    # verified completely enumerated 792 original count-preserving maps.
    if old_h1["schema"]!="EAzami_ch2_true_original_six_AU_nuclear_CTMC_Brownian_UD_four_user_requested_axes_v1":
        raise ValueError("Cannot mix EAzami earlier original gene trees with other models")
    ea=old_h1["per_panel_four_environment_transition_regime_results"]["n5_primary"]
    if ea["n_state_maps"]!=792 or ea["n_taxa"]!=12 or ea["n_source_D"]!=5:
        raise ValueError("Original East Asian CTMC 12tip exact 792 conditional source changed")
    return {
     "schema":"EAzami_GLOBAL_AUTHENTIC_NUCLEAR_STUDY_REGION_STRATIFIED_CTMC_BROWNIAN_UD_20261024_v1",
     "status":"NA63_REAL_AUTHOR_U_D_AND_EASTASIA_REAL_ORIGINAL_CTMC_SHARED_FOUR_CLIMATES",
     "geographic_scope":"North America native US-CA-MX botanical-source matched observations plus Japan/Taiwan original EAzami",
     "cannot_claim_all_global_Cirsium_species_tested":True,
     "original_published_NA_full_author_nuclear_phylogeny":63,
     "original_published_NA_botanical_D_count":5,
     "original_EA_6_nuclear_topology_sensitivity":True,
     "NA_per_author_original_nuclear_species_tree":na_result,
     "EA_Japan_Taiwan_same_original_U_D_CTMC":{
         "n_original_U":ea["n_source_U"],"n_original_D":ea["n_source_D"],
         "n_tip_species":12,"n_six_authentic_nuclear_trees":6,
         "observed_signed_branch_shifts":ea["observed_mean_Brownian_branch_shifts_x_CTMC_posterior"],
         "exact_4axis_joint_rank":ea["null_4axis_joint_norm"],
         "exact_4axis_axiswise_two_sided":ea["null_axes_abs_exact_two_sided_conditional_ranks"],
         "exact_4axis_maxT":ea["null_axes_maxT_family_adjusted_conditional_ranks"],
         "source_original_method_reproduced":old_h1["method_reproduces_frozen_original_BIO15_plus_BIO1_n10"]["status"]=="pass",
         "n_original_JP_TW_source_occurrences":748},
     "same_environment_layers":list(AXES),
     "has_verified_true_one_global_63plus12_nuclear_species_tree":False,
     "region_specific_BIO18_U_D_transitions_can_have_opposite_signs":True,
     "cannot_pool_species_as_independent_ancestral_gains":True,
     "no_dated_climate_at_transition":True,
     "no_plastid_or_grafted_phylogeny":True,
     "no_S1_EXIF_image_angle_as_true_gravity_U_D":True,
     "study_region_na_GBIF_source_metadata":source_counts,
     "next_global_true_nuclear_target":"Moreyra et al. 2025 350 genuine nuclear loci 248 Cirsium species, original author deposited final Newick + exact photographed species concept",
     "no_new_unresolved_infraspecific_names_proxy_to_species":True}

def execute(args):
    source_tree,author,states=original_na_sources(args.NA_tree,args.NA_states)
    with requests.Session() as s:
        s.headers.update({"User-Agent":"EAzami-original-CTMC-global-NA63-GBIF-fourclimate/1.0"})
        site,ledger=get_na_source_sites(author,s)
    root=Path(args.out);root.mkdir(parents=True,exist_ok=True)
    if site.empty:
        raise ValueError("No GBIF geolocated authentic North American species for authored tree")
    screened,rasters=new_climate_for_source(site,args.rasters,args.rsds_cache,args.rsds_metadata)
    evidence={"n_original_published_NA_taxa":len(author),
         "n_exact_strict_binomial_author_taxa":sum(t["author_exact_binomial_species_concept"] for t in author),
         "n_strict_matched_species_with_some_NA_occurrences":sum(v["n_original_GBIF_country_filtered"]>0 for v in ledger),
         "n_georeferenced_NA_source_observations":len(site),
         "n_complete_four_environment_NA_source_observations":int(screened[list(AXES)].notna().all(axis=1).sum()),
         "n_author_U":58,"n_author_D":5,
         "n_infraspecific_author_tips_not_collapsed":7,
         "original_climate_sources_sha256":{k:env.SOURCE_SHA[k] for k in AXES},
         "climate_source_measurement":rasters,
         "strict_species_source_selection_BLIND_to_head_U_D_and_climate":True,
         "not_full_NA_species_native_range_coverage":True,
         "GBIF_site_sample_ceiling_each_300_not_full_species_distribution":True}
    # All author original labels are reported even if no exact climate.
    available={record["source_name"]:record for record in screened.to_dict("records")}
    ledger_out=[]
    valid=screened.dropna(subset=list(AXES)).copy()
    for person in ledger:
        candidate=person.copy()
        nm=person["GBIF_exact_species_query"]
        sub=valid[valid.source_name.eq(nm)] if nm else valid.iloc[0:0]
        candidate["n_complete_4_original_GBIF_climate_sites"]=len(sub)
        candidate["n_source_5degree_cells_4axis_complete"]=int(
            ((np.floor((sub.latitude+90)/5)*72)+np.floor((sub.longitude+180)/5)).nunique()) if len(sub) else 0
        candidate["no_imputed_climate_or_taxonomic_alias"]=True
        ledger_out.append(candidate)
    (root/"NA63_PUBLISHED_AUTHOR_U_D_SPECIES_AND_SOURCE_COVERAGE.json").write_text(
        json.dumps({"status":"ORIGINAL_AUTHOR_NUCLEAR_SOURCE_QC","census":evidence,
          "all63_publication_taxa":ledger_out},ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    summary={}
    for min_obs,min_cell,label in ((3,1,"n3_secondary"),(5,2,"n5_primary"),(10,3,"n10_strict")):
        assembly,scope=make_eligible(author,screened,source_tree,min_occ=min_obs,min_cell=min_cell)
        if assembly is None:
            summary[label]=scope
            continue
        tr,delta,tipstates=assembly
        n_draws=args.draws if label=="n5_primary" else max(999,min(args.draws,999))
        null=monte_carlo_null(tr,delta,tipstates,draws=n_draws,seed=SEED+min_obs)
        summary[label]={**scope,"branch_regime_CTMC_Brownian_conditioned_null":null}
    if "n5_primary" not in summary or summary["n5_primary"]["status"].startswith("BLOCKED"):
        result={"schema":"EAzami_NA63_TRUE_NUCLEAR_AUTHOR_UD_FOUR_ENVIRONMENTS_INITIAL_GBIF_SOURCE_GATE_v1",
                "status":"NO_JUSTIFIABLE_FULL_NUCLEAR_CTMC_AT_SOURCE_DEPTH_5",
                "NA_authored_tree_63_and_U_D_original":evidence,
                "original_full_authored_63_taxon_SOURCE_ledger":ledger_out,
                "NA_species_niche_scoped":summary,
                "no_positive_evolutionary_climate_claim":True}
    else:
        ea=json.loads(Path(args.EA_result).read_text())
        result=aggregate_eastasia_and_na(summary,ea,evidence)
        result["source_NA_entire_exact_match_coverage"]=ledger_out
    (root/"GLOBAL_AUTHORIGINAL_TRUE_NUCLEAR_CTMC_UD_BIO18_BIO5_RSDS_ELEVATION.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print("GLOBAL_EAZAMI_AUTHOR_CTMC_NA_EA_REAL="+json.dumps({
       "status":result["status"],
       "NA63_original_nuclear_tips":63,"NA63_D5":5,
       "GBIF_new_geo_records":evidence["n_georeferenced_NA_source_observations"],
       "n_exact_species_photo_independent":evidence["n_strict_matched_species_with_some_NA_occurrences"],
       "n_four_environment_complete_sites":evidence["n_complete_four_environment_NA_source_observations"],
       "sampled_n5":summary.get("n5_primary",{}).get("n_original_scorable_species"),
       "n5_D":summary.get("n5_primary",{}).get("n_original_nodding_authored_D"),
       "n5_conditional_four_axis":summary.get("n5_primary",{}).get("branch_regime_CTMC_Brownian_conditioned_null",{}).get("four_axis_direction_unsigned_norm"),
       "not_one_worldwide_nuclear_species_tree":True},sort_keys=True),flush=True)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--NA-tree",type=Path)
    p.add_argument("--NA-states",type=Path)
    p.add_argument("--rasters",type=Path,required=True)
    p.add_argument("--rsds-cache",type=Path,required=True)
    p.add_argument("--rsds-metadata",type=Path,required=True)
    p.add_argument("--EA-result",type=Path,required=True)
    p.add_argument("--draws",type=int,default=MONTE_CARLO)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    execute(args)
if __name__=="__main__":
    main()
