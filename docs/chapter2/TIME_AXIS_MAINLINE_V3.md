# Chapter 2 time-axis mainline v3 — frozen audit

## Current answer

Chapter 2 asks whether present-day capitulum integration persists as shared evolutionary history. The current answer is bounded:

> **Present-day capitulum integration is detectable but scale dependent. Orientation, phyllary posture and stickiness each recur, yet recurrence count, exact transition placement and shared branch localization are distinct estimands. Once ancestral-reconstruction geometry and topology uncertainty are propagated, the available data do not support one persistent historical capitulum module.**

This is the frozen audit answer for the former Azami-dependent package. The active standalone answer is in `DIVERSITY_DEPTH_STANDALONE_V1.md` and `MANUSCRIPT_JEB_V4.md`.

## Evidence order

1. **Present integration.** At nobs>=5 the registered-module contrast is 0.164502 within taxa and 0.088475 among taxa; intervals are 0.130693–0.179475 and 0.024942–0.126171. The nobs>=2 ordering is the same. Within/among association-matrix similarity is rho=0.3663.
2. **Continuous state structure.** The original eight-unit family has 0/8 corrected two-sided results at both thresholds. After the fixed JPN29 exclusion, all eight nobs>=2 units remain `two_sided_not_supported`; the nobs>=5 family is `not_evaluable` because fewer than six concepts remain.
3. **Discrete recurrence.** Orientation requires 4–6 minimum changes across 1,000 bootstrap topologies, phyllary posture exactly three, and stickiness exactly five.
4. **Transition identifiability.** Orientation has no individually forced maximum-likelihood edge; the JPN36 orientation terminal edge is forced in 0.201 of bootstrap topologies. The JPN36 phyllary terminal edge is forced in 0.754. Stable counts do not identify all events.
5. **Continuous shared localization.** The original observed mean branch-change rho=0.408006 does not exceed the reconstruction-aware null (P=0.3504). The fixed JPN29-excluded sensitivity has rho=0.472278 and P=0.1959, also FAIL.
6. **Discrete shared localization.** Pairwise transition overlap is not consistently positive across substitution-length and equal-branch topology layers.

## Scientific decision table

| Property | Current status | Allowed wording | Prohibited promotion |
| --- | --- | --- | --- |
| Present integration | Supported and scale dependent | registered modules are stronger within than among taxa | genetic module; persistent historical module |
| Continuous state structure | No robust signal detected in sparse panel | `two_sided_not_supported`; high-depth exclusion family `not_evaluable` | zero signal; lost conservation; evolutionary independence |
| Discrete recurrence | Supported lower bounds | repeated minimum changes are required | independent origins; transition rate; adaptive convergence |
| Exact edge placement | Trait dependent | phyllary JPN36 more identifiable than orientation edges | every minimum step is a known event |
| Continuous shared localization | Reconstruction-aware FAIL | observed correlations are descriptive | coordinated evolutionary remodeling |
| Equal-branch topology signs | Diagnostic only | estimator sign is stable to topology treatment | evidence overriding the reconstruction-aware null |
| Discrete transition overlap | Not consistently positive | no one shared three-trait transition history is supported | fully independent histories; developmental modularity |

## Why the former headline failed

Permuting reconstructed branch values produced P=0.00010 but treated branches as exchangeable independent observations after they had inherited common phylogenetic and ancestral-state geometry. The valid null begins at the tips, independently permutes each phenotype, repeats Brownian conditional reconstruction and then recomputes branch correlations. Under that null, P=0.3504. The old independent-branch P value remains provenance only and cannot enter the abstract, title, conclusion or cover letter.

The earlier equal-branch bootstrap distribution was positive in 1,000/1,000 topologies, but it reused the same reconstruction structure and included identity-unresolved JPN29. It addresses estimator stability, not whether the statistic is unusual under independent tip histories.

## JPN29 provenance boundary

The primary study deliberately used a Japanese voucher labelled *Cirsium verutum*, so JPN29 remains in the raw nuclear tree. The accepted species range and specimen determination are unresolved, however, so the concept cannot support a clean Japanese phenotype join. A single outcome-independent sensitivity excluded only JPN29 and kept the same eight endpoints, threshold, minimum panel size, permutations and seed. It also failed (P=0.1959). This is a provenance correction, not a new confirmatory analysis or a replacement for the original FAIL.

## Tree and observation semantics

- The Japan38 compatibility tree uses 236 QC nuclear loci, 176 rootable loci and 1,000 UFBoot topologies.
- Branch lengths are substitutions/site, not absolute time.
- Continuous image values are global species-level proxies, not phenotypes measured on the sequenced Japanese vouchers.
- JPN20 is not forcibly collapsed because its two samples are non-monophyletic in the maximum-likelihood tree and 0/1,000 bootstrap trees.
- Missing evidence is not a biological zero or absence.

## Repository-wide material retained around the mainline

### Main or short Discussion

- 36/38 sampled Japanese concepts occur in the dominant radiation; this is historical context, not an evolutionary-rate claim.
- All four observed orientation × stickiness combinations occur within that radiation, demonstrating combinatorial phenotype diversity without proving independence.
- Species-tip compression erases within-lineage polymorphism in four audited systems; only the morph-linked *C. japonicum* var. *takaoense* example is currently testable and changes the minimum from one to two in a population-aware sensitivity.
- Broad climate, distance and sparse ploidy summaries do not provide a simple deterministic account of trait disparity; coverage prevents stronger inference.

### Supplement

- The global/high-depth lightness direction fails in source-balanced Japan7 (rho=0.2675, negative-tail P=0.7579; leave-one-out directions positive).
- Absolute-time calibration remains fail-closed, so there are no transition ages or rates per million years.
- Candidate continuous involucre/armature endpoints remain a two-concept coverage audit.
- Full topology, root-state, forced-edge and transition-overlap distributions are retained.

### Routed outside Chapter 2

- FDT1/FDT8 function and field protocols belong to phenotype × function/fitness.
- v3/v4 covariance simulations describe generation of the present phenotypic field and belong with Chapter 1 or thesis methods.
- Future population nuclear + plastid + cytotype data will discriminate retention, sorting, introgression and lineage-specific origin.

## Frozen JEB v3 audit package

- `MANUSCRIPT_JEB_V3.md` — frozen double-anonymous audit manuscript; not active submission text.
- `JEB_QUESTION_RESULT_FIGURE_MAP_V1.md` — four-figure evidence map.
- `JEB_SUPPORTING_INFORMATION_V1.md` — supplementary results and provenance.
- `JEB_TITLE_PAGE_TEMPLATE_V1.md` — separate identifying metadata and required declarations.
- `JEB_COVER_LETTER_TEMPLATE_V1.md` — bounded significance statement and AI disclosure.
- `chapter2_jeb_main_result_table_v1.csv` — machine-readable headline values and claim ceilings.

Versions v1/v2 and v3 are retained as audit history. `MANUSCRIPT_JEB_V4.md` is the active standalone text.
