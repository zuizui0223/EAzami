# JEB question–result–figure map v5

Status date: 2026-09-01  
Status: **ACTIVE FOR MANUSCRIPT JEB V5**

The paper-level empirical sequence is now:

**repeated evolutionary depth → shared-history test → present environmental correspondence → historical trajectory test → repeated-phenotype natural experiment → whole-capitulum synthesis**.

The central falsifiable question is no longer only whether capitulum traits changed repeatedly. It is also:

> **When a similar phenotype occurs repeatedly, does the same environmental direction recur across lineages and through time?**

A negative answer is retained as evidence for scale dependence, origin–maintenance decoupling or driver switching rather than discarded as a failed replication.

| Question | Estimand | Frozen result | Main display | Claim ceiling |
|---|---|---|---|---|
| Q1. How deep is capitulum diversity? | minimum changes + exact relative lineage-depth envelopes | orientation 4–6; phyllary 3; stickiness 5; median depth envelopes 0.795–0.994, 0.695–1.000, 0.937–0.954 | Figure 1 | repeated historical reassembly, not independent origins or rates |
| Q2. Did the modules repeatedly change on the same branches? | branch-aware and equal-branch shared-localization diagnostics | 0/3 discrete trait pairs pass the robust shared-localization rule | Figure 2 | rejects simple synchronized-history model, not complete independence |
| Q3. Does present orientation ecology point to the same hydric domain across scales, and did the origin trajectory align? | global BIO12 state-space result + East-Asian BIO15/BIO1 PGLS + chronology × palaeolocation PALEO-PGEM cosine | current hydric-domain correspondence; 94 age pairs × 4 regions = 376 origin scenarios; cosine q05 −0.799, median −0.065, q95 +0.609; origin unresolved | Figure 3 | present hydric candidate; historical origin driver not identified |
| Q4. Do repeated white states occur under the same current radiation context? | two dated sister-system phenotype contrasts + pair-level current RSDS + within-taxon slope | chroma lower in both white lineages; Arenicola RSDS concordant, Taiwan RSDS reversed; pair-level concordance 1/2; pooled within-taxon beta −0.4065 | Figure 4 | lineage-/scale-dependent current correspondence; not historical solar causation |
| Q5. Is the whole capitulum one synchronized syndrome, fully independent modules, or partial coordinated remodelling? | discrete shared-history boundary + 18-D present integration + repeated coarse image geometry | 0/3 shared transition pairs; within-among rho=0.3663; white lineages share circularity↑, solidity↑, visible-floret fraction↓ but fine geometry is heterogeneous | Figure 5 | partial module covariance; no common mechanism, convergence or adaptation |

## Figure 1 — Evolutionary depth differs among capitulum modules

### Panel a — Radiation context and coverage

- compact Japan38 scaffold showing the dominant Japanese radiation;
- 36/38 sampled concepts in the dominant radiation;
- trait-state coverage bars: orientation n=20, phyllary posture n=10, stickiness n=13;
- mark JPN20 non-monophyly and JPN31 exclusion as admission notes, not biological results.

### Panel b — Minimum-change distributions

- orientation: 4–6 across 1,000 UFBoot topologies, ML=6;
- phyllary posture: exactly 3;
- stickiness: exactly 5.

Label as **minimum changes**, never origins or rates.

### Panel c — Relative lineage-depth envelopes

Plot ML and bootstrap median lower–upper envelopes:

- orientation 0.795–0.994 bootstrap median envelope;
- phyllary 0.695–1.000;
- stickiness 0.937–0.954.

Axis: `relative lineage-depth (1 = terminal; topology only, not calendar time)`.

## Figure 2 — Transition localization rejects a simple synchronized-history model

### Panel a — Named-edge concentration

Retain the accepted post-JPN24 values:

- orientation JPN36 = 0.227;
- phyllary JPN36 = 0.728;
- stickiness JPN06 = 0.995;
- stickiness JPN36 = 0.707;
- stickiness JPN30 = 0.545;
- stickiness nine-tip internal edge = 0.681.

### Panel b — Pairwise transition-excess overlap

Show branch-aware point estimates against equal-branch bootstrap distributions for:

- orientation × phyllary;
- orientation × stickiness;
- phyllary × stickiness.

### Panel c — Decision

Large text/compact matrix:

`0 / 3 trait pairs pass the robust shared-transition-localization rule`.

Interpretation: the data reject a simple common-lability/synchronized-history model. Do not label the traits genetically or developmentally independent.

## Figure 3 — Orientation: current hydric correspondence versus unresolved origin trajectory

### Panel a — Current state-space bridge

Show the two independently defined hydric facets without merging coefficients:

- global public-image among-taxon orientation × BIO12: beta=+0.304359, q=0.021;
- East-Asian downward-minus-upward BIO15: +1.320 to +1.330 SD across six accepted topologies;
- East-Asian BIO1: −0.975 to −0.967 SD;
- BIO15 and BIO1 signs retained in 54/54 topology × species-LOO fits.

Caption language: **hydric-domain correspondence across different environmental statistics**, not replicated rainfall coefficient.

### Panel b — Core-Nipponocirsium origin chronology

Schematic only:

`erect C. morii split → candidate orientation-change stem → Japanese core / Taiwan core split`.

Display:

- parent central 0.79 Ma, marginal 0.43–1.18 Ma;
- child central 0.74 Ma, interval 0.60–0.87 Ma;
- 94 topologically admissible age pairs;
- explicitly state `cross-study scenario envelope, not joint posterior`.

### Panel c — Palaeolocation envelope

Four regional rows: Taiwan, Ryukyu corridor, southern Japan, broad East-Asian core corridor.

