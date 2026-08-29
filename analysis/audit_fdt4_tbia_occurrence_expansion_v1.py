#!/usr/bin/env python3
"""Audit TBIA occurrence API for public Taiwan records beyond frozen GBIF/TBN layers.

The audit reuses the frozen seven-taxon alias contract. Records are admitted only
when a source/original/resolved scientific name matches a predeclared focal name,
coordinates pass the same <=10 km uncertainty and geographic guards, and the
record is not an obvious GBIF or TBN mirror. Existing GBIF/TBN 0.05-degree cells
are excluded before any ecological analysis.
"""
from __future__ import annotations

import argparse, json, math, re
from pathlib import Path
from typing import Any
import pandas as pd
import requests

API_ROOT = "https://tbiadata.tw/api/v1/occurrence"
NAME_FIELDS = ("sourceScientificName", "originalScientificName", "scientificName")
AUDIT_COLUMNS = [
    'query_taxon','matched_name_field','matched_source_name','tbia_id','occurrence_id',
    'scientific_name','source_scientific_name','original_scientific_name','latitude','longitude',
    'coordinate_uncertainty_m','data_generalizations','thin_lat','thin_lon','new_vs_existing_cell',
    'rights_holder','dataset_name','tbia_dataset_id','source_dataset_id','gbif_dataset_id','references',
    'license','basis_of_record','event_date','county','municipality','obvious_gbif_mirror',
    'obvious_tbn_mirror','independent_source','open_license'
]


