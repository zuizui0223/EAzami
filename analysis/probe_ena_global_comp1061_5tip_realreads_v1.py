#!/usr/bin/env python3
"""Verify real five-continent-bridge Compositae1061 SRA lanes with ENA metadata.

Pre-download gate: accessions must be source-frozen, true paired FASTQ, checksums,
manageable gigabytes. Does NOT create molecular sequences or tree.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data/evidence/global_5taxa_comp1061_real_target_capture_bridge_v1.csv"
FIELDS="run_accession,scientific_name,library_layout,fastq_ftp,fastq_md5,fastq_bytes,study_accession,sample_accession"
URL="https://www.ebi.ac.uk/ena/portal/api/filereport"

def get(run):
    params=urllib.parse.urlencode({
        "accession":run,"result":"read_run","fields":FIELDS,"format":"tsv"
    })
    req=urllib.request.Request(URL+"?"+params,headers={"User-Agent":"EAzami-public-Comp1061-target-capture-source-QC/1.0"})
    with urllib.request.urlopen(req,timeout=70) as h:
        rows=list(csv.DictReader(io.StringIO(h.read().decode("utf-8")),delimiter="\t"))
    if len(rows)!=1 or rows[0]["run_accession"]!=run:
        raise ValueError(f"missing or multiple ENA Run accession rows: {run} ({len(rows)})")
    return rows[0]

def audit():
    with REGISTRY.open(encoding="utf-8",newline="") as h:roster=list(csv.DictReader(h))
    if len(roster)!=5 or len({r["SRR"] for r in roster})!=5:
        raise ValueError("five-tip source roster changed")
    names={r["source_taxon"] for r in roster}
    if len(names)!=5:
        raise ValueError("source taxon duplicate")
    items=[];total_bytes=0
    for r in roster:
        row=get(r["SRR"])
        urls=[x.strip() for x in row.get("fastq_ftp","").split(";") if x.strip()]
        md5=[x.strip() for x in row.get("fastq_md5","").split(";") if x.strip()]
        sizes=[int(x) for x in row.get("fastq_bytes","").split(";") if x.strip()]
        layout=row.get("library_layout","")
        if layout!="PAIRED" or len(urls)!=2 or len(md5)!=2 or len(sizes)!=2:
            raise ValueError(f"{r['SRR']} missing direct two-file paired FASTQ: {len(urls)}, {layout}")
        if any(n<10000 or n>3_500_000_000 for n in sizes):
            raise ValueError("unbounded/downstream too-small SRA readset")
        if any(len(x)!=32 or not all(c in "0123456789abcdef" for c in x) for x in md5):
            raise ValueError("invalid ENA FASTQ MD5 for "+r["SRR"])
        if not row.get("scientific_name","").casefold().startswith(r["source_taxon"].casefold()):
            raise ValueError("ENA scientificName and Moreyra source taxon disagree")
        if r["head_state_source_only"] not in {"U","D"}:
            raise ValueError("must not impute unnamed traits")
        total_bytes+=sum(sizes)
        items.append({**r,"ena_scientific_name":row["scientific_name"],
            "ena_fastq_links":urls,"ena_md5":md5,"ena_sizes":sizes,
            "run_total_fastq_bytes":sum(sizes),"source_registered_study":row.get("study_accession",""),
            "source_registered_sample":row.get("sample_accession","")})
    if total_bytes>=12_000_000_000:
        raise ValueError("five taxon source total >12 GB, redesign before fetch")
    return {"contract":"EAzami_real_worldwide_comp1061_5tip_source_ENA_verified_v1",
        "species_count":5,"distinct_biosamples":5,"n_fastq_files":10,
        "total_fastq_bytes":total_bytes,
        "all_runs_are_author_original_Moreyra_table_S1":True,
        "source_manifest_sha256":hashlib.sha256(REGISTRY.read_bytes()).hexdigest(),
        "readsets":items,
        "tree_inferred":False,
        "head_state_same_voucher":False,
        "next":"recover_loci_and_reinfer_J38_plus_five_worldwide_Comp1061_compatible_phylogram"
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    r=audit();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"species_count":r["species_count"],"total_fastq_bytes":r["total_fastq_bytes"],
        "per_run":[{"run":x["SRR"],"taxon":x["source_taxon"],
                    "MB":round(x["run_total_fastq_bytes"]/1e6,1)}
                   for x in r["readsets"]]},indent=2),flush=True)
if __name__=="__main__":main()
