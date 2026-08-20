# Aim 2 tranche-1 joint observation protocol

Status: 2026-08-20

## Purpose

Convert the merged antagonist meta-analysis and cross-layer pattern-reduction result into a field-ready measurement layer without adding a new doctoral Aim.

The question is no longer whether insect antagonists can reduce *Cirsium* seed output. The direct seed-output meta-analysis already supports a large repeatable cost. Tranche 1 must instead ask which capitulum module changes that cost and whether the same module changes pollinator benefit or abiotic protection.

## Data hierarchy

Keep four linked levels rather than flattening repeated observations into one row:

1. biological individual — `sampling/aim13_individual_sample_ledger_v1.csv`;
2. focal capitulum/treatment and final fitness — `sampling/aim2_capitulum_field_ledger_v1.csv`;
3. repeated observation bout on that capitulum — `sampling/aim2_capitulum_observation_bout_ledger_v1.csv`;
4. plant-season display/predation — `sampling/aim2_plant_display_predation_ledger_v1.csv`.

`individual_id` and `capitulum_id` are the join keys. An observation bout never creates a new biological individual or capitulum identity.

## Why the bout table is needed

The merged structural screen leaves one practical discriminating question: can environment, pollinator benefit and antagonist cost be explained with one shared response axis, or do capitulum modules respond semi-independently?

A single final capitulum row cannot represent time-varying microclimate and repeated interaction measurements. The bout table therefore stores contemporaneous conditions and both interaction channels on the same focal head.

## Minimum repeated-bout record

Each observation bout should preserve:

- `individual_id`, `population_id`, `capitulum_id`, `observation_bout_id`;
- local start/end time and phenological stage;
- realized orientation treatment/angle;
- sensor identity when a sensor is used;
- air temperature and relative humidity where measurable;
- wind, incident radiation, head-surface temperature and recent rainfall when measurable;
- capitulum wetness state;
- pollinator visits and effective contacts;
- antagonist visits/events and any damage observed during the bout;
- treatment integrity.

Microclimate columns are allowed to be blank when an instrument is unavailable. Do not substitute invented values or coarse climate rasters for missing head-scale measurements.

## Channel separation

Do not collapse the following into one generic `insect_activity` variable:

- pollinator visit count;
- effective pollination contact;
- antagonist visitation/event count;
- florivory or seed-predator evidence;
- final achene/seed output.

The point of tranche 1 is to observe benefit and cost together on ancestry-linked modules.

## Field order

1. **Orientation first** — natural orientation plus non-destructive reorientation/sham where feasible. Repeat observation bouts across contrasting weather/time windows, then retain pollen wetting/viability and final seed output in the capitulum table.
2. **W/coloured comparison second** — reuse the same bout structure so colour effects are not inferred from visitor counts without contemporaneous environment and effective contact.
3. **Phyllary/spine conditional third** — only after direct botanical variation is validated; use the same joint benefit/cost outcomes if manipulation is defensible.

## Analysis consequence

The first fitted field model should use ancestry/population structure and repeated-bout dependence explicitly. A useful minimal hierarchy is:

`module phenotype/treatment × microclimate -> pollinator benefit + antagonist cost -> reproductive fitness`

with population/individual/capitulum dependence retained rather than treating bouts as independent biological replicates.

Do not use this protocol to claim modular evolvability. It creates the data needed to test whether module-specific response remains necessary after ancestry and environment are controlled.
