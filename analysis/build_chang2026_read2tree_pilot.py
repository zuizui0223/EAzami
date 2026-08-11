#!/usr/bin/env python3
"""Build an assembly-free Read2Tree fast-screen plan for the six Chang 2026
Cirsium japonicum var. takaoense RNA-seq samples.

This layer is a topology sensitivity screen. It does not replace the
Trinity/OrthoFinder workflow and it must not be interpreted as evidence for
functional anthocyanin reactivation or as a test of introgression.
"""
from __future__ import annotations
import argparse, csv, json, shlex
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_SAMPLE_COUNT = 6
EXPECTED_MORPHS = {"BP": 3, "W": 3}
PLAN_FIELDS = ("stage","sample_id","run","morph","read_1","read_2","command")

def clean(value: object) -> str:
    return str(value or "").strip()

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(handle)]

def validate_panel(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    if len(rows) != EXPECTED_SAMPLE_COUNT:
        raise ValueError(f"Expected {EXPECTED_SAMPLE_COUNT} focal samples, observed {len(rows)}")
    sample_ids = [clean(r.get("sample_id")) for r in rows]
    runs = [clean(r.get("matched_run")) for r in rows]
    if any(not x for x in sample_ids + runs):
        raise ValueError("Each focal row must have sample_id and matched_run")
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Focal sample_id values are not unique")
    if len(runs) != len(set(runs)):
        raise ValueError("Focal SRA runs are not unique")
    if any(clean(r.get("library_layout")).upper() != "PAIRED" for r in rows):
        raise ValueError("Read2Tree pilot currently requires official PAIRED runs")
    if any(clean(r.get("panel_role")) != "focal_colour_morph" for r in rows):
        raise ValueError("Pilot may contain only focal_colour_morph rows")
    morphs = Counter(clean(r.get("morph")).upper() for r in rows)
    if dict(morphs) != EXPECTED_MORPHS:
        raise ValueError(f"Expected 3 BP and 3 W samples, observed {dict(morphs)}")
    return sorted(rows, key=lambda r: r["sample_id"])

def read_paths(row: Mapping[str, str], reads_root: Path, stage: str) -> tuple[Path, Path]:
    sid, run = clean(row.get("sample_id")), clean(row.get("matched_run"))
    if stage == "trimmed":
        base = reads_root / "samples" / sid / "trimmed"
        return base / f"{sid}.R1.trim.fastq.gz", base / f"{sid}.R2.trim.fastq.gz"
    if stage == "raw":
        base = reads_root / "samples" / sid / "raw"
        return base / f"{run}_1.fastq.gz", base / f"{run}_2.fastq.gz"
    raise ValueError(f"Unsupported reads stage: {stage}")

def command_text(parts: Sequence[object]) -> str:
    return shlex.join([str(p) for p in parts])

def build_plan(rows: Sequence[Mapping[str, str]], *, reads_root: Path, reads_stage: str,
               marker_dir: Path, dna_reference: Path, output_dir: Path,
               executable: str="read2tree", iqtree_executable: str="iqtree2",
               threads: int=8) -> tuple[list[dict[str, str]], dict[str, object]]:
    if threads < 1:
        raise ValueError("threads must be >=1")
    plan: list[dict[str, str]] = []
    step1 = [executable,"--step","1marker","--standalone_path",marker_dir,
             "--dna_reference",dna_reference,"--output_path",output_dir,"--debug","--threads",threads]
    plan.append({"stage":"1marker","sample_id":"","run":"","morph":"","read_1":"","read_2":"","command":command_text(step1)})
    for row in rows:
        sid, run, morph = clean(row.get("sample_id")), clean(row.get("matched_run")), clean(row.get("morph")).upper()
        r1, r2 = read_paths(row, reads_root, reads_stage)
        step2 = [executable,"--step","2map","--standalone_path",marker_dir,
                 "--dna_reference",dna_reference,"--reads",r1,r2,"--species_name",sid,
                 "--read_type","-ax sr","--output_path",output_dir,"--debug","--threads",threads]
        plan.append({"stage":"2map","sample_id":sid,"run":run,"morph":morph,
                     "read_1":str(r1),"read_2":str(r2),"command":command_text(step2)})
    step3 = [executable,"--step","3combine","--standalone_path",marker_dir,
             "--dna_reference",dna_reference,"--output_path",output_dir,"--debug","--threads",threads]
    plan.append({"stage":"3combine","sample_id":"","run":"","morph":"","read_1":"","read_2":"","command":command_text(step3)})
    dna_alignment = output_dir / "concat_merge_dna.phy"
    iqtree = [iqtree_executable,"-s",dna_alignment,"-m","MFP","-B","1000","--alrt","1000","-T","AUTO",
              "--prefix",output_dir/"takaoense6_read2tree_dna"]
    plan.append({"stage":"dna_tree","sample_id":"","run":"","morph":"","read_1":"","read_2":"","command":command_text(iqtree)})
    summary = {
        "analysis":"Chang 2026 takaoense Read2Tree fast screen",
        "sample_count":len(rows),
        "morph_counts":dict(sorted(Counter(clean(r.get("morph")).upper() for r in rows).items())),
        "reads_stage":reads_stage,
        "reference_marker_dir":str(marker_dir),
        "dna_reference":str(dna_reference),
        "output_dir":str(output_dir),
        "threads":threads,
        "read_mapper_preset":"-ax sr",
        "primary_tree_alignment":str(dna_alignment),
        "tree_mode":"nucleotide; preferred here because focal samples are closely related",
        "reference_pack_status":"must be prepared separately from source-backed OMA marker export",
        "claim_limit":"Reference-guided raw-read phylogeny is a fast topology screen. It does not test floral gene expression, identify a causal pigment locus, or distinguish introgression from ancestral polymorphism by itself."
    }
    return plan, summary

def validate_reference_manifest(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError("Reference manifest is empty")
    required = {"oma_code","scientific_name","reference_role","verified_in_oma"}
    if not required.issubset(rows[0]):
        raise ValueError(f"Reference manifest lacks required columns: {sorted(required)}")
    if any(clean(r.get("verified_in_oma")).lower() != "true" for r in rows):
        raise ValueError("All configured OMA reference genomes must be independently verified")
    codes = [clean(r.get("oma_code")) for r in rows]
    if len(codes) != len(set(codes)):
        raise ValueError("OMA reference codes are not unique")
    return rows

def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PLAN_FIELDS)); writer.writeheader(); writer.writerows(rows)

