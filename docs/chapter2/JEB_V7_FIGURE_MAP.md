# JEB V7 figure map — positive assembly first

Status date: 2026-09-03  
Status: **ACTIVE WORKING MAP FOR V7**

## Paper spine

`diversity within dominant radiation -> repeated component histories -> unequal evolutionary depth / mosaic assembly -> scale-partitioned present ecology -> calendar-time and historical-cause ceiling`

The main figures must follow this order. Historical-trigger failure is the terminal discrimination layer, not the opening biological result.

| Figure | Main question | Primary evidence | Main conclusion | Hard boundary |
| --- | --- | --- | --- | --- |
| Fig. 1 | What diversity is being assembled? | dominant-radiation membership + authority configurations | substantial capitulum diversity occurs within one young radiation | descriptive diversity, not transition history or diversification rate |
| Fig. 2 | How were three components assembled through the radiation? | minimum steps + relative-depth envelopes + shared-localization | repeated changes occupy unequal depths and do not form one synchronized history | no independent origins, rate, adaptation or genetic modularity |
| Fig. 3 | Is present ecological correspondence expressed on one biological scale? | Azami within/among + EAzami state contrasts for orientation | orientation–environment correspondence is scale-partitioned | no pooling of estimands, climate-selection or historical-cause claim |
| Fig. 4 | What can the best-bounded orientation event tell us historically? | 94 chronologies × 4 regions + regional ranking + four BIOCLIM axes | descriptive regional/climate tendencies exist but do not survive the full uncertainty gate | scenario robustness is not posterior probability or ancestral-area inference |
| Fig. 5 | How far does historical identifiability extend? | event-level climate/sea-level decision counts + evidence hierarchy | phenotypic assembly is better identified than one recurring coarse historical cause | no environmental irrelevance; no local land-bridge inference |

# Figure 1 — Diversity within the dominant radiation

## Purpose

Open on the **positive biological problem**, not on palaeoclimate uncertainty.

## Panels

### 1A. Nuclear radiation context

- compact accepted Japan38/Comp1061 scaffold;
- visually identify dominant radiation versus the two current secondary-history concepts;
- annotate `36 / 38 sampled Japanese paper concepts in dominant radiation`;
- keep JPN20/JPN31 admission exceptions in a small provenance note rather than the visual center.

### 1B. Authority-backed configuration matrix

Rows: admitted taxon concepts.  
Columns: orientation, phyllary posture, stickiness.  
Use missing/ambiguous states explicitly rather than imputing.

### 1C. Configuration summary

Show the observed orientation × stickiness combinations within the dominant radiation. If the source ontology and harmonized ontology differ, show both counts in the caption rather than collapsing them silently.

### Optional SI-only inset

Nine-taxon public-image/current-environment disparity can support the statement that within-radiation disparity is substantial, but it should not dominate Fig. 1 because it uses a smaller subset and is not a rate/history test.

## Figure 1 claim

> Multiple capitulum configurations occur within the same dominant young radiation; broad colonization history is therefore not a one-to-one proxy for present capitulum configuration.

# Figure 2 — Repeated mosaic assembly at unequal evolutionary depths

## Purpose

This is the **headline figure**.

## Panels

### 2A. Minimum-change burden

For each trait:

- orientation: ML 6; UFBoot 4–6, median 5;
- phyllary posture: exactly 3;
- stickiness: exactly 5.

Plot the UFBoot distribution, not just three isolated point values.

Add a caption sentence that `minimum changes are lower bounds, not independent origins or rates`.

### 2B. Relative lineage-depth envelopes

Display ML plus UFBoot exact lower/upper envelopes from `japan38_relative_event_depth_v1.json`.

Frozen UFBoot median envelopes:

- orientation: 0.795–0.994;
- phyllary: 0.695–1.000;
- stickiness: 0.937–0.954.

Axis label must be:

`relative lineage depth (1 = terminal; topology only, not time)`

### 2C. Paired-topology ordering

