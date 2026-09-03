# Supporting Information for Chapter 2 JEB V6

## Article

**Repeated capitulum differentiation at unequal evolutionary depths without a recurring coarse historical trigger in a young thistle radiation**

Status: **ACTIVE V6 SUPPORTING INFORMATION**

This Supporting Information preserves the historical-differentiation evidence hierarchy, admission decisions, negative and unresolved results, full claim boundaries and the distinction between trait-transition tests and broader lineage-differentiation context.

## Figure S1 — Harmonized Japan38 nuclear scaffold and admission boundaries

Use the accepted Comp1061-compatible phylogram. Branch lengths are substitutions per site and must not be labelled absolute time.

Admission notes:
- 39 ingroup biological samples represent 38 paper concepts;
- JPN20 retains two biological tips and is not forcibly collapsed;
- JPN31 remains excluded from primary trait history because the phenotype-tip identity conflict is unresolved;
- the scaffold is the harmonized common-locus reference, not the only East-Asian nuclear evidence.

## Table S1 — Discrete trait history summary

| Trait | Resolved concepts | ML / UFBoot minimum | Median UFBoot relative-depth envelope | Historical reading |
|---|---:|---|---|---|
| orientation | 20 | 6 / 4–6 | 0.795–0.994 | recurrent; internal-to-terminal placements admissible |
| phyllary posture | 10 | 3 / 3–3 | 0.695–1.000 | recurrent; deeper placements remain admissible |
| stickiness | 13 | 5 / 5–5 | 0.937–0.954 | recurrent; strongly shallow/terminal-biased |

Minimum counts are lower bounds. Relative lineage depth is topology only and is not event age or rate.

## Table S2 — Shared-transition-localization boundary

| Pair | Branch-aware rho | Equal-branch median | Equal-branch q05 | Robust rule |
|---|---:|---:|---:|---|
| orientation–phyllary | 0.362 | −0.059 | −0.206 | fail |
| orientation–stickiness | 0.202 | −0.387 | −0.392 | fail |
| phyllary–stickiness | 0.084 | 0.184 | −0.073 | fail |

Decision: **0/3** trait pairs pass the robust shared-transition-localization rule.

This rejects a simple synchronized-history model under current coverage. It does not prove genetic, developmental or functional independence.

## Figure S2 — Calendar identifiability funnel

Show the event-history gate:

`trait history → change-bearing branch → calendar chronology → palaeolocation → historical environment`.

Current counts:
- transitions reaching full calendar+palaeolocation+environment gate: **1**;
- conditional colour branch envelopes: **3**;
- dated sister contrasts not reconstructed transitions: **4**;
- dated range processes not linked to trait-transition age: **2**;
- additional machine-readable dated tree recovered for Japan38 change-bearing branches: **no**.

The one full-gate event is the core-Nipponocirsium erect/upward → nodding/downward orientation transition.

## Table S3 — Orientation chronology contract

| Quantity | Value |
|---|---|
| parent central age | 0.79 Ma |
| parent marginal interval | 0.43–1.18 Ma |
| child central age | 0.74 Ma |
| child interval | 0.60–0.87 Ma |
| admissible chronology pairs | 94 |
| event-window duration range | 10–580 kyr |
| palaeolocation scenarios | Taiwan; Ryukyu corridor; southern Japan; broad East-Asian core corridor |
| region × chronology scenarios | 376 |

The two node constraints come from separate public analyses. The 94 pairs are deterministic uncertainty scenarios, not a joint posterior.

## Table S4 — Orientation historical-climate robust-gate result

Variables: BIO1, BIO4, BIO12, BIO15.

| Estimand | Variables passing robust full chronology × palaeolocation gate |
|---|---:|
| signed endpoint direction | 0 |
| extreme mean environmental level | 0 |
| extreme absolute endpoint change | 0 |
| extreme within-window temporal variability | 0 |

Formal decision: `no_tested_climate_direction_survives_full_chronology_paleolocation_envelope` plus no robust level/change/variability rescue.

### Central-pair tendency retained for transparency

At 0.79→0.74 Ma:
- BIO1 decreases in 4/4 regions;
- BIO4 decreases in 4/4;
- BIO15 decreases in 4/4;
- BIO12 increases in 3/4.

For BIO1, central-pair level lies near the lower 5% and temporal SD near the upper 5% across all four regions. This is a sub-threshold tendency because it does not survive the full chronology envelope.

## Table S5 — Orientation matched-window regional medians

| Variable | Region | level mean percentile | absolute-change percentile | temporal-SD percentile |
|---|---|---:|---:|---:|
| BIO1 | Taiwan | 0.143 | 0.852 | 0.847 |
| BIO1 | Ryukyu | 0.141 | 0.884 | 0.850 |
| BIO1 | southern Japan | 0.143 | 0.871 | 0.851 |
| BIO1 | East-Asian core | 0.141 | 0.878 | 0.849 |
| BIO4 | Taiwan | 0.850 | 0.617 | 0.823 |
| BIO4 | Ryukyu | 0.854 | 0.653 | 0.735 |
| BIO4 | southern Japan | 0.856 | 0.640 | 0.723 |
| BIO4 | East-Asian core | 0.855 | 0.611 | 0.720 |
| BIO12 | Taiwan | 0.861 | 0.474 | 0.321 |
| BIO12 | Ryukyu | 0.855 | 0.482 | 0.239 |
| BIO12 | southern Japan | 0.489 | 0.582 | 0.474 |
| BIO12 | East-Asian core | 0.870 | 0.479 | 0.074 |
| BIO15 | Taiwan | 0.102 | 0.597 | 0.820 |
| BIO15 | Ryukyu | 0.138 | 0.608 | 0.803 |
| BIO15 | southern Japan | 0.859 | 0.534 | 0.627 |
| BIO15 | East-Asian core | 0.094 | 0.553 | 0.547 |

