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

## Keep biological and temporal levels separate

Aim 2 uses three linked field levels:

1. `sampling/aim2_capitulum_field_ledger_v1.csv` — focal capitulum/treatment and final fitness;
2. `sampling/aim2_capitulum_observation_bout_ledger_v1.csv` — repeated focal-head observation bouts, including explicit time window, microclimate, pollen state and interaction channels;
3. `sampling/aim2_plant_display_predation_ledger_v1.csv` — plant × phenology census and seasonal display/predation.

All link through `individual_id`, `population_id` and, for the first two levels, `capitulum_id`. Repeated bouts are not new biological replicates.

Do not copy plant-level display effects into a capitulum structural model and do not collapse early-window orientation effects into a single all-day visit count before testing timing.

## Baseline focal measurements

At flowering retain, where feasible:

- immutable individual/population/capitulum IDs;
- voucher-linked whole-plant and capitulum images;
- phenological stage;
- natural orientation and achieved treatment angle;
- standardized visible colour and UV reflectance;
- capitulum diameter/current display size;
- direct phyllary spread, spine length/direction and stickiness;
- later total/filled achene outcome.

Azami image proxies are not substituted for direct focal botanical measurements.

## Experiment 1 — orientation first

Primary system: Ryukyu *C. brevicaule* / *C. irumtiense* populations, expanded only after feasibility is demonstrated.

### Design

1. paired comparable capitula within a plant where architecture permits;
2. otherwise randomized plant/block assignment with sham handling;
3. record natural angle before treatment and achieved angle after treatment;
4. retain population and ancestry effects.

### Mechanism-reduction result governing measurements

`docs/ORIENTATION_MECHANISM_REDUCTION_RESULT_V1.md` compares five reduced mechanism families against:

- Azami orientation–temperature association positive;
- *Cremanthodium* natural nodding/artificial erect achene-set RR ≈ **3.59**;
- no detected *Cremanthodium* pollinator orientation preference;
- sunflower early-morning orientation effect positive;
- sunflower all-day landing effect near null.

The only family that robustly reproduced all five core targets was **time-window pollination + abiotic protection**. In 1,500 prior draws its full-core match rate was **18.3%**; abiotic-only and timing-only models each stopped at 4/5.

This does not prove that *Cirsium* uses either comparison-system mechanism. It means the field test must separate two candidate pathways rather than represent orientation by one static visitation coefficient.

### Pathway A — time-dependent pollinator presentation

Use `aim2_capitulum_observation_bout_ledger_v1.csv` and record by explicit observation bout:

- local start/end time and `time_window_class`;
- natural/achieved orientation;
- head-surface temperature and ambient temperature;
- pollen-presentation state;
- visitor guild/count;
- effective stigma/anther contact.

At minimum retain early-day bouts separately from later/all-day aggregation. An all-day null is not evidence that a timing effect is absent.

### Pathway B — rain / UV / wetting protection

In the same bout ledger record:

- recent rainfall or standardized wetting exposure;
- head wetness;
- pollen wetting;
- pollen-viability sample ID and viability where feasible.

Reconnect both pathways to final total/filled achenes in `aim2_capitulum_field_ledger_v1.csv`.

Required causal chain:

`orientation -> timing and/or protection -> pollen/contact response -> achene/seed fitness`

Florivory and seed-predator events remain separate channels so an orientation treatment is not mistakenly interpreted as pollination/protection when it altered antagonist exposure.

A small feasibility pilot may begin around 10 experimental units per treatment per population. Final replication follows pilot variance, treatment loss and feasible experimental unit.

## Experiment 2 — W/coloured function comparison

Priority contrasts:

- W/coloured *C. pendulum*;
- W/coloured *C. sieboldii*;
- *C. brevicaule* / *C. irumtiense* with ancestry/species-history interpretation retained;
- *takaoense* as external/public mechanistic anchor.

Required chain:

`ancestry-resolved colour -> effective pollination / abiotic response -> reproductive fitness`

Retain calibrated visible/UV phenotype, visitor/effective-contact data, relevant local abiotic measurements and achene/seed output. Distant white/coloured populations are not treated as a colour experiment without ancestry/geography/environment controls.

## Experiment 3 — phyllary/spine conditional gate

Do not manipulate phyllaries/spines until:

1. direct measurements validate the Azami image proxies in the focal system;
2. repeatable focal variation exists;
3. manipulation can alter antagonist access without a dominant wound artifact.

When admitted, measure both antagonist exclusion/damage and pollinator access/effective contact through final seed output. The large antagonist-cost meta result establishes biological pressure, not that any image proxy is a defence trait.

## Antagonist monitoring

Score focal capitula across bud/pre-anthesis, anthesis, seed development and mature-achene stages. Keep florivory, pre-dispersal seed predation and vegetative herbivory separate.

At the same field visits census whole-plant reproductive display so seasonal production and attacked-head fraction can be reconstructed without conflating plant and capitulum scales.

## Data model

- `aim2_capitulum_field_ledger_v1.csv`: head/treatment + final fitness;
- `aim2_capitulum_observation_bout_ledger_v1.csv`: head × time-window microclimate/pollen/pollinator/antagonist process;
- `aim2_plant_display_predation_ledger_v1.csv`: plant × census seasonal context.

Fine-grained event tables may be added later only if needed; they must retain `individual_id + capitulum_id + time`.

## Priority under limited field capacity

1. protect Aim 1 population replication;
2. baseline capitulum/plant measurements;
3. orientation feasibility with explicit timing + abiotic pathways;
4. W/coloured function;
5. phyllary/spine only after validation;
6. stickiness opportunistically.

## Stop rules

- no interaction-only sample without ancestry linkage;
- no visitation = effective pollination shortcut;
- no all-day visitation = no orientation effect shortcut;
- no adaptation claim without reproductive outcome;
- no pooled antagonist classes;
- no mixing seasonal plant display with focal-head traits;
- no final sample-size fixation before pilot variance/feasibility;
- no reduction of core population-genomic replication to fund Aim 2 manipulation.
