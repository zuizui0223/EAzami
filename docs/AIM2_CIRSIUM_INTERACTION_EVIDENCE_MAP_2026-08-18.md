# EAzami Aim 2 — *Cirsium* pollination–antagonist evidence map

Status date: 2026-08-19

## Purpose

Supporting evidence bridge only:

`Azami global capitulum modules -> Aim 2 literature priors -> ancestry-resolved trait -> interaction/protection -> fitness experiments`

It does not reopen Azami Chapter 1 or create a fourth Aim.

## Evidence classes

Keep pollinator behaviour, effective pollination, florivory, pre-dispersal seed predation and vegetative herbivory separate. Promote evidence only along:

`trait -> interaction/protection -> pollen/damage -> achene/seed output -> demography`

## Current bounded primary-literature seed

After the targeted 2026-08-19 recheck:

- **13 independent studies**
- **10 Cirsium taxa**
- **15 taxon-study rows**
- **13 direct capitulum rows**
- **2 contextual foliar-herbivory rows**

### Flower colour: existing pollination prior, incomplete fitness chain

Mogford (1974), DOI `10.1038/hdy.1974.91`, reports preferential pollination of white-flowered *C. palustre* in a natural colour polymorphism. Thus colour is not an interaction-evidence blank.

The doctoral gap is:

`ancestry-resolved W/C state -> effective pollination / abiotic response -> reproductive fitness`

No numerical colour effect size is frozen until full statistics and sampling variance are verified.

### Antagonist fitness cost and display trade-off

Van Leeuwen (1983), DOI `10.1007/BF00399214`, shows that predation substantially reduced achene production in *C. palustre* and *C. vulgare*.

Ohashi & Yahara (2000), DOI `10.1139/b99-182`, studied two Japanese *C. purpuratum* populations and found that seed/head predation increased with seasonal flower production; the resulting antagonist cost could counteract reproductive gains from producing more flowers.

This is especially important for the doctoral framing: more conspicuous or larger reproductive display can improve mutualist attraction yet simultaneously increase antagonist cost. Seasonal flower production is not treated as identical to a single-capitulum structural trait, so this study is a trade-off prior rather than a direct test of orientation or phyllary/spine function.

## Narrow quantitative meta-analysis now added

The previous prohibition applied to pooling the heterogeneous interaction evidence as though visitation, florivory, seed predation and different capitulum traits were one response. That prohibition remains.

A **narrow experimental estimand** is now sufficiently coherent for a quantitative pilot:

> benefit to reproductive output when insect herbivory on reproductive or apical tissues is experimentally reduced.

Canonical quantitative files:

- `data/evidence/cirsium_floral_herbivory_experimental_effects_v1.csv`
- `analysis/meta_analyze_cirsium_floral_herbivory.py`
- `data/evidence/cirsium_floral_herbivory_meta_pilot_v1.json`
- `docs/AIM2_CIRSIUM_FLORAL_HERBIVORY_META_PILOT_2026-08-19.md`

Current pool: **5 effect rows / 4 independent study clusters / 3 taxa or taxon concepts**.

Random-effects pilot result:

- pooled standardized `r = 0.3809`;
- 95% CI `0.2208–0.5210`;
- approximate equivalent standardized mean difference `= 0.8239`;
- `I^2 = 68.35%`.

Every leave-one-study-out pooled estimate remains positive. Thus the evidence has moved beyond a study count: the currently harmonizable experimental *Cirsium* literature shows a consistent reproductive benefit when insect herbivory is reduced.

This magnitude remains provisional because two newer effects use test-statistic-to-partial-r variance approximations and only four independent studies are currently pooled. Public raw data from Adhikari & Russell 2014 and West & Louda 2021 are the immediate route to >=5–6 independently reanalysed experiments.

## Module diagnosis

### 1. Head orientation — highest priority

No direct *Cirsium* orientation manipulation linked through rain/pollination to reproductive fitness was recovered in the bounded targeted search.

Field chain:

`orientation -> wetting / pollinator presentation -> pollen or effective contact -> seed set`

This remains the cleanest novel experiment tied directly to a primary Azami trait.

### 2. Flower colour — second priority

Published colour-dependent pollination exists, but ancestry-controlled effective-pollination and fitness evidence remains unresolved. Japanese/Ryukyu W/C systems uniquely allow Aim 1 ancestry and Aim 3 molecular mechanism to be attached to the same comparison.

### 3. Involucre/phyllary/spine — conditional third

No direct phyllary/spine manipulation linked to antagonist exclusion, pollinator access and fitness was recovered. Proceed only after direct botanical validation, repeatable focal variation and a low-artifact manipulation are demonstrated.

### 4. Stickiness — lower priority

The recovered direct manipulation was null for the tested defence/seed-output effect, so stickiness is not assumed to define a defence syndrome.

## Pooling boundary

**Broad heterogeneous interaction pooling remains unauthorized.** Do not combine pollinator visitation, effective pollination, florivory, seed predation, foliar herbivory or unrelated trait contrasts into one effect.

The new floral/reproductive-herbivory quantitative pilot is a separate, explicitly narrow estimand. It is allowed as a pilot but is not yet a definitive publication-grade genus-wide magnitude.

## Current doctoral decision

1. orientation manipulation first;
2. W/coloured functional comparison second, informed by the *C. palustre* pollination prior and nested with Aim 3;
3. phyllary/spine only after direct validation;
4. stickiness lower priority;
5. record pollinators and floral/seed antagonists together, but analyse their response classes separately.

## Claim boundary

The evidence map identifies functional priors and gaps. The separate narrow meta-analysis quantitatively supports a reproductive cost of insect herbivory in the currently extractable experiments, but it does not prove adaptive radiation or identify which capitulum module caused that cost.
