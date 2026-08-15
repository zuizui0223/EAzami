# EAzami micro-to-macro hypothesis program v2 — 2026-08-15

This extends `MICRO_TO_MACRO_HYPOTHESIS_PROGRAM_2026-08-15.md` without rewriting the validated v1 evidence synthesis.

## Evidence classes are now four-way

1. `published_conclusion` — directly established by source papers.
2. `EAzami_reanalysis` — patterns/problems found by EAzami reanalysis of public data.
3. `own_preliminary_result` — results generated in our other thistle analyses that are useful for hypothesis generation but retain their own validation/claim limits.
4. `EAzami_hypothesis` — new falsifiable statements derived from classes 2–3, with published conclusions used only as priors/context.

The new v2 addition is the current `zuizui0223/azami` Chapter-1 image-phenomics result, provenance-frozen in `data/evidence/azami_ch1_macro_trait_snapshot_v1.json`.

## Own preliminary macro result

The frozen cross-project result contains 216 taxa, 3,725 observations and 6,626 detected heads across nine image-derived trait endpoints.

After one-head-per-photo sensitivity, the fraction of visible variance below assigned-species means remains 0.582–0.899. Under balanced ten-photo subsampling it remains 0.528–0.879.

After correcting the old species-specific climate-association score for slope uncertainty, there is no common cross-module relationship between visible dispersion and within-species spatial climatic association:

- noise-adjusted Spearman rho = -0.0569 (95% bootstrap CI -0.265 to 0.155);
- hierarchical variance meta-regression b = -0.0416 (95% profile CI -0.274 to 0.200), P = 0.732.

These are image-level/macroscopic preliminary results. They are **not** genetic variance, phenotypic plasticity, local adaptation, evolutionary rate, or a resolved Cirsium species-tree result.

## EAzami-discovered problem M6 — species-mean scale compression

Combining M3 (species-tip coding erases W/C polymorphism) with the independent image-phenomics result exposes a broader scale problem:

> Compressing a species into one trait state or one trait mean can remove biologically relevant within-lineage structure, but the amount of within-species variation is not itself a universal proxy for environmental association or macroevolutionary change.

This is not a literature gap. It follows from two of our own results:

1. discrete W/C transition counts change when population states are retained;
2. continuous visible trait dispersion remains large below species means, while its common coupling to climate-association magnitude disappears after precision correction.

## HMM6 — cross-scale trait decoupling hypothesis

**Derivation:** M3 + M6.

**Hypothesis:** within-species trait dispersion, population-level discrete transition density, within-species environment–trait association and among-species niche/trait divergence are partially independent evolutionary/ecological axes. A single species mean or one generic `lability` parameter cannot represent all of them.

### Prediction

After measurement and topology uncertainty are propagated, taxa/clades that show high within-species visible dispersion will not necessarily show:

- high within-species climate-association magnitude;
- high W↔C transition density;
- rapid among-species trait divergence;
- large niche divergence.

The covariance structure should differ among colour, orientation and morphology modules and among evolutionary depths.

### Falsifier

After independent measurement validation and a resolved nuclear topology, a strong and consistent positive mapping emerges across modules from within-species dispersion → population transition density → among-species trait/niche divergence.

## Micro-to-macro consequence

The working programme is therefore no longer a single chain in which more molecular variation automatically produces more macroevolution. It becomes a set of linked but testably separable mappings:

`molecular state ↔ population state distribution ↔ lineage transition ↔ clade diversification`

and

`within-species dispersion ↔ environmental association ↔ among-species divergence`

Each arrow is an empirical question.

This matters directly for HMM1–HMM5:

- HMM1/HMM5 ask how molecular mechanisms map to repeated phenotype;
- HMM2 asks how population structure maps to inferred transition rate;
- HMM3 asks why one colonization radiated while others did not;
- HMM4 asks whether reticulation/ploidy covary with transition density;
- HMM6 asks whether these micro, population and macro summaries are actually one axis or several partially independent axes.

## Existing-data test added to macro issue

Once the accepted East-Asian nuclear topology is available, map the validated image-derived taxa to clades and compare, by trait module:

1. within-species visible dispersion;
2. within-species spatial environmental-association magnitude;
3. population-aware discrete transition density;
4. among-species niche divergence;
5. branch-level trait disparity/rate summaries where defensible.

Use hierarchical models with measurement error, topology ensembles, clade age and sampling effort. Do not call any one of these quantities `evolvability` by itself.
