# Azami series Chapter 2 — functional-diversity through time programme

Status: 2026-08-26

This is the execution programme for **Chapter 2**, not a free-standing repeat
of Azami. Chapter 1 supplies frozen global spatial hypotheses. Chapter 2 adds
functional-effect calibration, ancestry, evolutionary time, repeated
transitions, niche history and competing generative models. Its final layer
selects downstream causal experiments; it does not count those experiments as
already observed evidence.

## Core distinction from Azami

Azami is the spatial discovery layer:

`present-day global capitulum phenotype space -> within/among-taxon variation -> environmental structure`.

EAzami should be explicitly temporal and evolutionary:

`literature-derived functional effect sizes -> dated evolutionary history -> repeated functional transitions -> niche/distribution change -> ecological-event correspondence -> simulation-based model discrimination -> empirical validation targets`.

Chapter 2 should therefore ask how **functional disparity of reproductive/head traits changes through evolutionary time**, rather than repeating Chapter 1's present-day environment-trait map.

## Current Chapter 2 gate state

- **FDT1:** the quantitative *Aquilegia* calibration supports a
  context-dependent trichome -> enemy damage -> healthy-fruit pathway within one
  coordinated eight-population study cluster. Independent *Erica* corolla-
  stickiness and *Passiflora* sticky glandular-bract manipulations replicate an
  enemy damage/access mechanism, but they are not homologous pool-ready effects:
  the *Erica* link scale/sample size and *Passiflora* paired-plant covariance are
  unavailable, and whole-bract removal confounds adhesion with enclosure.
  Neither supplies a new fruit/seed fitness effect. *Ipomopsis* display and
  *Lilium* orientation remain direction-only because the accessible sources do
  not provide a lawful homologous numerical estimand. The three *Pedicularis*
  water-holding-bract rows retain exact model coefficients and reported SEs.
  The visitor model is binomial-logit, but the seed-set/predation link is
  unnamed. Independent envelope manipulations now add Cardueae spine removal
  (*Centaurea*), Asteraceae phyllary cutting (*Taraxacum*), a compound bract-
  concealment package (*Monotropsis*) and a liquid calyx barrier
  (*Chrysothemis*), with final seed/fruit directions in *Centaurea* and
  *Monotropsis*. *Rheum* supplies an opposite antagonist direction. This
  promotes the defensive-envelope mechanism and fitness direction to replicated
  calibration, but not to one pooled magnitude or a focal *Cirsium* adaptation.
  The colour gate is now stratified: a complete 64-cell *Ipomoea purpurea*
  CHS-null factorial extract opens bounded E14 whole-flavonoid thermoprotection
  analysis, and tomato complementation/antioxidant rescue supports a pollen-
  flavonol ROS mechanism. These studies do not isolate visible petal
  anthocyanin, each environmental experiment has chamber/greenhouse replication
  limits, and a direct *Mimulus* counterexample blocks a universal positive
  colour-protection prior. Equal-cell and reported-`n` descriptive margins both
  reproduce the author-reported genotype-by-maternal-temperature direction, but
  no interval is constructed from missing repeated-plant/cross-cell covariance.
  E13 visible-petal function remains partial.
- **FDT4:** present-day BIO15/BIO1 directions are stable across all six retained
  topologies after the frozen 11-taxon voucher augmentation, but the branchwise
  transition-niche concordance does not pass all-topology robustness.
- **FDT5-FDT7:** blocked until a machine-readable dated tree and node-age
  uncertainty are recovered. The current substitutions/site trees cannot be
  treated as absolute time.
- **FDT8:** remains a reverse-engineering output. It may prioritize orientation
  and W/coloured systems, but cannot close their causal fitness gates.

## Central question

> When ecological opportunity and selection regimes change, do floral/head functional modules repeatedly evolve toward similar functional solutions, and can those recurrent transitions explain rapid functional diversification in the young Japanese Cirsium radiation?

## Functional rather than purely morphological diversity

The primary object is not raw morphology. Each measured trait is mapped to one or more experimentally supported functional axes.

Provisional function axes:

1. **pollinator attraction / discovery**;
2. **pollination efficiency / effective contact**;
3. **reproductive-organ protection** from rain, UV and thermal exposure;
4. **antagonist exclusion / damage reduction**;
5. **resource-allocation / display cost**;
6. **sensory / pigment-mediated abiotic performance**;
7. **reproductive assurance** where a trait changes dependence on animal pollen transfer.

