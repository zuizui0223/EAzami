# Chapter 2 relative event-depth contract v1

Status date: 2026-08-28
Status: **FROZEN WITH AUDITED RUNTIME AND PROVENANCE AMENDMENT BEFORE RESULT ADMISSION**

Machine-readable contract: `data/evidence/chapter2_relative_event_depth_contract_v1.json`

The mathematical estimand, trait scope, expected minimum-step ranges, ecological hypothesis classes and claim ceiling were frozen before inspecting the depth outcomes. Before admitting any result, a reproducibility audit fixed Biopython at 1.85, admitted Python 3.10 and 3.11 only, and corrected a pre-existing artifact-provenance mismatch; no estimand or threshold was changed. CI uses Python 3.11 and local verification additionally establishes byte identity under Python 3.10. Tree and UFBoot hashes are exact-byte hashes; the three tracked CSV inputs use explicitly declared CRLF-to-LF canonicalized SHA-256 so Windows and Linux checkouts represent the same scientific text.

## Provenance correction

The localization fractions 0.201, 0.754, 0.67 and 0.40 reproduce with superseded tree run `32845725038`. The existing v1 history summary attached them to accepted run `32923076873`, whose tree and UFBoot hashes differ. Under run 329 the pre-extension fractions are 0.227, 0.728, 0.694 and 0.393, respectively. After adding the already frozen JPN24 sticky state, the current fractions become 0.227 for orientation JPN36, 0.728 for phyllary JPN36, 0.995 for stickiness JPN06 and 0.707 for stickiness JPN36.

The old fractions remain reproducible historical audit values but are not admissible as run-329 or post-JPN24 results.

## Question

> Among all histories that attain the frozen minimum number of unordered state changes, how shallow or deep can those changes be placed on the admitted topology without pretending that the phylogram is a dated tree?

This layer follows, but does not replace, the completed minimum-count result. It distinguishes three statements:

1. how many changes are minimally required;
2. how relatively shallow or deep the admissible minimum changes can be placed;
3. which ecological hypotheses those histories nominate for later tests.

Only the first two are Chapter 2 historical results. The third is a bounded prediction layer.

## Frozen trait scope

The completed Japan38 discrete histories are exactly:

- orientation: 20 resolved concepts;
- phyllary posture: 10 resolved concepts;
- stickiness: 13 resolved concepts after the frozen JPN24 authority extension.

Flower colour is not a fourth discrete history because no Japan38 W/C/P ontology with sequenced-individual morph linkage is frozen. Display is not a fourth history because only five of 38 exact concepts share one directly comparable size metric. Cytotype is an explanatory covariate rather than a capitulum trait.

## Relative lineage-depth estimand

For every non-root edge, let `N` be the total number of admitted concept tips and let `d` be the number of descendant tips subtended by that edge:

`relative_lineage_depth = (N - d) / (N - 1)`.

- `1.0` denotes a terminal edge;
- values nearer zero denote edges subtending broader, relatively deeper descendant lineages;
- the value is topology-only and is never interpreted as calendar time or an evolutionary rate.

For each trait and tree, dynamic programming evaluates all globally minimum-cost Sankoff reconstructions without enumerating or assigning equal probability to them. The output is the exact lower–upper envelope for:

- mean relative lineage depth across the required changes;
- number of terminal changes;
- number of internal changes.

The ML tree and all 1,000 raw UFBoot topologies are evaluated. Because the raw UFBoot trees lack branch lengths, no substitution-length or time value is invented for them.

## Fail-closed interpretation

- A lower bound of one terminal change means every minimum reconstruction on that tree requires at least one terminal event.
- An upper bound does not mean that placement is probable; it means that at least one equally minimal reconstruction permits it.
- Wide envelopes are an event-depth resolution result, not evidence that changes occurred uniformly through time.
- Trait comparisons are restricted to orientation, phyllary posture and stickiness. Three completed histories do not establish a general rule for every capitulum trait.
- No result is matched post hoc to colonization, fragmentation, glacial, niche or fitness events.

## Ecological prediction layer

- orientation nominates rainfall/wetting, thermal and pollinator-presentation mechanisms; BIO15/BIO1 remain a topology-stable but threshold-unresolved public niche lead;
- phyllary posture nominates enemy exclusion, wetness protection and pollinator-access trade-offs;
- stickiness retains competing enemy-benefit, null and pollinator/production-cost models.

These predictions define Chapter 3 observations and experiments. They do not label any reconstructed change adaptive.
