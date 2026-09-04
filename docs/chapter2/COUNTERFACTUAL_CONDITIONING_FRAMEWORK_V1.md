# Counterfactual conditioning framework for Chapter 2

Status date: 2026-09-04  
Role: **methodological synthesis / manuscript interpretation aid**

## Core problem

A trait–environment association can look unusual because the observed trait states are associated with environment, because those states are phylogenetically clustered, or because both arise from the same historical placement. A single label permutation does not distinguish these possibilities.

EAzami therefore uses a nested counterfactual conditioning ladder. Environmental observations and admitted phylogenies are held fixed while alternative trait maps are generated under progressively stronger historical constraints.

## Conditioning ladder

### Level 0 — observed map

Use the authority-backed trait map exactly as observed.

### Level 1 — state-frequency-preserving counterfactuals

Preserve only the number of taxa in each state. For the current East-Asian orientation panel, all `choose(9,4)=126` maps with five U and four D states are enumerated.

Question answered:

> Is the observed trait–environment contrast unusual relative to arbitrary placement of the same number of trait states?

### Level 2 — recurrence-conditioned counterfactuals

Retain only maps whose minimum-change profile matches the observed map across the same accepted topology ensemble.

Question answered:

> Is the observed ecological contrast still unusual among trait maps requiring the same amount of minimum historical change?

### Level 3 — recurrence + relative-depth-conditioned counterfactuals

Among recurrence-matched maps, retain the maps nearest to the observed topology-only lower/upper relative-depth geometry using a result-blind distance rule.

Question answered:

> Is the observed ecological contrast still unusual when both recurrence burden and historical placement depth resemble the observed trait history?

## Reverse-direction calibration

For each conditioning level, explicitly search for counterfactual maps with the opposite environmental sign.

This separates two questions:

1. Is the observed magnitude exceptional within the declared counterfactual class?
2. Is the observed sign mathematically forced by the declared historical constraints?

An opposite-direction map shows that the sign is not forced. Failure to find one in a finite, predeclared counterfactual class shows sign constraint within that class only; it is not evidence that the alternative history is biologically impossible.

## Current orientation result

Primary axis: BIO15 precipitation seasonality, observed D > U.

| Counterfactual pool | Maps | At least as positive as observed | Conditional fraction | Reverse BIO15 available? |
| --- | ---: | ---: | ---: | --- |
| state frequency only | 126 | 5 | 3.97% | yes |
| exact recurrence profile | 40 | 3 | 7.5% | yes; strongest signed statistic -1.784 |
| nearest recurrence + depth histories | 10 | 3 | 30% | no |

Secondary BIO1 shows 6.35% -> 10% -> 30%, and a reverse-sign map remains in the nearest-history pool.

## Interpretation

The observed BIO15 association is unusual under arbitrary state placement but loses magnitude-level extremeness when similar evolutionary geometry is retained. The present signal is therefore **history-conditioned / lineage-embedded**, not evidence for an ancestry-independent climatic effect.

This result is positive methodologically even though it does not strengthen a climatic mechanism: the conditioning ladder identifies which part of apparent ecological extremeness disappears after preserving the observed evolutionary history.

## Relation to other EAzami uncertainty layers

EAzami now separates three different robustness questions:

1. **Topology robustness** — does the historical inference survive alternative trees?
2. **Coverage robustness** — does the historical inference survive controlled loss/equalization of observed states?
3. **Counterfactual interpretation robustness** — does an ecological contrast remain exceptional under alternative trait maps with increasingly similar historical geometry?

These are non-exchangeable tests. Passing one does not imply passing another.

## General methodological claim

The defensible general statement is:

> Trait–environment associations in comparative radiations should be evaluated against counterfactual trait maps that preserve not only state frequencies but, where feasible, relevant properties of the observed evolutionary history. A contrast that is extreme under arbitrary label placement may cease to be exceptional once recurrence and historical depth are conditioned upon.

This is an inference framework, not a new ancestral-state reconstruction algorithm.

## Claim ceiling

Do not infer from this framework alone:

- natural selection;
- adaptation;
- plasticity;
- a transition-time environmental cause;
- independence from ancestry or geography;
- posterior probabilities from finite counterfactual fractions;
- biological impossibility from the absence of a reverse world in one finite counterfactual pool.

## Frozen sources

- `data/evidence/chapter2_orientation_environment_counterfactual_contract_v1.json`
- `data/evidence/chapter2_orientation_environment_counterfactual_result_v1.json`
- `data/evidence/chapter2_orientation_environment_scale_partition_v1.json`
- `data/evidence/chapter2_ecological_explanatory_reach_v1.json`
- `analysis/run_chapter2_orientation_environment_counterfactual_v1.py`
