#!/usr/bin/env python3
"""Concatenate aligned Compositae1061 loci with explicit missing-data padding."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_fasta(path:Path):
    out={}; name=None; seq=[]
    for raw in path.read_text().splitlines():
        x=raw.strip()
        if not x: continue
        if x.startswith('>'):
            if name is not None: out[name]=''.join(seq)
            name=x[1:].split()[0]; seq=[]
        else: seq.append(x)
    if name is not None: out[name]=''.join(seq)
    if len(out)!=len(set(out)): raise ValueError(f'duplicate headers in {path}')
    lengths={len(v) for v in out.values()}
    if len(lengths)!=1: raise ValueError(f'unaligned or ragged FASTA {path}: {sorted(lengths)}')
    return out, next(iter(lengths))

def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--eligible-loci',type=Path,required=True);p.add_argument('--alignment-dir',type=Path,required=True);p.add_argument('--primary-runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--partitions',type=Path,required=True);p.add_argument('--summary',type=Path,required=True);a=p.parse_args()
    loci=[x.strip() for x in a.eligible_loci.read_text().splitlines() if x.strip()]
    if len(loci)<100: raise ValueError('Refusing concatenation with <100 eligible loci')
    with a.primary_runs.open(encoding='utf-8-sig',newline='') as f: primary=list(csv.DictReader(f))
    taxa=[r['tip_id'] for r in primary]+['OUTGROUP_lett','OUTGROUP_sunf']
    concat={t:[] for t in taxa}; parts=[]; start=1
    for locus in loci:
        path=a.alignment_dir/f'{locus}.aln.fasta'
        if not path.is_file(): raise ValueError(f'missing alignment {path}')
        seqs,n=read_fasta(path)
        unknown=sorted(set(seqs)-set(taxa)-{'OUTGROUP_saff'})
        if unknown: raise ValueError(f'unexpected alignment labels for {locus}: {unknown}')
        for t in taxa: concat[t].append(seqs.get(t,'-'*n))
        end=start+n-1; parts.append((locus,start,end)); start=end+1
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w') as f:
        for t in taxa:
            s=''.join(concat[t]); f.write(f'>{t}\n');
            for i in range(0,len(s),80): f.write(s[i:i+80]+'\n')
    with a.partitions.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['locus','start','end']); w.writerows(parts)
    summary={'contract_version':'colour_rate_comp1061_concat_v1','loci':len(loci),'focal_taxa':len(primary),'outgroups':['OUTGROUP_lett','OUTGROUP_sunf'],'alignment_length':start-1,'missing_filled_with_gaps':True}
    a.summary.write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
