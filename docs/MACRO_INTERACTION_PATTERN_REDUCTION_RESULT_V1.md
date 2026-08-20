# Pattern-reduction simulation v1 — result

Status: 2026-08-20

## Run contract

- target registry: `data/evidence/macro_interaction_pattern_targets_v1.csv`
- scored targets: **11**
- model families: **5**
- prior draws: **180 per family**
- deterministic seed: `20260820`
- frozen summary: `data/evidence/macro_interaction_pattern_reduction_result_v1.json`

This is a structural sufficiency screen, not a fitted model-selection analysis.

## Ranking

| Model family | Best matched targets | Best pattern distance | Full-match rate |
|---|---:|---:|---:|
| full trade-off + modular evolvability | **11 / 11** | **0.118** | 1/180 = 0.0056 |
| full trade-off + common lability | 10 / 11 | 0.234 | 0 |
| antagonist only | 9 / 11 | 0.265 | 0 |
| pollinator only | 9 / 11 | 0.379 | 0 |
| environment only | 7 / 11 | 0.563 | 0 |

## What the first screen actually says

### 1. A single driver is insufficient

No environment-only, pollinator-only or antagonist-only draw reproduced the full observation-plus-interaction target bundle.

This is the strongest v1 result.

Azami's environment patterns cannot by themselves account for the quantitative pollinator/antagonist targets, while interaction-only models cannot jointly recover the frozen environmental structure and herbivory-cost pattern.

### 2. Joint ecological trade-offs are strongly favoured as a structural explanation

Putting environmental, pollinator and antagonist processes into the same generative model increased the best score from 7–9/11 to 10–11/11.

The best modular full-model draw simultaneously produced:

- below-taxon variance fraction = **0.751**;
- orientation–temperature `r = +0.411`;
- colour–precipitation `r = +0.306`;
- display–seasonality `r = +0.113`;
- display–precipitation `r = -0.030`;
- near-zero lability↔association coupling `rho = -0.0078`;
- orientation/colour environmental signal > shape signal (ratio **5.04**);
- display→pollinator `r = +0.722`, `R² = 0.521`;
- display→antagonist `r = +0.781`, `R² = 0.610`;
- reduced-herbivory seed-output RR = **2.876**, inside the empirical 95% target interval.

These are simulated summaries, not new empirical estimates.

### 3. Modularity is promising, but not yet demonstrated as necessary

Only `full_tradeoff_modular_evolvability` produced an 11/11 draw in this v1 run.

However, `full_tradeoff_common_lability` reached **10/11** with a lower but still good pattern distance. Its best draw reproduced the pollinator and antagonist response strengths and the empirical herbivory RR but missed the positive orientation–temperature target in that draw.

Therefore the correct current inference is:

> **The data bundle requires multiple ecological drivers more clearly than it requires modular evolvability specifically.**

Modularity becomes a testable second-stage hypothesis, not a conclusion from this toy screen.

## Why this is useful for the doctoral programme

The simulation now separates two questions that were previously mixed:

1. **Why are there trait/environment patterns?** — Azami documents them observationally.
2. **What minimal mechanism can generate those patterns together with known mutualist/antagonist effects?** — EAzami tests this structurally.

The first reduction result says that explaining an individual Azami environmental coefficient is too weak. A viable mechanism must simultaneously generate:

- environmental sorting;
- large below-taxon variation;
- weak cross-module common lability;
- display-dependent pollinator benefit;
- display-dependent antagonist cost;
- the large seed-output penalty of herbivory.

## Next discriminating targets

Do **not** add more model families yet. The next job is to discriminate the two full models.

Highest-value held-out targets are:

1. **orientation scale dependence** — early-morning pollinator effect in sunflower versus all-day null, plus nodding-head abiotic protection in *Cremanthodium*;
2. **direct defence architecture** — validated phyllary/spine measurements linked to antagonist access and seed output;
3. **population ancestry** — whether repeated trait states follow local ancestry/introgression rather than one shared species-level response axis;
4. **additional raw-data Cirsium interaction effects** — especially independent taxa rather than more contrasts from the same experiments.

These are the measurements most likely to distinguish `common_lability` from `modular_evolvability`.

## Claim boundary

The 11/11 result is not a posterior probability, Bayes factor, causal proof or estimate that the modular model is true. It shows only that, under the declared broad prior-predictive generator, the modular full model had the greatest structural capacity to reproduce the joint frozen pattern bundle.
