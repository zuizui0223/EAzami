# FDT1 targeted systematic review protocol

Status: 2026-08-24

## Objective

Fill only the causal/effect-size gaps exposed by the existing EAzami evidence audit. This is not another broad search for all floral-selection papers.

The primary question is:

> For capitulum-analog reproductive trait modules, what experimentally or selection-analytically supported effects connect a trait to an ecological mechanism and/or reproductive fitness, and how context-dependent are those effects?

## Module search priorities

1. **orientation** — independent direct reorientation experiments measuring pollination, rain/UV/thermal exposure, pollen performance and seed/fruit fitness;
2. **phyllary/spine defensive architecture** — direct or quasi-experimental structural defence -> antagonist access/damage -> reproductive fitness, with pollinator-access costs retained;
3. **stickiness/mucilage** — direct removal/neutralization or genetic-polymorphism experiments, with floral versus vegetative adhesive traits separated;
4. **flower pigmentation** — abiotic temperature/UV/drought manipulations and pollinator-mediated selection kept as separate causal families;
5. **display quantity** — direct display/head-number/size effects on pollinator benefit and reproductive-antagonist cost, preferably both agents in the same data-generating programme.

## Inclusion hierarchy

### Tier A — direct causal chain

Include with highest priority when the study directly manipulates the focal trait or a well-defined trait state and measures at least one mediator and reproductive fitness.

Examples:

`trait manipulation -> pollinator/rain/enemy mediator -> fruit/seed output`.

### Tier B — agent manipulation / experimentally isolated selection

Include when pollinator, antagonist or abiotic exposure is manipulated and selection on a focal trait is quantified, even if the trait itself is not manipulated.

Standardized selection gradients such as experimentally isolated `delta_beta` form their own metric family.

### Tier C — comparative or natural-selection context

Include for functional/evolutionary context when a trait is associated with interaction intensity, fitness or temporal environmental selection without direct manipulation. These rows are not pooled with Tier A/B effects by default.

## Required extraction fields

Each retained contrast receives:

- immutable study and effect IDs;
- taxon and family;
- reproductive structure/trait;
- EAzami module;
- trait direction/state contrast;
- selective agent;
- ecological mediator;
- causal stage;
- experimental/comparative design;
- study location where defensibly reported;
- fitness/process endpoint;
- treatment/control means, variance and n where available;
- reported standardized selection gradients and SE where applicable;
- source DOI/accession;
- independence/data-generation cluster;
- claim boundary.

## Effect-size families

Do **not** transform all evidence into one number.

### Positive continuous/count reproductive outcomes

Prefer `lnRR = log(mean_trait_state_A / mean_trait_state_B)` when means are strictly positive and the biological direction is predeclared.

### Binary fruit/seed success

Use a log risk ratio or log odds ratio only when event/non-event counts or an equivalent reconstructable model contrast are available. Keep RR and OR families separate unless an explicit conversion model is preregistered.

### Standardized pollinator-mediated selection

Retain standardized `delta_beta` and its SE as a separate family. Collapse repeated traits/contexts within article according to a preregistered dependency model; do not treat every gradient as an independent study.

### Correlations, R2 and regression coefficients

Retain as metric-specific evidence unless a common estimand is genuinely recoverable. Do not pool R2, slopes and response ratios.

### Direction/null-only evidence

Retain as structured evidence; do not invent an effect magnitude.

## Functional axes

The first-pass trait-to-function matrix may contain:

- pollinator attraction/discovery;
- effective pollination / pollen transfer;
- reproductive-organ protection from rain/wetting;
- UV/thermal protection;
- antagonist exclusion/damage reduction;
- antagonist apparency/discovery;
- display/resource cost;
- pigmentation-mediated abiotic performance;
- reproductive assurance.

A paper can contribute to more than one axis, but shared individuals and outcomes must retain one data-generation cluster.

## Context moderators

Extract when reported rather than reconstructing from coarse geography if avoidable:

- temperature / heat treatment;
- precipitation / watering / drought;
- UV/light exposure;
- elevation;
- pollinator abundance/guild or experimental access;
- antagonist guild/intensity;
- local plant/flower density;
- breeding system / autonomous selfing;
- flowering phenology;
- habitat/productivity/disturbance context.

FDT2 geographic meta-regression is run only after FDT1 effect rows are harmonized. Current Cirsium SDMs/niche models are a separate evolutionary-environment layer and are not substituted for study-level moderators.

## Independence rules

- repeated years, sites, traits and endpoints from the same underlying experiment belong to the same data-generation/article cluster;
- multiple outcomes from one experimental unit are not independent studies;
- reused datasets across papers are one data-generation family where provenance can be established;
- species in one comparative study are not automatically independent experiments;
- leave-one-data-generation-cluster-out sensitivity is preferred over row-wise deletion.

## Search stopping rule

For each `module x causal-stage x metric-family` cell, stop broadening when either:

1. at least 5 independent data-generation clusters support a homologous estimand and leave-one-cluster-out direction/magnitude is stable enough for a working prior; or
2. two successive search expansions yield no new eligible independent cluster and the cell is declared evidence-limited.

Do not lower inclusion criteria simply to reach `k >= 5`.

## Current verified seed

`data/evidence/fdt1_targeted_literature_screen_seed_v1.csv` contains high-confidence candidates found after the repository-only gap audit. It is a screening seed, not the final included-study ledger.

Immediate verified additions include independent orientation manipulation systems in *Mertensia*, *Abelia*, *Platycodon* and *Polygonatum*; a direct floral-stickiness manipulation in *Bejaria*; resistance-cost evidence from *Datura* as a non-floral adhesive analog; Asteraceae head-trait/florivory comparative evidence; and abiotic pigmentation systems in *Boechera*, *Ipomoea*, *Linanthus* and *Clarkia*.

## Claim boundary

The systematic review/meta-analysis may estimate functional priors, context dependence and evidence gaps. It cannot establish that a Japanese *Cirsium* trait state is adaptive. That requires ancestry-resolved trait -> mechanism -> reproductive-fitness validation in the focal radiation.
