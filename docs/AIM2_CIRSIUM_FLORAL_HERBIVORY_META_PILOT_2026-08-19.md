# Aim 2 quantitative pilot — reproductive cost of insect herbivory in *Cirsium*

Status: 2026-08-19

## Question

> Across experimental *Cirsium* studies, does reducing insect herbivory on reproductive or apical tissues increase reproductive output?

This is a **quantitative meta-analysis pilot**, not a literature-count evidence map.

The estimand is deliberately narrow:

`experimental reduction of reproductive/apical insect herbivory -> reproductive output`

Positive standardized effects mean greater reproductive output when herbivory is reduced.

## Inputs

Canonical extraction table:

`data/evidence/cirsium_floral_herbivory_experimental_effects_v1.csv`

Current quantitative pool:

- 5 extractable effect rows;
- 4 independent study clusters;
- 3 *Cirsium* taxa / taxon concepts;
- Maron et al. 2002 contributes two dune habitats but is collapsed to one study-level effect before the across-study model.

Two older effects use published Hedges-d/variance values reported in the 2016 broad flower-damage meta-analysis:

- *C. occidentale* — Maron et al. 2002, old dune and new dune;
- *C. canescens* — Louda & Potvin 1995.

Two newer experimental results are added from source-backed test statistics:

- West & Louda 2018, *C. canescens*: later floral-herbivory reduction and mature seeds per flower head, mixed-model `t=2.801`, denominator df `127`;
- Russell & Houseman 2019, *C. altissimum*: insect-access vs insect-exclusion seed-production contrast, `F(1,62)=6.45`.

## Standardization

All included effects are transformed to a common positive Fisher-z scale.

For published Hedges d:

`r = d / sqrt(d^2 + 4)`

followed by Fisher z. Because the source d is damage-vs-undamaged, the sign is reversed so positive means benefit of reducing herbivory. Its Fisher-z variance is obtained by the exact delta transformation `var(d)/(d^2+4)`.

For newer one-df t/F tests, partial r is reconstructed from the statistic and denominator df, followed by Fisher z. Their Fisher-z sampling variance currently uses `1/(df-1)` as a documented approximation. This is the main reason the current pooled magnitude is still called a pilot.

Multiple effect rows from one paper are first collapsed by inverse variance. The study-level effects are then pooled with a DerSimonian-Laird random-effects model.

Reproducible script:

`analysis/meta_analyze_cirsium_floral_herbivory.py`

Frozen result:

`data/evidence/cirsium_floral_herbivory_meta_pilot_v1.json`

## Result

Current four-study random-effects pilot:

- pooled Fisher z = **0.4011**;
- pooled standardized `r = 0.3809`;
- 95% CI for `r = 0.2208–0.5210`;
- approximate equivalent standardized mean difference = **0.8239**;
- approximate 95% CI = **0.4527–1.2209**;
- heterogeneity `Q = 9.479`, df = 3;
- `I^2 = 68.35%`;
- `tau^2 = 0.0220` on Fisher-z scale.

Under this pilot standardization, the pooled effect is positive: experimental reduction of insect herbivory is associated with higher reproductive output.

### Leave-one-study-out

The result is not driven by a single paper. Omitting each study in turn gives pooled `r` between **0.304 and 0.431**, and every leave-one-out 95% interval remains above zero under the same pilot variance assumptions.

This is stronger than the previous evidence-map statement that antagonists can matter. The current quantitative statement is:

> **Across the currently harmonizable experimental *Cirsium* studies, reducing reproductive/apical insect herbivory consistently improves reproductive output.**

## Biological interpretation

The moderate-to-large pooled standardized effect supports the antagonist side of the doctoral Aim 2 trade-off model:

`larger / more accessible / more conspicuous reproductive display`

may produce mutualist benefits, but reproductive-tissue insects can impose a substantial countervailing fitness cost.

The meta-analysis does **not** yet identify which capitulum module causes that cost. It therefore motivates, rather than replaces, the focal tests of:

1. orientation;
2. flower colour;
3. validated phyllary/spine architecture.

## Why this is not yet publication-grade

The direction is informative, but the pooled magnitude remains provisional because:

1. only four independent study clusters are included;
2. the 2018 and 2019 effects currently use test-statistic-to-partial-r variance approximations;
3. experimental targets differ: flower-head herbivory, broader insect exclusion and apical-meristem herbivory are not identical biological treatments;
4. additional individual-level data are publicly available and should be reanalysed directly rather than approximated.

## Immediate upgrade path

### A. Adhikari & Russell 2014 — *C. altissimum*

Dryad DOI `10.5061/dryad.772qd` provides individual-level plant and flower-head data. Reanalyse lifetime viable seed production under the apical-meristem insecticide treatment to the same benefit-of-herbivory-reduction estimand.

### B. West & Louda 2021 — *C. undulatum*

The USDA Ag Data Commons release `10.15482/USDA.ADC/1522649` contains plant/head data. Reanalyse the two-year floral-herbivory reduction experiment to the same reproductive-output estimand.

Adding these can raise the directly harmonized experimental set from four to at least six study clusters, while replacing some approximate transformed effects with raw-data estimates.

After that, fit a multilevel random-effects model with moderators such as:

- attacked tissue: flower head / apical meristem / whole reproductive plant;
- monocarpic vs iterocarpic life history;
- per-head vs per-plant/plot reproductive response;
- species/taxon;
- experimental herbivory-reduction magnitude where recoverable.

## Claim boundary

This pilot is a **real quantitative synthesis** and can be used to state that the currently extractable experimental evidence points consistently to a reproductive cost of insect herbivory in *Cirsium*.

Do not yet use the pooled `r` or approximate standardized mean difference as the definitive genus-wide magnitude. Do not infer that orientation, colour, spines or stickiness are adaptive from this result alone. The module-specific causal test remains Aim 2 field work.
