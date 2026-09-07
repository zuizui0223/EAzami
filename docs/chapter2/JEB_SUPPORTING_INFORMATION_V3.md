# Supporting Information for “Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation”

This Supporting Information is the active V7 submission-facing companion. It preserves uncertainty, post-result robustness labels, finite-map rank interpretation, and explicit claim ceilings. Earlier Supporting Information versions remain audit history for prior manuscript framings.

## S1. Nuclear scaffold and admission boundaries

The full Japan38 comparison uses the independently reconstructed Compositae1061-compatible common-locus scaffold. The accepted reconstruction used 236 quality-controlled loci, 176 rootable loci and a 161,654-bp concatenated alignment, with 1,000 UFBoot and 1,000 SH-aLRT replicates. Branch lengths are substitutions per site and are not calendar time.

Thirty-six of 38 sampled Japanese concepts occur in the dominant radiation. Authority-backed capitulum states remain missing or ambiguous where source descriptions do not resolve them. JPN20 remains represented by two biological sequence samples rather than being forcibly collapsed, and JPN31 remains excluded from primary trait-history joins where identity blocks a defensible phenotype assignment.

## S2. Discrete trait histories and relative lineage depth

| Trait | Resolved concepts | ML / UFBoot minimum changes | Median UFBoot relative-depth envelope |
| --- | ---: | --- | --- |
| orientation | 20 | 6 / 4–6, median 5 | 0.795–0.994 |
| phyllary posture | 10 | 3 / 3–3 | 0.695–1.000 |
| involucre stickiness | 13 | 5 / 5–5 | 0.937–0.954 |

Minimum changes are unordered-parsimony lower bounds. They are not counts of independent origins, convergence events or evolutionary rates. Relative lineage depth is topology-only: 1 marks a terminal edge and smaller values allow changes on edges subtending broader descendant lineages.

## S3. Paired-topology depth ordering

| Ordering | Topologies retaining direction | Classification |
| --- | ---: | --- |
| phyllary deeper-permissive than stickiness | 1000/1000 | robust |
| phyllary deeper-permissive than orientation | 993/1000 | robust |
| orientation deeper-permissive than stickiness | 905/1000, 7 ties | stable |
| complete phyllary < orientation < stickiness | 898/1000 | stable |

These fractions are topology-sensitivity descriptors rather than probabilities or independent biological replicates.

## S4. Coverage-matched missing-state sensitivity

Phyllary remained at its observed 10 resolved concepts. Orientation and stickiness were deterministically masked to 10 known states while the full 36-tip topology remained unchanged.

| Comparison | Fraction retaining phyllary-deeper relation |
| --- | ---: |
| phyllary < matched orientation median | 195/200 = 97.5% |
| phyllary < matched stickiness median, 5/5 | 193/200 = 96.5% |
| phyllary < matched stickiness median, 6/4 | 193/200 = 96.5% |
| phyllary < matched orientation q05 | 21/200 = 10.5% |
| phyllary < matched stickiness q05, 5/5 | 22/200 = 11.0% |
| phyllary < matched stickiness q05, 6/4 | 31/200 = 15.5% |

The central ordering survives matched observed-state coverage, whereas the deepest matched tails overlap. The result is not coverage-independent.

## S5. Shared-transition localization

| Trait pair | Branch-aware rho | Equal-branch median | q05 | Robust shared-localization rule |
| --- | ---: | ---: | ---: | --- |
| orientation–phyllary | 0.362 | −0.059 | −0.206 | fail |
| orientation–stickiness | 0.202 | −0.387 | −0.392 | fail |
| phyllary–stickiness | 0.084 | 0.184 | −0.073 | fail |

Zero of three pairs passes the declared cross-treatment rule. This rejects the simplest synchronized whole-capitulum history under current coverage but does not establish genetic or developmental independence.

## S6. Cross-scale orientation–environment correspondence

Within-taxon, among-taxon and East-Asian state contrasts are distinct estimands and are not pooled.

| Axis | Azami within-taxon | Azami among-taxon | East-Asian orientation result |
| --- | --- | --- | --- |
| BIO12 annual precipitation | +0.00533, q=0.874 | +0.30436, q=0.00640 | not used as a focal state contrast |
| BIO15 precipitation seasonality | −0.00762, q=0.121 | +0.0670, q=0.599 | D−U +1.320 to +1.330 SD; 6/6 topology and 54/54 topology × species-LOO sign stability |
| BIO1 annual mean temperature | +0.01715, q=0.0349 | −0.03024, q=0.836 | D−U −0.975 to −0.967 SD; 54/54 sign stability |

The correct source classification is `orientation_environment_association_is_scale_partitioned`.

## S7. History-conditioned counterfactual calibration

The strict East-Asian panel contains nine taxa, five upward/erect and four downward/nodding. All 126 placements of the four downward states were exhaustively evaluated.

| Counterfactual class | BIO15 maps at least as positive as observed | BIO1 maps at least as extreme in observed direction |
| --- | ---: | ---: |
| same state frequency | 5/126 = 3.97% | 8/126 = 6.35% |
| exact recurrence profile | 3/40 = 7.5% | 4/40 = 10% |
| recurrence + nearest relative-depth geometry | 3/10 = 30% | 3/10 = 30% |

A reverse BIO15 world exists among recurrence-matched maps and reaches a signed statistic of −1.784, but no reverse BIO15 map occurs in the nearest-history pool of 10. These are finite conditional ranks, not P values. The result does not support an ancestry-independent climatic effect.

## S8. Fixed transition-regime hypothesis

The predeclared U→D present-niche vector was `BIO15 up + BIO1 down`.

