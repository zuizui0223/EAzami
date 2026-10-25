#!/usr/bin/env python3
"""Construct world53 from the EIGHT empirically admitted new Moreyra BioSamples.

An originally preselected ninth source accession, SRR30887183 Cirsium fargesii,
failed the FROZEN 70-locus minimum with only 63/176 admitted source loci.
Do not lower thresholds or silently resample taxa after observing QC. Preserve
the source45 nuclear matrix and all allele-masked quality-passing original
consensuses unchanged, then re-infer an UNCONSTRAINED 53-tip nuclear tree.

All original missing positions are N or original source gaps. The tree is a
reference-guided preliminary 176-locus geography-first worldwide bridge, not
the unexecuted original Moreyra 350-locus world species tree.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

import build_real_world54_176locus_traitblind_extension_v1 as src54
import build_real_global45_comp1061_frozenJ38_bridge_v1 as src45

FAILED_SRR = "SRR30887183"
FAILED_SOURCE = "Cirsium fargesii"
FAILED_BIOSAMPLE = "SAMN44017847"
FAILED_ADMITTED_LOCI = 63
PREDECLARED_MINIMUM_ADMITTED_LOCI = 70
ORIGINAL_SOURCE_RUN = 40116044634
EXPECTED_NEW = 8
EXPECTED_TOTAL = 53
OUT_FASTA = "real_world53_176Comp1061_QC8_geography_first.fasta"


def build(*, j38_dir:Path, world45_dir:Path, source_dirs:list[Path], outdir:Path):
    prior, selection = src54.blinded_source_select(3)
    roster = {row["SRR"]:row for row in selection}
    if len(roster)!=9 or FAILED_SRR not in roster:
        raise ValueError("predeclared nine sample cohort changed; new version required")
    excluded = roster[FAILED_SRR]
    if excluded["taxon_source_label"]!=FAILED_SOURCE or excluded["biosample"]!=FAILED_BIOSAMPLE:
        raise ValueError("failed biological specimen ID mismatches original sample")
    source40,parts,_=src54.original_source(j38_dir)
    input45=world45_dir/"global45_original40_plus5real_Comp1061_176loci.fasta"
    if src54.sha(input45)!=src54.OLD45_ALIGNMENT_SHA:
        raise ValueError("previous accepted empirical 45-tip alignment SHA256 mismatch")
    old={r.id:str(r.seq).upper() for r in SeqIO.parse(input45,"fasta")}
    if len(old)!=45 or any(old.get(k)!=v for k,v in source40.items()):
        raise ValueError("original 45 nuclear alignment altered or original Japan38 40 tips lost")
    source_refs={p["locus"] for p in parts}
    chosen={}
    audits=[]
    for d in source_dirs:
        metadata=d/"consensus_QC.json"
        if not metadata.is_file():
            raise ValueError("success artifact lacks real source QC receipt: "+str(d))
        rec=json.loads(metadata.read_text(encoding="utf-8"))
        run=rec.get("run")
        if run not in roster or run==FAILED_SRR or run in chosen:
            raise ValueError("unexpected or failed source accession in QC-admitted group: "+str(run))
        original=roster[run]
        if rec["biosample"]!=original["biosample"] or rec["source_taxon_label"]!=original["taxon_source_label"]:
            raise ValueError("original S1 nuclear specimen differs from the frozen source manifest")
        if (rec["passes_strict_source_QC"] is not True or
            rec["n_admitted_loci"]<PREDECLARED_MINIMUM_ADMITTED_LOCI or
            rec["called_bp"]<src54.MIN_CONFIDENT_NT):
            raise ValueError("failed QC specimen cannot enter world53 nuclear tree")
        if rec["nuclear_source_trait_blind"] is not True:
            raise ValueError("source molecular accession selection was not trait blind")
        fa=d/f"{run}_176orthologs_masked.fa"
        if src54.sha(fa)!=rec["source_locus_alignment_SHA256"]:
            raise ValueError("genuine molecular source recovered consensus checksum mismatch")
        rows={r.id:str(r.seq).upper() for r in SeqIO.parse(fa,"fasta")}
        if len(rows)!=176 or set(rows)!=source_refs:
            raise ValueError("recovered FASTA not the unchanged original 176 Comp1061 locus universe")
        chosen[run]=rows
        audits.append(rec)
    expected=set(roster)-{FAILED_SRR}
    if set(chosen)!=expected or len(source_dirs)!=EXPECTED_NEW:
        raise ValueError("not exactly eight prespecified original specimens passed frozen QC")
    saff=source40["OUTGROUP_saff"]
    new={}
    for run,loci in sorted(chosen.items()):
        aligned_parts=[]
        for p in parts:
            left,right=int(p["start"])-1,int(p["end"])
            ref_aligned=saff[left:right]
            source_gene=loci[p["locus"]]
            if len(source_gene)!=sum(c!="-" for c in ref_aligned):
                raise ValueError("masked genuine source locus has invalid alignment coordinate length: "+p["locus"])
            r=iter(source_gene)
            projected="".join("-" if c=="-" else next(r) for c in ref_aligned)
            aligned_parts.append(projected)
        complete="".join(aligned_parts)
        if len(complete)!=src45.EXPECTED_LENGTH or any(c not in src45.DNA|{"-"} for c in complete):
            raise ValueError("assembled eight-source nuclear sequence length/alphabet invalid")
        new[src54.safe_tip(run)]=complete
    if set(old)&set(new):
        raise ValueError("biological sample repeated in original 45 nuclear source roster")
    combined={**old,**new}
    if len(combined)!=EXPECTED_TOTAL or any(len(v)!=src45.EXPECTED_LENGTH for v in combined.values()):
        raise ValueError("nuclear tree molecular sample count/length incorrect")
    outdir.mkdir(parents=True,exist_ok=True)
    fasta=outdir/OUT_FASTA
    SeqIO.write([SeqRecord(Seq(v),id=k,description="") for k,v in sorted(combined.items())],fasta,"fasta")
    source_region_counts={}
    for area in ("North_America","West_Palearctic","Continental_East_Central_Asia"):
        source_region_counts[area]=sum(roster[x]["source_region"]==area for x in chosen)
    if source_region_counts!={"North_America":3,"West_Palearctic":3,"Continental_East_Central_Asia":2}:
        raise ValueError("source region counts changed after predeclared QC exclusion")
    contract={
        "version":"real_world53_original45_plus_8_traitblind_moreyra_source_QC_v1",
        "source_full_predeclared_nine_BioSamples":9,
        "source_original_selection_seed":prior["seed"],
        "source_original_full_spectrum_9_selected_before_observing_U_D_or_colour":True,
        "source_initial_9_sample_workflow_run":ORIGINAL_SOURCE_RUN,
        "excluded_failed_source_specimen":{
            "SRR":FAILED_SRR,
            "taxon":FAILED_SOURCE,
            "biosample":FAILED_BIOSAMPLE,
            "frozen_minimum_loci":PREDECLARED_MINIMUM_ADMITTED_LOCI,
            "observed_admitted_loci":FAILED_ADMITTED_LOCI,
            "observed_confident_bases":25840,
            "reason":"63 < 70 unchanged predeclared source admission threshold",
            "phenotype_consulted_before_exclusion":False,
        },
        "n_original_source_molecular_tips":45,
        "n_newly_recovered_source_tips":EXPECTED_NEW,
        "n_total_real_molecular_tips":EXPECTED_TOTAL,
        "new_source_region_counts":source_region_counts,
        "new_source_coverage":[{
            "run":r["run"],"taxon":r["source_taxon_label"],"region":r["source_region"],
            "n_loci":r["n_admitted_loci"],"called_bp":r["called_bp"],
            "source_consensus_SHA256":r["source_locus_alignment_SHA256"]
        } for r in sorted(audits,key=lambda x:x["run"])],
        "original_45_alignment_sha256":src54.OLD45_ALIGNMENT_SHA,
        "source_original_45_tip_sequences_exactly_unchanged":all(combined[k]==v for k,v in old.items()),
        "original_nuclear_loci":len(parts),
        "source_alignment_bp":src45.EXPECTED_LENGTH,
        "new_53_alignment_sha256":src54.sha(fasta),
        "nuclear_tree_estimated":False,
        "claimed_full_294_tip_350_locus_moreyra_phylogeny":False,
        "orientation_colour_trait_consulted_for_tree_inference":False,
        "sample_grain_caveat":"53 molecular individual tips, NOT 53 accepted biological species. Includes population-level/variety duplication.",
    }
    (outdir/"real_world53_source_QC_receipt.json").write_text(
        json.dumps(contract,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"real_molecular_tips":53,"original_loci":176,
        "new_source_samples":8,"excluded_low_coverage_run":FAILED_SRR,
        "new_alignment_sha256":contract["new_53_alignment_sha256"],
        "source_region_counts":source_region_counts},indent=2),flush=True)
    return contract


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--j38-source-dir",type=Path,required=True)
    p.add_argument("--original45-dir",type=Path,required=True)
    p.add_argument("--new-consensus-dirs",type=Path,nargs="+",required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    build(j38_dir=a.j38_source_dir,world45_dir=a.original45_dir,
          source_dirs=a.new_consensus_dirs,outdir=a.outdir)


if __name__=="__main__":
    main()
