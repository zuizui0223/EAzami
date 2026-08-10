# Protocol: recover the final Moreyra 2025 tree ensemble and retained loci

## Goal

Recover the exact machine-readable phylogenetic artifacts behind Moreyra et al. 2025 after the sample/voucher table has been successfully reconstructed.

The missing objects are:

- final concatenated nuclear tree;
- final coalescent/species tree;
- dated tree used for biogeography;
- per-locus gene trees;
- retained 350-locus list;
- orthology/filtering criteria linked to those loci;
- any alternative topology or concordance/discordance output.

The tracking schema is:

- `data/schema/moreyra2025_tree_artifact_recovery.csv`

## Search order

1. Article supplementary landing page and every `mmc` attachment index.
2. Data-availability statement, author-accepted manuscript and embedded repository links.
3. TreeBASE, Dryad, Mendeley Data, Zenodo and Figshare using DOI, title, PII and first/corresponding author names.
4. NCBI BioProject links and SRA study metadata for external-analysis links.
5. Institutional repositories and project pages.
6. Direct author request for exact final files and locus list.

## Artifact acceptance criteria

A tree file is accepted only when it has:

- a stable source or author-provided provenance;
- sample names that can be joined to Supplementary Table S1;
- explicit analysis identity (concatenated, coalescent, dated or plastid);
- branch lengths interpreted correctly;
- rooting/outgroup information;
- support metric definition;
- checksum and local provenance record.

A figure-derived tree is a fallback only. It must be labelled `figure_reconstructed_topology`, contain no invented branch lengths, and preserve unresolved or unreadable nodes as polytomies.

## Reconciliation steps

1. Parse all tip labels.
2. Join tip labels to `Tree code names` from Supplementary Table S1.
3. Join BioSample/voucher/NCBI names using the completed Moreyra sample audit.
4. Flag unmatched and duplicated labels.
5. Preserve alternative genera and synonym conflicts.
6. Verify that focal East/NE Asian tips correspond to the intended samples.
7. Compare concatenated and coalescent topology around every flower-colour transition candidate.

## Locus recovery

For the 350 retained loci, record:

- original Compositae1061 target identifier;
- HybPiper gene identifier;
- retained/excluded status;
- occupancy;
- paralog warning;
- alignment length;
- informativeness/variable sites if available;
- whether the locus can be recovered from Chang transcriptomes or new target-capture samples.

The output should support three matrices:

1. Moreyra-compatible retained-locus matrix;
2. conservative single-copy matrix;
3. paralog/homeolog-aware matrix.

## Analyses unlocked by completion

- full-tree flower-colour ancestral-state reconstruction;
- ER/ARD model comparison with real branch lengths;
- stochastic mapping;
- topology-ensemble sensitivity;
- exact expected-information-gain ranking for missing taxa;
- definitive target-capture panel v1.0;
- comparison of nuclear versus plastid histories.

## Stop rule

Do not freeze formal transition rates from equal-length or manually invented branches. If the exact branch-length tree remains unavailable, report topology-only parsimony and contact the authors before proceeding to a figure-derived fallback.
