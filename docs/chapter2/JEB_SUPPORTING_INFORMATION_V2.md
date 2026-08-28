# Supporting Information for Chapter 2 JEB submission v2

## Article

**Capitulum configuration diversity, minimum change counts and ecological explanatory reach in a young thistle radiation**

This Supporting Information preserves admission decisions, sensitivity analyses, explicit `FAIL` / `unresolved` / `not_evaluable` outcomes and the distinction between present ecological correspondence and historical ecological causation. It supersedes `JEB_SUPPORTING_INFORMATION_V1.md` for the active manuscript; v1 remains audit history.

## Supplementary Figure S1 — Frozen phylogenetic scaffold and admission exceptions

Use the existing Comp1061 phylogram display. Branch lengths are substitutions per site, not absolute time. JPN20 remains represented by two biological samples and is not forcibly collapsed. JPN31 remains excluded from primary trait history because the taxonomic identity conflict blocks the phenotype join. These decisions predate the current manuscript synthesis.

## Supplementary Figure S2 — Continuous EAzami-native diagnostic boundary

Retain the seven-taxon direct continuous-trait diagnostic as a boundary result. Zero of four tested traits passes the corrected all-six-topology retention rule. This does not establish zero phylogenetic signal in Japan38; the direct panel is source- and lineage-clustered and cannot be transferred to the full radiation.

## Supplementary Figure S3 — Species-tip compression audit

All four audited colour-polymorphic systems contain white and coloured state information that one species-tip code cannot represent as separate extant states. Only one system currently has morph-linked nuclear samples. In that system, population-aware coding increases the minimum count from one to two. The result establishes an observation-resolution effect in one testable system, not a radiation-wide transition rate, regain event or general colour-history model.

## Supplementary Figure S4 — Source-balanced lightness stop rule

Retain the Japan-local lightness replication as a bounded negative result. The seven-concept source-balanced panel does not reproduce the preregistered anti-phylogenetic direction. It must not be used to infer that colour is generally conserved or labile in the Japanese radiation.

## Supplementary Figure S5 — Ecological topology and LOO sensitivity

Display the full four-axis orientation screen across the six AU-nonrejected optimized topologies and species leave-one-out fits. BIO15 and BIO1 are the focal axes in the main text. BIO4 and BIO12 remain sensitivity axes and are not promoted by outcome inspection.

## Table S1 — Tree, concept and phenotype admission exceptions

| Layer or concept | Scope | Admission status | Claim boundary |
| --- | --- | --- | --- |
| Comp1061 tree | 39 ingroup samples representing 38 paper concepts | accepted compatibility phylogram with 1,000 UFBoot trees | substitutions/site, not absolute time |
| JPN20 | two biological sequence samples for one paper concept | both tips retained; not forcibly collapsed | cannot be treated as one interchangeable sample |
| JPN31 | one sequence sample | excluded from primary trait history | no phenotype-tip value may be manufactured |
| exactly three discrete histories | orientation, phyllary posture, stickiness | admitted from exact authority concepts | colour/display/cytotype are not silently added |
| ecological orientation panel | nine taxa, U=5/D=4 | n≥10 independent thinned environment-complete occurrences per taxon | present-day taxon centroids, not ancestral niches |

## Table S2 — Discrete history summary

| Trait | Resolved concepts | ML / UFBoot minimum | ML depth envelope | Median UFBoot depth envelope | Current forced-edge examples |
| --- | ---: | --- | --- | --- | --- |
| orientation | 20 | 6 / 4–6 | 0.767–1.000 | 0.795–0.994 | no forced ML edge; JPN36=0.227 |
| phyllary posture | 10 | 3 / 3–3 | 0.695–1.000 | 0.695–1.000 | JPN36=0.728; root posture ambiguous |
| stickiness | 13 | 5 / 5–5 | 0.943–0.954 | 0.937–0.954 | JPN06=0.995; JPN36=0.707; nine-tip internal edge=0.681 |

Minimum counts are unordered-parsimony lower bounds. Relative lineage-depth equals one on a terminal edge and decreases for edges subtending broader descendant lineages. It is not an event age.

The previously quoted localization fractions 0.201, 0.754, 0.67 and 0.40 reproduce on superseded run 32845725038 and are retained only as provenance history.

## Table S3 — Discrete transition-overlap sensitivity

| Pair | Branch-aware rho | Equal-branch median | q05 | Cross-treatment rule |
| --- | ---: | ---: | ---: | --- |
| orientation–phyllary | 0.362 | −0.059 | −0.206 | fail |
| orientation–stickiness | 0.202 | −0.387 | −0.392 | fail |
| phyllary–stickiness | 0.084 | 0.184 | −0.073 | fail |

Zero of three trait pairs supplies a consistently positive shared-transition-localization pattern. This does not prove independent evolutionary modules.

## Table S4 — Orientation ecological correspondence

Primary panel: nine taxa, U=5 and D=4, each with at least ten independent thinned environment-complete occurrence records. Values below are standardized D-minus-U effects across the six accepted optimized topologies.

| Climate axis | Effect range | P range | Accepted-topology sign agreement | Species-LOO sign agreement | Main role |
| --- | ---: | ---: | ---: | ---: | --- |
| CHELSA BIO15 precipitation seasonality | +1.320 to +1.330 SD | 0.05054–0.05239 | 6/6 | 54/54 | primary ecological lead |
| CHELSA BIO1 annual mean temperature | −0.975 to −0.967 SD | 0.09604–0.09793 | 6/6 | 54/54 | secondary ecological lead |

