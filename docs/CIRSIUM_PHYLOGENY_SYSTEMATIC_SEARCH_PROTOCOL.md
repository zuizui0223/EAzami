# Systematic evidence-map protocol for *Cirsium* phylogeny

Version: 0.1  
Date: 2026-08-10

## Objective

Maintain a reproducible, updateable evidence map of the phylogeny and reticulate evolution of *Cirsium* and the Carduus–*Cirsium* group. The purpose is not to maximize the number of citations. It is to determine, for every Chapter 2 taxon and inference:

- whether a modern nuclear placement exists;
- whether the evidence is a deep backbone, a species tree, a population tree or only an organelle genealogy;
- whether hybridization, incomplete lineage sorting, polyploidy or taxonomic disagreement changes the interpretation;
- which missing data are genuine biological gaps rather than inaccessible supplements or synonym mismatches.

## Review scope

### Taxonomic scope

Primary:

- *Cirsium* sensu lato;
- *Lophiolepis*, *Epitrachys* and other segregates containing taxa historically placed in *Cirsium*;
- Carduus–*Cirsium* group studies that determine outgroups, generic boundaries or hybrid origins.

Contextual:

- Carduinae and Cardueae studies when they supply the deep nuclear backbone or reusable probe sets;
- cytogenetic and hybrid studies that constrain topology interpretation.

### Geographic scope

Global evidence is screened first. Regional extraction is then organized as:

1. Japan and Ryukyu Islands;
2. Taiwan;
3. China;
4. Korea;
5. Russian Far East, Sakhalin and Mongolia;
6. North America as a comparative rapid-radiation system;
7. Europe/Southwest Asia as the principal source of generic, hybridization and cytogenetic evidence;
8. Africa for Carduinae generic boundaries.

### Evidence scope

Include primary studies containing at least one of:

- nuclear phylogenomics, target capture or phylotranscriptomics;
- multilocus nuclear/plastid phylogeny or species delimitation;
- RAD-seq, whole-genome or population-genomic phylogeography;
- explicit tests of hybridization, admixture, allopolyploidy or introgression;
- chromosome number, flow-cytometric genome size or cytotype data tied to named taxa/populations;
- complete plastomes when needed to document maternal history or sequence availability;
- taxonomic revisions that change accepted names, synonyms or circumscription of focal lineages;
- public datasets containing matrices, tree files, gene trees, raw reads or sample metadata.

Exclude from the curated evidence registry:

- secondary webpages without a traceable primary source;
- ecological papers mentioning a phylogeny but adding no relevant tree/data;
- single barcode accessions with no reproducible taxon placement or voucher;
- horticultural white-flower records without natural-population provenance;
- review articles as evidence for a topology (they may be retained in a separate background bibliography).

## Search sources

### Automated discovery

The repository script `analysis/recover_cirsium_phylogeny_literature.py` searches:

- Crossref Works API;
- Europe PMC REST API.

Automated records are written to a candidate file only. They are never promoted directly into the curated registry.

### Manual and citation-based discovery

Search and verify through:

- PubMed/PMC;
- Web of Science and Scopus when institutional access is available;
- Google Scholar for citation chaining and nomenclatural literature;
- publisher supplementary-material pages;
- TreeBASE;
- Dryad;
- Mendeley Data;
- figshare;
- Zenodo;
- NCBI BioProject/SRA/BioSample/GenBank;
- institutional repositories and accepted manuscripts.

Every Tier-A study is subjected to backward-reference and forward-citation snowballing.

## Query families

The automated query file contains independent families so that failure of one wording does not erase a topic.

### Backbone and generic limits

- `Cirsium phylogeny`
- `Cirsium phylogenomics`
- `Carduus Cirsium phylogeny`
- `Carduinae Hyb-Seq`
- `Cirsium Lophiolepis phylogeny`
- `Cirsium generic delimitation`

### Regional phylogeny

Each is crossed with `Cirsium` and `phylogeny OR phylogenomics OR transcriptome OR target capture`:

- Japan;
- Ryukyu;
- Taiwan;
- China;
- Korea;
- Russian Far East;
- North America;
- Europe;
- Southwest Asia.

### Reticulation and genome evolution

- `Cirsium hybridization`
- `Cirsium introgression`
- `Cirsium allopolyploid`
- `Cirsium polyploidy`
- `Cirsium chromosome`
- `Cirsium genome size`
- `Cirsium RADseq`
- `Cirsium chloroplast capture`
- `Cirsium cytonuclear discordance`

