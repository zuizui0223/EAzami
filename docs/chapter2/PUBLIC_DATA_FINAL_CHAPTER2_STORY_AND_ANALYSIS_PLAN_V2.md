# Chapter 2 public-data final story and analysis plan v2

Status: 2026-08-31  
Supersedes: `PUBLIC_DATA_FINAL_CHAPTER2_STORY_AND_ANALYSIS_PLAN_V1.md`

## Chapter question

> **How deep is capitulum diversity in evolutionary time, through which geographic and environmental processes was it assembled, and when do those historical processes agree with the present environmental gradients recovered by Azami?**

Chapter 2 is the final public-data chapter before Chapter 3 introduces focal samples, calibrated phenotypes, direct exposure measurements, mechanism and reproductive fitness.

## Doctoral story

- **Chapter 1 / Azami — breadth across environmental state space.** Public images and occurrence-linked environments quantify how continuous capitulum phenotypes are distributed across present space.
- **Chapter 2 / EAzami — depth through evolutionary and environmental trajectory space.** Public phylogenies, dated subclades, occurrences, palaeoclimate and range-history data establish how often traits changed, how deeply or when they changed, what exposure opportunities surrounded those changes, and whether historical environmental movement points in the same direction as present sorting.
- **Chapter 3 — mechanism and fitness.** Own samples test the missing causal chain: phenotype → actual exposure → mediator/function → reproductive fitness.

The Chapter 1–2 bridge is not repeated significance testing. It is an explicit comparison between present **environmental states** and historical **environmental trajectories**.

## Ordered evidence chain

1. **Recurrence:** how many changes are required under the admitted topology ensemble?
2. **Temporal depth:** are changes deep/internal or shallow/terminal, and which can be bounded in calendar time from public dated nodes?
3. **Range process:** did colonization, fragmentation, secondary arrival or within-region diversification create a new exposure opportunity?
4. **Environmental trajectory:** what environmental level, direction, variability and extremes occurred through an admissible transition branch?
5. **Space–time concordance:** does that historical trajectory agree with the frozen Azami trait–environment direction?
6. **Cause-candidate ranking:** which drivers survive topology, chronology, paleolocation, alternative-variable and matched-null tests?
7. **Public-data ceiling:** which links require Chapter 3 samples and experiments?

## Resolved evolutionary depth

### Orientation

- ML minimum changes: 6.
- UFBoot minimum changes: 4–6.
- Placement spans internal and terminal parts of the radiation.
- Repetition is resolved, but individual Japan38 event dates are not because the admitted full tree is a substitutions/site phylogram rather than a public chronogram.

### Phyllary posture

- Exactly 3 minimum changes across 1,000 UFBoot trees.
- Deeper placements remain admissible.
- The history is stronger than the current environmental or functional identification.

### Stickiness

- Exactly 5 minimum changes across 1,000 UFBoot trees.
- Changes are strongly shallow/terminal-biased.
- Generic defence evidence is mixed/null; recurrence alone does not identify enemy-mediated adaptation.

### Continuous colour and outline

- Current EAzami-native matched coverage does not retain corrected topology-robust phylogenetic structure.
- This is unresolved detection, not proof of evolutionary independence or absence of history.
- Discrete morph-linked colour events are treated separately from sparse continuous-tip diagnostics.

## Corrected orientation chronology

The restricted six-taxon East-Asian scaffold originally forced an erect→nodding change on the 0.79–0.47 Ma Taiwan-trio stem. Adding public Japanese core Nipponocirsium changes that placement:

- `C. morii` is erect and basal within Nipponocirsium;
- Japanese core Nipponocirsium and Taiwan core Nipponocirsium are nodding;
- therefore the parsimonious minimum change lies on the **core-Nipponocirsium stem after `C. morii` and before the Japanese–Taiwan core split**.

The bounding ages come from separate public studies:

- parent / `C. morii` split: central 0.79 Ma, marginal 95% HPD 0.43–1.18 Ma;
- child / Japanese–Taiwan core split: central 0.74 Ma, marginal 95% interval 0.60–0.87 Ma.

