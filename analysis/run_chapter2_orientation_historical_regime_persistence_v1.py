#!/usr/bin/env python3
"""Specific H4 test: does the sole calendarized U->D event retain the present-niche sign regime?"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--historical-json',type=Path,required=True)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-csv',type=Path,required=True)
    return p.parse_args()


def main():
    a=parse_args()
    c=json.loads(a.contract.read_text())
    h=json.loads(a.historical_json.read_text())
    if c['version']!='chapter2_orientation_historical_regime_persistence_contract_v1':
        raise AssertionError('contract drift')
    if h['event_id']!=c['event_id']:
        raise AssertionError(('event drift',h['event_id'],c['event_id']))

    rows=pd.DataFrame(h['scenario_rows'])
    sub=rows[rows['variable'].isin(['BIO1','BIO15'])].copy()
    key=['region','young_ma','old_ma']
    piv=sub.pivot(index=key,columns='variable',values='delta').reset_index()
    if len(piv)!=int(c['source_historical_artifact']['expected_region_by_chronology_scenarios']):
        raise AssertionError(('scenario count drift',len(piv)))
    regions=list(c['source_historical_artifact']['expected_regions'])
    if sorted(piv['region'].unique())!=sorted(regions):
        raise AssertionError(('region drift',sorted(piv['region'].unique())))

    piv['h4_match']=(piv['BIO15']>0)&(piv['BIO1']<0)
    piv['exact_opposite']=(piv['BIO15']<0)&(piv['BIO1']>0)
    piv['bio15_expected']=piv['BIO15']>0
    piv['bio1_expected']=piv['BIO1']<0

    per_region={}
    for r in regions:
        d=piv[piv['region']==r]
        if len(d)!=94:
            raise AssertionError(('region chronology count drift',r,len(d)))
        per_region[r]={
            'n':int(len(d)),
            'h4_match_count':int(d['h4_match'].sum()),
            'h4_match_fraction':float(d['h4_match'].mean()),
            'exact_opposite_count':int(d['exact_opposite'].sum()),
            'exact_opposite_fraction':float(d['exact_opposite'].mean()),
            'bio15_positive_fraction':float(d['bio15_expected'].mean()),
            'bio1_negative_fraction':float(d['bio1_expected'].mean()),
        }

    support=all(per_region[r]['h4_match_fraction']>=0.75 for r in regions)
    opposite=all(per_region[r]['exact_opposite_fraction']>=0.75 for r in regions)
    if support:
        classification='historical_regime_persistence_supported'
    elif opposite:
        classification='historical_regime_opposite_direction_dominant'
    else:
        classification='historical_regime_persistence_not_supported'

    chrono=piv.groupby(['young_ma','old_ma'])['h4_match'].sum().reset_index(name='n_regions_matching')
    counts={str(k):int((chrono['n_regions_matching']==k).sum()) for k in range(5)}
    central=piv[(piv['young_ma'].round(2)==0.74)&(piv['old_ma'].round(2)==0.79)].copy()
    central_rows=[]
    for _,r in central.iterrows():
        central_rows.append({
            'region':r['region'],
            'BIO15_delta':float(r['BIO15']),
            'BIO1_delta':float(r['BIO1']),
            'h4_match':bool(r['h4_match']),
            'exact_opposite':bool(r['exact_opposite']),
        })

    out={
        'version':'chapter2_orientation_historical_regime_persistence_result_v1',
        'analysis_role':c['analysis_role'],
        'event_id':c['event_id'],
        'classification':classification,
        'overall':{
            'n_scenarios':int(len(piv)),
            'h4_match_count':int(piv['h4_match'].sum()),
            'h4_match_fraction':float(piv['h4_match'].mean()),
            'exact_opposite_count':int(piv['exact_opposite'].sum()),
            'exact_opposite_fraction':float(piv['exact_opposite'].mean()),
        },
        'per_region':per_region,
        'chronology_region_match_counts':counts,
        'n_chronologies_ge_3_of_4_regions':int((chrono['n_regions_matching']>=3).sum()),
        'n_chronologies_4_of_4_regions':int((chrono['n_regions_matching']==4).sum()),
        'central_0_79_to_0_74_ma':central_rows,
        'claim_boundary':c['claim_boundary'],
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_csv.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2)+'\n')
    piv.to_csv(a.out_csv,index=False)
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