Plot the cosine distribution between the frozen Azami BIO1/BIO4/BIO12/BIO15 state vector and each historical branch trajectory standardized against same-duration windows.

Cross-scenario result:

- n=376;
- q05 = −0.7991;
- median = −0.0647;
- q95 = +0.6087;
- matched-window percentile median = 0.4705;
- class = `origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty`.

### Panel d — Interpretation boundary

`present hydric correspondence ≠ identified historical hydric origin`.

Restricted Taiwan 0.79–0.47 Ma results move to Supporting Information except for a small pointer showing that present-niche directions cannot safely be projected backward.

## Figure 4 — Repeated white phenotype, different current radiation context

No raw public photographs are required in the main figure.

### Panel a — Dated sister-system design

Two paired schematics:

- Arenicola: *C. brevicaule* white vs *C. irumtiense* coloured; lineage split context ~0.93 Ma;
- Taiwan: *C. kawakamii* white vs *C. tatakaense* coloured; lineage split context ~0.35 Ma.

State explicitly that split age is not colour-transition age.

### Panel b — Colour phenotype contrasts

White minus coloured:

- chroma: −2.95 Arenicola; −6.16 Taiwan;
- lightness: +6.86 Arenicola; +8.24 Taiwan.

Show bootstrap intervals and usable n. The assay gate is directional/assessability based, not a significance gate.

### Panel c — Current RSDS contrasts

White minus coloured RSDS:

- Arenicola +1814; locality-collapsed +1712;
- Taiwan −686.5; locality-collapsed −1703.

Pair-level Azami-direction concordance = **1/2**.

Make the reversal visually explicit rather than averaging the two systems.

### Panel d — Hierarchical scale diagnostic

Pooled within-taxon demeaned chroma ~ RSDS:

- beta = −0.4065;
- two-sided permutation P=0.1141;
- prespecified expected-negative one-sided P=0.0361.

Label `secondary scale diagnostic` and never let it replace the 1/2 sister-pair primary result.

## Figure 5 — Partial coordinated remodelling within a modular historical mosaic

### Panel a — Coarse repeated head directions in the two white lineages

White minus coloured:

| endpoint | Arenicola | Taiwan | repeated direction |
|---|---:|---:|---|
| circularity | +0.238 | +0.159 | white higher |
| solidity | +0.092 | +0.099 | white higher |
| visible floret fraction | −0.305 | −0.028 | white lower |

Add uncertainty bars and indicate that only Arenicola circularity/solidity intervals exclude zero.

### Panel b — Heterogeneous fine geometry

Show a compact negative-evidence matrix for:

- aspect ratio;
- width-profile CV;
- involucre length/width;
- taper metrics;
- projection roughness/p95;
- spread fraction;
- bract projection peak density.

Classes: opposite direction / low information / not homologous to botanical phyllary posture.

### Panel c — Whole-capitulum synthesis

Combine three independent constraints:

1. discrete history: 0/3 trait pairs share robust transition localization;
2. present 18-D integration: within-versus-among association-matrix rho=0.3663;
3. sister systems: three coarse non-colour directions repeat with white state.

The graphical model should place the supported interpretation between two rejected extremes:

`complete independence` ← **partial coordinated remodelling inside modular, lineage-dependent histories** → `one synchronized universal syndrome`.

### Panel d — Evidence ceiling / Chapter 3 handoff

Use the final V3 ranked rows:

1. orientation × hydric exposure — repeated history/current candidate, origin driver unresolved;
2. colour × radiative environment — repeated white state, current RSDS lineage-/scale-dependent, historical driver unresolved;
3. phyllary posture — history resolved, driver unidentified;
4. stickiness — rapid history resolved, biotic driver unidentified;
5. orientation × temperature — directional scale mismatch;
6. outline/head packing — repeated coarse extant remodelling, historical process unresolved.

End arrow:

`public-data ceiling → direct exposure → mechanism → reproductive fitness`.

## Supporting Information routing

Keep the following out of the five main figures:

- full 376 orientation chronology × palaeolocation scenario rows;
- restricted 0.79–0.47 Ma Taiwan descendant palaeoclimate analysis, wet/dry controls, phenology-window precipitation and sea-level sensitivity;
- full Taiwan occurrence-source provenance and direct-TBN/broader-TBN tables;
- held-out climate prediction comparison;
- all 56 balanced public-image observation coordinates and full image-level measurement diagnostics;
- detailed fine-geometry contrasts;
- four polymorphic colour species-tip resolution audits;
- independent nuclear-data resource audit;
- cytotype/ploidy constraint table;
- full final V3 evidence matrix.

## Display gates

- Every main numeric panel must be generated from a frozen evidence artifact.
- Do not call minimum changes independent origins or convergence.
- Do not call relative lineage-depth event age or evolutionary rate.
- Do not treat the 0.74–0.79 Ma central pair as a confidence interval.
- Do not treat the chronology grid as a joint posterior or regional boxes as ancestral-area probabilities.
- Do not call BIO12 and BIO15 the same rainfall variable.
- Do not call present hydric correspondence historical rain causation.
- Do not replace the GBIF orientation primary with the direct-TBN tier after inspecting P values.
- Do not average Arenicola and Taiwan RSDS contrasts into one mean that hides the sign reversal.
- Do not promote the pooled within-taxon one-sided colour result over the 1/2 pair-level primary result.
- Do not call repeated white-state chroma a demonstrated pigment pathway, UV adaptation or independent convergent origin.
- Do not call coarse repeated head geometry a universal white-flower syndrome.
- Do not rewrite `not_evaluable` as no effect.
- Do not label the final model demonstrated selection or adaptation; `selection mosaic` remains a process hypothesis shorthand until focal mechanism and fitness are tested.
