#!/usr/bin/env python3
"""Same-SRR pipeline-discordance locus-screen on REAL unique52 Cirsium nuclear matrix.

This is a pre-specified *technical sensitivity* (NOT orthology/paralogy proof):
remove a frozen original nucleus Compositae1061 gene only when the
two past COMPUTATIONAL reconstructions of identical SAMN44017865 /
SRR30887251 had >=400 bases both called ACGT and >5% disagreement
on those shared bases. The duplicate molecular sample itself has
ALREADY been removed and is not a phylogenetic population replicate.
This removal is based solely on read-processing disagreement, not
taxonomic labels, head U/D, flower colour, native occurrence or topology.

Do not use gene disagreement from that single original run to assert
paralogs or homeologs in unrelated samples; these are candidate QC flags.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

SOURCE_BAL75_SHA="61dbdf36e61120606e2465d65478e499c6fbdd24cca1504b001bc5df26627e83"
SOURCE_LEDGER_SHA="5cfdae7495400101eace90c84e47794c151043589ca0b5943ff5d76a915a5541"
SOURCE_PIPELINE_DISAGREEMENTS_SHA="2ac9be19f80925dec544b9890f442523fbac997c82854ede561b40230cbabe66"
MIN_SHARED_BASES=400
MAX_ALLOWED_DISAGREEMENT_FRAC=0.05
EXPECTED_FLAGGED={"At1g02170","At3g04400"}
EXPECTED_RETAINED_LOCUS_COUNT=73
EXPECTED_RETAINED_BP=61302


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def readcsv(p):
    with Path(p).open(encoding="utf-8-sig",newline="") as h:
        return list(csv.DictReader(h))

def build(source75, coordinates, disagreement, outdir):
    for path,sig in ((source75,SOURCE_BAL75_SHA),
                     (coordinates,SOURCE_LEDGER_SHA),
                     (disagreement,SOURCE_PIPELINE_DISAGREEMENTS_SHA)):
        if digest(path)!=sig:
            raise ValueError("source original molecular locus/technical QC file changed "+str(path))
    intervals=readcsv(coordinates)
    geneQC={x["original_locus"]:x for x in readcsv(disagreement)}
    records=list(SeqIO.parse(source75,"fasta"))
    source={r.id:str(r.seq).upper() for r in records}
    if len(records)!=len(source) or len(source)!=52 or {len(s) for s in source.values()}!={62810}:
        raise ValueError("source true 52-tip unique-BioSample 75-locus sequences changed")
    if "J38S038" not in source or any("GLB2_SRR30887251" in x for x in source):
        raise ValueError("same-SRR duplicated individual was not removed before locus filter")
    dropped=set()
    summary=[]
    pos=1
    for gene in intervals:
        locus=gene["original_locus"]
        start,end=int(gene["subset_start"]),int(gene["subset_end"])
        if start!=pos or end<start:
            raise ValueError("original subset aligned 75-gene coordinate ledger changed")
        pos=end+1
        if locus not in geneQC:
            raise ValueError("same-source-run pipeline locus QC did not contain the original gene")
        audit=geneQC[locus]
        overlap=int(audit["overlap_called_bp"])
        divergent=int(audit["pipeline_disagreement_bp"])
        flag=overlap>=MIN_SHARED_BASES and divergent/overlap>MAX_ALLOWED_DISAGREEMENT_FRAC
        summary.append({
          "locus":locus,
          "original_75_gene_alignment_bp":end-start+1,
          "duplicated_SRR_technical_cross_pipeline_called_overlap":overlap,
          "duplicated_SRR_technical_call_discrepancies":divergent,
          "same_source_SRR_processing_disagreement":(divergent/overlap if overlap else None),
          "failed_technical_locus_screen":str(flag).lower(),
          "not_proven_paralog_or_homeolog":True,
        })
        if flag:dropped.add(locus)
    if pos-1!=62810 or dropped!=EXPECTED_FLAGGED:
        raise ValueError("unapproved source QC gene exclusions or gene order changed")
    selected=[x for x in intervals if x["original_locus"] not in dropped]
    result_bp=sum(int(x["subset_end"])-int(x["subset_start"])+1 for x in selected)
    if len(selected)!=EXPECTED_RETAINED_LOCUS_COUNT or result_bp!=EXPECTED_RETAINED_BP:
        raise ValueError("source 73-technical-screen nuclear gene count and BP drift")
    new={}
    for tip,s in source.items():
        shorter="".join(s[int(x["subset_start"])-1:int(x["subset_end"])] for x in selected)
        if len(shorter)!=result_bp:raise ValueError("trimmed true molecular source length changed")
        new[tip]=shorter
    outdir.mkdir(parents=True,exist_ok=True)
    fa=outdir/"real_world52_73loci_after_sameSRR_disagreement_screen.fasta"
    SeqIO.write([SeqRecord(Seq(s),id=tip,description="") for tip,s in sorted(new.items())],fa,"fasta")
    p=outdir/"world52_original75_technical_sameSRR_gene_qc.csv"
    with p.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    receipt={
      "version":"real_world52_73_original_gene_after_source_sameSRR_technical_discordance_screen_v1",
      "original_51_unique_Cirsium_BioSamples_plus_outgroup_tips":52,
      "same_molecule_BioSample_double_count_removed_before_gene_selection":True,
      "technical_screen_source_true_BioSample":"SAMN44017865",
      "technical_screen_source_true_SRR":"SRR30887251",
      "past_two_sequences_from_same_SRR_differed_due_to_processing_pipelines_not_population_genotypes":True,
      "original_locus_subset":75,
      "original_alignment_bp":62810,
      "technical_locus_disagreement_screen_shared_bases_min":MIN_SHARED_BASES,
      "technical_locus_disagreement_screen_fraction_strict_gt":MAX_ALLOWED_DISAGREEMENT_FRAC,
      "technical_flagged_gene_IDs":sorted(dropped),
      "original_gene_name_count_retained":len(selected),
      "aligned_bp_retained":result_bp,
      "molecular_source_unchanged_except_whole_flagged_locus_removal":True,
      "new_corrected_52tip_73gene_alignment_SHA256":digest(fa),
      "phenotype_taxon_clade_or_U_D_used_in_selection":False,
      "paralog_or_homeolog_or_genomic_hybridization_proven":False,
      "scope":"Source specimen pipeline disagreement screening sensitivity. This is not proof flagged genes are biological paralogs; retained genes also not certified single-copy.",
      "worldwide_294tip_350locus_Moreyra_final_species_tree_estimated":False,
    }
    (outdir/"world52_73gene_source_pipeline_screen_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2),flush=True)
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source75",type=Path,required=True)
    p.add_argument("--original75-ledger",type=Path,required=True)
    p.add_argument("--same-SRR-gene-disagreement",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    build(a.source75,a.original75_ledger,a.same_SRR_gene_disagreement,a.outdir)

if __name__=="__main__":
    main()
