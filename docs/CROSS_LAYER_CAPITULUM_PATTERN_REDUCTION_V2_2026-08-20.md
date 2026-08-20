# Cross-layer capitulum pattern reduction v2

Status: 2026-08-20

## Decision

Keep the two repositories separated by inferential role:

- **Azami** owns the global observational patterns: repeated head-level phenotype, hierarchical variation and environment–trait association.
- **EAzami** owns the biological-interaction evidence, quantitative fitness synthesis and generative reduction tests.

The question here is not whether the Azami correlations are causal. It is:

> **Can a deliberately small mechanism family reproduce both the Azami observation vector and the independently measured pollinator/antagonist/fitness patterns?**

v1 used binary pass/fail gates. v2 replaces those gates with an uncertainty-weighted distance and separates two structural questions:

1. **modularity** — must all capitulum modules share one latent within-taxon lability axis?
2. **interaction heterogeneity** — can one pollinator/antagonist response regime describe all populations, or must interaction strengths vary among populations/local contexts?

This remains a prior-predictive model-adequacy screen, not posterior inference.

## Expanded target registry

Canonical registry:

`data/evidence/capitulum_pattern_reduction_targets_v2.csv`

It contains **36 evidence-typed rows**:

- 8 Azami global observation targets;
- 17 Cirsium interaction/fitness targets;
- 10 Asteraceae mechanism calibrations/context rows;
- 1 external conceptual selection-conflict row.

Rows are not automatically treated as equally quantitative. `hard`, `soft` and `context` preserve evidence strength and inferential distance.

### Azami observation layer

The principal patterns remain:

- below-taxon visible variance across primary endpoints: **0.5886–0.9307**;
- common cross-module lability/environment-coupling rho **−0.0569**, bootstrap interval **−0.265 to 0.155**;
- positive orientation–temperature and chroma–precipitation associations;
- globally weak/model-dependent gross-outline support;
- seasonality associations in the image-derived involucre proxies: roughness **+0.0975**, spread **+0.0937**, maximum spine-like projection **+0.0911**.

These are observational reproduction targets. They are not converted into adaptive claims.

## Interaction patterns and concrete numbers

### Antagonist fitness cost

The direct Cirsium seed-output meta-analysis is the strongest quantitative anchor:

- herbivory-removal / ambient-herbivory seed-output RR = **2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- I² ≈ **1%**.

### Population-specific antagonist regime

In *C. purpuratum*, seed-damage probability against total floret production was fitted as:

- Nikko: `Pr = 1 − exp(−0.000063 F)`;
- Kawamata: `Pr = 1 − exp(−0.0000075 F)`.

The fitted attack coefficient differs by about **8.4-fold**. This is not noise to be averaged away: it is a target showing that the same display can operate under very different enemy pressure among populations.

### Population/density-specific pollinator regime

For *C. purpuratum* / *Bombus diversus*, heads probed per visit increased with display, but the slope depended strongly on stand density:

- 1997 high density: **0.11**;
- 1997 low density: **0.25**;
- 1998 high density: **0.078**;
- 1998 low density: **0.24**.

The same literature gives soft curve-strength targets:

- display → visitation-per-plant curve R² ≈ **0.637**;
- display → heads-probed-per-visit R² ≈ **0.533**.

Thus pollinator benefit is not one universal display coefficient either.

### Cross-Asteraceae size–predation calibration

In the Australian alpine 29-species dataset, head diameter correlated with:

- all predispersal seed predation: **r = 0.676**;
- Tephritidae predation: **r = 0.623**;
- mean Tephritidae larvae: **r = 0.482**.

Using one species per genus still gave **r = 0.717 / 0.661 / 0.606**, respectively. v2 scores the 29-species all-predation value as a soft external calibration and retains the others as robustness context.

### Additional numerical context retained but not forced into one score

- *C. pitcheri*: infested capitula produced **60% fewer mature seeds**.
- *C. arvense*: **20–85%** of heads attacked across place/date, with **20–80%** seed damage in attacked heads.
- *C. canescens*: an approximately **3-fold** viable-seed loss was associated downstream with about **6-fold** fewer seedlings and **6–37-fold** fewer new adults.
- *C. arvense* floral fragrance can be roughly **25-fold** greater than *C. repandum* and is temporally aligned with pollinator rather than florivore activity.
- complete pollinator exclusion in the retained *Cirsium* experiment produced **55%** total reproductive failure versus **<7%** under the other treatments.
- *Cremanthodium campanulatum*: nodding versus experimentally erect achene set **56.3% vs 15.7%**, RR ≈ **3.586**, with no orientation preference by pollinators.
- sunflower: east-facing plants out-sired west-facing plants in **5/7** trials, while a later study found no all-day landing difference by azimuth.
- *C. discolor* stickiness manipulation remains a useful null/negative control.