def write_shell(path: Path, plan: Sequence[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#!/usr/bin/env bash","set -euo pipefail","","# Generated Read2Tree fast-screen plan.","# Marker pack and FASTQ paths must exist before execution.",""]
    lines.extend(r["command"] for r in plan)
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")

def parse_args() -> argparse.Namespace:
    p=argparse.ArgumentParser(); p.add_argument("--panel",type=Path,required=True); p.add_argument("--reference-manifest",type=Path,required=True)
    p.add_argument("--reads-root",type=Path,required=True); p.add_argument("--reads-stage",choices=("trimmed","raw"),default="trimmed")
    p.add_argument("--marker-dir",type=Path,required=True); p.add_argument("--dna-reference",type=Path,required=True); p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--plan-outdir",type=Path,required=True); p.add_argument("--threads",type=int,default=8); p.add_argument("--read2tree",default="read2tree"); p.add_argument("--iqtree",default="iqtree2"); p.add_argument("--check-inputs",action="store_true"); return p.parse_args()

def main() -> int:
    a=parse_args(); rows=validate_panel(a.panel); refs=validate_reference_manifest(a.reference_manifest)
    plan, summary = build_plan(rows, reads_root=a.reads_root, reads_stage=a.reads_stage, marker_dir=a.marker_dir, dna_reference=a.dna_reference, output_dir=a.output_dir, executable=a.read2tree, iqtree_executable=a.iqtree, threads=a.threads)
    if a.check_inputs:
        missing=[]
        if not a.marker_dir.is_dir(): missing.append(str(a.marker_dir))
        if not a.dna_reference.is_file(): missing.append(str(a.dna_reference))
        for r in plan:
            if r["stage"]=="2map":
                for f in ("read_1","read_2"):
                    if not Path(r[f]).is_file(): missing.append(r[f])
        if missing: raise SystemExit("Missing required Read2Tree inputs:\n"+"\n".join(missing))
    a.plan_outdir.mkdir(parents=True, exist_ok=True); write_csv(a.plan_outdir/"read2tree_command_plan.csv", plan); write_shell(a.plan_outdir/"run_read2tree_fast_screen.sh", plan)
    summary["oma_reference_codes"]=[r["oma_code"] for r in refs]
    (a.plan_outdir/"read2tree_plan_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"samples={summary['sample_count']}"); print("morph_counts="+json.dumps(summary["morph_counts"],sort_keys=True)); print("oma_reference_codes="+"|".join(summary["oma_reference_codes"])); return 0

if __name__ == "__main__": raise SystemExit(main())
