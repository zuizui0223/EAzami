#!/usr/bin/env python3
"""Concatenate aligned Compositae1061 loci with explicit missing-data padding.

The two distant references (lett/sunf) are always required by the tree-input
contract.  The closer Cardueae reference `OUTGROUP_saff` is retained in the
concatenation whenever it occurs in at least one admitted alignment, with gaps
at loci where the original Compositae1061 target lacks that sequence.  It is a
reference/monophyly anchor, not part of the IQ-TREE rooting set.
"""
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
            if name is not None:
                if name in out: raise ValueError(f'duplicate header {name} in {path}')
                out[name]=''.join(seq)
            name=x[1:].split()[0]; seq=[]
        else: seq.append(x)
    if name is not None:
        if name in out: raise ValueError(f'duplicate header {name} in {path}')
        out[name]=''.join(seq)
    lengths={len(v) for v in out.values()}
    if len(lengths)!=1: raise ValueError(f'unaligned or ragged FASTA {path}: {sorted(lengths)}')
    return out, next(iter(lengths))

def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--eligible-loci',type=Path,required=True);p.add_argument('--alignment-dir',type=Path,required=True);p.add_argument('--primary-runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--partitions',type=Path,required=True);p.add_argument('--summary',type=Path,required=True);a=p.parse_args()
    loci=[x.strip() for x in a.eligible_loci.read_text().splitlines() if x.strip()]
    if len(loci)<100: raise ValueError('Refusing concatenation with <100 eligible loci')
    with a.primary_runs.open(encoding='utf-8-sig',newline='') as f: primary=list(csv.DictReader(f))
    focal=[r['tip_id'] for r in primary]
    if len(focal)!=len(set(focal)): raise ValueError('primary tip IDs are not unique')

    # First inspect every alignment so the optional saff reference is retained
    # deterministically if it occurs anywhere in the admitted matrix.
    loaded=[]; saff_loci=0
    allowed=set(focal)|{'OUTGROUP_lett','OUTGROUP_sunf','OUTGROUP_saff'}
    for locus in loci:
        path=a.alignment_dir/f'{locus}.aln.fasta'
        if not path.is_file(): raise ValueError(f'missing alignment {path}')
        seqs,n=read_fasta(path)
        unknown=sorted(set(seqs)-allowed)
        if unknown: raise ValueError(f'unexpected alignment labels for {locus}: {unknown}')
        for required in ('OUTGROUP_lett','OUTGROUP_sunf'):
            if required not in seqs: raise ValueError(f'{locus} lacks required reference {required}')
        if 'OUTGROUP_saff' in seqs: saff_loci+=1
        loaded.append((locus,seqs,n))

    reference_tips=['OUTGROUP_lett','OUTGROUP_sunf']
    if saff_loci:
        reference_tips.append('OUTGROUP_saff')
    taxa=focal+reference_tips
    concat={t:[] for t in taxa}; parts=[]; start=1
    for locus,seqs,n in loaded:
        for t in taxa: concat[t].append(seqs.get(t,'-'*n))
        end=start+n-1; parts.append((locus,start,end)); start=end+1

    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w') as f:
        for t in taxa:
            s=''.join(concat[t]); f.write(f'>{t}\n')
            for i in range(0,len(s),80): f.write(s[i:i+80]+'\n')
    with a.partitions.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['locus','start','end']); w.writerows(parts)
    summary={
        'contract_version':'colour_rate_comp1061_concat_v2',
        'loci':len(loci),
        'focal_taxa':len(primary),
        'root_outgroups':['OUTGROUP_lett','OUTGROUP_sunf'],
        'reference_tips':reference_tips,
        'saff_reference_loci':saff_loci,
        'alignment_length':start-1,
        'missing_filled_with_gaps':True,
        'claim_limit':'OUTGROUP_saff is retained as an optional near Cardueae reference when available; IQ-TREE rooting remains on lett+sunf and focal monophyly is checked against every retained reference tip.'
    }
    a.summary.write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
