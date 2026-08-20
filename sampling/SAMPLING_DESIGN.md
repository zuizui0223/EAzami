# Sampling design — doctoral mainline

Status: 2026-08-20

## Principle

Collect only biological data that the existing public/meta layer cannot reconstruct.

Sampling is organized around three doctoral gates, not a broad East Asian taxon atlas:

1. **Aim 1 — source of variation**;
2. **Aim 2 — ecological function and fitness**;
3. **Aim 3 — fast colour-switching mechanism**.

Canonical minimum-new-data table:

`data/evidence/doctoral_next_data_minimum_v1.csv`

Detailed rationale:

`docs/DOCTORAL_NEXT_DATA_GATE_2026-08-19.md`

## Aim 1 — population ancestry first

The core population panel is protected before comparative controls.

### Core 190

| Taxon | Minimum populations | Individuals / population | Minimum total |
|---|---:|---:|---:|
| *C. brevicaule* | 4 | 15 | 60 |
| *C. irumtiense* | 4 | 15 | 60 |
| *C. pendulum* | 4 | 10 | 40 |
| *C. sieboldii* | 2 | 15 | 30 |

**Core = 190 individuals.**

Then, if resources remain:

- *C. lineare*: 2 × 8 = 16;
- *C. dipsacolepis*: 2 × 8 = 16.

**Full minimum = 222; recommended fuller panel = 298.**

Do not reduce focal-population replication merely to complete the controls.

### Immutable individual identity

Every sampled individual receives one `individual_id` linking:

- coordinates and population;
- taxon determination and voucher/voucher-linked images;
- standardized visible colour and UV record where feasible;
- natural capitulum orientation;
- direct phyllary spread, spine length/direction and stickiness score;
- DNA sample;
- plastid companion;
- flow-cytometry/cytotype material;
- later Aim 2 and Aim 3 samples when the individual enters those subsets.

The canonical cross-Aim individual/sample ledger is:

`sampling/aim13_individual_sample_ledger_v1.csv`

Use **one row per biological individual**. Do not create a second individual identifier when that plant enters Aim 2 or Aim 3. Aim 2 capitulum IDs and Aim 3 RNA/pigment sample IDs must point back to this row.

### Biological material to secure now

For core population-genomic individuals:

- silica-dried leaf tissue for DNA;
- fresh leaf material suitable for flow cytometry, with appropriate reference material recorded;
- voucher or voucher-linked material;
- standardized capitulum photographs/reflectance for flowering individuals.

The purpose is to discriminate standing ancestral variation, introgression/gene flow and lineage-specific origin. RAD/resequencing is a shallow population layer, not the universal species backbone.

## Aim 2 — nested functional subset

Aim 2 is **not a separate field campaign**. Functional plants remain linked to Aim 1 populations and ancestry.

The merged antagonist meta-analysis already establishes a large reproductive cost of insect herbivory. Tranche 1 therefore does not re-test generic insect exclusion. It measures which capitulum module changes antagonist cost while recording pollinator benefit and abiotic protection on the same focal heads.

### Experiment order

1. **Head orientation first**
   - natural angle;
   - non-destructive reorientation/sham where feasible;
   - repeated time-stamped microclimate observation bouts on the same focal head;
   - rain/wetting exposure;
   - pollen wetting/viability;
   - visitor guild and effective contact;
   - antagonist events/damage;
   - reproductive output.

2. **W/coloured function second**
   - ancestry-resolved W/C comparisons;
   - visible + UV phenotype;
   - effective pollination and relevant abiotic response;
   - antagonist exposure/damage;
   - achene/seed output;
   - share material with Aim 3.

3. **Phyllary/spine conditional third**
   - only after direct botanical measurement validates the Azami image proxies;
   - only if repeatable focal-population variation exists;
   - only if manipulation can avoid a dominant wound artifact;
   - if tested, retain both antagonist protection and pollinator-access outcomes.

4. **Stickiness lower priority**
   - record opportunistically;
   - do not displace orientation or colour.

### Four linked data levels

Individual/sample identity across Aim 1 and Aim 3:

`sampling/aim13_individual_sample_ledger_v1.csv`

Focal capitulum/treatment and final fitness:

`sampling/aim2_capitulum_field_ledger_v1.csv`

Repeated observation bout on the same focal capitulum:

`sampling/aim2_capitulum_observation_bout_ledger_v1.csv`

Plant × phenology / seasonal display and predation:

`sampling/aim2_plant_display_predation_ledger_v1.csv`

Do not collapse these levels. Head orientation is a capitulum-level trait; microclimate and interaction observations vary among bouts; seasonal display and cumulative seed-predator load are plant-level quantities; DNA/cytotype/RNA/pigment identity belongs to the biological individual.

The bout ledger keeps pollinator visits/effective contacts and antagonist events/damage as separate channels. Microclimate fields may be blank when an instrument is unavailable, but missing values must not be replaced with invented head-scale measurements or coarse climate rasters. Detailed protocol:

`docs/AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md`

### Replication

An orientation feasibility pilot may begin at about 10 experimental units per treatment per population where feasible. Final replication is set after pilot variance, treatment loss and the feasible experimental unit (capitulum or plant) are known.

Repeated bouts are repeated measurements, not additional biological replicates. Analysis must retain population/individual/capitulum dependence.

## Aim 3 — flowering-stage mechanistic subset

Aim 3 material must be collected during flowering because it cannot be reconstructed from DNA later.

Use at least two independent W/C transitions. Priority systems:

- *C. brevicaule* / *C. irumtiense*;
- *C. pendulum* or *C. sieboldii* as an independent Japanese replicate;
- *takaoense* remains a molecular/public anchor rather than a prerequisite for field completion.

From the same `individual_id`, collect:

- DNA/ancestry link from Aim 1;
- floral RNA tissue at late bud / pigmentation onset;
- floral RNA tissue at pre-anthesis or fresh anthesis;
- separate pigment tissue;
- calibrated visible/UV phenotype;
- voucher link.

Record the actual sample IDs, collection time and preservation method in `aim13_individual_sample_ledger_v1.csv` at collection time. A freezer label or notebook-only mapping is not treated as the canonical identity record.

Use a lab-approved RNA-preservation protocol (for example immediate freezing or an RNA-preservation reagent) consistently within a comparison. Record preservation time and method rather than mixing undocumented protocols.

Where feasible, target 2–3 populations per colour state and 6–10 biological individuals per population/state for expression/pigment work. Final allocation can be adjusted after RNA-quality and variance pilots.

## Do not expand now

The following are explicitly deferred unless they change one of the three doctoral gates:

- Japan38 × 3 same-library RAD sensitivity;
- broad China/Taiwan collection just to increase taxon count;
- heavy 294→296 nuclear reconstruction as a sampling prerequisite;
- more broad-climate-only models;
- additional SRA/BLAST fishing in place of morph-linked population/floral data.

## Stop rule

Before adding a taxon, population, assay or analysis, ask which gate it changes:

- **Gate 1:** source of reusable variation;
- **Gate 2:** trait → interaction/protection → fitness;
- **Gate 3:** retained pathway → floral regulation → pigment/colour.

If it changes none of them, defer it.
