# Cirsium colour-history handoff from `chun` — 2026-08-27

## Decision

The *Cirsium* colour-history question now belongs entirely to EAzami. `chun` intentionally removed its remaining *Cirsium* documents and validator in commit `b1c1bd1d80c892ff8983bb15de87981cf71c26b6` after narrowing that repository to *Camellia*. The last pre-cleanup state is retained in parent commit `2f56b9fa77ea4988660e574925235224b954ef44`.

EAzami does **not** import the old mixed-family project wholesale. It preserves only the *Cirsium*-specific claim logic that remains necessary for the doctoral mainline.

The machine-readable canonical gate is:

`data/evidence/cirsium_colour_history_claim_gate_v1.json`

## What was retained

### 1. Separate history words by evidence level

- **Retention**: colour is ancestrally continuous through the relevant branch interval.
- **Recruitment/gain**: colour appears after a reconstructed white ancestor, without proof that floral pigment activity existed earlier.
- **Reactivation/re-expression**: requires both an active → suppressed/absent → active floral history and evidence that the underlying pigment machinery remained available through the suppressed interval.
- **Ancestral polymorphism + sorting**: a distinct alternative, not a nuisance category to be forced into gain/loss.

A coloured descendant is therefore never sufficient to call reactivation.

### 2. Keep the Ryukyu alternatives open

For the *C. brevicaule*–*C. irumtiense* contrast, four competing histories remain live:

1. coloured ancestor → white suppression/loss in *C. brevicaule*;
2. white ancestor → coloured recruitment in *C. irumtiense*;
3. ancestral colour polymorphism → differential sorting/fixation;
4. earlier coloured state → intervening white suppression → later reactivation.

The fourth is licensed only after the historical and molecular gates agree.

### 3. Polymorphism is an analysis unit

Within-lineage colour polymorphism, especially var. *takaoense*, must not be collapsed automatically to a taxon-level majority state. Sample/population-level mapping is required when the historical question depends on that polymorphism.

### 4. Molecular reuse is hierarchical

EAzami already establishes substantial upstream/core flavonoid context in `docs/CIRSIUM_MOLECULAR_TO_MACRO_BRIDGE_2026-08-15.md`. The unresolved mechanism is concentrated more strongly at terminal anthocyanin, MBW regulatory, transport/sequestration and cis-regulatory layers than at the question of whether *Cirsium* possesses a flavonoid pathway at all.

For a reactivation claim, the intended chain remains:

`ancestry/transition history -> coding/regulatory retention -> floral RNA -> pigment chemistry -> calibrated colour`

Presence of DFR/ANS alone is not historical proof.

## Current analysis position after PR #101

The multi-trait history and colour analyses now separate three levels that must not be mixed.

### A. Repeated capitulum-state history: already informative

Japan38 has recovered repeated states for orientation, phyllary and stickiness, and the simple whole-capitulum common-lability model is not supported by the current pairwise comparisons. This keeps modular evolution as a live hypothesis while falling short of proving modular evolvability.

### B. Continuous colour: exploratory pattern recovered, local history still blocked

Global exact-concept lightness shows an anti-phylogenetic/overdispersed pattern in the better-covered subsets, but population-matched Japan-local colour coverage remains below the historical gate. The current clean Japan window cannot be replaced by global species medians.

The immediate blockers remain the JPN38 reusable live-image gap and the JPN29 voucher-identity gap, or an equivalent fifth independent identity-resolved Japan-local concept.

### C. Present-day abiotic mechanism screens: currently negative

PR #101 added an independent WorldClim 2.1 public-data sensitivity using solar radiation, wind, a mean-temperature VPD proxy and their standardized three-axis exposure distance. The prespecified gate failed. VPD was descriptively positive but did not pass exact/robustness rules, so no WorldClim axis is promoted to a mechanism lead.

This closes another global species-proxy shortcut. It does not reject abiotic adaptation generally; it means the next useful test should be population-matched history plus local mechanistic exposure rather than another broad present-day global climate screen.

## Next execution sequence

1. Resolve a fifth Japan-local identity-resolved colour concept through JPN38, JPN29, or an equivalent independent population-matched source.
2. Rerun population-matched continuous-colour history without deriving a discrete W/C ontology from arbitrary L* thresholds.
3. Build the East Asian sample-level W/C/polymorphism matrix and map transition direction across accepted nuclear and plausible reticulation-sensitive histories.
4. Once at least two independent W/C transitions are resolved, compare pathway-locus genealogy and retained coding/regulatory capacity, followed by floral expression and pigment chemistry.
5. Only then promote `retention`, `recruitment`, `parallel transition`, or `reactivation` at the level actually supported by the evidence.

This keeps the doctoral mainline aligned with the broader design: global pattern discovery → mechanism priors from literature/meta-analysis → East Asian repeated multi-trait history → focal causal and molecular validation.
