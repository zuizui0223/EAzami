# Chapter 2 public-data final story and analysis plan v1

Status: 2026-08-31

## One-sentence chapter question

> **How deep is capitulum diversity in evolutionary time, what geographic/environmental processes accompanied repeated trait changes, and when do those historical drivers agree with the present environmental gradients recovered by Azami?**

Chapter 2 is the final public-data chapter before focal own-sample mechanism/fitness tests in Chapter 3. It should use public data to the explanatory ceiling without calling observational concordance adaptation.

## Core story

Chapter 1 (Azami) establishes **breadth across present environmental state space**. Chapter 2 (EAzami) establishes **depth through repeated evolutionary history and environmental trajectory space**. The bridge is not duplicated significance testing. The bridge asks whether the environmental direction associated with present phenotypic sorting is also recovered around the historical transitions that assembled the same phenotype.

The ordered evidence chain is:

1. **How many times?** Reconstruct minimum repeated trait changes and propagate topology/taxon-sampling uncertainty.
2. **When?** Convert only transitions with public dated anchors to bounded calendar constraints; retain relative-depth summaries for the full Japan38 history.
3. **Where/how did lineages move?** Reconstruct or bound dispersal/colonization/fragmentation context and paleolocation uncertainty rather than assigning modern descendant coordinates to ancestral branches.
4. **What environmental trajectory accompanied the transition?** Measure environmental level, direction, volatility and extremes through admissible windows and compare with duration-/opportunity-matched backgrounds.
5. **Does the historical trajectory agree with Azami?** Compare transition trajectory with the frozen Azami present-day trait–environment vector/domain only when chronology and location refer to the same event.
6. **How strong is the cause candidate?** Promote only drivers that converge across independent evidence layers; retain discordance and non-identifiability as biological results.

## What is already resolved

### Repeated history

- orientation: ML minimum 6; UFBoot minimum 4–6; mixed internal-to-terminal placement on Japan38.
- phyllary posture: exactly 3 minimum changes across all 1000 UFBoot trees; deeper placements remain admissible.
- stickiness: exactly 5 minimum changes across all 1000 UFBoot trees; strongly shallow/terminal-biased.
- continuous colour/outline: no corrected primary phylogenetic-structure support at current Japan coverage; unresolved rather than proof of no history.

### Present-space bridge from Azami

Azami uses nine frozen environmental predictors grouped as thermal (BIO1/BIO4), hydric (BIO12/BIO15), radiative-atmospheric (RSDS/VPD), mechanical (wind), growing-season water input (GSP) and productivity (NPP). The two strongest final among-taxon candidates are:

- orientation ~ BIO12: positive, robust to broad-space and historical-placement sensitivity;
- visible corolla chroma ~ RSDS: negative, robust to broad-space and historical-placement sensitivity.

### Present EAzami ecology

For orientation, downward/nodding states occupy higher BIO15 and lower BIO1 present niches with sign stability across accepted topologies and species LOO, while threshold support is source-sensitive. Present niche is not assumed to reconstruct the environment of trait origin.

## Public-data chronology strategy

The full Japan38 machine-readable chronogram is not public. Chapter 2 therefore combines relative full-history depth with public local/cross-study chronology constraints.

### Level A — full history, relative time

Use the Japan38 substitutions/site topology ensemble for minimum-change recurrence and topology-derived relative event depth. Do not convert relative depth to Ma.

### Level B1 — restricted six-taxon dated sensitivity

The six-taxon East-Asian scaffold contains erect C. morii and three nodding Taiwan core Nipponocirsium. Conditional on that restricted taxon set, one U→D minimum change is forced on the 0.79–0.47 Ma Taiwan-trio stem. This was useful for testing the analysis machinery and descendant-lineage Taiwan palaeoclimate, but it is **not robust to adding the public Japanese core Nipponocirsium taxa**.

### Level B2 — cross-study chronology refinement

Chang et al. 2026 places erect C. morii at the base of subsect. Nipponocirsium with a central split age of ~0.79 Ma (95% HPD 0.43–1.18). Chang et al. 2025 shows Japanese core Nipponocirsium and Taiwan core Nipponocirsium as nodding and dates their split to ~0.74 Ma (95% CI 0.60–0.87). Reconciliation therefore moves the parsimonious U→D transition deeper, onto the core-Nipponocirsium stem after C. morii and before the Japanese–Taiwan core split.