| Panel | State counts | Exact finite-map rank for U→D composite |
| --- | --- | ---: |
| n≥5 primary | 12 taxa, 7 U / 5 D | 16/792 = 2.02% |
| n≥3 sensitivity | 13 taxa, 7 U / 6 D | 19/1716 = 1.11% |
| strict n≥10 | 9 taxa, 5 U / 4 D | 4/126 = 3.17% |

In the strict panel, BIO15 alone ranks 7/126 = 5.56% and lower BIO1 alone 8/126 = 6.35%. The supported object is therefore the fixed two-axis present-niche regime rather than either single axis alone.

The reverse D→U direction tracks the opposite side of the same strict regime. Forward and reverse alignment are positive on 6/6 topologies and the exact bidirectional-floor rank is 3/126 = 2.38%. This is bidirectional present-niche tracking under the declared estimator, not demonstrated genetic or developmental reversibility.

## S9. Fixed falsification ladder

| Falsification | Result | Reading |
| --- | ---: | --- |
| strict n≥10 | 4/126 = 3.17% | pass |
| Japan-only n≥5 | 10/56 = 17.86% | directional but not exceptional |
| delete each strict-panel taxon | expected direction retained in 9/9 deletion panels | not one-taxon driven; exact extremeness is panel-sensitive |
| latitude/longitude residualization | 5/126 = 3.97% | persists after removing simple linear geography |
| internal-edge-only scoring | 3/126 = 2.38% | not confined to terminal-edge contrast |
| geography residualization + internal-edge-only | 3/126 = 2.38% | survives combined strict stress |
| combined n≥5 sensitivity | 29/792 = 3.66% | same qualitative result in expanded panel |

These tests are post-result robustness analyses, not independent confirmations. Internal environmental values are Brownian reconstructions from present-day niche centroids rather than observed ancestral environments.

## S10. Bounded historical orientation event and origin-regime persistence

Only one current capitulum event reaches the full public-data chain from trait transition to bounded chronology, palaeolocation scenarios and historical environment: the core-*Nipponocirsium* U→D orientation event.

- chronology pairs: 94;
- palaeolocation regions: 4;
- chronology × region scenarios: 376;
- central pair: 0.79–0.74 Ma;
- southern Japan ranks first in 48/94 chronology scenarios;
- southern Japan exceeds Taiwan in 61/94, the Ryukyu corridor in 61/94 and East-Asian core in 64/94 scenarios;
- none crosses the frozen 75% dominance gate.

At the central pair, BIO1, BIO4 and BIO15 decrease in all four regions, while BIO12 increases in three of four. No tested BIO1/BIO4/BIO12/BIO15 signed direction, level, absolute change or variability class survives the full chronology × palaeolocation uncertainty envelope.

The fixed present U→D sign combination (`BIO15 delta > 0`, `BIO1 delta < 0`) matches only 99/376 = 26.3% historical scenarios: Taiwan 20/94, Ryukyu corridor 9/94, southern Japan 41/94 and East-Asian core 29/94. The present regime is therefore not supported as a persistent origin regime.

## S11. Broader historical-cause ceiling

| Historical diagnostic | Scope | Robust classes |
| --- | --- | ---: |
| BIOCLIM atlas | 17 variables, six dated lineage contexts, 15,472 scenario × variable combinations | 0/324 event-level classes |
| global sea-level diagnostic | three representative clades × seven metrics | 0/21 event-metric classes |

This constrains one recurring coarse tested historical explanation. It does not show that environment, local palaeogeography or biotic interactions were irrelevant.

## S12. Mechanism and causal boundary

Current data do not identify rain/wetting, UV/radiation, temperature, pollinator behaviour, antagonists, selection, adaptation or reproductive-fitness benefit as the cause of any East-Asian *Cirsium* orientation transition. External experiments provide mechanism priors only. Direct causal resolution requires trait-linked mediator and reproductive-fitness measurements or better event-linked historical data.

## Machine-readable sources

- `data/evidence/chapter2_current_claims_h1_h4_v1.json`
- `data/evidence/chapter2_historical_differentiation_final_summary_v1.json`
- `data/evidence/chapter2_depth_ordering_robustness_result_v1.json`
- `data/evidence/chapter2_depth_coverage_matched_sensitivity_result_v1.json`
- `data/evidence/chapter2_orientation_environment_scale_partition_v1.json`
- `data/evidence/chapter2_orientation_environment_counterfactual_result_v1.json`
- `data/evidence/chapter2_orientation_transition_regime_hypothesis_result_v1.json`
- `data/evidence/chapter2_orientation_transition_regime_robustness_result_v1.json`
- `data/evidence/chapter2_orientation_transition_regime_single_deletion_result_v1.json`
- `data/evidence/chapter2_orientation_transition_regime_geography_residual_result_v1.json`
- `data/evidence/chapter2_orientation_transition_regime_internal_edge_result_v1.json`
- `data/evidence/chapter2_orientation_transition_regime_combined_stress_result_v1.json`
- `data/evidence/chapter2_orientation_origin_region_ranking_result_v1.json`

## Submission claim audit

- [x] minimum changes are not called independent origins or rates;
- [x] relative lineage depth is not called time;
- [x] topology and coverage sensitivities remain separate;
- [x] finite-map ranks are not called biological-replicate P values;
- [x] within/among/East-Asian ecology are not pooled;
- [x] transition-niche tracking is not called climatic causation, selection or adaptation;
- [x] reconstructed internal environments are not called observed ancestral climates;
- [x] Japan-only failure is retained;
- [x] present/origin regime non-persistence is retained;
- [x] 0/324 and 0/21 are not rewritten as environmental irrelevance.
