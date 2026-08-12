#!/usr/bin/env python3
"""Summarize current common-locus QC for the global Japanese-origin panel.

Primary tree admission is deliberately strict and non-adaptive:

- start from the frozen Moreyra conservative 241-locus universe;
- require current occupancy >= 0.80 across all admitted biological samples;
- require zero current HybPiper paralog warnings at the locus;
- require >=100 primary loci to launch the global placement tree.

The broader 531/1061 universes are reported as diagnostics/sensitivities only.
They are not allowed to rescue a failed primary gate automatically.  If the
strict primary gate fails, execution stops and a new, explicitly versioned
paralog/missing-data model must be justified before any relaxation.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path

SETS={
    'public_1061':'moreyra_public_1061_loci.txt',
    'reproducible_531':'moreyra_reproducible_531_candidate_loci.txt',
    'conservative_241':'moreyra_conservative_241_no_warning_loci.txt',
}
PRIMARY='conservative_241'
PRIMARY_OCC=0.80
PRIMARY_MIN_LOCI=100

def clean(x): return str(x or '').strip()
def read_csv(path,delimiter=','):
    with path.open(encoding='utf-8-sig',newline='') as h:
        return [{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h,delimiter=delimiter) if any(clean(v) for v in r.values())]
def fasta_ids(path):
    ids=[]
    with path.open(encoding='utf-8') as h:
        for line in h:
            if line.startswith('>'): ids.append(line[1:].strip().split()[0])
    return ids
def resolve_id(seqid,known):
    if seqid in known:return seqid
    hits=[x for x in known if seqid.startswith(x+'-') or seqid.startswith(x+'_') or seqid.startswith(x+'|')]
    if len(hits)==1:return hits[0]
    raise ValueError(f'unresolved recovered sequence id {seqid!r}')
def load_sets(root):
    out={}
    for name,fn in SETS.items():
        vals=[x.strip() for x in (root/fn).read_text().splitlines() if x.strip()]
        if not vals or len(vals)!=len(set(vals)):raise ValueError(f'invalid locus set {fn}')
        out[name]=set(vals)
    if len(out['conservative_241'])!=241 or len(out['reproducible_531'])!=531 or len(out['public_1061'])!=1061:
        raise ValueError('frozen locus-set count drift')
    return out
def parse_paralogs(path,known):
    rows=read_csv(path,delimiter='\t')
    if not rows or 'Species' not in rows[0]:raise ValueError('paralog report lacks Species')
    genes=[k for k in rows[0] if k!='Species']; warned=defaultdict(set);seen=set()
    for r in rows:
        s=r['Species']
        if s not in known:raise ValueError(f'unknown paralog-report sample {s}')
        seen.add(s)
        for g in genes:
            try:n=int(float(r[g] or 0))
            except ValueError:raise ValueError(f'invalid paralog count {s}/{g}={r[g]!r}')
            if n>1:warned[g].add(s)
    if seen!=known:raise ValueError(f'paralog report sample mismatch missing={len(known-seen)} extra={len(seen-known)}')
    return warned
def analyse(manifest,retrieved,paralog,locus_dir,min_occ=PRIMARY_OCC):
    rows=read_csv(manifest)
    known={r['tip_id'] for r in rows}
    if not rows or len(known)!=len(rows):raise ValueError('sample manifest must contain unique tip_id values')
    if len(rows)!=302:raise ValueError(f'expected 302 global tips, found {len(rows)}')
    assays={r['tip_id']:r['assay'] for r in rows}
    studies={r['tip_id']:r['source_study'] for r in rows}
    sets=load_sets(locus_dir);warned=parse_paralogs(paralog,known)
    present=defaultdict(set)
    for path in sorted(retrieved.glob('*.FNA')):
        samples=[resolve_id(x,known) for x in fasta_ids(path)]
        if len(samples)!=len(set(samples)):raise ValueError(f'duplicate sequence for a sample at {path.stem}')
        present[path.stem]=set(samples)
    threshold=math.ceil(min_occ*len(known))
    qrows=[];eligible={k:[] for k in sets}
    for locus in sorted(set().union(*sets.values())):
        ps=present.get(locus,set());pw=warned.get(locus,set())
        row={'locus':locus,'present':len(ps),'occupancy':len(ps)/len(known),'paralog_warning_samples':len(pw)}
        for name,base in sets.items():
            member=locus in base;ok=member and len(ps)>=threshold and not pw
            row[f'in_{name}']='yes' if member else 'no';row[f'eligible_{name}']='yes' if ok else 'no'
            if ok:eligible[name].append(locus)
        qrows.append(row)
    sample_rows=[]
    for tip in sorted(known):
        r={'tip_id':tip,'source_study':studies[tip],'assay':assays[tip]}
        for name,loci in eligible.items():
            n=sum(tip in present.get(l,set()) for l in loci);r[f'{name}_present']=n;r[f'{name}_fraction']=n/len(loci) if loci else 0
        sample_rows.append(r)
    def med(vals):return statistics.median(vals) if vals else 0
    set_summary={}
    for name,loci in eligible.items():
        by_study={}
        for study in sorted(set(studies.values())):
            vals=[r[f'{name}_fraction'] for r in sample_rows if r['source_study']==study]
            by_study[study]={'n':len(vals),'median_sample_fraction':med(vals)}
        set_summary[name]={'base_count':len(sets[name]),'current_strict_eligible_count':len(loci),'by_study':by_study}
    primary_n=len(eligible[PRIMARY]);launch=primary_n>=PRIMARY_MIN_LOCI
    summary={
        'contract_version':'japan_origin_global_comp1061_current_qc_v1',
        'global_tips':len(rows),'minimum_current_occupancy_fraction':min_occ,'minimum_present_tips':threshold,
        'current_paralog_rule':'zero HybPiper >1-copy warnings across all 302 admitted samples',
        'primary_locus_universe':PRIMARY,'primary_base_count':241,'primary_minimum_loci_to_launch':PRIMARY_MIN_LOCI,
        'sets':set_summary,'primary_current_eligible_loci':primary_n,'global_tree_launch_allowed':launch,
        'automatic_filter_relaxation_allowed':False,'global_common_locus_tree_completed':False,
        'claim_limit':'If fewer than 100 conservative-241 loci pass current 302-sample occupancy and zero-paralog QC, stop. Broader 531/1061 results are diagnostic and cannot automatically replace the failed primary matrix.'
    }
    return qrows,sample_rows,eligible,summary
def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:return
    with path.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--retrieved-dir',type=Path,required=True);p.add_argument('--paralog-report',type=Path,required=True);p.add_argument('--locus-dir',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args()
    q,s,e,x=analyse(a.manifest,a.retrieved_dir,a.paralog_report,a.locus_dir);a.outdir.mkdir(parents=True,exist_ok=True);write_csv(a.outdir/'locus_qc.csv',q);write_csv(a.outdir/'sample_qc.csv',s)
    for name,loci in e.items():(a.outdir/f'current_strict_{name}_loci.txt').write_text(''.join(x+'\n' for x in sorted(loci)),encoding='utf-8')
    (a.outdir/'current_qc_summary.json').write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,indent=2))
    if not x['global_tree_launch_allowed']:return 4
    return 0
if __name__=='__main__':raise SystemExit(main())
