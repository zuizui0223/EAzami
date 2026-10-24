#!/usr/bin/env python3
"""Staged real public Compositae1061 geographic bridge from 40 Japan nuclear tips.

New molecular data are not inferred from traits. The source Japan38 aligned
matrix (176 loci, 39 focal plus saff outgroup) is SHA-pinned. Five *new*
Moreyra 2025 source SRA reads (3 North America, 2 West Palearctic) are
reference-mapped onto frozen saff ortholog positions, then ML fit de novo
with IQ-TREE. This is a conservative reference-projected sensitivity tree,
NOT the final Moreyra 350-locus worldwide nuclear phylogeny. Missing base
coverage is N, never the saff reference base.

Usage:
 prepare --j38-source-dir ... --outdir ...
 consensus --bam ... --j38-source-dir ... --run ... --outdir ...
 combine --j38-source-dir ... --new-tip-dirs <dir>... --outdir ...
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, re
from collections import Counter
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

ORIGINAL_ALIGNMENT_SHA256="0ca1a0cf1f7a20e9b73f9f6929f937592da93e12846a7b6dde7899239bb004d5"
ORIGINAL_PARTITIONS_SHA256="30e6e5703a76b4065c3903c04b43179fb538d280539df66c7bf64706962a128e"
EXPECTED_LENGTH=161654
EXPECTED_LOCI=176
DNA=set("ACGTNRYKMSWBDHV")
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data/evidence/global_5taxa_comp1061_real_target_capture_bridge_v1.csv"
MIN_DEPTH=6
MIN_MAJOR_ALLELE_FRACTION=0.80
MIN_LOCUS_CONFIDENT_FRACTION=0.40
MIN_LOCUS_CONFIDENT_BP=100
MIN_ADMITTED_LOCI=70

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source(j38_dir):
    source_dir=Path(j38_dir)
    aln=source_dir/"tree_result/japan38_concat.fasta"
    parts=source_dir/"tree_result/partitions.csv"
    if sha(aln)!=ORIGINAL_ALIGNMENT_SHA256 or sha(parts)!=ORIGINAL_PARTITIONS_SHA256:
        raise ValueError("validated Japan38 176-locus source alignment or partition SHA drift")
    sequences={r.id:str(r.seq).upper() for r in SeqIO.parse(aln,"fasta")}
    if len(sequences)!=40 or "OUTGROUP_saff" not in sequences or any(len(s)!=EXPECTED_LENGTH for s in sequences.values()):
        raise ValueError("expected original 39+one outgroup 161654bp sample matrix")
    with parts.open(encoding="utf-8",newline="") as h:bounds=list(csv.DictReader(h))
    if len(bounds)!=EXPECTED_LOCI:
        raise ValueError("expected 176 original saff-rooted nuclear loci")
    pos=1
    for r in bounds:
        beg,end=int(r["start"]),int(r["end"])
        if beg!=pos or end>=EXPECTED_LENGTH+1 or end<beg:
            raise ValueError("unaligned/nonadjacent nuclear locus partitions")
        pos=end+1
    if pos-1!=EXPECTED_LENGTH:
        raise ValueError("original locus lengths do not sum to concatenation")
    return sequences,bounds

def registry():
    with REGISTRY.open(encoding="utf-8",newline="") as f:r=list(csv.DictReader(f))
    if len(r)!=5 or len({x["SRR"] for x in r})!=5 or len({x["source_taxon"] for x in r})!=5:
        raise ValueError("five frozen Moreyra taxon-SRR identity gate drift")
    return {x["SRR"]:x for x in r}

def safe_tip(record):
    return "GLB_"+record["SRR"]+"_"+record["source_taxon"].replace(" ","_")

def reference(alignments,parts):
    saff=alignments["OUTGROUP_saff"]
    out=[]
    for p in parts:
        a,b=int(p["start"])-1,int(p["end"])
        aligned=saff[a:b]
        if not aligned or any(c not in DNA|{"-"} for c in aligned):
            raise ValueError("published saff root contains unsupported alignment symbols")
        ref=aligned.replace("-","")
        # A short saff ortholog cannot support unique local mapping.
        # Preserve its original partition and mark new specimens as missing.
        if len(ref)<130:
            continue
        out.append(SeqRecord(Seq(ref),id=p["locus"],description=""))
    return out

def do_prepare(args):
    alignments,parts=source(args.j38_source_dir)
    ref=reference(alignments,parts)
    args.outdir.mkdir(parents=True,exist_ok=True)
    out=args.outdir/"reference_176_saff_Comp1061.fasta"
    SeqIO.write(ref,out,"fasta")
    receipt={"stage":"original_Japan38_rooted_nuclear_176_loci_to_mapping_reference",
        "original_40_tip_alignment_sha256":ORIGINAL_ALIGNMENT_SHA256,
        "reference_176_loci_SHA256":sha(out),"reference_loci":len(ref),
        "reference_bp":sum(len(r.seq) for r in ref),"total_aligned_length":EXPECTED_LENGTH,
        "five_moreyra_source_runs":list(registry()),
        "claim_limit":"saff coordinate-reference, not the original augmented Moreyra reference"}
    (args.outdir/"reference_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))

def do_consensus(args):
    import pysam
    alignments,parts=source(args.j38_source_dir)
    reg=registry()
    if args.run not in reg:
        raise ValueError("source SRR not in predeclared worldwide five")
    r=reg[args.run]
    expected=safe_tip(r)
    bam=pysam.AlignmentFile(str(args.bam),"rb")
    out=[]
    genewise=[]
    total_confident=0
    available_ref={r.id:str(r.seq) for r in reference(alignments,parts)}
    for record in parts:
        locus=record["locus"]
        if locus not in available_ref:
            # Keep this true source partition: insufficient saff reference
            # for a trustworthy BWA reference-aligned sample.
            original_aligned=alignments["OUTGROUP_saff"][int(record["start"])-1:int(record["end"])]
            missing_bases=len(original_aligned.replace("-",""))
            out.append(SeqRecord(Seq("N"*missing_bases),id=locus,description=""))
            genewise.append({"locus":locus,"reference_bp":missing_bases,
                "confident_bases":0,"confident_fraction":0.0,
                "mean_depth_called":0.0,"admitted":"false",
                "reason":"short_saff_reference_masked"})
            continue
        seq=available_ref[locus]
        cons=["N"]*len(seq)
        d=[]
        for col in bam.pileup(locus,0,len(seq),truncate=True,stepper="samtools",
                              min_base_quality=25,min_mapping_quality=30,
                              max_depth=20000):
            loc=col.reference_pos
            if loc<0 or loc>=len(seq):continue
            bases=[]
            for pr in col.pileups:
                seg=pr.alignment
                if pr.is_del or pr.is_refskip or pr.query_position is None:continue
                if seg.is_duplicate or seg.is_secondary or seg.is_supplementary or seg.is_qcfail:continue
                if seg.mapping_quality<30:continue
                base=seg.query_sequence[pr.query_position].upper()
                if base in "ACGT":bases.append(base)
            depth=len(bases)
            if depth<MIN_DEPTH:continue
            key,num=Counter(bases).most_common(1)[0]
            if num/depth<MIN_MAJOR_ALLELE_FRACTION:continue
            cons[loc]=key
            d.append(depth)
        confident=sum(x in "ACGT" for x in cons)
        mean_depth=sum(d)/len(d) if d else 0.0
        fraction=confident/len(cons)
        keep=confident>=MIN_LOCUS_CONFIDENT_BP and fraction>=MIN_LOCUS_CONFIDENT_FRACTION
        if not keep:
            cons=["N"]*len(cons)
        else:
            total_confident+=confident
        out.append(SeqRecord(Seq("".join(cons)),id=locus,description=""))
        genewise.append({"locus":locus,"reference_bp":len(seq),"confident_bases":confident,
                         "confident_fraction":round(fraction,6),"mean_depth_called":round(mean_depth,3),
                         "admitted":str(keep).lower(), "reason":"admitted" if keep else "low_callable_fraction_or_depth"})
    bam.close()
    admitted=[x for x in genewise if x["admitted"]=="true"]
    if len(admitted)<MIN_ADMITTED_LOCI or total_confident<20000:
        raise ValueError(f"low-confidence public source {args.run}: {len(admitted)} loci; {total_confident} confident bp")
    args.outdir.mkdir(parents=True,exist_ok=True)
    fa=args.outdir/f"{args.run}_ortholog_consensus_176.fasta"
    SeqIO.write(out,fa,"fasta")
    with (args.outdir/f"{args.run}_locus_QC.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(genewise[0]))
        w.writeheader();w.writerows(genewise)
    receipt={"stage":"public_real_SRR_reference_provisional_nuclear_consensus",
        "source_taxon":r["source_taxon"],"biosample":r["biosample"],"run":args.run,
        "tip_id":expected,"source_morphological_orientation_not_same_voucher":r["head_state_source_only"],
        "saff_frozen_reference":True,
        "n_frozen_loci":EXPECTED_LOCI,"admitted_nuclear_loci":len(admitted),
        "n_confident_nucleotide_bases":total_confident,
        "max_ortholog_QC_depth":round(max((x["mean_depth_called"] for x in genewise),default=0),2),
        "consensus_sha256":sha(fa),"min_mapping_quality":30,"min_base_quality":25,
        "min_depth":MIN_DEPTH,"min_major_allele_fraction":MIN_MAJOR_ALLELE_FRACTION,
        "locus_admitted_fraction":MIN_LOCUS_CONFIDENT_FRACTION,
        "claim_limit":"fast reference-guided SAFf ortholog consensus; strict nonambiguous major allele, masked missing/low confidence, not HybPiper homeolog/paralog-unambiguous proof"}
    (args.outdir/"consensus_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))

def do_combine(args):
    original,parts=source(args.j38_source_dir)
    wanted=set(registry())
    if len(args.new_tip_dirs)!=len(wanted):
        raise ValueError("must supply all five independent molecular source directories")
    new={}
    reports=[]
    for folder in args.new_tip_dirs:
        receipt_path=folder/"consensus_receipt.json"
        rc=json.loads(receipt_path.read_text(encoding="utf-8"))
        run=rc["run"]
        if run not in wanted or run in new or rc["source_taxon"]!=registry()[run]["source_taxon"]:
            raise ValueError("replicated/mismatched independent source in worldwide bridge")
        records={r.id:str(r.seq).upper() for r in SeqIO.parse(folder/f"{run}_ortholog_consensus_176.fasta","fasta")}
        if len(records)!=len(parts) or set(records)!={x["locus"] for x in parts}:
            raise ValueError("consensus missing or extra Compositae1061 loci")
        new[run]=records
        reports.append(rc)
    if set(new)!=wanted:
        raise ValueError("not all five exact taxon SRA source reads admitted")
    saff=original["OUTGROUP_saff"]
    combined={k:[] for k in new}
    for p in parts:
        a,b=int(p["start"])-1,int(p["end"])
        aligned=saff[a:b]
        for run,genes in new.items():
            ref=genes[p["locus"]]
            if len(ref)!=sum(x!="-" for x in aligned):
                raise ValueError("consensus length not matching reference-space ortholog")
            seq=iter(ref)
            projected="".join("-" if c=="-" else next(seq) for c in aligned)
            if len(projected)!=len(aligned):
                raise ValueError("alignment projection incorrect")
            combined[run].append(projected)
    final=dict(original)
    for run,chunks in combined.items():
        final[safe_tip(registry()[run])]="".join(chunks)
    if len(final)!=45 or len(set(final))!=len(final) or any(len(seq)!=EXPECTED_LENGTH for seq in final.values()):
        raise ValueError("45-tip true molecular worldwide pilot alignment incomplete")
    args.outdir.mkdir(parents=True,exist_ok=True)
    fasta=args.outdir/"global45_original40_plus5real_Comp1061_176loci.fasta"
    SeqIO.write([SeqRecord(Seq(seq),id=k,description="") for k,seq in sorted(final.items())],fasta,"fasta")
    report={"version":"global45_Comp1061_same_176locus_reference_projected_pilot_v1",
        "source_original_Japan38_tree_tips":40,"new_moreyra_public_target_capture_tips":5,
        "new_North_American_tips":3,"new_West_Palearctic_tips":2,
        "total_molecular_tips":len(final),"nuclear_loci":176,"alignment_bp":EXPECTED_LENGTH,
        "reference_source":"Carthamus saffroot of frozen independent Japan38 176-locus alignment",
        "original_alignment_sha256":ORIGINAL_ALIGNMENT_SHA256,
        "output_alignment_SHA256":sha(fasta),
        "original_matrix_unchanged":all(final[k]==seq for k,seq in original.items()),
        "all_new_sample_tips":[safe_tip(registry()[run]) for run in sorted(wanted)],
        "new_tip_reports":reports,
        "tree_inferred":False,
        "claim_boundary":"A reference-projected empirical multi-locus worldwide-bridge tree input; original 40-tip 176-locus alignment and five independent target-capture reads. Not accepted 294-tip, 350-locus Moreyra full phylogeny."
    }
    (args.outdir/"aligned_source_Acceptance.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"n_tips":45,"loci":176,"n_new":5,"old_matrix_exact":report["original_matrix_unchanged"]},indent=2))

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="action",required=True)
    prep=sub.add_parser("prepare");prep.add_argument("--j38-source-dir",type=Path,required=True);prep.add_argument("--outdir",type=Path,required=True)
    cons=sub.add_parser("consensus");cons.add_argument("--j38-source-dir",type=Path,required=True);cons.add_argument("--bam",type=Path,required=True);cons.add_argument("--run",required=True);cons.add_argument("--outdir",type=Path,required=True)
    comb=sub.add_parser("combine");comb.add_argument("--j38-source-dir",type=Path,required=True);comb.add_argument("--new-tip-dirs",type=Path,nargs="+",required=True);comb.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    {"prepare":do_prepare,"consensus":do_consensus,"combine":do_combine}[a.action](a)
if __name__=="__main__":main()
