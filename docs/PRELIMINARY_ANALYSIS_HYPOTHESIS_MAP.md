# Supporting preliminary-analysis map

Status: 2026-08-17

## Role of this document

This document is **not the doctoral hypothesis hierarchy**.

Doctoral center:

`docs/DOCTORAL_RESEARCH_CORE_PROGRAM.md`

The thesis has one central hypothesis and three Aims. The ten IDs below are retained only as evidence lanes that support, weaken alternatives to, or diagnose those Aims.

## Doctoral hierarchy first

### Central question

> Why did one young Japanese *Cirsium* radiation generate large capitulum and ecological diversity so quickly despite shallow lineage divergence?

### Central hypothesis

**Modular evolvability:** pre-existing variation can be reused/recombined through standing variation, introgression and cytotype/genome change, allowing phenotype to diverge faster than genome-wide lineage sorting.

### Three Aims

1. **Aim 1:** historical/genomic source of rapid phenotype divergence;
2. **Aim 2:** adaptive function of capitulum modules;
3. **Aim 3:** flower-colour reversibility as a mechanistic case.

## Where the ten support lanes belong

| Support lane | Doctoral role | Current use |
|---|---|---|
| H-RAD1 | premise | establishes the rapid-radiation system; not a standalone Aim |
| H-EVOL1 | Aim 1 | motivates modular phenotype reuse |
| H-RET1 | Aim 1 | standing variation vs introgression mechanism |
| H-CYTO1 | Aim 1 diagnostic | matched nuclear/plastid history |
| H-PL1 | Aim 1 modifier | ploidy-aware ancestry; deterministic morphology model already weakened |
| H-COL1 | Aim 1 + Aim 3 | exposes species-tip compression of W/C transitions |
| H-RYK1 | Aim 1 + Aim 3 focal system | Ryukyu population colour history |
| H-CLIM1 | Aim 2 alternative | broad climate-only explanation weakened; move to microhabitat/biotic function |
| H-ADAPT1 | Aim 2 | trait -> interaction/environment -> fitness |
| H-MECH1 | Aim 3 | retained anthocyanin pathway / regulatory reuse |

Machine-readable support registry:

`data/evidence/preliminary_hypothesis_registry_v1.csv`

## Preliminary-analysis policy

A new preliminary analysis is added only if it changes one of these decisions:

1. which Aim 1 population/system is sampled;
2. which historical mechanism can be discriminated;
3. which Aim 2 manipulation/interaction axis is tested;
4. which Aim 3 molecular target is measured;
5. which claim boundary can be advanced.

If none changes, stop.

## Current evidence ceilings

### Premise: rapid radiation

- 36/38 sampled Japanese paper taxon concepts lie in the dominant radiation.
- `C. lineare` is the strongest replicated secondary-history exception.
- `C. dipsacolepis` remains a secondary-arrival candidate.

This is enough to choose core and control systems. A full raw-read reconstruction is not required before sampling.

### Aim 1 support: phenotype history is not simple lineage sorting

Existing data already show:

- large capitulum disparity inside the dominant young radiation;
- separate colonization history does not monotonically order current trait distance;
- one origin history does not map to one orientation/stickiness syndrome;
- 2x/4x/6x occur in the dominant radiation, but ploidy does not deterministically set orientation;
- species-tip coding compresses all four reviewed W/C polymorphic systems;
- only `takaoense` currently has direct morph-linked high-dimensional W/C nuclear samples.

**Next decisive data:** matched population ancestry + phenotype + plastid + cytotype.

### Aim 2 support: broad climate is not enough

The current nine-taxon trait/environment screen does not show positive broad-CHELSA-distance coupling.

Do not respond by adding more similar rasters. New ecology should measure:

- microclimate/rain exposure;
- pollinator behaviour;
- florivory/seed predation;
- reproductive fitness.

### Aim 3 support: pathway retention is plausible only

DFR/ANS and other pathway homologs are recoverable, and DFR/ANS homologous reads occur in W and BP `takaoense` young-leaf RNA.

That does not resolve floral regulation.

**Next decisive data:** same-individual ancestry + coding/regulatory haplotype + floral RNA + pigment + standardized colour.

## What not to do next

- no more species-tip colour ASR without new morph↔genotype linkage;
- no more broad climate-only model variants;
- no more taxon-level ploidy correlations;
- no large plastid tree as a substitute for matched cytonuclear sampling;
- no untargeted SRA/BLAST fishing for mechanism;
- no routine heavy 294/296-tip tree rebuild as a sampling prerequisite.

## Sampling decision encoded by current preliminary results

Core Aim 1 minimum:

- `C. brevicaule` 60;
- `C. irumtiense` 60;
- `C. pendulum` 40;
- `C. sieboldii` 30;

= **190 core individuals**.

Comparative controls:

- `C. lineare` 16;
- `C. dipsacolepis` 16;

= **222 full minimum**.

The older ten support lanes remain useful only insofar as they help interpret these populations or select nested Aim 2/Aim 3 measurements.
