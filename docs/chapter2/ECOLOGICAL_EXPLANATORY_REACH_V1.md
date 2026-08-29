# Chapter 2 ecological explanatory reach v2

Status date: 2026-08-29

## Mainline

Chapter 2 uses a three-stage evidence sequence:

1. **minimum state-change lower bound** — how many changes are minimally required;
2. **relative event depth / placement resolution** — where in relative lineage depth those minimum histories can occur;
3. **ecological explanatory reach** — how far existing ecological data can account for the observed trait-state pattern after phylogenetic correction, without claiming historical causation.

The third stage is an empirical result, not a list of Discussion hypotheses.

## Estimand and decision rule

For a trait with sufficient state and climate coverage, the primary result reports:

- standardized state-associated climate effect and uncertainty;
- sign agreement across the accepted topology ensemble;
- species leave-one-out sign agreement;
- branchwise direction where a compatible diagnostic exists;
- whether the frozen primary inferential threshold is crossed;
- final class: `tendency_supported`, `unresolved`, or `not_evaluable`.

The classification is intentionally modest:

- `tendency_supported` = state-diverse comparison is estimable, the primary-axis sign is stable across all accepted topologies and species LOO fits, and the frozen primary phylogenetic-association threshold is crossed;
- `unresolved` = an estimable, directionally stable correspondence exists but the frozen inferential threshold is not crossed;
- `not_evaluable` = current frozen state × ecology overlap cannot estimate the requested contrast.

**Predictive gain is not required for this classification.** A held-out comparison against mean-only and phylogeny-only baselines is retained in Supporting Information as a transparency/small-panel sensitivity only.

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

### BIO1 — annual mean temperature

Downward/nodding taxa occupy colder niches:

- standardized PGLS effect, D minus U: **−0.975 to −0.967 SD**;
- P: **0.09604 to 0.09793**;
- sign agreement across accepted topologies: **6/6**;
- species LOO sign agreement: **54/54**;
- branchwise directional shift: **−0.1993 to −0.1992 SD**;
- branchwise permutation P: **0.108 to 0.136**.

### Orientation verdict

**`unresolved`**.

There is a reproducible ecological correspondence — higher BIO15 and lower BIO1 in the downward state — that persists after phylogenetic correction, across all accepted topologies, under species LOO, and in the independent branchwise direction diagnostic. The frozen primary PGLS threshold and branchwise permutation threshold are not crossed. This is stronger than a candidate-cause list and weaker than historical ecological explanation or adaptation.

Raw Comp1061 UFBoot trees were not retained in the accepted archived ecological input bundle, so an ecology-specific raw-bootstrap sign fraction is **`not_evaluable`** rather than silently replaced by the six AU topologies. The historical minimum-change and relative-depth analyses continue to propagate 1,000 Japan38 bootstrap topologies separately.

## Predictive sensitivity — Supporting Information only

For transparency, the n=9 panel also compares held-out climate prediction under:

1. a training-set mean-only null;
2. phylogeny-only Brownian conditional prediction;
3. phylogeny + orientation Brownian conditional prediction.

Orientation improves over a naive mean-only baseline but not over phylogeny-only in the current small panel. This is useful for understanding the data, but **it does not define the `unresolved` verdict** because the Chapter 2 question is how far current ecology corresponds to and constrains trait states, not whether orientation is the best predictor of climate.

## Phyllary posture

**`not_evaluable`** with current frozen climate assets.

The historical state map contains 10/38 resolved concepts, but only two taxa at the frozen occurrence gate also have an unambiguous phyllary state in the available climate panel, and both are `ascending`. There is therefore no state-diverse phylogeny-aware climate contrast to estimate.

Enemy exclusion, wetness protection and pollinator-access trade-offs remain Chapter 3 mechanisms. Their absence from this result is a coverage boundary, not evidence against those mechanisms.

## Stickiness

**`not_evaluable`** with current frozen climate assets.

The historical state map contains 13/38 resolved concepts, but only two taxa at the frozen occurrence gate also have an evaluable stickiness state, and both are nonsticky/nearly nonsticky. No sticky-versus-nonsticky climate contrast can be estimated. Current data also cannot distinguish climate association from enemy exclusion, pollinator cost or production cost.

## Climate is not assumed to be the only explanatory axis

A separate non-climate constraint registry (`data/evidence/chapter2_nonclimate_explanatory_constraints_v1.json`) records what current data can already bound without forcing underpowered multi-predictor models:

- deterministic one-to-one **ploidy → orientation** mapping is contradicted descriptively;
- one-to-one **broad colonization history → capitulum configuration** mapping is contradicted descriptively;
- independent Japanese population nuclear data constrain the assumption that one species tip is one homogeneous genomic unit;
- independent rDNA and local phylogenomic/network data show that the Comp1061 reconstruction is the harmonized full-panel scaffold, not the only nuclear evidence;
- pollinator/antagonist context is **not evaluable as a joined Japan38 comparative predictor** with current assets.

These are constraints, not causal explanations.

## Chapter 2 result

> Multiple minimum changes are required for orientation, phyllary posture and stickiness, but existing ecological data explain those histories unequally. Orientation shows a topology- and species-LOO-stable correspondence with precipitation seasonality and annual temperature and remains `unresolved` under the frozen inferential thresholds. Phyllary posture and stickiness are `not_evaluable` with the present climate/state overlap. Existing cytotype, broad-history and independent nuclear evidence additionally constrain simple alternatives without identifying a selective cause.

This closes the sequence as:

**minimum change count → relative event depth → ecological explanatory reach → explicit Chapter 3 data boundary**.

## Claim ceiling

Do not translate present-day taxon niche correspondence into an environmental cause for a particular reconstructed transition. These analyses do not establish ancestral climate, event age, convergence, adaptation, selective mechanism or fitness effect. `not_evaluable` must never be rewritten as “no relationship,” and a constrained simple model must not be confused with a complete causal explanation.
