# Orientation × environment counterfactual falsification v1

Status: **VALIDATED RESULT — HISTORY-EMBEDDED ECOLOGICAL CORRESPONDENCE**

## Question

The frozen nine-taxon East-Asian panel shows a large and direction-stable orientation contrast for precipitation seasonality (BIO15) and a secondary temperature contrast (BIO1), but the original phylogeny-aware inferential threshold is not crossed and the small held-out orientation model does not outperform phylogeny-only prediction.

This post-result falsification asks a different question:

> Is the observed environmental correspondence unusually strong among alternative orientation maps that preserve the same 5U/4D state count, and does that rarity remain after counterfactual maps are constrained to resemble the observed evolutionary history?

## Frozen design

All `choose(9,4)=126` assignments of four downward/nodding taxa were exhaustively enumerated. Environmental values and the six accepted AU topologies were never shuffled. Each assignment was inserted into the full 20-tip orientation crosswalk while all non-panel resolved states and ambiguous states were held fixed.

Three comparison pools were frozen before result inspection:

1. all 126 state-count-preserving maps;
2. maps whose six-topology minimum-step profile exactly matches the observed history;
3. the history-nearest quartile among recurrence-profile matches, ranked only by lower/upper relative-depth distance.

The observed history required exactly five minimum changes on each of the six accepted topologies. Forty of 126 counterfactual maps matched this recurrence profile. The history-nearest quartile contained 10 maps.

## BIO15 — precipitation seasonality

Observed standardized D-minus-U effects reproduce the frozen result exactly: **+1.320 to +1.330 SD**, with median signed statistic **+1.325**.

### All state-count-preserving worlds

Only **5/126 = 3.97%** of all 5U/4D assignments were at least as strongly positive as the observed map. The same exact rank was recovered on each of the six accepted topologies.

An opposite-direction world exists in this unrestricted set, so the positive observed sign is not mathematically forced by having four D and five U taxa.

### Same recurrence profile

Among the **40** assignments requiring exactly five minimum changes on every accepted topology, **3/40 = 7.5%** were at least as strongly positive as observed.

A strongly reversed BIO15 world also exists in this recurrence-matched pool (signed statistic **−1.784**). Therefore the five-change recurrence profile alone does not force the positive BIO15 correspondence.

### Similar recurrence + relative-depth geometry

Among the **10** recurrence-matched maps closest to the observed topology-only lower/upper depth geometry, **3/10 = 30%** were at least as strongly positive as observed.

No BIO15 counterfactual in this nearest-history pool reversed sign.

Thus the observed BIO15 magnitude is unusual among arbitrary same-count state maps, but it is **not unusually large once the comparison is restricted to histories with similar recurrence and depth geometry**. At the same time, the disappearance of reverse-sign worlds in the closest-history set shows that the positive direction is tightly associated with this lineage/history configuration.

## BIO1 — annual mean temperature

The observed D-minus-U effect reproduces the frozen result exactly at **−0.975 to −0.967 SD**. Using the prespecified signed direction `D < U`:

- all 126 maps: **8/126 = 6.35%** at least as extreme;
- recurrence-profile matched: **4/40 = 10%**;
- history-nearest: **3/10 = 30%**.

Unlike BIO15, a weak opposite-direction world remains even in the history-nearest pool. BIO1 is therefore a weaker counterfactual discriminator than BIO15.

## Classification

`counterfactual_correspondence_not_strengthened_beyond_history`

This does **not** mean that orientation and BIO15 are unrelated. It gives a more specific result:

> **The observed BIO15 correspondence is stronger than expected from arbitrary placement of four downward states, but much of that distinctiveness is inseparable from the lineage/history geometry of where downward states occur.**

The counterfactual analysis therefore strengthens the V7 interpretation of **lineage-embedded, scale-partitioned ecological correspondence**, rather than supporting an ancestry-independent climatic effect.

## Methodological implication

A trait–environment effect can look exceptional under a state-count-preserving null and cease to be exceptional after conditioning on an equally plausible evolutionary-history class. Counterfactuals that preserve only state frequencies answer a different question from counterfactuals that preserve recurrence and transition-depth geometry.

For EAzami this provides a concrete methodological result:

`trait–environment correspondence -> count-preserving counterfactual -> recurrence-matched counterfactual -> depth-matched counterfactual`

can reveal whether an apparent ecological association is separable from the historical arrangement of the trait itself.

## Claim boundary

This is a post-result falsification/sensitivity analysis and does not retroactively convert the frozen orientation ecology from `unresolved` into a preregistered confirmatory result. It does not establish precipitation as a selective agent, adaptation, plasticity or historical climatic causation. History matching conditions on recurrence and topology-only depth but cannot condition on all lineage properties, geography or unmeasured ecology. The panel remains nine species-level taxon centroids rather than same-individual phenotype–environment observations.

Machine contract: `data/evidence/chapter2_orientation_environment_counterfactual_contract_v1.json`  
Frozen result: `data/evidence/chapter2_orientation_environment_counterfactual_result_v1.json`  
Workflow run: `33835638889`; artifact `9923176123`; SHA256 `4528d35ed1308a8b47ca92c6ed4680267ccbe3579b249fe1762e520973410b5d`.
