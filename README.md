# EAzami — spatial breadth and evolutionary depth of capitulum diversity

## Active state — 2026-09-01

Chapter 2 is being rebuilt around two independent axes:

```text
SPACE
present geographic breadth / spatial structure of capitulum traits

TIME
evolutionary depth / recurrence / branch distribution of trait change
```

The active scientific frame is **not** an environment-first or cross-project comparison design.

Trait × environment analyses remain reproducible internal diagnostics, but they do not define the spatial axis, do not select the manuscript traits, and may remain absent from the final Results.

## Active question

> **How broadly is capitulum diversity distributed across present geographic space, how deeply and repeatedly was that diversity assembled through evolutionary time, and how do those two dimensions differ among capitulum modules?**

## Current two-axis evidence

### SPACE — environment-free pilot

The first spatial-breadth pilot uses the same authority-backed discrete trait ontologies as the frozen temporal-depth analysis, with source-name-guarded GBIF geography and no environmental predictors.

- workflow `33480007180`;
- artifact `9789577849`;
- orientation: 17 singleton-state taxa; U and D states each span roughly 1000 km or more at the taxon-centroid scale; no supported state segregation (P=0.370);
- stickiness: 12 singleton-state taxa; sticky and nonsticky states each span roughly 800–1000 km; weak unsupported segregation tendency (P=0.131);
- phyllary posture: only four singleton-state taxa with usable spatial support, so the primary spatial inference remains coverage-limited.

These are internal feasibility results and need not appear in the final manuscript.

### TIME — frozen discrete histories

- orientation: ML minimum 6; UFBoot minimum 4–6; median relative-depth envelope 0.795–0.994;
- phyllary posture: exactly 3 changes; median relative-depth envelope 0.695–1.000;
- stickiness: exactly 5 changes; shallow median relative-depth envelope 0.937–0.954;
- zero of three discrete trait pairs passes the robust shared-transition-localization rule.

Minimum changes are lower bounds. Relative lineage-depth is topology-only, not event age or rate.

### SPACE × TIME feasibility

The joined pilot (`workflow 33480348070`) shows that the two dimensions are empirically separable:

- orientation and stickiness are both geographically broad under the current taxon-level state geography;
- their temporal-depth structures differ, with orientation permitting a broader deep–shallow history and stickiness concentrated toward shallower lineage depth;
- phyllary retains strong temporal information but insufficient singleton-state spatial coverage for a balanced space-axis interpretation.

No cross-trait regression is fitted with only three modules and no composite breadth-depth score is constructed.

## Active Chapter 2 sources of truth

Start here:

1. `data/evidence/chapter2_space_breadth_time_depth_contract_v1.json` — active two-axis scientific contract;
2. `docs/chapter2/MANUSCRIPT_JEB_V6_REFRAME_OUTLINE.md` — active V6 manuscript architecture;
3. `docs/chapter2/SPACE_BREADTH_TIME_DEPTH_PILOT_RESULT_V1.md` — environment-free two-axis feasibility result;
4. `data/evidence/japan38_relative_event_depth_v1.json` — frozen temporal-depth result;
5. `data/evidence/japan38_nmns_capitulum_trait_seed_v1.csv` plus extension v2 — authority-backed state layer.

Internal exploratory diagnostics retained but not required for the manuscript:

- `data/evidence/chapter2_exploratory_trait_environment_atlas_contract_v1.json`;
- `data/evidence/chapter2_common9_environment_source_contract_v1.json`;
- 7×4 and 7×9 trait × environment screens;
- all-row topology sensitivity for those screens.

## V5 status

`docs/chapter2/MANUSCRIPT_JEB_V5.md` and its production package remain a reproducible **pre-reframe audit snapshot**. Their document-production QA remains valid, but V5 is no longer the active scientific framing and should not be submitted without the V6 rebuild.

The current working title direction is:

> **Spatial breadth and evolutionary depth of capitulum diversity in an East-Asian thistle radiation**

## Historical process layer

Historical environment/range analyses are now supporting case studies only when independently identifiable. The existing orientation chronology × palaeolocation envelope and dated sister-system phenotype contexts remain usable evidence, but neither defines the chapter's primary axes.

## Claim boundary

Chapter 2 does not establish adaptation, natural selection, independent origins, adaptive convergence, exact transition ages, historical range from current occurrences, or common environmental cause from repeated states. Missing or ambiguous evidence remains `not_evaluable`.

## Legacy programme-routing labels retained for audit compatibility

These exact labels are historical aliases used by downstream validators and are not the active scientific frame:

- `Chapter 1: present-day space/environment`;
- `Chapter 2: evolutionary time/history`;
- `Chapter 3: own RAD-seq + linked phenotype/function`;
- `Present-state v3/v4 covariance generators`;
- `COMPLETE_EXISTING_PUBLIC_HISTORY_CORE`;
- `Capitulum configuration diversity, minimum change counts`;
- `MANUSCRIPT_JEB_V3.md`.

## Frozen legacy submission package

The former package remains reproducible **audit snapshots** / audit history. Historical entry points include `docs/chapter2/MANUSCRIPT_JEB_V4.md`, `docs/chapter2/CHAPTER2_CORE_RESULT_RECOVERY_V1.md`, and `MANUSCRIPT_JEB_V3.md`.

Two frozen negative reconstruction-aware diagnostics remain part of the audit trail:

- P=0.3504;
- P=0.1959.
