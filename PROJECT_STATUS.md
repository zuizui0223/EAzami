# EAzami current resolution goal

Status date: 2026-08-16

## Main goal

EAzami is the evolutionary-resolution layer downstream of the global public-image macro screen in `zuizui0223/azami`.

The current scientific problem is now broader than building an East-Asian tree:

> **Why did one young Japanese *Cirsium* entry generate a large radiation, and how could closely related lineages acquire large capitulum and ecological disparity so quickly?**

Program order:

```text
Azami Chapter 1
Global public-image macro pattern / hypothesis generation
        ↓
EAzami nuclear history
Japanese origins + branch-scaled trait / niche histories
        ↓
Focal population / mechanism studies
Ancestry + gene flow + cytotype + expression + pigment + interaction + fitness
```

Cross-project roadmap: `docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md`.
Pre-tree synthesis: `docs/JAPAN_RADIATION_PRETREE_META_SYNTHESIS_2026-08-16.md`.

## Accepted public nuclear baseline

The current accepted inventory is:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

Independent public augmentation candidates are **EA01 + CNIPG**. EA02 is a duplicate-readset control only and cannot increment biological-tip count.

If EA01 and CNIPG both pass their independent gates, the maximum current public ceiling is **296 biological tips / 0 new analysis labels**. This is not accepted by arithmetic; one explicit common-locus combined analysis must also pass.

The supported Slurm/large-memory handoff exists and its execution contracts are validated. The actual heavy 294-tip BWA/BLASTx + IQ-TREE + source-label ASTRAL analysis has **not** been executed in this environment.

## Japanese-origin state

The working hierarchy is:

- **36/38 sampled Japanese paper taxon concepts** in one dominant radiation;
- *C. lineare*: replicated phylogenetic exception in 3/3 high-dimensional analyses and 2/2 independent high-dimensional data-generation groups;
- *C. dipsacolepis*: strong but still single-independent-group secondary-arrival candidate;
- Arenicola: not established as an additional Japanese colonization.

Current origin-count hierarchy:

- minimum defensible = 2 histories;
- best point hypothesis = 3 histories;
- 4+ = unresolved / not currently supported.

The current 36:1:1 occupancy under the 3-history point hypothesis is a **descriptive radiation-success asymmetry**, not an age-corrected diversification-rate estimate.

## Pre-tree radiation meta result

Existing public/authority data now constrain several simple explanations before the accepted branch-length tree exists.

### 1. Colonization separation does not order current capitulum disparity

Nine Japan-38 trait taxa currently have >=10 detector-positive public-image observations for a seven-axis non-circular comparison.

With *C. lineare* as the replicated secondary-history comparator:

- *lineare* → dominant-radiation trait centroid = **4.842**;
- largest dominant-radiation leave-one-out displacement = **8.103**, *C. sieboldii*;
- largest within-dominant pairwise trait distance = **6.751**;
- largest observed *lineare*→dominant pairwise distance = **6.275**.

Thus a separate colonization history is not a monotonic proxy for present capitulum distance in the current subset.

Frozen result: `data/evidence/japan_radiation_pre_tree_trait_disparity_v1.json`.

### 2. Colonization separation does not order broad current environmental position

Using the same nine taxa and four Azami CHELSA species-median descriptors:

- *lineare* → dominant-radiation environmental centroid = **1.188**;
- largest dominant leave-one-out displacement = **6.358**, *C. pendulum*;
- largest within-dominant environmental distance = **5.623**;
- largest observed *lineare*→dominant distance = **3.719**.

This is a present environmental-position screen, not a full niche analysis. *C. lineare* has only three balanced Azami environment observations.

Frozen result: `data/evidence/japan_radiation_pre_tree_environment_disparity_v1.json`.

### 3. Broad climate distance does not positively track capitulum distance in the current subset

Seven-axis capitulum distance × four-axis CHELSA distance:

- Spearman rho = **-0.215**;
- positive-coupling taxon-label permutation P = **0.732**;
- two-sided P = **0.492**;
- all leave-one-taxon-out correlations remain negative.

