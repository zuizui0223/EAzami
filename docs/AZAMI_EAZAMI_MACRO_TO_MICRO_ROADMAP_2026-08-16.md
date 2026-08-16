# Azami → EAzami macro-to-micro research roadmap — 2026-08-16

## Purpose

This document fixes the division of labour between `zuizui0223/azami` and `zuizui0223/EAzami` so that Chapter 1 remains a global hypothesis-generating analysis and later work can add phylogenetic and mechanistic resolution without retrofitting unsupported causal claims into Chapter 1.

The program is deliberately staged:

```text
Azami / Chapter 1
Global public-image macro screen
        ↓ hypotheses, trait distributions, candidate environmental structure
EAzami / evolutionary reconstruction
East Asian nuclear phylogeny + explicit transition histories
        ↓ independently repeated transitions and focal contrasts
Population / mechanism studies
Gene flow + ancestry + expression + pigment + biotic interaction + fitness
```

The same biological theme runs through all three levels: the capitulum is treated as a modular ecological interface whose colour, orientation, outline and defensive structures can respond to different selective and historical processes.

## Stage 1 — Azami / Chapter 1: global macro screen

### Role

`azami` asks what large-scale patterns are visible before a resolved *Cirsium* species history is imposed.

Its current canonical evidence includes:

- 216 image-analysis taxa in the balanced atlas;
- 3,725 retained public observations and 6,626 detected heads;
- orientation, visible colour and outline modules;
- a larger exhaustive detector-positive and spatially thinned layer for within-species spatial environment–trait associations;
- historical placement only as a sensitivity analysis because most image-analysis taxa are not direct tips in the dated backbone.

### What Chapter 1 is allowed to claim

- visible phenotype is distributed substantially below assigned species means;
- orientation, colour and shape are not reducible to one universal lability axis in the current data;
- some modules retain among-species or within-species environmental structure worth testing at higher resolution;
- public images can generate comparative trait hypotheses at global scale.

### What Chapter 1 must not claim

- a resolved *Cirsium* species tree;
- ancestral capitulum states;
- numbers or directions of evolutionary transitions;
- pollinator, herbivore, climate-adaptation or plasticity causation;
- genetic variance or evolutionary rate from image variance;
- molecular loss or regain mechanisms.

Those questions are handed to EAzami or focal empirical studies.

## Stage 2 — EAzami: evolutionary reconstruction

### Current role

EAzami turns macro patterns into explicit historical questions using public nuclear data and later targeted sampling.

The accepted public nuclear primary remains:

- 294 biological tips;
- 295 unique public SRRs;
- 270 source-preserving analysis taxon labels.

EA01 and CNIPG are the only current independent augmentation candidates; EA02 is a duplicate-readset control and does not count as an independent biological tip. The candidate ceiling is 296 tips and requires an explicit common-locus combined analysis before acceptance.

### First historical question: Japanese origin structure

The current working hierarchy is:

1. minimum defensible: one dominant Japanese radiation + a separate *C. lineare* history;
2. best current point hypothesis: add *C. dipsacolepis* as a second rare secondary arrival;
3. four or more histories: unresolved and not currently supported.

The 294→296 nuclear run therefore tests 2 vs 3 vs 4+ Japanese colonization histories rather than simply asking whether all Japanese taxa are monophyletic.

### Second historical question: repeated capitulum transitions

After an accepted nuclear tree is available, project Azami-derived and source-backed trait states onto the same phylogenetic framework and estimate:

- white ↔ coloured flower transitions;
- orientation transitions;
- continuous outline changes;
- later, phyllary angle, spine architecture and stickiness when defensible trait data exist.

The key quantity is not one preferred ancestral reconstruction but the distribution of transition histories across accepted alternative trees / topology support.

### Third historical question: modular versus coordinated evolution

Test whether capitulum modules evolve independently or repeatedly form correlated ecological combinations.

Examples of hypotheses to test, not assume:

- orientation may trade pollinator presentation against rain / radiation protection;
- pigmentation may combine pollinator signalling with abiotic stress physiology;
- spreading / recurved phyllary spines may alter florivore or seed-predator access while potentially changing pollinator access;
- sticky involucral surfaces may function as adhesive defence with possible non-target costs;
- colour, orientation and defensive architecture may compensate for or reinforce one another.

No syndrome should be named from intuition alone. Correlated evolution should be demonstrated after phylogenetic uncertainty and state uncertainty are propagated.

## Stage 3 — focal population and mechanism studies

Only transitions supported at Stage 2 are promoted to expensive mechanistic work.

### Priority systems that do not require waiting for a new broad China tree

1. *C. japonicum* var. *takaoense*: within-lineage W/BP population comparison.
2. *C. pendulum*: Japanese white versus nearby purple populations, with transregional coloured anchors.
3. *C. sieboldii*: Japanese white versus purple populations plus verified Zhejiang context.
4. *C. brevicaule* + *C. irumtiense*: Ryukyu population history and colour-mechanism comparison.
5. var. *albescens* plus coloured Taiwan controls: independent white-loss / retained-pathway comparison.

