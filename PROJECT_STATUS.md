# EAzami current state

Status date: 2026-08-18

## Doctoral center

The project has **one central question**, not ten parallel thesis hypotheses:

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

Central hypothesis:

> **Modular evolvability** — standing ancestral variation, introgression/gene flow and cytotype/genome changes allow pre-existing genetic/developmental modules to be reused and recombined, so phenotype can diverge faster than genome-wide lineage sorting.

Canonical program:

- `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`
- `data/evidence/doctoral_core_program_v1.csv`

The ten-row preliminary registry is a **supporting evidence register**, not the doctoral architecture.

## Three Aims and priority

### Aim 1 — historical/genomic source of rapid phenotype divergence

**Priority 1 / indispensable.**

Resolve standing variation vs introgression vs lineage-specific change using population ancestry, same-individual plastid and cytotype data.

Core systems:

- *C. brevicaule* + *C. irumtiense* — Ryukyu focal pair;
- *C. pendulum* W/coloured — independent mainland replicate;
- *C. sieboldii* W/coloured — second replicate when feasible;
- *takaoense* W/BP — molecular/public anchor.

`C. lineare` and `C. dipsacolepis` are comparative controls, not standalone doctoral questions.

### Aim 2 — adaptive function of capitulum modules

**Priority 2 / indispensable for an adaptive-radiation claim.**

Test ancestry-resolved populations for:

- orientation -> rain/UV/pollen protection vs pollinator presentation;
- colour -> pollinator attraction and abiotic effects;
- involucre/phyllary/spine -> antagonist defence vs pollinator access;
- reproductive-fitness consequences.

The first *Cirsium* interaction evidence map is now frozen at:

- `docs/AIM2_CIRSIUM_INTERACTION_EVIDENCE_MAP_2026-08-18.md`;
- `data/evidence/cirsium_interaction_evidence_seed_v1.csv`;
- `data/evidence/cirsium_interaction_evidence_summary_v1.json`.

The bounded primary-literature seed contains **10 independent studies, 9 taxa and 11 taxon-study rows**. It separates pollinator behaviour, effective pollination, florivory, pre-dispersal seed predation and foliar-herbivory context rather than pooling them.

Current Aim 2 decision:

1. **head-orientation manipulation first** — no direct *Cirsium* orientation -> interaction/protection -> fitness study was recovered in the bounded seed;
2. **W/coloured functional comparison second** — no direct *Cirsium* colour -> interaction -> fitness chain was recovered, and this can share individuals/material with Aim 3;
3. **phyllary/spine conditional third** — proceed only after direct botanical validation and repeatable focal-population variation;
4. **stickiness lower priority** — the one recovered direct manipulation was null.

A pooled effect-size meta-analysis is **not yet authorized**. It requires at least five independent studies and three taxa for one harmonized contrast/outcome, with original-study deduplication and sampling variance.

Broad CHELSA correlation is no longer a mainline substitute for functional evidence.

### Aim 3 — flower-colour reversibility as a mechanistic case

**Priority 3 / mechanistic flagship.**

Test whether recurrent W↔coloured changes use retained anthocyanin machinery through regulatory/expression change.

Required chain:

`population ancestry -> coding/regulatory haplotype -> floral RNA -> pigment -> standardized colour`

Existing DFR/ANS screens remain plausibility evidence only.

## Premise already strong enough

The rapid-radiation premise is sufficient for sampling decisions:

- 36/38 sampled Japanese paper taxon concepts belong to the dominant radiation;
- `C. lineare` is the strongest replicated secondary-history exception;
- `C. dipsacolepis` is a secondary-arrival candidate;
- large present capitulum and environmental disparity already occurs within the dominant young radiation.

The 36:1:1 point-hypothesis occupancy is descriptive, not an age-corrected diversification-rate estimate. A heavy branch-length rebuild is optional unless rate acceleration itself becomes decision-critical.

## Preliminary results that now serve the three Aims

### Supports Aim 1 framing

- separate colonization history does not monotonically order current capitulum disparity;
- one colonization history does not define one capitulum syndrome;
- 2x/4x/6x occur in the dominant radiation, but ploidy does not deterministically set orientation;
- all four reviewed W/C-polymorphic systems lose state multiplicity under one species-tip `P` code;
- only `takaoense` currently has morph-linked high-dimensional W/C nuclear samples;
- ILS/reticulation are plausible, but species-level data cannot assign standing variation vs introgression.

### Narrows Aim 2

In the current nine-taxon subset, broad four-axis CHELSA distance does not positively track capitulum distance. This weakens a simple broad-climate explanation and shifts new ecology toward microclimate, pollinators, florivores/seed predators and fitness.

