# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic framework needed to test those transitions.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project focuses initially on Japan, the Ryukyu Islands, Taiwan and China, and expands concentrically through Korea and the Russian Far East when those populations change a colour-history inference. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Two linked objectives

1. **Flower-colour evolution:** discover repeated white-flower origins, within-lineage polymorphism and credible coloured -> white -> coloured histories.
2. **East Asian nuclear phylogeny:** use existing phylotranscriptomic/target-capture backbones where they are strong, identify missing/unstable taxa and populations, and fill transition-critical gaps with target capture, RAD-seq or resequencing at the appropriate scale.

RAD-seq is therefore not a generic re-sequencing of taxa already resolved by nuclear phylogenomics. Sampling priority is based on information gain for colour-transition history, missing nuclear placement, ploidy/reticulation, geographic backbone value and population replication.

## Current preliminary inference

Existing nuclear phylogenies plus source-backed flower-colour states make **repeated white-flower evolution** the leading hypothesis. **True coloured regain/reactivation is not yet demonstrated.**

A preliminary Fitch-parsimony sensitivity analysis shows why population-aware coding is essential: treating colour-polymorphic var. *takaoense* as one ambiguous `{white, coloured}` species tip requires only one minimum transition in the focal Sinocirsium topology, whereas representing its white and coloured populations separately requires two. Species-level trait matrices can therefore undercount repeated colour transitions.

See `docs/PRELIMINARY_HYPOTHESES_2026-08-09.md` and `analysis/fitch_transition_sensitivity.csv`.

## Chapter logic

1. Build a population-aware flower-colour atlas from literature, herbarium material, public photographs and field observations.
2. Audit every atlas taxon against published nuclear phylogenomics, plastid-only evidence and chromosome/ploidy information.
3. Rank sequencing targets: transition-critical population histories first, genuine major nuclear-backbone gaps second, replication third.
4. Reconstruct flower-colour history across a topology set rather than one assumed tree.
5. Identify independent pigment-loss events, within-lineage polymorphisms and candidate regain/reactivation branches.
6. Select replicated transition systems for pigment chemistry, floral transcriptomics and targeted population genomics/WGS.
7. Test selection only after evolutionary direction and molecular mechanism are sufficiently resolved.

## State of *Cirsium* phylogeny

The accurate current summary is neither “the phylogeny is solved” nor “almost nothing is known.”

- The **deep Cardueae/Carduinae backbone** is now strongly resolved by Hyb-Seq.
- A broad **global species-level *Cirsium* nuclear backbone** now exists from 350-locus target capture.
- **Japan, North America and focal Taiwan/Ryukyu clades** have modern regional nuclear frameworks.
- **Generic circumscription remains actively debated**, especially broad *Cirsium* versus *Lophiolepis* and other segregates.
- **Population-level colour-morph history, introgression and cytotype variation** remain unresolved in the focal East Asian systems.
- Complete plastomes and small plastid trees are retained as **maternal-history evidence**, not treated as substitutes for a multilocus nuclear species tree.
- Hybridization, incomplete lineage sorting, allopolyploidy, aneuploidy and B chromosomes require tree/network and ploidy-aware sensitivity analyses.

The project now maintains an evidence-typed state-of-field map rather than relying only on Chang and Moreyra:

- `docs/CIRSIUM_PHYLOGENY_STATE_OF_FIELD_2026-08-10.md`
- `data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_consensus_and_gaps_2026-08-10.csv`
- `docs/CIRSIUM_PHYLOGENY_SYSTEMATIC_SEARCH_PROTOCOL.md`

Automated Crossref and Europe PMC searches produce **unreviewed candidates only**. They never enter the curated evidence registry automatically. A monthly/manual GitHub Actions workflow reruns the candidate search and uploads the evidence-discovery files as an artifact.

## Current published nuclear anchors

### Herrando-Moraira et al. 2019 — deep Cardueae framework

Hyb-Seq across Cardueae provides the deep nuclear species-tree/outgroup framework and openly archived alignments, gene trees and species trees. Nuclear and plastid histories are retained separately because some cytonuclear discordance persists.

