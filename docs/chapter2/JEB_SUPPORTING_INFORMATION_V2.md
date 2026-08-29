# Supporting Information for Chapter 2 JEB submission v3

## Article

**Capitulum configuration diversity, minimum change counts and ecological explanatory reach in a young thistle radiation**

This Supporting Information preserves admission decisions, sensitivity analyses, explicit `FAIL` / `unresolved` / `not_evaluable` outcomes, the distinction between present ecological correspondence and historical ecological causation, and the distinction between the harmonized Japan38 scaffold and other independent nuclear evidence. It supersedes `JEB_SUPPORTING_INFORMATION_V1.md` for the active manuscript; v1 remains audit history.

## Supplementary Figure S1 — Frozen phylogenetic scaffold and admission exceptions

Use the existing Comp1061 phylogram display. Branch lengths are substitutions per site, not absolute time. JPN20 remains represented by two biological samples and is not forcibly collapsed. JPN31 remains excluded from primary trait history because the taxonomic identity conflict blocks the phenotype join. These decisions predate the current manuscript synthesis.

The Comp1061 tree is the primary **harmonized common-locus scaffold** for the full Japan38 comparison. It is not the only nuclear evidence available for Japanese or East-Asian *Cirsium*; independent rDNA, MIG-seq/RAD, transcriptome, reference-genome and local phylotranscriptomic resources are summarized below.

## Supplementary Figure S2 — Continuous EAzami-native diagnostic boundary

Retain the seven-taxon direct continuous-trait diagnostic as a boundary result. Zero of four tested traits passes the corrected all-six-topology retention rule. This does not establish zero phylogenetic signal in Japan38; the direct panel is source- and lineage-clustered and cannot be transferred to the full radiation.

## Supplementary Figure S3 — Species-tip compression audit

All four audited colour-polymorphic systems contain white and coloured state information that one species-tip code cannot represent as separate extant states. Only one system currently has morph-linked nuclear samples. In that system, population-aware coding increases the minimum count from one to two. The result establishes an observation-resolution effect in one testable system, not a radiation-wide transition rate, regain event or general colour-history model.

Independent genome-wide evidence reinforces the *need to treat species-tip compression as a real resolution problem* without changing the minimum-count result itself. A 2017–2021 Japanese MIG-seq/RAD programme reported large within-population variation, isolation by distance and weak named-species separation in an examined diploid subsection. A public 2022 *C. maritimum* MIG-seq Genepop matrix supplies a reusable one-species example overlapping Japan38 JPN_17. Neither source is linked to the exact Japan38 phenotype/voucher and neither is substituted for the common-locus species tree.

## Supplementary Figure S4 — Source-balanced lightness stop rule

Retain the Japan-local lightness replication as a bounded negative result. The seven-concept source-balanced panel does not reproduce the preregistered anti-phylogenetic direction. It must not be used to infer that colour is generally conserved or labile in the Japanese radiation.

## Supplementary Figure S5 — Ecological topology and LOO sensitivity

Display the full four-axis orientation screen across the six AU-nonrejected optimized topologies and species leave-one-out fits. BIO15 and BIO1 are the focal axes in the main text. BIO4 and BIO12 remain sensitivity axes and are not promoted by outcome inspection.

## Table S1 — Tree, concept and phenotype admission exceptions

| Layer or concept | Scope | Admission status | Claim boundary |
| --- | --- | --- | --- |
| Comp1061 tree | 39 ingroup samples representing 38 paper concepts | accepted harmonized common-locus compatibility phylogram with 1,000 UFBoot trees | primary full-panel scaffold; not the only East-Asian nuclear evidence; substitutions/site, not absolute time |
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

## Table S5 — Predictive diagnostic retained as sensitivity, not the main ecological decision

For every topology and held-out taxon, three predictions were compared:

1. **mean-only null** — training-set mean; no trait and no phylogenetic covariance;
2. **phylogeny-only** — intercept plus Brownian conditional prediction;
3. **phylogeny + orientation** — intercept plus U/D state and Brownian conditional prediction.

Positive ΔMSE means model 3 predicts held-out climate better than the named baseline.

