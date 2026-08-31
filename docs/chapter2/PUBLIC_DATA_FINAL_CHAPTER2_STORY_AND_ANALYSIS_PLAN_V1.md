# Chapter 2 public-data final story and analysis plan v1

Status: 2026-08-31

## One-sentence chapter question

> **How deep is capitulum diversity in evolutionary time, what geographic/environmental processes accompanied repeated trait changes, and when do those historical drivers agree with the present environmental gradients recovered by Azami?**

Chapter 2 is the final public-data chapter before focal own-sample mechanism/fitness tests in Chapter 3. It should use public data to the explanatory ceiling without calling observational concordance adaptation.

## Core story

Chapter 1 (Azami) establishes **breadth across present environmental state space**. Chapter 2 (EAzami) establishes **depth through repeated evolutionary history and environmental trajectory space**. The bridge is not duplicated significance testing. The bridge asks whether the environmental direction associated with present phenotypic sorting is also recovered around the historical transitions that assembled the same phenotype.

The ordered evidence chain is:

1. **How many times?** Reconstruct minimum repeated trait changes and propagate topology uncertainty.
2. **When?** Convert only those transitions with public dated anchors to bounded parent–child calendar windows; retain relative-depth summaries for the full Japan38 history.
3. **Where/how did lineages move?** Reconstruct or bound dispersal/colonization/fragmentation context and paleolocation uncertainty rather than assigning modern descendant coordinates to ancestral branches.
4. **What environmental trajectory accompanied the transition?** Measure environmental level, direction, volatility and extremes through each admissible window and compare with duration-/opportunity-matched non-event windows.
5. **Does the historical trajectory agree with Azami?** Compare the EAzami transition trajectory with the frozen Azami present-day trait–environment vector/domain.
6. **How strong is the cause candidate?** Promote only drivers that converge across independent evidence layers; retain discordance as evidence for origin–maintenance decoupling or driver switching.

## What is already resolved

### Repeated history

- orientation: ML minimum 6; UFBoot minimum 4–6; mixed internal-to-terminal placement.
- phyllary posture: exactly 3 minimum changes across all 1000 UFBoot trees; deeper placements remain admissible.
- stickiness: exactly 5 minimum changes across all 1000 UFBoot trees; strongly shallow/terminal-biased.
- continuous colour/outline: no corrected primary phylogenetic-structure support at current Japan coverage; this is unresolved rather than proof of no history.

### Present-space bridge from Azami

Azami uses nine frozen environmental predictors grouped as thermal (BIO1/BIO4), hydric (BIO12/BIO15), radiative-atmospheric (RSDS/VPD), mechanical (wind), growing-season water input (GSP) and productivity (NPP). The two strongest final among-taxon candidates are:

- orientation ~ BIO12: positive, robust to broad-space and historical-placement sensitivity;
- visible corolla chroma ~ RSDS: negative, robust to broad-space and historical-placement sensitivity.

### Present EAzami ecology

For orientation, downward/nodding states occupy higher BIO15 and lower BIO1 present niches with sign stability across accepted topologies and species LOO, while threshold support is source-sensitive. Phyllary and stickiness remain not evaluable with the frozen climate overlap.

## Public-data chronology strategy

The full Japan38 machine-readable chronogram is not currently public. Therefore the chapter uses a two-level chronology rather than inventing dates.

### Level A — full history, relative time

Use the Japan38 substitutions/site topology ensemble for minimum-change recurrence and topology-derived relative event depth. Do not convert relative depth to Ma.

### Level B — local exact public dated sensitivities

Use published node-age scaffolds only where taxon/clade reconciliation is explicit. A deterministic minimum-history enumerator now identifies three public branch-bounded trait events on the six-taxon East-Asian scaffold:

1. **ORI_TAIWAN_TRIO_STEM** — orientation U→D forced on the 0.79–0.47 Ma Nipponocirsium lineage in all three frozen topology variants and all minimum histories.
2. **COL_BREVICAULE_TERMINAL** — coloured→white forced on the C. brevicaule terminal lineage; admissible branch window 0–0.93 Ma.
3. **COL_KAWAKAMII_TERMINAL** — coloured→white forced on the C. kawakamii terminal lineage; topology-union branch window 0–0.47 Ma.

