#!/usr/bin/env python3
"""Derive a morphology-blind high-occupancy nuclear locus sensitivity from real world53.

Keep a WHOLE original Compositae1061 locus only if every one of the 13
molecular source specimens sampled outside Japan (6 NA / 5 Western
Palearctic / 2 continental East-Central Asia) has >=40% unambiguous
ACGT source characters across the original aligned locus. Do not inspect
U/D, colour, climate, tree topology or base variation to select loci.
Uncovered alleles remain N; full source genetic panel 53-tip, 176-locus
is not replaced by the smaller data conditioning sensitivity.
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

FULL_ALIGNMENT_SHA="9179394190a3ab499a122439bca9c8bbe74e205a315440e4f7442b5ee225b237"
ORIGINAL_PARTITIONS_SHA="30e6e5703a76b4065c3903c04b43179fb538d280539df66c7bf64706962a128e"
THRESHOLD=0.40
NA=(
    "GLB_SRR30887153_Cirsium_ownbeyi",
    "GLB_SRR30887180_Cirsium_flodmanii",
    "GLB_SRR30887231_Cirsium_vinaceum",
    "GLB2_SRR25265683_Cirsium_mohavense",
    "GLB2_SRR25265699_Cirsium_hesperium",
    "GLB2_SRR25265707_Cirsium_fontinale_var._campylon",
)
WEST=(
    "GLB_SRR30887156_Cirsium_oleraceum",
    "GLB_SRR30887186_Cirsium_erisithales",
    "GLB2_SRR25265555_Cirsium_arvense",
    "GLB2_SRR30887218_Cirsium_brachycephalum",
    "GLB2_SRR30887242_Cirsium_leucocephalum",
)
ASIA=(
    "GLB2_SRR25265705_Cirsium_fanjingshanense",
    "GLB2_SRR30887251_Cirsium_kamtschaticum",
)
OUTSIDE=NA+WEST+ASIA


def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(alignment:Path, partitions:Path, out:Path):
    if digest(alignment)!=FULL_ALIGNMENT_SHA or digest(partitions)!=ORIGINAL_PARTITIONS_SHA:
        raise ValueError("source 53-tip nucleotides or original 176 gene partitions changed")
    records=list(SeqIO.parse(alignment,"fasta"))
    seq={r.id:str(r.seq).upper() for r in records}
    if len(seq)!=len(records) or len(seq)!=53 or "OUTGROUP_saff" not in seq:
        raise ValueError("source molecular sample identity mismatch")
    if len({x for x in seq if x.startswith("GLB")})!=13 or set(OUTSIDE)!={x for x in seq if x.startswith("GLB")}:
        raise ValueError("all original 6 North America, 5 western, 2 continental Asia specimen labels required")
    if {len(s) for s in seq.values()}!={161654}:
        raise ValueError("source 53-tip alignment length drift")
    with partitions.open(encoding="utf-8",newline="") as h:
        parts=list(csv.DictReader(h))
    if len(parts)!=176 or len({x["locus"] for x in parts})!=176:
        raise ValueError("not exactly the 176 original nuclear partitions")
    at=1
    stats=[]
    retained=[]
    for row in parts:
        left,right=int(row["start"]),int(row["end"])
        if left!=at or right<left:raise ValueError("noncontiguous original nuclear locus coordinates")
        at=right+1
        fractions={
            tip:sum(v in "ACGT" for v in seq[tip][left-1:right])/(right-left+1)
            for tip in OUTSIDE
        }
        accept=all(v>=THRESHOLD for v in fractions.values())
        stats.append({
            "original_gene":row["locus"],"original_start":left,"original_end":right,
            "aligned_columns":right-left+1,
            "NA_samples_ge40pct":sum(fractions[x]>=THRESHOLD for x in NA),
            "West_samples_ge40pct":sum(fractions[x]>=THRESHOLD for x in WEST),
            "Asia_samples_ge40pct":sum(fractions[x]>=THRESHOLD for x in ASIA),
            "all_13_external_sample_coverage_pass":str(accept).lower(),
            "minimum_external_ACGT_fraction":round(min(fractions.values()),8),
            "average_external_ACGT_fraction":round(sum(fractions.values())/13,8),
        })
        if accept: retained.append(row)
    if at!=161655:raise ValueError("original loci do not span complete 53-tip DNA alignment")
    size=sum(int(x["end"])-int(x["start"])+1 for x in retained)
    if len(retained)!=74 or size!=61240:raise ValueError("blind matched-occupancy source panel changed")
    out.mkdir(parents=True,exist_ok=True)
    target=out/"world53_74_all13ge40pct_nuclear_loci.fasta"
    def trim(dna):
        return "".join(dna[int(row["start"])-1:int(row["end"])] for row in retained)
    SeqIO.write([SeqRecord(Seq(trim(source)),id=tip,description="") for tip,source in sorted(seq.items())],
                target,"fasta")
    if len(list(SeqIO.parse(target,"fasta")))!=53 or digest(target)==FULL_ALIGNMENT_SHA:
        raise ValueError("new subset FASTA is not a preserved, separate 53-tip original-locus sensitivity")
    def dump_table(path,rows):
        with path.open("w",encoding="utf-8",newline="") as handle:
            w=csv.DictWriter(handle,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    dump_table(out/"all176_gene_region_occupancy_audit.csv",stats)
    offsets=[];start=1
    for row in retained:
        width=int(row["end"])-int(row["start"])+1
        offsets.append({"original_gene":row["locus"],"original_start":row["start"],
                        "original_end":row["end"],"new_start":start,"new_end":start+width-1})
        start+=width
    dump_table(out/"selected74_gene_original_to_new_coordinates.csv",offsets)
    info={
        "version":"world53_74all13ge40pct_morphology_blind_real_nuclear_loci_v1",
        "old_alignment_SHA256":FULL_ALIGNMENT_SHA,
        "old_original_partitions_SHA256":ORIGINAL_PARTITIONS_SHA,
        "full_source_tips":53,"full_original_nuclear_loci":176,"old_alignment_bp":161654,
        "outside_Japan_population_molecular_samples":13,
        "geographic_source_counts":{"North_America":6,"West_Palearctic":5,"Continental_East_Central_Asia":2},
        "selection_rule":"retain entire pre-aligned nuclear locus only if each of the 13 samples is >=40% ACGT in the original locus; geography and missingness only",
        "minimum_fraction":THRESHOLD,
        "trait_source_or_taxonomic_orientation_used_to_select_loci":False,
        "ancestral_nuclear_tree_used_to_select_loci":False,
        "retained_loci":len(retained),"retained_aligned_bp":size,
        "selected74_locus_ids":[x["locus"] for x in retained],
        "selected_fasta_SHA256":digest(target),
        "no_nucleotide_imputation":True,
        "status":"AUTHENTIC_MOLECULAR_SUBSET_ONLY_TREE_NOT_YET_ESTIMATED",
        "limitation":"a coverage-conditioned sensitivity of the same real source DNA, not a second biological or globally representative independent phylogeny"
    }
    (out/"source74_nuclear_locus_occupancy_contract.json").write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps({k:info[k] for k in (
        "full_source_tips","retained_loci","retained_aligned_bp","selected_fasta_SHA256",
        "trait_source_or_taxonomic_orientation_used_to_select_loci")},indent=2),flush=True)
    return info


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-alignment",type=Path,required=True)
    p.add_argument("--original-partitions",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    build(args.source_alignment,args.original_partitions,args.outdir)


if __name__=="__main__":
    main()
