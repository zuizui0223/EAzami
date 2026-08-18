# Aim 2 field nesting plan — 2026-08-18

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

## Baseline measurements attached to focal individuals

At flowering, every focal individual used in the population panel should retain, where feasible:

- `individual_id`, population and locality;
- voucher-linked whole-plant and capitulum images;
- phenological stage;
- natural capitulum orientation as a continuous angle plus categorical audit state;
- standardized visible colour and a UV-reflectance file where available;
- capitulum diameter and display size;
- direct phyllary spread angle, spine length/direction and stickiness score;
- treatment eligibility and capitulum identity;
- later achene/seed outcome.

Image proxies from Azami are not substituted for direct focal botanical measurements.

## Experiment 1 — orientation first

Primary system: Ryukyu *C. brevicaule* / *C. irumtiense* populations, expanded to another ancestry-resolved lineage only after feasibility is demonstrated.

Design hierarchy:

1. use comparable capitula within the same plant for paired control/manipulation where plant architecture permits;
2. otherwise use randomized plant/block assignment with a sham-handling control;
3. record natural angle before treatment and achieved angle after treatment;
4. do not combine populations before retaining population and ancestry effects.

Required response chain:

`orientation -> rain/wetting or pollinator presentation -> pollen/contact response -> achene/seed set`

Minimum measurements:

- rainfall or standardized wetting exposure;
- pollen wetting and viability where feasible;
- visitor guild, visit count and effective stigma/anther contact;
- florivory and seed-predator damage;
- total and filled achenes/seeds.

A small feasibility pilot may begin with about 10 experimental units per treatment per population, but final replication is determined from pilot variance, treatment loss and the feasible experimental unit (capitulum or plant). The pilot is not promoted as a definitive fitness test.

## Experiment 2 — W/coloured function comparison

Primary contrasts:

- W/coloured *C. pendulum* populations;
- W/coloured *C. sieboldii* where reproducible populations are secured;
- *C. brevicaule* / *C. irumtiense* only with ancestry and species-history interpretation retained;
- *takaoense* as an external/public-mechanistic anchor rather than a prerequisite for Japanese field completion.

Required response chain:

`ancestry-resolved colour -> pollinator/abiotic response -> reproductive fitness`

Measurements:

- calibrated visible and UV reflectance;
- pigment-linked sampling for Aim 3 focal individuals;
- floral temperature or UV/water-stress response only where the field design can measure it directly;
- visitor guild and effective contact, not visitor identity alone;
- achene/seed set.

Distant white and coloured populations are not treated as a colour experiment without ancestry, geography and environment controls.

## Experiment 3 — phyllary/spine conditional gate

Do not manipulate phyllaries/spines until all three gates pass:

1. direct measurements validate that Azami image proxies track botanical angle/length in the focal system;
2. repeatable among-individual or among-population variation is present;
3. a manipulation can alter antagonist access without destroying the capitulum or introducing a larger wound artifact.

When admitted, record both sides of the trade-off:

- florivore/seed-predator entry and damage;
- pollinator landing, access and effective contact;
- seed outcome.

## Antagonist monitoring common to all experiments

Score focal capitula repeatedly at:

1. bud/pre-anthesis;
2. anthesis;
3. post-anthesis/seed development;
4. mature achene collection.

Keep florivory, pre-dispersal seed predation and vegetative herbivory as separate outcomes.

## Data model

Canonical prospective template:

`sampling/aim2_capitulum_field_ledger_v1.csv`

One row represents one focal capitulum/treatment outcome. Repeated visitor or antagonist events can be stored in a linked event table later, keyed by `individual_id + capitulum_id`.

## Priority under limited field capacity

1. preserve Aim 1 population replication;
2. obtain direct baseline capitulum traits from those populations;
3. run orientation feasibility/manipulation;
4. add W/coloured functional comparisons;
5. add phyllary/spine manipulation only after its validity gates;
6. measure stickiness opportunistically rather than displacing the first two experiments.

## Stop rules

- do not create a separate interaction-only sample with no ancestry linkage;
- do not call visitation effective pollination without contact/pollen evidence;
- do not infer adaptation from damage or visitor counts without reproductive outcome;
- do not pool different antagonist classes;
- do not fix final experimental sample size before pilot variance and experimental-unit feasibility are known;
- do not let Aim 2 manipulation reduce the core population-genomic replication needed for Aim 1.