These numbers constrain interpretation without pretending that scent, orientation, visitation, seed predation and lifetime fitness are one interchangeable outcome.

## Seven model families

v2 compares:

1. `ENV_ONLY`
2. `ENV_POLL`
3. `ENV_ANT`
4. `FULL_COUPLED_GLOBAL`
5. `FULL_MODULAR_GLOBAL`
6. `FULL_COUPLED_HET`
7. `FULL_MODULAR_HET`

`MODULAR` allows module-specific within-taxon variance. `HET` allows separate population/local-context pollinator and antagonist regimes.

Each family receives **1,500 deterministic broad prior draws**. Scores are uncertainty-weighted squared distances. The numerical widths used for several descriptive literature targets are deliberately broad operational screening weights, not posterior measurement-error estimates.

## Result

Canonical summary:

`data/evidence/capitulum_pattern_reduction_simulation_v2_summary.json`

### Best-distance ranking

| model | best distance | 1% distance |
|---|---:|---:|
| `FULL_MODULAR_HET` | **7.61** | **15.43** |
| `FULL_MODULAR_GLOBAL` | 18.95 | 25.83 |
| `FULL_COUPLED_HET` | 25.49 | 35.79 |
| `FULL_COUPLED_GLOBAL` | 29.83 | 42.26 |
| `ENV_POLL` | 591.11 | 602.32 |
| `ENV_ANT` | 878.34 | 887.82 |
| `ENV_ONLY` | 1439.34 | 1446.00 |

The absolute distance scale has no biological units and must not be interpreted across different target registries. The useful information is the within-v2 model contrast.

### Factorial diagnosis

Relative to `FULL_COUPLED_GLOBAL`:

- allowing module-specific variation lowers best distance by **10.87**;
- allowing interaction heterogeneity alone lowers it by **4.33**;
- the model allowing both reaches **7.61**.

Within the modular model, adding interaction heterogeneity lowers distance by **11.34**. Under heterogeneous interaction regimes, adding modularity lowers distance by **17.88**.

So both structural axes matter in this minimal model family.

## What the best model reproduces

The best `FULL_MODULAR_HET` draw reproduces several independent scales simultaneously:

- below-taxon fractions **0.572–0.822**, close to the observed Azami range;
- cross-module lability correlation **−0.148**, inside the empirical uncertainty interval;
- herbivory-removal seed-output RR **2.653**, close to the meta-analytic 2.674;
- size–predation `r = 0.691`, close to the external 0.676;
- attack coefficients `6.82×10⁻⁵` and `8.25×10⁻⁶`, close to the two *C. purpuratum* regimes;
- *C. pitcheri*-scale seed loss **0.636**;
- external orientation-protection RR **3.31**.

## What it still fails to reduce cleanly

The largest remaining distance component is the **population-specific pollinator response**.

The best draw produces probing slopes approximately:

`0.107 / 0.411 / 0.106 / 0.454`

versus observed:

`0.11 / 0.25 / 0.078 / 0.24`.

So merely multiplying one global response curve by a high-density/low-density factor is still too crude. The next pollination model should explicitly represent at least:

- local floral density / neighbouring display;
- visitation saturation;
- within-plant movement and diminishing probing return;
- possibly visitor identity or revisitation state.

This is a useful failure, not something to tune away by adding arbitrary parameters.

## Biological interpretation

The reduction sequence now says more than v1:

```text
Azami observation layer
  large within-taxon variation
  + module-specific environmental structure
  + no common lability axis
                ↓
Interaction literature
  large antagonist fitness cost
  + pollinator benefit of display
  + enemy cost of display
  + strong population/context dependence
                ↓
Reduction test
  environment only                    fails badly
  one biotic channel                  fails badly
  full interactions + shared lability improves
  module-specific variation           improves further
  population-specific interactions    improve further
  both together                       best current reduction
```

Within this deliberately minimal family, **semi-independent trait modules plus context-dependent interaction regimes are the most economical current reduction**.

This is not proof that those are the unique causal mechanisms. Many richer models can generate the same summaries.

## Consequence for the doctoral field design

Population replication in Aim 2 is no longer only an ancestry-control convenience.

It is required to test a model prediction:

> **the functional effect of a capitulum state should change among populations as pollinator availability, local floral density and antagonist pressure change.**

Therefore the key field response is not simply a global treatment mean. For each focal population retain:

- trait state / manipulation;
- local floral density and plant display;
- visitor guild, effective contact and revisitation where possible;
- antagonist abundance/damage;
- mature/filled achene output;
- ancestry/cytotype identity from Aim 1.

A trait can then be tested for both a mean effect and a `trait × interaction-regime` effect.

## Repository boundary

No simulation-derived causal statement should be moved into the Azami submission results.

Azami supplies frozen observation targets. EAzami tests whether candidate mechanisms can reproduce them jointly with independent biological-interaction evidence.
