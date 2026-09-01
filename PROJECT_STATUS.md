# EAzami current state

Status date: 2026-09-01

## Active status: Chapter 2 public-data synthesis complete; JEB V5 production in progress

Chapter 2 now asks not only how many times capitulum traits changed, but whether similar phenotypes share the same environmental explanation across evolutionary time, lineages and biological scales.

Scientific status: **COMPLETE_PUBLIC_DATA_V3_SYNTHESIS**.  
Submission status: **V5_TEXT_FIGURES_AND_DOCX_BUILD_VALIDATED — FINAL_QA_PENDING**.

The active manuscript is:

`docs/chapter2/MANUSCRIPT_JEB_V5.md`

Active title:

> **Modular evolutionary depth and lineage-dependent environmental correspondence of capitulum traits in a young thistle radiation**

V5 validation passes at 220 abstract words and 4,846 main-text words before references. The five-figure package and the anonymous-manuscript/title-page/SI/cover-letter DOCX package also build successfully in CI.

## Dissertation mainline

```text
Chapter 1 / Azami
public-image phenotypic breadth × present environmental state space
        ↓
Chapter 2 / EAzami
repeated evolutionary depth × timing/range process × environmental trajectories
        ↓
Chapter 3
own ancestry-linked samples × direct exposure × mechanism × reproductive fitness
```

Chapter 1 supplies frozen external present-state predictions for the Chapter 2 space–time tests; Chapter 2 does not re-screen Azami predictors after seeing EAzami outcomes.

## Chapter 2 final answer

> **Capitulum diversity is assembled at unequal evolutionary depths across component traits. Environmental correspondence is lineage- and scale-dependent, and similar extant phenotypes do not guarantee a common historical driver. Public data support partial coordinated remodelling inside a modular historical mosaic, while direct selective mechanism and fitness remain unresolved.**

Final process model:

`modular_hierarchical_selection_mosaic_with_partial_coordinated_remodelling`

This is a testable explanatory model, not demonstrated natural selection.

## Core historical results

### Orientation

- 20 resolved concepts;
- ML minimum changes = 6;
- UFBoot minimum = 4–6;
- bootstrap median relative lineage-depth envelope = 0.795–0.994;
- no individually forced ML edge; JPN36 terminal forced in 0.227 of bootstrap topologies.

### Phyllary posture

- ten resolved concepts;
- exactly 3 minimum changes across ML and all 1,000 UFBoot trees;
- bootstrap median relative-depth envelope = 0.695–1.000;
- JPN36 terminal forced in 0.728.

### Stickiness

- 13 resolved concepts;
- exactly 5 minimum changes across ML and all 1,000 UFBoot trees;
- relative-depth envelope = 0.937–0.954;
- JPN06=0.995, JPN36=0.707, JPN30=0.545 and one nine-tip internal edge=0.681.

Zero of three discrete trait pairs passes the cross-treatment robust shared-transition-localization rule.

Minimum changes are lower bounds. Relative lineage-depth is topology-only and not an event age or evolutionary rate.

## Orientation environmental result

### Present correspondence

Frozen global Azami:

- orientation angle × BIO12: beta=+0.304359, q=0.021.

Frozen East-Asian EAzami primary:

- BIO15 D−U = +1.320 to +1.330 SD;
- BIO1 D−U = −0.975 to −0.967 SD;
- signs retained in 6/6 accepted topologies and 54/54 topology × species-LOO fits.

Independent Taiwan occurrence-source tiers preserve the same directions while the threshold class is source-sensitive.

### Historical origin envelope

Public taxon expansion places the minimum erect→nodding change on the core-Nipponocirsium stem after erect *C. morii* and before the Japanese-core/Taiwan-core split.

The two bounding dates come from separate studies and are not a joint posterior. The deterministic scenario envelope contains:

- 94 admissible age pairs;
- four palaeolocation scenarios;
- 376 region × chronology trajectories;
- state–trajectory cosine q05 = −0.7991, median = −0.0647, q95 = +0.6087;
- matched-window percentile median = 0.4705.

Decision:

`origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty`

Thus current hydric correspondence is better identified than the historical origin environment.

## Flower-colour result

Two publicly dated sister comparisons were remeasured with the frozen Azami image pipeline after trait-neutral public-image selection and cropping.

### Repeated phenotype direction

Arenicola, *C. brevicaule* white vs *C. irumtiense* coloured:

- chroma white−coloured = −2.95;
- lightness = +6.86.

Taiwan, *C. kawakamii* white vs *C. tatakaense* coloured:

- chroma = −6.16;
- lightness = +8.24.

The dated splits (~0.93 and ~0.35 Ma) are lineage-divergence contexts, not colour-transition dates.

### Current RSDS test

Frozen global Azami predicts higher current RSDS → lower visible chroma.

- Arenicola: RSDS white−coloured = +1814; direction concordant;
- Taiwan: RSDS white−coloured = −686.5 and −1703 after 0.05° locality aggregation; direction reversed;
- primary pair-level concordance = 1/2;
- pooled within-taxon secondary beta = −0.4065, two-sided permutation P=0.1141, prespecified negative one-sided P=0.0361.

Decision:

`replicated_white_state_current_RSDS_lineage_scale_dependent_historical_driver_unresolved`

The secondary within-taxon direction does not override the 1/2 pair-level result.

## Partial coordinated remodelling

Both white lineages show the same coarse non-colour directions:

- circularity +0.238 / +0.159;
- solidity +0.092 / +0.099;
- visible floret fraction −0.305 / −0.028.

Fine outline and involucre projection/taper metrics are heterogeneous or low-information. This supports a coarse remodelling hypothesis but not a universal white-flower whole-capitulum syndrome or common developmental mechanism.

The independent present 18-D synthesis retains within-versus-among association-matrix rho=0.3663. Together with the 0/3 shared discrete-history result, the evidence supports partial covariance within otherwise asymmetric histories.

## Final trait × driver classes

1. orientation × hydric exposure — `history_resolved_current_hydric_candidate_origin_driver_unresolved`;
2. flower colour × radiative environment — `replicated_white_state_current_RSDS_lineage_scale_dependent_historical_driver_unresolved`;
3. phyllary posture × enemy/wetting/access — `history_resolved_cause_unidentified`;
4. stickiness × biotic enemy/cost regime — `rapid_history_resolved_biotic_driver_unidentified`;
5. orientation × thermal regime — `directional_mismatch_to_explain`;
6. outline/head packing × multivariate environment — `present_breadth_plus_replicated_coarse_extant_remodelling_history_unresolved`;
7. whole capitulum synthesis — `partial_module_covariation_universal_synchronized_syndrome_not_supported`.

All rows retain `causal_claim_allowed=no`.

## Legacy downstream doctoral routing labels retained for compatibility

The sampling and mechanism programme predates the V5 public-data manuscript and several validators still key on its historical labels. These labels remain valid downstream routing commitments and do not supersede the V5 Chapter 2 story:

- `Chapter 1 — phenotype × present-day space/environment`;
- `Chapter 2 — phenotype × evolutionary time/history`;
- `Chapter 3 — own RAD-seq × linked phenotype/function`;
- `origin discrimination` remains a Chapter 3 objective using `nuclear population genomics`, `plastid haplotype` and `cytotype` on ancestry-linked material;
- `FDT1 trait-to-function evidence` remains a supporting mechanism-prior layer;
- `Cirsium reproductive-herbivory RR = 2.674` remains a supporting interaction prior rather than a Chapter 2 causal result;
- these mechanism and interaction resources are routed to the `Chapter 3 causal layer`.

## Active sources of truth

### Manuscript/package

- `docs/chapter2/MANUSCRIPT_JEB_V5.md`;
- `docs/chapter2/JEB_QUESTION_RESULT_FIGURE_MAP_V5.md`;
- `docs/chapter2/JEB_SUPPORTING_INFORMATION_V3.md`;
- `docs/chapter2/JEB_TITLE_PAGE_TEMPLATE_V2.md`;
- `docs/chapter2/JEB_COVER_LETTER_TEMPLATE_V2.md`;
- `analysis/validate_chapter2_manuscript_v5.py`;
- `analysis/make_chapter2_jeb_figures_v5.py`;
- `analysis/build_chapter2_jeb_docx_v3.py`.

### Final synthesis

- `data/evidence/chapter2_final_integrated_evidence_v3.json`;
- `data/evidence/chapter2_final_integrated_evidence_v3.csv`;
- `docs/chapter2/PUBLIC_DATA_FINAL_CHAPTER2_STORY_AND_ANALYSIS_PLAN_V3.md`.

### Key source layers

- `data/evidence/japan38_relative_event_depth_v1.json`;
- `data/evidence/chapter2_ecological_explanatory_reach_v1.json`;
- `data/evidence/fdt4_taiwan_multisource_orientation_sensitivity_v1.json`;
- `data/evidence/chapter2_orientation_origin_envelope_result_v1.json`;
- `data/evidence/chapter2_four_taxon_azami_measurement_result_v1.json`;
- `data/evidence/chapter2_colour_rsds_focal_concordance_result_v1.json`.

V1–V4 manuscript and figure/package files are frozen audit history, not active submission sources.

## Current production tasks

Completed in CI:

- V5 manuscript evidence/word-count validation;
- five main figures generated in PNG and PDF from frozen evidence;
- anonymous V5 manuscript, separate title page, SI V3 and cover-letter template generated as DOCX and checked for active-title routing and basic anonymity.

Remaining QA:

1. inspect visual legibility and finalize figure legends/alternative text;
2. complete primary-source reference and DOI audit;
3. complete data-availability, author declaration and repository-archive fields;
4. perform final prohibited-claim and anonymous-file metadata review.

No new discovery analysis is authorized merely to improve the submission story. New public data are incorporated only when they address a preregistered identifiability gap.

## Chapter 3 priority tests

- **orientation × hydric exposure:** gravity-referenced orientation manipulation with wetting/pollen/effective-contact/viable-seed chain;
- **Arenicola vs Taiwan colour:** intentionally exploit the same white phenotype under opposite current pair-level RSDS contrast; test shared versus switched pigment/developmental mechanism and selective environment;
- **coarse head packing:** test whether circularity/solidity/floret exposure share development or function with colour;
- **phyllary/stickiness:** directly separate enemy, wetting, access and production/pollinator-cost pathways.

## Claim boundary

Chapter 2 does not establish independent origins, convergence, exact transition ages, ancestral-area probabilities, historical rain or solar causation, pigment/UV mechanism, common developmental programme, natural selection or adaptation. Those upgrades require Chapter 3 ancestry-linked mechanism and reproductive-fitness evidence.