Head size, head number, orientation, phyllary/spine architecture, stickiness and pigmentation may load on more than one functional axis. The loading must come from evidence, not intuition.

The resulting object is a **trait x function effect matrix**. This matrix can later transform Cirsium morphology into a literature-informed functional trait space.

The executable interface is now
`data/evidence/fdt1_trait_function_loading_contract_v1.csv`. It carries 15
module-function rows and records evidence state, allowable Chapter 2 use,
uncertainty treatment, counterevidence and claim ceiling. It deliberately has
no fixed numeric Cirsium tip weights: every external loading remains conditional
on homology, measurement scale and focal proxy validation.

## Analysis layer 1 — experimental trait-to-function meta-analysis

### Question

For each trait module, which ecological pathway and fitness component does changing the trait actually alter?

### Eligible evidence

Prioritize manipulative or quasi-experimental studies that estimate a causal contrast on:

- pollinator visitation / discovery;
- effective stigma/anther contact or pollen transfer;
- pollen viability / wetting / reproductive-organ protection;
- florivore or predispersal seed-predator access/damage;
- fruit, viable seed or filled-achene output;
- recruitment only where the reproductive contrast is retained downstream.

Natural selection-gradient studies are retained in a separate estimand family and are not pooled directly with trait manipulations.

### Effect-size families

Do not force heterogeneous outcomes into one effect size. Maintain parallel families:

- log response ratio (lnRR) for count/proportion/rate outcomes where positive and comparable;
- log odds ratio for binary success where appropriate;
- Hedges g / standardized mean difference for continuous performance measures;
- treatment-induced difference in standardized directional selection gradient for agent-of-selection studies.

Within-paper multiple contrasts are nested or collapsed before across-study pooling as appropriate.

### Key moderators

- functional module;
- manipulated selection agent;
- mediator type;
- fitness stage;
- pollinator functional guild;
- antagonist guild;
- breeding system / self-compatibility;
- population density / local display;
- latitude and elevation as descriptors, not causal variables;
- temperature, precipitation/rain, UV, aridity and seasonality where recoverable;
- study year/site and plant family/genus.

### Main output

For each module, estimate a **functional effect vector**, for example:

`display -> pollinator benefit + enemy cost + resource cost`

`orientation -> wetting/UV protection + time-window pollination + possible enemy exposure`

`spines/phyllaries -> enemy exclusion +/- pollinator handling cost`

`pigmentation -> pollinator sensory effect + abiotic protection`

`stickiness -> context-specific enemy exclusion, with generic defence allowed to remain null`.

## Analysis layer 2 — geographic selection-regime meta-regression

### Question

Where in environmental space is each functional benefit or cost strongest?

Do not fit `latitude -> trait` as the biological model. Latitude/elevation are proxies. The biological moderators are climate, abiotic exposure, interaction opportunity and demographic context.

Each study/effect receives geographic coordinates where available and is linked to climate/environmental covariates. The goal is to estimate **selection-regime response surfaces**, not a global trait map.

Examples:

- expected pollinator benefit of larger display under pollinator scarcity/density regimes;
- expected antagonist cost of large display under enemy-rich regimes;
- expected protection benefit of nodding orientation under rain/UV regimes;
- expected pigment benefit under cold/high-UV/arid regimes.

These surfaces provide priors for the later evolutionary analysis.

### Current FDT2 gate (2026-08-26)

The 49 FDT1 seed rows collapse to **23 primary-source study clusters**. The
source-context audit preserves reported study geography and imposed exposure,
but it does not identify any cross-study family that simultaneously has a
homologous module -> mediator -> fitness estimand, recoverable effect variance
and independent environmental variation.

- only three source-cluster rows have one usable exact treatment-site
  coordinate; additional exact multi-site geography remains nested within two
  papers;
- ten sources can inform directional exposure calibration, but temperature,
  UV, rain/water and light differ in tissue, dose, duration and endpoint;
- five experimental contexts are additionally confounded with one chamber,
  greenhouse, bench or plot-level exposure;
- author affiliation, taxon range and source-population locality are forbidden
  substitutes for an unreported outcome environment.

Therefore FDT2 is **`READINESS_REGISTRY_ONLY /
STOP_BEFORE_MODERATOR_MODEL`**. No latitude slope, geographic response surface
or pooled exposure moderator is fitted. Reopening requires a preregistered
effect-level ledger for one homologous estimand family, with study clustering,
sampling variance/covariance and field versus experimental exposure explicitly
separated. This threshold must be fixed before effect access rather than chosen
from the observed outcome pattern.

