# EAzami research plan — diversity breadth to historical depth

Status date: 2026-08-28

## Active standalone rule

Chapter 1 asks how broad capitulum diversity is across present space and environment. Chapter 2 asks how deep independently assembled capitulum diversity is in phylogenetic and biogeographic history. This is a conceptual handoff, not a data handoff: EAzami cannot require Azami results, phenotype artifacts or significance-selected traits.

The active Chapter 2 question is:

> **How much recurrent change is required in the traits that form alternative capitulum configurations within a young Japanese thistle radiation, and which evolutionary events remain identifiable under phylogenetic and observation uncertainty?**

The full pipeline, 17-item inventory, PR #126 disposition and JEB gate are frozen in `docs/chapter2/DIVERSITY_DEPTH_STANDALONE_V1.md`. The five-group main result selection is frozen in `docs/chapter2/CHAPTER2_CORE_RESULT_RECOVERY_V1.md` and `data/evidence/chapter2_core_result_recovery_v1.csv`. The public-evidence historical core is scientifically complete. Zero comparable scalar Japan38 tips limits the continuous extension but is not a Chapter 2 completion gate. The prior present-integration question and reconstruction-aware negative results remain audit history.

Completed continuous, niche and cytotype screens are retained as Supporting Information boundaries. They are no longer presented alongside the five main result groups as if every available analysis were an equal Chapter 2 contribution.

## Dissertation architecture

The same decomposed capitulum phenotype is used across three orthogonal questions:

1. **Chapter 1 — phenotype × present-day space/environment:** where continuous phenotypes occur and how within- and among-taxon associations differ.
2. **Chapter 2 — phenotype × evolutionary time/history:** which states retain phylogenetic structure, how often defined states recur, which edges are identifiable, and whether traits share transition localization.
3. **Chapter 3 — own phylogenomics × linked phenotype/function:** build a Japan-wide RAD-seq sensitivity phylogeny/network, test the Chapter 2 histories that remain admissible, then evaluate candidate mechanisms and fitness under separate causal designs.

Validated function is not required before a measurable phenotype enters Chapter 2.

## Chapter 2 central question

> **How much recurrent change is required in three traits forming capitulum configurations within the dominant radiation, and why are recurrence counts more recoverable than individual events?**

The primary analysis separates five estimands:

- observed configuration diversity within the dominant radiation;
- minimum recurrence of independently defined discrete states;
- exact transition-placement identifiability;
- shared discrete branch localization;
- loss of event information under species-tip compression;

Prospective discriminatory sampling is then derived from the remaining histories; it is a design output rather than a sixth empirical estimand.

The current evidence does not require a shared whole-capitulum history and does not prove fully independent histories. Recurrence and localization are empirically distinct.

## Supporting and legacy frozen evidence

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

> **A dominant young radiation contains multiple capitulum configurations and requires repeated changes in three constituent traits, while recurrence counts remain more recoverable than the individual evolutionary events responsible for them.**

This **configuration diversity plus recurrent trait change** result is the active biological contribution; unsupported common localization is a secondary boundary rather than the headline.

The independent seven-taxon continuous diagnostic does not detect corrected topology-robust retention and remains supporting evidence only. This does not mean the traits have zero phylogenetic structure, are labile, evolve independently, arose independently or lack shared development or selection.

## JEB paper architecture

Primary submission target: **Journal of Evolutionary Biology**, Research Article.

1. Establish that 36/38 sampled concepts belong to the dominant radiation and enumerate observed authority-backed configurations within it.
2. Show that three discrete state ontologies require repeated minimum changes.
3. Separate recurrence-count robustness from exact edge identifiability.
4. Use the species-tip compression audit to expose a second event-resolution limit.
5. Treat overlap, continuous, niche and cytotype analyses as boundary tests rather than additional discovery claims.
6. Convert unresolved histories into predeclared Chapter 3 sample priorities and falsifiers.

Main figures:

- Figure 1: dominant-radiation context, independent trait admission and observed configuration diversity;
- Figure 2: trait-specific recurrence-count distributions;
- Figure 3: recurrence robustness versus forced-edge localization;
- Figure 4: overlap boundary, species-tip compression and Chapter 3 sampling consequences.

The n=7 continuous diagnostic belongs in Supporting Information or the Figure 1 coverage panel, not as a headline positive result.

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

1. Keep `MANUSCRIPT_JEB_V3.md` and its generated files as an immutable audit snapshot.
2. Use `MANUSCRIPT_JEB_V4.md` as the active standalone text and rebuild the four-figure package around its public-history result order.
3. Freeze the Chapter 3 RAD-seq/phenotype sample ledger from `chapter2_to_chapter3_sampling_priorities_v1.csv` without treating it as field authorization.
4. Preserve the exact n=7 negative diagnostic and do not add/remove traits or taxa to obtain a favourable result.
5. Build the anonymous DOCX and complete reference, declarations and data-availability audits.

## Stop rules

- no `FAIL` -> independence;
- no `not_evaluable` -> zero or absence;
- no repeated minimum change -> independent origin or adaptive convergence;
- no positive topology sign -> shared biological event;
- no substitutions/site -> absolute time or evolutionary rate;
- no global species proxy -> population-matched phenotype;
- no present-state simulation -> realized phylogenetic history.
