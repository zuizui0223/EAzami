# EAzami current state

Status date: 2026-08-20

## Doctoral center

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

Central hypothesis: **modular evolvability** — reusable standing variation, gene flow/introgression and cytotype/genome changes allow phenotype modules to diverge faster than genome-wide lineage sorting.

Priority:
1. **Aim 1 — source of variation**.
2. **Aim 2 — adaptive function**.
3. **Aim 3 — colour mechanism**.

## Existing-data premise

- 36/38 sampled Japanese concepts are in the dominant young radiation.
- *C. lineare* is the strongest replicated secondary-history exception.
- *C. dipsacolepis* remains a candidate secondary arrival.
- large capitulum disparity occurs inside the dominant radiation.
- broad current-climate distance does not positively order capitulum distance in the current nine-taxon subset.
- ploidy is not a deterministic explanation of orientation.
- species-tip coding compresses documented W/C polymorphism.
- the heavy 294→296 raw-read tree is preserved but deferred.

## Aim 2 — quantitative antagonist result

The interaction evidence map remains useful for deciding which biological pathways and capitulum modules to test, but Aim 2 now has a **direct quantitative result**, not only a literature prior.

Canonical result:

`data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json`

Estimand:

`RR = viable/mature seed output under experimentally reduced insect herbivory / seed output under ambient herbivory`

Only directly reported seed-output means and SEs were harmonized. Multiple years/habitats/strata from the same data-generation study were collapsed before across-study pooling.

Current coverage:

- **9 within-study contrasts**;
- **4 independent data-generation studies**;
- **2 *Cirsium* taxa/taxon concepts**.

Random-effects result:

- pooled **RR = 2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- 95% CI **58.1–66.6%**;
- **I² = 1.0%**.

All four study-level effects are positive (RR 2.29, 3.57, 2.48, 2.67). Leave-one-study-out pooled RR remains 2.60–2.73 and every interval remains above 1.

### What is now resolved

Within the currently harmonizable experimental *Cirsium* literature:

> **insect herbivory on reproductive structures imposes a large and repeatable maternal-fitness cost.**

Aim 2 therefore no longer asks whether antagonists matter at all.

### What remains unresolved

The causal evolutionary question is now:

> **Which capitulum modules reduce or redistribute this established antagonist cost, and what pollination or abiotic costs accompany that protection?**

Current functional order:

1. **head orientation first** — test presentation/wetting plus antagonist access and final seed output;
2. **W/coloured comparison second** — effective pollination/abiotic response/fitness, nested with Aim 3;
3. **phyllary/spine after direct botanical validation** — test antagonist exclusion versus pollinator-access cost;
4. **stickiness lower priority**.

The strong antagonist baseline makes phyllary/spine defence more biologically consequential, but it does **not** prove that the image-derived phyllary/spine proxies are defensive traits.

### Pooling boundary

The narrow seed-output lnRR meta-analysis is valid because it uses one explicit estimand. **Broad heterogeneous pooling remains prohibited**: do not combine pollinator visitation, effective pollination, florivory, seed predation, foliar herbivory, or unrelated trait contrasts into one effect.

## Cross-layer reduction result

The merged pattern-reduction screen uses frozen Azami observational patterns plus independent *Cirsium* interaction/fitness targets.

Initial 500-draw screen per model family:

- ENV_ONLY: 0 accepted;
- ENV_POLL: 0;
- ENV_ANT: 0;
- FULL_COUPLED: 0, with the common-lability constraint as the last failure;
- FULL_MODULAR: 2 accepted.

This is **not proof of modular evolvability**. The useful result is structural: environment plus only one interaction channel is insufficient; pollination and antagonism can jointly reproduce the interaction patterns, but one shared response/lability axis conflicts with the near-zero cross-module coupling in Azami.

Field consequence: collect environment/microclimate, pollinator benefit, antagonist cost, module phenotype and reproductive fitness together on ancestry-linked material.

## Sampling

Core minimum = **190**:
- *C. brevicaule* 60
- *C. irumtiense* 60
- *C. pendulum* 40
- *C. sieboldii* 30

Controls +32:
- *C. lineare* 16
- *C. dipsacolepis* 16

Full minimum = **222**, recommended fuller design = **298**.

Aim 2 measurements remain nested within the same ancestry-resolved populations.

## Three unresolved new-data gates

Doctoral execution remains compressed to **three unresolved new-data gates**; the quantitative antagonist and pattern-reduction results sharpen Gate 2 but do not add a fourth gate.

1. **Aim 1:** same-individual phenotype + population ancestry + plastid + cytotype to resolve standing variation vs introgression vs lineage-specific origin.
2. **Aim 2:** determine which ancestry-linked capitulum modules alter the now-quantified antagonist cost, pollination/protection pathways and reproductive fitness.
3. **Aim 3:** same-individual floral-stage RNA + coding/regulatory haplotype + pigment + calibrated colour in at least two independent W/C transitions.

Canonical execution files:

- `data/evidence/doctoral_next_data_minimum_v1.csv`;
- `docs/DOCTORAL_NEXT_DATA_GATE_2026-08-19.md`;
- `sampling/SAMPLING_DESIGN.md`.

## Gate 2 operationalization

Aim 2 now uses four linked levels rather than one flattened field table:

1. individual/sample identity — `sampling/aim13_individual_sample_ledger_v1.csv`;
2. focal capitulum/treatment and final fitness — `sampling/aim2_capitulum_field_ledger_v1.csv`;
3. repeated time-stamped microclimate + pollinator + antagonist observation — `sampling/aim2_capitulum_observation_bout_ledger_v1.csv`;
4. plant-season display/predation — `sampling/aim2_plant_display_predation_ledger_v1.csv`.

Detailed protocol:

`docs/AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md`

Repeated bouts are not biological replicates. They remain linked to the same `capitulum_id`; final achene/seed output remains in the focal-capitulum table. Pollinator and antagonist channels stay separate rather than being collapsed into generic insect activity.

## What must be secured during flowering

- immutable individual/population IDs and voucher-linked phenotype;
- calibrated visible/UV colour;
- natural orientation and direct phyllary/spine traits;
- time-stamped head-scale microclimate where measurable;
- effective pollination and antagonist records on the same functional individuals/heads;
- total and filled achenes / mature seed output;
- Aim 3 floral RNA at late bud/pigmentation onset and pre-anthesis/fresh anthesis;
- separate pigment tissue linked to the same individual.

## Stop rules

- no heavy tree prerequisite for field sampling;
- no more broad climate-only preliminary models;
- no SRA/BLAST fishing as a substitute for morph-linked population/floral data;
- no broad interaction pooling simply because several studies exist;
- do not re-test whether insect antagonists can reduce *Cirsium* seed output; use that as an established quantitative prior and test **which module changes the cost**;
- no “adaptive radiation” claim until Aim 2 links a focal trait through interaction/protection to reproductive fitness.
