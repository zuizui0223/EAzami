# Temporal selection-pressure triangulation for capitulum diversity v1

Status date: 2026-08-30

## Decision

The cause of capitulum diversity is evaluated by triangulating six distinct evidence dimensions rather than asking whether Azami and EAzami are both individually significant:

> **repeated history (R) → relative event placement (T) → present spatial gradient (S) → present state–ecology correspondence (C) → dated historical environmental correspondence (P) → trait-to-function-to-fitness evidence (F)**

Azami supplies **S**, the breadth of present-day phenotype sorting along environmental gradients. EAzami currently supplies **R**, **T** and, where coverage permits, **C**. EAzami will supply environmental influence or variability through time only after **P** is estimable from dated transition windows. Current taxon niche centroids are not historical environments and cannot substitute for P.

The machine-readable contract and ledger are:

- `../../data/evidence/chapter2_temporal_selection_pressure_contract_v1.json`;
- `../../data/evidence/chapter2_temporal_selection_pressure_concordance_v1.csv`.

## What counts as stronger explanatory reach

A factor becomes a stronger candidate selective pressure when independent evidence dimensions converge on the same ecological domain:

1. the trait has repeatedly changed rather than merely separating one old clade;
2. the repeated changes can be localized in relative or absolute time;
3. the homologous trait is sorted along a present-day spatial gradient;
4. present states retain a phylogeny-aware niche difference in the same ecological domain;
5. independently dated transition windows align with prespecified environmental changes or high-variability intervals;
6. direct manipulation closes the trait → mechanism → reproductive-fitness path.

No current trait reaches all six levels. Convergence of R, S and C raises a trait to a **space–time selection-pressure candidate**, not to demonstrated adaptation. P and F remain necessary for historical and adaptive explanation.

## Current temporal result

Relative lineage-depth equals one on a terminal edge and decreases for an edge subtending more descendant lineages. It is a topology-only coordinate, not calendar time.

| Trait | Resolved concepts | Minimum changes | Median UFBoot depth envelope | Current relative-time interpretation |
| --- | ---: | ---: | ---: | --- |
| orientation | 20 | ML 6; UFBoot 4–6, median 5 | 0.795–0.994 | mixed internal-to-terminal histories; recurrence is robust but exact timing is diffuse |
| phyllary posture | 10 | exactly 3 on ML and 1,000/1,000 UFBoot | 0.695–1.000 | the broadest admissible temporal span; a relatively early change and terminal reconfiguration can be equally minimal |
| stickiness | 13 | exactly 5 on ML and 1,000/1,000 UFBoot | 0.937–0.954 | shallow and tightly concentrated; three to four terminal plus one to two internal changes on the ML topology |

The three traits therefore do not only differ in the number of required changes. Their admissible temporal geometry differs. Phyllary posture permits the deepest histories, orientation spans internal and terminal alternatives, and stickiness is concentrated near shallow lineage-specific reassembly.

## Orientation — strongest current multi-axis convergence

### R: repeated history

Orientation requires four to six minimum changes across the accepted bootstrap topology ensemble. This rejects a one-split description of the observed states, but does not count independent origins or identify transition direction.

### T: relative event placement

The median exact depth envelope is 0.795–0.994 and no orientation edge is forced on the maximum-likelihood topology. JPN36 is the most frequent named terminal localization but is forced in only 0.227 of bootstrap topologies. The repeated history is therefore stronger than its event localization.

### S: Azami spatial gradient

At the global among-taxon scale, higher annual precipitation amount (BIO12) is associated with a larger signed head-axis angle relative to image vertical:

- standardized coefficient +0.304359;
- global-family q=0.021;
- broad-space coefficient +0.286086, permutation P=0.017;
- direction retained in all 52 historical-placement sensitivities and all applicable sampling-composition perturbations.

This is present-day spatial sorting. The image axis is not a gravity-referenced three-dimensional angle and the result does not measure rain interception.

### C: EAzami present state–ecology correspondence