### Data recovery

- study title plus `dataset`, `Newick`, `Nexus`, `TreeBASE`, `Dryad`, `Mendeley Data`, `figshare`, `BioProject`, `SRA`;
- DOI searches in data repositories;
- author plus focal taxon plus `supplementary`.

## Screening workflow

### Stage 1 — machine candidate generation

Output fields:

- source database;
- query;
- title;
- year;
- DOI;
- journal;
- authors;
- abstract/snippet;
- topic flags;
- automated relevance score;
- `screening_status = unreviewed`.

Deduplication uses normalized DOI first and normalized title second.

### Stage 2 — title/abstract screening

Assign one of:

- `include_primary`;
- `include_dataset`;
- `background_only`;
- `exclude_irrelevant`;
- `duplicate`;
- `needs_full_text`.

Two questions control inclusion:

1. Does the paper contain new phylogenetic, reticulation, cytotype or taxonomic evidence?
2. Can that evidence change an EAzami topology, alternative history or sequencing decision?

### Stage 3 — full-text extraction

For included studies record:

- exact taxon/sample count;
- geographic coverage;
- marker/locus type and number;
- nuclear versus organellar evidence;
- concatenation, coalescent and/or network methods;
- rooting and outgroups;
- accession numbers and vouchers;
- tree/supplement/data availability;
- principal supported relationships;
- conflicting relationships;
- ploidy/cytotype details;
- stated ILS/hybridization interpretation;
- limitations relevant to Chapter 2;
- taxa that join the focal colour atlas.

### Stage 4 — evidence adjudication

A relationship is entered into the consensus/gap matrix only after the evidence class is explicit.

- A plastome placement can fill `maternal_history_status` but not `nuclear_tree_status`.
- A cytological cluster can fill `ploidy_or_chromosome` but not a tree node.
- A one-tip target-capture placement fills species-level coverage but not population-level coverage.
- A historical white form fills `candidate_colour_evidence` but not `extant_population_verified`.
- Conflicting high-quality nuclear analyses are retained as a topology set, not resolved by vote.

## Evidence tiers

### Tier A

- hundreds/thousands of nuclear loci or transcriptome orthogroups;
- explicit coalescent/species-tree analysis;
- decisive genome-wide admixture/allopolyploid analysis;
- reusable public matrices/tree files or raw reads preferred.

### Tier B

- several nuclear/plastid loci with broad sampling;
- regional species delimitation;
- genomic/cytological evidence interpreted on a multilocus tree.

### Tier C

- local AFLP, flow cytometry, chromosomes, hybrid fertility or taxonomic comment/reply;
- supports alternatives but is not a broad backbone.

### Tier D

- single plastome, morphology-only treatment or barcode-only record;
- used for maternal history, names, vouchers and candidate detection.

## Bias controls

- Do not search only for papers supporting repeated white loss or regain.
- Include studies showing no hybridization, no polyploidy or stable species boundaries.
- Preserve both sides of the *Lophiolepis* generic debate.
- Separate publication date from data-generation date.
- Do not assume that a recent paper supersedes an older study at every scale; a population study can remain more relevant locally.
- Do not treat citation count as evidence quality.
- Record taxon-name concepts and synonym mappings before declaring a missing tip.

## Stopping rule for the first evidence-map release

The initial map is ready when:

1. every Tier-A paper has backward and forward citation screening;
2. all global, North American and East Asian modern nuclear studies found by at least two query families are screened;
3. every focal Chapter 2 taxon has an evidence-state classification;
4. all claimed phylogenetic gaps have been checked against accepted names, synonyms, supplementary tip tables and public project metadata;
5. unresolved conflicts are represented in the consensus/gap matrix;
6. the search date, query set and number of records at each screening stage are frozen.

The map remains living and is rerun monthly by GitHub Actions after merge.

## Outputs

Curated:

- `data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_consensus_and_gaps_2026-08-10.csv`
- `docs/CIRSIUM_PHYLOGENY_STATE_OF_FIELD_2026-08-10.md`

Generated candidates:

- `data/evidence/generated/cirsium_phylogeny_literature_candidates.csv`
- `data/evidence/generated/cirsium_phylogeny_search_log.csv`

Generated outputs are evidence-discovery aids, not manuscript-ready citations until manually curated.
