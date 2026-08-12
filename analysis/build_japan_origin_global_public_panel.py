#!/usr/bin/env python3
"""Build the 302-biological-sample global public panel for Japanese Cirsium origins.

The Moreyra full reconciliation CSV is a recovered workflow artifact rather than
a publisher file committed to this repository.  This builder therefore accepts
that CSV explicitly, combines it with the frozen Chang 2025/2026 run manifests,
and verifies the counts/provenance frozen in
``data/evidence/japan_origin_global_public_panel_contract_v1.json``.

The output is an accession/provenance manifest, not a phylogenetic result.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_CONTRACT=Path('data/evidence/japan_origin_global_public_panel_contract_v1.json')
DEFAULT_CH25=Path('data/evidence/chang2025_public_run_manifest_v1.csv')
DEFAULT_CH26=Path('data/evidence/chang2026_public_run_manifest_v1.csv')
DEFAULT_OUTDIR=Path('results/japan_origin_global_public_panel')

FIELDS=(
    'panel_id','source_study','bioproject','assay','source_taxon_label',
    'analysis_taxon_label','voucher','biosample','run_accessions','run_count',
    'region','location','name_review_required','common_locus_space','claim_boundary'
)

def clean(x:object)->str: return str(x or '').strip()
def norm_chang_taxon(x:str)->str:
    x=clean(x)
    return 'Cirsium '+x[3:] if x.startswith('C. ') else x

def slug(x:str)->str: return re.sub(r'[^A-Za-z0-9]+','_',clean(x)).strip('_') or 'sample'
def joinvals(values:Iterable[str])->str: return '|'.join(sorted({clean(v) for v in values if clean(v)}))

def read_csv(path:Path)->tuple[list[str],list[dict[str,str]]]:
    with path.open(encoding='utf-8-sig',newline='') as h:
        r=csv.DictReader(h); fields=list(r.fieldnames or [])
        rows=[{k:clean(v) for k,v in row.items()} for row in r if any(clean(v) for v in row.values())]
    if not rows: raise ValueError(f'{path}: no rows')
    return fields,rows

def load_contract(path:Path)->dict:
    x=json.loads(path.read_text(encoding='utf-8'))
    if x.get('contract_version')!='japan_origin_global_public_panel_v1':
        raise ValueError('unexpected global-panel contract version')
    return x

def build_moreyra(rows:Sequence[Mapping[str,str]])->tuple[list[dict[str,str]],list[dict[str,str]]]:
    req={'tree_code','biosample','run','experiment','voucher_and_herbarium','region_class','geographic_location','sra_link_status','scope_class','tree_code_vs_sra_name','name_reconciliation_priority'}
    missing=req-set(rows[0])
    if missing: raise ValueError(f'Moreyra reconciliation missing {sorted(missing)}')
    cir=[r for r in rows if r['tree_code'].startswith('Cirsium') and r['sra_link_status']=='linked_runinfo']
    excluded=[r for r in cir if r['scope_class']=='source_conflict_target_vs_outside']
    clean_rows=[r for r in cir if r['scope_class']!='source_conflict_target_vs_outside']
    by:dict[str,list[Mapping[str,str]]]=defaultdict(list)
    for r in clean_rows:
        if not r['biosample']: raise ValueError('linked Moreyra Cirsium row lacks BioSample')
        by[r['biosample']].append(r)
    out=[]
    for bio in sorted(by):
        g=by[bio]
        taxa=sorted({r['tree_code'] for r in g})
        if len(taxa)!=1: raise ValueError(f'Moreyra BioSample {bio} retains multiple source taxon labels: {taxa}')
        rel={r['tree_code_vs_sra_name'] for r in g if r['tree_code_vs_sra_name']}
        high=any(r['name_reconciliation_priority']=='high' for r in g)
        runs=sorted({r['run'] for r in g if r['run']})
        out.append({
            'panel_id':f'MRY_{slug(bio)}','source_study':'Moreyra2025','bioproject':'PRJNA957074',
            'assay':'Compositae1061_target_capture','source_taxon_label':taxa[0],'analysis_taxon_label':taxa[0],
            'voucher':joinvals(r['voucher_and_herbarium'] for r in g),'biosample':bio,
            'run_accessions':'|'.join(runs),'run_count':str(len(runs)),'region':joinvals(r['region_class'] for r in g),
            'location':joinvals(r['geographic_location'] for r in g),
            'name_review_required':str(high or rel!={'exact'}).lower(),'common_locus_space':'Compositae1061_direct',
            'claim_boundary':'Moreyra source labels are preserved; placement is not a newly inferred dispersal result.'
        })
    return out,excluded

def build_chang25(rows:Sequence[Mapping[str,str]])->list[dict[str,str]]:
    req={'taxon','voucher','biosample','experiment','run','library_layout','geographic_location','match_status'}
    missing=req-set(rows[0])
    if missing: raise ValueError(f'Chang2025 manifest missing {sorted(missing)}')
    out=[]
    for r in rows:
        if r['library_layout']!='PAIRED' or r['match_status']!='verified': raise ValueError(f'unverified Chang2025 row {r["voucher"]}')
        loc=r['geographic_location']; tax=r['taxon']
        out.append({'panel_id':f'CH25_{slug(r["voucher"])}','source_study':'Chang2025','bioproject':'PRJNA1158676','assay':'leaf_RNAseq_transcriptome','source_taxon_label':tax,'analysis_taxon_label':tax,'voucher':r['voucher'],'biosample':r['biosample'],'run_accessions':r['run'],'run_count':'1','region':'Japan' if loc.casefold().startswith('japan') else 'Taiwan','location':loc,'name_review_required':'false','common_locus_space':'Compositae1061_homolog_projection_required','claim_boundary':'Public transcriptome run is verified; homolog recovery is still required before joint inference.'})
    return out

def build_chang26(rows:Sequence[Mapping[str,str]])->list[dict[str,str]]:
    req={'taxon','voucher','matched_biosample','matched_run','matched_library_layout','match_confidence','location','matched_scientific_name','match_evidence'}
    missing=req-set(rows[0])
    if missing: raise ValueError(f'Chang2026 manifest missing {sorted(missing)}')
    out=[]
    for r in rows:
        if r['matched_library_layout']!='PAIRED' or r['match_confidence']!='verified': raise ValueError(f'unverified Chang2026 row {r["voucher"]}')
        tax=norm_chang_taxon(r['taxon']); loc=r['location']
        name_review=('exact_taxon' not in r['match_evidence'] and tax!=r['matched_scientific_name'])
        out.append({'panel_id':f'CH26_{slug(r["voucher"])}','source_study':'Chang2026','bioproject':'PRJNA1311153_or_reused_public_run','assay':'leaf_RNAseq_transcriptome','source_taxon_label':r['taxon'],'analysis_taxon_label':tax,'voucher':r['voucher'],'biosample':r['matched_biosample'],'run_accessions':r['matched_run'],'run_count':'1','region':'Japan' if loc.upper().startswith('JAPAN') else 'Taiwan','location':loc,'name_review_required':str(name_review).lower(),'common_locus_space':'Compositae1061_homolog_projection_required','claim_boundary':'Source-paper voucher identity is retained when NCBI taxon labels differ; homolog recovery is still required before joint inference.'})
    return out

def validate(panel:Sequence[Mapping[str,str]],excluded:Sequence[Mapping[str,str]],contract:Mapping)->dict:
    exp=contract['expected_global_inventory']
    source=Counter(r['source_study'] for r in panel)
    nrun=sum(int(r['run_count']) for r in panel)
    labels=len({r['analysis_taxon_label'] for r in panel})
    if len(panel)!=exp['biological_samples']: raise ValueError(f'global biological-sample count {len(panel)} != {exp["biological_samples"]}')
    if nrun!=exp['public_run_accessions']: raise ValueError(f'global run count {nrun} != {exp["public_run_accessions"]}')
    if labels!=exp['source_preserving_analysis_taxon_labels']: raise ValueError(f'global label count {labels} != {exp["source_preserving_analysis_taxon_labels"]}')
    expected_source={'Moreyra2025':exp['Moreyra2025_samples'],'Chang2025':exp['Chang2025_samples'],'Chang2026':exp['Chang2026_samples']}
    if dict(source)!=expected_source: raise ValueError(f'source counts {dict(source)} != {expected_source}')
    if len({r['panel_id'] for r in panel})!=len(panel): raise ValueError('duplicate global panel_id')
    if len(excluded)!=1 or excluded[0]['scope_class']!='source_conflict_target_vs_outside': raise ValueError('expected exactly one preserved Moreyra source-conflict exclusion')
    for tax in ('Cirsium brevicaule','Cirsium irumtiense','Cirsium dipsacolepis','Cirsium lineare'):
        if not any(r['analysis_taxon_label']==tax for r in panel): raise ValueError(f'missing critical taxon {tax}')
    return {'contract_version':'japan_origin_global_public_panel_v1','biological_samples':len(panel),'public_run_accessions':nrun,'unique_source_preserving_analysis_taxon_labels':labels,'source_counts':dict(sorted(source.items())),'region_counts':dict(sorted(Counter(r['region'] for r in panel).items())),'moreyra_excluded_source_conflict_rows':len(excluded),'global_common_locus_tree_executed':False,'new_china_sampling_freeze_allowed':False}

def write_csv(path:Path,rows:Sequence[Mapping[str,str]])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(FIELDS));w.writeheader();w.writerows(rows)

def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--moreyra-reconciliation',type=Path,required=True);p.add_argument('--chang2025',type=Path,default=DEFAULT_CH25);p.add_argument('--chang2026',type=Path,default=DEFAULT_CH26);p.add_argument('--contract',type=Path,default=DEFAULT_CONTRACT);p.add_argument('--outdir',type=Path,default=DEFAULT_OUTDIR);a=p.parse_args()
    contract=load_contract(a.contract);_,mr=read_csv(a.moreyra_reconciliation);_,c25=read_csv(a.chang2025);_,c26=read_csv(a.chang2026)
    mrows,excluded=build_moreyra(mr);panel=mrows+build_chang25(c25)+build_chang26(c26);summary=validate(panel,excluded,contract)
    write_csv(a.outdir/'japan_origin_global_public_panel_v1.csv',panel)
    (a.outdir/'japan_origin_global_public_panel_summary_v1.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (a.outdir/'moreyra_source_conflict_exclusion_v1.json').write_text(json.dumps(excluded,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False));return 0
if __name__=='__main__': raise SystemExit(main())
