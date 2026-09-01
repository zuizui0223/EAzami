# Supporting Information for Chapter 2 JEB submission V5

## Article

**Modular evolutionary depth and lineage-dependent environmental correspondence of capitulum traits in a young thistle radiation**

This Supporting Information preserves the evidence layers that are necessary to audit the V5 conclusions but would overload the five main figures. It retains negative, `unresolved` and `not_evaluable` results and keeps present ecological correspondence separate from historical environmental causation.

The main-text evidence order is:

`repeated depth → shared-history boundary → orientation state–trajectory test → colour natural experiment → whole-capitulum synthesis`.

## Supplementary Figure S1 — Harmonized Japan38 nuclear scaffold and admission exceptions

Use the accepted Comp1061-compatible phylogram. Branch lengths are substitutions per site and must not be labelled absolute time.

Admission notes:

- 38 paper concepts, 39 focal biological samples;
- 236 QC loci, 176 rootable loci, 161,654 aligned bp;
- JPN20 represented by two non-monophyletic sequence samples and not forcibly collapsed;
- JPN31 excluded from primary trait history because the frozen identity/locality conflict prevents a clean phenotype join;
- the tree is the **harmonized common-locus Japan38 scaffold**, not the only nuclear evidence available for East-Asian *Cirsium*.

## Supplementary Figure S2 — Full minimum-history and edge-localization diagnostics

### Table S2.1 — Discrete history summary

| Trait | Resolved concepts | ML / UFBoot minimum | ML depth envelope | Median UFBoot depth envelope | Selected forced-edge fractions |
|---|---:|---|---|---|---|
| orientation | 20 | 6 / 4–6 | 0.767–1.000 | 0.795–0.994 | no forced ML edge; JPN36=0.227 |
| phyllary posture | 10 | 3 / 3–3 | 0.695–1.000 | 0.695–1.000 | JPN36=0.728 |
| stickiness | 13 | 5 / 5–5 | 0.943–0.954 | 0.937–0.954 | JPN06=0.995; JPN36=0.707; JPN30=0.545; nine-tip internal edge=0.681 |

Minimum counts are unordered-parsimony lower bounds. Relative lineage-depth equals one on a terminal edge and decreases for edges subtending broader descendant lineages. It is not event age.

### Table S2.2 — Transition-overlap sensitivity

| Trait pair | Branch-aware rho | Equal-branch median | Equal-branch q05 | Robust shared-localization rule |
|---|---:|---:|---:|---|
| orientation–phyllary | 0.362 | −0.059 | −0.206 | fail |
| orientation–stickiness | 0.202 | −0.387 | −0.392 | fail |
| phyllary–stickiness | 0.084 | +0.184 | −0.073 | fail |

Zero of three pairs retains consistently positive transition localization across branch-length treatments. This constrains a simple synchronized-history model but does not prove genetic, developmental or selective independence.

The previously quoted localization fractions 0.201, 0.754, 0.67 and 0.40 reproduce only on superseded run 32845725038 and are provenance history, not active values.

## Supplementary Figure S3 — Full orientation present-ecology sensitivity

### Frozen GBIF primary

Panel: n=9 taxa, U=5 and D=4; each taxon has at least ten independent thinned environment-complete occurrences.

| Axis | D−U effect across six accepted topologies | P range | Topology sign | Species LOO sign | Frozen class |
|---|---:|---:|---:|---:|---|
| BIO15 precipitation seasonality | +1.320 to +1.330 SD | 0.05054–0.05239 | 6/6 | 54/54 | `unresolved` |
| BIO1 annual mean temperature | −0.975 to −0.967 SD | 0.09604–0.09793 | 6/6 | 54/54 | `unresolved` |

### Direct Taiwan biodiversity-network sensitivity

Panel: n=11, U=6 and D=5.

- BIO15 D−U +1.136 to +1.143 SD, P=0.03789–0.03980;
- BIO1 D−U −1.001 to −0.994 SD, P=0.04819–0.04904;
- sign agreement 6/6 topologies and 66/66 topology × species-LOO fits;
- frozen tier class `tendency_supported`.

### Broader source-name-guarded Taiwan sensitivity

