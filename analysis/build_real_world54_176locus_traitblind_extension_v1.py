#!/usr/bin/env python3
"""Add nine *trait-blind* Moreyra BioSamples to completed actual world45 nuclear matrix.

Reuses original 40 Japan38 aligned 176-locus source and the genuine 45-tip
sequence matrix (SHA frozen); does NOT merge or graft previously inferred
tree topologies. All new 9 specimens are independently retrieved FASTQ, BWA
mapped and strict N-masked allele consensuses before de-novo IQ-TREE.

Four stages: prepare, fetch, consensus, combine. No head/colour is used in
selection, sequence analysis, reference mapping, rooting or tree inference.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
import urllib.request
from collections import Counter
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

import build_real_global45_comp1061_frozenJ38_bridge_v1 as original
from select_real_world45_traitblind_moreyra_next9_v1 import build as blinded_source_select

OLD45_ALIGNMENT_SHA="8759e1b10f20979fd317aa5fbf7cd448f8401e69306c1e71cd344240470b5042"
MAX_BYTES_PER_FILE=2_500_000_000
MIN_LOCUS_COVERAGE=original.MIN_LOCUS_CONFIDENT_FRACTION
MIN_LOCUS_NT=original.MIN_LOCUS_CONFIDENT_BP
MIN_ACCEPTED_LOCI=original.MIN_ADMITTED_LOCI
MIN_CONFIDENT_NT=20000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def registry():
    prior,selected=blinded_source_select(3)
    return {r["SRR"]:r for r in selected}


def safe_tip(run):
    r=registry()[run]
    return r["source_tree_tip_provisional"]


def original_source(j38_dir):
    alignment,partitions=original.source(j38_dir)
    refs=original.reference(alignment,partitions)
    if len(refs)!=174:
        raise ValueError("unexpected frozen original saff reference locus count")
    return alignment,partitions,refs


def do_prepare(args):
    alignment,partitions,refs=original_source(args.j38_source_dir)
    args.outdir.mkdir(parents=True,exist_ok=True)
    fa=args.outdir/"reference_174_saff_source_loci.fasta"
    SeqIO.write(refs,fa,"fasta")
    report={
        "version":"source_world54_true_176_comp1061_original40_reference_v1",
        "original40_alignment_sha":original.ORIGINAL_ALIGNMENT_SHA256,
        "n_original_loci":176,
        "n_mappable_original_saff_loci":174,
        "reference_SHA256":sha(fa),
        "new_source_SRRs":list(registry()),
        "source_morphology_selection_used":False,
    }
    (args.outdir/"source_reference.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"reference_loci":len(refs),"new_source_SRRs":list(registry())}))


def do_fetch(args):
    r=registry().get(args.run)
    if r is None:
        raise ValueError("not a source-frozen nine-trait-blind original Moreyra run")
    source=json.loads(args.ena_receipt.read_text(encoding="utf-8"))
    matches=[x for x in source["source_reads"] if x["SRR"]==args.run]
    if len(matches)!=1:
        raise ValueError("ENA source verification receipt missing exact run")
    item=matches[0]
    if item["biosample"]!=r["biosample"] or item["taxon_source_label"]!=r["taxon_source_label"]:
        raise ValueError("source blind selection drift vs ENA published metadata")
    args.outdir.mkdir(parents=True,exist_ok=True)
    digests=[]
    for i,(url,expected_md5,length) in enumerate(zip(
            item["ENA_fastq_URLS"],item["ENA_fastq_MD5"],item["ENA_fastq_bytes"]),1):
        if not url.startswith("ftp.sra.ebi.ac.uk/") or length>MAX_BYTES_PER_FILE:
            raise ValueError("non approved ENA read endpoint or oversized source file")
        path=args.outdir/f"R{i}.fastq.gz"
        target="https://"+url
        for attempt in range(3):
            try:
                digest=hashlib.md5()
                request=urllib.request.Request(target,headers={
                    "User-Agent":"EAzami-world54-traitblind-Moreyra-source-read-analysis/1.0"})
                with urllib.request.urlopen(request,timeout=130) as data,path.open("wb") as out:
                    while True:
                        buf=data.read(2*1024*1024)
                        if not buf:break
                        out.write(buf)
                        digest.update(buf)
                if path.stat().st_size!=length or digest.hexdigest()!=expected_md5:
                    raise ValueError("source-run real FASTQ content changed from published MD5")
                digests.append(digest.hexdigest())
                break
            except Exception as exc:
                if path.exists():path.unlink()
                if attempt>=2:
                    raise
                print("READ_SOURCE_RETRY",args.run,i,attempt,str(exc),flush=True)
                time.sleep(3+4*attempt)
        print("SOURCE_REAL_FASTQ_MD5_OK",args.run,i,round(length/1e6,2),"MB",flush=True)
    if len(digests)!=2:raise ValueError("expected exactly two original paired FASTQs")
    (args.outdir/"frozen_source_read_MD5_QC.json").write_text(json.dumps({
        "source_SRR":args.run,"source_biosample":r["biosample"],
        "source_taxon":r["taxon_source_label"],
        "paired_fastq_verified_md5":digests,"source_trait_used_to_choose_sample":False,
    },indent=2)+"\n")


def do_consensus(args):
    import pysam
    if args.run not in registry():
        raise ValueError("run accession not in frozen trait-blind source cohort")
    original40,parts,refs=original_source(args.j38_source_dir)
    source_by_locus={r.id:str(r.seq) for r in refs}
    output=[]
    QC=[]
    confident_total=0
    bam=pysam.AlignmentFile(str(args.bam),"rb")
    for p in parts:
        locus=p["locus"]
        if locus not in source_by_locus:
            orig=original40["OUTGROUP_saff"][int(p["start"])-1:int(p["end"])]
            output.append(SeqRecord(Seq("N"*len(orig.replace("-",""))),id=locus,description=""))
            QC.append({"locus":locus,"source_ortholog_bp":len(orig.replace("-","")),
                       "confident_bp":0,"confidence_fraction":0.,
                       "admitted":"false","reason":"short_outgroup_reference_locus_missing"})
            continue
        seq=source_by_locus[locus]
        consensus=["N"]*len(seq)
        for col in bam.pileup(locus,0,len(seq),truncate=True,stepper="samtools",
                              min_base_quality=25,min_mapping_quality=30,
                              max_depth=20000):
            pos=col.reference_pos
            if pos<0 or pos>=len(seq):continue
            basecalls=[]
            for read in col.pileups:
                if read.is_del or read.is_refskip or read.query_position is None:continue
                align=read.alignment
                if align.is_duplicate or align.is_secondary or align.is_supplementary or align.is_qcfail:
                    continue
                if align.mapping_quality<30:continue
                base=align.query_sequence[read.query_position].upper()
                if base in "ACGT":basecalls.append(base)
            if len(basecalls)<original.MIN_DEPTH:continue
            nucleotide,n=max(Counter(basecalls).items(),key=lambda p:p[1])
            if n/len(basecalls)>=original.MIN_MAJOR_ALLELE_FRACTION:
                consensus[pos]=nucleotide
        known=sum(c in "ACGT" for c in consensus)
        admit=(known>=MIN_LOCUS_NT and known/len(seq)>=MIN_LOCUS_COVERAGE)
        if not admit:
            consensus=["N"]*len(consensus)
        else:
            confident_total+=known
        output.append(SeqRecord(Seq("".join(consensus)),id=locus,description=""))
        QC.append({"locus":locus,"source_ortholog_bp":len(seq),
                   "confident_bp":known,"confidence_fraction":round(known/len(seq),5),
                   "admitted":str(admit).lower(),"reason":"eligible" if admit else "low_coverage_masked"})
    bam.close()
    admitted=sum(r["admitted"]=="true" for r in QC)
    args.outdir.mkdir(parents=True,exist_ok=True)
    fa=args.outdir/f"{args.run}_176orthologs_masked.fa"
    SeqIO.write(output,fa,"fasta")
    with (args.outdir/f"{args.run}_QC_per_locus.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(QC[0]))
        writer.writeheader();writer.writerows(QC)
    row=registry()[args.run]
    result={
        "run":args.run,"tip_id":safe_tip(args.run),"source_taxon_label":row["taxon_source_label"],
        "biosample":row["biosample"],"source_region":row["source_region"],
        "n_original_loci":176,"n_admitted_loci":admitted,
        "called_bp":confident_total,"source_locus_alignment_SHA256":sha(fa),
        "nuclear_source_trait_blind":True,
        "reference_mapping_source":"unchanged original Japan38 40-tip saff locus alignment",
        "minimum_locus_confident_fraction":MIN_LOCUS_COVERAGE,
        "minimum_called_bp":MIN_CONFIDENT_NT,
        "passes_strict_source_QC":(admitted>=MIN_ACCEPTED_LOCI and confident_total>=MIN_CONFIDENT_NT),
        "head_colour_not_observed_same_sequenced_individual":True,
    }
    (args.outdir/"consensus_QC.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2),flush=True)
    if not result["passes_strict_source_QC"]:
        raise ValueError("new source specimen failed predeclared real nuclear strict locus QC")


def do_combine(args):
    original40,parts,_=original_source(args.j38_source_dir)
    source45_path=args.original45_dir/"global45_original40_plus5real_Comp1061_176loci.fasta"
    if sha(source45_path)!=OLD45_ALIGNMENT_SHA:
        raise ValueError("source 45-tip full real nucleotide alignment is no longer original")
    source45={r.id:str(r.seq).upper() for r in SeqIO.parse(source45_path,"fasta")}
    if len(source45)!=45 or any(source45[k]!=original40[k] for k in original40):
        raise ValueError("baseline 45-tip source molecular sequence no longer contains preserved original 40")
    previous_loci={p["locus"] for p in parts}
    added={}
    audited=[]
    for d in args.new_consensus_dirs:
        receipt=json.loads((d/"consensus_QC.json").read_text(encoding="utf-8"))
        run=receipt["run"]
        if run not in registry() or run in added or not receipt["passes_strict_source_QC"]:
            raise ValueError("missing/duplicate/failed source selection in final phylogenetic combination")
        seqs={r.id:str(r.seq).upper() for r in SeqIO.parse(d/f"{run}_176orthologs_masked.fa","fasta")}
        if len(seqs)!=176 or set(seqs)!=previous_loci:
            raise ValueError("source specimen does not have exactly all original source locus labels")
        added[run]=seqs
        audited.append(receipt)
    if set(added)!=set(registry()) or len(added)!=9:
        raise ValueError("all nine prespecified region-stratified original S1 BioSamples required for 54-tip tree")
    saff=original40["OUTGROUP_saff"]
    novel={}
    for run,seqs in added.items():
        seq_chunks=[]
        for part in parts:
            a,b=int(part["start"])-1,int(part["end"])
            aligned=saff[a:b]
            gene=seqs[part["locus"]]
            if len(gene)!=len(aligned.replace("-","")):
                raise ValueError("nuclear consensus length differs from original source gene reference")
            it=iter(gene)
            seq_chunks.append("".join("-" if c=="-" else next(it) for c in aligned))
        complete="".join(seq_chunks)
        if len(complete)!=original.EXPECTED_LENGTH or any(c not in original.DNA|{"-"} for c in complete):
            raise ValueError("invalid nucleotide character or alignment length in new sample")
        novel[safe_tip(run)]=complete
    if set(source45)&set(novel):
        raise ValueError("new sample tip accidentally duplicates original 45-tip nuclear sample")
    combined={**source45,**novel}
    if len(combined)!=54 or len(set(combined))!=54:
        raise ValueError("unexpected real source 54-tip count")
    args.outdir.mkdir(parents=True,exist_ok=True)
    f=args.outdir/"real_world54_176Comp1061_traitblind_9added.fasta"
    SeqIO.write([SeqRecord(Seq(s),id=tip,description="") for tip,s in sorted(combined.items())],f,"fasta")
    result={
        "version":"real_world54_176Comp1061_original45_plus9_traitblind_source_alignment_v1",
        "original_45tip_matrix_SHA256":OLD45_ALIGNMENT_SHA,
        "original_Japan38_39_and_Carthamus_sequences_unchanged":True,
        "all_45_current_sequences_frozen":all(combined[k]==source45[k] for k in source45),
        "n_total_tips":54,"n_original_tips":45,"n_new_independent_BioSamples":9,
        "source_moreyra_2025_S1_genetic_voucher_runs":sorted(added),
        "loci_original":176,"alignment_length_bp":original.EXPECTED_LENGTH,
        "new9_summarized_QC":audited,
        "original45_alignment_SHA256":OLD45_ALIGNMENT_SHA,
        "new54_alignment_SHA256":sha(f),
        "tree_not_yet_inferred":True,
        "external_phenotypes_not_consulted":True,
        "not_complete_Moreyra_294tip_350gene_tree":True
    }
    (args.outdir/"source_nuclear54_alignment_QC.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"actual_biological_tips":54,"new_source_tips":9,
                      "nuclear_loci":176,"source_sequence_sha":result["new54_alignment_SHA256"]},indent=2))


def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="action",required=True)
    a=sub.add_parser("prepare")
    a.add_argument("--j38-source-dir",type=Path,required=True)
    a.add_argument("--outdir",type=Path,required=True)
    a=sub.add_parser("fetch")
    a.add_argument("--run",required=True)
    a.add_argument("--ena-receipt",type=Path,required=True)
    a.add_argument("--outdir",type=Path,required=True)
    a=sub.add_parser("consensus")
    a.add_argument("--run",required=True)
    a.add_argument("--j38-source-dir",type=Path,required=True)
    a.add_argument("--bam",type=Path,required=True)
    a.add_argument("--outdir",type=Path,required=True)
    a=sub.add_parser("combine")
    a.add_argument("--j38-source-dir",type=Path,required=True)
    a.add_argument("--original45-dir",type=Path,required=True)
    a.add_argument("--new-consensus-dirs",type=Path,nargs="+",required=True)
    a.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    {"prepare":do_prepare,"fetch":do_fetch,"consensus":do_consensus,"combine":do_combine}[args.action](args)

if __name__=="__main__":
    main()
