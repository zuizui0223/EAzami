# EAzami current state

Status date: 2026-09-02

## Active status

Scientific status: **CHAPTER2_DIFFERENTIATION_TRIGGER_ROUND1_VALIDATED**  
Submission status: **V5_QA_COMPLETE_BUT_PRE_REFRAME — V6_REBUILD_REQUIRED**

Chapter 2 is now the **historical differentiation** chapter.

```text
Chapter 1
present environmental gradients after spatial control
→ maintenance / current ecological sorting candidates

Chapter 2
repeated trait differentiation + evolutionary depth
+ historical environmental context at bounded events
→ origin / differentiation-trigger candidates

Chapter 3
candidate environment → trait function → reproductive fitness
→ adaptive explanation only after causal validation
```

Chapter 1 and Chapter 2 remain analytically independent until the later dissertation-synthesis step.

## Active sources of truth

- `data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv`
- `docs/chapter2/HISTORICAL_DIFFERENTIATION_EVIDENCE_SYNTHESIS_V1.md`
- `data/evidence/chapter2_differentiation_time_axis_contract_v1.json`
- `data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`
- `data/evidence/chapter2_orientation_deboer_sealevel_envelope_v1_summary.json`
- `data/evidence/chapter2_orientation_mpt_overlap_audit_v1.json`
- `docs/chapter2/MANUSCRIPT_JEB_V6_REFRAME_OUTLINE.md`

## Frozen recurrence and relative depth

### Orientation

- 20 resolved concepts;
- ML minimum changes = 6;
- UFBoot minimum = 4–6, median 5;
- median relative-depth envelope = 0.795–0.994;
- mixed internal-to-terminal history.

### Phyllary posture

- 10 resolved concepts;
- exactly 3 changes across ML and all 1,000 UFBoot trees;
- median relative-depth envelope = 0.695–1.000;
- relatively deep placements remain admissible.

### Stickiness

- 13 resolved concepts;
- exactly 5 changes across ML and all 1,000 UFBoot trees;
- median relative-depth envelope = 0.937–0.954;
- strongly shallow/terminal-biased.

Zero of three discrete trait pairs passes robust shared-transition localization.

Minimum changes are lower bounds. Relative lineage depth is topology-only, not calendar age or evolutionary rate.

## Event-time identifiability

Public evidence currently contains:

- **1** calendar + paleolocation + historical-environment evaluable trait transition: core-Nipponocirsium orientation;
- **3** conditional flower-colour terminal branch envelopes;
- **4** dated sister phenotype contrasts that are not reconstructed trait transitions;
- **2** dated range processes whose dates are not stickiness-transition dates.

The main identifiability result is that **repeated trait history is much better resolved than repeated historical cause**.

## Orientation historical differentiation — first full validation round

The core-Nipponocirsium erect/upward → nodding/downward event is evaluated over:

- 94 admissible chronology pairs;
- 4 predeclared paleolocation regions;
- 376 region × chronology scenarios.

### Signed climate direction

The central 0.79→0.74 Ma pair appears coherent, but no BIO1/BIO4/BIO12/BIO15 direction survives the full chronology × paleolocation envelope.

Decision:

`no_tested_climate_direction_survives_full_chronology_paleolocation_envelope`

### Climate level, change magnitude and variability

The V2 matched-window analysis finds no variable passing the robust gate for:

- environmental level;
- signed change;
- absolute endpoint change;
- temporal variability.

Tendency only:

- BIO1 is generally low-side in level and high-side in variability;
- BIO4 is generally high-side in level;
- the central pair is near the lower 5% for BIO1 level and upper 5% for BIO1 temporal SD in all four regions.

These tendencies do not survive full chronology uncertainty and are not promoted to trigger evidence.

### Global sea-level / range-reorganization context

Spratt–Lisiecki covers only 16/94 admissible chronologies, so full-envelope inference is coverage-limited.

The independent model-based de Boer 5.3-Myr series covers 94/94. No tested global sea-level metric survives the full chronology gate:

- mean sea level;
- SD;
- range;
- absolute endpoint change;
- mean 1-kyr absolute change;
- maximum 1-kyr absolute change.

Decision:

`no_global_sea_level_metric_survives_full_chronology_gate`

Global eustatic sea level is range-reorganization context only; it is not local island connectivity or a selective pressure on orientation.

### Mid-Pleistocene context

90/94 admissible orientation chronologies overlap 0.7–0.9 Ma. Therefore MPT overlap is largely a chronology consequence, not an independent trigger test.

Decision:

`mid_pleistocene_overlap_is_chronology_context_not_independent_trigger_evidence`

### Repeated trigger

`not_evaluable_single_dated_transition_event`

Orientation is recurrent in the phylogeny, but only one orientation transition is currently dateable at this resolution.

## Other modules

### Phyllary posture

Recurrent and relatively deep, but current dated sister architecture contrasts are not transition ages. Historical trigger remains `not_evaluable`.

### Stickiness

Repeated and shallow, but published dates concern range processes rather than sticky/nonsticky transition branches. Historical trigger remains `not_evaluable_trait_age_unlinked`.

### Flower colour

Two dated white-lineage contexts exist, but ancestral colour and exact transition timing remain conditional and no commensurate historical radiation series exists. Repeated historical colour trigger remains `not_evaluable`.

### Whole capitulum

Unequal recurrence/depth plus 0/3 robust shared-transition localization does not support one synchronized historical event or one universal trigger for the entire capitulum. This is not proof of complete independence.

## Current scientific conclusion

> **Capitulum traits differentiated repeatedly but at unequal evolutionary depths. Pleistocene climatic and geographic reorganization is a strong lineage-diversification context, whereas trait-specific historical causes are much less identifiable. For the best-bounded orientation event, no tested directional climate change, extreme climate state, unusually large climate change/variability, or global eustatic sea-level metric survives the full uncertainty gates.**

This is the current public-data ceiling, not evidence that historical environmental effects were absent.

## Next analytical priority

1. freeze and validate the new historical-differentiation evidence ledger;
2. determine whether any additional orientation transition can be calendar-bounded from newly recoverable public dated-tree assets;
3. keep colour as conditional lineage-differentiation context unless ancestral colour and historical radiation become identifiable;
4. keep phyllary/stickiness historical trigger `not_evaluable` until actual transition-bearing chronology exists;
5. rebuild V6 manuscript/figures around the identifiability hierarchy rather than an environment-first story.

## V5 production snapshot

`docs/chapter2/MANUSCRIPT_JEB_V5.md` remains a fully QA'd pre-reframe snapshot. Its document QA is retained, but it is not the active submission text.

Working V6 title direction:

> **Evolutionary depth and historical environmental context of capitulum differentiation in a young East-Asian thistle radiation**

## Claim boundary

Chapter 2 does not establish adaptation, natural selection, convergence, independent origins, exact transition ages, ancestral-area probabilities, local land bridges or a common environmental trigger. Historical alignment is observational. Mechanism and reproductive fitness belong to Chapter 3.

## Legacy downstream doctoral routing labels retained for compatibility

These exact phrases are historical routing aliases and are not the active Chapter 2 framing:

- `Chapter 1 — phenotype × present-day space/environment`;
- `Chapter 2 — phenotype × evolutionary time/history`;
- `Chapter 3 — own RAD-seq × linked phenotype/function`;
- `origin discrimination`;
- `nuclear population genomics`;
- `plastid haplotype`;
- `cytotype`;
- `FDT1 trait-to-function evidence`;
- `Cirsium reproductive-herbivory RR = 2.674`;
- `Chapter 3 causal layer`.

## Legacy JEB V3/V4 audit aliases retained for validator compatibility

- `HOLD_JEB_PACKAGE_REBUILD_ONLY`;
- `Active standalone title`;
- `v4 is current submission text`;
- `CHAPTER2_CORE_RESULT_RECOVERY_V1.md`.

These labels preserve historical audit routing only.