These are conditional on the six-taxon public state coding and minimum-change criterion. They do not replace the unresolved Japan38 colour history and they do not identify exact transition instants.

## Event-by-process registry

`data/evidence/chapter2_public_event_process_registry_v1.csv` separates **trait events** from **biogeographic exposure opportunities**. In addition to the three dated trait events, the registry retains:

- the dominant Japanese founder radiation (~2.4 Ma; 1.7–3.6 Ma) as a radiation/exposure context;
- the separate C. dipsacolepis jump to Japan (~1.0 Ma; 0.4–2.2 Ma) as a process natural experiment on a lineage with a terminal relative stickiness change, without equating jump time and trait-change time;
- the C. lineare East-Asia→Japan expansion (~1.4 Ma; 0.7–2.7 Ma) as the sticky comparator process context;
- the Sinocirsium Japan–Taiwan split (~0.44 Ma; 0.31–0.66 Ma) as a distribution-history event for which species-tip colour transitions are explicitly not identifiable;
- the late-Pleistocene/Holocene var. takaoense demographic contraction–expansion as a published range-history process, not a colour-origin event.

This prevents the common error `range event = selective cause = trait transition`.

## Environmental trajectory design

Do not perform an all-BIOCLIM fishing screen. Use mechanism- and cross-axis-defined families.

### Shared Azami × EAzami state–trajectory core

Use BIO1, BIO4, BIO12 and BIO15 because these variables are directly shared by the frozen Azami atlas and PALEO-PGEM. For each dated event window estimate:

- event-window mean;
- young-minus-old directional change;
- absolute net change;
- temporal SD and range;
- mean/max absolute 1-kyr change;
- cellwise sign agreement across the paleolocation uncertainty set;
- regional spatial IQR / temporal SD;
- percentile relative to all same-duration background windows.

Then compare the frozen Azami standardized slope vector β_space with the background-standardized historical environmental change vector ΔE_time using cosine similarity. This is the primary state–trajectory concordance statistic.

### Orientation wetting-mechanism refinement

Use BIO13/BIO16 (wettest month/quarter precipitation) as wet-side proxies and BIO14/BIO17 as dry-side controls. A rain/wetting interpretation becomes more specific only if wet-side dynamics are more exceptional than dry-side dynamics under the same null and are robust across plausible Taiwan cells.

### Distribution-process environment layer

Treat geographic reorganization separately from climatic selection. Public process data include stochastic biogeographic reconstructions for Japan, published historical SDMs/EBSP for Taiwanese Sinocirsium, and independent Quaternary land/sea-connectivity evidence. These layers can test whether a lineage entered or fragmented across a new exposure regime, but cannot by themselves identify the selective agent.

### Secondary climate analyses

BIO5/6/7 and BIO8–11 may describe thermal extremes/seasonal regimes after the primary families. BIO18/19 are not flowering-season rainfall without a phenology layer.

### Do not force false equivalents

RSDS, VPD, wind, GSP and NPP have no directly commensurate PALEO-PGEM time series. They require separate historical models and must not be presented as direct Azami–EAzami replication.

## Current local orientation result and what it means

The public Taiwan 0.79–0.47 Ma U→D sensitivity already rejects a simple assumption that present sorting identifies the transition driver:

- BIO12 increases through the branch, but its change/variability is not exceptional among same-duration 5-Myr windows;
- BIO15 absolute net change is relatively large (~92.7th percentile) but the regional median changes toward **lower** seasonality, opposite the present D-high BIO15 niche direction, and cellwise signs are mixed;
- BIO1 moves toward warming, opposite the present D-cooler niche direction, although the cellwise warming sign is robust;
- the four-dimensional Azami-state vs historical-trajectory cosine is ~0.059 with a ~0.518 null percentile, i.e. no unusual multivariate directional concordance;
- wet-side BIO13/BIO16 do not outperform dry-side BIO14/BIO17 controls (wet-minus-dry contrast ~0.60 null percentile).