| Axis | ΔMSE vs mean-only null | ΔMSE vs phylogeny-only | Interpretation |
| --- | ---: | ---: | --- |
| BIO15 | +0.224 to +0.230 | −0.108 to −0.102 | orientation helps relative to naive null but not beyond ancestry in this small predictive diagnostic |
| BIO1 | +0.364 to +0.370 | −0.199 to −0.192 | same qualitative result |

This diagnostic is retained for transparency but is **not required to define ecological explanatory reach in the main paper**. The primary classification is based on the magnitude/direction of the correspondence, topology and species-LOO stability, frozen inferential thresholds and whether the trait × ecology overlap is evaluable. With only nine taxa, predictive model competition is not promoted as the central result.

## Table S6 — Trait-level ecological evaluation

| Trait | Historical coverage | Frozen climate overlap | Evaluation | Reason |
| --- | --- | --- | --- | --- |
| orientation | 20 resolved concepts | 9 state-diverse taxa at n≥10 | `unresolved` | BIO15/BIO1 directions are large and stable to all six accepted topologies and all species-LOO fits, but frozen PGLS/branchwise thresholds are not crossed |
| phyllary posture | 10 resolved concepts | 2 unambiguous n≥10 taxa, both ascending | `not_evaluable` | no state-diverse phylogeny-aware climate contrast is estimable |
| stickiness | 13 resolved concepts | 2 evaluable n≥10 taxa, both nonsticky | `not_evaluable` | no sticky/nonsticky climate contrast is estimable |

`not_evaluable` is a data-resolution result. It must not be rewritten as no ecological relationship.

## Table S7 — Non-climate explanatory factors available from current data

| Factor | Current overlap/result | What it can currently say | What it cannot say |
| --- | --- | --- | --- |
| cytotype/ploidy | 9 source-backed concepts; 7 with known orientation in dominant radiation | one-to-one ploidy assignment of orientation is inconsistent with observed data: upward/ascending occurs at 2x, 4x and 6x; diploids include upward and downward states | no statistical independence, transition rate or causal ploidy effect |
| broad biogeographic history | 36/38 Japan concepts in dominant radiation; rare secondary-history comparators | capitulum configurations do not map one-to-one onto the broad colonization-history class | no event-specific selective cause |
| population/genetic structure | pre-2025 Japanese MIG-seq/RAD; public *C. maritimum* MIG-seq | species-tip coding can conceal population structure and named-species boundaries can be weak in a shallow radiation | no radiation-wide trait explanation without same-individual trait/genotype linkage |
| pollinator / antagonist context | source-backed *Cirsium* literature and meta-analysis priors | supplies mechanistic alternatives and shows strong reproductive antagonist costs at genus level | no joined Japan38 taxon-level predictor matrix for the three focal history traits |

Thus climate is not assumed to be the only biologically plausible driver; it is simply the only ecological predictor currently joined densely enough to orientation for a phylogeny-aware comparative screen.

## Table S8 — Independent nuclear-DNA evidence outside the Moreyra 2025 scaffold

| Year | Evidence | Scale | Direct relevance to Chapter 2 | Admission boundary |
| --- | --- | --- | --- | --- |
| 2012 | Korean *C. pendulum* / *C. setidens* 18S–ITS–5.8S–ITS2–partial 28S | multi-locality rDNA | exact species-name overlap with JPN38 *C. pendulum*; NE-Asia nuclear context | linked rDNA array; not genome-wide topology |
| 2015 | Korean *C. japonicum*, *C. shantarense*, *C. nipponicum*, *C. chanroenicum* rDNA | regional rDNA | downward *C. shantarense* clusters with upward *C. japonicum* despite orientation difference | sparse sampling; not evidence of evolutionary independence |
| 2017–2021 | KAKEN 17K07524 Japanese MIG-seq/RAD | regional/population genome-wide reduced representation | large within-population variation, IBD and weak species separation support species-tip resolution caution | grey/direct report; raw genotype matrix unrecovered |
| 2018 | Korean *C. japonicum* var. *spinossimum* RNA-seq | functional transcriptome | 51,133-unigene floral reference resource | not species-tree evidence |
| 2019 | Cardueae Compositae1061 Hyb-Seq | deep phylogenomics | independently validates locus-framework/backbone continuity | sparse within *Cirsium* |
| 2020 | *C. japonicum* transcriptome–metabolome | functional transcriptome | 104,890 unigenes and phenylpropanoid/flavonoid orthologs for later mechanism work | not ancestry/history evidence |
| 2022 | *C. maritimum* MIG-seq Genepop | within-species population genomics | reusable exact species overlap with JPN17 | not the Japan38 voucher; no direct focal-trait linkage |
| 2024 | Korean *C. nipponicum* nuclear genome | reference genome | mapping/orthology/probe resource | not a Japanese radiation tree |
| 2024 | Chinese *Lamyropsis macracantha* ITS/ETS | local nuclear taxonomy | warns against exact-name gap inference | narrow taxonomic scope |
| 2025–2026 | Nipponocirsium / Taiwan–Ryukyu phylotranscriptomics | regional species-tree/network | strongest independent local topology and reticulation sensitivities | incomplete Japan38 coverage |