Central estimates suggest 0.79–0.74 Ma, but these ages come from separate analyses and their marginal uncertainty intervals overlap. **0.74–0.79 Ma is therefore a cross-study central-age sensitivity, not a joint posterior event interval.** The ancestral geographic setting before the Japanese–Taiwan split is unresolved, so a direct event-level palaeoclimate cause test is currently not evaluable from public data.

This refinement is scientifically important: adding public taxa changes the inferred geographic setting of origin. It demonstrates why current descendant geography cannot safely be substituted for transition geography.

## Public dated colour events

A deterministic minimum-history enumerator on the six-taxon dated scaffold identifies two conditional local coloured→white events:

1. C. brevicaule terminal lineage: 0–0.93 Ma branch envelope.
2. C. kawakamii terminal lineage: topology-union 0–0.47 Ma branch envelope.

These are branch-bounded minimum-history events, not exact transition dates and not a replacement for the unresolved Japan38 colour history.

In the Taiwanese C. japonicum complex, public phylotranscriptomic data show within-lineage white/bluish-purple polymorphism and reticulation. Species-tip colour coding would erase real population variation. Thus public data themselves define the Chapter 3 sampling requirement: link individual/population colour state to ancestry and environment.

## Event-by-process registry

`data/evidence/chapter2_public_event_process_registry_v1.csv` separates trait events from geographic exposure opportunities. It contains:

- restricted-tree and cross-study orientation chronology rows;
- two local dated colour-history rows;
- the dominant Japanese founder radiation (~2.4 Ma; 1.7–3.6 Ma) as an exposure/radiation context;
- C. dipsacolepis separate arrival (~1.0 Ma; 0.4–2.2 Ma) and C. lineare East-Asia→Japan expansion as process contrasts for stickiness, without assigning those range dates to trait changes;
- Sinocirsium Japan–Taiwan divergence and var. takaoense late-Pleistocene/Holocene demographic history as distribution processes without manufactured colour-origin events.

The intended process model is:

`range reorganization → altered environmental/biotic exposure → trait transition`,

not `range change = selective pressure`.

## Environmental trajectory design

Do not perform an all-BIOCLIM fishing screen. Use mechanism- and cross-axis-defined families.

### Shared Azami × EAzami state–trajectory core

BIO1, BIO4, BIO12 and BIO15 are directly shared by the frozen Azami atlas and PALEO-PGEM. For a defensibly located dated event estimate:

- state level;
- directional change;
- absolute change;
- temporal SD/range;
- mean/max 1-kyr change;
- paleolocation cellwise sign agreement;
- regional spatial uncertainty / temporal variation;
- duration-matched percentile.

The multivariate summary is cosine similarity between frozen Azami β_space and background-standardized ΔE_time.

### What the restricted Taiwan analysis actually showed

On the restricted 0.79–0.47 Ma Taiwan-trio placement:

- BIO12 increased but its change/variability was not exceptional;
- BIO15 absolute change was relatively large (~92.7th percentile) but moved toward lower seasonality, opposite the present D-high BIO15 niche direction, with mixed cellwise signs;
- BIO1 moved toward warming, opposite the present D-cooler niche direction;
- the BIO1/BIO4/BIO12/BIO15 state–trajectory cosine was ~0.059 with null percentile ~0.518;
- wet-side BIO13/BIO16 did not outperform dry-side BIO14/BIO17 controls (~0.60 null percentile).

These results remain valid **for the restricted-tree Taiwan descendant-lineage sensitivity**, but after the Japanese-core chronology audit they cannot be promoted as the environment of the actual orientation origin.

### Anthesis-window sensitivity

Public current phenology for the three Taiwan nodding descendants gives C. pengii Aug–Nov, C. kawakamii Sep–Oct and C. tatakaense Aug–Oct. Sep–Oct is the shared descendant window and Aug–Nov the union envelope. Monthly PALEO-PGEM precipitation is used as a mechanism-oriented sensitivity, not ancestral phenology reconstruction. Because the actual transition is likely deeper than the Taiwan-trio stem, this analysis evaluates whether the descendant lineage's reproductive-season climate is compatible with the present rain-exposure mechanism, not the origin event itself.

### Sea-level process sensitivity

The NOAA Spratt–Lisiecki 0–798 ka global sea-level stack provides a separate range-reorganization context. In the restricted 0.79–0.47 Ma window, sea-level temporal SD was only ~1.35th percentile and range ~9.1th percentile among same-duration windows. Thus this interval was not unusually volatile in global sea level. This weakens a simple 'exceptionally strong sea-level oscillation triggered this local transition' story, while local connectivity remains unresolved without a geological/bathymetric threshold.

