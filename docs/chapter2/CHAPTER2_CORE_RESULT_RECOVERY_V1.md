# Chapter 2 core-result recovery v1

Status date: 2026-08-28

Scientific status: **COMPLETE_CONFIGURATION_DIVERSITY_AND_MINIMUM_CHANGE_CORE** plus **BOUNDED_ECOLOGICAL_EXPLANATORY_REACH**

Machine-readable ledger: `data/evidence/chapter2_core_result_recovery_v1.csv`

## Why the Chapter 2 story needed compression

The repository contains completed phylogenomic, trait-history, continuous-trait, niche, cytotype, function, simulation and field-readiness lanes. Those lanes answer different questions. Treating every completed analysis as one Chapter 2 result creates a sequence of weak diagnostics and obscures the strongest biological result.

The active paper therefore uses only complete, source-backed, reproducible results that directly answer historical assembly or the explanatory reach of existing ecology. Function, present-state simulation and field protocols remain routed to their proper chapters.

## New Chapter 2 position

Chapter 1 measures capitulum phenotype across present space. Chapter 2 asks **How many state changes are minimally required in the traits that form alternative capitulum configurations, at what relative lineage depth those histories remain admissible, and how far existing ecological data explain the present trait states after accounting for phylogeny?** Chapter 3 then resolves remaining population/history uncertainty with own genomic and same-individual phenotype data and tests causal function separately.

This is not a test of whether Chapter 1 significance is repeated. It is a standalone evolutionary-morphology question using an independently assembled EAzami evidence base.

The operational sequence is:

**minimum state-change lower bound → relative lineage-depth / named-edge event resolution → ecological explanatory reach → explicit Chapter 3 boundary**.

## Four contributions

### 1. Biological result: configuration diversity with multiple minimum changes within a dominant radiation

The historical context is concentrated: 36 of 38 sampled Japanese concepts, or 94.7%, occur in the dominant radiation. Within the authority-covered dominant-radiation subset, at least three harmonized orientation × stickiness configurations are observed: downward/nonsticky, upward/nonsticky and upward/sticky.

The accepted topology ensemble requires more than one minimum change in every focal trait ontology:

- orientation: 20 resolved concepts; ML minimum 6; UFBoot range 4–6, median 5;
- phyllary posture: 10 resolved concepts; exactly 3 changes in all 1,000 UFBoot trees;
- stickiness: 13 resolved concepts; exactly 5 changes in all 1,000 UFBoot trees.

The positive biological conclusion is that capitulum diversity in this young radiation cannot be represented only as retention of one unchanged set of trait states. These counts remain topology-conditioned lower bounds rather than counts of independent origins or convergence.

### 2. Inferential result: minimum-count stability, relative lineage-depth and named-edge resolution are different properties

Stable counts do not imply equally resolved histories. Orientation has no individually forced maximum-likelihood edge and JPN36 is forced in only 0.227 of bootstrap topologies. The JPN36 phyllary terminal edge is forced in 0.728. Stickiness is more tightly localized: JPN06 and JPN36 terminal edges are forced in 0.995 and 0.707, and one nine-tip internal edge in 0.681, of bootstrap topologies.

Exact topology-only relative lineage-depth envelopes add a separate coordinate. Median bootstrap lower–upper envelopes are 0.795–0.994 for orientation, 0.695–1.000 for phyllary posture and 0.937–0.954 for stickiness. Median widths are 0.200, 0.305 and 0.017.

Thus three resolution coordinates must be kept separate:

1. **minimum-count stability**;
2. **relative lineage-depth envelope**;
3. **named-edge event resolution**.

Stickiness is count-stable and depth-constrained, phyllary is count-stable but depth-ambiguous, and orientation remains weakly localized.

### 3. Boundary result: one shared whole-capitulum transition history is not required

Zero of three trait pairs meets the cross-treatment shared-localization rule. Branch-aware transition-excess correlations are positive, but the equal-branch fifth percentiles are negative for all three pairs. This constrains a simple common-lability alternative without proving evolutionary independence, developmental modularity or distinct selective agents.

### 4. Ecological result: explanatory reach is asymmetric and stops before adaptation

The frozen East-Asian orientation panel contains nine taxa, U=5 and D=4, each with at least ten independent thinned environment-complete occurrences.

Across the six AU-nonrejected optimized topologies:

- BIO15 D−U = +1.320 to +1.330 SD, P=0.05054–0.05239;
- BIO1 D−U = −0.975 to −0.967 SD, P=0.09604–0.09793;
- accepted-topology sign agreement = 6/6 for both axes;
- species LOO sign agreement = 54/54 for both axes.

The branchwise diagnostic has the same directions on all six topologies, but its permutation thresholds are not crossed.