Downward/nodding taxa occupy present niches with higher precipitation seasonality (BIO15) and lower annual mean temperature (BIO1). In the frozen GBIF-only panel, the BIO15 downward-minus-upward effect is +1.320 to +1.330 SD and the BIO1 effect is −0.975 to −0.967 SD. Both signs persist across all six accepted topologies and all 54 topology × species leave-one-out fits.

Independent Taiwan occurrence-source sensitivities retain both signs. The direct-TBN-native tier crosses the frozen threshold and is `tendency_supported`; the broader non-GBIF-mirror TBN tier returns to `unresolved`. Thus the biological direction is stable while threshold support is niche-centroid/source-definition sensitive.

### Current domain-level concordance

Azami BIO12 and EAzami BIO15 are not the same variable:

- BIO12 measures the spatial gradient in **annual precipitation amount**;
- BIO15 measures **temporal unevenness of precipitation within a year** in present taxon niches.

Their agreement is therefore not coefficient replication. It is **hydric cross-facet concordance**: orientation is independently associated with more than one dimension of rainfall regime. This makes wetting/exposure a stronger candidate domain than it would be from either chapter alone.

BIO1 does not form an equally simple cross-axis match. The Azami orientation result is scale-dependent and a universal “downward = cold” rule is not supported. In East Asia, BIO1 may represent direct thermal conditions, elevation-associated climate, snow/phenology, pollinator turnover or covariance with seasonal precipitation. These alternatives remain open.

### P: historical environmental variability

Not yet evaluable. The active Japan38 scaffold has substitutions-per-site branch lengths and the exact relative lineage-depth envelope does not yield calendar transition windows. Present BIO15/BIO1 niche centroids cannot identify what the climate was when a reconstructed change occurred.

Consequently, the current supported statement is:

> **Orientation is recurrent and its spatial and present ecological associations converge on the hydric domain, making hydric exposure and variability the strongest public-data candidate selective-pressure family. Event-specific Pleistocene correspondence and adaptation remain untested.**

## Phyllary posture — strong history, driver unidentified

Phyllary posture requires exactly three changes across every accepted bootstrap topology and permits the broadest relative-depth envelope, 0.695–1.000. It could therefore include a relatively broad-lineage reorganization as well as terminal changes.

No homologous Azami spatial endpoint currently exists. Projection, taper and roughness are continuous image-geometry measurements; they cannot be equated post hoc with authority-coded ascending, spreading or recurved posture. The frozen climate panel also contains only two evaluable posture taxa and both are ascending.

Candidate pressure domains—wetting protection, reproductive-enemy exclusion, mechanical protection and pollinator-access cost—remain biologically distinct and unresolved. This is an **ontology and overlap gap**, not evidence that phyllary history lacks an environmental cause.

## Stickiness — shallow recurrence, potentially local selection mosaic

Stickiness requires exactly five changes across all 1,000 bootstrap topologies. Its median depth envelope is narrow and shallow, 0.937–0.954. On the maximum-likelihood topology, every minimum reconstruction contains both terminal and internal changes, with three to four terminal and one to two internal changes.

That geometry is compatible with lineage-local reassembly, but it does not identify a driver. There is no calibrated Azami stickiness endpoint, no state-diverse current climate comparison and no historical time series for enemy communities. A local biotic-selection model—reproductive enemies, florivores, associated arthropod communities or production cost—may fit this shallow pattern better than one continental climate gradient, but this remains a hypothesis. Climate non-association would not refute a biotic driver.

## Visible colour — strong spatial factor, temporal depth unresolved

Azami finds a robust among-taxon association between higher shortwave radiation and lower visible CIELAB corolla chroma:

- standardized coefficient −0.345372, q=0.006;
- broad-space coefficient −0.712411, permutation P=0.001;
- direction stable across all 52 historical-placement sensitivities.

However, the Japan38 continuous-history family does not retain corrected two-sided support for lightness, chroma or hue, and no sequenced-individual W/C/P event ontology is admitted. Therefore colour has a strong radiative spatial candidate but no defensible transition count, dated event window or historical radiation correspondence.

This difference has at least two live explanations:

1. visible colour may be evolutionarily labile and repeatedly track local environments, leaving weak phylogenetic structure;
2. the Japan38 time-axis panel may be too sparse or too compressed at the species-tip level to detect that history.

The current data do not distinguish them. Visible JPEG chroma also cannot be translated into anthocyanin concentration, UV patterning or pigment-pathway activity.

## Why spatial and temporal factors may differ without contradiction

A difference between Azami and EAzami is informative only after distinguishing the following causes:

1. **Geographic scale:** Azami compares a broad global sample; EAzami resolves a young East-Asian radiation.
2. **Environmental statistic:** a spatial mean or amount can differ from seasonality, temporal variance, extremes or rate of change.
3. **Present versus historical exposure:** extant niche centroids need not equal ancestral environments at transition time.
4. **Ontology:** image-derived continuous geometry may not be homologous to a botanical state used in reconstruction.
5. **Selective agent:** climate layers cannot represent pollinator, enemy or community turnover directly.
6. **Coverage and power:** absence of temporal support in a small matched panel is not proof of evolutionary lability.
7. **Trait-specific timing:** shallow lineage-local changes may respond to different processes than broad-lineage changes.

Accordingly, the analysis records `unidentified` separately from true directional `discordance`.

## Current explanatory ranking

| Trait | Current convergence | Selective-pressure interpretation |
| --- | --- | --- |
| orientation | R + T + S + C; S and C converge on hydric domain | strongest public-data selection-pressure candidate; historical event and fitness gates open |
| colour | S strong; T/history unresolved | radiative spatial sorting candidate; temporal cause not identified |
| phyllary posture | R + T strong; S/C incomparable | repeated history with driver unidentified |
| stickiness | R + shallow T strong; S/C unavailable | local biotic-selection candidate only; no generic defence promotion |
| outline/architecture | spatial phenotype measured; temporal bridge weak or missing | measurement and coverage frontier |

This is not a ranking of biological importance. It is a ranking of current explanatory closure.

## Next executable public-data test

### Gate 1 — obtain an admitted dated transition map

1. audit whether a published dated *Cirsium* chronogram can be linked by accession or auditable node mapping to the Japan38 concepts;
2. propagate each trait’s minimum-history edge envelope rather than selecting one convenient reconstruction;
3. derive event time windows with topology and dating uncertainty;
4. stop if only a single radiation age is available—relative lineage-depth must not be linearly converted to Ma.

### Gate 2 — freeze factor-specific historical hypotheses

Before inspecting event overlap:

- orientation primary domain: hydric variability/exposure; thermal regime secondary; connectivity only where a geographic split is explicitly represented;
- colour: radiation/optical and temperature hypotheses only after a population-linked colour transition map exists;
- phyllary posture: no climate-first promotion until homologous posture coverage and candidate wetting/enemy/access data are distinguished;
- stickiness: climate is not a substitute for historical enemy/community turnover.

### Gate 3 — test event–environment correspondence

For each trait and factor, compare observed transition-window overlap with a null that preserves:

- the number of changes;
- branch duration and topology uncertainty;
- trait-state coverage;
- the admissible reconstruction envelope.

The result classes are `historical_correspondence_supported`, `unresolved`, or `not_evaluable`. Only a supported P result joined to direct function and fitness evidence can promote a candidate selective pressure toward adaptive explanation.

## Canonical conclusion

> **Capitulum diversity is best approached as the outcome of trait-specific selection mosaics acting at different temporal depths. Orientation currently supplies the strongest triangulation: repeated history, global precipitation-amount sorting and East-Asian precipitation-seasonality correspondence independently converge on a hydric exposure domain. Colour, phyllary posture and stickiness expose complementary open links in the evidence chain. Multiple-domain concordance raises explanatory power, but event-specific historical environment and fitness remain the gates between a plausible selective pressure and demonstrated adaptation.**

## Claim ceiling

Do not infer calendar event ages from relative lineage-depth. Do not treat present niche centroids as ancestral climate. Do not call minimum changes independent origins. Do not convert domain concordance into adaptation, convergence or fitness benefit. `not_evaluable` and `unidentified` are evidence-boundary results, not zero effects.