def args():
    p=argparse.ArgumentParser()
    p.add_argument('--alias-contract',type=Path,required=True)
    p.add_argument('--existing-occurrences',type=Path,nargs='+',required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--timeout',type=float,default=90)
    return p.parse_args()


def text(x:Any)->str:
    return ' '.join(str(x or '').replace('×','x').split())


def canon(x:Any)->str:
    s=text(x).casefold().replace(' variety ',' var. ').replace(' forma ',' f. ')
    s=re.sub(r'\s+',' ',s).strip()
    return s


def name_match(value:Any, allowed:list[str])->bool:
    s=canon(value)
    return any(s==canon(a) or s.startswith(canon(a)+' ') for a in allowed if canon(a))


def as_float(x:Any):
    try: v=float(x)
    except (TypeError,ValueError): return None
    return v if math.isfinite(v) else None


def as_bool(x:Any)->bool:
    if isinstance(x,bool): return x
    return text(x).casefold() in {'true','1','yes','y'}


def cell(lat:float,lon:float,thin:float):
    return math.floor(lat/thin), math.floor(lon/thin)


def rows(payload:dict)->list[dict]:
    for k in ('data','results'):
        if isinstance(payload.get(k),list): return [x for x in payload[k] if isinstance(x,dict)]
    return []


def next_url(payload:dict)->str:
    n=payload.get('next')
    if isinstance(n,str): return n
    links=payload.get('links')
    if isinstance(links,dict) and isinstance(links.get('next'),str): return links['next']
    return ''


def get_all(session:requests.Session,query:str,timeout:float)->list[dict]:
    url=API_ROOT; params={'name':query,'limit':1000}; out=[]; seen=set()
    for _ in range(100):
        r=session.get(url,params=params,timeout=timeout)
        # TBIA currently returns HTTP 404 for a valid query with zero matches.
        # Treat that as an empty page rather than aborting the all-taxon audit.
        if r.status_code==404:
            return out
        r.raise_for_status(); p=r.json()
        if not isinstance(p,dict): raise RuntimeError(f'non-object TBIA payload for {query}')
        out.extend(rows(p)); n=next_url(p)
        if not n or n in seen: break
        seen.add(n); url=n; params=None
    return out


def geo_ok(row:dict,rule:dict,g:dict,lat:float,lon:float)->bool:
    county=text(row.get('county'))
    inside=(float(g['lat_min'])<=lat<=float(g['lat_max']) and float(g['lon_min'])<=lon<=float(g['lon_max']))
    guard=rule.get('geographic_guard',{})
    if rule['analysis_taxon']=='Cirsium japonicum var. albescens':
        allowed={canon(x) for x in guard.get('allowed_counties',[])}
        bb=guard.get('fallback_bbox',{})
        county_ok=canon(county) in allowed if county else False
        bbox_ok=bool(bb) and float(bb['lat_min'])<=lat<=float(bb['lat_max']) and float(bb['lon_min'])<=lon<=float(bb['lon_max'])
        return county_ok or bbox_ok
    extra={canon(x) for x in guard.get('additional_allowed_counties_outside_global_bbox',[])}
    return inside or (county and canon(county) in extra)


def mirror_flags(row:dict)->tuple[bool,bool]:
    holder=canon(row.get('rightsHolder')); refs=canon(row.get('references')); ds=canon(row.get('datasetName'))
    gbif=bool(text(row.get('gbifDatasetID'))) or 'gbif' in holder or 'gbif.org' in refs or 'gbif' in ds
    tbn=('台灣生物多樣性網絡' in holder or re.search(r'(^|\W)tbn($|\W)',holder) is not None or 'tbn.org.tw' in refs or 'plant.tbn.org.tw' in refs)
    return gbif,tbn


def main():
    a=args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    contract=json.loads(a.alias_contract.read_text())
    g=contract['global_filters']; thin=float(g['spatial_thin_degrees']); max_unc=float(g['max_coordinate_uncertainty_m'])
    taxa=[r['analysis_taxon'] for r in contract['rules']]
    existing_cells={t:set() for t in taxa}
    for p in a.existing_occurrences:
        d=pd.read_csv(p)
        for _,r in d.iterrows():
            t=text(r.get('scientific_name_query'))
            if t not in existing_cells: continue
            lat=as_float(r.get('latitude',r.get('decimalLatitude'))); lon=as_float(r.get('longitude',r.get('decimalLongitude')))
            if lat is not None and lon is not None: existing_cells[t].add(cell(lat,lon,thin))

    ses=requests.Session(); ses.headers.update({'User-Agent':'EAzami-TBIA-public-occurrence-audit/1.0'})
    audit=[]; accepted=[]; summary=[]
    for rule in contract['rules']:
        taxon=rule['analysis_taxon']; allowed=list(rule['allowed_occurrence_names'])
        queries=[]
        for q in list(rule.get('lookup_queries',[]))+allowed:
            if q and q not in queries and not (taxon.endswith('fukienense') and canon(q)==canon('Cirsium japonicum')): queries.append(q)
        raw={}
        for q in queries:
            for r in get_all(ses,q,a.timeout):
                key=text(r.get('id') or r.get('occurrenceID') or '') or json.dumps(r,sort_keys=True,ensure_ascii=False)
                raw.setdefault(key,r)
        counts={'raw':len(raw),'name_match':0,'coordinate':0,'strict':0,'independent':0,'new_cell':0,'open_license':0}
        for r in raw.values():
            matched_field=''; matched_name=''
            for f in NAME_FIELDS:
                if name_match(r.get(f),allowed): matched_field=f; matched_name=text(r.get(f)); break
            if not matched_field: continue
            counts['name_match']+=1
            lat=as_float(r.get('standardLatitude',r.get('verbatimLatitude'))); lon=as_float(r.get('standardLongitude',r.get('verbatimLongitude')))
            if lat is None or lon is None or not geo_ok(r,rule,g,lat,lon): continue
            counts['coordinate']+=1
            unc=as_float(r.get('coordinateUncertaintyInMeters'))
            strict=(unc is not None and unc<=max_unc)
            if not strict: continue
            counts['strict']+=1
            gbif,tbn=mirror_flags(r); independent=not gbif and not tbn
            if independent: counts['independent']+=1
            c=cell(lat,lon,thin); new=c not in existing_cells[taxon]
            if independent and new: counts['new_cell']+=1
            lic=text(r.get('license')); open_license=('cc' in canon(lic) or 'creative commons' in canon(lic) or '公共領域' in text(lic))
            if independent and new and open_license: counts['open_license']+=1
            row={
                'query_taxon':taxon,'matched_name_field':matched_field,'matched_source_name':matched_name,
                'tbia_id':text(r.get('id')),'occurrence_id':text(r.get('occurrenceID')),
                'scientific_name':text(r.get('scientificName')),'source_scientific_name':text(r.get('sourceScientificName')),
                'original_scientific_name':text(r.get('originalScientificName')),
                'latitude':lat,'longitude':lon,'coordinate_uncertainty_m':unc,'data_generalizations':as_bool(r.get('dataGeneralizations')),
                'thin_lat':c[0],'thin_lon':c[1],'new_vs_existing_cell':new,
                'rights_holder':text(r.get('rightsHolder')),'dataset_name':text(r.get('datasetName')),
                'tbia_dataset_id':text(r.get('tbiaDatasetID')),'source_dataset_id':text(r.get('sourceDatasetID')),'gbif_dataset_id':text(r.get('gbifDatasetID')),
                'references':text(r.get('references')),'license':lic,'basis_of_record':text(r.get('basisOfRecord')),
                'event_date':text(r.get('eventDate')),'county':text(r.get('county')),'municipality':text(r.get('municipality')),
                'obvious_gbif_mirror':gbif,'obvious_tbn_mirror':tbn,'independent_source':independent,'open_license':open_license,
            }
            audit.append(row)
            if independent and new: accepted.append(row)
        summary.append({'taxon':taxon,**counts,'existing_cells':len(existing_cells[taxon]),'queries':' | '.join(queries)})

    audit_df=pd.DataFrame(audit,columns=AUDIT_COLUMNS); acc=pd.DataFrame(accepted,columns=AUDIT_COLUMNS); sm=pd.DataFrame(summary)
    audit_df.to_csv(a.out_dir/'tbia_occurrence_audit_all_strict.csv',index=False)
    acc.to_csv(a.out_dir/'tbia_independent_new_cells_candidates.csv',index=False)
    sm.to_csv(a.out_dir/'tbia_occurrence_coverage_summary.csv',index=False)
    holders=[]
    if not acc.empty:
        holders=(acc.groupby(['query_taxon','rights_holder','dataset_name']).size().reset_index(name='records').sort_values(['query_taxon','records'],ascending=[True,False]).to_dict('records'))
    payload={'contract_version':'fdt4_tbia_occurrence_expansion_v1','api':API_ROOT,'source_contract':contract['contract_version'],
             'filters':{'max_coordinate_uncertainty_m':max_unc,'spatial_thin_degrees':thin,'gbif_tbn_mirrors_excluded':True,'existing_cells_excluded':True},
             'summary':sm.to_dict('records'),'independent_source_breakdown':holders,
             'claim_boundary':'TBIA is an aggregator. Only source-name-guarded records not identified as GBIF/TBN mirrors and occupying cells absent from the frozen GBIF/TBN layers are candidates for ecological sensitivity; license and source composition remain explicit.'}
    (a.out_dir/'fdt4_tbia_occurrence_expansion_v1.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
    print(sm.to_string(index=False))

if __name__=='__main__': main()
