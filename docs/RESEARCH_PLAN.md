# Chapter 2 Research Plan

## Working title

**Repeated loss and reactivation of floral anthocyanin pigmentation in East Asian *Cirsium***

## Biological problem

Flower-colour evolution is often described as repeated gain or loss of pigmentation, but apparent reversals can be produced by ancestral polymorphism, introgression or misidentified phylogenetic direction. This chapter asks whether floral anthocyanin pigmentation has genuinely been lost and later re-expressed in East Asian *Cirsium*, and whether repeated transitions use the same molecular machinery.

## Scope

Primary geographic scope: Japan, Ryukyu Islands, Taiwan and China.

Primary biological scope: *Cirsium* lineages for which flower colour can be scored with explicit evidence and placed on an existing molecular/phylogenomic backbone.

This chapter does **not** rebuild the complete East Asian species phylogeny from scratch. Published phylogenomic backbones, including Chang et al. for the Taiwanese *C. japonicum* complex and Arenicola, are treated as starting hypotheses and augmented only where transition-focused sampling requires finer population resolution.

## Aim 1 — Build a flower-colour transition atlas

Compile observation-level evidence for flower colour across East Asian *Cirsium*.

Each record must preserve:

- accepted and source taxon names;
- population/locality and country;
- evidence source and source identifier;
- qualitative colour state;
- whether the observation is assessable;
- life stage;
- whether colour is directly observed or only reported at taxon level;
- optional continuous colour measurements when calibrated/usable imagery is available.

Do not collapse literature descriptions, image observations and field measurements into a single undifferentiated value.

### Primary states for screening

`white`, `near_white`, `pale_pink`, `pink`, `purple`, `blue_purple`, `polymorphic`, `unknown`.

For the first phylogenetic screen, these can be collapsed under explicit sensitivity analyses to:

- anthocyanin-absent/very-low (`white`, optionally `near_white`);
- anthocyanin-visible (`pale_pink` through `blue_purple`);
- polymorphic;
- unknown.

## Aim 2 — Reconstruct repeated losses and candidate regains

Map population/taxon colour states onto one or more existing East Asian *Cirsium* phylogenies.

Core analyses:

1. stochastic character mapping or Bayesian/ML ancestral-state reconstruction;
2. comparison of equal-rates, all-rates-different and constrained irreversible/reversible transition models;
3. tree/topology sensitivity across credible published backbones;
4. state-definition sensitivity (`near_white` grouped with white vs coloured);
5. sampling sensitivity for polymorphic taxa;
6. explicit flagging of branches whose apparent regain is not robust to topology or coding.

### A candidate regain is not accepted from ancestral-state reconstruction alone

A branch enters the mechanistic-regain tier only when all of the following are plausible:

- an ancestral/intermediate white state has strong posterior/model support;
- the descendant coloured population/lineage is well sampled;
- ancestral polymorphism is not a simpler explanation;
- introgression from a coloured lineage is evaluated;
- molecular data show restored anthocyanin production rather than an unrelated visible pigment mechanism.

## Aim 3 — Identify the molecular route of repeated transitions

Choose 3–5 independent, strongly supported transition systems after Aim 2.

Priority systems include:

- *C. brevicaule* ↔ *C. irumtiense* in the Ryukyus;
- *C. japonicum* var. *albescens* and colour-polymorphic var. *takaoense* in Taiwan;
- additional Japanese or Chinese within-taxon colour polymorphisms or white/coloured sister lineages discovered by the atlas.

For each selected system, combine:

### Pigment chemistry

- total anthocyanin;
- anthocyanin composition;
- major flavonoid intermediates where feasible.

### Floral transcriptomics

Sample matched floral developmental stages and test the anthocyanin pathway and its regulatory network, including structural genes and MYB-bHLH-WD40 regulators/repressors.

### Genomics

Use population resequencing / WGS only after candidate transitions are prioritized. Test:

- coding loss-of-function;
- cis-regulatory divergence;
- structural variants / TE insertions;
- candidate-gene haplotypes;
- local ancestry and introgression;
- population differentiation around candidate loci.

## Aim 4 — Distinguish molecular scenarios

The chapter should explicitly discriminate among at least four models:

1. **Independent irreversible loss** — different white lineages lose structural pathway function.
2. **Repeated regulatory silencing** — pathway remains intact but is repeatedly switched off.
3. **True reactivation/regain** — a previously silenced but functional pathway is switched back on.
4. **Apparent regain by introgression/ancestral polymorphism** — colour returns without de novo reactivation.

## Separation from the next chapter

Pollinator choice, UV, drought, temperature and other selective agents are not the primary causal tests here. They can be retained as metadata and candidate hypotheses, but formal selection-pressure identification belongs after the transition direction and molecular mechanism are established.

## Deliverables

1. East Asian *Cirsium* flower-colour evidence atlas.
2. Taxon/population phylogeny table with provenance.
3. Ancestral-state and transition-count sensitivity report.
4. Ranked list of mechanistic focal systems.
5. Matched field/molecular sampling plan.
6. Pigment + RNA-seq + genomic comparison for replicated transitions.

## Decision gate before expensive sequencing

Do not launch broad WGS across all taxa. First complete the colour atlas and phylogenetic transition screen. WGS/resequencing should target branches that maximize information about repeated loss, true regain, and shared vs distinct molecular mechanisms.
