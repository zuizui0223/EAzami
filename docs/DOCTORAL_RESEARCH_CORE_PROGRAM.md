# Doctoral research core program

Status: 2026-08-18

## One central question

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

This is the doctoral-level question. The repository no longer treats every operational uncertainty as an equal thesis hypothesis.

## One central hypothesis

> **Modular-evolvability hypothesis:** rapid Japanese *Cirsium* diversification was facilitated by reuse and recombination of pre-existing genetic/developmental variation—through standing variation, gene flow/introgression, and cytotype/genome changes—so capitulum modules could diverge faster than genome-wide lineage sorting.

The hypothesis predicts that colour, orientation, involucre/spine architecture and related modules need not track one species tree or one environmental axis, and that repeated states may reuse ancestry or regulatory machinery rather than arise by independent de novo pathway loss/reconstruction every time.

## Premise already strong enough

The rapid-radiation premise is not a separate doctoral Aim.

- 36/38 sampled Japanese paper taxon concepts belong to the dominant young radiation.
- *C. lineare* is the strongest replicated secondary-history exception.
- *C. dipsacolepis* is a secondary-arrival candidate.
- Large capitulum and environmental disparity already occur inside the dominant radiation.

The exact age-corrected diversification rate can be estimated later if it becomes publication-critical; it is not required to choose the doctoral sampling design.

# Three Aims

## Aim 1 — Historical/genomic source of rapid phenotypic divergence

**Priority: indispensable / first.**

Question:

> Are repeated capitulum states produced by reuse of standing ancestral variation and/or introgression, with cytotype and cytonuclear history modifying which variants can be reused?

Predictions:

1. phenotype state will not map perfectly to species-level ancestry;
2. repeated states will sometimes share local nuclear ancestry/haplotypes across taxon or population boundaries;
3. nuclear and plastid histories may disagree where introgression/chloroplast capture occurred;
4. ploidy will not deterministically specify phenotype, but may change ancestry/homeolog structure or the accessible variation pool.

Primary focal systems:

- **core field system:** *C. brevicaule* + *C. irumtiense* across the Ryukyus;
- **independent Japanese replicate:** W/coloured *C. pendulum*;
- **second replicate when feasible:** W/coloured *C. sieboldii*;
- **molecular/public anchor:** W/BP *C. japonicum* var. *takaoense*.

Secondary-history controls:

- *C. lineare*;
- *C. dipsacolepis*.

They are controls, not separate thesis chapters.

Required data:

`individual_id -> standardized capitulum phenotype -> nuclear population ancestry -> plastid haplotype -> flow-cytometry cytotype`

Main analyses:

- population structure/local ancestry;
- standing-variation vs introgression tests;
- matched cytonuclear discordance;
- ploidy-aware ancestry sensitivity;
- repeated-transition comparison across focal systems.

Success criterion:

At least two independent focal systems discriminate among lineage-specific mutation, retained ancestral variation and introgression strongly enough to explain where repeated phenotypic states came from.

## Aim 2 — Adaptive function of capitulum modules

**Priority: indispensable for the word “adaptive”. Run after or alongside Aim 1 in ancestry-resolved populations.**

Question:

> Do the capitulum modules that diverged rapidly actually alter pollination, abiotic protection, antagonistic interactions and reproductive fitness?

The existing broad-climate screen is a negative guide: broad CHELSA distance does not positively order current capitulum distance, so more broad raster correlation is not the main next step.

Prioritized functional modules:

1. **head orientation** — rain/UV/pollen protection versus pollinator presentation;
2. **flower colour** — pollinator attraction plus possible abiotic effects;
3. **involucre/phyllary/spine architecture** — florivore/seed-predator defence versus pollinator access.

Required evidence:

- standardized field phenotype;
- interaction observations;
- manipulative or quasi-manipulative comparison;
- reproductive-fitness response such as pollen viability, fruit/achene set, seed set or damage-mediated fitness.

### Cirsium interaction evidence map

The first bounded, source-backed evidence map is now frozen in:

- `docs/AIM2_CIRSIUM_INTERACTION_EVIDENCE_MAP_2026-08-18.md`;
- `data/evidence/cirsium_interaction_evidence_seed_v1.csv`;
- `data/evidence/cirsium_interaction_evidence_summary_v1.json`.

It contains 10 independent studies across 9 *Cirsium* taxa and 11 taxon-study rows. The evidence is not pooled across incompatible levels: visitor behaviour, effective pollination, florivory, pre-dispersal seed predation and foliar herbivory remain separate.

The current seed supports three design decisions:

1. capitulum display and floral scent already affect pollinator or mutualist–antagonist behaviour in *Cirsium*, although the fitness chain is often incomplete;
2. pre-dispersal seed predators can strongly reduce seed output and can associate with capitulum size or position;
3. the primary Azami modules head orientation, flower colour and phyllary/spine architecture remain direct functional gaps in the bounded seed.

Therefore the field sequence is:

1. **orientation manipulation first** — connect natural/manipulated angle to rain exposure, pollen condition, effective visits and seed set;
2. **W/coloured comparison second** — share ancestry-resolved individuals and floral material with Aim 3;
3. **phyllary/spine conditional third** — launch only after direct botanical validation and repeatable population variation;
4. **stickiness lower priority** — the one recovered direct manipulation was null, so it is not assumed to be a defence syndrome.

A formal effect-size meta-analysis is not yet authorized. One harmonized contrast/outcome must first reach at least five independent studies and three taxa with original-study deduplication and sampling variance. Until then, this product is an evidence map and field-design gate.

Success criterion:

A replicated trait -> interaction/environment -> fitness link for at least one module, preferably with the same functional direction in more than one ancestry-resolved population or lineage.

## Aim 3 — Flower-colour reversibility as a deep mechanistic case

**Priority: mechanistic flagship.**

Question:

> Are repeated white <-> coloured transitions enabled by retention and regulatory reuse of the anthocyanin pathway rather than repeated destruction and de novo rebuilding of the pathway?

Flower colour is used here as a mechanistic model of the broader modular-evolvability hypothesis, not as a disconnected side project.

Primary systems:

- *C. brevicaule* / *C. irumtiense*;
- W/BP *takaoense*;
- *C. pendulum* or *C. sieboldii* as an independent replication target when material is available.

Required same-individual chain:

`population ancestry -> coding/regulatory haplotype -> floral RNA/expression -> pigment chemistry -> standardized colour phenotype`

Existing DFR/ANS homology and young-leaf read detection establish only pathway-retention plausibility; they do not establish floral regulation or causation.

Success criterion:

At least two independent W/C transitions show whether pathway retention plus regulatory/expression change is recurrent, versus lineage-specific coding loss or unrelated mechanisms.

# What the old 10 operational hypotheses become

The ten-row preliminary registry is retained as a **supporting evidence register**, not ten equal doctoral hypotheses.

- `H-RAD1` -> premise/system justification;
- `H-EVOL1`, `H-RET1`, `H-CYTO1`, `H-PL1`, `H-COL1`, `H-RYK1` -> Aim 1 diagnostics;
- `H-CLIM1` -> weakened simple alternative informing Aim 2 design;
- `H-ADAPT1` -> Aim 2;
- `H-MECH1` + colour component of `H-COL1/H-RYK1` -> Aim 3.

No new thesis Aim is created because one of these support lanes acquires another analysis.

# Sampling priority

## Core population panel — 190 individuals before controls

The biologically central panel is:

- *C. brevicaule*: **60 minimum**;
- *C. irumtiense*: **60 minimum**;
- *C. pendulum*: **40 minimum**;
- *C. sieboldii*: **30 minimum**.

Total core = **190**.

This directly tests the central hypothesis across the Ryukyu focal pair plus replicated mainland W/C polymorphism.

## Comparative controls — +32 individuals

- *C. lineare*: **16 minimum**;
- *C. dipsacolepis*: **16 minimum**.

Total full minimum = **222**.

These 32 individuals test whether the dominant radiation differs from secondary histories; they are lower priority than obtaining adequate population replication in the core 190.

## First field tranche if resources are limited

Do not thin every taxon equally. Protect population replication in the focal systems.

First tranche priority:

1. Ryukyu *brevicaule* / *irumtiense* endpoints and core islands;
2. reproducible W/coloured *pendulum* populations;
3. matched *sieboldii* W/coloured wetlands;
4. only then secondary-history controls.

Public *takaoense* W/BP samples remain a useful discovery/molecular anchor; new Taiwan sampling is valuable but is not allowed to block the Japanese/Ryukyu core.

Aim 2 manipulation plants are nested inside these ancestry-resolved populations rather than collected as a disconnected ecological sample. Orientation and colour measurements must be attached to population/individual IDs before treatment assignment.

# Thesis logic

```text
Premise
one young Japanese radiation + large phenotype disparity
        |
        v
Aim 1: WHERE DID THE VARIATION COME FROM?
standing variation / introgression / cytotype / cytonuclear history
        |
        +------------------+
        |                  |
        v                  v
Aim 2: WHY IS IT USEFUL?   Aim 3: HOW CAN IT SWITCH SO FAST?
trait -> interaction       retained pathway -> regulation
-> fitness                 -> pigment -> phenotype
```

Together, the three Aims test one explanation for rapid radiation: **modular reuse of variation, followed by ecological sorting and functional differentiation**.

# Stop rules

- A branch-length 294/296-tip rebuild is not a doctoral prerequisite.
- Broad climate correlations are not expanded unless a genuinely new ecological axis is added.
- Pollinator visitation is not treated as effective pollination or fitness without contact/pollen/reproduction evidence.
- Florivory, pre-dispersal seed predation and foliar herbivory are not pooled as one antagonist effect.
- An interaction-database record is discovery evidence, not an effect size, until its original study is verified.
- Taxon-level ploidy correlations are not treated as a chapter.
- A separate plastid megatree is not substituted for matched cytonuclear sampling.
- Additional SRA/BLAST fishing is not a mechanism study.
- “Adaptive radiation” is used only after Aim 2 provides fitness evidence; until then use “rapid radiation” and “modular-evolvability hypothesis”.
