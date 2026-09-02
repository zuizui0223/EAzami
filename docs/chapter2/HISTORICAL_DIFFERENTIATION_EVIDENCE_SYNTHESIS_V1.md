# Chapter 2 historical differentiation evidence synthesis v1

Status date: 2026-09-02  
Status: **ACTIVE SCIENTIFIC SYNTHESIS; public-data claim ceiling**

## Central result

Chapter 2 now separates three questions that were previously too easy to collapse:

1. **Did the trait change repeatedly?**
2. **How deep in the radiation can those changes occur?**
3. **When a change can actually be bounded in calendar time, is its historical environmental context unusual or repeated?**

The current public evidence gives a strong answer to the first two questions for orientation, phyllary posture and stickiness, but a much weaker answer to the third.

The result is therefore not a single environmental-causation story. It is an **identifiability gradient across capitulum modules**.

Machine-readable ledger:

- `../../data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv`

## 1. Repeated differentiation is well supported, but differs in depth

| Module | Minimum-change lower bound | Relative-depth structure |
| --- | ---: | --- |
| Orientation | ML 6; UFBoot 4–6, median 5 | mixed internal-to-terminal; median UFBoot envelope 0.795–0.994 |
| Phyllary posture | exactly 3 | deeper placements remain admissible; 0.695–1.000 |
| Stickiness | exactly 5 | strongly shallow/terminal-biased; 0.937–0.954 |

Zero of three discrete trait pairs passes the robust shared-transition-localization rule.

Thus capitulum differentiation was recurrent, but its temporal architecture differs among modules. This is stronger than merely counting present states, and it does not require a common historical cause.

## 2. Calendar-time identifiability is the limiting step

Only one current trait transition passes the full public-data gate of:

`trait transition -> bounded branch/time -> paleolocation scenarios -> historical environment`

That event is the core-Nipponocirsium erect/upward -> nodding/downward orientation transition.

Other available dates are weaker evidence classes:

- flower colour: conditional dated terminal-lineage envelopes;
- phyllary/display: dated extant sister contrasts, not reconstructed transitions;
- stickiness: dated range processes whose ages are not trait-transition ages.

This distinction is itself a primary Chapter 2 result: **repeated history is much better identified than repeated historical cause.**

## 3. Orientation: no tested directional climate trigger survives uncertainty

The one dateable orientation event is bounded between the *C. morii* split and the Japanese-core/Taiwan-core split. The cross-study node constraints yield 94 admissible chronology pairs, evaluated under four predeclared paleolocation scenarios (376 region × chronology scenarios).

At the single central 0.79 -> 0.74 Ma pair, the historical trajectory looks coherent:

- BIO1 decreases in 4/4 regions;
- BIO4 decreases in 4/4;
- BIO15 decreases in 4/4;
- BIO12 increases in 3/4.

But the apparent direction is not robust. Across the full chronology × paleolocation envelope, BIO1, BIO4, BIO12 and BIO15 are all directionally unresolved.

Formal decision:

`no_tested_climate_direction_survives_full_chronology_paleolocation_envelope`

This prevents a central-age narrative from being promoted to a historical trigger.

## 4. Climate regime, change magnitude and variability are also formally unresolved

The extended V2 analysis evaluates, independently of any present-day coefficient:

- environmental level within the branch window;
- signed endpoint change;
- absolute endpoint change;
- within-window temporal SD;
- same-duration matched windows in the same paleolocation region.

No BIO1/BIO4/BIO12/BIO15 variable passes the full chronology × paleolocation robust gate for level, signed direction, absolute change or temporal variability.

Formal result:

- robust signed-direction variables: 0;
- consistently extreme level variables: 0;
- consistently extreme absolute-change variables: 0;
- consistently extreme variability variables: 0.

### Tendency-only regime context

There is nevertheless a useful diagnostic pattern that must remain below the formal claim threshold:

- BIO1 regional median level percentiles are ~0.14 in all four paleolocation scenarios;
- BIO1 regional median temporal-SD percentiles are ~0.85;
- BIO4 regional median level percentiles are ~0.85;
- for the central 0.79 -> 0.74 Ma pair, BIO1 level is near the lower 5% and BIO1 temporal SD near the upper 5% in all four regions.

This suggests a **cold / climatically variable Pleistocene regime context** may be more plausible than a single directional temperature change as the relevant historical background. It is not a passed trigger test because chronology uncertainty broadens the event window enough that the pattern does not remain extreme across admissible scenarios.

Source summary:

- `../../data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`

## 5. Global sea level does not provide a robust trigger signal

Two independent global sea-level sensitivities now constrain the range-reorganization interpretation.

### Spratt–Lisiecki stack

The empirical stack covers only 16/94 admissible orientation chronologies. The central 0.79 -> 0.74 Ma window is not unusual in sea-level mean, SD, range, endpoint change or 1-kyr change metrics. Because 78/94 chronology pairs are uncovered, full-envelope inference is `not_evaluable` under this source.

