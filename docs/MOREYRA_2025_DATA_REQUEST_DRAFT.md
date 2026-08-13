# Draft request for Moreyra et al. 2025 analysis artifacts

Date drafted: 2026-08-11  
Status: draft only; not sent

## Suggested subject

Request for target FASTA, retained-locus list and tree files from Moreyra et al. 2025

## Suggested message

Dear Dr. Moreyra and colleagues,

I am developing a comparative study of repeated floral anthocyanin loss and possible re-expression in East Asian *Cirsium*. Your paper, “A thorny tale: The origin and diversification of *Cirsium* (Compositae)” (Molecular Phylogenetics and Evolution, 2025), provides the essential global nuclear backbone for this work.

I have recovered the public raw reads under BioProject `PRJNA957074` and Supplementary Data 1, and I have reconciled the Supplementary Table S1 tree codes, vouchers and BioSamples. I also found the public repository `ldmoreyra/A-thorny-tale`, containing:

- `hybpiper_stats_exonerate.tsv`
- `seq_lengths_exonerate.tsv`
- `paralog_report.xlsx`

These resources allow the automatic warning-count and raw-occupancy portions of the locus filtering to be reconstructed, but I have not located the exact target/reference FASTA, final retained 350-locus list, retained alignments, per-locus gene trees or final machine-readable trees.

Would you be willing to share, or point me to a public archive containing, the following files and provenance information?

### 1. HybPiper target/reference input

- the exact target/reference FASTA used for the published assembly;
- whether the sequences are nucleotide or amino-acid targets;
- the target-file name and version;
- the associated Compositae1061 release or source deposit;
- the mapping mode used (`bwa`, `diamond`, `blastx` or other);
- if available, a checksum for the target file.

I am specifically seeking the HybPiper target/reference FASTA, rather than the short capture bait/probe oligonucleotide file.

### 2. Locus-retention information

- the names/IDs of the final 350 retained loci;
- the final retained/excluded status for loci with 1–10 HybPiper paralog warnings;
- any table or log recording the manual gene-tree orthology decisions;
- the final alignment-level occupancy/missingness results used to reduce the candidate set to 350 loci.

### 3. Alignment and gene-tree files

- the 350 final per-locus alignments;
- corresponding per-locus gene trees, including branch lengths and support values;
- any collapsed-branch or gene-tree filtering settings used before species-tree inference.

### 4. Final tree files

- final concatenated nuclear tree;
- final coalescent/species tree;
- dated tree used for biogeographic analyses;
- alternative topology or concordance outputs used in the interpretation;
- Newick/Nexus files with an indication of the branch-length and support metrics.

### 5. Software and parameter provenance

If readily available, a workflow, environment file, command log or version list for:

- HybPiper and mapper/assembler dependencies;
- alignment and trimming;
- per-locus and concatenated tree inference;
- coalescent species-tree inference;
- dating and biogeographic analyses.

The immediate aim is to reconstruct a small 12-sample East/Northeast Asian pilot from the public reads, verify compatibility with the published recovery summaries, and then add only transition-critical East Asian taxa that are genuinely absent from existing modern nuclear datasets. I will preserve the published tree codes, voucher identities and alternative taxonomic names rather than silently collapsing them.

Any files can remain under the reuse terms you specify. I would be happy to cite a preferred repository DOI or data paper, and to share the resulting reconciliation and reproducibility notes with you.

Thank you very much for making the raw reads and supplementary sample information publicly available.

Sincerely,

[Name]  
[Affiliation]  
[Contact]

## Minimal version

Dear Dr. Moreyra and colleagues,

I am using your 2025 global *Cirsium* phylogeny as the nuclear backbone for a study of repeated floral anthocyanin loss in East Asia. I have recovered Supplementary Data 1, `PRJNA957074`, and the three files in `ldmoreyra/A-thorny-tale`, but I have not found the exact HybPiper target/reference FASTA, the final retained 350-locus list, retained alignments/gene trees or final Newick trees.

Could you please share or identify the archive for:

1. the exact nucleotide/protein target FASTA and version/checksum;
2. the final 350 retained locus IDs and manual paralog-review decisions;
3. the final alignments and per-locus gene trees;
4. concatenated, coalescent and dated Newick/Nexus trees;
5. software versions or command/workflow files, if available?

I am preparing a public-read reconstruction pilot and will distinguish a compatible rerun from an exact reproduction unless the target/version and retained files can be confirmed. I would be glad to cite your preferred data repository and share the reconciliation notes.

Thank you very much,

[Name]

## Before sending

- confirm the corresponding author and preferred institutional contact from the published article;
- add the sender's current affiliation and project description;
- decide whether to request all files at once or begin with the target FASTA, final locus list and final tree files;
- include the EAzami repository link only after the branch/PR is ready for external viewing;
- do not describe the 531 reproducible candidates as the published final 350;
- offer a preferred public archive rather than requesting email attachments where possible.
