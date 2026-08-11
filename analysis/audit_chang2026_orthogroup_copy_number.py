#!/usr/bin/env python3
"""Audit copy-number/homeolog-sensitive orthogroup classes for Chang 2026.

The strict gene-tree matrix uses complete one-copy orthogroups, but that primary
filter can hide biologically relevant copy structure in a polyploid/reticulate
group. This audit reads every OrthoFinder Orthogroup_Sequences FASTA and classifies
copy state without automatically selecting a homeolog.
"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
from typing import Sequence

FIELDS=("orthogroup_id","status","observed_sequence_count","mapped_sample_count","focal_present_count","focal_multicopy_samples","control_multicopy_samples","focal_missing_samples","control_missing_samples","max_copy_number","copy_vector","source_fasta","interpretation")

def clean(x): return str(x or "").strip()

def fasta_records(handle):
    header=None; parts=[]
    for raw in handle:
        line=raw.strip()
        if not line: continue
        if line.startswith(">"):
            if header is not None: yield header,"".join(parts)
            header=line[1:]; parts=[]
        else: parts.append(line)
    if header is not None: yield header,"".join(parts)

def sample_from_header(header:str,sample_ids:Sequence[str]):
    ident=header.split()[0]
    if ident in sample_ids: return ident
    matches=[s for s in sample_ids if ident.startswith(s+"|") or ident.startswith(s+"__")]
    return matches[0] if len(matches)==1 else None

def read_panel(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as h: rows=list(csv.DictReader(h))
    ids=[clean(r.get("sample_id")) for r in rows]
    if len(rows)!=19 or any(not x for x in ids) or len(set(ids))!=19: raise ValueError("Expected 19 unique panel sample IDs")
    focal=[clean(r["sample_id"]) for r in rows if clean(r.get("panel_role"))=="focal_colour_morph"]
    if len(focal)!=6: raise ValueError(f"Expected six focal samples, observed {len(focal)}")
    return ids,focal

def find_sequence_directory(root:Path):
    matches=sorted(root.rglob("Orthogroups_SingleCopyOrthologues.txt"))
    if len(matches)!=1: raise ValueError(f"Expected one OrthoFinder result set, observed {len(matches)}")
    directory=matches[0].parent.parent/"Orthogroup_Sequences"
    if not directory.is_dir(): raise FileNotFoundError(directory)
    return directory

def fasta_paths(directory:Path):
    paths=sorted({*directory.glob("*.fa"),*directory.glob("*.fasta"),*directory.glob("*.faa")})
    if not paths: raise FileNotFoundError(f"No orthogroup FASTAs in {directory}")
    return paths

def audit_one(path:Path,samples:Sequence[str],focal:Sequence[str]):
    counts=Counter(); unmapped=[]; empty=[]; observed=0; focal_set=set(focal)
    with path.open(encoding="utf-8") as h:
        for header,seq in fasta_records(h):
            observed+=1
            if not seq: empty.append(header)
            sample=sample_from_header(header,samples)
            if sample is None: unmapped.append(header)
            else: counts[sample]+=1
    controls=[s for s in samples if s not in focal_set]; fm=[s for s in focal if counts[s]==0]; cm=[s for s in controls if counts[s]==0]; fmulti=[s for s in focal if counts[s]>1]; cmulti=[s for s in controls if counts[s]>1]
    if empty: status="empty_sequences"; interpretation="At least one FASTA record is empty."
    elif unmapped: status="unmapped_headers"; interpretation="At least one sequence cannot be assigned uniquely to a panel sample."
    elif fm: status="focal_missing"; interpretation="One or more W/BP focal samples are absent; unsuitable for six-tip topology scoring."
    elif fmulti: status="focal_multicopy"; interpretation="A focal sample has multiple observed copies; no homeolog is selected automatically."
    elif cm: status="control_missing"; interpretation="All six focal samples are one-copy but at least one external control is absent."
    elif cmulti: status="focal_one_copy_control_multicopy"; interpretation="All six focal samples are one-copy and complete; one or more controls have multiple copies."
    elif all(counts[s]==1 for s in samples): status="strict_complete_one_copy"; interpretation="Exactly one sequence is present for all 19 samples."
    else: status="other_copy_state"; interpretation="Copy state does not match a predefined sensitivity class."
    return {"orthogroup_id":path.stem,"status":status,"observed_sequence_count":observed,"mapped_sample_count":sum(counts[s]>0 for s in samples),"focal_present_count":sum(counts[s]>0 for s in focal),"focal_multicopy_samples":"|".join(fmulti),"control_multicopy_samples":"|".join(cmulti),"focal_missing_samples":"|".join(fm),"control_missing_samples":"|".join(cm),"max_copy_number":max([counts[s] for s in samples] or [0]),"copy_vector":"|".join(f"{s}:{counts[s]}" for s in samples),"source_fasta":str(path),"interpretation":interpretation}

def audit(root:Path,panel:Path):
    samples,focal=read_panel(panel); directory=find_sequence_directory(root); rows=[audit_one(path,samples,focal) for path in fasta_paths(directory)]; statuses=Counter(row["status"] for row in rows)
    summary={"audit_version":"chang2026_orthogroup_copy_audit_v1","panel_sample_count":19,"focal_sample_count":6,"orthogroup_count":len(rows),"status_counts":dict(sorted(statuses.items())),"strict_complete_one_copy_count":statuses.get("strict_complete_one_copy",0),"focal_one_copy_control_multicopy_count":statuses.get("focal_one_copy_control_multicopy",0),"focal_multicopy_count":statuses.get("focal_multicopy",0),"focal_missing_count":statuses.get("focal_missing",0),"orthogroup_sequence_directory":str(directory),"primary_rule":"strict_complete_one_copy only","copy_aware_sensitivity_rule":"retain focal_one_copy_control_multicopy separately; never choose one focal homeolog automatically when focal_multicopy","claim_limit":"Observed transcript/protein copy classes do not identify alleles, homeolog ancestry, duplication timing or ploidy by themselves."}
    return rows,summary

def main():
    p=argparse.ArgumentParser(); p.add_argument("--orthofinder-root",type=Path,required=True); p.add_argument("--panel",type=Path,required=True); p.add_argument("--outdir",type=Path,required=True); a=p.parse_args(); rows,summary=audit(a.orthofinder_root,a.panel); a.outdir.mkdir(parents=True,exist_ok=True)
    with (a.outdir/"orthogroup_copy_number_audit.csv").open("w",encoding="utf-8",newline="") as h: w=csv.DictWriter(h,fieldnames=FIELDS,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    (a.outdir/"orthogroup_copy_number_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8"); print("status_counts="+json.dumps(summary["status_counts"],sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
