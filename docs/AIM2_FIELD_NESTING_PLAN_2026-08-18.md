# Aim 2 field nesting plan — 2026-08-20

## Decision

Aim 2 is not a separate field campaign. Functional measurements are nested within the same ancestry-resolved populations collected for Aim 1.

```text
population / individual identity
        + nuclear ancestry
        + plastid haplotype
        + cytotype
        + capitulum phenotype
        + interaction / protection response
        + reproductive fitness
```

This preserves the doctoral mainline: explain where variation came from, then test what it does.

## Biological levels must remain separate

The *C. purpuratum* evidence shows that greater seasonal flower production can increase pre-dispersal seed predation and counteract reproductive gains. That is a **plant-level seasonal display trade-off**, not the same quantity as a focal capitulum's orientation, colour or phyllary geometry.

The orientation mechanism-reduction result adds a third necessary level: a whole-day visitor total can hide a biologically important early time-window effect.

Therefore Aim 2 uses three linked ledgers:

1. `sampling/aim2_capitulum_field_ledger_v1.csv` — one focal capitulum/treatment outcome;
2. `sampling/aim2_orientation_time_window_ledger_v1.csv` — one focal capitulum × observation time window, preserving temperature/wetting and visit timing;
3. `sampling/aim2_plant_display_predation_ledger_v1.csv` — one plant × phenology census, with final seasonal flower production and plant-level predation/reproductive output when available.

All link through `individual_id`, `population_id` and, for the first two levels, `capitulum_id`.

Do not copy a plant-level display effect into a capitulum-level structural model and do not collapse early-window orientation effects into a single all-day visit count before testing timing.

## Baseline measurements attached to focal individuals

At flowering, every focal individual should retain, where feasible:

- `individual_id`, population and locality;
- voucher-linked whole-plant and capitulum images;
- phenological stage;
- natural capitulum orientation as a continuous angle plus categorical audit state;
- standardized visible colour and UV reflectance where available;
- capitulum diameter and current display size;
- direct phyllary spread angle, spine length/direction and stickiness score;
- treatment eligibility and capitulum identity;
- plant-level counts of buds/open/post-anthesis/mature capitula at repeated censuses;
- later achene/seed outcome.

Image proxies from Azami are not substituted for direct focal botanical measurements.

## Experiment 1 — orientation first

Primary system: Ryukyu *C. brevicaule* / *C. irumtiense* populations, expanded to another ancestry-resolved lineage only after feasibility is demonstrated.

Design hierarchy:

1. use comparable capitula within the same plant for paired control/manipulation where plant architecture permits;
2. otherwise use randomized plant/block assignment with a sham-handling control;
3. record natural angle before treatment and achieved angle after treatment;
4. retain population and ancestry effects rather than pooling them away.

### Mechanism-reduction result now governing measurement

The reduced cross-study simulation compares static pollinator preference, abiotic protection and time-window thermal timing. The only family that robustly reproduced all five core patterns was **time-window pollination + abiotic protection**.

The comparison bundle was:

- Azami orientation–temperature association positive;
- *Cremanthodium* natural nodding/artificial erect achene-set RR ≈ 3.59;
- no detected *Cremanthodium* pollinator orientation preference;
- sunflower early-morning orientation effect positive;
- sunflower all-day landing effect near null.

This does **not** prove that *Cirsium* uses either comparison-system mechanism. It changes the field design: orientation must be decomposed into at least two candidate pathways rather than represented by one static visitation coefficient.

### Pathway A — time-dependent pollinator presentation

Required measurements by explicit time window:

- local start/end time;
- natural/achieved orientation;
- head-surface temperature and ambient temperature;
- pollen-presentation state where assessable;
- visitor guild and count;
- effective stigma/anther contact.

At minimum distinguish an early-day window from the later/all-day aggregate. Do not infer absence of a timing effect from an all-day null.

