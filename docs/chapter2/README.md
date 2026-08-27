# Chapter 2 — phenotype through evolutionary time

## Status

`TIME_AXIS_MAINLINE_V3.md` is the active Chapter 2 scientific source of truth.

Primary manuscript:

- `MANUSCRIPT_JEB_V2.md`
- target: **Journal of Evolutionary Biology**, Research Article

The previous function-first and simulation-centred Chapter-2 framings remain archived as evidence/programme layers, but neither defines the current Chapter 2.

## Dissertation symmetry

```text
same decomposed continuous capitulum phenotype
        │
        ├── Chapter 1 — phenotype × present-day space/environment
        │
        ├── Chapter 2 — phenotype × evolutionary time/history
        │
        └── Chapter 3 — phenotype × function/fitness
```

Chapter 2 is not restricted to traits that were environmentally significant in Chapter 1, and validated function is not required before a phenotype can enter historical analysis.

## Chapter 2 central question

> **When a complex reproductive phenotype is decomposed into continuous components, does evolutionary history preserve trait states, allow fully independent component change, or concentrate multidimensional change in shared evolutionary episodes?**

The chapter separates:

1. **state conservation** — do close relatives retain similar continuous values?
2. **recurrence** — how many changes are required for independently defined discrete states?
3. **change localization** — do large continuous changes occur on the same branches?
4. **module specificity** — does historical coordination follow present-day measurement modules?
5. **topology robustness** — which conclusions survive the rapid-radiation topology ensemble?

## Frozen phenotype bridge

The Chapter-2 continuous phenotype is reused from the frozen Azami Chapter-1 artifact rather than reconstructed from a species-level trait database.

- 46,276 strict-spatial image observations;
- 1,018,072 long-format trait rows;
- 18 continuous endpoints;
- exact continuous phenotype for 14 Japan38 concepts;
- no infraspecific-to-broad-species substitution;
- no missing-value imputation;
- no artificial discretization.

Primary time-axis units:

- orientation angle;
- LAB lightness;
- LAB chroma;
- circular hue;
- outline aspect ratio;
- outline circularity;
- outline solidity;
- width-profile CV.

Candidate continuous involucre/armature endpoints remain coverage-audit-only because only two exact concepts reach >=2 observations.

## Nuclear history scaffold

- 38 paper concepts → 39 focal biological samples;
- 40 tips including safflower outgroup;
- 236 QC nuclear loci / 176 rootable loci;
- 161,654-bp concatenated alignment;
- UFBoot 1000 / SH-aLRT 1000;
- branch lengths = substitutions/site, **not absolute time**;
- JPN20 is non-monophyletic and is not forcibly collapsed;
- JPN31 is excluded from primary phenotype history because of the frozen identity/locality conflict.

## Core result chain

### 1. Continuous states are weakly conserved

At both >=2 and >=5 observation thresholds:

- **0/8** primary units pass the BH-corrected two-sided phylogenetic-structure family;
- Pagel lambda MLE = **0** for every scalar unit.

High-depth lightness remains a directional anti-phylogenetic diagnostic, not a promoted family-level historical claim.

### 2. Discrete states recur

Authority-backed states:

- orientation: 20 resolved; ML 6; UFBoot 4–6;
- phyllary posture: 10 resolved; exactly 3 changes on all 1000 UFBoot topologies;
- stickiness: 13 resolved; exactly 5 changes on all 1000 UFBoot topologies after the merged JPN24 repair.

These are recurrence lower bounds, not convergence counts.

### 3. Continuous change is broadly coordinated

On the ML substitution-length phylogram:

- mean pairwise branch-change rho = **0.408006**;
- branch permutation P = **0.00010**.

### 4. Global coordination is topology-robust, module specificity is not

Across 1000 equal-branch UFBoot topologies:

- global mean rho median = **0.141287**;
- q05 = **0.118995**;
- fraction positive = **1.000**;
- robust-positive gate = **PASS**.

