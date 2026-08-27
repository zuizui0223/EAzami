# Chapter 2 target journal v1 — Journal of Evolutionary Biology

Status: **active first submission target** for the phenotype × evolutionary-history paper.

## Primary target

**Journal of Evolutionary Biology (JEB), Research Article**

Current journal contract checked 2026-08-27:

- JEB prioritizes rigorous studies that advance understanding of evolutionary process and yield insights of interest beyond the focal taxon;
- robust negative results are acceptable when they provide new evolutionary information;
- phylogenetics, morphology, evolutionary ecology, micro- and macroevolution are in scope;
- Research Articles allow up to 7,500 words and a 250-word abstract.

Official sources:
- Oxford Academic, JEB Author Guidelines: https://academic.oup.com/jeb/pages/author-guidelines
- Oxford Academic, JEB Aims and Scope: https://academic.oup.com/jeb/pages/about

## Why the paper fits JEB

The paper is not framed as a descriptive history of Japanese *Cirsium*. The focal evolutionary question is:

> **When a complex phenotype is decomposed into continuous components, are evolutionary histories expressed primarily as conserved trait states, independent trait changes, or coordinated episodes of multidimensional change?**

The result is informative because two simple alternatives both fail:

1. **Conserved-syndrome expectation:** individual continuous trait values should retain detectable phylogenetic structure and trait suites should remain lineage-specific.
2. **Fully independent-component expectation:** if trait values are labile, branch-wise changes in different phenotype dimensions should be largely uncoupled.

The frozen analyses instead show weak individual state-level phylogenetic structure, repeated changes in independently coded discrete states, and **topology-robust positive coordination of branch-wise continuous change**. That coordination is broad rather than robustly confined within the present-day phenotype modules. The paper therefore contributes a general distinction between **state conservation** and **where evolutionary change is concentrated**.

## Headline gate — PASSED

The active headline is:

> **Coordinated evolutionary change without a conserved phenotypic syndrome.**

The predeclared continuous topology-robustness rule was:

- empirical bootstrap-topology fifth percentile of global mean branch-change rho > 0; and
- fraction of usable bootstrap topologies with positive global mean rho >= 0.95.

Observed equal-branch UFBoot result:

- usable topologies: **1000/1000**;
- global mean pairwise branch-change rho median: **0.141287**;
- q05: **0.118995**;
- q95: **0.199615**;
- positive fraction: **1.000**;
- decision: **topology_robust_positive**.

Thus the headline survives removal of substitution-length heterogeneity and propagation across the full raw UFBoot topology ensemble.

The stronger claim that coordinated change is preferentially confined within the Chapter 1 phenotype modules did **not** pass the parallel robustness rule:

- within-minus-between median: **0.112435**;
- q05: **-0.095160**;
- positive fraction: **0.946**;
- decision: **not_topology_robust_positive**.

Therefore the JEB framing is **broad coordinated change without a stable module boundary**, not demonstrated modular evolvability.

## Stretch target

**Evolution** remains a stretch target because the topology-sensitive continuous result now survives. Promotion from JEB to Evolution would still require the final manuscript to make a genuinely general conceptual contribution rather than merely documenting a known phenomenon in another taxon/context. Its current author guidance explicitly notes that demonstrating a well-established phenomenon in another taxon/context may be insufficient.

Official source: https://academic.oup.com/evolut/pages/author-guidelines

Current decision: **submit to JEB first**. The exact continuous panel (eight concepts in the complete 8-unit coupling analysis) is strong enough for a concept-driven JEB test but still makes Evolution a higher-risk first submission.

## Backup target

**American Journal of Botany** is the biological fallback if JEB judges the exact-concept Japanese continuous panel too sparse for a broad evolutionary readership. A plant-focused morphology/evolution framing would fit there without changing the scientific result.

## Not the first target

**New Phytologist** is not the first submission target. The paper is concept-driven, but the present exact continuous panel remains narrow enough that a broad plant-journal desk decision could reasonably judge the result too taxon-limited. Reconsider only after stronger population/lineage replication or a second radiation is added.

## Article architecture for JEB

Target length: 6,000–7,000 words before references.

1. Abstract <=250 words.
2. Introduction: integration/modularity → state history versus change history → rapid radiation test.
3. Materials and methods: phenotype bridge → exact concept matching → nuclear topology → continuous and discrete historical tests → topology sensitivity.
4. Results: radiation context → state-level structure → discrete recurrence → branch-change coordination → topology robustness.
5. Discussion: coordinated lability versus conserved syndrome; why neither fixed syndrome nor complete independence is supported; limits and next ancestry/function tests.
6. Conclusion optional and short.

## Scope boundaries

This submission does **not** claim:

- absolute evolutionary rates or dated trait-transition times;
- adaptation or adaptive radiation;
- validated ecological function of image-derived phenotypes;
- independent origin or convergence from repeated parsimony changes;
- developmental/genetic modularity;
- one unique causal mechanism for coordinated branch changes.

Branch lengths in the focal compatibility tree remain substitutions/site.