Source: PR #160 only after pinned Python 3.11 / Biopython 1.85 validation succeeds.

Show topology-wise pairwise ordering fractions rather than a regression. The panel should visually answer whether the same bootstrap topology tends to retain:

`phyllary deeper-permissive -> orientation intermediate -> stickiness shallow`.

Until #160 is validated, keep the panel frame/place-holder in figure code but do not render provisional fractions in the submission figure.

### 2D. Shared-transition localization

Compact 3-pair matrix:

- orientation × phyllary;
- orientation × stickiness;
- phyllary × stickiness.

Headline: `0 / 3 trait pairs pass the robust shared-transition-localization rule`.

Do **not** use this panel to claim developmental/genetic independence.

### Figure 2 side note: turnover burden audit

Do not say `same lability, different depth`.

Simple descriptive ML steps/resolved concepts are:

- orientation 6/20 = 0.300;
- phyllary 3/10 = 0.300;
- stickiness 5/13 = 0.385.

Because state ontologies differ, these are not commensurable rates. The allowed inference is:

> Depth stratification is not explained away by a trivial coverage-adjusted minimum-change count; equal lability is not established.

## Figure 2 claim

> Three capitulum components changed repeatedly but occupy unequal relative depths and do not repeatedly share one synchronized transition history.

# Figure 3 — Orientation ecology is scale-partitioned

## Purpose

Restore present ecology without letting it take over the historical paper.

## Design

Three rows = BIO12, BIO15, BIO1.  
Three evidence columns = Azami within-taxon, Azami among-taxon, EAzami East-Asian state contrast.

Use effect direction and support status, not a single pooled coefficient.

### BIO12 annual precipitation

- within: beta +0.00533, q=0.874 — unsupported;
- among: beta +0.30436, q=0.00640 — supported;
- class: `among_only`.

### BIO15 precipitation seasonality

- within: beta −0.00762, q=0.121 — not FDR-supported;
- among: beta +0.0670, q=0.599 — unsupported;
- East-Asian D−U: +1.320 to +1.330 SD;
- sign stable 6/6 accepted topologies and 54/54 topology × species-LOO fits;
- class: `lineage_state_difference_not_mirrored_by_within_taxon_response`.

### BIO1 annual mean temperature

- within: beta +0.01715, q=0.0349 — supported;
- among: beta −0.03024, q=0.836 — unsupported;
- East-Asian D−U: approximately −0.975 to −0.967 SD, 54/54 sign stable;
- class: `within_only_in_azami_with_opposite_east_asian_state_direction`.

## Display rule

A dot/arrow matrix is preferable to three conventional significance plots because the estimands differ and are not pooled.

Do not plot `depth × ecological reach` across the three discrete traits. PR #162 shows that phyllary remains state-degenerate in the frozen environment panel and stickiness is lineage-confounded when the gate is relaxed. A three-point cross-trait regression would manufacture an estimand that is not identified.

## Figure 3 claim

> Present orientation–environment correspondence is organized, but the relevant biological scale changes among environmental axes.

# Figure 4 — Bounded orientation history: tendency versus uncertainty

## Purpose

Show why a coherent historical story can be biologically useful yet remain below the final claim threshold.

## Panels

### 4A. Event chronology gate

Show the core-*Nipponocirsium* topology bridge:

`erect/upward C. morii side -> bounded stem -> nodding/downward core`.

Central chronology: 0.79–0.74 Ma.  
Full admissible chronology set: 94 parent–child pairs.  
Four palaeolocation scenarios: Taiwan, Ryukyu corridor, southern Japan, East-Asian core.  
Total: 376 scenarios.

### 4B. Regional ordering

Within each exact chronology pair, rank the four regional state–trajectory cosines.

Frozen result:

- southern Japan rank 1: 48/94 = 0.511;
- southern Japan > Taiwan: 61/94 = 0.649;
- southern Japan > Ryukyu: 61/94 = 0.649;
- southern Japan > East-Asian core: 64/94 = 0.681.

