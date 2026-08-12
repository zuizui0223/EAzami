#!/usr/bin/env python3
"""Prepare common-locus FASTAs for the 302-sample Japanese-origin placement tree."""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
REF_PREFIXES=('lett','saff','sunf')

def clean(x):return str(x or '').strip()
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
        for name,seq in rows:
            h.write(f'>{name}\n')
            for i in range(0,len(seq),80):h.write(seq[i:i+80]+'\n')
def load_manifest(path):
    with path.open(encoding='utf-8-sig',newline='') as h:rows=[{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h)]
    if len(rows)!=302 or len({r['tip_id'] for r in rows})!=302:raise ValueError('expected 302 unique global tip IDs')
    return rows
def load_loci(path):
    x=[z.strip() for z in path.read_text().splitlines() if z.strip()]
    if not x or len(x)>241 or len(x)!=len(set(x)):raise ValueError('primary locus list must be unique and within frozen 241 universe')
    return x
def refs(path):
    out={}
    for hdr,seq in read_fasta(path):
        for p in REF_PREFIXES:
            if hdr.startswith(p+'-'):
                out.setdefault(hdr[len(p)+1:],[]).append((f'OUTGROUP_{p}',seq.upper()));break
    return out
def retrieved(root):
    out={}
    for p in root.iterdir():
        if not p.is_file():continue
        for suffix in ('.FNA','.fasta','.fa','.fas','.fna'):
            if p.name.endswith(suffix):
                locus=p.name[:-len(suffix)]
                if locus in out:raise ValueError(f'duplicate retrieved locus file {locus}')
                out[locus]=p;break
    return out
def normalize(records,tips):
    out=[];seen=set()
    for hdr,seq in records:
        cand=hdr.split()[0]
        hits=[t for t in tips if cand==t or cand.startswith(t+'-') or cand.startswith(t+'_') or cand.startswith(t+'|')]
        if len(hits)!=1:continue
        tip=hits[0]
        if tip in seen:raise ValueError(f'multiple recovered sequences for {tip}')
        if seq:out.append((tip,seq.upper()));seen.add(tip)
    return out
def build(manifest,locus_list,retrieved_dir,target,outdir,min_fraction=.80):
    rows=load_manifest(manifest);tips={r['tip_id'] for r in rows};wanted=load_loci(locus_list);files=retrieved(retrieved_dir);reference=refs(target);min_n=math.ceil(len(tips)*min_fraction)
    m=[];eligible=[];saff=0;locus_dir=outdir/'loci_unaligned'
    for locus in wanted:
        focal=normalize(read_fasta(files[locus]),tips) if locus in files else []
        anchors=reference.get(locus,[])
        row={'locus':locus,'focal_sequences':len(focal),'focal_fraction':len(focal)/len(tips),'reference_sequences':len(anchors),'has_lett':any(x[0]=='OUTGROUP_lett' for x in anchors),'has_sunf':any(x[0]=='OUTGROUP_sunf' for x in anchors),'has_saff':any(x[0]=='OUTGROUP_saff' for x in anchors),'eligible':False,'reason':''}
        if len(focal)<min_n:row['reason']='focal_occupancy_below_0.80'
        elif not row['has_lett'] or not row['has_sunf']:row['reason']='required_root_reference_missing'
        else:
            row['eligible']=True;row['reason']='eligible';eligible.append(locus);saff+=int(row['has_saff']);write_fasta(locus_dir/f'{locus}.fasta',focal+anchors)
        m.append(row)
    outdir.mkdir(parents=True,exist_ok=True)
    with (outdir/'locus_manifest.csv').open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(m[0]));w.writeheader();w.writerows(m)
    (outdir/'eligible_loci.txt').write_text(''.join(x+'\n' for x in eligible),encoding='utf-8')
    s={'contract_version':'japan_origin_global_comp1061_tree_inputs_v1','global_focal_tips':302,'supplied_primary_loci':len(wanted),'minimum_focal_occupancy_fraction':min_fraction,'minimum_focal_sequences':min_n,'eligible_loci':len(eligible),'eligible_loci_with_saff_reference':saff,'required_root_references':['OUTGROUP_lett','OUTGROUP_sunf'],'optional_near_reference':'OUTGROUP_saff','tree_input_ready':len(eligible)>=100,'automatic_relaxation_allowed':False,'claim_limit':'Tree-input readiness is an engineering gate only. It does not imply any Japanese monophyly or colonisation result.'}
    (outdir/'tree_input_summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
    if not s['tree_input_ready']:raise ValueError(f'Only {len(eligible)} strict global loci; primary launch requires >=100 and may not auto-relax')
    return s
def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--locus-list',type=Path,required=True);p.add_argument('--retrieved-dir',type=Path,required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();build(a.manifest,a.locus_list,a.retrieved_dir,a.target,a.outdir);return 0
if __name__=='__main__':raise SystemExit(main())