Module-specific screens:

- orientation rho ≈ **-0.012**;
- visible colour rho ≈ **-0.003**;
- outline shape rho ≈ **-0.281**.

No module shows positive broad-current-climate distance coupling. This does **not** reject ecological adaptation on biotic, microclimatic or unmeasured environmental axes.

Frozen results:

- `data/evidence/japan_radiation_pre_tree_trait_environment_coupling_v1.json`;
- `data/evidence/japan_radiation_pre_tree_module_environment_coupling_v1.json`.

### 4. Ploidy does not define one head-orientation syndrome

Current source-backed dominant-radiation cytotype concepts:

- 2x = 5;
- 4x = 2;
- 6x = 1.

Upward/ascending capitula occur in 2x, 4x and 6x taxa, while diploid dominant-radiation taxa include both upward/erect and downward/nodding states.

Therefore ploidy is not used as a deterministic morphology explanation. Any role for polyploidy in evolvability must be tested through transition history, homeolog ancestry, genomic novelty, gene flow or diversification association.

Frozen result: `data/evidence/japan38_cytotype_trait_overlap_v1.json`.

### 5. Origin history does not define one capitulum syndrome

The current source-backed authority seed contains 20 dominant-radiation concepts plus the two secondary comparators.

The dominant sample contains both upward and downward/nodding heads, both sticky and non-sticky involucres, and four observed orientation × stickiness combinations. The two secondary comparators are both upward/erect but differ in stickiness.

Frozen result: `data/evidence/japan38_authority_module_combinations_v1.json`.

## Current adaptive-radiation verdict

### Strong now

- a young rapid Japanese radiation exists;
- radiation success is strongly asymmetric among current Japanese histories;
- large present capitulum disparity exists inside the dominant young radiation;
- substantial current environmental-position disparity also exists inside it;
- ILS/reticulation and cytogenetic change are real in East-Asian *Cirsium*;
- species-tip coding under-resolves documented W/C polymorphism.

### Simple explanations already weakened

- deeper/separate colonization history → greater current capitulum distance;
- greater broad current climate distance → greater capitulum distance;
- one ploidy class → one head orientation;
- one colonization history → one capitulum syndrome.

### Still hypotheses

- the dominant radiation has elevated **branch-scaled trait or niche evolutionary rates**;
- standing variation / reticulation / polyploidy increased evolvability;
- particular capitulum modules were adaptive drivers of diversification;
- Japanese *Cirsium* meets a strict causal definition of adaptive radiation.

Preferred wording remains **rapid Japanese radiation**, **radiation-success asymmetry**, and **adaptive-radiation / evolvability hypothesis**.

## Azami → EAzami trait bridge state

The bridge is now real data, not only a schema.

General Chapter-1 handoff:

- 216 taxa;
- usable colour = 215;
- shape = 215;
- orientation = 214;
- auxiliary involucre/spine = 210.

Japan-38 exhaustive public-image recovery:

- 36 distinct Japan-38 species binomials;
- **18 binomials** present in the original exhaustive Azami detector-positive source;
- **20/38 paper concepts** represented at binomial level;
- 9 trait taxa with >=10 detector-positive observations.

Continuous image traits and authority-backed categorical traits remain separate evidence layers. Broad species image records are not silently assigned to paper varieties.

## Involucre / spine correction

Phyllary/involucre/spine are **not new to Chapter 1**.

Azami already analysed exploratory high-resolution image proxies:

- `involucre_projection_roughness`;
- `involucre_spread_fraction`;
- `spine_peak_count_proxy`;
- `spine_relative_length_max_proxy`.

EAzami carries these existing proxies into the nuclear-history layer and later validates them against direct botanical phyllary angle, actual spine length/orientation/stiffness and field function. Visible stickiness/glandularity is a separate categorical/functional layer.

## Current flower-colour inference

