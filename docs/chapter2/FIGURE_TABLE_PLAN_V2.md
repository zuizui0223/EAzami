# Chapter 2 figure/table plan v2

## Figure 1 — The capitulum is phenotypically decomposable

Purpose: establish the Azami endpoint before discussing function or history.

Show:
- phenotype components: orientation, colour, outline/shape, involucre/phyllary architecture, armature and display;
- within-taxon versus among-taxon organization;
- cross-scale association similarity;
- a visual warning that image modules are not automatically functional modules.

Primary message:

> Present-day capitulum diversity is not one fixed syndrome, and trait association structure changes across biological scale.

## Figure 2 — Phenotype → candidate function

Rows = phenotype components. Columns = candidate functional axes:
- effective pollination;
- abiotic reproductive protection;
- antagonist access/damage;
- display/discovery;
- trait cost;
- final reproductive fitness.

Encode evidence type/directness rather than pretending every mapping is validated. Mandatory anchors:
- Cirsium reproductive-herbivory RR 2.674 as a pathway-level fitness anchor, not a trait-specific effect;
- orientation multi-pathway evidence;
- display mutualist/antagonist trade-off;
- stickiness mixed benefit/null/cost evidence;
- phyllary protection as candidate rather than validated Cirsium function.

## Figure 3 — Trait-specific repeated histories on the Japan38 nuclear tree

One shared nuclear tree with separate aligned trait panels. Do not draw one composite syndrome state.

Panel A — orientation:
- resolved concepts = 20;
- ML minimum = 6;
- UFBoot range = 4–6;
- branch localization weak.

Panel B — phyllary posture:
- resolved concepts = 10;
- 3 changes across all 1000 UFBoot trees;
- JPN36 terminal forced fraction = 0.754.

Panel C — stickiness:
- resolved concepts = 13 after merged JPN24 authority repair;
- ML minimum = 5;
- ML root state = sticky;
- all 1000 UFBoot trees require exactly 5 changes;
- canonical source = PR #124, merge `4276930a0bbd0e02fcdddcfb070812ebe8df8561`.

Repeated changes are recurrence lower bounds, not adaptive-convergence counts.

## Figure 4 — From recurrence to convergence: the evidence ladder

```text
repeated present state
        ↓
independent origin?
        ↓
ancestral retention / sorting / introgression excluded or quantified
        ↓
same or equivalent function?
        ↓
same ecological regime?
        ↓
reproductive-fitness consequence?
        ↓
functional / adaptive convergence
```

Current placement:
- orientation/phyllary/stickiness: recurrence reached;
- population origin discrimination: not reached;
- focal functional validation: not reached broadly;
- adaptive convergence: not reached.

## Supplementary Figure S1 — Cross-scale generative constraint

Summarize the auxiliary simulation programme:
- v3.1 mechanism gap;
- `NULL_COUPLED` scalar winner;
- held-out 0/64 failure;
- among-only directional improvement;
- draft v4.1 scale-specific covariance adequacy, labelled provisional until canonical/held-out validation.

Message:

> The present phenotype statistically requires scale-aware covariance formation, but this is not a transition-history reconstruction.

## Supplementary Figure S2 — Colour stop-rule

Show:
- high-depth continuous lightness anti-phylogenetic pattern;
- source-balanced Japan7 non-replication;
- no promotion to W/C transition, convergence or reactivation.

## Table 1 — Trait/function/history status

Columns:
- phenotype component;
- Azami measurement status;
- candidate function;
- strongest functional evidence;
- focal functional validation status;
- historical state coverage;
- recurrence lower bound;
- origin-discrimination status;
- convergence status.

## Table 2 — Historical-origin alternatives and discriminating data

Rows:
- ancestral retention;
- independent lineage-specific origin;
- ancestral polymorphism/sorting;
- introgression/gene flow;
- hybridization/cytoplasmic capture;
- reversal/re-expression.

Columns:
- expected nuclear signal;
- expected plastid signal;
- cytotype relevance;
- phenotype linkage needed;
- whether species-level tree can resolve it.

## Supplementary Table S1 — Exact history provenance

Include tree run/artifact, locus counts, branch-length semantics, UFBoot count, taxon/concept exclusions and authority source for every discrete state.

## Supplementary Table S2 — Functional evidence ledger

Do not pool incompatible endpoints. Preserve source taxon, manipulation, mediator, endpoint and transportability to Cirsium.