Therefore this local event currently supports **no simple persistent-driver historical hydric alignment**. This does not erase the strong present orientation–hydric correspondence. It motivates the distinction between transition origin and present sorting/maintenance.

## Colour becomes a two-level result, not a missing-data footnote

Public data now support two distinct statements that must remain separate:

1. On the six-taxon dated scaffold, minimum-history reconstruction permits two topology-robust branch-bounded coloured→white events (C. brevicaule and C. kawakamii).
2. In the Taiwanese C. japonicum complex, published phylotranscriptomic work shows white/bluish-purple polymorphism within var. takaoense and colour variation in var. fukienense, with reticulate signal; therefore species-tip colour coding would erase real within-lineage variation.

This explains why the strong Azami RSDS–chroma spatial pattern cannot simply be translated into a species-level deep-time colour transition test. The public-data ceiling itself predicts the Chapter 3 sampling unit: population/individual-level colour state linked to ancestry and environment.

## Three competing process models

### ST1 — persistent driver

The same environmental domain drives transition and present sorting. Prediction: transition windows move along the Azami-predicted environmental direction more strongly than matched non-event windows and show consistent paleolocation signs.

### ST2 — origin–maintenance decoupling

Current environment sorts/maintains the phenotype, but the historical transition occurred under a different or nondirectional environmental trajectory. Prediction: strong present association plus typical/opposite transition trajectories.

### ST3 — driver switching / selection mosaic

Different transitions arrive at similar phenotypes through different environmental or biotic routes. Prediction: different dated events align with different environmental domains; no universal synchronized capitulum history is required.

## Distribution-history process layer

To answer “what happened during range history?”, integrate public biogeographic evidence before environmental interpretation:

1. classify each usable dated event by biogeographic context: dominant Japanese radiation, secondary arrival, Taiwan/East-Asian within-region diversification, island/continental fragmentation where explicitly supported;
2. retain ancestral-area probability/scenario sets when available; otherwise use bounded regional scenario sets rather than point paleolocations;
3. test whether transitions cluster around colonization/fragmentation opportunities only when event and lineage dates are independently bounded;
4. separate **dispersal/fragmentation opportunity** from **environmental selective trajectory**. Range change can create the exposure opportunity without being the selective agent itself.

This makes “distribution change triggered trait change” a testable two-step model:

`range reorganization → new environmental/biotic exposure → trait transition`,

rather than equating dispersal timing with causation.

## Trait-by-trait public-data ceiling

### Orientation

Highest-priority public-data trait. Full recurrence (4–6), one current public dated event window, present Azami BIO12 sorting, present EAzami BIO15/BIO1 ecology, PALEO-PGEM trajectory tests, and mechanism literature all exist. Continue dated-event recovery and phenology refinement.

### Colour

Azami spatial evidence is strong for RSDS–chroma. The dated six-taxon scaffold now supplies two local branch-bounded coloured→white minimum-history events, but their terminal windows are broad and no directly equivalent historical surface-RSDS series is available. More importantly, the public Sinocirsium data show lineage-level colour polymorphism/reticulation, so a single species-tip W/C ontology is biologically inadequate for that complex. Public data can therefore establish local repeated colour history plus a population-level identifiability boundary, but not a general historical solar-selection test.

### Phyllary posture

History is strong (3 repeated changes), but Azami image geometry is not homologous to authority-coded posture and present ecology is not evaluable. Priority is public botanical calibration/homologous posture coverage and range-history context. Driver remains unidentified rather than discordant.

### Stickiness

History is strong and shallow (5 changes), while public generic-defence evidence is mixed/null and no historical enemy series exists. The C. dipsacolepis and C. lineare biogeographic histories provide a useful process contrast, but dispersal ages cannot be assigned as stickiness-transition ages. Use climate only as a negative/alternative explanation, not as a proxy for enemy pressure. The public-data ceiling may be “rapid lineage-specific reassembly with unresolved/possibly biotic driver.”