Panel: n=11, U=6 and D=5.

- BIO15 D−U +1.078 to +1.084 SD, P=0.04874–0.05110;
- BIO1 D−U −0.915 to −0.909 SD, P=0.06525–0.06598;
- sign agreement 6/6 topologies and 66/66 topology × species-LOO fits;
- frozen tier class `unresolved`.

The biological direction is robust; threshold crossing depends on the admissible occurrence-source definition used to estimate niche centroids. The direct-TBN tier is not selected as the primary after observing its P values.

### Predictive sensitivity

The held-out mean-null / phylogeny-only / phylogeny-plus-orientation comparison remains Supporting Information only. Orientation improves prediction relative to a mean-only null but not relative to the phylogeny-only Brownian predictor in the n=9 panel. Predictive model competition does not define the main ecological classification.

## Supplementary Figure S4 — Orientation origin chronology × palaeolocation envelope

The active historical target is the core-Nipponocirsium stem after erect *C. morii* and before the sampled Japanese-core/Taiwan-core nodding split.

The dates come from separate public studies and are not a joint posterior:

- parent/*C. morii* split: central 0.79 Ma; marginal interval 0.43–1.18 Ma;
- child Japanese-core/Taiwan-core split: central 0.74 Ma; interval 0.60–0.87 Ma.

A deterministic grid retains 94 topologically admissible parent>child pairs. Four predeclared palaeolocation scenarios are evaluated:

1. Taiwan;
2. Ryukyu corridor;
3. southern Japan;
4. broad East-Asian core corridor.

This gives 376 region × chronology trajectories. Public PALEO-PGEM BIO1/BIO4/BIO12/BIO15 values are standardized against all same-duration regional windows and compared with the frozen Azami orientation state vector by cosine similarity.

### Table S4.1 — Regional envelope summary

| Region | n age scenarios | cosine q05 | cosine median | cosine q95 | fraction cosine >0 | matched-null percentile median |
|---|---:|---:|---:|---:|---:|---:|
| Taiwan | 94 | −0.791 | −0.122 | +0.592 | 0.383 | 0.452 |
| Ryukyu corridor | 94 | −0.859 | −0.084 | +0.641 | 0.415 | 0.468 |
| southern Japan | 94 | −0.695 | +0.054 | +0.643 | 0.553 | 0.539 |
| broad East-Asian core corridor | 94 | −0.810 | −0.078 | +0.578 | 0.447 | 0.471 |

Cross-scenario:

- cosine q05 −0.7991;
- median −0.0647;
- q95 +0.6087;
- matched-window percentile median 0.4705;
- classification `origin_trajectory_unresolved_under_public_chronology_and_paleolocation_uncertainty`.

The regional boxes are scenarios rather than ancestral-area probabilities. The chronology grid is not a joint posterior. The historical analysis therefore identifies an uncertainty ceiling rather than an event-specific hydric cause.

Full 376 scenario rows are retained in the checksum-identified successful workflow artifact referenced by `data/evidence/chapter2_orientation_origin_envelope_result_v1.json`.

## Supplementary Figure S5 — Restricted Taiwan descendant sensitivity

The previously analysed 0.79–0.47 Ma Taiwan-trio interval is not the unique orientation origin after public Japanese core Nipponocirsium is included. It is retained as a restricted descendant-lineage sensitivity.

Key results:

- BIO12 increases, but change/variability is typical among same-duration windows;
- BIO15 changes toward lower seasonality, opposite the present downward-state high-BIO15 association;
- BIO1 warms, opposite the present downward-state cooler-niche association;
- four-dimensional state–trajectory cosine ≈0.059 with null percentile ≈0.518;
- wet-side BIO13/BIO16 dynamics do not outperform dry-side BIO14/BIO17 controls;
- Sep–Oct and Aug–Nov descendant flowering-window precipitation increase directionally but are not exceptional;
- regional spatial uncertainty is >11× the temporal SD for the focal hydric variables;
- global sea-level variability over the interval is not exceptional relative to same-duration windows.

This sensitivity is retained specifically to demonstrate why current niche direction cannot be projected backward to infer origin.

## Supplementary Figure S6 — Public-image cohort and colour assay validation

Two dated sister-system comparisons were measured with the same frozen public-image trait implementation used for the global state-space analysis:

- Arenicola: *C. brevicaule* white versus *C. irumtiense* bluish-purple;
- Taiwan: *C. kawakamii* white versus *C. tatakaense* purple.

Public iNaturalist observations were selected under one source contract. Duplicate photo IDs were removed. Multiscale crops were selected only by the frozen foreground-mask quality, sharpness and resolution, without using known flower colour, environment or measured trait values. After the neutral gate, all four taxa were balanced to 14 observations.

### Table S6.1 — Colour assay

| System | n white usable | n coloured usable | chroma white−coloured | bootstrap 95% | lightness white−coloured |
|---|---:|---:|---:|---|---:|
| Arenicola | 7 | 8 | −2.951 | −21.92 to +4.71 | +6.86 |
| Taiwan | 3 | 3 | −6.162 | −19.48 to +3.46 | +8.24 |

The preregistered assay gate passed because the white lineage had lower chroma in both systems with at least three usable observations per role. The gate validates direction and assessability; it is not a significance rule, and both chroma intervals include zero.

## Supplementary Figure S7 — Focal current colour–RSDS concordance

Only the frozen global prediction `higher current CHELSA RSDS -> lower visible chroma` was tested. No environmental predictor screen was performed.

### Table S7.1 — Sister-pair primary result

| System | RSDS white−coloured | bootstrap 95% | chroma white−coloured | Azami direction |
|---|---:|---|---:|---|
| Arenicola | +1814 | +663.1 to +1957 | −2.951 | concordant |
| Taiwan | −686.5 | −1513 to −172 | −6.162 | discordant |

After taxon × 0.05° locality aggregation:

- Arenicola RSDS +1712, still concordant;
- Taiwan RSDS −1703, still reversed.

Primary pair-level concordance = 1/2.

### Secondary within-taxon diagnostic

Across 21 usable colour observations from all four taxa after within-taxon demeaning:

- standardized beta = −0.4065;
- two-sided restricted permutation P=0.1141;
- prespecified expected-negative one-sided P=0.0361.

The within-taxon result is a scale diagnostic and does not replace the 1/2 pair-level primary outcome. Current RSDS may covary with geography, elevation, ancestry and other environmental variables, and it is not a historical surface-radiation reconstruction.

## Supplementary Figure S8 — Coarse repeated remodelling and fine-geometry negative evidence

### Table S8.1 — Same-direction coarse endpoints

| Endpoint, white−coloured | Arenicola | Taiwan | Repeated direction |
|---|---:|---:|---|
| circularity | +0.238 | +0.159 | white higher |
| solidity | +0.092 | +0.099 | white higher |
| visible floret fraction | −0.305 | −0.028 | white lower |

Only the Arenicola circularity and solidity bootstrap intervals exclude zero. The repeated result is therefore directional rather than uniformly strong.

### Fine-geometry endpoints retained as heterogeneous or low-information

- shape aspect ratio;
- width-profile CV;
- involucre length/width ratio;
- apical taper ratio;
- basal taper ratio;
- projection roughness;
- projection p95;
- spread fraction;
- bract projection peak density.

Image-derived involucre proxies are not botanical phyllary-posture measurements. Opposite directions and low usable n are retained as evidence against a universal white-flower whole-capitulum syndrome.

## Supplementary Figure S9 — Present 18-D integration and whole-capitulum boundary

The frozen complete-case present analysis contains 127 taxa. PC1–PC3 explain 42.3% cumulatively. Within-versus-among association-matrix similarity is Spearman rho=0.3663.

This moderate present association is combined with:

- 0/3 robust shared localization among discrete orientation/phyllary/stickiness histories;
- repeated coarse head directions in the two dated white-lineage comparisons;
- heterogeneous fine geometry.

The bounded conclusion is **partial module covariance inside trait-specific histories**, not one synchronized syndrome and not complete independence.

## Supplementary Table S10 — Trait × driver final evidence classes

| Trait × driver | Final public-data class | Primary missing link |
|---|---|---|
| orientation × hydric exposure | `history_resolved_current_hydric_candidate_origin_driver_unresolved` | ancestral exposure / focal fitness |
| flower colour × radiative environment | `replicated_white_state_current_RSDS_lineage_scale_dependent_historical_driver_unresolved` | historical radiative exposure / focal mechanism-fitness |
| phyllary posture × enemy/wetting/access | `history_resolved_cause_unidentified` | homologous spatial/environmental and mechanism evidence |
| stickiness × biotic enemy/cost | `rapid_history_resolved_biotic_driver_unidentified` | historical biotic driver / benefit-cost fitness path |
| orientation × thermal regime | `directional_mismatch_to_explain` | scale-matched thermal causation |
| outline/head packing × multivariate environment | `present_breadth_plus_replicated_coarse_extant_remodelling_history_unresolved` | dated continuous history / mechanism |
| whole capitulum | `partial_module_covariation_universal_synchronized_syndrome_not_supported` | shared development/pleiotropy/correlated selection versus independent response |

All rows retain `causal_claim_allowed=no`.

## Supplementary Table S11 — Non-climate constraints

- Cytotype/ploidy: upward/ascending orientation occurs at 2x, 4x and 6x; diploids include both orientation states, so a deterministic one-to-one ploidy explanation is inconsistent with the current panel.
- Broad biogeographic history: multiple capitulum configurations occur inside the dominant Japanese radiation; configuration does not map one-to-one to the broad colonization class.
- Population/genetic structure: independent Japanese MIG-seq/RAD and public *C. maritimum* population data demonstrate below-species-tip structure relevant to the species-tip resolution boundary.
- Independent local topology: Korean rDNA and 2025/2026 East-Asian phylotranscriptomics provide narrower-scale nuclear constraints; heterogeneous marker systems are not pooled into one branch-length tree.
- Pollinator/enemy context: biologically plausible, but no dense harmonized Japan38 interaction matrix supports an equivalent comparative test.

## Supplementary Table S12 — Species-tip colour compression boundary

All four audited polymorphic systems contain extant white and coloured states that a single species-tip code cannot represent simultaneously. Only one currently has morph-linked nuclear samples. In that system, population-aware coding increases the minimum from one to two. This is an observation-resolution result, not a radiation-wide colour-transition rate or regain result.

## Supporting machine-readable sources

Primary source artifacts for V5 include:

- `data/evidence/chapter2_final_integrated_evidence_v3.json`;
- `data/evidence/japan38_relative_event_depth_v1.json`;
- `data/evidence/chapter2_time_axis_compute/japan38_latest_module_transition_overlap_v2.json`;
- `data/evidence/chapter2_time_axis_compute/japan38_latest_module_overlap_topology_sensitivity_v2.json`;
- `data/evidence/chapter2_ecological_explanatory_reach_v1.json`;
- `data/evidence/fdt4_taiwan_multisource_orientation_sensitivity_v1.json`;
- `data/evidence/chapter2_orientation_origin_envelope_result_v1.json`;
- `data/evidence/chapter2_four_taxon_azami_measurement_result_v1.json`;
- `data/evidence/chapter2_colour_rsds_focal_concordance_result_v1.json`;
- `data/evidence/chapter2_nonclimate_explanatory_constraints_v1.json`;
- `data/evidence/east_asia_independent_nuclear_evidence_audit_v1.csv`.

## File and claim audit

- [x] minimum changes, relative lineage-depth, current ecology and historical environment are separate estimands;
- [x] current BIO12/BIO15 correspondence is not described as one replicated coefficient;
- [x] orientation origin chronology is a scenario envelope, not a joint posterior;
- [x] restricted Taiwan descendant analysis is not treated as the unique origin branch;
- [x] pair-level colour RSDS reversal is shown rather than averaged away;
- [x] within-taxon colour slope remains secondary;
- [x] coarse head directions are separated from heterogeneous fine geometry;
- [x] `not_evaluable` is retained as non-identifiability;
- [x] no minimum-change count is called convergence or independent origin;
- [x] no present environment is called historical cause;
- [x] no repeated white state is called a demonstrated pigment/UV mechanism;
- [x] no whole-capitulum pattern is called genetic modularity or common development;
- [x] no row establishes selection, adaptation or reproductive-fitness benefit.
