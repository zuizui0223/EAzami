# EAzami current state

Status date: 2026-08-27

## Canonical dissertation mainline

```text
shared continuous capitulum phenotype ontology
        │
        ├── Chapter 1 — phenotype × present-day space/environment
        │     where phenotypes occur; within/among variation; environmental alignment
        │
        ├── Chapter 2 — phenotype × evolutionary time/history
        │     phylogenetic state structure; recurrence; branch-wise change; historical coupling
        │
        └── Chapter 3 — phenotype × function/fitness
              trait → performance → reproductive fitness; mutualist/antagonist/abiotic pathways

Chapter 2 recurrence
        ↓
origin discrimination — nuclear population genomics + plastid haplotype + cytotype
        ↓
functional / adaptive convergence synthesis
```

This replaces the previous `phenotype → function → history` ordering. Function is not an admission gate for Chapter 2. Chapter 1 and Chapter 2 use the same phenotype ontology on orthogonal axes: space versus evolutionary history.

Active Chapter 2 sources of truth:

- `docs/chapter2/TIME_AXIS_MAINLINE_V3.md`
- `docs/chapter2/MANUSCRIPT_JEB_V1.md`
- `docs/chapter2/JEB_QUESTION_RESULT_FIGURE_MAP_V1.md`
- `docs/chapter2/META_SIM_DISPOSITION_V1.md`
- `data/evidence/chapter2_analysis_disposition_v1.csv`
- `data/evidence/chapter2_time_axis_compute/`

## Chapter 1 endpoint inherited by Chapter 2

Azami establishes the present phenotypic field rather than a fixed floral syndrome:

- categorical databases are replaced by repeated continuous image-derived measurements;
- below-taxon variation is retained rather than collapsed to one species value;
- the same observations carry geographic coordinates;
- component phenotypes have trait-specific spatial/environmental structure;
- within- and among-taxon organization are only partially aligned.

Chapter 2 does **not** select only Chapter-1 environmentally significant traits. It asks how the same measurable phenotype dimensions are distributed through evolutionary history.

## Chapter 2 — phenotype through evolutionary history

### Nuclear history scaffold

Canonical Japan38 Comp1061 compatibility reconstruction:

- 38 paper taxon concepts;
- 39 focal biological samples;
- 40 tips including safflower outgroup;
- 241 frozen locus universe / 236 QC loci / 176 rootable loci;
- 161,654-bp concatenated alignment;
- IQ-TREE with UFBoot 1000 and SH-aLRT 1000;
- branch lengths = substitutions/site, **not absolute time**;
- JPN20 is represented by two non-monophyletic samples in ML and 0/1000 UFBoot trees and is not forcibly collapsed;
- JPN31 is excluded from primary phenotype-history inference because of the frozen identity/locality conflict.

Published phylogenomics provides the broader context: 36/38 sampled Japanese concepts belong to the dominant Pleistocene Japanese radiation, while the compatibility tree is used for the focal reproducible trait-history analyses.

### Continuous phenotype recovery

Azami compute-only PR #77 reused the frozen Chapter-1 artifact rather than rebuilding phenotype data for the phylogeny:

- 46,276 strict-spatial observations;
- 1,018,072 long-format trait rows;
- 18 continuous endpoints;
- exact Japan38 continuous-trait coverage for 14 concepts;
- no broad-species substitution for infraspecific concepts;
- no missing-data imputation;
- no discretization to increase historical coverage.

Primary Chapter-2 continuous units:

1. orientation angle;
2. CIELAB lightness;
3. CIELAB chroma;
4. circular hue;
5. outline aspect ratio;
6. outline circularity;
7. outline solidity;
8. width-profile CV.

Main threshold = >=2 observations per exact concept; high-depth sensitivity = >=5. Candidate continuous involucre/armature endpoints remain coverage-audit-only because only two exact concepts reach >=2 observations.

### Result 1 — trait states are weakly conserved

Across the eight primary continuous inferential units:

- **0/8** pass the two-sided BH-corrected phylogenetic-structure family at >=2;
- **0/8** pass at >=5;
- Pagel lambda MLE = **0** for every scalar unit at both thresholds.

The high-depth lightness subset retains a strong directional anti-phylogenetic diagnostic (rho = -0.707; exact two-sided P = 0.0444), but it does not survive the eight-unit two-sided family (q = 0.356). Therefore Chapter 2 does not promote a universal anti-phylogenetic colour claim.

Supported statement:

> **The measured continuous capitulum states are not strongly conserved by relatedness in the current exact-concept Japanese panel.**

### Result 2 — discrete states recur

Authority-backed discrete histories remain separate from image-derived continuous metrics:

- **orientation:** 20 resolved; ML minimum 6; UFBoot 4–6, median 5;
- **phyllary posture:** 10 resolved; exactly 3 minimum changes on all 1000 UFBoot topologies;
- **stickiness:** 13 resolved after the merged JPN24 authority repair; ML minimum 5 and **1000/1000 UFBoot topologies = 5**.

These are recurrence lower bounds. They are not counts of adaptive convergence or proof of independent origin.

### Result 3 — large continuous changes are coordinated across traits

On the substitution-length ML phylogram, BM-conditional branch-change magnitudes show broad positive coordination:

- mean of 28 pairwise branch-change Spearman correlations = **0.408006**;
- independent-branch permutation P = **0.00010**.

This is not simply a present-day covariance result. It asks whether large reconstructed changes in different continuous phenotype dimensions occur on the same branches.

### Result 4 — global coordination is topology-robust, module specificity is not

