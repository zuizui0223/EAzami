# Chapter 2 ecological explanatory reach v1

## Mainline

Chapter 2 now uses a three-stage evidence sequence:

1. **minimum state-change lower bound** — how many changes are minimally required;
2. **relative event depth / placement resolution** — where in relative lineage depth those minimum histories can occur;
3. **ecological explanatory reach** — how far existing ecological data can account for the observed trait-state pattern after phylogenetic correction, without claiming historical causation.

The third stage is an empirical result, not a list of Discussion hypotheses.

## Estimand and decision rule

For a trait with sufficient state and climate coverage, report:

- standardized state-associated climate effect and uncertainty;
- sign agreement across the accepted topology ensemble;
- species leave-one-out sign agreement;
- branchwise direction where a compatible branchwise diagnostic exists;
- held-out prediction improvement relative to phylogeny-only;
- final class: `tendency_supported`, `unresolved`, or `not_evaluable`.

`tendency_supported` requires a stable direction plus positive predictive gain beyond phylogeny-only under the frozen primary gate. A stable direction without predictive gain is `unresolved`. Missing state diversity or inadequate coverage is `not_evaluable`, not a negative biological result.

## Orientation

The frozen primary East-Asian panel contains nine taxa (5 upward/erect, 4 downward/nodding) with at least ten independent thinned environment-complete occurrences per taxon. The first six AU-nonrejected optimized Comp1061 topologies are propagated; topology 1 is the maximum-likelihood member of the preregistered candidate set.

### BIO15 — precipitation seasonality

Downward/nodding taxa occupy higher precipitation-seasonality niches:

- standardized PGLS effect, D minus U: **+1.320 to +1.330 SD**;
- P: **0.05054 to 0.05239**;
- sign agreement across accepted topologies: **6/6**;
- species LOO sign agreement: **54/54** topology × left-out-taxon fits;
- branchwise directional shift: **+0.268 to +0.269 SD**;
- branchwise permutation P: **0.094 to 0.124**.

However, adding orientation to the Brownian phylogeny-only predictor does not improve held-out BIO15 prediction: mean LOO ΔMSE (phylogeny-only minus phylogeny+orientation) is **−0.108 to −0.102** across the six topologies. The direction is therefore robust, but predictive explanatory gain is not established.

### BIO1 — annual mean temperature

Downward/nodding taxa occupy colder niches:

- standardized PGLS effect, D minus U: **−0.975 to −0.967 SD**;
- P: **0.09604 to 0.09793**;
- sign agreement across accepted topologies: **6/6**;
- species LOO sign agreement: **54/54**;
- branchwise directional shift: **−0.1993 to −0.1992 SD**;
- branchwise permutation P: **0.108 to 0.136**.

Held-out BIO1 prediction also does not improve over phylogeny-only: LOO ΔMSE is **−0.199 to −0.192**.

### Orientation verdict

**`unresolved`**.

There is a reproducible ecological correspondence — higher BIO15 and lower BIO1 in the downward state — that persists after phylogenetic correction, across all accepted topologies, under species LOO, and in the independent branchwise direction diagnostic. But the frozen primary significance threshold is not crossed consistently and predictive performance is not improved over phylogeny-only. This is stronger than “candidate causes” and weaker than an ecological explanation.

Raw Comp1061 UFBoot trees were not retained in the accepted archived ecological input bundle, so an ecology-specific raw-bootstrap sign fraction is **`not_evaluable`** rather than silently replaced by the six AU topologies. The historical minimum-change and relative-depth analyses continue to propagate 1,000 Japan38 bootstrap topologies separately.

## Phyllary posture

**`not_evaluable`** with current frozen climate assets.

The historical state map contains 10/38 resolved concepts, but only two taxa at the frozen occurrence gate also have an unambiguous phyllary state in the available climate panel, and both are `ascending`. There is therefore no state-diverse phylogeny-aware climate contrast to estimate.

Enemy exclusion, wetness protection, and pollinator-access trade-offs remain Chapter 3 mechanisms. Their absence from this result is a coverage boundary, not evidence against those mechanisms.

## Stickiness

**`not_evaluable`** with current frozen climate assets.

The historical state map contains 13/38 resolved concepts, but only two taxa at the frozen occurrence gate also have an evaluable stickiness state, and both are nonsticky/nearly nonsticky. No sticky-versus-nonsticky climate contrast can be estimated. Current data also cannot distinguish climate association from enemy exclusion, pollinator cost, or production cost.

## Chapter 2 result

The result is therefore asymmetric rather than uniformly positive or negative:

> Multiple minimum changes are required for orientation, phyllary posture and stickiness, but existing ecological data explain those histories unequally. Orientation shows a topology- and species-LOO-stable correspondence with precipitation seasonality and annual temperature, yet does not improve held-out prediction beyond phylogeny alone and remains unresolved. Phyllary posture and stickiness are not evaluable with the present climate/state overlap and require direct local-environment and biotic measurements.

This closes the Chapter 2 sequence as:

**minimum change count → relative event depth → ecological explanatory reach → explicit Chapter 3 data boundary**.

## Claim ceiling

Do not translate present-day taxon niche correspondence into an environmental cause for a particular reconstructed transition. These analyses do not establish ancestral climate, event age, convergence, adaptation, selective mechanism, or fitness effect. `not_evaluable` must never be rewritten as “no relationship.”
