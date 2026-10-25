#!/usr/bin/env python3
"""Repair source-level duplicate BioSample in the empirical world53 Cirsium tree.

CRITICAL: 'J38S038' and 'GLB2_SRR30887251_Cirsium_kamtschaticum'
are SAME individual (SAMN44017865/SRR30887251), not disjoint
Japan vs Siberian populations. The original J38 reconstruction is retained;
the repeated reference-mapped copy is never another species, trait or event.

The immutable 53-tip input alignment and original S1 voucher table are
source-audited before source-blind de-duplication. One honest 52-BioSample
176-original-gene alignment and a separate 12-external-source-balanced
75-gene subset are output, without ever replacing source allele calls.
"""
from __future__ import annotations

import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

SOURCE53_SHA="9179394190a3ab499a122439bca9c8bbe74e205a315440e4f7442b5ee225b237"
SOURCE_TRAITS_SHA="457059076a15d91be941d661a19b2590e25192a89399f22ed6f2299eeff5198a"
SOURCE_PARTITIONS_SHA="30e6e5703a76b4065c3903c04b43179fb538d280539df66c7bf64706962a128e"
DUP_J38="J38S038"
DUP_SECONDARY="GLB2_SRR30887251_Cirsium_kamtschaticum"
DUP_BIOSAMPLE="SAMN44017865"
DUP_RUN="SRR30887251"
SOURCE_INGROUP_NAME="Cirsium kamtschaticum"
LONGER_REFERENCE_MIN_BASES=50000
ORIGINAL_GENE_UNIVERSE=176
MATCHED_MIN_ACGT_FRAC=.40
EXPECTED_BALANCED_LOCI=75
EXPECTED_BALANCED_BP=62810
DNA="ACGT"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_hash(path, expected):
    if sha(path)!=expected:
        raise ValueError("original source-backed nucleotide / S1 provenance SHA changed: "+str(path))


def load_csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as h:
        return list(csv.DictReader(h))


def fasta(path):
    original=list(SeqIO.parse(path,"fasta"))
    data={r.id:str(r.seq).upper() for r in original}
    if len(data)!=len(original) or not original:
        raise ValueError("non-unique/missing biological nucleotide identities")
    return data


def write_fasta(path, sequence):
    SeqIO.write([SeqRecord(Seq(s),id=name,description="")
                for name,s in sorted(sequence.items())],path,"fasta")