Held-out prediction clarifies what the correspondence explains. Relative to a mean-only null, phylogeny+orientation improves prediction: BIO15 ΔMSE=+0.224 to +0.230 and BIO1=+0.364 to +0.370. Relative to phylogeny-only Brownian kriging, the same model is worse: BIO15 ΔMSE=−0.108 to −0.102 and BIO1=−0.199 to −0.192. Therefore orientation carries stable ecological information but does not yet add explanatory reach beyond ancestry. Its evaluation is `unresolved`.

Phyllary posture and stickiness are `not_evaluable` at the same ecological gate. Each overlaps only two resolved n≥10 climate taxa, and neither overlap contains two state classes. This is not evidence of no ecological relationship.

## Hypothesis recovery

| Hypothesis | Result | Status |
| --- | --- | --- |
| The dominant radiation contains multiple capitulum configurations | at least three harmonized combinations | supported descriptively |
| Each focal trait requires more than one minimum state change | orientation 4–6; phyllary 3; stickiness 5 | supported as topology-conditioned lower bounds |
| Stable minimum-change counts imply equally stable event depth and locations | trait-specific depth and forced-edge profiles differ strongly | contradicted descriptively |
| One branch-localization pattern spans all three traits | zero of three pairs meets the cross-treatment rule | not supported; boundary result |
| Orientation has a broad climate correspondence after phylogenetic correction | BIO15 positive and BIO1 negative on 6/6 topologies and 54/54 species LOO fits | directional correspondence supported |
| Orientation adds predictive explanation beyond ancestry | positive ΔMSE vs mean-only null but negative ΔMSE vs phylogeny-only | unresolved |
| Phyllary and stickiness can be climate-tested with current assets | only two same-state evaluable climate taxa for each | `not_evaluable` |
| Minimum changes are independent origins or adaptations | ancestry, direction, historical environment, mechanism and fitness are not jointly observed | not tested |

## What belongs in the JEB main text

The main text has **five result groups only**:

1. 36/38 concepts in the dominant radiation and at least three harmonized orientation × stickiness configurations;
2. three trait-specific minimum-change distributions;
3. minimum-count stability versus relative lineage-depth and named-edge event resolution;
4. the zero-of-three cross-treatment shared-localization boundary;
5. ecological explanatory reach: orientation `unresolved`, phyllary posture `not_evaluable`, stickiness `not_evaluable`.

Species-tip colour compression now belongs in Supporting Information as a resolution audit. The continuous n=7 screen, cytotype overlap, source-balanced colour stop and legacy reconstruction-null diagnostics also remain Supporting Information. Their role is to bound interpretation, not to create a parade of null results.

## Material routed out of Chapter 2

- Azami present-integration and continuous reconstruction-null results: legacy method audit, not standalone EAzami primary evidence;
- v3/v4 covariance simulations: Chapter 1 robustness or thesis methods;
- reproductive-herbivory and selection-mosaic syntheses: Chapter 3 functional context;
- JPN36 and JPN15 manipulations: Chapter 3 causal tests after rights/conservation authorization;
- own Japan-wide RAD-seq: Chapter 3 history resolution, not a Chapter 2 completion dependency;
- dated transition timing and ecological event matching: STOP until a defensible dated ensemble exists.

## JEB presentation

**Recommended title**

> **Capitulum configuration diversity, minimum change counts and ecological explanatory reach in a young thistle radiation**

**Four-figure order**

1. dominant-radiation context, trait admission and observed configuration diversity;
2. minimum-change counts and relative lineage-depth envelopes;
3. named-edge localization and cross-trait shared-localization boundary;
4. ecological effect direction, topology/LOO robustness, null versus phylogeny-only prediction, and trait-level `unresolved/not_evaluable` evaluation.

The central sentence is:

> **A dominant young radiation contains multiple capitulum configurations and each of three constituent traits requires multiple minimum changes, but historical resolution and ecological explanatory reach are asymmetric: orientation has a stable climate direction without predictive gain beyond phylogeny, whereas phyllary posture and stickiness are not evaluable with the current ecological overlap.**

The title preserves the searchable phrase **Capitulum configuration diversity, minimum change counts** while the paper now closes with a quantitative ecological reach result.

## Claim ceiling

The paper establishes topology-conditioned minimum-change lower bounds, observed configuration diversity, trait-dependent relative lineage-depth and named-edge resolution, and bounded present ecological explanatory reach. Relative lineage-depth is not absolute time. Present trait–climate correspondence is not historical niche reconstruction, event-specific environmental matching, convergence, adaptation or causal selection. `not_evaluable` is a data-resolution result, not a biological negative.
