# JEB V6 reframe outline — differentiation through evolutionary time

Status date: 2026-09-03  
Status: **PUBLIC-DATA SCIENCE FROZEN; NEXT STEP IS FULL V6 MANUSCRIPT REBUILD**

The merged V5 manuscript remains a reproducible production snapshot, but its environment-first framing is superseded. Chapter 2 is now a historical-differentiation paper.

## Working title direction

> **Evolutionary depth and historical environmental context of capitulum differentiation in a young East-Asian thistle radiation**

## Dissertation logic

The important distinction is **maintenance versus differentiation**, not simply space versus time.

```text
Chapter 1
present phenotype ~ present environmental gradient after spatial control
→ maintenance / current ecological sorting candidates

Chapter 2
repeated trait differentiation through evolutionary time
+ historical environment/range context at bounded differentiation events
→ origin / differentiation-trigger candidates

Chapter 3
candidate environment → trait function → reproductive fitness
→ adaptive explanation only if the causal path is supported
```

Chapter 1 and Chapter 2 remain independent until the later dissertation synthesis asks whether differentiation-time and maintenance-time environmental domains are retained, lost, reversed or replaced.

## Central Chapter 2 question

> **How repeatedly and how deeply were capitulum traits differentiated, which changes can actually be bounded in calendar time, and does any historical environmental or range-reorganization regime recur robustly across those differentiation windows?**

The inferential sequence is:

1. recurrence;
2. relative evolutionary depth;
3. calendar event identifiability;
4. paleogeographic identifiability;
5. historical environmental level / signed change / absolute change / variability;
6. independently measurable range-reorganization context;
7. recurrence of a historical trigger only when the relevant differentiation events are independently bounded;
8. Chapter 3 mechanism and fitness.

Final current public-data classification:

`repeated_differentiation_resolved_but_recurring_tested_environmental_trigger_not_identified_under_public_data`

## Question 1 — How often and how deeply did capitulum traits differentiate?

This part is independent of any environmental model.

- **Orientation:** ML minimum 6; UFBoot 4–6, median 5; median relative-depth envelope 0.795–0.994; internal-to-terminal histories.
- **Phyllary posture:** exactly 3 minimum changes; median envelope 0.695–1.000; relatively deeper placements remain admissible.
- **Stickiness:** exactly 5 minimum changes; median envelope 0.937–0.954; strongly shallow/terminal-biased.
- **Shared history:** 0/3 discrete trait pairs pass robust shared-transition localization.

Result-level interpretation:

> Capitulum modules were repeatedly reassembled, but their temporal architectures differ. The simplest synchronized whole-capitulum history is not supported.

Minimum changes remain lower bounds. Relative lineage depth is topology-only and is not event age, rate or probability.

## Question 2 — Which differentiation events can actually be placed in calendar time?

The evidence ledger separates:

### Calendar + paleolocation + historical environment evaluable

- **Orientation / core-Nipponocirsium stem:** erect/upward → nodding/downward after the erect *C. morii* split and before the Japanese-core/Taiwan-core split.

### Conditional dated transition branch envelopes

- white *C. kawakamii* terminal lineage in Taiwan;
- broader Taiwan topology-union colour envelope;
- white *C. brevicaule* terminal lineage in Arenicola.

### Dated extant contrasts, not reconstructed transitions

- Taiwan and Arenicola phyllary architecture;
- Taiwan and Arenicola floral display/coarse head remodelling.

### Dated range process, trait age unlinked

- *C. dipsacolepis* and *C. lineare* range events cannot be assigned as dates of stickiness transitions.

A renewed public audit found no machine-readable dated Newick/posterior that can calendarize additional Japan38 trait-changing branches.

Result-level interpretation:

> **Repeated trait history is much better identified than repeated historical cause.** Published lineage dates cannot be borrowed as trait-event dates.

## Question 3 — What historical environment accompanied the best-bounded orientation event?

