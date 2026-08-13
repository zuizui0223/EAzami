#!/usr/bin/env python3
"""Build the contract-gated Read2Tree fast-screen plan for six Chang 2026
Cirsium japonicum var. takaoense RNA-seq samples.

The six-sample plan may only be generated from a validated OMA marker-pack
contract. This prevents an arbitrary marker directory or stale OMA export from
silently entering the candidate-regain topology screen.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, shlex
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_SAMPLE_COUNT=6
EXPECTED_MORPHS={"BP":3,"W":3}
EXPECTED_OMA_CODES=("CYNCS","HELAN","DAUCS")
EXPECTED_OMA_RELEASE="May2026"
EXPECTED_MARKER_COUNT=400
PLAN_FIELDS=("stage","sample_id","run","morph","read_1","read_2","command")

def clean(value: object)->str: return str(value or "").strip()
def sha256_file(path: Path)->str:
    d=hashlib.sha256()
    with path.open("rb") as h:
        for block in iter(lambda:h.read(1024*1024),b""): d.update(block)
    return d.hexdigest()
def read_csv(path: Path)->list[dict[str,str]]:
    with path.open(encoding="utf-8-sig",newline="") as h: return [{k:clean(v) for k,v in row.items()} for row in csv.DictReader(h)]

def validate_panel(path: Path)->list[dict[str,str]]:
    rows=read_csv(path)
    if len(rows)!=EXPECTED_SAMPLE_COUNT: raise ValueError(f"Expected {EXPECTED_SAMPLE_COUNT} focal samples, observed {len(rows)}")
    sample_ids=[clean(r.get("sample_id")) for r in rows]; runs=[clean(r.get("matched_run")) for r in rows]
    if any(not x for x in sample_ids+runs): raise ValueError("Each focal row must have sample_id and matched_run")
    if len(sample_ids)!=len(set(sample_ids)): raise ValueError("Focal sample_id values are not unique")
    if len(runs)!=len(set(runs)): raise ValueError("Focal SRA runs are not unique")
    if any(clean(r.get("library_layout")).upper()!="PAIRED" for r in rows): raise ValueError("Read2Tree pilot currently requires official PAIRED runs")
    if any(clean(r.get("panel_role"))!="focal_colour_morph" for r in rows): raise ValueError("Pilot may contain only focal_colour_morph rows")
    morphs=Counter(clean(r.get("morph")).upper() for r in rows)
    if dict(morphs)!=EXPECTED_MORPHS: raise ValueError(f"Expected 3 BP and 3 W samples, observed {dict(morphs)}")
    return sorted(rows,key=lambda r:r["sample_id"])

def validate_reference_manifest(path: Path)->list[dict[str,str]]:
    rows=read_csv(path)
    if not rows: raise ValueError("Reference manifest is empty")
    required={"oma_release","oma_code","scientific_name","reference_role","verified_in_oma"}; missing=required-set(rows[0])
    if missing: raise ValueError(f"Reference manifest lacks required columns: {sorted(missing)}")
    codes=tuple(clean(r.get("oma_code")) for r in rows)
    if codes!=EXPECTED_OMA_CODES: raise ValueError(f"Expected OMA codes {EXPECTED_OMA_CODES}, observed {codes}")
    if any(clean(r.get("oma_release"))!=EXPECTED_OMA_RELEASE for r in rows): raise ValueError(f"Reference manifest must be pinned to OMA {EXPECTED_OMA_RELEASE}")
    if any(clean(r.get("verified_in_oma")).lower()!="true" for r in rows): raise ValueError("All configured OMA reference genomes must be independently verified")
    return rows

def load_marker_contract(path: Path,refs: Sequence[Mapping[str,str]]):
    c=json.loads(path.read_text(encoding="utf-8"))
    if c.get("contract_version")!="eazami_read2tree_oma_marker_pack_v1": raise ValueError("Unsupported Read2Tree marker-pack contract version")
    if c.get("execution_allowed") is not True: raise ValueError("Read2Tree marker-pack contract does not allow execution")
    if c.get("oma_release")!=EXPECTED_OMA_RELEASE: raise ValueError(f"Marker pack is not from OMA {EXPECTED_OMA_RELEASE}")
    if tuple(c.get("reference_codes",[]))!=EXPECTED_OMA_CODES: raise ValueError("Marker-pack reference codes do not match the frozen EAzami reference set")
    if tuple(clean(r.get("oma_code")) for r in refs)!=tuple(c.get("reference_codes",[])): raise ValueError("Reference manifest and marker-pack contract disagree")
    params=c.get("export_parameters",{})
    if params.get("minimum_species_coverage")!=1.0: raise ValueError("Marker pack was not exported with minimum species coverage 1.0")
    if params.get("maximum_markers")!=EXPECTED_MARKER_COUNT or c.get("marker_count")!=EXPECTED_MARKER_COUNT: raise ValueError("Validated marker pack is not the frozen 400-marker export")
    marker_dir=(path.parent/clean(c.get("normalized_marker_dir"))).resolve(); dna=(path.parent/clean(c.get("dna_reference"))).resolve()
    if not marker_dir.is_dir(): raise ValueError(f"Validated marker directory is missing: {marker_dir}")
    if not dna.is_file(): raise ValueError(f"Validated DNA reference is missing: {dna}")
    if sha256_file(dna)!=clean(c.get("dna_reference_sha256")): raise ValueError("dna_ref.fa SHA256 does not match marker-pack contract")
    if len(list(marker_dir.glob("*.fa")))!=400 or len(list(marker_dir.glob("*.fna")))!=400: raise ValueError("Normalized marker directory does not contain 400 AA/DNA marker pairs")
    return c,marker_dir,dna

def read_paths(row: Mapping[str,str],reads_root: Path,stage: str):
    sid,run=clean(row.get("sample_id")),clean(row.get("matched_run"))
    if stage=="trimmed":
        base=reads_root/"samples"/sid/"trimmed"; return base/f"{sid}.R1.trim.fastq.gz",base/f"{sid}.R2.trim.fastq.gz"
    if stage=="raw":
        base=reads_root/"samples"/sid/"raw"; return base/f"{run}_1.fastq.gz",base/f"{run}_2.fastq.gz"
    raise ValueError(f"Unsupported reads stage: {stage}")
def command_text(parts: Sequence[object])->str: return shlex.join([str(p) for p in parts])
def build_plan(rows: Sequence[Mapping[str,str]],*,reads_root: Path,reads_stage: str,marker_dir: Path,dna_reference: Path,output_dir: Path,executable: str="read2tree",iqtree_executable: str="iqtree2",threads: int=8):
    if threads<1: raise ValueError("threads must be >=1")
    plan=[]
    step1=[executable,"--step","1marker","--standalone_path",marker_dir,"--dna_reference",dna_reference,"--output_path",output_dir,"--debug","--threads",threads]
    plan.append({"stage":"1marker","sample_id":"","run":"","morph":"","read_1":"","read_2":"","command":command_text(step1)})
    for row in rows:
        sid,run,morph=clean(row.get("sample_id")),clean(row.get("matched_run")),clean(row.get("morph")).upper(); r1,r2=read_paths(row,reads_root,reads_stage)
        step2=[executable,"--step","2map","--standalone_path",marker_dir,"--dna_reference",dna_reference,"--reads",r1,r2,"--species_name",sid,"--read_type","-ax sr","--output_path",output_dir,"--debug","--threads",threads]
        plan.append({"stage":"2map","sample_id":sid,"run":run,"morph":morph,"read_1":str(r1),"read_2":str(r2),"command":command_text(step2)})
    step3=[executable,"--step","3combine","--standalone_path",marker_dir,"--dna_reference",dna_reference,"--output_path",output_dir,"--debug","--threads",threads]
    plan.append({"stage":"3combine","sample_id":"","run":"","morph":"","read_1":"","read_2":"","command":command_text(step3)})
    dna_alignment=output_dir/"concat_merge_dna.phy"; iqtree=[iqtree_executable,"-s",dna_alignment,"-m","MFP","-B","1000","--alrt","1000","-T","AUTO","--prefix",output_dir/"takaoense6_read2tree_dna"]
    plan.append({"stage":"dna_tree","sample_id":"","run":"","morph":"","read_1":"","read_2":"","command":command_text(iqtree)})
    summary={"analysis":"Chang 2026 takaoense Read2Tree fast screen","sample_count":len(rows),"morph_counts":dict(sorted(Counter(clean(r.get("morph")).upper() for r in rows).items())),"reads_stage":reads_stage,"reference_marker_dir":str(marker_dir),"dna_reference":str(dna_reference),"output_dir":str(output_dir),"threads":threads,"read_mapper_preset":"-ax sr","primary_tree_alignment":str(dna_alignment),"tree_mode":"nucleotide; preferred here because focal samples are closely related","reference_pack_status":"validated OMA marker-pack contract required","claim_limit":"Reference-guided raw-read phylogeny is a fast topology screen. It does not test floral gene expression, identify a causal pigment locus, or distinguish introgression from ancestral polymorphism by itself."}
    return plan,summary

def write_csv(path: Path,rows: Iterable[Mapping[str,object]]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as h: w=csv.DictWriter(h,fieldnames=list(PLAN_FIELDS));w.writeheader();w.writerows(rows)
def write_shell(path: Path,plan: Sequence[Mapping[str,str]]):
    path.parent.mkdir(parents=True,exist_ok=True); lines=["#!/usr/bin/env bash","set -euo pipefail","","# Generated Read2Tree fast-screen plan.","# OMA marker pack was validated before this plan was generated.",""]; lines.extend(r["command"] for r in plan); path.write_text("\n".join(lines)+"\n",encoding="utf-8")
def parse_args():
    p=argparse.ArgumentParser();p.add_argument("--panel",type=Path,required=True);p.add_argument("--reference-manifest",type=Path,required=True);p.add_argument("--marker-contract",type=Path,required=True);p.add_argument("--reads-root",type=Path,required=True);p.add_argument("--reads-stage",choices=("trimmed","raw"),default="trimmed");p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--plan-outdir",type=Path,required=True);p.add_argument("--threads",type=int,default=8);p.add_argument("--read2tree",default="read2tree");p.add_argument("--iqtree",default="iqtree2");p.add_argument("--check-inputs",action="store_true");return p.parse_args()
def main():
    a=parse_args();rows=validate_panel(a.panel);refs=validate_reference_manifest(a.reference_manifest);contract,marker_dir,dna=load_marker_contract(a.marker_contract,refs);plan,summary=build_plan(rows,reads_root=a.reads_root,reads_stage=a.reads_stage,marker_dir=marker_dir,dna_reference=dna,output_dir=a.output_dir,executable=a.read2tree,iqtree_executable=a.iqtree,threads=a.threads)
    if a.check_inputs:
        missing=[r[f] for r in plan if r["stage"]=="2map" for f in ("read_1","read_2") if not Path(r[f]).is_file()]
        if missing: raise SystemExit("Missing required Read2Tree FASTQ inputs:\n"+"\n".join(missing))
    a.plan_outdir.mkdir(parents=True,exist_ok=True);write_csv(a.plan_outdir/"read2tree_command_plan.csv",plan);write_shell(a.plan_outdir/"run_read2tree_fast_screen.sh",plan);summary.update({"oma_reference_codes":[r["oma_code"] for r in refs],"oma_release":contract["oma_release"],"marker_count":contract["marker_count"],"marker_pack_sha256":contract["normalized_pack_sha256"],"marker_contract":str(a.marker_contract)});(a.plan_outdir/"read2tree_plan_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");print(f"samples={summary['sample_count']}");print(f"marker_count={summary['marker_count']}");return 0
if __name__=="__main__": raise SystemExit(main())