### de Boer 5.3-Myr model-based reconstruction

The independent de Boer reconstruction covers all 94 chronology pairs. Relative to same-duration Pleistocene windows, no tested metric is robustly high or low across chronology:

- mean sea level: unresolved;
- SD: unresolved;
- range: unresolved;
- absolute endpoint change: unresolved;
- mean absolute 1-kyr change: unresolved;
- maximum absolute 1-kyr change: unresolved.

Formal decision:

`no_global_sea_level_metric_survives_full_chronology_gate`

The central 50-kyr window has relatively high sea-level SD/range/change-rate percentiles, but this does not survive the full chronology envelope.

Source summary:

- `../../data/evidence/chapter2_orientation_deboer_sealevel_envelope_v1_summary.json`

Global sea level remains a broad range-reorganization context. It is not a reconstruction of local Ryukyu/Taiwan land connectivity and is not a selective pressure on capitulum orientation.

## 6. Mid-Pleistocene overlap is context, not independent evidence

The orientation chronology is centered near ~0.8 Ma, but this overlap is largely built into the chronology constraint:

- 56/94 admissible pairs span exactly 0.800 Ma;
- 90/94 overlap 0.700–0.900 Ma;
- 78/94 overlap 0.750–0.850 Ma;
- 71/94 overlap 0.770–0.830 Ma.

Therefore a statement such as “orientation differentiation occurred around the Mid-Pleistocene Transition” is acceptable temporal context, but the MPT cannot be promoted to a causal trigger from overlap alone.

Machine-readable audit:

- `../../data/evidence/chapter2_orientation_mpt_overlap_audit_v1.json`

## 7. Radiation context and trait trigger must remain separate

Published phylogenomic/biogeographic studies support a young Pleistocene *Cirsium* radiation shaped by dispersal, geographic isolation, glacial oscillations and island fragmentation. That is **lineage-diversification context**.

The trait-specific result is narrower. Current public evidence does not show that the bounded orientation transition occurred during a climate or global sea-level regime that remains exceptional across chronology and paleolocation uncertainty.

The hierarchy is therefore:

`Pleistocene lineage diversification context`

is supported more strongly than

`a particular climate/range process triggered a capitulum-trait transition`.

A stronger lineage-level result cannot be borrowed to fill a missing trait-event result.

## 8. Trait-specific synthesis

### Orientation

**Best resolved historical module.** Recurrent across the phylogeny and spanning internal-to-terminal depths. One stem event is calendar-bounded. Its exact climate/range trigger remains unresolved. Cold/high-variability and high-temperature-seasonality regime tendencies are diagnostic only.

### Phyllary posture

**Recurrent and relatively deep, but not dateable as a transition.** Dated sister architecture contrasts exist, but these cannot be substituted for reconstructed posture changes. Historical driver remains `not_evaluable`.

### Stickiness

**Repeated shallow reassembly.** Existing public dates concern range events rather than sticky/nonsticky transitions. The shallow history is compatible with a local or biotic process, but this remains a hypothesis rather than a historical trigger result.

### Flower colour

**Two dated lineage contexts, but conditional trait history.** White/low-chroma phenotype occurs in Taiwan and Arenicola sister systems, but ancestral colour and the time of the colour change on each terminal branch are not sufficiently resolved. A common historical radiative trigger cannot currently be tested.

### Whole capitulum

Different recurrence counts, different relative-depth structures and 0/3 robust shared-transition localization reject the simplest model of one synchronized historical event or one universal trigger for the entire capitulum. This does not prove complete independence or genetic modularity.

## 9. Current Chapter 2 conclusion

The strongest public-data conclusion is:

> **Capitulum traits differentiated repeatedly but at unequal evolutionary depths. The Pleistocene radiation provides a well-supported backdrop of climatic and geographic reorganization, yet the historical environmental trigger of individual capitulum transitions is substantially less identifiable. For the best-bounded orientation event, neither a directional climate change, an extreme climate regime, unusually large climate variability/change, nor global eustatic sea-level dynamics survives the full chronology and paleolocation uncertainty gates.**

This is not a null evolutionary result. It distinguishes **when lineage diversification context is identifiable from when a trait-specific cause is not**.

## 10. Handoff to the dissertation synthesis and Chapter 3

Chapter 1 can independently identify present-day environmental factors associated with the maintenance or sorting of phenotypic diversity. Chapter 2 identifies how those phenotypes were assembled through time and whether a historical differentiation trigger can be recovered.

Only after both are independently frozen should the dissertation ask whether:

- the same environmental domain is retained from differentiation to maintenance;
- historical and present directions differ;
- a historical trigger disappeared after origin;
- a present maintenance factor arose later;
- driver switching or lineage-specific selection mosaics are plausible.

Chapter 3 then tests the candidate environment -> trait function -> reproductive fitness path. Historical alignment alone never establishes natural selection or adaptation.