The core-Nipponocirsium orientation event has 94 admissible chronology pairs × 4 predeclared paleolocation regions = 376 scenarios. Historical variables are evaluated without using a present-day trait–environment result as a prior.

### Signed direction

At the central 0.79 → 0.74 Ma pair, BIO1/BIO4/BIO15 decrease in all four regions and BIO12 increases in three of four.

Across the full uncertainty envelope:

`no_tested_climate_direction_survives_full_chronology_paleolocation_envelope`

### Environmental level, absolute change and variability

Formal result:

- robust signed-direction variables = 0;
- consistently extreme level variables = 0;
- consistently extreme absolute-change variables = 0;
- consistently extreme variability variables = 0.

BIO1 low-level/high-variability and BIO4 high-level tendencies remain descriptive only because they do not survive all chronology/paleolocation gates.

Source:

- `../../data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`

## Question 4 — Does global sea level identify an orientation range-reorganization trigger?

No robust full-envelope result is recovered.

- Spratt–Lisiecki covers only 16/94 admissible chronologies and is `not_evaluable` for the full envelope.
- The independent de Boer reconstruction covers 94/94 chronologies, but mean sea level, SD, range, endpoint change and 1-kyr change metrics all remain unresolved across chronology.

Decision:

`no_global_sea_level_metric_survives_full_chronology_gate`

Global eustatic sea level is a range-reorganization context variable. It is not local Taiwan/Ryukyu/Japan connectivity and is not a selective pressure on capitulum orientation.

## Question 5 — Is there a recurring climate regime across representative lineage differentiations?

A separate internal lineage-level test broadens beyond the one calendar-bounded trait transition without pretending that lineage-divergence dates are capitulum-transition ages.

Design:

- 17 BIOCLIM variables;
- 6 dated lineage contexts;
- representative Nipponocirsium, Arenicola and Sinocirsium groups;
- 15,472 tested scenario × variable combinations;
- univariate level, absolute change and local variability;
- multivariate climate state, displacement and variability;
- age, paleolocation and matched-background uncertainty.

Formal result:

- robust event-level classes = **0/324**;
- recurring climate-context candidates = **0**.

Decision:

`no_recurring_lineage_differentiation_context_survives_age_region_background_gates`

Nipponocirsium and Sinocirsium show sub-threshold cool/high-temperature-variability tendencies, whereas Arenicola is nearer background conditions. That heterogeneity argues against one universal climatic differentiation regime.

Source:

- `../../data/evidence/chapter2_lineage_differentiation_environment_atlas_v1_summary.json`

## Question 6 — Is global sea-level context recurrent across representative lineage differentiations?

A parallel de Boer diagnostic uses three representative clade contexts and seven sea-level metrics per group.

Formal result:

- event-metric classes = 21;
- robust event-metric classes = **0/21**;
- recurring global sea-level candidates = **0**.

Decision:

`no_recurring_global_sea_level_context_survives_age_background_window_gates`

Source:

- `../../data/evidence/chapter2_lineage_differentiation_sealevel_v1.json`

This constrains a universal global-eustatic differentiation context but does not test local strait opening, island area, habitat continuity or other fine-scale palaeogeography.

## Question 7 — Is Mid-Pleistocene timing itself evidence for a trigger?

No. The orientation chronology constraint itself makes Mid-Pleistocene overlap common:

- 56/94 admissible pairs span exactly 0.800 Ma;
- 90/94 overlap 0.700–0.900 Ma;
- 78/94 overlap 0.750–0.850 Ma;
- 71/94 overlap 0.770–0.830 Ma.

Classification:

`broad_mpt_overlap_high_but_not_event_discriminating`

Pleistocene climatic/geographic reorganization remains a meaningful broad radiation context, not an independent trait-trigger result.

## Question 8 — Is there a repeated historical trigger for capitulum differentiation?

For a **trait-specific** repeated trigger, at least two homologous transitions must be independently bounded before their historical environments are compared. No current capitulum module reaches that gate.

Orientation:

`not_evaluable_single_dated_transition_event`

Other modules:

- **Flower colour:** dated conditional white-lineage contexts, but transition timing/direction and historical radiative driver remain unresolved.
- **Phyllary posture:** recurrent/deep but no transition-bearing calendar chronology.
- **Stickiness:** recurrent/shallow but dated range events are not trait-transition ages.

At the broader **lineage-differentiation context** level, both the 17-BIOCLIM and global sea-level analyses return zero recurring robust candidates.

The public-data conclusion is therefore not “no environmental cause.” It is:

> **Repeated differentiation is well resolved, but one recurring tested historical trigger is not identified. The remaining explanation space includes heterogeneous lineage-specific drivers, local palaeogeographic processes, biotic interactions and other environmental dimensions that current public event chronologies do not identify at the necessary scale.**

## Proposed Results order

1. **Repeated differentiation occurs at unequal evolutionary depths.**
2. **Calendar-time identifiability is much weaker than recurrence/depth identifiability.**
3. **The best-bounded orientation event has no robust tested climate or global-sea-level trigger after full uncertainty propagation.**
4. **Broader lineage-differentiation windows likewise lack one recurring 17-BIOCLIM or global sea-level regime.**
5. **The whole-capitulum history is heterogeneous: shared dynamic Pleistocene backdrop, unequal trait histories, unresolved/heterogeneous event-specific causes.**

## Proposed main figures

### Figure 1 — Repeated differentiation and evolutionary depth

Phylogeny plus minimum-change burden and relative-depth envelopes for orientation, phyllary posture and stickiness.

### Figure 2 — What can actually be dated?

Trait × evidence matrix showing relative-depth only, dated range context, dated sister contrast, conditional transition branch and calendar+paleolocation+environment-evaluable classes.

### Figure 3 — One bounded orientation event: central narrative versus full uncertainty

Show the central 0.79 → 0.74 Ma trajectory alongside the 94 × 4 scenario envelopes and matched-background climate metrics. The visual purpose is to show why central-date storytelling is insufficient.

### Figure 4 — Do broader historical regimes recur?

Two panels:

- 17-BIOCLIM × representative lineage differentiations: 0/324 robust event-level classes, 0 recurring candidates;
- global sea level × three clades: 0/21 robust classes, 0 recurring candidates.

Include a clear boundary that these are lineage-context diagnostics, not trait-transition tests or local-connectivity reconstructions.

### Figure 5 — Differentiation identifiability hierarchy

`recurrence → relative depth → calendar event → paleolocation → historical context → repeated trigger → Chapter 3 causal test`

This is the integrative conceptual figure.

## Role of current spatial/environment analyses

The environment-free spatial-breadth pilot and present 7×4 / 7×9 trait–environment screens are retained as internal diagnostics. They may remain absent from the final Results, figures and abstract. They do not select historical variables or determine which Chapter 2 result is primary.

## Canonical frozen science

- `../../data/evidence/chapter2_historical_differentiation_final_summary_v1.json`
- `../../data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv`
- `HISTORICAL_DIFFERENTIATION_EVIDENCE_SYNTHESIS_V1.md`
- `../../data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`
- `../../data/evidence/chapter2_lineage_differentiation_environment_atlas_v1_summary.json`
- `../../data/evidence/chapter2_lineage_differentiation_sealevel_v1.json`
- `../../data/evidence/chapter2_public_dated_tree_recovery_audit_v2.json`

## Submission gate for V6

The public-data differentiation programme is now at its current identifiability ceiling. Do **not** expand the chapter with opportunistic additional environmental screens.

Next:

1. validate the frozen final synthesis under CI;
2. rebuild `MANUSCRIPT_JEB_V6.md` from this outline rather than editing V5 paragraph-by-paragraph;
3. rebuild figures around the five-panel logic above;
4. retain `not_evaluable` distinctions and the local-fragmentation/global-sea-level boundary;
5. QA the anonymous submission package after the V6 manuscript stabilizes.

V5 remains a reproducible pre-reframe production snapshot until V6 is rebuilt and QA'd.
