# EAzami research plan — space, evolutionary history, then function

Status date: 2026-08-27

## Dissertation architecture

The same decomposed capitulum phenotype is used across three orthogonal questions:

1. **Chapter 1 — phenotype × present-day space/environment:** where continuous phenotypes occur and how within- and among-taxon associations differ.
2. **Chapter 2 — phenotype × evolutionary time/history:** which states retain phylogenetic structure, how often defined states recur, which edges are identifiable, and whether traits share transition localization.
3. **Chapter 3 — phenotype × function/fitness:** how candidate traits alter performance, interactions and reproductive fitness.

Validated function is not required before a measurable phenotype enters Chapter 2.

## Chapter 2 central question

> **Does present-day phenotypic integration persist as one shared evolutionary history?**

The analysis separates five estimands:

- present integration at within- and among-taxon scales;
- continuous phylogenetic state structure;
- minimum recurrence of independently defined discrete states;
- exact transition-placement identifiability;
- shared continuous or discrete branch localization.

The current evidence does not support either a persistent whole-capitulum module or fully independent histories. The bounded result is that present integration, recurrence and localization are empirically distinct.

## Frozen evidence

### Present phenotype

- >=5 registered-module contrast: 0.164502 within taxa vs 0.088475 among taxa;
- >=2 contrast: 0.157688 vs 0.083662;
- within/among association-matrix similarity: rho=0.3663.

### Continuous history

- eight orientation/colour/shape units;
- original corrected family: 0/8 supported at both thresholds;
- fixed JPN29 exclusion: 8/8 `two_sided_not_supported` at >=2 and >=5 family `not_evaluable`;
- original reconstruction-aware branch null: P=0.3504, FAIL;
- fixed JPN29 exclusion null: P=0.1959, FAIL.

### Discrete history

- orientation: four to six minimum changes across 1,000 topologies;
- phyllary posture: exactly three;
- stickiness: exactly five;
- transition placement more identifiable for the JPN36 phyllary edge than for any orientation edge;
- no discrete pair has consistently positive transition overlap across branch-length treatments.

## Chapter 2 paper claim

> **Present-day phenotypic integration does not imply a shared evolutionary history in a rapid thistle radiation.**

This means the available panel does not support one persistent historical capitulum module. It does not mean the traits have zero phylogenetic structure, evolve independently, arose independently or lack shared development or selection.

## JEB paper architecture

Primary submission target: **Journal of Evolutionary Biology**, Research Article.

1. Present integration is scale dependent.
2. Robust continuous state structure is not detected in the sparse exact-concept panel.
3. Three discrete state ontologies require repeated minimum changes.
4. Recurrence-count robustness differs from exact edge identifiability.
5. Continuous shared localization fails a reconstruction-aware null in both frozen panels.
6. Discrete shared localization is topology dependent.

Main figures:

- Figure 1: within/among present integration;
- Figure 2: recurrence, forced edges and state-structure decisions;
- Figure 3: original and JPN29-excluded reconstruction-aware nulls;
- Figure 4: discrete overlap and claim boundary.

## What happens to existing meta-analysis

Trait-to-function meta-analysis, reproductive herbivory, selection mosaic, demographic transmission and the JPN36 field protocol remain primary Chapter 3 evidence. They may motivate future explanations of historical patterns but do not define the Chapter 2 estimand.

## What happens to existing simulation

The v3/v4 generators model formation of the present within/among phenotype field. They remain Chapter 1 Supplement or thesis-methods material. They do not locate evolutionary events and are not historical simulations.

## Interesting repository-wide material

Use briefly in the main text or Discussion:

- 36/38 sampled Japanese concepts in the dominant radiation;
- all four observed orientation × stickiness combinations within that radiation;
- recurrence-count versus edge-identifiability contrast;
- JPN20 non-monophyly as a fail-closed admission example.

Use in Supplement:

- source-balanced Japan7 lightness non-replication;
- species-tip compression in the one morph-linked colour-polymorphism system;
- absolute-time calibration STOP;
- candidate involucre/armature coverage limitation;
- broad climate/ploidy descriptive constraint.

Do not import into the mainline:

- causal function claims from meta-analysis;
- present-state simulator outcomes as phylogenetic history;
- post-hoc endpoint or taxon substitutions;
- colour regain or anti-phylogenetic rescue claims.

## Later origin-discrimination layer

Repeated states still admit ancestral retention, lineage-specific origin, ancestral sorting, introgression and reversal. The next discriminator should link standardized phenotype, nuclear population ancestry, plastid haplotype and cytotype in the same biological individuals where possible.

## Immediate actions

1. Keep `MANUSCRIPT_JEB_V3.md` and the four generated figures as the active submission package.
2. Complete author metadata, funding and conflict fields on the separate title page.
3. Produce and inspect a line-numbered DOCX/PDF after author metadata are available.
4. Archive the submission commit and public data/code DOI by revision at the latest.
5. Do not reopen frozen analyses to obtain a favourable historical-coupling result.

## Stop rules

- no `FAIL` -> independence;
- no `not_evaluable` -> zero or absence;
- no repeated minimum change -> independent origin or adaptive convergence;
- no positive topology sign -> shared biological event;
- no substitutions/site -> absolute time or evolutionary rate;
- no global species proxy -> population-matched phenotype;
- no present-state simulation -> realized phylogenetic history.
