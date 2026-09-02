# JEB V6 reframe outline — differentiation through evolutionary time

Status date: 2026-09-02  
Status: **ACTIVE SCIENTIFIC OUTLINE; ROUND-1 HISTORICAL TRIGGER TESTS VALIDATED; NOT YET A SUBMISSION DRAFT**

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

Chapter 1 and Chapter 2 remain independent until the later dissertation synthesis asks whether differentiation-time and maintenance-time directions are retained, lost, reversed or replaced.

## Central Chapter 2 question

> **How repeatedly and how deeply were capitulum traits differentiated, which changes can actually be bounded in calendar time, and did any historical environmental state, change, instability or range-reorganization regime robustly accompany those bounded events?**

The inferential sequence is:

1. recurrence;
2. relative evolutionary depth;
3. calendar event identifiability;
4. paleogeographic identifiability;
5. historical environmental level / signed change / absolute change / variability;
6. independently measurable range-reorganization context;
7. repeated-trigger status across at least two independently bounded homologous transitions;
8. Chapter 3 mechanism and fitness.

The central conceptual result emerging from public data is an **identifiability gradient**: repeated trait differentiation is much better resolved than repeated historical cause.

## Question 1 — How often and how deeply did capitulum traits differentiate?

This part is independent of any environmental model.

- **Orientation:** ML minimum 6; UFBoot 4–6, median 5; median relative-depth envelope 0.795–0.994; internal-to-terminal histories.
- **Phyllary posture:** exactly 3 minimum changes; median envelope 0.695–1.000; relatively deeper placements remain admissible.
- **Stickiness:** exactly 5 minimum changes; median envelope 0.937–0.954; strongly shallow/terminal-biased.
- **Shared history:** 0/3 discrete trait pairs pass robust shared-transition localization.

Minimum changes are lower bounds. Relative lineage depth is topology-only and is not event age, rate or probability.

### Result-level interpretation

Capitulum modules were repeatedly reassembled, but the temporal architecture differs among traits. This rules out the simplest idea that all components repeatedly shifted together at one characteristic depth without proving complete historical independence.

## Question 2 — Which differentiation events can actually be placed in calendar time?

The primary evidence table is the machine-readable ledger:

- `../../data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv`

Current public-data classes are:

### Calendar + paleolocation + historical environment evaluable

- **Orientation / core-Nipponocirsium stem:** erect/upward → nodding/downward after the erect *C. morii* split and before the Japanese-core/Taiwan-core split.

### Conditional dated transition branch envelopes

- white *C. kawakamii* terminal lineage in Taiwan;
- broader Taiwan topology-union colour envelope;
- white *C. brevicaule* terminal lineage in Arenicola.

These are not exact colour-transition dates because ancestral colour and the position of the change on each terminal branch remain conditional.

### Dated extant contrasts, not reconstructed transitions

- Taiwan and Arenicola phyllary architecture;
- Taiwan and Arenicola floral display/coarse head remodelling.

### Dated range process, trait age unlinked

- *C. dipsacolepis* and *C. lineare* range events cannot be assigned as dates of stickiness transitions.

### Result-level interpretation

A major Chapter 2 result is therefore methodological but biologically important: **calendar time is not equally identifiable for all repeated phenotypic changes**. Published lineage dates cannot be borrowed as trait-event dates.

## Question 3 — What historical environment accompanied the best-bounded orientation event?

The core-Nipponocirsium orientation event has 94 admissible chronology pairs × 4 predeclared paleolocation regions = 376 scenarios.

Historical variables are evaluated without using a present-day trait–environment coefficient as a prior.

### 3A. Signed direction

At the single central 0.79 → 0.74 Ma pair:

- BIO1 decreases in 4/4 regions;
- BIO4 decreases in 4/4;
- BIO15 decreases in 4/4;
- BIO12 increases in 3/4.

However, every variable becomes directionally unresolved across the full chronology × paleolocation envelope.

Validated decision:

`no_tested_climate_direction_survives_full_chronology_paleolocation_envelope`