def reconstruct(source53, source_trait_table, original_partitions, outdir):
    require_hash(source53,SOURCE53_SHA)
    require_hash(source_trait_table,SOURCE_TRAITS_SHA)
    require_hash(original_partitions,SOURCE_PARTITIONS_SHA)
    genotype=fasta(source53)
    phenotype=load_csv(source_trait_table)
    parts=load_csv(original_partitions)
    by_tip={r["tip_id"]:r for r in phenotype}
    if len(genotype)!=len(by_tip) or set(genotype)!=set(by_tip) or len(genotype)!=53:
        raise ValueError("original sequence and S1 genetic accession provenance did not exactly join 53 named tips")
    if len(parts)!=ORIGINAL_GENE_UNIVERSE or len({r["locus"] for r in parts})!=ORIGINAL_GENE_UNIVERSE:
        raise ValueError("original source locus universe wrong")
    if {len(s) for s in genotype.values()}!={161654}:
        raise ValueError("actual original 176-gene nuclear alignment length not preserved")
    if set(x["head_orientation"] for x in phenotype)!={"U","D","?"}:
        raise ValueError("source U/D categories changed")
    accession=defaultdict(list)
    runids=defaultdict(list)
    for row in phenotype:
        if row["tip_id"]=="OUTGROUP_saff":
            if row["source_biosample"] or row["source_run"]:
                raise ValueError("outgroup wrongly supplied with Cirsium S1 accession")
            continue
        if not row["source_biosample"] or not row["source_run"]:
            raise ValueError("ingroup tip lacks original source S1 BioSample/SRR identifier")
        accession[row["source_biosample"]].append(row["tip_id"])
        for token in row["source_run"].split("|"):
            if token:runids[token].append(row["tip_id"])
    biosample_duplicates={x:sorted(v) for x,v in accession.items() if len(v)>1}
    if biosample_duplicates!={DUP_BIOSAMPLE:sorted([DUP_J38,DUP_SECONDARY])}:
        raise ValueError("expected exactly ONE source BioSample collision; investigate source registry")
    if sorted(runids[DUP_RUN])!=sorted([DUP_J38,DUP_SECONDARY]):
        raise ValueError("same original library SRR is not duplicated as anticipated")
    a,b=by_tip[DUP_J38],by_tip[DUP_SECONDARY]
    if (a["source_biosample"],a["source_run"])!=(DUP_BIOSAMPLE,DUP_RUN):
        raise ValueError("original Japan38 source genetic identity drift")
    if (b["source_biosample"],b["source_run"])!=(DUP_BIOSAMPLE,DUP_RUN):
        raise ValueError("new purported extra species has a different original accession")
    if (a["head_orientation"],b["head_orientation"])!=("D","D"):
        raise ValueError("original botanical head evidence for one species changed")
    if SOURCE_INGROUP_NAME.casefold() not in a["source_taxon"].casefold() or b["source_taxon"]!=SOURCE_INGROUP_NAME:
        raise ValueError("source taxonomic concept identity changed")
    if not any(x in a["source_voucher"].lower() for x in ("siberia","kamchatka","chukotka")):
        raise ValueError("original J38 accession's field voucher is not documented as Siberian")
    if len([x for x in genotype[DUP_J38] if x in DNA])<LONGER_REFERENCE_MIN_BASES:
        raise ValueError("original source DNA does not meet defensible original-assembly preference")
    if sum(x in DNA for x in genotype[DUP_J38]) <= sum(x in DNA for x in genotype[DUP_SECONDARY]):
        raise ValueError("secondary reference-mapped version unexpectedly has higher original read coverage")

    # Same specimen independently assembled by two pipelines can have
    # different nucleotide characters; quantify, never treat as genealogy.
    av,bv=genotype[DUP_J38],genotype[DUP_SECONDARY]
    mask=[k for k,(x,y) in enumerate(zip(av,bv)) if x in DNA and y in DNA]
    differences=sum(av[i]!=bv[i] for i in mask)
    if len(mask)<30000 or differences<1:
        raise ValueError("unexpected lack of sufficient duplicate pipeline comparison")
    disputed=[]
    spans=[]
    pos=1
    for locus in parts:
        l,r=int(locus["start"]),int(locus["end"])
        if l!=pos or r<l:
            raise ValueError("published original nuclear partitions do not preserve source coordinates")
        pos=r+1
        overlap=sum(av[i] in DNA and bv[i] in DNA for i in range(l-1,r))
        diff=sum(av[i] in DNA and bv[i] in DNA and av[i]!=bv[i] for i in range(l-1,r))
        disputed.append({"original_locus":locus["locus"],"overlap_called_bp":overlap,
                         "pipeline_disagreement_bp":diff,
                         "pipeline_disagreement_fraction":(diff/overlap if overlap else "")})
        spans.append((locus,l-1,r))
    if pos!=161655:
        raise ValueError("original source gene partitions no longer sum to original length")
    removed={DUP_SECONDARY}
    good={k:v for k,v in genotype.items() if k not in removed}
    p_good=[x for x in phenotype if x["tip_id"] not in removed]
    if len(good)!=52 or len({x["source_biosample"] for x in p_good if x["tip_id"]!="OUTGROUP_saff"})!=51:
        raise ValueError("correct 52 tips / 51 unique Cirsium BioSamples not achieved")
    counts=Counter(x["head_orientation"] for x in p_good if x["tip_id"]!="OUTGROUP_saff")
    if counts!=Counter({"U":19,"D":8,"?":24}):
        raise ValueError("invalid surviving botanical head states after true genetic de-duplication")
    outside=[x for x in good if x.startswith("GLB")]
    if len(outside)!=12:
        raise ValueError("the remaining 12 North-American, Western, Asian genetic sample IDs are not unique")
    outside_by_region=Counter(by_tip[t]["region"] for t in outside)
    if outside_by_region!={"North_America":6,"West_Palearctic":5,"Continental_East_Central_Asia":1}:
        raise ValueError("source geographic region labels drift after genetic sample de-duplication")
    occupancy=[];eligible=[]
    for locus,lo,hi in spans:
        fractions=[sum(x in DNA for x in good[t][lo:hi])/(hi-lo) for t in outside]
        ok=all(z>=MATCHED_MIN_ACGT_FRAC for z in fractions)
        occupancy.append({"original_locus":locus["locus"],"original_start":lo+1,"original_end":hi,
                          "aligned_bp":hi-lo,"outside_samples_ge40":sum(z>=.4 for z in fractions),
                          "n_distinct_external_BioSamples":12,"admitted":str(ok).lower(),
                          "minimum_ACGT_external":round(min(fractions),8)})
        if ok:eligible.append((locus,lo,hi))
    n_bp=sum(hi-lo for _,lo,hi in eligible)
    if (len(eligible),n_bp)!=(EXPECTED_BALANCED_LOCI,EXPECTED_BALANCED_BP):
        raise ValueError("morphology-blind unique-BioSample genomic occupancy source audit changed")
    outdir.mkdir(parents=True,exist_ok=True)
    full=outdir/"world52_original176_uniqueBioSamples.fasta"
    write_fasta(full,good)
    subset=outdir/"world52_75loci_all12_external_uniqueBioSamples.fasta"
    shorter={k:"".join(seq[lo:hi] for _,lo,hi in eligible) for k,seq in good.items()}
    write_fasta(subset,shorter)
    def write_csv(path,rows):
        with path.open("w",encoding="utf-8",newline="") as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    write_csv(outdir/"world52_source_S1_unique_BioSample_9traits.csv",p_good)
    write_csv(outdir/"world52_original176_12external_gene_occupancy.csv",occupancy)
    write_csv(outdir/"same_SRR_processed_twice_176_locus_discordance.csv",disputed)
    genelist=[];start=1
    for locus,lo,hi in eligible:
        genelist.append({"original_locus":locus["locus"],"original_start":lo+1,
                         "original_end":hi,"subset_start":start,"subset_end":start+hi-lo-1})
        start+=hi-lo
    write_csv(outdir/"world52_75frozen_gene_coordinate_ledger.csv",genelist)
    source_dup={
      "version":"EAzami_world53_source_molecular_same_BioSample_de_duplication_to52_v1",
      "source_original_53tip_176locus_DNA_SHA256":SOURCE53_SHA,
      "source_original_53tip_S1_taxon_state_SHA256":SOURCE_TRAITS_SHA,
      "source_original_176_gene_partitions_SHA256":SOURCE_PARTITIONS_SHA,
      "molecular_source_nuclear_individual_tips_before_dedup":53,
      "unique_individual_BioSamples_after_de_dup":51,
      "result_true_molecular_tips_with_Carthamus_outgroup":52,
      "duplicate_detection_independent_of_morphology":True,
      "duplicate_BioSample":DUP_BIOSAMPLE,"duplicate_SRR":DUP_RUN,
      "duplicate_tip_ids":sorted([DUP_J38,DUP_SECONDARY]),
      "source_voucher_original_J38":a["source_voucher"],
      "retained_BioSample_tip":DUP_J38,"excluded_reference_remapped_tip":DUP_SECONDARY,
      "source_both_tips_same_actual_sequenced_individual":True,
      "sequence_read_processing_disagreement_is_not_evolution":True,
      "comparison_both_pipelines_confident_base_overlap":len(mask),
      "comparison_both_pipelines_confident_base_disagreement":differences,
      "disagreement_p":differences/len(mask),
      "original_J38_confident_bp":sum(x in DNA for x in av),
      "reference_mapped_extra_confident_bp":sum(x in DNA for x in bv),
      "duplicate_molecular_taxon_state":a["head_orientation"],
      "nuclear_corrected_ingroup_states":dict(counts),
      "selected_12_nonJapan_original_GLB_extra_specimens_by_source_region":dict(outside_by_region),
      "external_12_sample_all_ge40pct_original_loci":len(eligible),
      "external_12_sample_original_locus_subset_aligned_bp":n_bp,
      "gene_selection_uses_no_flower_head_colour_or_phylogenetic_topology":True,
      "source_52tip_176locus_alignment_SHA256":sha(full),
      "source_52tip_75locus_alignment_SHA256":sha(subset),
      "source_52tip_S1_original_nine_trait_csv_SHA256":sha(outdir/"world52_source_S1_unique_BioSample_9traits.csv"),
      "genetic_outgroup":"OUTGROUP_saff",
      "not_relabelled_as_52_species":True,
      "historical_ancestral_UD_event_count_from_pseudoreplicate_not_allowed":True,
      "complete_Moreyra_294_BioSample_350gene_accepted_phylogeny_available":False,
      "two_source_pipelines_allele_disagreement_requires_independent_read_orthology_review":True,
    }
    (outdir/"world52_unique_BioSamples_source_collision_QC.json").write_text(
        json.dumps(source_dup,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:source_dup[k] for k in (
      "duplicate_BioSample","duplicate_SRR",
      "comparison_both_pipelines_confident_base_overlap",
      "comparison_both_pipelines_confident_base_disagreement",
      "result_true_molecular_tips_with_Carthamus_outgroup",
      "nuclear_corrected_ingroup_states",
      "external_12_sample_all_ge40pct_original_loci",
      "external_12_sample_original_locus_subset_aligned_bp",
      "source_52tip_176locus_alignment_SHA256",
      "source_52tip_75locus_alignment_SHA256"
    )},indent=2),flush=True)
    return source_dup


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source53",type=Path,required=True)
    p.add_argument("--source-traits",type=Path,required=True)
    p.add_argument("--partitions",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    reconstruct(a.source53,a.source_traits,a.partitions,a.outdir)


if __name__=="__main__":
    main()
