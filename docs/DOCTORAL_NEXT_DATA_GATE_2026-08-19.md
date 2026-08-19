# Doctoral next-data gate — 2026-08-19

## Decision

Do not add another preliminary-analysis branch unless it changes one of the three data gates below.

The existing public/meta layer is already sufficient to justify the system and choose focal sampling. What remains cannot be solved by more species-tip coding, more broad climate rasters, or a routine heavy-tree rebuild.

## What existing data already establish

- one dominant young Japanese radiation contains 36/38 sampled concepts;
- substantial capitulum disparity occurs inside that radiation;
- broad current-climate distance does not simply order current capitulum disparity in the present subset;
- current ploidy class does not deterministically specify head orientation;
- species-tip coding compresses known W/C polymorphism;
- pollination and pre-dispersal seed predation both matter in *Cirsium*, but published evidence does not resolve the focal trait-to-fitness mechanisms needed here.

These are premises and design constraints, not additional thesis Aims.

# The only three unresolved doctoral gates

## Gate 1 — source of reusable variation (Aim 1)

Question:

> Are repeated capitulum states produced from standing ancestral variation, introgression/gene flow, or lineage-specific change?

Why existing data stop:

Species-level and public-tip phylogenies do not provide morph-linked population ancestry for the focal W/C or Ryukyu populations.

Collect now:

- immutable `individual_id`;
- voucher-linked standardized capitulum phenotype;
- nuclear population-genomic DNA;
- same-individual or tightly matched plastid haplotype;
- flow-cytometry cytotype/genome-size material;
- colour/UV, natural orientation and direct phyllary/spine measurements.

Minimum core panel:

- *C. brevicaule* 60;
- *C. irumtiense* 60;
- *C. pendulum* 40;
- *C. sieboldii* 30.

**Core = 190.** Protect this replication before adding *C. lineare* 16 and *C. dipsacolepis* 16 controls.

Decision after data:

At least two independent focal systems must distinguish standing variation, introgression/gene flow and lineage-specific origin well enough to explain where repeated phenotype states came from.

## Gate 2 — ecological function and fitness (Aim 2)

Question:

> Do the capitulum modules that diverged rapidly actually change pollination, protection, antagonist attack and reproductive fitness?

Why existing data stop:

The evidence map shows pollinator behaviour, colour discrimination and seed-predator costs, but it does not provide the ancestry-linked causal chain for the focal modules.

Field order:

1. **head orientation first**;
2. **W/coloured comparison second**;
3. **phyllary/spine only after direct botanical validation**;
4. stickiness opportunistic/lower priority.

Collect now at the focal-head level:

- natural and achieved orientation;
- rain/wetting exposure;
- pollen wetting/viability where feasible;
- visitor guild and visit count;
- effective stigma/anther contact;
- florivory and pre-dispersal seed-predator damage;
- total and filled achenes.

Also collect the plant-level seasonal context:

- flowering display through time;
- cumulative head production;
- attacked-head fraction;
- plant-level reproductive output.

Use the existing linked ledgers:

- `sampling/aim2_capitulum_field_ledger_v1.csv`;
- `sampling/aim2_plant_display_predation_ledger_v1.csv`.

A feasibility orientation pilot can begin at about 10 experimental units per treatment per population where feasible. Final replication is determined from pilot variance, treatment loss and whether the experimental unit is a capitulum or plant.

Decision after data:

A replicated `trait -> interaction/protection -> reproductive fitness` link for at least one module is the minimum gate for an adaptive-function claim.

## Gate 3 — fast switching mechanism (Aim 3)

Question:

> Are repeated white↔coloured changes enabled by retained anthocyanin machinery plus regulatory/expression change, rather than repeated pathway destruction and rebuilding?

Why existing data stop:

Public homologs and young-leaf reads establish pathway-retention plausibility only. They do not report floral-stage expression or causation.

Collect now from an Aim 1/Aim 2 subset using the same `individual_id`:

- coding/regulatory haplotype;
- floral RNA at late bud/pigmentation onset;
- floral RNA at pre-anthesis or fresh anthesis;
- separate pigment tissue;
- calibrated visible/UV phenotype;
- ancestry and cytotype already attached through Aim 1.

Design target:

- at least **two independent W/C transitions**;
- where feasible, 2–3 populations per colour state;
- target 6–10 biological individuals per population/state for expression/pigment work, with final allocation adjusted after RNA-quality and variance pilots.

Decision after data:

Determine whether pathway retention plus regulatory/expression change recurs across independent transitions, or whether coding loss/other mechanisms dominate.

# Do not expand now

- no Japan38 × 3 same-library RAD sensitivity before core 190 is protected;
- no broad China/Taiwan collection merely to increase taxon count;
- no heavy 294→296 tree as a field-sampling prerequisite;
- no more broad CHELSA-only variants;
- no extra SRA/BLAST fishing as a substitute for morph-linked population or floral data;
- no pooled visitor/florivory/seed-predation effect simply because the bibliography becomes larger.

## Operational rule

If a proposed analysis or collection does not change Gate 1, 2 or 3, defer it.

Machine-readable source of truth:

`data/evidence/doctoral_next_data_minimum_v1.csv`
