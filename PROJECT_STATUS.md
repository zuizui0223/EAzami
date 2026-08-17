# EAzami current state

Status date: 2026-08-17

## Doctoral center

The project now has **one central question**, not ten parallel thesis hypotheses:

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

Central hypothesis:

> **Modular evolvability** — standing ancestral variation, introgression/gene flow and cytotype/genome changes allow pre-existing genetic/developmental modules to be reused and recombined, so phenotype can diverge faster than genome-wide lineage sorting.

Canonical program:

- `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`
- `data/evidence/doctoral_core_program_v1.csv`

The ten-row preliminary registry is now explicitly a **supporting evidence register**, not the doctoral architecture.

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

### Supports Aim 3 plausibility

Anthocyanin-pathway homologs are recoverable from *C. nipponicum* and DFR/ANS homologous reads are detectable in W and BP `takaoense` young-leaf public RNA. This is compatible with pathway retention but does not demonstrate floral regulation or causation.

## Sampling priority

### Core 190 minimum

- *C. brevicaule*: 60
- *C. irumtiense*: 60
- *C. pendulum*: 40
- *C. sieboldii*: 30

The core 190 has higher doctoral value than spreading effort thinly over every Japanese species.

### Controls +32

- *C. lineare*: 16
- *C. dipsacolepis*: 16

Full minimum = **222**. Recommended fuller design remains **298** where population replication can be increased.

Do not reduce core population replication merely to complete the control set.

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
- Do not use taxon-level ploidy as causal evidence; link cytotype to Aim 1 individuals.
- Do not build a separate plastid megatree instead of matched cytonuclear sampling.
- Do not call the radiation adaptive until Aim 2 yields fitness evidence.
- Do not claim regulatory reuse until Aim 3 connects genotype/expression/pigment/phenotype.

## Next action

**Finish the Aim 1 collection design first.** Protect population replication for the Ryukyu focal pair and mainland W/C replicates, then add comparative controls. Functional experiments and floral molecular sampling should be nested within those same ancestry-resolved populations wherever possible.

## Navigation

- Doctoral core: `docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`
- Core machine-readable program: `data/evidence/doctoral_core_program_v1.csv`
- Supporting preliminary lanes: `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`
- Supporting registry: `data/evidence/preliminary_hypothesis_registry_v1.csv`
- Detailed RAD plan: `docs/JAPAN_RADSEQ_PHASE_A_SAMPLING_PLAN_2026-08-16.md`
- Deferred heavy analyses: `docs/DEFERRED_HEAVY_ANALYSES.md`
