# Azami capitulum v3 one-shot scoring v1

Status: frozen before model-family distances or rankings, 2026-08-27.

This comparison asks which of the fourteen preregistered conditional generator families is most structurally sufficient for the sixty-two artifact-backed Azami observational estimands. It does not identify a true causal mechanism.

## Primary and sensitivity scopes

The main score uses the preregistered complete-18 `>=5` scope. The `>=2` scope is a replication-threshold sensitivity and cannot replace the main score after outcomes are inspected. Each scope contains 31 scalar targets.

## Equal target-class weighting

The four target classes each receive one quarter of the total score:

- registered-module structure;
- environmental-block multivariate R2;
- within-vs-among coefficient-matrix cosine;
- core4-vs-process-extension partial R2.

Rows are averaged within a class before class means are averaged. This prevents target count from becoming an implicit weight.

## Frozen discrepancy scales

- structure: identity-scale squared error divided by `max(observed bootstrap 95% half-width, 0.05)^2`;
- block R2: square-root R2 difference divided by `0.10^2`;
- coefficient cosine: raw difference divided by `0.25^2`;
- incremental partial R2: square-root partial-R2 difference divided by `0.10^2`.

Observed permutation P/Q/support labels are not added as extra score terms because the partial-R2 target already represents the registered incremental estimand and post-outcome double counting is prohibited.

## Prior-predictive replication

Sixteen explicit paired seeds are frozen in `data/evidence/azami_capitulum_v3_scoring_contract_v1.json`. Every family is evaluated at every seed on the same artifact-backed environmental design.

The family-level primary statistic is the median total distance across the sixteen draws. Quartiles, draw ranks and paired win fractions are retained rather than reducing each family to one lucky draw.

## Robust-leader gate

A family is called a robust leader only when all frozen criteria pass:

1. it is the unique primary median leader outside the 5%/0.01 tie tolerance;
2. it beats every other family on at least 75% of paired primary draws;
3. its `>=2` sensitivity median rank is at most two;
4. its sensitivity median remains within 10% of the sensitivity-best family.

Failure gives `no_robust_leader`. It does not trigger retuning.

## Factor contrasts

Matched paired contrasts separately diagnose:

- coupled versus modular residual architecture;
- shared versus independent within/among coefficient architecture;
- core4 versus process-at-both-scales;
- core4 versus process-among-only;
- process-at-both-scales versus process-among-only.

A positive-direction fraction of at least 0.75 is reported as direction-consistent only. It is not causal support.

## Held-out evidence

FDT1 pollinator, antagonist, orientation, phyllary and stickiness evidence is excluded from the 62-target fit and remains independent biological interpretation/validation evidence.

## Stop rule

After the first one-shot workflow output is inspected, no target weight, discrepancy scale, seed, model family, generator prior, endpoint loading, scope hierarchy or process permission may be changed to rescue a preferred result. Any future redesign must receive a new version and cannot replace this frozen result.