A visually coherent central chronology therefore cannot be promoted to the historical trigger.

### 3B. Environmental level, absolute change and variability

The extended matched-window analysis evaluates:

- event-window mean level;
- signed endpoint change;
- absolute endpoint change;
- temporal SD;
- same-duration windows within the same paleolocation region.

Formal result:

- robust signed-direction variables = 0;
- consistently extreme level variables = 0;
- consistently extreme absolute-change variables = 0;
- consistently extreme variability variables = 0.

Source:

- `../../data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`

### Tendency-only regime context

A sub-threshold historical-regime pattern remains useful for interpretation but is not a passed trigger test:

- BIO1 regional median level percentiles are ~0.14 across all four regions;
- BIO1 regional median temporal-SD percentiles are ~0.85;
- BIO4 regional median level percentiles are ~0.85;
- at the central 0.79 → 0.74 Ma pair, BIO1 level is near the lower 5% and BIO1 temporal SD near the upper 5% in all four regions.

This points more naturally to a **cold / climatically variable Pleistocene regime context** than to one robust directional temperature change. Chronology uncertainty prevents promotion beyond tendency-level interpretation.

## Question 4 — Was the event associated with unusual sea-level or range-reorganization dynamics?

### Spratt–Lisiecki sensitivity

The empirical stack covers only 16/94 admissible orientation chronologies. The central 50-kyr window is not unusual in sea-level mean, SD, range, endpoint change or 1-kyr change metrics. Because 78/94 chronology pairs are uncovered, the full envelope is `not_evaluable` under this source.

### de Boer full-chronology sensitivity

An independent model-based global reconstruction covers all 94 chronology pairs. Relative to same-duration Pleistocene windows, none of six metrics passes the robust full-chronology gate:

- mean sea level;
- SD;
- range;
- absolute endpoint change;
- mean absolute 1-kyr change;
- maximum absolute 1-kyr change.

Validated decision:

`no_global_sea_level_metric_survives_full_chronology_gate`

Source:

- `../../data/evidence/chapter2_orientation_deboer_sealevel_envelope_v1_summary.json`

Global eustatic sea level is a range-reorganization context variable. It is not a reconstruction of local Ryukyu/Taiwan connectivity and cannot be interpreted as a selective pressure on capitulum orientation.

## Question 5 — Is Mid-Pleistocene timing itself evidence for a trigger?

No. The chronology constraint itself makes Mid-Pleistocene overlap common:

- 56/94 admissible pairs span exactly 0.800 Ma;
- 90/94 overlap 0.700–0.900 Ma;
- 78/94 overlap 0.750–0.850 Ma;
- 71/94 overlap 0.770–0.830 Ma.

Decision:

`mid_pleistocene_overlap_is_chronology_context_not_independent_trigger_evidence`

Published Pleistocene glaciation, isolation and island-fragmentation results remain meaningful **lineage-diversification context**, but that evidence cannot substitute for a trait-specific trigger test.

## Question 6 — Is there a repeated historical trigger?

A repeated differentiation-trigger candidate requires at least two independently bounded homologous trait transitions whose own chronology/paleolocation uncertainty is propagated before comparing environmental direction or regime.

Current orientation status:

`not_evaluable_single_dated_transition_event`

Orientation is recurrent in the relative phylogenetic history, but only one transition is currently dateable at this resolution.

### Other trait gates

- **Flower colour:** two dated white-lineage contexts exist, but transition timing/direction remain conditional and a commensurate historical radiation series is absent.
- **Phyllary posture:** recurrent and relatively deep, but dated sister architecture contrasts are not reconstructed posture transitions.
- **Stickiness:** recurrent and shallow, but range-event ages are not trait-transition ages.

Thus no capitulum module currently supports a defensible repeated historical environmental trigger under public data alone.

## Question 7 — What does this say about capitulum differentiation as a whole?

The strongest synthesis is not “no environmental cause.” It is:

> **Capitulum traits differentiated repeatedly but at unequal evolutionary depths, while the historical causes of those transitions are substantially less identifiable than the transition histories themselves.**

