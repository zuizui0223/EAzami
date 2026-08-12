#!/usr/bin/env python3
"""Summarize current 20-tip Compositae1061 occupancy/paralog QC after HybPiper.

This script intersects the *current* 20-tip recovered loci with the frozen
Moreyra-derived 1061/531/241 locus sets.  A locus is currently tree-eligible
within a base set only when >=80% of the 20 focal taxa have one recovered DNA
sequence and no focal sample has >1 sequence in HybPiper's paralog report.

The outputs are diagnostics and pre-tree matrix manifests. They do not promote
a branch-length tree or unlock flower-colour transition-rate fitting.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path

SETS={
 "public_1061":"moreyra_public_1061_loci.txt",
 "reproducible_531":"moreyra_reproducible_531_candidate_loci.txt",
 "conservative_241":"moreyra_conservative_241_no_warning_loci.txt",
}

def clean(x): return str(x or '').strip()
def read_csv(p,delimiter=','):
 with p.open(encoding='utf-8-sig',newline='') as h: return [{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h,delimiter=delimiter) if any(clean(v) for v in r.values())]
def parse_fasta(p):
 ids=[]
 with p.open(encoding='utf-8') as h:
  for line in h:
   if line.startswith('>'): ids.append(line[1:].strip().split()[0])
 return ids
def resolve_id(seqid,known):
 if seqid in known:return seqid
 hits=[x for x in known if seqid.startswith(x+'-') or seqid.startswith(x+'_')]
 if len(hits)==1:return hits[0]
 raise ValueError(f'unresolved focal FASTA id {seqid!r}')
def load_sets(d):
 out={}
 for k,f in SETS.items():
  p=d/f; loci=[x.strip() for x in p.read_text().splitlines() if x.strip()]
  if len(loci)!=len(set(loci)):raise ValueError(f'duplicate loci in {p}')
  out[k]=set(loci)
 return out
def parse_paralogs(p,known):
 rows=read_csv(p,delimiter='\t');
 if not rows or 'Species' not in rows[0]:raise ValueError('paralog report lacks Species')
 genes=[k for k in rows[0] if k!='Species']; out=defaultdict(set); seen=set()
 for r in rows:
  s=r['Species']
  if s not in known: raise ValueError(f'unknown paralog-report sample {s}')
  seen.add(s)
  for g in genes:
   try:n=int(float(r[g] or 0))
   except ValueError: raise ValueError(f'invalid paralog count {s}/{g}={r[g]!r}')
   if n>1: out[g].add(s)
 if seen!=known: raise ValueError(f'paralog report sample mismatch missing={sorted(known-seen)}')
 return out
def analyse(runs_path,retrieved_dir,paralog_path,locus_dir,min_occ=0.80):
 runs=read_csv(runs_path); known={r['tip_id'] for r in runs}
 if len(runs)!=20 or len(known)!=20:raise ValueError('expected 20 unique primary tips')
 dtype={r['tip_id']:r['data_type'] for r in runs}; groups=Counter(dtype.values())
 if groups!={'leaf_rnaseq':13,'target_capture':7}:raise ValueError(f'data-type split drift {groups}')
 sets=load_sets(locus_dir); paralogs=parse_paralogs(paralog_path,known)
 locus_present=defaultdict(set)
 for p in sorted(retrieved_dir.glob('*.FNA')):
  locus=p.stem; ids=parse_fasta(p); samples=[]
  for i in ids:samples.append(resolve_id(i,known))
  if len(samples)!=len(set(samples)):raise ValueError(f'duplicate focal sequence at locus {locus}')
  locus_present[locus]=set(samples)
 all_loci=sorted(set().union(*sets.values()))
 qrows=[]; eligible={k:[] for k in sets}
 threshold=math.ceil(min_occ*len(known))
 for locus in all_loci:
  present=locus_present.get(locus,set()); ps=paralogs.get(locus,set())
  row={'locus':locus,'focal_present':len(present),'focal_occupancy':len(present)/20,'rnaseq_present':sum(dtype[s]=='leaf_rnaseq' for s in present),'target_capture_present':sum(dtype[s]=='target_capture' for s in present),'current_paralog_samples':len(ps)}
  for k,s in sets.items():
   member=locus in s; ok=member and len(present)>=threshold and not ps
   row[f'in_{k}']='yes' if member else 'no'; row[f'eligible_{k}']='yes' if ok else 'no'
   if ok:eligible[k].append(locus)
  qrows.append(row)
 sample_rows=[]
 for tip in sorted(known):
  row={'tip_id':tip,'data_type':dtype[tip]}
  for k,loci in eligible.items():
   n=sum(tip in locus_present.get(l,set()) for l in loci); row[f'{k}_present']=n; row[f'{k}_fraction']=n/len(loci) if loci else 0
  sample_rows.append(row)
 def med(vals):return statistics.median(vals) if vals else 0
 set_summary={}
 for k,loci in eligible.items():
  rn=[r[f'{k}_fraction'] for r in sample_rows if r['data_type']=='leaf_rnaseq']; tc=[r[f'{k}_fraction'] for r in sample_rows if r['data_type']=='target_capture']
  set_summary[k]={'base_count':len(sets[k]),'current_eligible_count':len(loci),'median_rnaseq_sample_fraction':med(rn),'median_target_capture_sample_fraction':med(tc),'absolute_library_type_median_gap':abs(med(rn)-med(tc)),'all_20_taxa_represented':all(r[f'{k}_present']>0 for r in sample_rows)}
 summary={'contract_version':'colour_rate_comp1061_current_qc_v1','primary_tips':20,'min_current_locus_occupancy':min_occ,'minimum_present_tips':threshold,'data_type_counts':dict(groups),'sets':set_summary,'mapping_mode_not_inferred_from_files':True,'tree_matrix_auto_promotion_allowed':False,'branch_length_tree_completed':False,'rate_fit_execution_allowed':False,'claim_limit':'Current occupancy/no-paralog filtering is necessary but not sufficient for tree promotion. Mapping-mode, library-type missingness, alignment, outgroup/rooting, topology and replicate sensitivities remain required.'}
 return qrows,sample_rows,eligible,summary
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:return
 with p.open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--retrieved-dir',type=Path,required=True);p.add_argument('--paralog-report',type=Path,required=True);p.add_argument('--locus-dir',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);p.add_argument('--min-occupancy',type=float,default=.80);a=p.parse_args()
 q,s,e,x=analyse(a.runs,a.retrieved_dir,a.paralog_report,a.locus_dir,a.min_occupancy);a.outdir.mkdir(parents=True,exist_ok=True);write_csv(a.outdir/'locus_qc.csv',q);write_csv(a.outdir/'sample_qc.csv',s)
 for k,loci in e.items():(a.outdir/f'current_{k}_loci.txt').write_text(''.join(z+'\n' for z in sorted(loci)))
 (a.outdir/'current_qc_summary.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
if __name__=='__main__':main()
