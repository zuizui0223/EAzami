#!/usr/bin/env python3
"""Occupancy/paralog QC for the 39-sample Japan-38 compatibility reconstruction."""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import defaultdict
from pathlib import Path

SETS={
 'public_1061':'moreyra_public_1061_loci.txt',
 'reproducible_531':'moreyra_reproducible_531_candidate_loci.txt',
 'conservative_241':'moreyra_conservative_241_no_warning_loci.txt',
}
EXPECTED_TIPS=39

def clean(x): return str(x or '').strip()
def read_csv(p,delimiter=','):
    with p.open(encoding='utf-8-sig',newline='') as h:return [{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h,delimiter=delimiter) if any(clean(v) for v in r.values())]
def parse_fasta(p):
    return [line[1:].strip().split()[0] for line in p.read_text(encoding='utf-8').splitlines() if line.startswith('>')]
def resolve_id(seqid,known):
    if seqid in known:return seqid
    hits=[x for x in known if seqid.startswith(x+'-') or seqid.startswith(x+'_') or seqid.startswith(x+'|')]
    if len(hits)==1:return hits[0]
    raise ValueError(f'unresolved focal FASTA id {seqid!r}')
def load_sets(d):
    out={}
    for k,f in SETS.items():
        vals=[x.strip() for x in (d/f).read_text().splitlines() if x.strip()]
        if len(vals)!=len(set(vals)):raise ValueError(f'duplicate loci in {d/f}')
        out[k]=set(vals)
    if len(out['conservative_241'])!=241:raise ValueError('frozen conservative set must contain 241 loci')
    return out
def parse_paralogs(p,known):
    rows=read_csv(p,'\t')
    if not rows or 'Species' not in rows[0]:raise ValueError('paralog report lacks Species')
    genes=[k for k in rows[0] if k!='Species']; out=defaultdict(set); seen=set()
    for r in rows:
        s=r['Species'];
        if s not in known:raise ValueError(f'unknown paralog-report sample {s}')
        seen.add(s)
        for g in genes:
            try:n=int(float(r[g] or 0))
            except ValueError:raise ValueError(f'invalid paralog count {s}/{g}={r[g]!r}')
            if n>1:out[g].add(s)
    if seen!=known:raise ValueError(f'paralog report sample mismatch missing={sorted(known-seen)}')
    return out
def analyse(manifest_path,retrieved_dir,paralog_path,locus_dir,min_occ=.80):
    manifest=read_csv(manifest_path); known={r['tip_id'] for r in manifest}
    if len(manifest)!=EXPECTED_TIPS or len(known)!=EXPECTED_TIPS:raise ValueError(f'expected {EXPECTED_TIPS} unique tips')
    sets=load_sets(locus_dir); paralogs=parse_paralogs(paralog_path,known); present=defaultdict(set)
    for p in sorted(retrieved_dir.glob('*.FNA')):
        samples=[resolve_id(i,known) for i in parse_fasta(p)]
        if len(samples)!=len(set(samples)):raise ValueError(f'duplicate focal sequence at locus {p.stem}')
        present[p.stem]=set(samples)
    threshold=math.ceil(min_occ*EXPECTED_TIPS); qrows=[]; eligible={k:[] for k in sets}
    for locus in sorted(set().union(*sets.values())):
        ps=present.get(locus,set()); para=paralogs.get(locus,set())
        row={'locus':locus,'focal_present':len(ps),'focal_occupancy':len(ps)/EXPECTED_TIPS,'current_paralog_samples':len(para)}
        for k,s in sets.items():
            member=locus in s; ok=member and len(ps)>=threshold and not para
            row[f'in_{k}']='yes' if member else 'no'; row[f'eligible_{k}']='yes' if ok else 'no'
            if ok:eligible[k].append(locus)
        qrows.append(row)
    sample_rows=[]
    for tip in sorted(known):
        row={'tip_id':tip}
        for k,loci in eligible.items():
            n=sum(tip in present.get(l,set()) for l in loci); row[f'{k}_present']=n; row[f'{k}_fraction']=n/len(loci) if loci else 0
        sample_rows.append(row)
    set_summary={}
    for k,loci in eligible.items():
        fractions=[r[f'{k}_fraction'] for r in sample_rows]
        set_summary[k]={'base_count':len(sets[k]),'current_eligible_count':len(loci),'median_sample_fraction':statistics.median(fractions) if fractions else 0,'all_39_samples_represented':all(r[f'{k}_present']>0 for r in sample_rows)}
    strict=set_summary['conservative_241']
    summary={'contract_version':'japan38_comp1061_current_qc_v1','biological_samples':EXPECTED_TIPS,'min_current_locus_occupancy':min_occ,'minimum_present_tips':threshold,'sets':set_summary,'tree_input_ready':strict['current_eligible_count']>=100 and strict['all_39_samples_represented'],'automatic_filter_relaxation_allowed':False,'claim_boundary':'Compatibility-space QC only. It does not reproduce the unpublished Moreyra final-350 matrix or prove any trait transition.'}
    return qrows,sample_rows,eligible,summary
def write_csv(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--retrieved-dir',type=Path,required=True);p.add_argument('--paralog-report',type=Path,required=True);p.add_argument('--locus-dir',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);p.add_argument('--min-occupancy',type=float,default=.80);a=p.parse_args()
    q,s,e,x=analyse(a.manifest,a.retrieved_dir,a.paralog_report,a.locus_dir,a.min_occupancy);a.outdir.mkdir(parents=True,exist_ok=True);write_csv(a.outdir/'locus_qc.csv',q);write_csv(a.outdir/'sample_qc.csv',s)
    for k,loci in e.items():(a.outdir/f'current_{k}_loci.txt').write_text(''.join(z+'\n' for z in sorted(loci)),encoding='utf-8')
    (a.outdir/'current_qc_summary.json').write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,indent=2))
    if not x['tree_input_ready']:raise SystemExit('Japan38 conservative-241 tree input not ready')
if __name__=='__main__':main()