Show the frozen 75% dominance gate visibly. Label these values `scenario-wise ranking robustness`, never probability.

### 4C. Central climate trajectory

At 0.79–0.74 Ma:

- BIO1 decreases in all four regions;
- BIO4 decreases in all four;
- BIO15 decreases in all four;
- BIO12 increases in three of four.

This panel is explicitly descriptive.

### 4D. Full-envelope decision

For BIO1/BIO4/BIO12/BIO15 show that signed direction, environmental level, absolute change and temporal variability do not survive the complete chronology × palaeolocation gate.

The visual contrast should be `coherent central story` versus `uncertainty envelope crosses decision boundary`.

## Figure 4 claim

> The best-bounded event contains regional and climatic tendencies, but they are not robust to the admitted chronology and palaeolocation uncertainty.

# Figure 5 — Historical identifiability ceiling

## Purpose

End the paper on an **information hierarchy**, not a wall of null results.

## Panels

### 5A. Evidence funnel

Suggested ordered tiers:

1. configuration diversity — resolved;
2. repeated minimum history — resolved for 3 traits;
3. relative depth — resolved as exact envelopes;
4. shared named/localized history — partial/weak;
5. calendar-linked trait events — sparse (one current full-chain orientation event);
6. recurring historical cause — unresolved/not identified.

### 5B. Broader climate diagnostic

- 17 BIOCLIM;
- six dated lineage contexts;
- 15,472 scenario × variable combinations;
- robust event-level classes: **0/324**.

### 5C. Global sea-level diagnostic

- three representative clades;
- seven metrics;
- robust event-metric classes: **0/21**.

### 5D. Final interpretation box

Use positive wording:

> `phenotypic assembly is identifiable farther than recurring historical cause`

Do not write `environment does not matter`.

## Figure 5 claim

> Public data resolve repeated mosaic assembly and unequal evolutionary depth much more strongly than one recurring coarse historical cause.

# Supporting / companion routing

## Supporting Information, not main figures

### Occurrence-gate resolution audit — PR #162

- n≥10 makes both phyllary and stickiness state-degenerate in the frozen niche panel;
- n≥5 restores stickiness state diversity only through one sticky lineage;
- lowering the gate does not restore phyllary state diversity;
- broader environment-free public occurrence support contains phyllary ascending/appressed and balanced 6/6 sticky/nonsticky panels.

Use this to explain `not_evaluable`; do not convert the single-lineage climate contrast into a trait effect.

### White-coloured sister-system bridge

Keep repeated colour + geometry directions as Supporting/Discussion context, not as a fourth discrete historical module.

### Named-edge resolution / inverse sampling design

Move the former V4 main-figure material on forced edges and sampling priorities to SI or Chapter 3 planning.

## Companion mechanism evidence — PR #163

- focal *C. brevicaule* antagonist exposure;
- Japanese phenology/geography-structured antagonist regime;
- *C. purpuratum* display × predispersal seed-predation trade-off;
- 2026 recruitment-context observation;
- experimental RR=2.674 retained as pathway-level magnitude anchor, not an East-Asian measured effect.

This belongs in Discussion/SI as `MECHANISTIC_PRIOR`, not in the focal historical-cause chain.

# Final display gates

1. No panel may convert minimum changes into independent origins or convergence.
2. No relative-depth axis may be labelled Ma, old/recent, rate or probability.
3. No UFBoot fraction may be called a posterior probability or independent replicate frequency.
4. No within/among/East-Asian ecological estimands may be pooled.
5. No three-trait `depth × ecological reach` correlation is allowed under current coverage.
6. No regional scenario fraction may be called an ancestral-area probability.
7. No global sea-level panel may imply local land connectivity.
8. `0/324` and `0/21` constrain the tested coarse historical regimes; they do not demonstrate environmental irrelevance.
9. PR #160 paired-ordering numbers enter Fig. 2 only after the pinned-runtime CI completes.
10. Main-paper visual emphasis must remain on assembly history; mechanism priors and resolution audits stay supporting/companion.
