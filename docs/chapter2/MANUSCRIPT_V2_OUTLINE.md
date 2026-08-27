# Manuscript v2 outline — from decomposed phenotypes to trait-specific histories

## Working title

**From complex phenotype to trait-specific history: decomposing capitulum diversification in Cirsium**

Alternative:

**A complex floral head is not one evolutionary syndrome: functional candidates and repeated trait histories in Cirsium**

## Paper-level claim available now

> **Cirsium capitulum diversity is better represented as a set of partly decoupled phenotype components than as one syndrome, and the currently resolved components do not share one common evolutionary history. Orientation, phyllary posture and stickiness each require repeated state changes on the accepted nuclear topology ensemble, while functional evidence indicates that these phenotypes can engage distinct pollination, protection and antagonist pathways. The origins and adaptive convergence of those repeated states remain unresolved and define the next population and experimental tests.**

This claim does not require calling repeated states adaptive convergence and does not require modular evolvability to be true.

---

# 1. Introduction

## 1.1 Complex organs are often treated as syndromes

Frame the problem: floral/capitulum phenotypes are frequently compressed into categories or presumed integrated syndromes. Such compression can hide cases where component traits have different environmental associations, functions and evolutionary histories.

## 1.2 The key distinction

Separate four questions that are often conflated:

1. what phenotypic components exist;
2. what functions those components can perform;
3. how the component states changed through history;
4. whether repeated changes are independent and convergent.

## 1.3 Why Cirsium

Cirsium provides a common homologous capitulum architecture with substantial variation in orientation, colour, involucre/phyllary architecture, armature, stickiness and display. The Japanese radiation provides a shallow nuclear-history framework in which repeated states can be studied without comparing fundamentally different floral organizations.

## 1.4 Questions

Q1. Is current capitulum phenotype organized as one syndrome or as partly separable components across within- and among-taxon scales?

Q2. Which ecological functions are biologically plausible for those components based on independent manipulation and quantitative literature?

Q3. Do currently resolved component states share one evolutionary history or require repeated trait-specific changes?

Q4. What remains necessary to distinguish ancestral retention, independent origin, ancestral polymorphism and introgression before convergence can be claimed?

---

# 2. Methods

## 2.1 Phenotypic decomposition from Azami

Use the frozen continuous phenotype framework and within/among decomposition as the empirical present. Do not reframe image modules as validated functional modules.

Primary structural quantities to report include within-taxon module organization, among-taxon module organization and cross-scale association similarity.

## 2.2 Functional annotation evidence

Use the existing quantitative interaction/effect registries and strict Cirsium herbivory meta-analysis.

Keep separate:

- trait → pollination performance;
- trait → abiotic protection;
- trait → antagonist access/damage;
- interaction/damage → mature or viable seed output;
- seed output → downstream demographic transmission.

Do not pool orientation, phyllary, stickiness, display and colour into one generic functional effect.

## 2.3 Nuclear history

Use the accepted Japan38 Comp1061 compatibility tree and 1000 UFBoot trees with branch lengths interpreted only as substitutions/site.

Report tree provenance, unresolved/non-monophyletic concepts and fail-closed state handling.

## 2.4 Trait-specific history reconstruction

Reconstruct orientation, phyllary posture and stickiness separately using source-backed state definitions and minimum-change lower bounds across the topology ensemble.

Treat colour separately because the source-balanced Japan-local continuous-history replication does not support promotion of the global high-depth lightness signal.

## 2.5 Whole-capitulum lability diagnostic

Use the existing cross-module transition-overlap analysis to test the simple competitor that all component traits share one historical lability axis.

Do not equate failure of that simple competitor with proof of developmental/genetic modularity.

## 2.6 Auxiliary scale-specific generative analysis

Place the 62-target simulation programme after the main history analysis or in supplement. Its purpose is to diagnose whether one covariance/process architecture can reproduce the observed within/among field.

It must not be described as reconstructing evolutionary transition history.

---

# 3. Results

## 3.1 The capitulum is not one present-day syndrome

Lead with Azami:

- component traits are measurable separately;
- within-taxon organization exceeds among-taxon organization;
- within/among association geometry is only partially aligned;
- simple broad climate-distance, colonization-history-distance and deterministic ploidy explanations are inadequate in the current comparisons.

Interpretation: the present phenotype itself gives no reason to assume one conserved syndrome.

## 3.2 Component phenotypes map to different candidate functions

### Orientation

Independent manipulations support pollination/timing and abiotic-protection pathways reaching reproductive success. A static visitation-only model is insufficient.

### Display

Greater display can increase pollinator discovery/probing while also increasing antagonist exposure.

### Phyllary / armature