Canonical audit and machine-readable gate:

- `docs/FDT2_PRIMARY_STUDY_CONTEXT_AUDIT_2026-08-26.md`;
- `data/evidence/fdt2_source_context_registry_v1.csv`;
- `data/evidence/fdt2_context_readiness_summary_v1.json`.

## Analysis layer 3 — repeated/convergent evolution evidence synthesis across plants

### Question

Do similar ecological shifts repeatedly accompany the same functional solutions across independent lineages?

This is not necessarily a classical scalar meta-analysis because published phylogenetic studies use heterogeneous trait and niche models. Begin as a systematic event-level evidence synthesis.

For each independent published transition, code:

- ancestral/derived functional state;
- estimated transition direction and uncertainty;
- branch/node age where available;
- ecological transition (pollinator guild, rain/UV regime, altitude/climate, antagonist regime, habitat shift);
- whether the same functional state arose independently elsewhere;
- whether molecular/developmental reuse was demonstrated;
- whether fitness/adaptation was experimentally validated.

If enough homologous events accumulate, fit a hierarchical transition-coupling model such as the probability of a functional transition conditional on an ecological regime shift relative to background branches.

Maintain strict terminology:

- **repeated/homoplastic state** = same state appears independently;
- **convergence/parallelism** = requires a defined ancestral relationship and mechanism/trajectory criterion;
- **parallel/convergent adaptation** = additionally requires ecological function/fitness evidence.

### Current FDT3 preflight (2026-08-26)

The repository currently contains six relevant material classes, but none is
an extracted external repeated-evolution event ledger:

- 23 FDT1/FDT2 study clusters calibrate trait -> function and exposure;
- 54 citation/DOI entries inventory focal *Cirsium* phylogeny and biogeography;
- the focal orientation analysis supports a topology-robust lower bound of at
  least five state changes, but not direction, historical niche or adaptation;
- six capitulum modules define Chapter 2 hypotheses;
- eight method/theory anchors define comparative models.
- a bounded orientation pilot audited seven primary comparative sources and
  admitted zero branch events.

These units are not exchangeable. Functional experiments are not transition
events, papers and tips are not independent origins, focal *Cirsium* evidence
belongs to FDT4, and method papers are not observations. Therefore the v1 event
ledger is deliberately schema-complete and row-empty, and FDT3 is
**`NOT_READY_ZERO_PRIMARY_EVENT_LEDGER_ROWS_SOURCE_FAMILY_IDENTIFIED`**.

The orientation pilot identified Xiang et al.'s 41-species *Lonicera* analysis
as the priority source family because it combines orientation ancestral-state
reconstruction, pollinator shift, phenology/temperature and experimental seed
output. It is not yet event-row-ready: the lawful accessible record did not
expose Supporting Figure S1/Table S3 node probabilities or a branchwise joint
orientation-ecology ledger. Six additional studies were retained as
topology-limited trait histories or explicit near misses rather than being
silently dropped.

Reopening requires a bounded primary-source extraction within one prespecified
module-function family. Each retained event must separate trait transition from
ecological transition, preserve topology/direction uncertainty, use one study
cluster denominator, and leave age, molecular reuse and fitness validation
missing when they were not demonstrated. Negative screens and directionally
unresolved cases remain in the audit rather than disappearing from the
denominator.

Canonical machine contracts:

- `data/evidence/fdt3_existing_material_preflight_v1.csv`;
- `data/evidence/fdt3_repeated_evolution_event_ledger_v1.csv`;
- `data/evidence/fdt3_existing_material_preflight_v1.json`;
- `data/evidence/fdt3_orientation_primary_pilot_v1.csv`;
- `docs/FDT3_ORIENTATION_REPEATED_EVOLUTION_PRIMARY_PILOT_2026-08-26.md`.

## Analysis layer 4 — Cirsium dated evolutionary-history + niche linkage

### Existing temporal anchors

Published nuclear phylogenomics already provide a usable temporal scaffold:

- dominant Japanese radiation after a Middle-Asia -> Japan dispersal at about 2.4 Ma (95% CI 1.7-3.6 Ma);
- C. lineare Japanese range expansion at about 1.4 Ma (0.7-2.7 Ma);
- C. dipsacolepis secondary Japanese founder at about 1.0 Ma (0.4-2.2 Ma);
- East-Asian Sinocirsium vs. Arenicola+Nipponocirsium split about 1.30 Ma;
- Arenicola vs. Nipponocirsium split about 1.02 Ma;
- C. brevicaule vs. C. irumtiense about 0.93 Ma.