### Moreyra et al. 2023/2025 — Carduinae and global *Cirsium*

The 2023 Hyb-Seq study resolves major Carduinae lineages and the 2025 study provides the largest *Cirsium* species-level nuclear framework to date: 350 nuclear loci, 299 plants and 251 taxa, including 38 Japanese species. Raw reads for the 2025 study are under BioProject `PRJNA957074`.

Important consequence: new sequencing should not blindly rebuild the global or Japanese species tree. First recover exact tips, synonyms and tree artifacts, then sequence only genuine transition-critical gaps or populations.

### Chang et al. 2026 — Sinocirsium/Arenicola framework

The study resolves the *C. japonicum* complex, *C. brevicaule*, *C. irumtiense* and related lineages with thousands of orthogroups. Raw reads are under BioProject `PRJNA1311153`.

Important consequence: species-level placement of the core Ryukyu pair and Taiwanese *C. japonicum* varieties should not be unnecessarily repeated. RAD-seq effort moves to population structure, gene flow and causal colour-associated variation.

### Chang et al. 2025 — Nipponocirsium framework

The study resolves Japanese and Taiwanese Nipponocirsium and documents diploid/tetraploid/dysploid structure. Raw reads are under BioProject `PRJNA1158676`.

Important consequence: Nipponocirsium is an existing nuclear anchor and a ploidy-aware test case, not an unstructured phylogeny gap.

### Reproducible recovery of deposited project tips

`analysis/recover_ncbi_project_runs.py` reconstructs the public sample set directly from official NCBI SRA metadata. It produces a run-level table, a unique-taxon summary and an exact-match audit for focal East Asian taxa. This distinguishes:

- an exact public project tip;
- a paper/tree placement whose accession is still pending;
- a project-tip status that is unresolved rather than absent;
- a true modern nuclear gap after synonyms and supplements are checked;
- a species already resolved by a separate Chang nuclear dataset.

The directly verified anchor is *C. domonii* (`SAMN34240283`, `SRS18284452`, `SRX21011499`, `SRR25265717`). A manual workflow at `.github/workflows/recover-ncbi-project-metadata.yml` runs the same recovery and uploads the generated tables without modifying the repository.

See `docs/PRJNA957074_RECOVERY_UPDATE_2026-08-10.md` and `docs/PRJNA957074_RECOVERY_RUNBOOK.md`.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times in East Asian *Cirsium*.
- **H2 — regain/reactivation:** at least some coloured lineages descend from an inferred white ancestor or white intermediate.
- **H3 — regulatory reuse:** repeated white-flower transitions disproportionately involve regulatory suppression of a conserved anthocyanin pathway rather than repeated irreversible loss of structural genes.
- **H4 — repeated molecular route:** independent regain events, if present, reactivate homologous regulatory modules or ancestral functional haplotypes.
- **H5 — history alternatives:** some apparent loss/regain events are better explained by ancestral polymorphism, introgression or reticulate/polyploid history.

`Regain` and `reactivation` are hypotheses, not assumed states. They require concordant support from ancestral-state reconstruction, population history and molecular evidence.

## Initial focal systems

- Ryukyu Arenicola: *C. brevicaule* (white) and *C. irumtiense* (coloured)
- Taiwan Sinocirsium: fixed-white var. *albescens* and colour-polymorphic var. *takaoense*
- Taiwan Nipponocirsium: white *C. kawakamii* vs coloured *C. tatakaense* / *C. pengii*
- Japan: within-species white/coloured *C. pendulum* and *C. sieboldii*
- Japan–China/Korea bridge populations of widespread focal species
- Korea–NE Asia: historical white-form candidates whose extant status and nuclear placement are being audited
- additional East Asian transition systems discovered by the atlas and systematic evidence map

## Work tracked as GitHub issues