Protective-envelope/exclusion is plausible but requires direct focal validation; image geometry is not yet defence.

### Stickiness

Direct evidence contains benefit, null and cost; no generic defence sign is retained.

### Antagonist fitness channel

The strict Cirsium seed-output meta-analysis gives RR 2.674 (95% CI 2.388–2.993) under reduced versus ambient insect herbivory, establishing that the reproductive-enemy pathway is large enough to matter for fitness.

## 3.3 Component traits have repeated but different historical patterns

### Orientation

Report ML minimum 6 and UFBoot 4–6 after the JPN34 state repair. Emphasize poor exact branch localization.

### Phyllary posture

Report 3 minimum changes across all 1000 UFBoot trees and JPN36 as the strongest current partly localizable transition target.

### Stickiness

Report canonical main ML 5 / UFBoot 4–5. If PR124 is fixed and merged before manuscript freeze, update to 13 resolved and exactly 5 changes on every UFBoot tree; otherwise retain it as a sensitivity/provisional extension.

## 3.4 The simple whole-capitulum historical-lability model is not supported

No module pair is consistently positive across branch-length-aware and topology-only transition-overlap diagnostics.

This result supports trait-specific historical structure, not proven modular evolvability.

## 3.5 Colour is a negative historical control

High-depth global/Japan38 continuous lightness shows anti-phylogenetic structure, but source-balanced Japan7 does not replicate the same directional signal. Therefore colour is not promoted to a Japanese-radiation repeated-history conclusion through this route.

## 3.6 Repeated state is not yet convergence

State explicitly that the current tree can establish recurrence lower bounds but cannot by itself distinguish ancestral retention, independent mutation, ancestral sorting or introgression.

The next required layer is population ancestry linked to phenotype.

## 3.7 Auxiliary result: scale decoupling is also required statistically

Summarize the simulator only after the biological results:

- v3.1 biological driver families all fail absolute adequacy;
- scalar targets alone admit NULL_COUPLED;
- held-out support geometry rejects that null (0/64);
- among-only process helps but remains inadequate;
- draft v4.1 indicates scale-specific covariance as the first adequate architecture on the seven-target screen, pending canonical/held-out validation.

Interpret this as independent support that within/among structure should not be forced into one covariance process.

---

# 4. Discussion

## 4.1 From syndrome to functional components

Main conceptual point: complex reproductive organs can be decomposed into phenotypes whose candidate functions and histories differ. Integration at one biological scale does not imply a fixed evolutionary syndrome.

## 4.2 Phenotypic recurrence versus functional recurrence

Distinguish:

- repeated phenotype;
- independent origin;
- functional convergence;
- adaptive convergence.

Different phenotypes may provide the same function, and the same phenotype may provide multiple functions.

## 4.3 The historical origin problem

Explain why species-tree recurrence is insufficient. Introduce the next nuclear population genomics + plastid + cytotype layer as a direct discriminator of ancestral retention, ancestral sorting, gene flow and lineage-specific origin.

## 4.4 The ecological convergence problem

Explain why focal manipulations must link:

`trait → effective interaction/protection → mature/viable seed`

in independently derived lineages before adaptive convergence can be claimed.

## 4.5 Higher-order evolvability as an endpoint

Only here discuss modular evolvability. If multiple traits show independent histories and repeated origins reuse ancestral variants or introgressed modules, modular evolvability becomes a stronger synthesis. It should not be assumed in Methods or Results.

## 4.6 Scale-specific covariance as a complementary structural result

Use the simulator to show that the statistical organization of the present also requires scale decoupling. Keep this distinct from evolutionary transition history.

---

# 5. Conclusion

Proposed ending:

> **The Cirsium capitulum is not well represented as one fixed adaptive syndrome. Its component phenotypes show different present-day organization, plausible functional pathways and repeated historical changes. Current nuclear-history evidence supports recurrence but does not yet identify the origin or adaptive meaning of those repeated states. The next step is therefore not to add more syndrome categories, but to connect decomposed phenotypes to function, ancestry and fitness until repeated states can be separated into retention, independent origin and genuine convergence.**

---

# Figure architecture

Figure 1 — phenotype decomposition: Azami continuous components and within/among organization.

Figure 2 — phenotype → candidate function map with evidence strength and claim boundary.

Figure 3 — Japan38 nuclear tree with separate orientation/phyllary/stickiness histories; no composite syndrome state.

Figure 4 — claim ladder from repeated state to independent origin to functional/adaptive convergence.

Supplementary Figure S1 — 62-target generative constraint results and scale-decoupling diagnostics.

Supplementary Figure S2 — colour negative-control history and source-balance stop rule.