Current EAzami also has a 153-locus focal compatibility tree with topology uncertainty and a topology-robust lower bound of >=5 orientation-state changes among 17 resolved tips.

### Niche/distribution analysis

For each focal taxon/lineage:

1. build current climatic/edaphic niche models from vetted occurrences;
2. estimate pairwise niche overlap plus equivalency/similarity where sample size permits;
3. reconstruct ancestral niche axes on the dated phylogeny rather than comparing present means only;
4. estimate branch-wise niche shifts and ask whether trait transitions occur on the same or immediately adjacent branches;
5. use paleodistribution models for selected well-sampled lineages to test range contraction/expansion and refugial connectivity;
6. combine with published biogeographic event reconstructions rather than inventing historical ranges from current SDMs alone.

The key statistic is not simply `trait ~ current climate`, but **temporal concordance between functional transition and niche shift**.

## Analysis layer 5 — functional disparity through time

### Build a literature-informed functional space

Raw Cirsium traits are converted to functional coordinates using the meta-analysis effect matrix. Where evidence is weak, retain a low-confidence or missing loading rather than assigning a function by assumption.

Possible traits:

- capitulum size;
- simultaneous/seasonal head number;
- continuous orientation;
- visible/UV pigmentation;
- direct phyllary/spine dimensions;
- stickiness;
- validated gross architecture variables.

### Temporal metrics

On a dated phylogeny and ancestral-state posterior:

- phylomorphospace / phylo-functional space;
- sum-of-variances or Rao-type functional disparity;
- disparity-through-time using time slices;
- rate of functional-space expansion versus packing;
- module-specific transition accumulation through time;
- functional distance among sister lineages versus divergence age.

Primary prediction under ecological opportunity:

> functional disparity should expand rapidly after major geographic/environmental opportunities and then shift toward packing or repeated occupation of existing functional regimes.

Do not require a classic early-burst result; adaptive radiations can show repeated or episodic shifts rather than one simple early pulse.

## Analysis layer 6 — ecological-event correspondence

Predeclare event classes rather than selecting events after seeing the trait history.

Candidate Cirsium event classes:

1. colonization/founder dispersal into Japan;
2. island fragmentation / changing land-bridge connectivity;
3. major Quaternary glacial/interglacial transitions within dating uncertainty;
4. lineage-specific habitat/niche shifts;
5. genome-size/cytotype shifts where independently supported;
6. inferred pollination-niche or antagonist-regime shifts where data exist.

Test whether functional-transition intensity rises around event windows relative to branch-length-matched null windows.

Pleistocene event matching must propagate node-age uncertainty; do not assign a transition to a named glacial episode from a point estimate alone.

## Analysis layer 7 — evolutionary simulations

Simulation is used to discriminate hypotheses, not to decorate the empirical tree.

Use the empirical dated tree and literature-derived effect priors where possible.

### M0 — neutral / unconstrained

- BM for continuous traits;
- equal-rate Mk for discrete states;
- no ecological coupling.

### M1 — single abiotic driver

One shared climate axis shifts all trait optima/rates.

Prediction: trait changes should align broadly with the same environmental direction.

### M2 — single biotic driver

One pollination or antagonist axis dominates all reproductive trait evolution.

### M3 — common-lability

Branches differ in one latent whole-capitulum evolutionary rate; all modules tend to change together, independent of module-specific ecology.

### M4 — modular selection mosaic

Each module has a distinct environment/interaction-dependent transition or optimum function, informed by the meta-analysis.

Prediction: repeated states occur, but transitions are decoupled among modules and align with module-specific ecological contexts.

### M5 — ecological-opportunity pulse

M4 plus temporary increases in transition/functional-space expansion following predeclared colonization/fragmentation/niche-opening events.

### Posterior-predictive / simulation targets

Compare observed and simulated:

- number of independent origins per module;
- functional disparity-through-time curve;
- convergence/reoccupation count;
- branch-wise trait-niche concordance;
- cross-module transition covariance;
- phylogenetic signal;
- niche overlap among sister versus non-sister lineages;
- concentration of transitions near ecological-event windows.

Prefer posterior predictive/model-adequacy or simulation-based inference to ad hoc visual matching.

## Biotic-interaction geography: claim boundary

