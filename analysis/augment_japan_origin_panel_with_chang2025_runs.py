#!/usr/bin/env python3
"""Join all 13 verified Chang 2025 public RNA-seq runs into the Japan-origin panel."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path

DEFAULT_PANEL=Path('data/evidence/generated/japan_origin_max_public_panel/japan_origin_max_public_panel_v1_run_resolved.csv')
DEFAULT_RUNS=Path('data/evidence/chang2025_public_run_manifest_v1.csv')
DEFAULT_OUTPUT=Path('data/evidence/generated/japan_origin_max_public_panel/japan_origin_max_public_panel_v1_all_runs_resolved.csv')
REQ_PANEL={'source_study','analysis_taxon_label','voucher','biosample','public_identifiers','run_accessions','run_resolution_state'}
REQ_RUN={'taxon','voucher','biosample','experiment','run','library_layout','match_status','source_workflow_run','source_artifact_id','source_artifact_sha256'}

def clean(x): return str(x or '').strip()
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as h:
        r=csv.DictReader(h); fields=list(r.fieldnames or [])
        rows=[{k:clean(v) for k,v in row.items()} for row in r if any(clean(v) for v in row.values())]
    return fields,rows

def joinvals(vals): return '|'.join(sorted({clean(v) for v in vals if clean(v)}))

def validate_runs(rows):
    if len(rows)!=13: raise ValueError(f'expected 13 Chang2025 rows, found {len(rows)}')
    missing=REQ_RUN-set(rows[0])
    if missing: raise ValueError(f'run manifest missing {sorted(missing)}')
    if len({r['voucher'] for r in rows})!=13 or len({r['run'] for r in rows})!=13 or len({r['biosample'] for r in rows})!=13:
        raise ValueError('Chang2025 voucher/run/BioSample must be one-to-one')
    if any(r['library_layout']!='PAIRED' or r['match_status']!='verified' for r in rows):
        raise ValueError('all Chang2025 rows must be verified paired-end')
    if len({r['source_artifact_sha256'] for r in rows})!=1: raise ValueError('mixed artifact provenance')
    return {r['voucher']:r for r in rows}

def augment(panel,runs):
    by=validate_runs(runs); seen=set(); out=[]
    for src in panel:
        row=dict(src)
        if row.get('source_study')=='Chang2025':
            v=row.get('voucher','')
            if v not in by: raise ValueError(f'Chang2025 panel voucher missing from frozen run manifest: {v}')
            rr=by[v]
            if row.get('analysis_taxon_label')!=rr['taxon']: raise ValueError(f'taxon mismatch for {v}')
            row['biosample']=rr['biosample']
            row['run_accessions']=rr['run']
            row['public_identifiers']=joinvals([row.get('public_identifiers'),rr['run'],rr['experiment'],rr['biosample']])
            row['run_resolution_state']='resolved_public_runs'
            seen.add(v)
        out.append(row)
    if seen!=set(by): raise ValueError(f'not all frozen Chang2025 rows joined: {sorted(set(by)-seen)}')
    return out

def summarize(rows):
    c25=[r for r in rows if r['source_study']=='Chang2025']
    c26=[r for r in rows if r['source_study']=='Chang2026']
    mry=[r for r in rows if r['source_study']=='Moreyra2025']
    if len(c25)!=13 or len(c26)!=33 or len(mry)!=50: raise ValueError(f'unexpected source counts: Moreyra={len(mry)} Chang2025={len(c25)} Chang2026={len(c26)}')
    unresolved=[r for r in rows if r['run_resolution_state']!='resolved_public_runs']
    if unresolved: raise ValueError(f'focused public panel still has {len(unresolved)} unresolved rows')
    states=Counter(r['run_resolution_state'] for r in rows)
    return {'contract_version':'japan_origin_all_public_runs_resolved_v1','panel_rows':len(rows),'source_counts':{'Moreyra2025':50,'Chang2025':13,'Chang2026':33},'resolved_public_rows':len(rows),'unresolved_public_rows':0,'chang2025_unique_runs':len({r['run_accessions'] for r in c25}),'chang2025_unique_biosamples':len({r['biosample'] for r in c25}),'run_resolution_state_counts':dict(sorted(states.items())),'joint_common_locus_tree_executed':False,'new_china_sampling_freeze_allowed':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--panel',type=Path,default=DEFAULT_PANEL);p.add_argument('--runs',type=Path,default=DEFAULT_RUNS);p.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);a=p.parse_args()
    fields,panel=read(a.panel); missing=REQ_PANEL-set(fields)
    if missing: raise SystemExit(f'panel missing {sorted(missing)}')
    _,runs=read(a.runs); out=augment(panel,runs); s=summarize(out)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(out)
    a.output.with_name('japan_origin_max_public_panel_v1_all_runs_resolved_summary.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(s,indent=2,ensure_ascii=False));return 0
if __name__=='__main__': raise SystemExit(main())
