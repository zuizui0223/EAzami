# Macro observation → interaction mechanism → pattern reduction

Status: 2026-08-20

## Repository boundary

### `zuizui0223/azami` = observational macro layer

Azami Chapter 1 remains responsible for what is directly observed in global public-image phenomics:

- continuous head-level trait distributions;
- below-taxon / among-photo / among-head variance;
- trait-specific environmental associations;
- spatial robustness and environmental sorting;
- image-derived involucre/spine-like proxy associations.

Azami does **not** infer that pollinators, antagonists, rain, UV, plasticity or local adaptation caused those patterns.

### `zuizui0223/EAzami` = mechanism-reduction layer

EAzami receives frozen observational targets from Azami and combines them with quantitative biological-interaction targets from experiments and meta-analysis. Its additional question is:

> **What is the smallest ecological/evolutionary mechanism family that can generate the joint pattern bundle?**

This is deliberately stronger than explaining one environmental correlation at a time.

## Target registry

Machine-readable source:

`data/evidence/macro_interaction_pattern_targets_v1.csv`

The registry keeps four kinds of evidence separate:

1. **Azami observational targets** — environment↔trait and cross-scale structure;
2. **Cirsium quantitative targets** — direct pollination, seed-predation and seed-output effects;
3. **Asteraceae comparative targets** — broader capitulum-size/antagonist and orientation mechanisms;
4. **null / scale-dependent targets** — e.g. stickiness null and time-window-specific orientation effects.

A target may be stored as:

- an exact effect or interval;
- a sign / monotonicity pattern;
- a null expectation;
- an ordinal relationship between modules.

Not every literature row is scored in simulation v1. `fit_target` rows are the compact core; `context_target` rows are held out for later falsification/extension.

## Quantitative interaction patterns already frozen

### Antagonist cost

The narrow EAzami lnRR meta-analysis estimates:

- seed output under reduced herbivory / ambient herbivory = **2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- I² ≈ **1%**.

This is a direct seed-output target, not an evidence count.

### Display → pollinator benefit in *Cirsium purpuratum*

Ohashi & Yahara's display experiment reports:

- relative bumblebee visitation vs number of flower heads: saturating positive relationship, `R² = 0.637`, `n = 57`;
- number of heads probed per visit vs display: positive relationship, `R² = 0.533`, `n = 57`.

### Display → antagonist cost in *Cirsium purpuratum*

Ohashi & Yahara's field populations show increasing predation with display:

- Nikko: `Pr = 1 - exp(-0.000063 F)`, `n = 13`, `R² = 0.44`;
- Kawamata: `Pr = 1 - exp(-0.0000075 F)`, `n = 27`, `R² = 0.26`;
- Nikko multiple regression: floret number standardized coefficient `0.86`, `t = 2.34`, simple `r = 0.61` for seed damage.

Thus the same broad display axis can increase both mutualist response and antagonist exposure.

### Broader Asteraceae pattern

Fenner et al. (2002) found increasing pre-dispersal infestation with capitulum size among 20 Asteraceae species and within three detailed species. A later 34-species alpine survey found increasing infestation with capitulum size and, despite lower loss per infested capitulum in larger heads, higher **overall** pre-dispersal seed loss in larger-capitulum species.

### Orientation mechanisms are scale dependent

- *Cremanthodium campanulatum*: experimentally erect heads set fewer achenes than natural nodding heads; water/UV-B reduced pollen viability; pollinator preference between orientations was not detected.
- *Helianthus annuus*: east-facing heads warmed earlier, presented pollen earlier, received more early-morning visits and had a siring advantage.
- a 2024 sunflower field study found all-day pollinator landings independent of head azimuth.

The v1 model therefore must not equate a time-window interaction effect with a universal all-day visitation effect.

## Simulation v1: structural sufficiency

Script:

`analysis/simulate_macro_interaction_pattern_reduction.py`

Five model families are compared under broad symmetric parameter draws:

1. `environment_only`;
2. `pollinator_only`;
3. `antagonist_only`;
4. `full_tradeoff_common_lability`;
5. `full_tradeoff_modular_evolvability`.

The scored bundle asks whether one random draw can jointly reproduce:

- high below-taxon visible variance;
- the observed signs of orientation/colour/shape/involucre environmental responses;
- weak common lability↔environment-response coupling;
- stronger orientation/colour than gross-shape environmental structure;
- positive display→pollinator response;
- positive display→antagonist response;
- seed-output cost in the observed herbivory-RR range.

### Why the two full models differ

`full_tradeoff_common_lability` assumes one taxon-level response/lability factor shared across modules.

`full_tradeoff_modular_evolvability` allows orientation, colour, display/shape and involucre/defence modules to vary independently in their responsiveness.

This directly tests whether adding **modularity**, rather than merely adding more ecological drivers, is needed to reproduce the cross-scale decoupling seen in Azami.

## Interpretation boundary

Simulation v1 is a **prior-predictive pattern-reduction test**.

It is not:

- fitted demographic/evolutionary inference;
- a likelihood comparison;
- a posterior probability of mechanisms;
- proof that any target association is adaptive;
- proof that Azami image proxies are botanical defence traits.

The useful result is structural:

> which mechanisms are insufficient, which combinations can reproduce the joint pattern bundle, and which empirical targets most strongly discriminate model families?

## Next escalation rule

Only after v1 identifies a discriminating target should complexity increase. Candidate upgrades are:

1. replace broad interaction priors with raw-data reanalysis for additional *Cirsium* species;
2. add explicit time-window orientation dynamics;
3. add population ancestry/introgression from Aim 1;
4. fit focal parameters to ancestry-resolved field data.

Do **not** build a large ABM merely because it is possible. The simulation exists to reduce the observed pattern to the smallest mechanism set.