The evidence ledger is `data/evidence/east_asia_independent_nuclear_evidence_audit_v1.csv`. The full audit narrative is `docs/chapter2/EAST_ASIA_INDEPENDENT_NUCLEAR_EVIDENCE_AUDIT_V1.md`.

The correct framing is: **the accepted Comp1061 tree is the harmonized full-panel scaffold, not the sole nuclear evidence.** Heterogeneous nuclear marker systems are not pooled into a single branch-length analysis.

## Table S9 — Ecological mechanism boundary

| Trait | Existing Chapter 2 result | Mechanisms not identified by current data | Required next evidence |
| --- | --- | --- | --- |
| orientation | stable BIO15/BIO1 correspondence, inference unresolved | rain/wetting, thermal presentation, pollinator presentation | same-individual state/environment data and direct mechanism/fitness measurements |
| phyllary posture | repeated minimum changes; ecology not evaluable | enemy exclusion, wetness protection, pollinator-access cost | broader direct posture coverage plus enemy/wetness/access measurements |
| stickiness | repeated minimum changes; ecology not evaluable | enemy benefit, null effect, pollinator cost, production cost | sticky/nonsticky ancestry-matched measurements and manipulation |

These are Chapter 3 mechanism discriminators, not historical causes inferred by Chapter 2.

## Table S10 — Stop rules and claim boundaries

| Analysis or evidence layer | Frozen decision | Boundary retained in this submission |
| --- | --- | --- |
| absolute transition time | `STOP_NOT_IDENTIFIABLE` | no calendar ages or rates from substitutions/site tree |
| minimum changes | admitted lower bounds | not independent-origin counts or convergence counts |
| relative lineage-depth | admitted topology-only envelopes | not event age or ecological event timing |
| orientation climate correspondence | `unresolved` | stable direction may be reported; not adaptation or repeated ecological convergence |
| predictive comparison | supporting sensitivity only | not required as the primary ecological-reach estimand |
| phyllary ecology | `not_evaluable` | not no relationship |
| stickiness ecology | `not_evaluable` | not no relationship |
| independent nuclear evidence | multi-scale correction layer | does not permit heterogeneous markers to be merged into one tree |
| species-tip colour compression | one morph-linked system plus independent population-genetic precedents | not a general rate/regain result |
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
- `data/evidence/japan38_cytotype_trait_overlap_v1.json`
- `data/evidence/east_asia_independent_nuclear_evidence_audit_v1.csv`

## File and claim audit

- [x] minimum change, relative lineage-depth and ecological reach are reported as distinct estimands;
- [x] ecological correspondence is not made dependent on predictive model competition;
- [x] predictive diagnostics are retained transparently in Supporting Information;
- [x] species LOO and accepted-topology sign stability are explicit;
- [x] raw ecological UFBoot sign rate is marked `not_evaluable` rather than substituted;
- [x] phyllary and stickiness `not_evaluable` states are not reported as zero effects;
- [x] the independent nuclear evidence landscape is distinguished from the harmonized full-panel scaffold;
- [x] pre-2025 Japanese/Korean nuclear resources are not silently omitted;
- [x] functional transcriptomes/reference genomes are not mislabelled as species-tree evidence;
- [x] no minimum step is called an independent origin, convergence or adaptation;
- [x] no substitutions/site branch is called absolute time;
- [x] no present ecological correspondence is called historical causation.
