# EAzami — evolutionary depth and environmental history of capitulum diversity

## Active state — 2026-09-01

EAzami is the evolutionary-history half of the public-data thesis block:

```text
Chapter 1 / Azami
present phenotypic breadth across environmental state space
        ↓
Chapter 2 / EAzami
repeated evolutionary depth + temporal/geographic process + state–trajectory correspondence
        ↓
Chapter 3
own samples: ancestry-linked phenotype → actual exposure → mechanism → reproductive fitness
```

Chapter 2 is now **public-data complete at the current identifiability ceiling**. The active scientific synthesis was frozen in PR #151 and the active JEB text is V5.

## Current scientific answer

> **Capitulum diversity is assembled at unequal evolutionary depths across component traits, and environmental correspondence is both lineage- and scale-dependent. Public data support partial coordinated remodelling inside a modular historical mosaic, not one synchronized capitulum syndrome and not complete trait independence.**

### Discrete evolutionary depth

- orientation: ML minimum 6; UFBoot minimum 4–6; bootstrap median relative-depth envelope 0.795–0.994;
- phyllary posture: exactly 3 changes; relative-depth envelope 0.695–1.000;
- stickiness: exactly 5 changes; shallow relative-depth envelope 0.937–0.954;
- zero of three discrete trait pairs passes the robust shared-transition-localization rule.

Minimum changes are lower bounds. Relative lineage-depth is topology-only, not event age or rate.

### Orientation × environment

Current evidence independently points to a hydric domain:

- Azami global among-taxon orientation × BIO12: beta=+0.304359, q=0.021;
- EAzami downward-minus-upward BIO15: +1.320 to +1.330 SD across six accepted topologies;
- BIO15/BIO1 directions survive 54/54 topology × species leave-one-out fits.

But the historical origin environment is not identified. The public core-Nipponocirsium chronology × paleolocation envelope contains 94 admissible age pairs × 4 regions = 376 scenarios. The Azami-state / historical-trajectory cosine spans q05 −0.799, median −0.065, q95 +0.609, so the origin classification is:

`origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty`.

### Flower colour × radiation

Two publicly dated white–coloured sister systems recover the same extant colour direction with the frozen Azami image-measurement pipeline:

- Arenicola: white-minus-coloured chroma −2.95, lightness +6.86;
- Taiwan: chroma −6.16, lightness +8.24.

Current RSDS does **not** give one repeated pair-level rule:

- Arenicola white-minus-coloured RSDS +1814 → Azami-direction concordant;
- Taiwan −686.5, and −1703 after 0.05° locality aggregation → pair-level reversal;
- primary pair-level concordance = 1/2;
- pooled within-taxon secondary slope beta=−0.4065.

Thus the repeated white phenotype is real enough to compare, but a universal persistent-RSDS explanation is weakened. Historical radiative causation remains non-identifiable.

### Partial coordinated head remodelling

Both white lineages also show the same coarse directions:

- circularity higher;
- solidity higher;
- visible floret fraction lower.

Fine outline/involucre geometry is heterogeneous or low-information. The supported whole-capitulum model is therefore:

`modular_hierarchical_selection_mosaic_with_partial_coordinated_remodelling`

`selection mosaic` is a process hypothesis shorthand, not demonstrated natural selection or adaptation.

## Legacy programme-routing labels retained for audit compatibility

The following labels are historical programme-routing aliases used by downstream validators. They do **not** replace the V5 active scientific story:

- `Chapter 1: present-day space/environment`;
- `Chapter 2: evolutionary time/history`;
- `Chapter 3: own RAD-seq + linked phenotype/function`;
- `Present-state v3/v4 covariance generators` remain Chapter 1/thesis-methods diagnostics rather than the Chapter 2 evolutionary-transition model.

## Active Chapter 2 sources of truth

Start here:

1. `docs/chapter2/MANUSCRIPT_JEB_V5.md` — active JEB manuscript text;
2. `docs/chapter2/JEB_QUESTION_RESULT_FIGURE_MAP_V5.md` — active five-figure contract;
3. `data/evidence/chapter2_final_integrated_evidence_v3.json` — final trait × driver synthesis;
4. `docs/chapter2/PUBLIC_DATA_FINAL_CHAPTER2_STORY_AND_ANALYSIS_PLAN_V3.md` — final public-data story;
5. `data/evidence/chapter2_orientation_origin_envelope_result_v1.json` — audited orientation chronology × paleolocation decision summary;
6. `data/evidence/chapter2_four_taxon_azami_measurement_result_v1.json` — two dated sister-system image result;
7. `data/evidence/chapter2_colour_rsds_focal_concordance_result_v1.json` — focal colour–RSDS result;
8. `data/evidence/japan38_relative_event_depth_v1.json` — discrete-history depth envelopes;
9. `data/evidence/chapter2_ecological_explanatory_reach_v1.json` — frozen East-Asian ecology primary;
10. `data/evidence/fdt4_taiwan_multisource_orientation_sensitivity_v1.json` — occurrence-source sensitivity.

`MANUSCRIPT_JEB_V1.md` through `V4.md` and the V3/V4 production packages remain reproducible audit snapshots. They are not active submission files.

## JEB submission state

Target: **Journal of Evolutionary Biology — Research Article**.

Active title:

> **Modular evolutionary depth and lineage-dependent environmental correspondence of capitulum traits in a young thistle radiation**

V5 manuscript validation passes:

- abstract: 220 words;
- main text before references: 4,846 words;
- final V3 evidence values and prohibited-claim guards: valid;
- active display plan: five figures.

The five-figure generator and the V5 anonymous-manuscript/title-page/SI/cover-letter DOCX builder both execute successfully in CI and upload inspectable artifacts.

Remaining work is production QA, not discovery:

1. audit visual legibility and final figure captions/alternative text;
2. complete primary-source reference and data-availability audits;
3. complete author declarations and final anonymous-file metadata checks.

No new field, RAD-seq, dated-tree, phenotype or fitness result is required to complete the public-data manuscript.

## Claim boundary

Chapter 2 does **not** establish:

- independent origins or adaptive convergence from minimum changes;
- exact trait-transition ages from lineage split dates;
- ancestral-area probabilities from regional palaeolocation scenarios;
- historical rain or solar causation from present climate associations;
- pigment pathway, UV mediation or common developmental mechanism from public images;
- natural selection or adaptation without focal mechanism and reproductive-fitness evidence.

Missing or `not_evaluable` evidence is retained as non-identifiability, not rewritten as biological absence.