The central values suggest a 0.74–0.79 Ma branch, but this is **not a joint posterior interval**. The marginal intervals overlap, and the pre-split ancestral region is unresolved. Consequently:

- the origin event is represented by a deterministic chronology × paleolocation scenario envelope;
- the Taiwan 0.79–0.47 Ma analysis is retained only as a restricted descendant-lineage sensitivity;
- adding public taxa is allowed to move an event; the movement is a scientific result, not an inconvenience to optimize away.

The corrected machine-readable registry is `chapter2_public_event_process_registry_v2.csv`.

## Range-history process model

Distribution change is an exposure opportunity, not automatically a selective pressure:

`range reorganization → new abiotic/biotic exposure → trait transition`.

Public events are classified as:

- dominant Japanese founder dispersal and radiation;
- secondary arrival / independent range expansion;
- Japanese–Taiwan or island-clade splitting;
- within-region diversification;
- late-Quaternary demographic/range shifts.

A range event is linked to a trait only when the trait-bearing branch is independently reconciled. Otherwise it remains context or a natural-experiment candidate.

The public global sea-level sensitivity for the restricted 0.79–0.47 Ma Taiwan descendant interval found no unusual sea-level volatility relative to same-duration windows. That weakens a simple high-volatility trigger for that restricted interval, while remaining agnostic about local bathymetry and the deeper origin branch.

## Environmental state–trajectory analysis

### Shared primary space

Use the exact variables shared between Azami and PALEO-PGEM:

- BIO1 — annual mean temperature;
- BIO4 — temperature seasonality;
- BIO12 — annual precipitation;
- BIO15 — precipitation seasonality.

For every usable branch/scenario estimate:

- branch-window mean;
- young minus old directional change;
- absolute net change;
- temporal SD and range;
- mean and maximum absolute 1-kyr change;
- same-duration background percentile;
- regional spatial IQR / temporal SD;
- cellwise direction agreement where a bounded region is available.

Define:

- `β_space` = frozen standardized Azami orientation slopes in BIO1/BIO4/BIO12/BIO15;
- `ΔE_time` = background-standardized historical branch trajectory in the same four variables.

The primary integration statistic is:

`cosine(β_space, ΔE_time)`.

### Orientation wetting refinement

Use:

- BIO13 and BIO16 as wettest-month / wettest-quarter proxies;
- BIO14 and BIO17 as driest-month / driest-quarter controls.

A wetting-specific historical interpretation requires wet-side dynamics to outperform dry-side controls and remain stable across paleolocation scenarios. These are climatic exposure proxies, not direct measurements of rain on flowers.

### Phenology refinement

Public flowering months can define descendant anthesis-window precipitation sensitivity. This is biologically closer to reproductive wetting than annual rainfall, but it cannot be transferred to an unresolved ancestor unless ancestral phenology is separately bounded.

### False-equivalence prohibition

Historical surface equivalents are not available in the frozen PALEO-PGEM layer for Azami RSDS, VPD, wind, GSP and NPP. Orbital insolation, humidity, wind or productivity models would be separate model layers and cannot be labelled direct replication.

## Current restricted Taiwan result

The 0.79–0.47 Ma descendant-lineage sensitivity does not support a simple `present sorting = origin driver` interpretation:

- BIO12 increases but its branch change/variability is typical;
- BIO15 changes relatively strongly but toward lower seasonality, opposite the present nodding-state high-BIO15 association, and cellwise signs are mixed;
- BIO1 warms, opposite the present nodding-state cooler-niche association;
- the four-dimensional state–trajectory cosine is approximately 0.059 with a null percentile near 0.518;
- BIO13/BIO16 wet-side change does not outperform BIO14/BIO17 dry-side controls.

Because this is not the unique origin branch, these results diagnose the danger of reading present niches backward into history rather than deciding the origin mechanism.

## Origin-envelope analysis

The next primary analysis propagates both unresolved dimensions:

1. enumerate parent/child age pairs across the published marginal intervals, retaining only topologically admissible parent > child pairs;
2. evaluate Taiwan, Ryukyu corridor, southern Japan and broad East-Asian core-corridor paleolocation scenarios;
3. calculate BIO1/BIO4/BIO12/BIO15 branch trajectories for every chronology × location scenario;
4. compare each trajectory with same-duration regional climate windows;
5. test whether state–trajectory cosine direction survives the complete scenario envelope.

Outcomes:

- **robust concordance:** the same environmental direction survives chronology and paleolocation uncertainty and is unusually aligned relative to matched windows;
- **robust discordance:** the opposite direction survives both uncertainty dimensions;
- **unresolved:** sign or tail status depends on age/location scenario.

The likely value of an unresolved result is substantive: public data can resolve recurrent history but not the ancestral exposure that generated one transition.

## Three process models

### ST1 — persistent driver

The same environmental domain contributed to historical transition and present sorting/maintenance. Support requires repeated or uncertainty-robust historical direction concordant with Azami, not merely a present niche association.

### ST2 — origin–maintenance decoupling

The historical transition occurred under a typical, opposite or unidentified trajectory, while current environments strongly sort or maintain the phenotype. Range sorting, later niche tracking and changing selective agents are candidate explanations.

### ST3 — driver switching / selection mosaic

Independent transitions reached similar phenotypes through different abiotic or biotic routes. This becomes testable only after multiple dated trait events are recovered; one local branch cannot distinguish it from ST2.

## Trait-specific public-data ceilings

| Trait | Evolutionary depth | Present environmental bridge | Historical cause status |
|---|---|---|---|
| Orientation | 4–6 changes; mixed depth; core-stem dated envelope | Azami BIO12; EAzami BIO15/BIO1 present niches | strongest candidate, but origin trajectory currently chronology/location limited |
| Colour | two conditional dated white-state terminal events on the public six-taxon scaffold; broader history unresolved | strong Azami RSDS–chroma | direct historical surface-RSDS and morph-linked population chronology absent |
| Phyllary posture | 3 changes, including deeper placements | no homologous calibrated Azami posture axis | history resolved, driver unidentified |
| Stickiness | 5 shallow changes | no homologous Azami spatial axis; generic defence evidence weak | rapid reassembly resolved, driver possibly biotic but publicly unidentified |
| Outline/architecture | strong present breadth | several Azami environmental associations | matched continuous time-axis coverage insufficient |

## Model hierarchy

BM/OU are secondary process baselines, not the chapter question.

- Use BM/OU/environment-dependent continuous models only after a commensurate continuous trait has adequate matched tips and a defensible dated tree.
- Use discrete event/transition analyses for orientation, phyllary and stickiness.
- With multiple dated events, compare constant transition opportunity against environment-dependent transition hazard or matched event/non-event branches while propagating topology, duration, age and paleolocation.
- Do not interpret lower AIC alone as adaptation.

## Remaining public-data work before Chapter 3

1. Complete the core-Nipponocirsium origin chronology × paleolocation envelope.
2. Exhaust public dated subclades for additional orientation and homologous trait events.
3. Preserve event-level results before any cross-event aggregation.
4. Add public phenology only where descendant/ancestor applicability is explicit.
5. Classify range reorganization separately from selective trajectory.
6. Retain matched windows, dry-side controls, thermal alternatives and location/topology scenarios.
7. Stop when chronology, phenotype homology, location or environmental equivalents make a trait–driver pair non-identifiable.

## Chapter 2 endpoint

Each trait × driver receives one final class:

1. multi-layer concordant candidate;
2. present sorting / historical origin decoupled;
3. driver switching / heterogeneous events;
4. history resolved, cause unidentified;
5. not evaluable at public-data resolution.

Chapter 2 ends with a ranked candidate-and-limit map, not an adaptation claim. Chapter 3 then prioritizes the strongest convergence and the most informative discordances for direct mechanism and fitness tests.
