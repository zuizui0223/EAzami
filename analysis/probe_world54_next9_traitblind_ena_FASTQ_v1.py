#!/usr/bin/env python3
"""Check source-frozen, morphology-blind nine Moreyra nuclear SRRs against ENA FASTQ.

This stage checks actual source run layout, URLs, MD5, bytes and source species
names. It does NOT alter the region-stratified pre-phenotype random draw.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

from select_real_world45_traitblind_moreyra_next9_v1 import build

API="https://www.ebi.ac.uk/ena/portal/api/filereport"
FIELDS="run_accession,scientific_name,library_layout,fastq_ftp,fastq_md5,fastq_bytes,study_accession,sample_accession"


def fetch(run):
    params=urllib.parse.urlencode({
        "accession":run, "result":"read_run", "fields":FIELDS, "format":"tsv"
    })
    req=urllib.request.Request(API+"?"+params,headers={
        "User-Agent":"EAzami-blind-world54-public-Comp1061-run-QC/1.0"})
    with urllib.request.urlopen(req,timeout=65) as h:
        records=list(csv.DictReader(io.StringIO(h.read().decode("utf-8")),delimiter="\t"))
    if len(records)!=1 or records[0]["run_accession"]!=run:
        raise ValueError(f"ENA response missing/ambiguous for frozen accession {run}")
    return records[0]


def audit():
    original,panel=build(3)
    verified=[];total=0
    for r in panel:
        ena=fetch(r["SRR"])
        u=[x.strip() for x in ena["fastq_ftp"].split(";") if x.strip()]
        d=[x.strip() for x in ena["fastq_md5"].split(";") if x.strip()]
        n=[int(x) for x in ena["fastq_bytes"].split(";") if x.strip()]
        if ena["library_layout"]!="PAIRED" or len(u)!=len(d) or len(d)!=len(n) or len(n)!=2:
            raise ValueError("selected molecular SRA not directly retrievable as two original paired FASTQs: "+r["SRR"])
        if any(not x.startswith("ftp.sra.ebi.ac.uk/") for x in u):
            raise ValueError("ENA read not hosted on original trusted FTP/HTTPS SRA endpoint")
        if any(len(x)!=32 or not all(c in "0123456789abcdef" for c in x) for x in d):
            raise ValueError("ENA FASTQ MD5 malformed")
        if any(x<=1000 for x in n):
            raise ValueError("published FASTQ is empty or too small")
        if not ena["scientific_name"].casefold().startswith(r["taxon_source_label"].casefold()):
            raise ValueError("source submitted ENA scientific name does not match frozen original taxon: "+r["SRR"])
        if ena["sample_accession"].strip() not in {r["biosample"],""}:
            raise ValueError("published source BioSample accession conflicts with original S1")
        row={**r,"ENA_scientific_name":ena["scientific_name"],
            "ENA_sample_accession":ena["sample_accession"],"ENA_study_accession":ena["study_accession"],
            "ENA_fastq_URLS":u,"ENA_fastq_MD5":d,"ENA_fastq_bytes":n,
            "total_download_bytes":sum(n),
            "source_orientation_and_colour_not_consulted":True}
        total+=sum(n)
        verified.append(row)
        print(json.dumps({"SRR":r["SRR"],"taxon":r["taxon_source_label"],
               "area":r["source_region"],"size_MB":round(sum(n)/1e6,2)}),flush=True)
    receipt={
        "version":"real_world54_blind_source_9_ENA_QC_v1",
        "parent_traitblind_selection_seed":original["seed"],
        "n_molecular_individuals":len(verified),
        "n_read_files":len(verified)*2,
        "total_download_bytes":total,
        "source_phenotype_used_for_admission":False,
        "all_paired_run_biosamples_crosschecked_with_original_Moreyra_S1":True,
        "all_public_FASTQ_MD5_source_frozen":True,
        "source_reads":verified,
        "gene_tree_inferred":False,
        "global54_cirsium_phylogram_inferred":False
    }
    return receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"total_MB":round(result["total_download_bytes"]/1e6,1),
                      "n":result["n_molecular_individuals"]},indent=2))


if __name__=="__main__":
    main()