### Do not force false historical equivalents

RSDS, VPD, wind, GSP and NPP have no directly commensurate PALEO-PGEM time series. Historical orbital/solar forcing or vegetation models may be added only as explicitly separate model layers; they cannot be called replication of Azami surface RSDS/NPP.

## Three competing process models

### ST1 — persistent driver

The same environmental domain contributes to historical transition and present sorting. Requires defensible event chronology, paleolocation and same-direction historical exposure beyond matched backgrounds.

### ST2 — origin–maintenance decoupling

Current environment sorts/maintains the phenotype, but historical origin is associated with a different, typical or opposite trajectory.

### ST3 — driver switching / selection mosaic

Different transitions arrive at similar phenotypes through different environmental or biotic routes.

At present, the public orientation record is **not yet sufficient to choose ST1 vs ST2/ST3**, because the chronology can be refined but the actual pre-Japan/Taiwan transition paleolocation is unresolved. The restricted Taiwan result is evidence against a naive present-niche-equals-origin assumption, not proof of ST2.

## Trait-by-trait public-data ceiling

### Orientation

Strongest trait for evolutionary depth: 4–6 repeats on Japan38; erect C. morii plus nodding core Nipponocirsium narrows the likely transition placement in a cross-study reconciliation; Azami BIO12 and EAzami current BIO15/BIO1 provide a strong present hydric bridge. Public data now reveal that **taxon sampling and paleolocation, not climate-series availability, are the main barriers to historical causal attribution**.

### Colour

Azami RSDS–chroma is strong. Public dated scaffold gives two conditional local C→W events, but no directly equivalent historical surface-RSDS series and terminal windows are broad. Sinocirsium colour polymorphism/reticulation shows why population-level ancestry-linked sampling is necessary.

### Phyllary posture

History is strong (3 repeated changes), but Azami image geometry is not homologous to authority-coded posture and comparable ecology is insufficient. Driver remains unidentified.

### Stickiness

History is strong and shallow (5 changes), generic defence evidence is mixed/null, and no historical enemy series exists. C. dipsacolepis/C. lineare range histories are useful process contrasts but cannot date the stickiness transition.

### Outline/architecture

Present breadth is measurable, but matched time-axis coverage and functional mapping are insufficient. Keep as a public-data boundary rather than manufacture BM/OU conclusions.

## Model hierarchy

BM/OU are secondary baselines, not the chapter question. Use continuous evolutionary models only when adequate matched continuous trait coverage exists. For discrete traits, event/transition models are more aligned with the question. Environment-dependent transition hazard becomes appropriate only after multiple dated and geographically resolved events are available.

## Remaining public-data execution before Chapter 3

1. **P1 dated-event audit:** continue only source-reconciled additions; record when adding taxa changes event placement.
2. **P2 event-by-process registry:** implemented and now distinguishes restricted-tree, cross-study refinement and range-process rows.
3. **P3 environmental trajectory:** retain Taiwan restricted sensitivity; do not promote it to origin-level T3 after chronology refinement.
4. **P4 state–trajectory concordance:** run only on events with commensurate chronology+paleolocation; otherwise classify not evaluable.
5. **P5 phenology:** use public flowering months to improve mechanism exposure, explicitly as descendant/current phenology sensitivity.
6. **P6 distribution trigger:** use sea-level/biogeographic evidence as exposure opportunity, requiring local geological thresholds before connectivity claims.
7. **P7 falsification:** preserve negative controls, taxon-addition sensitivity, paleolocation scenarios and topology/age uncertainty.

## Final Chapter 2 result classes

Each trait × driver ends as one of:

1. multi-layer concordant candidate;
2. present sorting / historical origin decoupled;
3. driver switching / heterogeneous events;
4. history resolved, cause unidentified;
5. not evaluable at public-data resolution.

Taxon-sampling-sensitive event placement is itself reported as a sixth diagnostic flag rather than hidden.

## Chapter 2 endpoint and Chapter 3 handoff

Chapter 2 ends with a ranked causal-candidate map and an identifiability map. For each trait it states:

- recurrence/depth;
- strongest defensible timing;
- range-history context;
- what environmental trajectory is actually identifiable;
- whether Azami present-space evidence is concordant, discordant or not yet comparable;
- which missing measurement prevents stronger inference.

Chapter 3 then targets the missing causal links with own data: calibrated phenotype → actual environmental exposure → mediator/function → reproductive fitness, with ancestry and population sampling designed explicitly around the identifiability failures exposed by Chapter 2.
