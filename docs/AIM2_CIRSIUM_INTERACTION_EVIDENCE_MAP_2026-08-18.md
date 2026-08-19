# EAzami Aim 2 — *Cirsium* pollination–antagonist evidence map

Status date: 2026-08-19

## Purpose

This is a supporting evidence layer for doctoral Aim 2:

```text
Azami Chapter 1
global capitulum modules and within-taxon distributions
        ↓
EAzami Aim 2 evidence map
which modules already have functional evidence?
        ↓
ancestry-resolved focal field tests
trait -> interaction / protection -> reproductive fitness
```

It does not reopen Azami Chapter 1 and does not create another doctoral Aim.

Canonical files:

- `data/evidence/cirsium_interaction_evidence_seed_v1.csv`
- `data/evidence/cirsium_interaction_evidence_summary_v1.json`
- `analysis/summarize_cirsium_interaction_evidence.py`
- `data/templates/cirsium_interaction_effect_size_template_v1.csv`
- `docs/AIM2_FIELD_NESTING_PLAN_2026-08-18.md`

## Evidence classes

Keep these separate:

1. pollinator visitation/behaviour;
2. effective pollination (contact, pollen deposition/export/viability);
3. florivory;
4. pre-dispersal seed predation;
5. vegetative herbivory as demographic context.

Evidence is promoted only along:

`trait -> interaction/protection -> pollen/damage -> achene/seed output -> demography`

Visitor counts alone are not effective pollination or fitness.

## Current bounded primary-literature seed

After the targeted 2026-08-19 recheck:

- **12 independent studies**
- **10 *Cirsium* taxa**
- **14 taxon-study rows**
- **12 direct capitulum-interaction rows**
- **2 contextual foliar-herbivory rows**

This is still a bounded source-backed seed, not an exhaustive census.

### New correction: flower colour is not an evidence blank

Mogford (1974), *Flower colour polymorphism in Cirsium palustre 2. Pollination*
(DOI `10.1038/hdy.1974.91`) reports preferential pollination of white-flowered
plants in a natural colour polymorphism.

Therefore the earlier wording “no direct *Cirsium* flower-colour interaction
study” is withdrawn.

The correct boundary is:

> direct colour→pollination evidence exists, but the bounded seed still lacks
> replicated ancestry-controlled colour→effective-pollination→reproductive-
> fitness evidence.

No numerical effect size is frozen from this paper until the full statistics
needed for sampling variance are verified.

### Predation evidence strengthened

Van Leeuwen (1983), DOI `10.1007/BF00399214`, adds source-backed evidence for
*C. palustre* and *C. vulgare*: natural predation caused substantial reductions
in achene production. This strengthens the case that antagonists can matter for
fitness, but it does not identify selection on a particular phyllary/spine
module.

## Module diagnosis and field order

### 1. Head orientation — highest priority

No direct *Cirsium* orientation manipulation linked through rain/pollination to
reproductive fitness was recovered in the bounded targeted search.

Field chain:

`orientation -> wetting / presentation -> pollen or effective contact -> seed set`

This remains the cleanest novel experiment tied directly to a primary Azami
trait.

### 2. Flower colour — second priority, now with a published pollination prior

The *C. palustre* result means pollinator discrimination by colour is plausible
within *Cirsium*. The doctoral gap is now sharper, not weaker:

`ancestry-resolved W/C state -> effective pollination / abiotic response -> fitness`

The Japanese W/C systems are valuable because Aim 1 ancestry and Aim 3
molecular data can be attached to the same colour comparison.

### 3. Involucre/phyllary/spine — conditional third

No direct phyllary/spine manipulation linked to both antagonist access and
pollinator access was recovered.

Proceed only after:

1. direct botanical measurements validate the image proxy in the focal system;
2. repeatable natural variation exists;
3. manipulation can avoid a dominant wound artifact.

Then measure both antagonist damage and pollinator-access cost, followed by seed
output.

### 4. Stickiness — lower priority

One recovered direct manipulation was null for the tested defence/seed-output
effect. Stickiness is therefore measured opportunistically rather than assumed
to define a defence syndrome.

## Effect-size pooling gate

Formal pooling remains **not authorized**.

For one harmonized contrast/outcome require at minimum:

- >=5 independent studies;
- >=3 *Cirsium* taxa;
- compatible biological contrast and response scale;
- original-study deduplication;
- sampling variance or recoverable summary statistics;
- null results retained.

Do not pool visitor abundance, effective pollination, florivory,
pre-dispersal seed predation and foliar herbivory into one effect.

## Current doctoral decision

1. orientation manipulation first;
2. W/coloured functional comparison second, now informed by the *C. palustre*
   pollination prior and nested with Aim 3;
3. phyllary/spine only after direct validation;
4. stickiness lower priority;
5. record pollinators and floral/seed antagonists together, but analyse their
   response classes separately.

## Claim boundary

This bounded evidence map prioritizes doctoral observations and experiments. It
does not estimate a pooled effect, prove adaptive radiation, or show that an
unrecovered study/interaction is absent.