Deep Pleistocene pollinator and antagonist distributions usually cannot be reconstructed with the same confidence as climate. Therefore:

- use modern pollinator/antagonist geographic data to estimate present interaction opportunity;
- use literature meta-regression to infer how interaction effects vary with climate/geography;
- use published historical biogeographic/ecological evidence where available;
- do **not** pretend that present pollinator maps are literal 1-Ma historical distributions.

Historical biotic selection is inferred only when supported by multiple independent lines: trait transition, ecological context, lineage history and ideally functional evidence.

## Chapter 2 hypothesis set

### H1 — functional selection mosaic
Different head/reproductive modules respond to different ecological agents; one universal driver is insufficient.

### H2 — repeated functional solutions
Similar functional states recur on independent branches more often than expected under neutral/common-lability models.

### H3 — niche-transition coupling
Independent functional transitions are temporally associated with module-relevant niche/environment shifts more strongly than with unrelated environmental axes.

### H4 — ecological-opportunity pulse
Functional disparity and/or transition intensity increases after colonization, fragmentation or niche-opening events and later shifts toward packing/reoccupation.

### H5 — modularity versus common lability
Module-specific ecological models predict transition histories better than a single latent branch-lability process.

### H6 — functional rather than morphological convergence
Lineages may reach similar ecological functions through different raw morphologies. Literature-informed functional space should therefore reveal convergence not obvious in raw trait space.

## What Chapter 2 can and cannot claim

### Can claim if supported

- quantitative functional effects of trait modules from prior experiments;
- geography/environment dependence of those effects;
- repeated functional-state evolution;
- temporal concordance of functional and niche shifts;
- better fit/adequacy of modular selection-mosaic simulations than neutral/single-driver/common-lability alternatives;
- ecological-opportunity-consistent functional diversification.

### Cannot claim without focal experiments

- that a specific Japanese trait state is locally adaptive;
- that a reconstructed historical ecological agent caused a transition;
- adaptive radiation as a demonstrated fitness process;
- molecular parallelism/reuse without ancestry-resolved molecular data.

Chapter 2 should therefore end by **reverse-engineering the empirical systems that maximize discrimination among competing mechanisms**.

## Reverse engineering empirical work

For every transition cluster identified, compute information value based on:

- independent transition confidence;
- strength of meta-derived functional prediction;
- contrast in ecological regime;
- ancestry matching feasibility;
- trait manipulability;
- flowering overlap;
- ability to measure filled achenes/recruitment;
- molecular sampling feasibility.

The top-ranked systems become Aim 2/Aim 3 field experiments. Thus the meta/comparative paper determines what the doctorate should experimentally test rather than the experiment list being fixed in advance.

## Intended Chapter 2 figures

1. **Functional architecture:** trait modules -> functional axes -> selection agents -> fitness stages, with meta-analytic effect sizes.
2. **Selection-regime geography:** environment-dependent functional benefit/cost surfaces.
3. **Cirsium functional phylomorphospace:** dated tree mapped into literature-informed functional space.
4. **Functional disparity through time:** with colonization/fragmentation/niche-event windows and uncertainty.
5. **Repeated transitions + niche shifts:** independent functional origins and branch-wise niche change.
6. **Simulation discrimination:** observed summaries against M0-M5 predictive distributions.
7. **Experiment reverse-engineering map:** which transition systems best discriminate mechanisms.

## Literature anchors for the design

- Caruso et al. 2019, Evolution, meta-analysis of agents of selection on floral traits: pollinator-mediated selection exceeds other biotic selection on average but is similar to abiotic selection; strong trait-type heterogeneity.
- Wellborn & Langerhans 2015, Ecology and Evolution: ecological opportunity as niche availability plus niche discordance with explicit spatiotemporal structure.
- Stroud & Losos 2016, Annual Review: ecological opportunity and adaptive radiation.
- Ingram & Mahler 2013, Methods in Ecology and Evolution: SURFACE framework for detecting convergent OU regimes.
- Butler & King 2004, American Naturalist: OU adaptive-regime modelling.
- Guillerme et al. / later plant disparity literature: time-slicing and disparity-through-time analyses.
- Linaria radiation study (Annals of Botany 2025): integration of phylogenomics, niche overlap/equivalency, MaxEnt, comparative methods and biogeography in a spatiotemporal plant-radiation analysis.
- Moreyra et al. 2025 and Chang et al. 2026: Cirsium dated phylogenomics, biogeography, niche/demographic context and Quaternary radiation anchors.
