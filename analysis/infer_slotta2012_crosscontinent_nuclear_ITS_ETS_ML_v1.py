#!/usr/bin/env python3
"""Build a de-novo transcontinental Cirsium tree from actual nuclear rDNA ITS+ETS.

This is a new independent low-resolution paired-nuclear-rDNA reconstruction.
Never call it a 350-locus Moreyra 2025 whole-world Compositae1061 phylogeny.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,math,shutil,subprocess
from collections import Counter
from pathlib import Path

from Bio import AlignIO,Phylo,SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def run(cmd,stdout=None):
    r=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if r.returncode:
        raise RuntimeError(f"Command failed ({r.returncode}): {' '.join(cmd)}\n{r.stderr[-2200:]}")
    if stdout:
        Path(stdout).write_text(r.stdout,encoding="utf-8")
    return r.stdout


def build(guide:Path,outdir:Path,threads:int,bootstrap:int):
    outdir.mkdir(parents=True,exist_ok=True)
    with (guide/"admitted_specimen_nuclear_ITS_ETS.csv").open(encoding="utf-8",newline="") as f:
        samples=list(csv.DictReader(f))
    if len(samples)<35 or len({r["tip_id"] for r in samples})!=len(samples):
        raise ValueError("source QC gate was not passed or duplicate biological tips")
    tips={r["tip_id"] for r in samples}
    aligned={}
    locus_lengths={}
    for locus in ("ITS","ETS"):
        source=guide/f"{locus}_unaligned.fasta"
        rows=list(SeqIO.parse(source,"fasta"))
        if {r.id for r in rows}!=tips:
            raise ValueError("nuclear source sequences incomplete or extra: "+locus)
        aln_path=outdir/f"{locus}_aligned.fasta"
        mafft=shutil.which("mafft")
        if not mafft:
            raise RuntimeError("MAFFT is not available; refuse unaligned phylogram")
        run([mafft,"--auto","--thread",str(threads),str(source)],stdout=aln_path)
        alns=list(SeqIO.parse(aln_path,"fasta"))
        seen={r.id for r in alns}
        if seen!=tips:
            raise ValueError("aligned nuclear locus changed tip names: "+locus)
        lens={len(r.seq) for r in alns}
        if len(lens)!=1 or min(lens)<200:
            raise ValueError("per-locus MAFFT alignment invalid: "+locus)
        aligned[locus]={r.id:str(r.seq).upper().replace("U","T") for r in alns}
        locus_lengths[locus]=next(iter(lens))

    concatenated=[]
    L1,L2=locus_lengths["ITS"],locus_lengths["ETS"]
    for row in sorted(samples,key=lambda r:r["tip_id"]):
        tip=row["tip_id"]
        concatenated.append(SeqRecord(Seq(aligned["ITS"][tip]+aligned["ETS"][tip]),id=tip,description=""))
    fasta=outdir/"nuclear_ITS_ETS_source_vouchered_concat.fasta"
    SeqIO.write(concatenated,fasta,"fasta")
    parts=outdir/"nuclear_ITS_ETS_partitions.txt"
    parts.write_text(f"DNA, ITS = 1-{L1}\nDNA, ETS = {L1+1}-{L1+L2}\n",encoding="utf-8")
    # Only original published Carduus outgroup taxa, never a near Cirsium taxon.
    roots=[r["tip_id"] for r in samples if r["species_binomial"]=="Carduus nutans"]
    if not roots:
        roots=[r["tip_id"] for r in samples if r["species_binomial"].startswith("Carduus ")]
    if not roots:
        raise ValueError("source outgroup absent from input")
    outgroup=roots[0]
    exe=next((q for q in ("iqtree2","iqtree3","iqtree") if shutil.which(q)),None)
    if exe is None:
        raise RuntimeError("IQ-TREE executable not installed")
    prefix=outdir/"slotta2012_Cirsium_transcontinental_ITS_ETS_ML"
    cmd=[exe,"-s",str(fasta),"-p",str(parts),"-m","MFP",
         "-B",str(bootstrap),"--alrt","1000","-T",str(threads),
         "-seed","20261024","-o",outgroup,"--prefix",str(prefix)]
    run(cmd)
    treefile=Path(str(prefix)+".treefile")
    if not treefile.is_file():
        raise ValueError("IQ-TREE completed without a Newick treefile")
    tree=Phylo.read(treefile,"newick")
    leaf_names=[r.name for r in tree.get_terminals()]
    if len(leaf_names)!=len(samples) or set(leaf_names)!=tips or len(leaf_names)!=len(tips):
        raise ValueError("empirical nuclear ML tree leaf set fails exact source-voucher audit")
    branch=[float(x.branch_length) for x in tree.find_clades()
            if x is not tree.root and x.branch_length is not None]
    if not branch or not all(math.isfinite(x) and x>=0 for x in branch):
        raise ValueError("nuclear ML tree lacks valid real inferred branch lengths")
    freq=Counter(row["species_binomial"] for row in samples)
    def site_counts(matrix):
        return sum(len({seq[i] for seq in matrix.values() if seq[i] in "ACGT"})>=2
                   for i in range(len(next(iter(matrix.values())))))
    report={
        "version":"slotta2012_newly_inferred_real_transcontinental_nuclear_ITS_ETS_tree_v1",
        "result":"real_public_GenBank_accession_paired_vouchers_MAFFT_IQTREE_ML_COMPLETED",
        "original_source_publication":"Slotta, Horvath & Foley 2012 DOI 10.3390/plants1020061",
        "author_sequence_type":"nrDNA ITS and ETS (multicopy linked ribosomal regions)",
        "new_reanalysis":"EAzami de-novo MAFFT/IQ-TREE ML using original paired specimen table",
        "n_phylogram_tips":len(leaf_names),
        "n_sampled_species_binomial_labels":len(freq),
        "n_Cirsium_tips":sum(x.startswith("Cirsium ") for x in freq for _ in range(freq[x])),
        "n_Carduus_tips":sum(x.startswith("Carduus ") for x in freq for _ in range(freq[x])),
        "original_source_outgroup":outgroup,
        "alignment_locus_lengths":locus_lengths,
        "alignment_total_bp":L1+L2,
        "alignment_variable_site_count":site_counts({r.id:str(r.seq) for r in concatenated}),
        "software":exe,
        "iqtree_command":cmd,
        "n_taxon_duplicate_biological_specimens":sum(v>1 for v in freq.values()),
        "branch_lengths_in_substitutions_per_site":True,
        "rooted_tree_in_absolute_time_Ma":False,
        "published_Moreyra_final_350_locus_world_nuclear_tree":False,
        "this_is_full_294_tip_Cirsium_tree":False,
        "observed_phylogram_newick_sha256":hashlib.sha256(treefile.read_bytes()).hexdigest(),
        "known_limits":[
            "Nuclear ITS and ETS come from the same ribosomal repeat and are not independent low-copy nuclear genes.",
            "This is a small publicly paired three-region reanalysis, not exhaustive phylogenomic sampling of genus Cirsium.",
            "Low sequence differentiation, concerted evolution and potential hybridization can distort nuclear ribosomal genealogies.",
            "Only source-authenticated GenBank specimen pairs are allowed; taxa without both loci are left out.",
            "Geographic collection origin and morphology must be joined independently, with uncertainty and potential cultivated specimens stated.",
            "Root/branch length is substitution/site, not calibrated events or measured palaeoclimate.",
        ]
    }
    (outdir/"nuclear_phylogram_receipt.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sequence-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--threads",type=int,default=2)
    p.add_argument("--bootstrap",type=int,default=1000)
    a=p.parse_args()
    build(a.sequence_dir,a.outdir,a.threads,a.bootstrap)

if __name__=="__main__":
    main()
