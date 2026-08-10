# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic framework needed to test those transitions.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project focuses initially on Japan, the Ryukyu Islands, Taiwan and China. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Two linked objectives

1. **Flower-colour evolution:** discover repeated white-flower origins, within-lineage polymorphism and credible coloured -> white -> coloured histories.
2. **East Asian nuclear phylogeny:** use existing phylotranscriptomic/target-capture backbones where they are strong, identify missing/unstable taxa and populations, and fill transition-critical gaps with RAD-seq.

RAD-seq is therefore not a generic re-sequencing of taxa already resolved by nuclear phylogenomics. Sampling priority is based on information gain for colour-transition history, missing nuclear placement, ploidy/reticulation, geographic backbone value and population replication.

## Current preliminary inference

Existing nuclear phylogenies plus source-backed flower-colour states make **repeated white-flower evolution** the leading hypothesis. **True coloured regain/reactivation is not yet demonstrated.**

A preliminary Fitch-parsimony sensitivity analysis shows why population-aware coding is essential: treating colour-polymorphic var. *takaoense* as one ambiguous `{white, coloured}` species tip requires only one minimum transition in the focal Sinocirsium topology, whereas representing its white and coloured populations separately requires two. Species-level trait matrices can therefore undercount repeated colour transitions.

See `docs/PRELIMINARY_HYPOTHESES_2026-08-09.md` and `analysis/fitch_transition_sensitivity.csv`.

## Chapter logic

1. Build a population-aware flower-colour atlas from literature, herbarium material, public photographs and field observations.
2. Audit every atlas taxon against published nuclear phylogenomics, plastid-only evidence and chromosome/ploidy information.
3. Rank RAD-seq targets: transition-critical population histories first, genuine major nuclear-backbone gaps second, replication third.
4. Reconstruct flower-colour history across a topology set rather than one assumed tree.
5. Identify independent pigment-loss events, within-lineage polymorphisms and candidate regain/reactivation branches.
6. Select replicated transition systems for pigment chemistry, floral transcriptomics and targeted population genomics/WGS.
7. Test selection only after evolutionary direction and molecular mechanism are sufficiently resolved.

## Current published nuclear anchors

### Chang et al. 2026 — Sinocirsium/Arenicola framework

The study resolves the *C. japonicum* complex, *C. brevicaule*, *C. irumtiense* and related lineages with thousands of orthogroups. Raw reads are under BioProject `PRJNA1311153`.

Important consequence: species-level placement of the core Ryukyu pair and Taiwanese *C. japonicum* varieties should not be unnecessarily repeated. RAD-seq effort moves to population structure, gene flow, missing sister/bridge taxa and causal colour-associated variation.

### Chang et al. 2025 — Nipponocirsium framework

The study resolves Japanese and Taiwanese Nipponocirsium and documents diploid/tetraploid/dysploid structure. Raw reads are under BioProject `PRJNA1158676`.

Important consequence: Nipponocirsium is an existing nuclear anchor and a ploidy-aware test case, not an unstructured phylogeny gap.

### Moreyra et al. 2025 — Japanese nuclear backbone

The 350-nuclear-locus Carduus–Cirsium phylogeny includes 38 Japanese *Cirsium* species and shows that much of the Japanese radiation already has a modern nuclear backbone. Raw reads are under BioProject `PRJNA957074`.

Important consequence: new RAD-seq in Japan should focus on white/coloured population polymorphism, unsampled species, introgression and bridge populations rather than rebuilding the species-level tree blindly.

### Reproducible recovery of deposited project tips

`analysis/recover_ncbi_project_runs.py` reconstructs the public sample set directly from official NCBI SRA metadata. It produces a run-level table, a unique-taxon summary and an exact-match audit for 32 focal East Asian taxa. This distinguishes:

- an exact public project tip;
- a paper/tree placement whose accession is still pending;
- a project-tip status that is unresolved rather than absent;
- a true modern nuclear gap after synonyms and supplements are checked;
- a species already resolved by a separate Chang nuclear dataset.

The directly verified anchor is *C. domonii* (`SAMN34240283`, `SRX21011499`, `SRR25265717`). A manual workflow at `.github/workflows/recover-ncbi-project-metadata.yml` runs the same recovery and uploads the generated tables without modifying the repository.

See `docs/PRJNA957074_RECOVERY_UPDATE_2026-08-10.md`.

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
- Japan–China bridge populations of widespread focal species where available
- Korea–NE Asia: historical white-form candidates whose extant status and nuclear placement are being audited
- additional East Asian transition systems discovered by the atlas

## Work that requires new data

Tracked as GitHub issues so it does not block current analytical work:

- #2 — paired white/coloured field sampling
- #3 — pigment chemistry, floral RNA-seq and causal-region genotyping
- #4 — RAD-seq + ploidy sampling and reticulation tests
- #5 — downstream selection tests after mechanism/history is resolved
- #6 — completion of the flower-colour atlas and literature-backed coding
- #7 — exact published tree files and branch lengths
- #8 — exact Japanese placements and Korea/NE Asia expansion

## Repository structure

- `docs/RESEARCH_PLAN.md` — aims, hypotheses, analyses and decision rules
- `docs/PRELIMINARY_HYPOTHESES_2026-08-09.md` — hypotheses from existing evidence only
- `docs/EVIDENCE_AUDIT_2026-08-09.md` — source-backed audit of current nuclear phylogenomics and priorities
- `docs/PHYLOGENY_GAP_AND_RADSEQ_PLAN.md` — RAD-seq gap logic
- `docs/PRJNA957074_RECOVERY_UPDATE_2026-08-10.md` — project-tip recovery and evidence-state rules
- `data/regional_master_taxa_seed.csv` — current source-backed East Asian master table
- `data/evidence/focal_taxa_prjna957074.txt` — focal accepted names for project recovery
- `data/evidence/prjna957074_focal_tip_recovery_2026-08-10.csv` — current accession-level audit
- `data/schema/flower_colour_records.csv` — observation-level flower-colour schema
- `data/schema/taxon_transition_candidates.csv` — transition-screening schema
- `sampling/RADSEQ_PANEL_V0_1.csv` — first hypothesis-driven RAD sampling panel
- `sampling/RADSEQ_PANEL_V0_2_EIG.csv` — proxy-information-gain-ranked panel
- `analysis/fitch_transition_sensitivity.py` — minimum transition-count sensitivity
- `analysis/directional_transition_sensitivity.py` — root-dependent loss/regain counts
- `analysis/mk_rate_sensitivity.py` — exploratory ER/ARD Mk sensitivity
- `analysis/proxy_information_gain_priority.py` — transparent decision-priority scoring
- `analysis/recover_ncbi_project_runs.py` — complete public SRA/BioSample project recovery
- `analysis/prioritize_radseq_sampling.py` — ranks RAD-seq candidates
- `tests/test_recover_ncbi_project_runs.py` — offline recovery-helper tests
- `molecular/` — pigment, RNA-seq and genomic workflows
- `manuscript/` — Chapter 2 manuscript materials

## Analyses that should continue before new field data arrive

1. Complete the source-backed East Asian colour-state atlas.
2. Recover all usable modern nuclear tip coverage and exact deposited sample metadata.
3. Run population-aware vs species-level transition sensitivity.
4. Run formal ML/stochastic ancestral-state reconstruction when exact trees and enough tips are coded.
5. Repeat across alternative published nuclear topologies / network-informed scenarios.
6. Quantify which missing taxon or population changes transition count/direction most strongly.
7. Freeze RAD-seq panel v1.0 from expected information gain rather than raw taxon count.

No large WGS cohort should be finalized before this transition/gap screen is complete.
