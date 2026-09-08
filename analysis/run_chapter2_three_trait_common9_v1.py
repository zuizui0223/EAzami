#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'analysis' / 'run_chapter2_three_trait_ecology_panel_v1.py'
spec = importlib.util.spec_from_file_location('three_trait_base', BASE)
core = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(core)


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=Path,required=True)
    p.add_argument('--extension',type=Path,required=True)
    p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-taxa',type=Path,required=True)
    p.add_argument('--out-rows',type=Path,required=True)
    return p.parse_args()


def bh_adjust(values):
    p=np.asarray(values,float); order=np.argsort(p); ranked=p[order]; n=len(p)
    adj=ranked*n/np.arange(1,n+1); adj=np.minimum.accumulate(adj[::-1])[::-1]; adj=np.minimum(adj,1.0)
    out=np.empty(n,float); out[order]=adj
    return out.tolist()


def main():
    a=parse_args(); c=json.loads(a.contract.read_text(encoding='utf-8'))
    seed=pd.read_csv(a.seed,dtype=str).fillna(''); ext=pd.read_csv(a.extension,dtype=str).fillna('')
    df=pd.concat([seed,ext],ignore_index=True).drop_duplicates('paper_japan_member_id',keep='last')
    reg=[]
    for r in df.to_dict('records'):
        out={'paper_japan_member_id':r['paper_japan_member_id'],'taxon_name':r['nmns_taxon_concept']}; any1=False
        for t in core.UNIVERSE:
            st=core.states(r,t); out[t+'_singleton_state']=next(iter(st)) if len(st)==1 else ''; out[t+'_allowed_states']='|'.join(sorted(st)); any1 |= len(st)==1
        if any1: reg.append(out)

    session=requests.Session(); session.headers.update({'User-Agent':'EAzami three-trait common9 panel'})
    envs=list(c['environment']['variables']); urls=c['environment']['urls']
    occ_parts=[]; n_by_taxon={}
    for i,r in enumerate(reg):
        q=r['taxon_name']; thin=core.clean(core.fetch_occ(session,q),q); n_by_taxon[q]=int(len(thin))
        if len(thin):
            thin=thin[['latitude','longitude']].copy(); thin['taxon_name']=q; occ_parts.append(thin)
        print(i+1,len(reg),q,len(thin),flush=True); time.sleep(.01)

    all_occ=pd.concat(occ_parts,ignore_index=True) if occ_parts else pd.DataFrame(columns=['latitude','longitude','taxon_name'])
    if not all_occ.empty:
        for e in envs:
            print('sampling',e,len(all_occ),flush=True)
            all_occ[e]=core.sample(all_occ,urls[e])

    rows=[]
    for r in reg:
        q=r['taxon_name']; out=dict(r); out['n_thinned']=n_by_taxon.get(q,0)
        g=all_occ.loc[all_occ.taxon_name==q] if not all_occ.empty else all_occ
        if len(g):
            out.update({e:float(np.nanmedian(g[e])) for e in envs}); out['centroid_lat']=float(np.nanmedian(g.latitude)); out['centroid_lon']=float(np.nanmedian(g.longitude))
        else:
            out.update({e:np.nan for e in envs}); out['centroid_lat']=np.nan; out['centroid_lon']=np.nan
        rows.append(out)
    taxa=pd.DataFrame(rows)

    result={'version':'chapter2_three_trait_common9_result_v1','status_date':'2026-09-08','environment_variables':envs,'primary':{},'sensitivity':{},'claim_boundary':c['claim_ceiling']}
    for t in core.UNIVERSE: result['primary'][t]=core.analyze(taxa,t,3,envs)
    result['sensitivity']['phyllary_min1']=core.analyze(taxa,'phyllary',1,envs)

    flat=[]
    for trait,res in result['primary'].items():
        if res.get('status')!='evaluated': continue
        for env,z in res.get('univariate',{}).items():
            frac=z['two_sided_rank_count']/z['n_maps']
            flat.append({'trait':trait,'environment':env,'contrast':z['contrast'],'standardized_difference':z['observed'],'rank_count':z['two_sided_rank_count'],'n_maps':z['n_maps'],'exact_fraction':frac})
    if flat:
        qvals=bh_adjust([r['exact_fraction'] for r in flat])
        for r,v in zip(flat,qvals): r['bh_q_across_evaluable_trait_environment_rows']=float(v)
    result['univariate_rows']=flat
    result['multiplicity']={'family':'all evaluable primary trait x common9 univariate rows','n_rows':len(flat),'method':'Benjamini-Hochberg'}
    result['cross_trait_conclusion']='All three historical traits were passed through the same nine-variable present-environment pipeline. Ecological evidence is compared by identical data/QC rules, while trait-specific resolution limits remain explicit.'
    result['classification']={t:result['primary'][t]['status'] for t in core.UNIVERSE}

    a.out_json.parent.mkdir(parents=True,exist_ok=True); a.out_taxa.parent.mkdir(parents=True,exist_ok=True); a.out_rows.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); taxa.to_csv(a.out_taxa,index=False); pd.DataFrame(flat).to_csv(a.out_rows,index=False)
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
