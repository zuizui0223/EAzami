# Moreyra et al. 2025 exact-tree and retained-locus status

Date: 2026-08-11

## What has now been recovered

- the verified Elsevier Supplementary Data 1 DOCX;
- a normalized supplement sample table;
- the complete public SRA run metadata recoverable from BioProject `PRJNA957074`;
- a public-project taxon summary;
- an accepted-name and synonym audit for transition-relevant East Asian taxa;
- a sequencing-decision panel that separates species placement from population history.

The supplement is retrieved reproducibly from:

`https://ars.els-cdn.com/content/image/1-s2.0-S1055790325000028-mmc1.docx`

The retrieval URL, SHA256, size, table inventory and normalized outputs are versioned through the repository workflow and derived evidence tables. Publisher binary files are not committed.

## What the recovered supplement can establish

Supplementary Table S1 can establish, where fields are present:

- submitted taxon/sample names;
- voucher and specimen provenance;
- BioSample or sequence-project linkage;
- regional and sample-level inclusion in the published study;
- whether an apparent gap was caused by an accepted-name or synonym mismatch.

Together with public SRA metadata, this is sufficient to distinguish:

1. a published nuclear sample with public reads;
2. a published sample whose current public-run match remains unresolved;
3. a public-project sample whose exact supplement row is unresolved;
4. a true candidate gap only after name and data-source audits are exhausted.

## What remains unavailable

The recovered Supplementary Data 1 is **not** a substitute for the final phylogenetic tree artifact. The current recovery has not established a reusable file containing all of the following:

- the final full-sample Newick/Nexus topology;
- branch lengths;
- node support values in machine-readable form;
- the exact 350 retained nuclear-locus list;
- the locus-by-sample occupancy matrix;
- per-locus orthology/paralogy filters;
- the complete set of gene trees used by the coalescent analysis;
- alternative concatenated/coalescent trees needed for a topology ensemble.

Until these are recovered or reconstructed, formal rate comparisons and stochastic character mapping on the Moreyra backbone remain premature.

## Current analysis policy

- Use the recovered sample table to classify nuclear coverage and sequencing gaps.
- Use published topology statements only as topology fragments, without inventing branch lengths.
- Do not graft missing taxa into one fixed tree and report that as a resolved evolutionary history.
- Keep concatenated, coalescent, paralog-aware and plastid histories separate.
- Use topology-only parsimony as a transparent diagnostic, not as a substitute for branch-length-aware inference.

## Recovery routes still being pursued

1. publisher supplementary/CDN enumeration beyond `mmc1`;
2. Crossref and article metadata relations;
3. TreeBASE, Dryad, Mendeley Data, figshare and Zenodo searches by DOI, title and author;
4. NCBI BioProject/SRA reconstruction of sampled tips;
5. direct author or corresponding-author request for final tree, retained-locus list and occupancy matrix;
6. if no deposited tree exists, a documented reconstruction from public Compositae1061 reads under the published filtering logic.

## Reanalysis fallback

If no exact final tree file is publicly recoverable, the fallback is not figure tracing. It is a reproducible reanalysis:

1. recover all public PRJNA957074 libraries;
2. run HybPiper or a compatible Compositae1061 extraction;
3. reproduce a conservative single-copy matrix;
4. identify the Moreyra-compatible retained subset where the paper provides sufficient filtering detail;
5. infer per-locus trees with consistent trimming/model rules;
6. infer concatenated and ASTRAL-family trees;
7. compare the reconstructed topology to published figures and reported clades;
8. archive the exact commands, software versions, locus lists and occupancy summaries.

This reconstructed tree must be labelled as an EAzami reanalysis, not as the authors' deposited final tree.

## Immediate consequence

The current evidence is already sufficient to prevent indiscriminate species-level RAD sequencing. However, it is not yet sufficient to treat Moreyra branch lengths or exact sister relationships as recovered for formal ancestral-state likelihood analyses.
