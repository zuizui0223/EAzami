#!/usr/bin/env python3
"""Build CHELSA-ready TBIA sensitivity tiers from the source-audited candidates."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
import build_focal_occurrence_niche_sample_information_v1 as niche


def args():
    p=argparse.ArgumentParser(); p.add_argument('--niche-config',type=Path,required=True); p.add_argument('--audit',type=Path,required=True); p.add_argument('--out-dir',type=Path,required=True); return p.parse_args()

def b(s):
    if s.dtype==bool:return s
    return s.astype(str).str.casefold().isin({'true','1','yes'})

def choose(d:pd.DataFrame)->pd.DataFrame:
    if d.empty:return d.copy()
    x=d.copy(); x['coordinate_uncertainty_m']=pd.to_numeric(x['coordinate_uncertainty_m'],errors='coerce')
    x=x.sort_values(['query_taxon','thin_lat','thin_lon','open_license','coordinate_uncertainty_m','tbia_id'],ascending=[True,True,True,False,True,True],na_position='last')
    return x.drop_duplicates(['query_taxon','thin_lat','thin_lon'],keep='first').copy()

def envframe(d,predictors,tier):
    if d.empty:return pd.DataFrame(columns=['scientific_name_query','latitude','longitude','environment_complete']+[f'chelsa_{k}' for k in predictors])
    x=pd.DataFrame({'scientific_name_query':d.query_taxon.astype(str),'latitude':pd.to_numeric(d.latitude,errors='coerce'),'longitude':pd.to_numeric(d.longitude,errors='coerce'),
        'coordinate_uncertainty_m':pd.to_numeric(d.coordinate_uncertainty_m,errors='coerce'),'thin_lat':d.thin_lat,'thin_lon':d.thin_lon,
        'tbia_id':d.tbia_id.astype(str),'tbia_occurrence_id':d.occurrence_id.astype(str),'tbia_rights_holder':d.rights_holder.astype(str),'tbia_dataset_name':d.dataset_name.astype(str),
        'tbia_license':d.license.astype(str),'tbia_data_generalizations':d.data_generalizations,'occurrence_source':f'TBIA_v1_{tier}'})
    x,_=niche.sample_chelsa(x,predictors); cols=[f'chelsa_{k}' for k in predictors]; x['environment_complete']=x[cols].notna().all(axis=1)
    return x[x.environment_complete].reset_index(drop=True)
def main():
    a=args(); a.out_dir.mkdir(parents=True,exist_ok=True); cfg=json.loads(a.niche_config.read_text()); predictors=cfg['chelsa']['predictors']; d=pd.read_csv(a.audit)
    if len(d):
        d=d[b(d.independent_source)&b(d.new_vs_existing_cell)].copy()
    payload={'contract_version':'fdt4_tbia_sensitivity_v1','status':'supporting_cross_source_sensitivity_not_primary_replacement','tiers':{}}
    for tier in ('open_reusable','all_independent_public'):
        q=d.copy()
        if tier=='open_reusable' and len(q):q=q[b(q.open_license)].copy()
        selected=choose(q); env=envframe(selected,predictors,tier)
        selected.to_csv(a.out_dir/f'tbia_{tier}_selected_cells.csv',index=False); env.to_csv(a.out_dir/f'tbia_{tier}_additions_environment_complete.csv',index=False)
        cov=[]
        for t in [x['scientific_name'] for x in cfg['taxa']]:
            cov.append({'taxon':t,'added_cells':int((env.scientific_name_query==t).sum()) if len(env) else 0})
        payload['tiers'][tier]={'selected_cells':len(selected),'environment_complete_additions':len(env),'coverage':cov,'rights_holders':sorted(selected.rights_holder.dropna().astype(str).unique().tolist()) if len(selected) else []}
    payload['claim_boundary']='Open-reusable and all-independent-public tiers are kept separate. Neither replaces the frozen GBIF/TBN result without inspecting source composition, taxonomic guards, topology saturation and LOO stability.'
    (a.out_dir/'fdt4_tbia_sensitivity_manifest_v1.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(payload,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
