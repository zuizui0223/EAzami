#!/usr/bin/env python3
"""Build the Japan-38 biological-sample subset from the deduplicated 294-tip panel.

This does not use Japan-38 membership as a topology constraint. It only freezes the
sample/run provenance needed for an independent 241-locus compatibility reconstruction.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
from pathlib import Path

EXPECTED_CONCEPTS=38
EXPECTED_SAMPLES=39
EXPECTED_RUNS=40
CONFLICT_MEMBER='JPN_31'


def clean(x): return str(x or '').strip()
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as h:
        return [{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h) if any(clean(v) for v in r.values())]
def slug(x): return re.sub(r'[^A-Za-z0-9]+','_',clean(x)).strip('_')

def build(global_panel:Path,j38_audit:Path,outdir:Path):
    panel=read_csv(global_panel); audit=read_csv(j38_audit)
    by_member={r['paper_japan_member_id']:r for r in audit}
    if len(by_member)!=EXPECTED_CONCEPTS: raise ValueError(f'expected {EXPECTED_CONCEPTS} unique Japan38 concepts')
    rows=[r for r in panel if r.get('japan38_member_ids')]
    if len(rows)!=EXPECTED_SAMPLES: raise ValueError(f'expected {EXPECTED_SAMPLES} Japan38 biological samples, found {len(rows)}')
    member_ids={m for r in rows for m in r['japan38_member_ids'].split('|') if m}
    if member_ids!=set(by_member): raise ValueError(f'Japan38 membership mismatch missing={sorted(set(by_member)-member_ids)} extra={sorted(member_ids-set(by_member))}')
    all_runs=[x for r in rows for x in r['run_accessions'].split('|') if x]
    if len(all_runs)!=EXPECTED_RUNS or len(set(all_runs))!=EXPECTED_RUNS: raise ValueError(f'expected {EXPECTED_RUNS} unique SRRs')
    rows=sorted(rows,key=lambda r:(r['japan38_member_ids'],r['biosample']))
    manifest=[]; by_concept=defaultdict(list)
    for i,r in enumerate(rows,1):
        mids=[x for x in r['japan38_member_ids'].split('|') if x]
        if len(mids)!=1: raise ValueError(f"sample {r['biosample']} maps to !=1 Japan38 concept: {mids}")
        mid=mids[0]; a=by_member[mid]; tip=f'J38S{i:03d}'
        out={
            'index':str(i-1),'tip_id':tip,'panel_id':r['panel_id'],'source_study':r['source_studies'],
            'assay':r['assay'],'analysis_taxon_label':r['analysis_taxon_label'],'paper_japan_member_id':mid,
            'paper_taxon_concept':a['paper_taxon_concept'],'voucher':r['voucher'],'biosample':r['biosample'],
            'run_accessions':r['run_accessions'],'run_count':r['run_count'],'sample_origin_class':a['sample_origin_class'],
            'membership_confidence':a['paper_japan_membership_confidence'],
            'trait_asr_primary_allowed':'false' if mid==CONFLICT_MEMBER else 'true',
            'claim_boundary':'Nuclear placement is reconstructed independently in the frozen 241-locus compatibility space; taxon-concept morphology is not same-voucher phenotyping.'
        }
        manifest.append(out); by_concept[mid].append(tip)
    outdir.mkdir(parents=True,exist_ok=True)
    fields=list(manifest[0])
    for fn,delim in [('sample_manifest.csv',','),('sample_manifest.tsv','\t')]:
        with (outdir/fn).open('w',encoding='utf-8',newline='') as h:
            w=csv.DictWriter(h,fieldnames=fields,delimiter=delim,lineterminator='\n');w.writeheader();w.writerows(manifest)
    concepts=[]
    for mid in sorted(by_member):
        tips=sorted(by_concept[mid]); a=by_member[mid]
        concepts.append({'paper_japan_member_id':mid,'paper_taxon_concept':a['paper_taxon_concept'],'tip_ids':'|'.join(tips),'n_biological_samples':len(tips),'trait_asr_primary_allowed':'false' if mid==CONFLICT_MEMBER else 'true','replicate_monophyly_required':'true' if len(tips)>1 else 'false'})
    with (outdir/'concept_map.csv').open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(concepts[0]));w.writeheader();w.writerows(concepts)
    replicated=[r for r in concepts if r['n_biological_samples']>1]
    if len(replicated)!=1 or replicated[0]['paper_japan_member_id']!='JPN_20' or replicated[0]['n_biological_samples']!=2:
        raise ValueError(f'unexpected replicated Japan38 concepts: {replicated}')
    summary={
        'contract_version':'japan38_comp1061_subset_panel_v1','paper_taxon_concepts':EXPECTED_CONCEPTS,
        'biological_samples':EXPECTED_SAMPLES,'public_run_accessions':EXPECTED_RUNS,
        'replicated_concept':'JPN_20','replicated_concept_samples':2,'identity_conflict_concept':CONFLICT_MEMBER,
        'trait_asr_primary_concepts':EXPECTED_CONCEPTS-1,'frozen_locus_universe':'moreyra_conservative_241_no_warning',
        'tree_role':'independent compatibility reconstruction; not the unpublished Moreyra final-350 tree',
        'claim_boundary':'Japan38 membership determines sample inclusion only, never topology. JPN_31 remains in the tree but is excluded from primary trait ASR until voucher/sample identity is resolved.'
    }
    (outdir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False)); return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--global-panel',type=Path,required=True);p.add_argument('--japan38-audit',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();build(a.global_panel,a.japan38_audit,a.outdir)
if __name__=='__main__': main()