These are descriptive matched-window positions and not posterior probabilities.

## Figure S3 — Global sea-level chronology coverage

### Spratt–Lisiecki
- full-envelope chronology coverage: 16/94;
- decision: insufficient for a full chronology-envelope test.

### de Boer
- full-envelope chronology coverage: 94/94;
- tested metrics: state/mean, SD, range, absolute endpoint change, mean absolute 1-kyr change, maximum absolute 1-kyr change;
- robust metrics across chronology: 0;
- formal decision: `no_global_sea_level_metric_survives_full_chronology_gate`.

Global sea level is a broad range-reorganization context variable only. It does not reconstruct local Taiwan/Ryukyu/Japan connectivity.

## Figure S4 — Mid-Pleistocene overlap audit

Orientation chronology overlap:
- 56/94 admissible pairs span exactly 0.800 Ma;
- 90/94 overlap 0.700–0.900 Ma;
- 78/94 overlap 0.750–0.850 Ma;
- 71/94 overlap 0.770–0.830 Ma.

Classification: `broad_mpt_overlap_high_but_not_event_discriminating`.

The overlap is chronology context and is not independent trigger evidence.

## Table S6 — Broader lineage-differentiation climate atlas design

| Design element | Value |
|---|---|
| BIOCLIM variables | 17 |
| dated lineage contexts | 6 |
| representative groups | Nipponocirsium; Arenicola; Sinocirsium |
| tested scenario × variable combinations | 15,472 |
| event-level decision classes | 324 |
| robust event-level classes | **0** |
| recurring climate-context candidates | **0** |

Formal decision: `no_recurring_lineage_differentiation_context_survives_age_region_background_gates`.

This is a lineage-diversification context analysis, not a capitulum-transition test.

### Sub-threshold tendencies

Nipponocirsium and Sinocirsium show cooler / more temperature-variable tendencies in some univariate summaries. Arenicola lies closer to the matched-background centre. No tendency passes every age, region, background and window gate and none is promoted to the main conclusion.

## Table S7 — Multi-lineage global sea-level diagnostic

Representative dated contexts:
- Nipponocirsium: 0.74 Ma, interval 0.60–0.87;
- Arenicola: 0.93 Ma, interval 0.71–1.33;
- Sinocirsium: 0.44 Ma, interval 0.31–0.66.

Seven metrics × three clades = **21 event-metric classes**.

Results:
- robust event-metric classes: **0/21**;
- recurring global sea-level candidates: **0**;
- decision: `no_recurring_global_sea_level_context_survives_age_background_window_gates`.

## Table S8 — Trait-specific historical endpoint

| Module | Repeated history | Relative depth | Calendarized trait transition | Historical trigger status |
|---|---|---|---|---|
| orientation | yes; 4–6 | mixed internal-to-terminal | one full-gate stem event | climate and global sea-level trigger unresolved; repeated trigger not evaluable |
| phyllary posture | yes; 3 | relatively deeper | unavailable | not evaluable |
| stickiness | yes; 5 | shallow/terminal-biased | unavailable; dated range events are not trait ages | not evaluable |
| flower colour | conditional dated white-lineage branch contexts | not admitted as full repeated discrete history | exact transition timing unresolved | historical radiative trigger not evaluable |

## Table S9 — V5 evidence retained outside the V6 main spine

The following analyses remain scientifically valid frozen results but are not used to determine the V6 historical conclusion:
- present-day orientation–environment correspondence;
- two public-image white–coloured sister comparisons;
- current RSDS–chroma pair-level/within-taxon analyses;
- partial coordinated coarse head remodelling.

These results are retained for audit history and later dissertation synthesis. V6 does not use them to infer historical cause.

## Table S10 — Claim boundaries and stop rules

| Layer | V6 decision | Prohibited promotion |
|---|---|---|
| minimum changes | lower bounds | independent origins / convergence counts |
| relative lineage depth | topology-only | Ma / event ages / rates |
| calendar audit | one full-gate trait event | assigning broad radiation age to every change |
| orientation climate | all robust gates unresolved | historical climate causation / adaptation |
| orientation sea level | no robust global metric | local land bridge reconstruction |
| 17-BIOCLIM lineage atlas | 0/324 robust | trait-transition causation |
| three-clade sea level | 0/21 robust | no palaeogeographic role |
| final paper | repeated differentiation resolved; recurring tested trigger not identified | adaptation / natural selection / environmental irrelevance |

## Canonical machine-readable sources

- `data/evidence/chapter2_historical_differentiation_final_summary_v1.json`
- `data/evidence/chapter2_historical_differentiation_evidence_ledger_v1.csv`
- `data/evidence/japan38_relative_event_depth_v1.json`
- `data/evidence/chapter2_orientation_differentiation_environment_v2_summary.json`
- `data/evidence/chapter2_lineage_differentiation_environment_atlas_v1_summary.json`
- `data/evidence/chapter2_lineage_differentiation_sealevel_v1.json`
- `data/evidence/chapter2_orientation_mpt_overlap_audit_v1.json`
- `data/evidence/chapter2_public_dated_tree_recovery_audit_v2.json`

## Final SI conclusion

The public evidence strongly supports repeated capitulum differentiation and unequal evolutionary depth. It does not recover one recurring tested BIOCLIM or global eustatic sea-level trigger after event-timing, regional and matched-background uncertainty are propagated. Missing local palaeogeography, biotic processes and event-specific exposure remain non-identifiable rather than biologically absent.
