#!/usr/bin/env python3
"""Prepare safflower-rooted common-locus FASTAs for the 39-sample Japan-38 tree."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
EXPECTED_TIPS=39
ROOT_PREFIX='saff'
ROOT_TIP='OUTGROUP_saff'

def read_fasta(path):
    rows=[];name=None;seq=[]
    for raw in path.read_text(encoding='utf-8').splitlines():
        x=raw.strip()
        if not x:continue
        if x.startswith('>'):
            if name is not None:rows.append((name,''.join(seq)))
            name=x[1:].split()[0];seq=[]
        else:seq.append(x)
    if name is not None:rows.append((name,''.join(seq)))
    return rows
def write_fasta(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as h:
        for name,seq in rows:h.write(f'>{name}\n{seq}\n')
def load_manifest(path):
    with path.open(encoding='utf-8-sig',newline='') as h:rows=list(csv.DictReader(h))
    tips=[r['tip_id'].strip() for r in rows]
    if len(rows)!=EXPECTED_TIPS or len(set(tips))!=EXPECTED_TIPS:raise ValueError(f'expected {EXPECTED_TIPS} unique tips')
    return tips
def normalize(records,tips):
    out=[];seen=set()
    for hdr,seq in records:
        cand=hdr.split()[0];hits=[t for t in tips if cand==t or cand.startswith(t+'-') or cand.startswith(t+'_') or cand.startswith(t+'|')]
        if len(hits)!=1:continue
        tip=hits[0]
        if tip in seen:raise ValueError(f'multiple recovered sequences for {tip}')
        if seq:out.append((tip,seq.upper()));seen.add(tip)
    return out
def reference_saff(target):
    out={}
    for hdr,seq in read_fasta(target):
        if hdr.startswith(ROOT_PREFIX+'-'):out[hdr[len(ROOT_PREFIX)+1:]]=(ROOT_TIP,seq.upper())
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--locus-list',type=Path,required=True);p.add_argument('--retrieved-dir',type=Path,required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args()
    tips=load_manifest(a.manifest);wanted=[x.strip() for x in a.locus_list.read_text().splitlines() if x.strip()];refs=reference_saff(a.target);eligible=[];rows=[]
    for locus in wanted:
        src=a.retrieved_dir/f'{locus}.FNA'
        focal=normalize(read_fasta(src),tips) if src.is_file() else []
        root=refs.get(locus)
        ok=bool(root) and len(focal)>=1
        rows.append({'locus':locus,'focal_sequences':len(focal),'has_saff':bool(root),'eligible':ok})
        if ok:eligible.append(locus);write_fasta(a.outdir/'loci_unaligned'/f'{locus}.fasta',focal+[root])
    a.outdir.mkdir(parents=True,exist_ok=True)
    with (a.outdir/'locus_manifest.csv').open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.outdir/'eligible_loci.txt').write_text(''.join(x+'\n' for x in eligible),encoding='utf-8')
    summary={'contract_version':'japan38_comp1061_tree_inputs_v1','focal_tips':EXPECTED_TIPS,'supplied_qc_loci':len(wanted),'eligible_loci_with_saff':len(eligible),'root_tip':ROOT_TIP,'tree_input_ready':len(eligible)>=100,'claim_boundary':'Only QC-admitted loci with a safflower reference enter the tree. Missing focal sequences are handled as gaps after alignment; no unpublished Moreyra topology is imposed.'}
    (a.outdir/'tree_input_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
    if not summary['tree_input_ready']:raise SystemExit('fewer than 100 saff-rootable Japan38 loci')
if __name__=='__main__':main()
