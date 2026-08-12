#!/usr/bin/env python3
"""Resolve all 33 Chang 2026 transcriptome rows in the Japan-origin panel.

The authoritative join is the frozen output of the independent complete NCBI
reconciliation workflow.  Voucher identity is the key; no geography, flower
colour, or preferred topology is used to assign a run.
"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path

DEFAULT_PANEL=Path('data/evidence/generated/japan_origin_max_public_panel/japan_origin_max_public_panel_v1.csv')
DEFAULT_RUNS=Path('data/evidence/chang2026_public_run_manifest_v1.csv')
DEFAULT_OUTPUT=Path('data/evidence/generated/japan_origin_max_public_panel/japan_origin_max_public_panel_v1_run_resolved.csv')
REQ_PANEL={'source_study','analysis_taxon_label','voucher','biosample','public_identifiers','run_accessions','run_resolution_state'}
REQ_RUN={'taxon','voucher','matched_run','matched_experiment','matched_biosample','matched_library_layout','match_confidence','match_status','source_workflow_run','source_artifact_id','source_artifact_sha256'}

def clean(x): return str(x or '').strip()
def norm_taxon(x):
    x=clean(x)
    return 'Cirsium '+x[3:] if x.startswith('C. ') else x

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as h:
        r=csv.DictReader(h); fields=list(r.fieldnames or [])
        rows=[{k:clean(v) for k,v in row.items()} for row in r if any(clean(v) for v in row.values())]
    return fields,rows

def joinvals(vals): return '|'.join(sorted({clean(v) for v in vals if clean(v)}))

def validate_run_manifest(rows):
    if len(rows)!=33: raise ValueError(f'expected 33 Chang2026 rows, found {len(rows)}')
    missing=REQ_RUN-set(rows[0])
    if missing: raise ValueError(f'run manifest missing {sorted(missing)}')
    vouchers=[r['voucher'] for r in rows]; runs=[r['matched_run'] for r in rows]; bios=[r['matched_biosample'] for r in rows]
    if len(set(vouchers))!=33 or len(set(runs))!=33 or len(set(bios))!=33:
        raise ValueError('Chang2026 voucher/run/BioSample must be one-to-one')
    if any(r['matched_library_layout']!='PAIRED' or r['match_confidence']!='verified' for r in rows):
        raise ValueError('all Chang2026 rows must be verified paired-end')
    if len({r['source_artifact_sha256'] for r in rows})!=1: raise ValueError('mixed artifact provenance')
    return {r['voucher']:r for r in rows}

def augment(panel,runs):
    by=validate_run_manifest(runs); seen=set(); out=[]
    for src in panel:
        row=dict(src)
        if row.get('source_study')=='Chang2026':
            v=row.get('voucher','')
            if v not in by: raise ValueError(f'Chang2026 panel voucher missing from frozen run manifest: {v}')
            rr=by[v]
            if row.get('analysis_taxon_label')!=norm_taxon(rr['taxon']): raise ValueError(f'taxon mismatch for {v}')
            row['biosample']=rr['matched_biosample']
            row['run_accessions']=rr['matched_run']
            row['public_identifiers']=joinvals([row.get('public_identifiers'),rr['matched_run'],rr['matched_experiment'],rr['matched_biosample']])
            row['run_resolution_state']='resolved_public_runs'
            seen.add(v)
        out.append(row)
    if seen!=set(by): raise ValueError(f'not all frozen Chang2026 rows joined; unmatched={sorted(set(by)-seen)}')
    return out

def summary(rows):
    ch=[r for r in rows if r['source_study']=='Chang2026']; ry=[r for r in ch if r['analysis_taxon_label'] in {'Cirsium brevicaule','Cirsium irumtiense'}]
    if len(ch)!=33 or len(ry)!=6: raise ValueError('unexpected Chang2026/Arenicola row counts')
    if any(r['run_resolution_state']!='resolved_public_runs' for r in ch): raise ValueError('not all Chang2026 rows resolved')
    states=Counter(r['run_resolution_state'] for r in rows)
    return {'contract_version':'japan_origin_chang2026_run_augmentation_v1','panel_rows':len(rows),'chang2026_rows':33,'chang2026_unique_runs':len({r['run_accessions'] for r in ch}),'chang2026_unique_biosamples':len({r['biosample'] for r in ch}),'arenicola_rows':6,'arenicola_unique_runs':len({r['run_accessions'] for r in ry}),'run_resolution_state_counts':dict(sorted(states.items())),'all_chang2026_verified_run_resolved':True,'joint_common_locus_tree_executed':False,'new_china_sampling_freeze_allowed':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--panel',type=Path,default=DEFAULT_PANEL);p.add_argument('--runs',type=Path,default=DEFAULT_RUNS);p.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);a=p.parse_args()
    fields,panel=read(a.panel); missing=REQ_PANEL-set(fields)
    if missing: raise SystemExit(f'panel missing {sorted(missing)}')
    _,runs=read(a.runs); out=augment(panel,runs); s=summary(out)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(out)
    a.output.with_name('japan_origin_max_public_panel_v1_run_resolved_summary.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(s,indent=2,ensure_ascii=False));return 0
if __name__=='__main__': raise SystemExit(main())