### Pathway B — rain / UV / wetting protection

Required measurements:

- rainfall or standardized wetting dose;
- head wetness;
- pollen wetting;
- pollen viability using a sample ID tied to the focal head/time;
- final total and filled achenes.

If possible, pair natural-rain observations with a standardized wetting feasibility treatment so treatment exposure is interpretable.

### Shared outcome

Both pathways must ultimately reconnect to:

`orientation -> timing and/or protection -> pollen/contact response -> achene/seed fitness`

Florivory and seed-predator damage remain recorded so a treatment is not mistakenly interpreted as pollination/protection when it changed antagonist exposure.

A small feasibility pilot may begin with about 10 experimental units per treatment per population. Final replication is determined from pilot variance, treatment loss and whether the experimental unit is capitulum or plant.

## Experiment 2 — W/coloured function comparison

Primary contrasts:

- W/coloured *C. pendulum* populations;
- W/coloured *C. sieboldii* where reproducible populations are secured;
- *C. brevicaule* / *C. irumtiense* only with ancestry/species-history interpretation retained;
- *takaoense* as an external/public mechanistic anchor.

Published *C. palustre* colour-dependent pollination is treated as a prior, not as a substitute for the focal test.

Required chain:

`ancestry-resolved colour -> effective pollination / abiotic response -> reproductive fitness`

Measurements:

- calibrated visible and UV reflectance;
- pigment-linked sampling for Aim 3 focal individuals;
- visitor guild and effective contact;
- floral temperature/UV/water response only where directly measurable;
- achene/seed set.

Distant white and coloured populations are not treated as a colour experiment without ancestry, geography and environment controls.

## Experiment 3 — phyllary/spine conditional gate

Do not manipulate phyllaries/spines until:

1. direct measurements validate that Azami image proxies track botanical angle/length in the focal system;
2. repeatable among-individual or among-population variation exists;
3. manipulation can alter antagonist access without a dominant wound artifact.

When admitted, record both:

- florivore/seed-predator entry and damage;
- pollinator landing/access/effective contact;
- seed outcome.

The large antagonist-cost meta result gives this mechanism biological importance, but it does not establish that any Azami image proxy is a defence trait.

## Antagonist monitoring common to all experiments

Score focal capitula repeatedly at:

1. bud/pre-anthesis;
2. anthesis;
3. post-anthesis/seed development;
4. mature achene collection.

At the same visits, census whole-plant reproductive display so seasonal flower production and the fraction of attacked capitula can be reconstructed without conflating plant and capitulum scales.

Keep florivory, pre-dispersal seed predation and vegetative herbivory as separate outcomes.

## Data model

- `aim2_capitulum_field_ledger_v1.csv`: focal head/treatment level and final fitness.
- `aim2_orientation_time_window_ledger_v1.csv`: head × time-window temperature/wetting/pollination process.
- `aim2_plant_display_predation_ledger_v1.csv`: individual × census seasonal display/antagonist context.

Repeated fine-grained insect events may later be stored separately, but every event/table must retain `individual_id + capitulum_id` and time.

## Priority under limited field capacity

1. preserve Aim 1 population replication;
2. obtain direct baseline capitulum and plant-display measurements;
3. run orientation feasibility/manipulation with explicit timing + abiotic pathway measurements;
4. add W/coloured functional comparisons;
5. add phyllary/spine manipulation only after validity gates;
6. measure stickiness opportunistically.

## Stop rules

- no separate interaction-only sample with no ancestry linkage;
- no visitation = effective pollination shortcut;
- no all-day visitation = no orientation effect shortcut;
- no adaptation claim from damage/visitor counts without reproductive outcome;
- no pooling of antagonist classes;
- no mixing plant-level seasonal display with focal-capitulum structural traits;
- no final sample-size fixation before pilot variance/experimental-unit feasibility;
- no reduction of core population-genomic replication to fund Aim 2 manipulation.
