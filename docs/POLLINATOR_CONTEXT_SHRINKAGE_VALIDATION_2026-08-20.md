# Pollinator context shrinkage validation

Status: 2026-08-20

## Why this check follows PR #38

PR #38 showed that the four *Cirsium purpuratum* heads-probed-per-visit slopes cannot be represented perfectly by one shared annual mean plus one shared density ratio. However, the fully context-specific four-parameter structure is saturated: four parameters for four observations.

Therefore the next question is predictive rather than training-fit based:

> **Do context-specific deviations improve prediction when they are shrunk toward a shared response structure?**

## Data

All four slopes come from the same primary study, same species, same driver and same response definition:

- 1997 high-density stand: 0.11;
- 1997 low-density stand: 0.25;
- 1998 high-density stand: 0.078;
- 1998 low-density stand: 0.24.

Canonical source: `data/evidence/capitulum_pattern_reduction_targets_v2.csv`.

## Model

On log slope:

`log(slope) = common mean + density contrast + year deviation + year×density deviation`

The common mean and density contrast are unpenalized. The year and year×density terms receive the same ridge penalty `lambda`, shrinking them toward the shared structure.

`lambda` is selected only by leave-one-out prediction across a fixed 401-point grid from `1e-4` to `1e4`. This is not a posterior variance estimate.

## Result

- shared density-only LOO log-RMSE = **0.244791**;
- partial-pooling LOO log-RMSE = **0.239090**;
- predictive improvement = **2.33%**;
- selected `lambda` = **1.9953**;
- effective degrees of freedom = **2.484**, versus 2 for the shared model and 4 for the saturated model.

Full-data shrunk context coefficients are small:

- 1998 mean deviation = **-0.0650** on log scale;
- 1998×low-density deviation = **+0.00485**.

The fitted slopes are 0.0957, 0.2524, 0.0897 and 0.2377. The model retains the major density contrast while strongly shrinking the extra year/context terms.

## Interpretation

The correct conclusion is narrower than the raw residual comparison from PR #38:

1. forcing all contexts to share one response structure does create detectable training residual;
2. allowing context flexibility can reduce that residual;
3. **but with only four slopes, partial pooling yields only a small leave-one-out predictive gain**;
4. the present evidence therefore does **not** justify adding unpooled year-specific pollinator parameters to the full macro-interaction simulation.

The full simulation should keep population/context heterogeneity as a biological possibility and field-design requirement, but not proliferate temporal parameters until replicated context data exist.

## Development decision

`do_not_promote_unpooled_temporal_context_parameters`

Next empirical discriminator:

- repeat comparable display→effective-pollination response measurements across populations and time windows;
- retain density/context metadata;
- then estimate context variance with partial pooling using actual replication.

This result does not weaken the broader v2 conclusion that environment + mutualist + antagonist channels jointly outperform one-driver models. It only prevents the pollinator submodel from being over-expanded on four observations.