- #2 — paired white/coloured field sampling
- #3 — pigment chemistry, floral RNA-seq and causal-region genotyping
- #4 — RAD-seq + ploidy sampling and reticulation tests
- #5 — downstream selection tests after mechanism/history is resolved
- #6 — completion of the flower-colour atlas and literature-backed coding
- #7 — exact published tree files and branch lengths
- #8 — exact Japanese placements and Korea/NE Asia expansion
- #9 — systematic global evidence map for phylogeny, reticulation and cytogenetics

## Repository structure

### Research and interpretation

- `docs/RESEARCH_PLAN.md` — aims, hypotheses, analyses and decision rules
- `docs/PRELIMINARY_HYPOTHESES_2026-08-09.md` — hypotheses from existing evidence only
- `docs/CIRSIUM_PHYLOGENY_STATE_OF_FIELD_2026-08-10.md` — current global and East Asian phylogenetic synthesis
- `docs/CIRSIUM_PHYLOGENY_SYSTEMATIC_SEARCH_PROTOCOL.md` — reproducible evidence-map protocol
- `docs/EVIDENCE_AUDIT_2026-08-09.md` — source-backed audit of nuclear phylogenomics and priorities
- `docs/PHYLOGENY_GAP_AND_RADSEQ_PLAN.md` — sequencing-gap logic
- `docs/EXISTING_DATA_WORKSTREAM_STATUS_2026-08-10.md` — existing-data work vs new-data blockers

### Curated evidence

- `data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv` — evidence-typed primary literature/data registry
- `data/evidence/cirsium_phylogeny_consensus_and_gaps_2026-08-10.csv` — consensus, conflicts and true gaps
- `data/evidence/cirsium_phylogeny_search_queries.txt` — versioned search query families
- `data/regional_master_taxa_seed.csv` — current source-backed East Asian master table
- `data/evidence/focal_taxa_prjna957074.txt` — focal accepted names for project recovery
- `data/evidence/prjna957074_focal_tip_recovery_2026-08-10.csv` — current accession-level audit

### Analysis and automation

- `analysis/recover_cirsium_phylogeny_literature.py` — Crossref/Europe PMC candidate discovery and deduplication
- `.github/workflows/recover-cirsium-phylogeny-literature.yml` — monthly/manual literature candidate recovery
- `tests/test_recover_cirsium_phylogeny_literature.py` — offline parser/deduplication tests
- `analysis/recover_ncbi_project_runs.py` — complete public SRA/BioSample project recovery
- `analysis/fitch_transition_sensitivity.py` — minimum transition-count sensitivity
- `analysis/directional_transition_sensitivity.py` — root-dependent loss/regain counts
- `analysis/mk_rate_sensitivity.py` — exploratory ER/ARD Mk sensitivity
- `analysis/proxy_information_gain_priority.py` — transparent decision-priority scoring
- `analysis/prioritize_radseq_sampling.py` — ranks sequencing candidates

### Sampling and molecular follow-up

- `data/schema/flower_colour_records.csv` — observation-level flower-colour schema
- `data/schema/taxon_transition_candidates.csv` — transition-screening schema
- `sampling/RADSEQ_PANEL_V0_1.csv` — first hypothesis-driven RAD sampling panel
- `sampling/RADSEQ_PANEL_V0_2_EIG.csv` — proxy-information-gain-ranked panel
- `molecular/` — pigment, RNA-seq and genomic workflows
- `manuscript/` — Chapter 2 manuscript materials

## Analyses that should continue before new field data arrive

1. Complete the systematic phylogeny evidence map and exact tree/sample recovery.
2. Complete the source-backed East Asian colour-state atlas.
3. Harmonize accepted names, historical names and alternative generic combinations.
4. Join nuclear, plastid, ploidy, reticulation and flower-colour evidence without collapsing their evidence levels.
5. Run population-aware vs species-level transition sensitivity.
6. Run formal ML/stochastic ancestral-state reconstruction when exact trees and enough tips are coded.
7. Repeat across alternative nuclear topologies and network-informed scenarios.
8. Quantify which missing taxon or population changes transition count/direction most strongly.
9. Freeze target-capture/RAD panel v1.0 from expected information gain rather than raw taxon count.

No large WGS cohort should be finalized before this transition/gap screen is complete.
