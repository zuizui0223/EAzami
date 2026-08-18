# EAzami Aim 2 — *Cirsium* pollination–antagonist evidence map

Status date: 2026-08-18

## Purpose

This work is the evidence bridge between:

```text
Azami Chapter 1
global capitulum modules and within-taxon distributions
        ↓
EAzami Aim 2
which modules plausibly alter interactions and fitness?
        ↓
ancestry-resolved field manipulation
trait -> interaction / protection -> reproductive fitness
```

It does **not** reopen Azami Chapter 1 and does not add another doctoral Aim. It narrows Aim 2 to experiments that are not already answered by published *Cirsium* work.

Canonical files:

- `data/evidence/cirsium_interaction_evidence_seed_v1.csv`
- `data/evidence/cirsium_interaction_evidence_summary_v1.json`
- `analysis/summarize_cirsium_interaction_evidence.py`
- `data/templates/cirsium_interaction_effect_size_template_v1.csv`

## Central Aim 2 question

> Do rapidly divergent capitulum modules alter pollination, abiotic protection, florivory or pre-dispersal seed predation, and do those changes reach reproductive fitness?

The operational model is a trade-off:

```text
pollinator presentation / access
              ↕
rain, UV, florivore and seed-predator protection
```

A structure that looks defensive is not called an adaptation without a functional comparison.

## Interaction classes

Keep these classes separate throughout extraction and analysis.

1. **Pollinator visitation**
   - visitor abundance, visitation rate, residence time and movement.
   - This is not automatically effective pollination.

2. **Effective pollination**
   - stigma/anther contact, pollen deposition, pollen export, pollen-tube growth or pollen viability.

3. **Florivory**
   - consumption of florets, reproductive tissues or floral signals during flowering.

4. **Pre-dispersal seed predation**
   - damage or consumption within capitula before seed dispersal.

5. **Foliar/vegetative herbivory**
   - retained as demographic context, not pooled with direct capitulum antagonism.

## Outcome hierarchy

Evidence is promoted in this order:

```text
interaction occurrence
    ↓
visitor / antagonist behaviour or abundance
    ↓
pollen transfer or damage
    ↓
fruit, achene or seed production
    ↓
recruitment or population growth
```

A study that reports only visitors cannot support a fitness claim.

## Bounded primary-literature seed

The current seed contains:

- **10 independent studies**;
- **9 *Cirsium* species**;
- **11 taxon–study rows**;
- **9 direct capitulum-interaction rows**;
- **2 contextual foliar-herbivory rows**.

Current direct evidence includes:

- two Japanese *C. purpuratum* studies linking floral display to bumble-bee foraging and revisitation;
- two studies showing that *Cirsium* floral scent can attract or temporally partition pollinators and florivores;
- four independent studies quantifying pre-dispersal seed predation;
- one direct stickiness manipulation in *C. discolor*, with a null result for seed-predator defence and seed production.

This is a bounded, verified seed rather than an exhaustive review. Absence from this table is never treated as biological absence.

## Current module diagnosis

### Head orientation — highest field priority

No direct *Cirsium* study was recovered in the bounded seed that manipulated head orientation and followed:

`orientation -> rain/pollinator response -> reproductive fitness`

This is therefore the cleanest novel Aim 2 experiment and directly uses an Azami Chapter 1 trait.

Required focal design:

- natural orientation recorded continuously;
- temporary, non-destructive reorientation where feasible;
- rain exposure / pollen wetting / pollen viability;
- visitor guild, visit rate and contact effectiveness;
- achene/seed set;
- ancestry-resolved population identity.

### Flower colour — second priority and Aim 3 bridge

No direct *Cirsium* W/coloured comparison was recovered that connected colour through pollination or abiotic performance to fitness.

Required focal design:

- standardized visible + UV reflectance;
- natural W/coloured population pairs after Aim 1 ancestry resolution;
- pollinator guild and effective contact;
- floral temperature/UV or water-stress responses where biologically justified;
- pigment chemistry and seed set;
- matched Aim 3 floral material.

### Involucre/phyllary/spine — conditional third priority

The bounded seed recovered effects of capitulum size and position on seed-predator attack, but no direct phyllary/spine manipulation.

Do not launch a large experiment merely because the proxy exists in Azami. First confirm repeatable focal-population variation and botanical validity of:

- phyllary angle;
- actual spine length, direction and stiffness;
- pollinator-access geometry.

Then test both sides of the same manipulation:

- antagonist entry/damage;
- pollinator landing/access/contact;
- seed output.

### Stickiness — lower priority unless focal variation is strong

The single recovered direct manipulation was null. Stickiness is therefore not assumed to be a defence syndrome. It is measured opportunistically but does not displace orientation or colour from the core field design.

### Display size and scent — established interaction candidates, incomplete fitness chains

Published *Cirsium* studies already show effects on pollinator behaviour and mutualist–antagonist attraction. New EAzami work should use these findings to record both pollinators and antagonists, rather than repeating display-only visitor models without fitness.

## Discovery sources

Use interaction databases for discovery and coverage diagnostics:

- Global Biotic Interactions (GloBI);
- Mangal;
- Web of Life.

For research inference:

- use a stable/versioned data release where available;
- retain original dataset and paper identifiers;
- deduplicate at the original-study level;
- verify each candidate against the primary source;
- never use a database interaction record as an effect size by itself.

GloBI API or browser results are exploratory and dynamic. A frozen source release or a dated derivative must be archived before quantitative publication use.

## Effect-size promotion gate

A pooled effect is not yet authorized.

For one harmonized contrast/outcome, pooling requires at minimum:

- five independent studies;
- three *Cirsium* taxa;
- compatible biological contrasts and response scales;
- original-study deduplication;
- sampling variance or enough raw summary statistics;
- visitor abundance separated from effective pollination;
- florivory, seed predation and foliar herbivory separated;
- null results retained.

Until a stratum passes this gate, the product remains a systematic evidence map and field-design tool.

## Current doctoral decision

The existing literature changes field priority as follows:

1. **orientation manipulation first**;
2. **W/coloured functional comparison second**, nested with Aim 3;
3. **phyllary/spine only after direct trait validation and focal variation are confirmed**;
4. **stickiness opportunistic/lower priority**;
5. record pollinators and floral/seed antagonists together because the same signal can recruit both.

## Claim boundary

The current seed shows that the meta-analytic program is feasible and that published evidence is uneven across modules. It does not estimate a pooled effect, prove adaptive radiation, or demonstrate that orientation/colour/phyllary studies do not exist outside the bounded search.
