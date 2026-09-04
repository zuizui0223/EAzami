# Orientation × environment counterfactual falsification v1

Status: **FROZEN DESIGN; RESULT PENDING CI**

Execution trigger: 2026-09-04; this line changes no contract, estimand, pool or decision rule.

## Question

The existing nine-taxon East-Asian panel shows a large, direction-stable orientation contrast for precipitation seasonality (BIO15) and a secondary temperature contrast (BIO1), but the frozen phylogeny-aware threshold is not crossed and the small held-out predictor does not beat phylogeny-only prediction.

This follow-up asks a different question:

> Is the observed environmental correspondence unusually strong among alternative orientation maps that preserve the same 5U/4D ecological-panel state count, including alternatives that retain the observed recurrence profile and similar relative-depth geometry?

## Counterfactual worlds

All `choose(9,4)=126` assignments are enumerated. Environmental values and topology are never shuffled. Only which four of the nine taxa are labelled downward/nodding is changed.

Each counterfactual is then inserted into the full 20-tip orientation crosswalk. The remaining orientation states are held fixed and ambiguous states remain ambiguous.

Three comparison pools are declared before result inspection:

1. all 126 state-count-preserving maps;
2. maps with the exact observed six-topology minimum-step profile;
3. the history-nearest quartile among recurrence-profile-matched maps, using topology-only lower/upper relative-depth distance.

## Primary and secondary axes

- primary: BIO15, observed direction `D > U`;
- secondary: BIO1, observed direction `D < U`.

The statistic is the median signed standardized PGLS effect across the same six accepted AU topologies.

## Reverse-direction calibration

For every pool, the analysis also asks whether a counterfactual with the opposite environmental direction exists. If an opposite-direction world can retain similar recurrence/depth geometry, the observed sign is not mathematically forced by the historical constraints.

## Interpretation boundary

This is a post-result falsification/sensitivity analysis. A rare observed correspondence among the declared counterfactual worlds can strengthen the statement that orientation and the environmental axis are non-randomly associated conditional on the declared history constraints. It cannot establish climatic selection, adaptation, plasticity or transition-time historical causation.

Machine contract: `data/evidence/chapter2_orientation_environment_counterfactual_contract_v1.json`.