### Outline/architecture

Present breadth is measurable, but matched time-axis coverage and functional mapping are insufficient. Keep as diversity-depth boundaries rather than manufacture BM/OU results from sparse data.

## Model hierarchy

BM/OU are secondary baselines, not the chapter question.

- continuous traits: use BM/OU/environment-dependent continuous models only after adequate matched coverage and a valid continuous history estimand exist;
- discrete traits: prefer event/transition analyses because the question is whether environmental trajectory changes the opportunity/risk of state transition;
- for multiple dated events, compare constant transition opportunity against environment-dependent transition hazard or matched-event case-control models while propagating branch duration, topology, age and paleolocation uncertainty.

No model is promoted simply because it has lower AIC; the biological interpretation must remain tied to the space–time evidence ladder.

## Public-data analyses still worth completing before Chapter 3

### P1 — Exhaust dated-event recovery

Continue searching public literature/supplements/raw sequence panels for additional exactly reconciled dated orientation/phyllary/stickiness/colour subclades. The first implementation now yields one orientation and two colour branch-bounded events.

### P2 — Build event-by-process registry

Implemented in `data/evidence/chapter2_public_event_process_registry_v1.csv`; continue adding only source-reconciled rows. Every row separates trait-event certainty from range-process certainty.

### P3 — Run state–trajectory tests across all dated events

Orientation is implemented. Colour can receive climate/control trajectory summaries but cannot receive a direct RSDS replication unless a defensible historical radiative layer is added and clearly labelled non-equivalent to surface RSDS.

### P4 — Test origin–maintenance concordance across events

Ask whether Azami-predicted environmental direction is enriched among transition trajectories. A consistent positive pattern supports ST1; heterogeneous directions support ST3; systematic current-vs-history discordance supports ST2.

### P5 — Add public phenology where defensible

Recover taxon-level flowering months from authoritative/public floras. Where event lineage phenology can be bounded, derive monthly/anthesis-window palaeoclimate rather than relying only on annual BIOCLIM. This is especially valuable for orientation because rain-on-reproductive-structures is season-specific.

### P6 — Distribution-trigger analysis

Use public biogeographic reconstructions, historical SDMs/demography and sea-level/land-connectivity histories to classify whether trait events followed colonization, fragmentation or within-region diversification. Test “range change opens a new selective environment” rather than treating range change itself as selection.

### P7 — Negative-control and falsification analyses

Retain dry-side controls for wetting, thermal alternatives for hydric models, non-event matched windows, alternative paleolocation cells/scenarios and topology/minimum-history envelopes. A cause candidate is strong only when it survives these alternatives.

## Final Chapter 2 result classes

Each trait × driver ends in one of five classes:

1. **multi-layer concordant candidate** — recurrence + dated event + historical trajectory + present Azami/Eazami direction converge;
2. **present sorting / historical origin decoupled** — current ecological pattern is strong but transition trajectory does not match;
3. **driver switching / heterogeneous events** — different events support different domains;
4. **history resolved, cause unidentified** — recurrence/timing are known but comparable driver data are absent;
5. **not evaluable at public-data resolution** — chronology, phenotype homology, paleolocation or environmental resolution is insufficient.

These are explanatory outcomes, not success/failure filters.

## Chapter 2 endpoint and Chapter 3 handoff

Chapter 2 should end with a ranked causal-candidate map, not a causal claim. For each trait it states:

- how many changes are required;
- how deep/when they occurred at the strongest public resolution;
- which range-history context surrounded them;
- which environmental trajectory dimensions were compatible, incompatible or unresolved;
- whether the same driver appears in Azami present-space sorting;
- what exact mechanism/fitness test remains.

Chapter 3 then uses own samples to test the missing causal links: calibrated phenotype → environmental exposure → mediator/function → reproductive fitness, prioritizing the public-data candidates that achieved the strongest multi-layer convergence and the discordances that most sharply separate competing mechanisms.