Within-minus-between module contrast:

- median = **0.112435**;
- q05 = **-0.095160**;
- fraction positive = **0.946**;
- robust-positive gate = **FAIL**.

Thus large evolutionary changes are coordinated across phenotype dimensions, but not robustly bounded by the present-day module partition.

### 5. Discrete transition overlap is topology-sensitive

Equal-branch UFBoot median transition-overlap rho:

- orientation × phyllary = **-0.0594**;
- orientation × stickiness = **-0.3870**;
- phyllary × stickiness = **0.1840**.

No discrete pair shows a consistently positive shared-transition history across branch-length-aware and topology-only layers.

## Current Chapter 2 conclusion

The evidence rejects both extremes:

- **fixed conserved syndrome** — unsupported;
- **fully independent component histories** — incomplete.

Supported bounded interpretation:

> **A complex capitulum can lose phylogenetic conservation of its component states while retaining coordinated episodes of broad phenotypic remodeling. Present-day modules do not map cleanly onto stable historical modules.**

This is not a claim of developmental/genetic modularity, adaptation, adaptive convergence or an absolute evolutionary rate.

## Active files

### Science and manuscript

- `TIME_AXIS_MAINLINE_V3.md` — current scientific line.
- `MANUSCRIPT_JEB_V2.md` — active submission draft.
- `JEB_SUBMISSION_TARGET_V1.md` — journal fit and go/no-go rules.
- `JEB_QUESTION_RESULT_FIGURE_MAP_V1.md` — question → evidence → result → figure map.
- `../../data/evidence/chapter2_jeb_main_result_table_v1.csv` — headline numerical result registry.
- `../../data/evidence/chapter2_time_axis_compute/` — frozen continuous/discrete history outputs.

### Programme disposition

- `META_SIM_DISPOSITION_V1.md` — routes prior meta-analysis and simulation work.
- `../../data/evidence/chapter2_analysis_disposition_v1.csv` — machine-readable routing ledger.
- `../RESEARCH_PLAN.md` — dissertation research plan.

### Legacy/source material

The following remain available but are not the active Chapter-2 organizing source:

- `MAINLINE_V2.md` — earlier function-first framing;
- `MANUSCRIPT_V2_OUTLINE.md` — earlier outline;
- `TRAIT_FUNCTION_EVIDENCE_V1.md` — retained for Chapter 3 function/fitness;
- `MANUSCRIPT_V1.md` — previous simulation-centred draft;
- V1/V2 figure/submission maps and claim registries.

## Where previous analyses now belong

### Chapter 1 Supplement / thesis structural methods

- v3.1 generator-family inadequacy;
- PR #119 NULL_COUPLED scalar winner;
- PR #120 held-out 0/64 failure;
- PR #123 among-only process diagnostic;
- provisional PR #122 scale-specific covariance v4.1.

These concern generation of the **present phenotype field**, not phylogenetic transition history.

### Chapter 3 — phenotype × function/fitness

- FDT1 trait-to-function evidence;
- reproductive-herbivory RR = 2.674;
- pollinator × antagonist selection mosaic;
- selection leverage and demographic transmission;
- orientation/display/stickiness/phyllary functional calibrations.

Function explains why historical changes may matter; it does not determine which traits are admitted to Chapter 2.

## Later origin/convergence layer

Repeated states still require origin discrimination. The next discriminator should link, where possible, the same biological individuals:

`standardized phenotype + nuclear population genomics + plastid haplotype + cytotype`.

Only after origin, ecological association, equivalent function and reproductive fitness are resolved can repeated histories be promoted to functional/adaptive convergence.

## Prohibited shortcuts

- current covariance → realized evolutionary history;
- low phylogenetic signal → convergence;
- repeated minimum-change steps → independent origin or adaptive convergence;
- coordinated branch change → shared developmental/genetic mechanism;
- substitutions/site → absolute time or rate/Myr;
- image phenotype → validated function;
- simulation adequacy → realized evolutionary history.
