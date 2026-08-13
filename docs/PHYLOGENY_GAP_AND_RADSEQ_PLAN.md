# Phylogeny-gap audit and RAD-seq strategy

## Why Chapter 2 also needs a phylogenetic workstream

Existing East Asian *Cirsium* phylogenies are essential backbones, but they are not automatically sufficient for reconstructing flower-colour transitions. The Chapter 2 question depends on whether the exact white, coloured and polymorphic taxa/populations needed to distinguish alternative histories are represented by nuclear data with adequate support.

This project therefore has two linked goals:

1. reconstruct repeated loss and possible regain/reactivation of floral anthocyanin pigmentation; and
2. improve the East Asian nuclear phylogenetic framework where current sampling or marker resolution is insufficient for that inference.

The phylogeny is not an independent taxonomic side project. Sampling is prioritized by how strongly a missing lineage affects a flower-colour transition hypothesis, while still retaining a broader East Asian backbone objective.

## Why nuclear RAD-seq

East Asian *Cirsium* contains polyploid, hybridizing and reticulate lineages. Plastid loci represent a single maternally inherited history and may have limited resolution among young lineages or disagree with nuclear history after introgression/chloroplast capture. RAD-seq is therefore used to obtain many genome-wide nuclear loci across a broad taxon sample.

RAD-seq does not remove the complications caused by polyploidy. The pipeline must explicitly audit ploidy, allele depth, paralogy, missingness and locus reproducibility, and results should be compared across conservative filtering strategies.

## Three linked sampling tiers

### Tier A — transition-critical samples: highest priority

Sample any taxon/population whose phylogenetic placement can distinguish competing colour histories.

Examples:

- white and coloured members of the same nominal taxon;
- white/coloured sister-lineage candidates;
- lineages between an inferred coloured ancestor and a candidate coloured regain;
- geographically intermediate populations that may reveal introgression;
- taxa whose current placement relies only on plastid data or weakly resolved nuclear data.

Goal: make every claimed loss or regain testable rather than dependent on grafted or assumed placements.

### Tier B — backbone-gap samples: high priority

Sample accepted East Asian *Cirsium* taxa absent from a sufficiently resolved nuclear backbone, especially when they:

- represent major geographic regions or sections;
- are close relatives of Tier A taxa;
- are polyploid or taxonomically unstable;
- bridge Japanese, Ryukyu, Taiwanese and Chinese clades;
- have conflicting nuclear/plastid placements.

Goal: prevent transition counts from being biased by missing branches.

### Tier C — redundancy and population replication

Add replicate individuals/populations for:

- within-taxon colour polymorphism;
- suspected hybrid zones;
- widespread taxa with strong geographic structure;
- transition-critical taxa for which one individual would be unsafe.

Goal: distinguish species-tree signal from population structure, polymorphism or introgression.

## Gap-audit table

`data/schema/phylogeny_gap_audit.csv` tracks one row per accepted taxon or focal population. Required fields include:

- taxon and population identity;
- region;
- flower-colour evidence state;
- representation in each existing backbone;
- nuclear versus plastid data availability;
- support/resolution status;
- known or suspected ploidy;
- whether placement is transition-critical;
- RAD-seq priority and rationale.

This table is the bridge between the colour atlas and sequencing design.

## Priority score

The default conceptual score is:

`priority = transition_information + phylogeny_gap + reticulation_ploidy + geographic_backbone + replication_need`

Each component is scored 0–2. The score is a decision aid, not a biological statistic.

### 2 points

Critical: without the sample, a principal loss/regain hypothesis or major backbone gap cannot be resolved.

### 1 point

Useful: improves confidence, replication or regional coverage.

### 0 points

Low marginal information for the current chapter.

Transition information has precedence over the total score: a lineage that directly distinguishes `coloured -> white` from `coloured -> white -> coloured` is Tier A even if other components are low.

## RAD-seq analytical objectives

The primary RAD-seq products are:

1. a nuclear East Asian phylogenetic backbone with explicit support;
2. concordance/sensitivity across filtering choices relevant to polyploidy;
3. species/population clustering and detection of obvious admixture/reticulation;
4. a list of nodes where a bifurcating tree is an inadequate summary;
5. colour-state ancestral reconstruction repeated across plausible nuclear trees/networks.

The Chapter 2 colour claims must propagate phylogenetic uncertainty. A regain should not be claimed from a single weakly supported topology.

## Decision rules

- If an existing well-supported nuclear placement already resolves a transition, do not sequence that taxon merely for completeness.
- If a candidate regain depends on an unrepresented or weakly resolved lineage, it becomes Tier A.
- If nuclear and plastid histories conflict, prioritize nuclear RAD-seq replication and retain the discordance as biological information rather than forcing one tree.
- If polyploid/hybrid signal makes a single species tree unstable, use network/admixture summaries and test colour transitions over a topology set.
- Mechanistic RNA-seq/WGS follow-up is prioritized only after the focal transition remains credible across the phylogenetic sensitivity set.
