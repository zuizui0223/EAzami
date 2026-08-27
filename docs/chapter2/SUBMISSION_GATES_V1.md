# Chapter 2 submission gates v1

The goal is to submit the current inference result without waiting for every downstream doctoral dataset. Tasks are separated into **submission-essential**, **strong but optional for this paper**, and **later thesis chapters**.

## A. Submission-essential

### A1. Freeze one canonical manuscript evidence state

Before figure generation, record the exact `main` commit and the canonical files used for:

- 62-target handoff;
- PR #119 scalar decision/family summary;
- PR #120 held-out decision/cell frequencies;
- PR #123 diagnostic decision/family summary;
- current merged Japan38 history summary.

Do not mix results from open PRs into a manuscript labelled as current `main`.

### A2. Generate publication figures from machine-readable evidence

Required:

- Figure 1 conceptual dependency diagram;
- Figure 2 empirical field / 62-target handoff;
- Figure 3 scalar screen + held-out falsification + diagnostic;
- Figure 4 realized-history / next-data bridge.

All numerical panels must be generated from committed CSV/JSON or immutable workflow artifacts. No manual transcription of plotted values.

### A3. Add a single manuscript-grade Methods provenance table

For each analytical stage report:

- source run / artifact;
- pre-outcome contract commit where applicable;
- seeds/draw count;
- replication threshold;
- permutation count;
- score/adequacy rule;
- independent revalidation run.

This is critical because the paper's credibility depends on the fact that PR #119, #120 and #123 had different evidential roles and were not iteratively retuned into one analysis.

### A4. Preserve the negative result

The submitted paper must retain:

- `NULL_COUPLED` as the scalar-target winner;
- 0/64 held-out primary pattern;
- no diagnostically adequate addition in PR #123.

Do not soften the failure of the tested families into “among-only model explained the pattern.” It did not meet adequacy.

### A5. Run an implementation audit, not a scientific retune

Before submission, independently check that:

- all 14 families still emit the same 18D observation schema;
- the 62-estimand adapter is exact;
- no observed response phenotype enters the conditional generator;
- held-out support states were not used in PR #119 scoring;
- PR #123 cannot overwrite PR #119 winner fields;
- within-taxon Freedman–Lane permutations remain within taxon;
- BH is applied only to the four predeclared block-specific tests within scope/scale.

Fix only implementation errors. Any change to model family, priors, weights, seeds, target definition or adequacy rule is a new version and cannot replace the frozen primary results.

### A6. Tighten the empirical Azami description

The manuscript needs a concise, source-backed paragraph stating what the present field actually shows before compression. It must distinguish:

- high-dimensional continuous trait variation;
- within-taxon organization;
- among-taxon organization;
- partial cross-scale correspondence;
- core4 sufficiency within taxa;
- additional process information among taxa.

Do not re-run broad exploratory climate analyses merely to add more associations.

### A7. Literature framing

A final literature pass is required for three concepts only:

1. inverse problems / equifinality in ecology and evolution;
2. within- versus among-species trait–environment relationships and ecological fallacy/cross-scale non-equivalence;
3. generative or simulation-based model criticism / posterior- or prior-predictive checking.

The literature review should frame the conceptual gap rather than expand the Cirsium natural-history bibliography indiscriminately.

### A8. Decide the exact paper boundary for Japan38

Recommended main-paper use:

- one short Results paragraph;
- Figure 4A or supplement;
- evidence that multiple capitulum modules require repeated state changes on the nuclear topology ensemble.

Do **not** make Japan38 transition counts the primary test of the inverse-problem paper. If including them forces extensive additional taxonomy/history review, move the detailed tree to Supplement and keep only the next-data bridge in the main text.

## B. Strong additions but not required to submit this paper

### B1. Merge JPN24 stickiness authority repair

PR #124 has already validated the authority assignment and history recomputation. If merged before manuscript freeze, use the 13-resolved / 5-step topology-robust result. If not merged, use current main and state the coverage limitation.

The paper does not depend on resolving JPN15 phyllary posture.

### B2. Independent external reproduction of the full workflow

A clean checkout or archived release that reproduces the compact decisions would strengthen the methods section. This is desirable but should not trigger new model exploration.

### B3. Larger preregistered replication of the original model families

Only if reviewers or internal audit identify Monte Carlo precision as a material weakness, define a **new replication analysis** before running it. It must preserve the original PR #119 result as primary and cannot alter family definitions or scoring. Do not perform this merely because 16 draws feels aesthetically small.

### B4. Formal information-gain ranking for next observations

The Chapter 2 Discussion proposes selecting the next measurement by its expected ability to shrink the admissible-history set. A formal implementation would be valuable, but the current empirical demonstration already supports the conceptual claim that richer constraints remove histories left admissible by scalar geometry.

## C. Explicitly not required for Chapter 2 submission

These belong to realized-history or causal chapters and should not delay the current paper.

### C1. New population genomic sampling

- nuclear population-genomic DNA;
- plastid haplotype;
- cytotype/genome size.

These are necessary to distinguish standing variation, introgression and lineage-specific origin, but the current paper's conclusion is precisely that such evidence is still needed.

### C2. JPN36 / JPN15 field manipulation outcomes

Field causality is downstream of the current generative-history constraint paper.

### C3. Floral RNA-seq / pigment mechanism

Retained anthocyanin machinery, regulation and reactivation are a separate mechanistic question.

### C4. Absolute transition timing

Do not delay submission for absolute-time FDT5/FDT6 while the calibration gate remains unresolved.

### C5. Rescue of flower-colour anti-phylogenetic hypotheses

The frozen colour stop rule remains in force.

## D. Recommended paper endpoint

The paper is ready for submission when the following statement is fully supported by frozen figures and methods:

> A simple snapshot generator can reproduce a scalar compression of the present *Cirsium* capitulum field, but fails independently held-out scale-specific inferential constraints; existing among-taxon process additions move toward the observed hierarchy without becoming adequate. Therefore the present constrains a set of possible generative histories without uniquely identifying one, and unresolved histories directly specify the next ancestry and causal data to collect.

No new biological sampling is required to make that statement publishable.