### Mechanistic ladder

For focal transitions, keep these evidence levels separate:

```text
population ancestry / gene flow
→ coding / structural candidate state
→ floral expression
→ pigment chemistry
→ visible phenotype
→ pollinator / antagonist interaction
→ fitness consequence
```

A homologous read, BLAST hit, annotated pathway member, floral expression difference and causal locus are distinct evidence levels.

## Trait bridge from Azami to EAzami

The cross-repository bridge should contain one row per taxon × trait endpoint × evidence scope rather than only species means.

Minimum fields:

- `source_taxon_name`
- `accepted_analysis_taxon`
- `trait_module`
- `trait_endpoint`
- `state_type` (`continuous`, `discrete`, `circular`, `polymorphic`)
- `estimate_or_state`
- `uncertainty_or_range`
- `n_observations`
- `n_populations_or_spatial_units` when available
- `evidence_source`
- `assessability_status`
- `phylogeny_tip_match_status`
- `claim_boundary`

Species with documented polymorphism must not be forced into one W/C or one orientation state simply to satisfy ancestral-state software.

## Planned ancestral-state analysis

### Discrete traits

For white/coloured states and later categorical orientation / defensive states:

- compare ER / SYM / ARD-style transition models where estimable;
- retain polymorphic states or population/sample tips when morph-genotype linkage exists;
- use stochastic character mapping or equivalent transition-history sampling;
- repeat across accepted alternative nuclear trees / bootstrap or topology ensembles;
- report transition-count and ancestral-state uncertainty, not only one best reconstruction.

### Continuous traits

For orientation angle where defensible, Lab/chroma components and outline traits:

- retain continuous values where possible;
- compare Brownian / OU and, only when justified, rate-heterogeneous alternatives;
- propagate within-taxon measurement uncertainty;
- avoid interpreting public-image variance directly as evolutionary variance.

### Circular traits

Hue and any circular orientation representation require circular treatment; sine/cosine components must not be counted as independent biological traits.

## New capitulum traits: later expansion, not Chapter 1 revision

Do not reopen the current Chapter 1 analysis simply to add newly interesting traits.

Create a next-generation trait layer for:

- phyllary angle / degree of spreading or recurvature;
- spine length and orientation;
- visible involucral stickiness / glandularity only when actually assessable;
- capitulum size and display architecture;
- potentially floral-height / branching context.

The first task is an ontology and assessability protocol, not immediate global automated classification. Literature-level species descriptions and image-level observations must remain separate evidence columns.

## Current gates

### Completed or sufficiently established

- Chapter 1 macro pattern and uncertainty-aware lability correction;
- current 294-tip public nuclear inventory and deduplication;
- EA01 / CNIPG 296-ceiling execution contracts;
- Japanese-origin 2 vs 3 vs 4+ hypothesis hierarchy;
- repeated white-flower interpretation as a working macroevolutionary pattern;
- source-backed W/BP linkage for the six public *takaoense* samples;
- DFR / ANS assay-level recoverability in both current W and BP public young-leaf RNA runs.

### In progress / blocked by execution

- actual 294-tip BWA and BLASTx trees;
- source-label ASTRAL tree and accepted alternative topology set;
- EA01 / CNIPG empirical admission;
- final 296 common-locus tree if both pass.

### Not yet executed

- cross-repository trait-tip bridge table;
- colour / orientation / shape ancestral-state reconstruction on the accepted EAzami nuclear tree;
- correlated-evolution tests among capitulum modules;
- global phyllary/spine/stickiness trait extraction;
- focal fitness experiments establishing adaptive significance.

## Work order

1. Keep Azami Chapter 1 on submission/credibility gates only; do not add ASR or mechanistic claims there.
2. Complete the EAzami maximum-public nuclear tree on HPC / large-memory compute.
3. Build the Azami→EAzami trait-tip bridge independently of preferred transition histories.
4. Freeze a supported topology ensemble and taxon crosswalk.
5. Run ancestral-state / transition-history analyses for colour first, then orientation, then continuous shape.
6. Add phyllary/spine/stickiness ontology and evidence collection as the next trait-generation project.
7. Promote only replicated or high-information transitions to population genomics and ecological experiments.

## Stop rules

- Do not freeze a broad new China sampling list before the public nuclear tree identifies the continental branches that bracket unresolved Japanese histories.
- Do not use the grafted Azami historical tree as the definitive ancestral-state tree.
- Do not convert species-level polymorphism to a fixed state for convenience.
- Do not infer adaptation from macro correlation alone.
- Do not infer pathway loss from missing annotation or pathway-table coverage.
- Do not add a new trait to Chapter 1 merely because it is interesting; treat it as the next comparative layer unless it is required to repair a current validity problem.
