#!/usr/bin/env python3
"""Full-chronology model-based global sea-level sensitivity for the orientation event.

Uses the NOAA de Boer et al. 5.3-Myr reconstruction because it covers all 94
admissible chronology pairs. The primary null is same-duration windows within the
Pleistocene (0-2580 ka); the full 5.3-Myr record is a secondary sensitivity.

This is a global eustatic context test. It does not reconstruct local island
connectivity, and it cannot identify selection on capitulum orientation.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

METRICS=("mean_m","sd_m","range_m","endpoint_abs_change_m","mean_abs_1k_change_m","max_abs_1k_change_m")
PLEISTOCENE_MAX_KA=2580.0


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--orientation-contract',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    return p.parse_args()


def enumerate_age_pairs(contract:dict[str,Any])->list[tuple[float,float]]:
    c=contract['chronology_scenarios']; parent=c['parent_node']; child=c['child_node']
    pg=np.linspace(parent['lower_ma'],parent['upper_ma'],16)
    cg=np.linspace(child['lower_ma'],child['upper_ma'],10)
    pairs=set()
    for old in pg:
        for young in cg:
            if old>young and (old-young)>=0.010:
                pairs.add((round(float(young),6),round(float(old),6)))
    central=(round(float(child['central_ma']),6),round(float(parent['central_ma']),6))
    if central[1]>central[0]: pairs.add(central)
    return sorted(pairs,key=lambda x:(x[1]-x[0],x[0],x[1]))


def load_source(path:Path)->pd.DataFrame:
    lines=path.read_text(encoding='utf-8-sig',errors='replace').splitlines()
    header_i=None
    for i,line in enumerate(lines):
        if line.startswith('age_calkaBP\t') and i+1<len(lines):
            try:
                float(lines[i+1].split('\t')[0])
                header_i=i; break
            except Exception:
                pass
    if header_i is None:
        raise ValueError('numeric age_calkaBP data header not found')
    df=pd.read_csv(io.StringIO('\n'.join(lines[header_i:])),sep='\t')
    for c in ('age_calkaBP','sealev'):
        if c not in df.columns: raise ValueError(f'missing required column {c}')
        df[c]=pd.to_numeric(df[c],errors='coerce')
    df=df.dropna(subset=['age_calkaBP','sealev']).sort_values('age_calkaBP').drop_duplicates('age_calkaBP')
    return df.reset_index(drop=True)


def one_kyr_series(df:pd.DataFrame)->tuple[np.ndarray,np.ndarray]:
    lo=float(df.age_calkaBP.min()); hi=float(df.age_calkaBP.max())
    ages=np.arange(np.ceil(lo),np.floor(hi)+1e-9,1.0)
    vals=np.interp(ages,df.age_calkaBP.to_numpy(float),df.sealev.to_numpy(float))
    return ages,vals


def metrics(ages:np.ndarray,vals:np.ndarray,young:float,old:float)->dict[str,float]:
    duration=float(old-young)
    grid=np.arange(young,old+1e-9,1.0)
    if len(grid)<2: grid=np.array([young,old],float)
    y=np.interp(grid,ages,vals)
    d=np.diff(y)
    return {
      'mean_m':float(np.mean(y)),
      'sd_m':float(np.std(y,ddof=1)),
      'range_m':float(np.max(y)-np.min(y)),
      'endpoint_abs_change_m':float(abs(y[-1]-y[0])),
      'mean_abs_1k_change_m':float(np.mean(np.abs(d))),
      'max_abs_1k_change_m':float(np.max(np.abs(d))),
    }


def pct(x:np.ndarray,v:float)->float:
    return float((np.sum(x<=v)+0.5)/(len(x)+1.0))


def qsum(x:list[float])->dict[str,float]:
    a=np.asarray(x,float)
    return {'min':float(a.min()),'q05':float(np.quantile(a,.05)),'median':float(np.median(a)),'q95':float(np.quantile(a,.95)),'max':float(a.max())}


def null_metrics(ages:np.ndarray,vals:np.ndarray,duration:float,max_age:float)->dict[str,np.ndarray]:
    starts=np.arange(float(ages.min()),np.floor(max_age-duration)+1e-9,1.0)
    if len(starts)<100: raise ValueError(f'too few matched windows duration={duration} max_age={max_age}')
    rows=[metrics(ages,vals,float(s),float(s+duration)) for s in starts]
    return {m:np.asarray([r[m] for r in rows],float) for m in METRICS}


def classify(summary:dict[str,dict[str,float]])->dict[str,str]:
    out={}
    for m,q in summary.items():
        if q['q05']>=.95: out[m]='robust_high_across_chronology'
        elif q['q95']<=.05: out[m]='robust_low_across_chronology'
        else: out[m]='unresolved_across_chronology'
    return out


def main()->int:
    args=parse_args()
    contract=json.loads(args.orientation_contract.read_text(encoding='utf-8'))
    pairs=enumerate_age_pairs(contract)
    if len(pairs)!=94: raise AssertionError(f'expected 94 pairs, got {len(pairs)}')
    df=load_source(args.source); ages,vals=one_kyr_series(df)
    if ages.max()<1180 or ages.min()>0: raise AssertionError(f'insufficient source coverage {ages.min()}-{ages.max()} ka')

    caches={"pleistocene":{},"full_record":{}}
    rows=[]
    for young_ma,old_ma in pairs:
        young=young_ma*1000.; old=old_ma*1000.; dur=old-young
        key=round(dur,6)
        if key not in caches['pleistocene']:
            caches['pleistocene'][key]=null_metrics(ages,vals,dur,min(PLEISTOCENE_MAX_KA,float(ages.max())))
            caches['full_record'][key]=null_metrics(ages,vals,dur,float(ages.max()))
        ev=metrics(ages,vals,young,old)
        rec={'young_ma':young_ma,'old_ma':old_ma,'duration_ka':dur,**ev}
        for bg in ('pleistocene','full_record'):
            for m in METRICS:
                rec[f'{bg}_{m}_percentile']=pct(caches[bg][key][m],ev[m])
        rows.append(rec)

    summaries={}
    classes={}
    for bg in ('pleistocene','full_record'):
        summaries[bg]={m:qsum([r[f'{bg}_{m}_percentile'] for r in rows]) for m in METRICS}
        classes[bg]=classify(summaries[bg])
    central=min(rows,key=lambda r:abs(r['young_ma']-.74)+abs(r['old_ma']-.79))
    primary_robust=[m for m,c in classes['pleistocene'].items() if c!='unresolved_across_chronology']
    result={
      'contract_version':'chapter2_orientation_deboer_sealevel_envelope_v1',
      'status_date':'2026-09-02',
      'event_id':'ORI_CORE_NIPPONO_STEM',
      'source':{
        'dataset':'NOAA/WDS Global 5 Million Year Sea Level, Temperature, and d18Osw Reconstructions',
        'dataset_doi':'10.25921/xs31-nt56',
        'associated_publication_doi':'10.1038/ncomms3999',
        'columns':{'age':'age_calkaBP','sea_level':'sealev'},
        'source_resolution':'100 yr; analysis interpolated to 1 kyr',
        'source_type':'model-based global reconstruction'
      },
      'chronology_coverage':{'n_total_pairs':94,'n_covered_pairs':94,'coverage_fraction':1.0},
      'primary_background':{'name':'Pleistocene same-duration windows','range_ka':[0,PLEISTOCENE_MAX_KA]},
      'secondary_background':{'name':'full-record same-duration windows','range_ka':[float(ages.min()),float(ages.max())]},
      'metric_percentile_summary':summaries,
      'metric_classification':classes,
      'primary_robust_metrics':primary_robust,
      'central_0_79_to_0_74_ma':central,
      'scenario_rows':rows,
      'decision':'no_global_sea_level_metric_survives_full_chronology_gate' if not primary_robust else 'global_sea_level_metric_survives_full_chronology_gate',
      'repeated_trigger_status':'not_evaluable_single_dated_transition_event',
      'claim_boundary':[
        'The de Boer series is model-based and is an independent sensitivity, not a replacement for the Spratt-Lisiecki stack.',
        'Global eustatic sea level does not reconstruct local island connectivity or fragmentation.',
        'A robust global sea-level association would be a range-reorganization context candidate, not a selective pressure on capitulum orientation.',
        'One dated orientation transition cannot establish a repeated differentiation trigger.'
      ]
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'coverage':result['chronology_coverage'],'primary_summary':summaries['pleistocene'],'primary_class':classes['pleistocene'],'central':central,'decision':result['decision']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
