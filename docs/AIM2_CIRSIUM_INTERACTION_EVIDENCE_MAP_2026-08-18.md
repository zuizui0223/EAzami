# EAzami Aim 2 — *Cirsium* pollination–antagonist evidence map

Status date: 2026-08-20

## Purpose

Supporting bridge:

`Azami global capitulum modules -> interaction evidence -> quantitative antagonist baseline -> ancestry-resolved trait -> interaction/protection -> fitness experiments`

This is not another doctoral Aim.

## Evidence classes remain separate

Keep pollinator behaviour, effective pollination, florivory, pre-dispersal seed predation and vegetative herbivory separate. Promote evidence only along:

`trait -> interaction/protection -> pollen/damage -> achene/seed output -> demography`

## Bounded interaction evidence map

Current seed:

- **13 independent studies**;
- **10 *Cirsium* taxa**;
- **15 taxon-study rows**;
- **13 direct capitulum rows**;
- **2 contextual foliar-herbivory rows**.

Decision-relevant priors include:

- *C. palustre*: natural flower-colour-dependent pollination exists, but ancestry-controlled colour→effective-pollination→fitness remains unresolved;
- *C. purpuratum*: greater seasonal flower production can increase pre-dispersal seed predation, supporting a mutualist-attraction versus antagonist-cost trade-off;
- no direct *Cirsium* head-orientation manipulation linked through interaction/protection to reproductive fitness was recovered;
- no direct phyllary/spine manipulation linked to both antagonist access and pollinator access was recovered;
- the recovered direct stickiness manipulation was null for its tested defence/seed-output effect.

## Direct quantitative antagonist baseline — v2

The evidence map has now been supplemented by a **narrow, directly interpretable random-effects meta-analysis**.

Canonical files:

- `data/evidence/cirsium_floral_herbivory_lnrr_effects_v2.csv`
- `analysis/meta_analyze_cirsium_floral_herbivory_lnrr_v2.py`
- `data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json`
- `docs/AIM2_CIRSIUM_FLORAL_HERBIVORY_LNRR_META_V2_2026-08-19.md`

Estimand:

`RR = viable/mature seed output under experimentally reduced insect herbivory / seed output under ambient herbivory`

Only direct seed-output means and SEs enter this synthesis. Multiple habitats/strata/years from one data-generation study are collapsed before across-study pooling.

Coverage:

- **9 within-study contrasts**;
- **4 independent data-generation studies**;
- **2 taxa/taxon concepts**.

Result:

- pooled **RR = 2.674**;
- 95% CI **2.388–2.993**;
- ambient-herbivory loss of potential seed output = **62.6%**;
- 95% CI **58.1–66.6%**;
- **I² = 1.0%**.

Study-level RR values are 2.29, 3.57, 2.48 and 2.67. Every leave-one-study-out pooled RR remains 2.60–2.73 with its confidence interval above 1.

### Interpretation

Within the currently harmonizable experiments, the antagonist side of the doctoral trade-off is quantitatively strong:

> **reducing insect herbivory produces about 2.7-fold more viable/mature seeds on average.**

The next biological question is therefore not “do insect antagonists matter?” but:

> **which capitulum modules alter this large antagonist fitness cost, and what mutualist or abiotic costs accompany that protection?**

## Module diagnosis after the meta-analysis

### 1. Head orientation — first functional experiment

Still the cleanest direct gap.

Required chain:

`orientation -> wetting/presentation + antagonist access -> effective pollination/damage -> seed output`

Record both pollinator and antagonist pathways so an apparent defence benefit is not interpreted without its possible pollination cost.

### 2. Flower colour — second

Published colour-dependent pollination exists, but ancestry-controlled effective-pollination and fitness evidence remains unresolved. Japanese/Ryukyu W/C systems allow the same comparison to feed Aim 3.

### 3. Involucre/phyllary/spine — biologically strengthened, methodologically gated

The large quantified antagonist cost makes a defence hypothesis more consequential. However, the Azami involucre/spine variables are image-geometry proxies, not botanical truth.

Proceed only after:

1. direct botanical measurements validate proxy correspondence in the focal system;
2. repeatable focal variation exists;
3. manipulation can change access without a dominant wound artifact.

Then test both:

`phyllary/spine -> antagonist access/damage -> seed output`

and

`phyllary/spine -> pollinator access/effective contact -> seed output`.

### 4. Stickiness — lower priority

Keep opportunistic measurement; do not assume defence from appearance.

## Pooling boundary

The narrow seed-output lnRR analysis is legitimate because its estimand is explicit and harmonized. **Broad interaction pooling remains unauthorized.** Do not combine pollinator visitation, effective pollination, florivory, seed predation, foliar herbivory or unrelated trait contrasts simply to increase sample size.

Future quantitative synthesis should proceed only by adding another clearly harmonized estimand, for example a sufficiently replicated floral-display→pollinator or floral-display→antagonist relationship. Those effects should remain guild-specific before any conflict comparison.

## Current doctoral decision

1. treat a large antagonist seed-output cost as an established quantitative prior;
2. orientation manipulation first;
3. W/coloured function second;
4. phyllary/spine only after botanical validation, but explicitly test defence versus pollinator-access trade-off when admitted;
5. do not repeat generic insect-exclusion experiments unless they identify a focal trait mechanism.

## Claim boundary

The quantitative synthesis estimates the reproductive cost of insect herbivory in the currently harmonizable *Cirsium* experiments. It does not identify the causal capitulum trait, prove selection on a module, or demonstrate adaptive radiation. Those are Aim 2 field tests.
