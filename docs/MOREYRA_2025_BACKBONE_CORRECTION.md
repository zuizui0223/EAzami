# Moreyra et al. 2025 correction — Japanese nuclear backbone

Date: 2026-08-10

## Why this matters

The initial EAzami scaffold treated the Japanese nuclear phylogeny as a large unresolved gap. That is too pessimistic.

Moreyra et al. (2025), *A thorny tale: The origin and diversification of Cirsium (Compositae)*, used target-capture data from 350 nuclear loci for 299 plants / 251 taxa and explicitly included 38 Japanese *Cirsium* species, 30 of them endemic. The paper recovered all but two sampled Japanese species in a clade interpreted as a rapid Pleistocene radiation following a single dispersal to Japan.

Raw reads are deposited under NCBI BioProject `PRJNA957074`; sample-level accessions and voucher information are reported in supplementary Table S1.

## Consequence for EAzami

RAD-seq should not be justified simply as “building the first nuclear phylogeny of Japanese *Cirsium*”. A substantial Japanese nuclear backbone already exists.

The higher-value RAD-seq objectives are now:

1. add taxa genuinely absent from modern nuclear datasets, especially flower-colour-transition-critical taxa;
2. add population replication within species represented by only one target-capture sample;
3. resolve within-species white/coloured polymorphism and geographic structure;
4. test introgression and reticulation around candidate colour transitions;
5. connect the Japanese radiation to Chinese, Korean, Ryukyu and Taiwanese bridge populations using a shared population-genomic framework.

## Project-tip recovery before new sequencing

A taxon may already occur in `PRJNA957074` or a published tree even when its exact sample is not visible in the article text. The repo now separates:

- exact SRA project tip verified;
- paper/tree placement verified but accession pending;
- main-text mention only;
- project-tip unresolved;
- true nuclear gap after supplements, runinfo and synonyms are checked.

`analysis/recover_ncbi_project_runs.py` reconstructs the complete public SRA run table and compares it with a versioned focal-taxon list. This recovery must precede interpretation of an apparent Japanese/Korean gap as a reason to generate new sequence data.

The first directly verified project anchor is *C. domonii*:

- BioSample `SAMN34240283`
- SRA sample `SRS18284452`
- experiment `SRX21011499`
- run `SRR25265717`
- library `Cirsium-domonii_FJ318`
- locality Japan: Honshu

## Priority rule update

A Japanese or Korean taxon is Tier A only if at least one of the following is true:

- its placement changes the inferred number or direction of white/coloured transitions;
- it contains natural white/coloured polymorphism;
- it is absent after complete Moreyra/SRA/synonym recovery and lies near a transition-critical branch;
- population-level data are required to distinguish regain from ancestral polymorphism or introgression.

A uniformly coloured species already strongly represented in a modern nuclear tree is a low RAD-seq priority unless it is needed as a flanking control.

## Immediate white-polymorphism candidates

### *Cirsium pendulum*

A natural white-flowered form is documented in Japan. Because the species extends into Korea, China and the Russian Far East, the correct comparison is not only Japanese white vs Japanese purple, but also Japanese white vs a transregional coloured population background.

Key questions:

- Is the white form one geographically derived lineage or repeated local loss?
- Is the white haplotype shared with continental populations as old standing variation?
- Does the white form reuse the same anthocyanin regulatory node as Taiwanese and Ryukyu white lineages?

### *Cirsium sieboldii*

A Japanese white-flowered form is documented, and the expanded taxonomic treatment connects the species to Zhejiang. It is therefore a second transregional within-species history test rather than only a Japanese form.

### Korean candidates

Historical white-form names in *C. setidens*, *C. rhinoceros*, *C. schantarense* and *C. vlassovianum* provide additional screening candidates. They are not promoted until extant or voucher-backed white material is confirmed. Their modern nuclear coverage must be recovered before new sequencing is proposed.

## Remaining source gap

The exact Moreyra Newick/branch lengths and complete Supplementary Data 1 are still required for formal Mk/stochastic mapping. Public SRA metadata resolves public project membership, but it does not by itself recover the final inferred tree or tips that may lack public reads.

The next verification task is therefore two-part:

1. run the official project recovery workflow and join all public tips to the East Asian colour/ploidy atlas;
2. recover the exact Supplementary Data/Newick artifacts to place those tips on the published topology.
