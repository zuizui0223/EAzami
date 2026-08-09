# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic framework needed to test those transitions.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project focuses initially on Japan, the Ryukyu Islands, Taiwan and China. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Two linked objectives

1. **Flower-colour evolution:** discover repeated white-flower origins, within-lineage polymorphism and credible coloured -> white -> coloured histories.
2. **East Asian nuclear phylogeny:** use existing phylotranscriptomic backbones where they are strong, identify missing/unstable taxa and populations, and fill transition-critical gaps with RAD-seq.

RAD-seq is therefore not a generic re-sequencing of taxa already resolved by transcriptomics. Sampling priority is based on information gain for colour-transition history, missing nuclear placement, ploidy/reticulation, geographic backbone value and population replication.

## Chapter logic

1. Build a population-aware flower-colour atlas from literature, herbarium material, public photographs and field observations.
2. Audit every atlas taxon against published nuclear phylogenomics, plastid-only evidence and chromosome/ploidy information.
3. Rank RAD-seq targets: transition-critical gaps first, major East Asian backbone gaps second, replication third.
4. Reconstruct flower-colour history across a topology set rather than one assumed tree.
5. Identify independent pigment-loss events, within-lineage polymorphisms and candidate regain/reactivation branches.
6. Select replicated transition systems for pigment chemistry, floral transcriptomics and targeted population genomics/WGS.
7. Test selection only after evolutionary direction and molecular mechanism are sufficiently resolved.

## Current published nuclear anchors

### Chang et al. 2026 — Sinocirsium/Arenicola framework

The study sampled 12 *Cirsium* taxa and 33 *Cirsium* samples, resolving the *C. japonicum* complex, *C. brevicaule*, *C. irumtiense* and related lineages with thousands of orthogroups. Raw reads are under BioProject `PRJNA1311153`.

Important consequence: species-level placement of the core Ryukyu pair and Taiwanese *C. japonicum* varieties should not be unnecessarily repeated. RAD-seq effort moves to population structure, gene flow, missing sister/bridge taxa and causal colour-associated variation.

### Chang et al. 2025 — Nipponocirsium framework

The study sampled seven *Cirsium* species across Taiwan and Japan and documented diploid/tetraploid/dysploid structure. Raw reads are under BioProject `PRJNA1158676`.

Important consequence: Nipponocirsium is an existing nuclear anchor and a ploidy-aware test case, not an unstructured phylogeny gap.

See `docs/EVIDENCE_AUDIT_2026-08-09.md` and `data/evidence/published_nuclear_phylogeny_coverage_seed.csv`.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times in East Asian *Cirsium*.
- **H2 — regain/reactivation:** at least some coloured lineages descend from an inferred white ancestor or white intermediate.
- **H3 — regulatory reuse:** repeated white-flower transitions disproportionately involve regulatory suppression of a conserved anthocyanin pathway rather than repeated irreversible loss of structural genes.
- **H4 — repeated molecular route:** independent regain events, if present, reactivate homologous regulatory modules or ancestral functional haplotypes.
- **H5 — phylogeny matters:** targeted nuclear RAD-seq changes some colour-history inferences by resolving taxa/populations missing from current regional backbones.

`Regain` and `reactivation` are hypotheses, not assumed states. They require concordant support from ancestral-state reconstruction, population history and molecular evidence.

## Initial focal systems

- Ryukyu Arenicola: *C. brevicaule* (white) and *C. irumtiense* (coloured) — population-level history/gene flow rather than repeating species delimitation.
- Taiwan *C. japonicum* complex: fixed-white var. *albescens* and colour-polymorphic var. *takaoense* — paired morph/population sampling and causal genomics.
- Additional Japanese and Chinese white/coloured sister-lineage or within-taxon polymorphism candidates discovered by the atlas.

## Repository structure

- `docs/RESEARCH_PLAN.md` — aims, hypotheses, analyses and decision rules
- `docs/EVIDENCE_AUDIT_2026-08-09.md` — source-backed audit of current nuclear phylogenomics and priorities
- `docs/PHYLOGENY_GAP_AND_RADSEQ_PLAN.md` — RAD-seq gap logic
- `data/schema/flower_colour_records.csv` — observation-level flower-colour schema
- `data/schema/taxon_transition_candidates.csv` — transition-screening schema
- `data/schema/phylogeny_gap_audit.csv` — taxon/population gap and priority schema
- `data/evidence/published_nuclear_phylogeny_coverage_seed.csv` — published nuclear coverage seed
- `sampling/SAMPLING_DESIGN.md` — field and molecular sampling logic
- `analysis/validate_colour_atlas.py` — atlas schema/QC validator
- `analysis/build_phylogeny_gap_from_evidence.py` — joins colour atlas to published nuclear coverage
- `analysis/prioritize_radseq_sampling.py` — ranks RAD-seq candidates
- `molecular/` — pigment, RNA-seq and genomic workflows
- `manuscript/` — Chapter 2 manuscript materials

## First executable milestones

1. Complete a vetted Japan–Ryukyu–Taiwan–China *Cirsium* master taxon table.
2. Attach population-aware flower-colour evidence to every taxon.
3. Join the atlas to published nuclear/ploidy coverage.
4. Estimate where missing taxa can change the number or direction of white/coloured transitions.
5. Freeze the first RAD-seq panel from those information-critical gaps.

No large WGS cohort should be finalized before this transition/gap screen is complete.
