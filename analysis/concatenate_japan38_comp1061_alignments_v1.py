#!/usr/bin/env python3
"""Concatenate aligned Japan-38 Comp1061 loci with safflower as the sole root tip."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
EXPECTED_TIPS=39
ROOT='OUTGROUP_saff'

def read_fasta(path):
    out={};name=None;seq=[]
    for raw in path.read_text(encoding='utf-8').splitlines():
        x=raw.strip()
        if not x:continue
        if x.startswith('>'):
            if name is not None:out[name]=''.join(seq)
            name=x[1:].split()[0];seq=[]
        else:seq.append(x)
    if name is not None:out[name]=''.join(seq)
    lens={len(v) for v in out.values()}
    if len(lens)!=1:raise ValueError(f'ragged alignment {path}: {lens}')
    return out,next(iter(lens))
def main():
    p=argparse.ArgumentParser();p.add_argument('--eligible-loci',type=Path,required=True);p.add_argument('--alignment-dir',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--partitions',type=Path,required=True);p.add_argument('--summary',type=Path,required=True);a=p.parse_args()
    loci=[x.strip() for x in a.eligible_loci.read_text().splitlines() if x.strip()]
    if len(loci)<100:raise ValueError('Refusing concatenation with <100 eligible loci')
    with a.manifest.open(encoding='utf-8-sig',newline='') as h:rows=list(csv.DictReader(h))
    focal=[r['tip_id'].strip() for r in rows]
    if len(focal)!=EXPECTED_TIPS or len(set(focal))!=EXPECTED_TIPS:raise ValueError(f'expected {EXPECTED_TIPS} unique focal tips')
    allowed=set(focal)|{ROOT};loaded=[]
    for locus in loci:
        f=a.alignment_dir/f'{locus}.aln.fasta'
        seqs,n=read_fasta(f);unknown=set(seqs)-allowed
        if unknown:raise ValueError(f'unexpected labels {locus}: {sorted(unknown)}')
        if ROOT not in seqs:raise ValueError(f'{locus} lacks {ROOT}')
        loaded.append((locus,seqs,n))
    taxa=focal+[ROOT];concat={t:[] for t in taxa};parts=[];start=1
    for locus,seqs,n in loaded:
        for t in taxa:concat[t].append(seqs.get(t,'-'*n))
        end=start+n-1;parts.append((locus,start,end));start=end+1
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',encoding='utf-8') as h:
        for t in taxa:h.write(f'>{t}\n{"".join(concat[t])}\n')
    with a.partitions.open('w',encoding='utf-8',newline='') as h:
        w=csv.writer(h);w.writerow(['locus','start','end']);w.writerows(parts)
    summary={'contract_version':'japan38_comp1061_concat_v1','loci':len(loci),'focal_tips':EXPECTED_TIPS,'tree_tip_count':EXPECTED_TIPS+1,'root_tip':ROOT,'alignment_length':start-1,'missing_filled_with_gaps':True,'claim_boundary':'Independent conservative-241 compatibility tree; not the unpublished Moreyra final-350 phylogeny.'}
    a.summary.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