The branchwise diagnostic retains the same directions on all six topologies. For BIO15 the transition-weighted shift is +0.268 SD with permutation P=0.094–0.124. For BIO1 it is −0.199 SD with permutation P=0.108–0.136.

The archived ecological input bundle does not retain raw Comp1061 UFBoot trees, so an ecology-specific raw-bootstrap sign rate is `not_evaluable`. The six accepted AU topologies are not used as a substitute for 1,000 raw bootstrap trees.

## Table S5 — Predictive explanatory reach against two baselines

For every topology and held-out taxon, three predictions were compared:

1. **mean-only null** — training-set mean; no trait and no phylogenetic covariance;
2. **phylogeny-only** — intercept plus Brownian conditional prediction;
3. **phylogeny + orientation** — intercept plus U/D state and Brownian conditional prediction.

Positive ΔMSE means model 3 predicts held-out climate better than the named baseline.

| Axis | ΔMSE vs mean-only null | ΔMSE vs phylogeny-only | Interpretation |
| --- | ---: | ---: | --- |
| BIO15 | +0.224 to +0.230 | −0.108 to −0.102 | orientation helps relative to naive null but not beyond ancestry |
| BIO1 | +0.364 to +0.370 | −0.199 to −0.192 | orientation helps relative to naive null but not beyond ancestry |

The corresponding median ΔMSE values are +0.227 and −0.105 for BIO15, and +0.367 and −0.196 for BIO1. This is the key reason orientation remains `unresolved` rather than `tendency_supported`.

## Table S6 — Trait-level ecological evaluation

| Trait | Historical coverage | Frozen climate overlap | Evaluation | Reason |
| --- | --- | --- | --- | --- |
| orientation | 20 resolved concepts | 9 state-diverse taxa at n≥10 | `unresolved` | direction is topology- and species-LOO-stable, but the trait does not improve prediction beyond phylogeny-only and primary inferential thresholds are not crossed |
| phyllary posture | 10 resolved concepts | 2 unambiguous n≥10 taxa, both ascending | `not_evaluable` | no state-diverse phylogeny-aware climate contrast is estimable |
| stickiness | 13 resolved concepts | 2 evaluable n≥10 taxa, both nonsticky | `not_evaluable` | no sticky/nonsticky climate contrast is estimable |

`not_evaluable` is a data-resolution result. It must not be rewritten as no ecological relationship.

## Table S7 — Ecological mechanism boundary

| Trait | Existing Chapter 2 result | Mechanisms not identified by current data | Required next evidence |
| --- | --- | --- | --- |
| orientation | stable BIO15/BIO1 correspondence, predictive reach unresolved | rain/wetting, thermal presentation, pollinator presentation | same-individual state/environment data and direct mechanism/fitness measurements |
| phyllary posture | repeated minimum changes; ecology not evaluable | enemy exclusion, wetness protection, pollinator-access cost | broader direct posture coverage plus enemy/wetness/access measurements |
| stickiness | repeated minimum changes; ecology not evaluable | enemy benefit, null effect, pollinator cost, production cost | sticky/nonsticky ancestry-matched measurements and manipulation |

These are Chapter 3 mechanism discriminators, not historical causes inferred by Chapter 2.

## Table S8 — Stop rules and claim boundaries

| Analysis or evidence layer | Frozen decision | Boundary retained in this submission |
| --- | --- | --- |
| absolute transition time | `STOP_NOT_IDENTIFIABLE` | no calendar ages or rates from substitutions/site tree |
| minimum changes | admitted lower bounds | not independent-origin counts or convergence counts |
| relative lineage-depth | admitted topology-only envelopes | not event age or ecological event timing |
| orientation climate correspondence | `unresolved` | not adaptation or repeated ecological convergence |
| phyllary ecology | `not_evaluable` | not no relationship |
| stickiness ecology | `not_evaluable` | not no relationship |
| species-tip colour compression | one morph-linked system | not a general rate/regain result |
| direct functional mechanism | Chapter 3 | no historical transition is called adaptive from present correlations |

## Machine-readable sources

- `data/evidence/chapter2_core_result_recovery_v1.csv`
- `data/evidence/chapter2_relative_event_depth_contract_v1.json`
- `data/evidence/japan38_relative_event_depth_v1.json`
- `data/evidence/chapter2_time_axis_compute/japan38_latest_module_transition_overlap_v2.json`
- `data/evidence/chapter2_time_axis_compute/japan38_latest_module_overlap_topology_sensitivity_v2.json`
- `data/evidence/chapter2_ecological_explanatory_reach_v1.json`
- `data/evidence/fdt4_eastasia_pgls_recovered_diagnostic_v1.json`
- `data/evidence/fdt4_branchwise_niche_transition_concordance_v1.json`
- `data/evidence/hmm2_population_aware_transition_test_v1.json`
- `data/evidence/chapter2_eazami_native_continuous_history_diagnostic_v1.json`

## File and claim audit

- [x] minimum change, relative lineage-depth and ecological reach are reported as distinct estimands;
- [x] null and phylogeny-only predictive baselines are separated;
- [x] species LOO and accepted-topology sign stability are explicit;
- [x] raw ecological UFBoot sign rate is marked `not_evaluable` rather than substituted;
- [x] phyllary and stickiness `not_evaluable` states are not reported as zero effects;
- [x] no minimum step is called an independent origin, convergence or adaptation;
- [x] no substitutions/site branch is called absolute time;
- [x] no present ecological correspondence is called historical causation.