- repeated white-flower evolution remains the best-supported broad pattern;
- Arenicola currently favours white loss on *C. brevicaule*; regain in *C. irumtiense* is not established;
- var. *takaoense* remains a topology-supported candidate regain;
- four reviewed W/C-polymorphic systems all lose state multiplicity under one species-tip `P` code;
- only *takaoense* currently has morph-linked high-dimensional W/C nuclear samples;
- in that one system, minimum transition count changes from 1 to 2 under population/sample-aware coding;
- replicated rate inflation remains unresolved because morph↔genotype linkage is only 1/4 among the reviewed polymorphic systems.

DFR / ANS homologous reads are recoverable from current W and BP young-leaf public RNA runs, but this is not floral differential expression or causal proof.

## Existing-data priority before new biological sampling

Use public/authority data first for:

1. accepted branch-length/topology ensemble from the maximum-public nuclear analysis;
2. branch-scaled trait disparity/rates for colour, orientation, outline and existing involucre/spine proxies;
3. full-occurrence niche divergence rather than current species-median climate positions;
4. gene-tree concordance/discordance and reduced-network metrics;
5. source-backed cytotype/genome-size transition mapping;
6. age/sampling-corrected dominant-vs-secondary radiation success.

Trait-gap recovery priorities:

- A0: *C. dipsacolepis* — nuclear placement exists; recover quantitative phenotype before more species-placement sequencing;
- A1: *C. alpicola* — dominant-radiation 6x comparator;
- manual identity gates: *C. yuki-uenoanum* / `C. waldsteinii`, *C. effusum* / `C. pulchellum`;
- remaining gaps: rank by branch information after the accepted tree.

Authority descriptions already recover major categorical states for *dipsacolepis* and *alpicola*; continuous image distributions remain missing.

## New biological data required only for non-identifiable questions

Phase-A population data are reserved for questions public data cannot answer:

- morph↔genotype ancestry beyond *takaoense*;
- standing ancestral variation versus introgression;
- population cytotype distributions;
- ploidy-aware local ancestry / homeolog histories;
- trait → interaction → fitness causation;
- genotype → floral expression → pigment → phenotype mechanisms.

Current population-RAD target remains **222 minimum / 298 recommended individuals** across *C. pendulum*, *C. sieboldii*, *C. lineare*, *C. dipsacolepis*, *C. brevicaule* and *C. irumtiense*. RAD is the population-history layer, not the universal cross-ploidy species backbone.

## Remaining mainline gates

1. Execute the validated 294-tip BWA/BLASTx + concatenated/source-label ASTRAL handoff on Slurm / large-memory compute.
2. Freeze accepted branch lengths and topology ensemble; accept/reject EA01 and CNIPG under predeclared gates.
3. Run branch-scaled radiation-success, trait-rate, niche and discordance analyses.
4. Recover only branch-informative missing public traits/taxa.
5. Then collect the Phase-A population panel for histories that remain non-identifiable.
6. Promote only replicated high-information transitions to functional/fitness experiments.

## Stop rules

- broad new China sampling remains unfrozen until the public nuclear tree identifies the relevant mainland brackets;
- the Azami grafted tree is not the definitive ancestral-state tree;
- polymorphic taxa are not collapsed to one fixed state for convenience;
- image vertical is not treated as true gravity without validation;
- macro/state-space correlations do not establish adaptation or evolutionary rates;
- ploidy and 2C genome size remain separate evidence variables;
- organelle history remains separate from the nuclear organismal-history layer.

## Navigation

- Operational nuclear state: `docs/CURRENT_STATE_2026-08-14.md`
- Macro→micro roadmap: `docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md`
- Pre-tree synthesis: `docs/JAPAN_RADIATION_PRETREE_META_SYNTHESIS_2026-08-16.md`
- Adaptive-radiation evidence ladder: `docs/JAPAN_ADAPTIVE_RADIATION_EVIDENCE_STATUS_2026-08-16.md`
- Japan RAD Phase A: `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`
- Trait-gap / pre-tree disparity idea: `docs/ideas/JAPAN_RADIATION_TRAIT_COVERAGE_AND_PRETREE_DISPARITY_2026-08-16.md`
- Issue #21: macro radiation / reticulation tests
- Issue #23: Azami→EAzami trait bridge and ASR pipeline