The new evidence map adds a second narrowing step:

- display size and floral scent already have direct *Cirsium* interaction evidence, but generally incomplete fitness chains;
- seed predators can substantially reduce reproductive output and may track capitulum size or position;
- the focal Azami modules orientation, colour and phyllary/spine remain direct functional gaps in the bounded seed;
- therefore the next work is not another broad correlation but ancestry-resolved manipulation and fitness measurement.

### Supports Aim 3 plausibility

Anthocyanin-pathway homologs are recoverable from *C. nipponicum* and DFR/ANS homologous reads are detectable in W and BP `takaoense` young-leaf public RNA. This is compatible with pathway retention but does not demonstrate floral regulation or causation.

## Sampling priority

### Core 190 minimum

- *C. brevicaule*: 60
- *C. irumtiense*: 60
- *C. pendulum*: 40
- *C. sieboldii*: 30

The **190 core individuals** have higher doctoral value than spreading effort thinly over every Japanese species.

### Controls +32

- *C. lineare*: 16
- *C. dipsacolepis*: 16

Full minimum = **222**. Recommended fuller design remains **298** where population replication can be increased.

Do not reduce core population replication merely to complete the control set.

Aim 2 measurements should be nested within the same focal populations wherever possible. Orientation, colour, visitor/antagonist observations and fitness do not require every RAD individual to enter a manipulation, but all experimental plants must retain population and ancestry linkage.

## What is no longer an independent doctoral hypothesis

- `H-RAD1` — premise/system justification;
- `H-CLIM1` — weakened simple alternative;
- `H-PL1` — modifier/diagnostic inside Aim 1;
- `H-CYTO1` — diagnostic inside Aim 1;
- `H-RYK1` — focal system inside Aim 1 and Aim 3;
- `H-COL1` — transition-resolution diagnostic shared by Aim 1 and Aim 3;
- `H-EVOL1/H-RET1` — direct support lanes for Aim 1;
- `H-ADAPT1` — Aim 2;
- `H-MECH1` — Aim 3.

Supporting ledger: `data/evidence/preliminary_hypothesis_registry_v1.csv`.

## Heavy-compute state

The accepted public nuclear inventory remains **294 biological tips / 295 SRRs / 270 source-preserving labels**. EA01 and CNIPG remain candidates; EA02 remains excluded as a duplicate-readset control.

The 294→296 Slurm reconstruction path is preserved but **deferred**. It is not a prerequisite for Aim 1 sampling. Reopen it only if:

- branch-scaled diversification/trait rate becomes a primary result;
- candidate admission changes a focal-system decision;
- a reviewer/journal requires the reconstruction for a specific claim.

## Stop rules

- Do not turn supporting evidence lanes into new thesis Aims.
- Do not add broad descriptive analyses unless they change focal sampling or a claim boundary.
- Do not use more broad climate rasters as a substitute for Aim 2 functional ecology.
- Do not pool visitor abundance, effective pollination, florivory, seed predation and foliar herbivory into one effect.
- Do not treat an interaction-database record as an effect size without verifying the original study.
- Do not infer functional absence merely because a module is absent from the bounded interaction seed.
- Do not use taxon-level ploidy as causal evidence; link cytotype to Aim 1 individuals.
- Do not build a separate plastid megatree instead of matched cytonuclear sampling.
- Do not call the radiation adaptive until Aim 2 yields fitness evidence.
- Do not claim regulatory reuse until Aim 3 connects genotype/expression/pigment/phenotype.

## Next action

**Finish the Aim 1 collection design while embedding the Aim 2 measurements that cannot be added later.** Protect population replication for the Ryukyu focal pair and mainland W/C replicates; pre-register orientation, colour, visitor, antagonist and fitness measurements for those same populations. Continue the full interaction census only to sharpen those field contrasts, not to create a separate thesis Aim.

## Navigation

- Doctoral core: `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`
- Aim 2 interaction evidence map: `docs/AIM2_CIRSIUM_INTERACTION_EVIDENCE_MAP_2026-08-18.md`
- Aim 2 frozen evidence seed: `data/evidence/cirsium_interaction_evidence_seed_v1.csv`
- Aim 2 summary: `data/evidence/cirsium_interaction_evidence_summary_v1.json`
- Core machine-readable program: `data/evidence/doctoral_core_program_v1.csv`
- Supporting preliminary lanes: `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`
- Supporting registry: `data/evidence/preliminary_hypothesis_registry_v1.csv`
- Detailed RAD plan: `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`
- Deferred heavy analyses: `docs/DEFERRED_HEAVY_ANALYSES.md`