Pleistocene climatic and geographic reorganization is strongly supported as a background for lineage diversification. Yet for the one trait event with adequate calendar and paleolocation bounds, no tested climate direction, climate-level extremeness, change magnitude, temporal variability or global sea-level metric survives the full uncertainty gates.

This creates a biologically useful hierarchy:

1. young Pleistocene radiation context — well supported;
2. recurrent capitulum differentiation — well supported for several modules;
3. trait-specific event timing — limited;
4. event-specific historical trigger — unresolved;
5. repeated trigger across homologous events — currently not evaluable;
6. selection/adaptation — reserved for Chapter 3 mechanism and reproductive fitness.

## Role of current spatial/environment analyses

The environment-free spatial-breadth pilot and 7×4 / 7×9 current trait–environment screens are retained as **internal diagnostics**. They may remain absent from the final Results, figures and abstract.

They do not select historical variables or determine which Chapter 2 result is primary.

## Proposed main figures

### Figure 1 — Repeated differentiation and evolutionary depth

Phylogeny plus minimum-change burden and relative-depth envelopes for orientation, phyllary posture and stickiness.

### Figure 2 — What can actually be dated?

Trait × evidence ledger showing relative-depth only, dated range context, dated sister contrast, conditional transition branch and calendar+paleolocation+environment-evaluable event classes.

### Figure 3 — One bounded orientation event: central narrative versus full uncertainty

For BIO1/BIO4/BIO12/BIO15 show:

- the central 0.79 → 0.74 Ma trajectory;
- the 94 chronology × 4 paleolocation scenario envelope;
- matched-window level/change/variability percentiles;
- the distinction between tendency-only regime context and formal unresolved classification.

### Figure 4 — Range-reorganization context and its limits

Show Spratt–Lisiecki chronology coverage and the independent de Boer 94/94 full-chronology result. Emphasize that no global sea-level metric survives the full chronology gate and that global eustatic sea level is not local connectivity.

The dated Taiwan/Arenicola sister-system colour/head-remodelling cases can be placed in a smaller panel or Supporting Information because they are conditional differentiation contexts rather than exact trait-transition tests.

### Figure 5 — Differentiation identifiability hierarchy

Trait × evidence matrix:

`recurrence → relative depth → calendar event → paleolocation → historical climate/range context → repeated trigger → Chapter 3 causal test`

This is the integrative figure and the main conceptual contribution.

## What is retained from V5

Retain as empirical or audit evidence, but reposition:

- discrete minimum-change and relative-depth results;
- 0/3 shared-history boundary;
- chronology/paleolocation work;
- dated white–coloured sister systems and coarse remodelling;
- provenance, uncertainty and claim-boundary infrastructure.

Present-day environmental associations from V5 are not required headline results.

## Active sources

- `../../data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv`
- `HISTORICAL_DIFFERENTIATION_EVIDENCE_SYNTHESIS_V1.md`
- `HISTORICAL_DIFFERENTIATION_TRIGGER_RESULT_V1.md`
- `../../data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`
- `../../data/evidence/chapter2_orientation_deboer_sealevel_envelope_v1_summary.json`
- `../../data/evidence/chapter2_orientation_mpt_overlap_audit_v1.json`

## Submission gate for V6

The first historical-trigger validation round is complete. Before rebuilding the JEB submission package:

1. keep the new differentiation evidence ledger green under CI;
2. perform one final public audit for any machine-readable dated tree/posterior that could calendar-bound additional orientation transitions;
3. if none is recoverable, freeze repeated-trigger status as `not_evaluable_single_dated_transition_event` rather than deriving dates from figures or relative depth;
4. decide whether conditional colour sister-system contexts remain a main-text panel or Supporting Information;
5. write V6 from the identifiability hierarchy, not by editing V5 paragraph by paragraph;
6. retain the distinction between historical alignment and natural selection/adaptation throughout.

V5 remains a reproducible pre-reframe production snapshot until the V6 manuscript is rebuilt and QA'd.
