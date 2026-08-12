#!/usr/bin/env python3
"""Prepare common-locus FASTAs for the 20-tip flower-colour branch-length tree.

Input is the HybPiper ``retrieve_sequences dna --fasta_dir`` output from one
mapping mode. The supplied locus list is already the current no-paralog subset
of the frozen Moreyra conservative-241 universe; loci are retained for this
cross-assay tree only when at least 80% of the 20 frozen focal taxa have a
recovered sequence. Original Compositae1061 reference sequences are appended as
explicit non-Cirsium references. `lett` and `sunf` are required; `saff` is
retained and counted wherever available but is not a locus-admission criterion.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REF_PREFIXES=("lett","saff","sunf")


def clean(x: object)->str: return str(x or "").strip()

def read_fasta(path: Path)->list[tuple[str,str]]:
    rows=[]; name=None; seq=[]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line: continue
        if line.startswith(">"):
            if name is not None: rows.append((name,"".join(seq)))
            name=line[1:].split()[0]; seq=[]
        else: seq.append(line)
    if name is not None: rows.append((name,"".join(seq)))
    return rows

def write_fasta(path: Path, rows:list[tuple[str,str]])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8") as f:
        for name,seq in rows:
            f.write(f">{name}\n")
            for i in range(0,len(seq),80): f.write(seq[i:i+80]+"\n")

def loci(path: Path)->list[str]:
    values=[x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not values or len(set(values))!=len(values): raise ValueError("Locus list must contain unique non-empty loci")
    if len(values)>241: raise ValueError("Current tree locus list cannot exceed the frozen 241-locus universe")
    return values

def primary_tips(path: Path)->list[dict[str,str]]:
    with path.open(encoding="utf-8-sig",newline="") as f: rows=[{k:clean(v) for k,v in r.items()} for r in csv.DictReader(f)]
    if len(rows)!=20 or len({r["tip_id"] for r in rows})!=20: raise ValueError("Expected 20 unique primary tips")
    return rows

def target_refs(path: Path)->dict[str,list[tuple[str,str]]]:
    out={}
    for header,seq in read_fasta(path):
        hit=None
        for p in REF_PREFIXES:
            if header.startswith(p+"-"):
                hit=(p,header[len(p)+1:]); break
        if hit is None: continue
        p,locus=hit
        out.setdefault(locus,[]).append((f"OUTGROUP_{p}",seq))
    return out

def retrieve_files(root: Path)->dict[str,Path]:
    out={}
    for p in root.iterdir():
        if not p.is_file(): continue
        name=p.name
        for suffix in (".FNA",".fasta",".fa",".fas",".fna"):
            if name.endswith(suffix):
                locus=name[:-len(suffix)]
                if locus in out: raise ValueError(f"Duplicate retrieved locus file: {locus}")
                out[locus]=p; break
    return out

def normalize_focal_records(records:list[tuple[str,str]], tip_ids:set[str])->list[tuple[str,str]]:
    out=[]; seen=set()
    for header,seq in records:
        candidate=header.split()[0]
        matches=[t for t in tip_ids if candidate==t or candidate.startswith(t+"-") or candidate.startswith(t+"|")]
        if len(matches)!=1: continue
        tip=matches[0]
        if tip in seen: raise ValueError(f"Multiple recovered sequences for primary tip {tip}")
        if seq: out.append((tip,seq.upper())); seen.add(tip)
    return out

def build(primary:Path,locus_list:Path,retrieved:Path,target:Path,outdir:Path,min_fraction:float=0.8)->dict[str,object]:
    tips=primary_tips(primary); ids={r["tip_id"] for r in tips}; wanted=loci(locus_list)
    files=retrieve_files(retrieved); refs=target_refs(target)
    min_n=int(len(ids)*min_fraction + 0.999999)
    manifest=[]; eligible=[]; eligible_saff=0
    locus_dir=outdir/"loci_unaligned"
    for locus in wanted:
        focal=normalize_focal_records(read_fasta(files[locus]),ids) if locus in files else []
        anchors=refs.get(locus,[])
        row={
            "locus":locus,"focal_sequences":len(focal),"focal_fraction":len(focal)/20,
            "reference_sequences":len(anchors),
            "has_lett":any(x[0]=="OUTGROUP_lett" for x in anchors),
            "has_sunf":any(x[0]=="OUTGROUP_sunf" for x in anchors),
            "has_saff":any(x[0]=="OUTGROUP_saff" for x in anchors),
            "eligible":False,"reason":""
        }
        if len(focal)<min_n: row["reason"]="focal_occupancy_below_0.80"
        elif not row["has_lett"] or not row["has_sunf"]: row["reason"]="required_root_reference_missing"
        else:
            row["eligible"]=True; row["reason"]="eligible"; eligible.append(locus)
            if row["has_saff"]: eligible_saff+=1
            write_fasta(locus_dir/f"{locus}.fasta",focal+anchors)
        manifest.append(row)
    outdir.mkdir(parents=True,exist_ok=True)
    fields=list(manifest[0])
    with (outdir/"locus_manifest.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(manifest)
    (outdir/"eligible_loci.txt").write_text("\n".join(eligible)+("\n" if eligible else ""),encoding="utf-8")
    summary={
        "contract_version":"colour_rate_comp1061_tree_inputs_v2",
        "supplied_current_locus_count":len(wanted),
        "maximum_frozen_locus_universe":241,
        "focal_taxa":20,
        "minimum_focal_occupancy_fraction":min_fraction,
        "minimum_focal_sequences":min_n,
        "eligible_loci":len(eligible),
        "eligible_loci_with_saff_reference":eligible_saff,
        "required_root_references":["OUTGROUP_lett","OUTGROUP_sunf"],
        "optional_near_reference":"OUTGROUP_saff",
        "tree_input_ready":len(eligible)>=100,
        "claim_limit":"The >=100 eligible-locus threshold is a conservative engineering gate for launching the tree stage. Safflower-reference coverage is recorded diagnostically and is not used to relax or tighten locus admission post hoc."
    }
    (outdir/"tree_input_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    if not summary["tree_input_ready"]: raise ValueError(f"Only {len(eligible)} current-clean loci passed the cross-assay occupancy/root-reference gate")
    return summary

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--primary-runs",type=Path,required=True);p.add_argument("--locus-list",type=Path,required=True);p.add_argument("--retrieved-dir",type=Path,required=True);p.add_argument("--target",type=Path,required=True);p.add_argument("--outdir",type=Path,required=True);p.add_argument("--min-fraction",type=float,default=0.8);a=p.parse_args()
    print(json.dumps(build(a.primary_runs,a.locus_list,a.retrieved_dir,a.target,a.outdir,a.min_fraction),indent=2));return 0
if __name__=="__main__": raise SystemExit(main())