A branch-length-free sensitivity set every non-root branch to 1.0 and repeated the continuous branch-change analysis across all 1000 raw UFBoot topologies.

Global mean pairwise branch-change correlation:

- usable topologies = **1000/1000**;
- median rho = **0.141287**;
- 5th percentile = **0.118995**;
- 95th percentile = **0.199615**;
- fraction positive = **1.000**.

Thus the global coordinated-change tendency survives topology uncertainty and removal of substitution-length information, although its magnitude is weaker than on the ML phylogram.

Module-specific coordination does **not** meet the preregistered topology-robust rule:

- within-minus-between median = **0.112435**;
- 5th percentile = **-0.095160**;
- fraction positive = **0.946**.

Supported statement:

> **Evolutionary remodeling is broadly coordinated across phenotype dimensions, but the coordination is not confined robustly to the present-day measurement modules.**

### Result 5 — discrete transition overlap is topology-sensitive

With the latest authority states, branch-length-aware ML overlap can be positive for some pairs, especially orientation × stickiness, but equal-branch UFBoot sensitivity changes the pattern:

- orientation × phyllary: median rho = **-0.0594**, fraction positive = **0.349**;
- orientation × stickiness: median rho = **-0.3870**, fraction positive = **0.009**;
- phyllary × stickiness: median rho = **0.1840**, fraction positive = **0.782**.

Therefore no discrete pair has a consistently positive shared-transition history across branch-length-aware and topology-only layers.

## Current Chapter 2 interpretation

The current evidence rejects both extreme simplifications:

1. **fixed conserved syndrome** — unsupported because continuous trait states show little robust phylogenetic conservation and multiple discrete traits require repeated changes;
2. **fully independent trait histories** — also incomplete because large continuous changes concentrate on shared evolutionary branches across every bootstrap topology.

The bounded interpretation is:

> **A complex capitulum can lose phylogenetic conservation of its component states while retaining coordinated episodes of broad phenotypic remodeling. Present-day modules do not map cleanly onto stable historical modules.**

This is a historical pattern claim, not a developmental-genetic mechanism, adaptation claim, or absolute evolutionary-rate result.

## Submission target

Primary target: **Journal of Evolutionary Biology — Research Article**.

Reason: the paper asks a general evolutionary question about multivariate phenotype history, combines morphology/phylogenetics/macroevolution, explicitly propagates topology uncertainty, and contains informative negative results. The manuscript is organized around a general distinction among **state conservation, recurrence, and change localization**, not around Cirsium natural history alone.

Current title:

> **Coordinated evolutionary change without a conserved phenotypic syndrome in a rapid thistle radiation**

Stretch target: *Evolution* only if the general branch-change result is strengthened enough to justify a broader conceptual claim. Plant-focused fallback: *Evolutionary Journal of the Linnean Society* / *Botanical Journal of the Linnean Society* if generality is judged insufficient for JEB.

## Where the meta-analysis and simulations go

### Chapter 1 Supplement / thesis structural methods

Retain, but do not call these evolutionary transition histories:

- v3.1 generator-family inadequacy;
- PR #119 NULL_COUPLED scalar-target winner;
- PR #120 held-out support geometry 0/64;
- PR #123 among-only process diagnostic;
- draft PR #122 scale-specific covariance v4.1.

These address how the **present within/among phenotypic field** can be generated statistically.

### Chapter 2 Supplement

- detailed Japan-origin evidence ledger;
- absolute-time calibration/blocking audit;
- coverage and taxon-concept reconciliation;
- full topology-sensitivity distributions;
- external repeated-evolution benchmark if completed.

### Chapter 3 — function/fitness

Move the functional meta-synthesis here as primary evidence rather than burying it in Chapter 2:

- FDT1 trait-to-function evidence;
- Cirsium reproductive-herbivory RR = 2.674 (95% CI 2.388–2.993);
- pollinator × antagonist selection mosaic;
- selection leverage;
- demographic transmission;
- orientation/display/stickiness/phyllary functional calibrations.

Function/fitness is used later to explain **why** historical changes occurred and whether repeated histories can be promoted to adaptive convergence.

## Later origin and convergence gates

Repeated states still allow:

- ancestral retention;
- independent lineage-specific change;
- ancestral polymorphism / sorting;
- introgression / gene flow;
- hybridization / cytoplasmic capture;
- reversal or re-expression.

Next origin discriminator should link the same biological individuals where possible:

- standardized phenotype;
- nuclear population genomics;
- plastid haplotype;
- cytotype / genome size.

Claim ladder remains:

`repeated state → independent origin → repeated ecological association → same/equivalent function → reproductive fitness → functional/adaptive convergence`.

## Immediate executable priorities

1. finish the JEB manuscript against the frozen continuous/discrete topology-sensitivity results;
2. make the main figure set: conceptual state-vs-change distinction, continuous trait/state panel, discrete recurrence tree, branch-change coordination/topology sensitivity;
3. keep JPN15 phyllary posture unknown unless an exact authority safely maps it to the frozen ontology; it is not a license to invent a state;
4. do not reopen colour acquisition solely to rescue an anti-phylogenetic sign;
5. do not run more present-state generator families for Chapter 2;
6. keep function/fitness meta-analysis intact for Chapter 3.

## Stop rules

- no present covariance → historical mechanism shortcut;
- no repeated state → independent origin shortcut;
- no repeated state → adaptive convergence shortcut;
- no branch-change coordination → shared developmental/genetic mechanism shortcut;
- no substitutions/site → absolute time or rate/Myr shortcut;
- no image-derived phenotype → validated function shortcut;
- no simulation adequacy → realized evolutionary history shortcut.
