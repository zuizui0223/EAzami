# EAzami current state

Status date: 2026-08-21

## Doctoral center

> **Why did one young Japanese *Cirsium* radiation generate such large capitulum and ecological diversity so quickly, despite shallow lineage divergence?**

Central working hypothesis: **modular evolvability** — reusable standing variation, gene flow/introgression and cytotype/genome changes may allow phenotype modules to diverge faster than genome-wide lineage sorting.

This remains a hypothesis, not a conclusion. Current pattern-reduction results do not decisively distinguish modular evolvability from a common-lability full model.

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

## Aim 2 — quantified antagonist baseline

Canonical result:

`data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json`

Estimand:

`RR = viable/mature seed output under experimentally reduced insect herbivory / seed output under ambient herbivory`

Current harmonized coverage:

- **9 within-study contrasts**;
- **4 independent data-generation studies**;
- **2 *Cirsium* taxa/taxon concepts**.

Random-effects result:

- pooled **RR = 2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- 95% CI **58.1–66.6%**;
- **I² = 1.0%**.

Resolved:

> **insect herbivory on reproductive structures imposes a large and repeatable maternal-fitness cost in the currently harmonizable *Cirsium* experiments.**

Aim 2 therefore asks which capitulum modules alter this established antagonist cost, what pollination/abiotic costs accompany those modules, and whether the effect reaches reproductive fitness.

## Cross-layer pattern reduction — current conclusion

EAzami keeps the global Azami environment/trait layer observational and uses frozen Azami patterns plus independent interaction/fitness literature as mechanism-reduction targets.

The literature-number-rich registry contains concrete pollination, antagonist, display, orientation/rain, size-predation and colour-choice targets rather than only Azami environmental signs.

### 36-target v2 screen

Best-distance ranking in the seven-family screen:

1. FULL_MODULAR_HET — **7.61**
2. FULL_MODULAR_GLOBAL — **18.95**
3. FULL_COUPLED_HET — **25.49**
4. FULL_COUPLED_GLOBAL — **29.83**

Five fixed simulation replicates per parameter draw preserved the full-model ordering:

1. FULL_MODULAR_HET — **7.75**
2. FULL_MODULAR_GLOBAL — **23.03**
3. FULL_COUPLED_HET — **27.00**
4. FULL_COUPLED_GLOBAL — **37.22**

This demonstrates that the v2 ordering is not a single-simulation lottery, but it does not make the distances posterior model probabilities.

### Broader multi-seed held-out screen

The separate 31-row robust screen gives:

- full modular: accepted median core distance **0.287**, held-out reproduction **0.706**;
- full common-lability: **0.297**, held-out reproduction **0.689**;
- antagonist-only: **0.419**, held-out **0.417**;
- pollinator-only: **0.429**, held-out **0.317**;
- environment-only: **0.586**, held-out **0.133**.

The common-lability full model produced the only 11/11 core draw in that run. Therefore the defensible conclusion is:

> **joint environmental structure + mutualist response + antagonist cost is structurally supported much more strongly than any single-driver family; current evidence does not yet decisively distinguish common lability from modular evolvability.**

The simulations are structural-sufficiency screens, not likelihood fits, Bayes factors, posterior model probabilities or causal proof.

## Mechanism-gap reductions now completed

### Orientation

A static `orientation → pollinator preference` mechanism is insufficient for the current cross-study pattern. The reduced orientation screen instead requires separate candidate pathways:

- time-window pollination / thermal timing;
- rain/UV/wetting protection.

The field schema therefore preserves early-day versus later/all-day bouts, head-scale microclimate, wetting, pollen presentation/viability, effective contacts and final achenes. An all-day visitation null is not treated as evidence of no orientation effect.

### Pollinator display × density/context

Four *C. purpuratum* heads-probed slopes show residual under one shared mean and one shared density ratio. Exact log-space decomposition shows that context flexibility can remove the training residual, but the fully context-specific four-parameter form is saturated for four observations.

Predictive shrinkage/leave-one-out validation gives:

- shared density-only LOO log-RMSE = **0.244791**;
- partial-pooling LOO log-RMSE = **0.239090**;
- improvement = **2.33%**;
- effective df = **2.484**.

Decision:

> **do not promote unpooled year/site pollinator parameters into the full macro-interaction simulation yet.**

Instead the Aim 2 bout ledger records focal display, quantitative local plant/head density, `heads_probed_total`, visits and effective contacts so the context term can be estimated from replicated focal-system data with partial pooling.

### Flower colour

The former sign-only *C. palustre* prior `white preferred` is now quantitative. Six significant white-preference bee-type × population cases reconstructed from Mogford Fig. 24 give

`white selection ratio = white visit share / white morph share`

with:

- conditional range **1.1516–1.6118**;
- geometric mean **1.3019**.

This is a **soft, significance-conditioned calibration**, not a pooled effect: the cases are clustered within one study system and included because significant white preference was reported.

Decision:

> **do not hard-code `white always preferred`; measure the same availability-normalized selection ratio in the W/coloured focal system.**

The field schema now preserves focal `colour_class`, local same/alternative-colour open-head availability, pollinator visits and effective contacts within a defined colour-choice context.

Canonical note:

`docs/AIM2_CIRSIUM_PALUSTRE_COLOUR_PREFERENCE_2026-08-21.md`

## Aim 2 functional order

1. **head orientation first** — timing/protection pathways and reproductive fitness;
2. **W/coloured comparison second** — availability-normalized colour choice, effective contact, abiotic context and fitness, nested with Aim 3;
3. **phyllary/spine conditional third** — only after direct botanical validation and a defensible manipulation;
4. **stickiness lower priority / negative-control evidence**, not a generic defence proxy.

The image-derived involucre/spine metrics remain morphological proxies; existing antagonist costs do not prove these proxies are defensive traits.

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

Aim 2 measurements remain nested within the same ancestry-resolved populations. Exact P001–P014 localities remain field/current-source verified rather than invented.

## Three unresolved new-data gates

Doctoral execution remains compressed to **three unresolved new-data gates**; the mechanism reductions sharpen Gate 2 but do not add a fourth gate.

1. **Aim 1:** same-individual phenotype + population ancestry + plastid + cytotype to resolve standing variation vs introgression vs lineage-specific origin.
2. **Aim 2:** determine which ancestry-linked capitulum modules alter antagonist cost, pollination/protection pathways and reproductive fitness.
3. **Aim 3:** same-individual floral-stage RNA + coding/regulatory haplotype + pigment + calibrated colour in at least two independent W/C transitions.

Canonical execution files:

- `data/evidence/doctoral_next_data_minimum_v1.csv`;
- `docs/DOCTORAL_NEXT_DATA_GATE_2026-08-19.md`;
- `sampling/SAMPLING_DESIGN.md`.

## Gate 2 operationalization

Aim 2 uses four linked levels:

1. individual/sample identity — `sampling/aim13_individual_sample_ledger_v1.csv`;
2. focal capitulum/treatment and final fitness — `sampling/aim2_capitulum_field_ledger_v1.csv`;
3. repeated time-stamped microclimate + display/density/colour context + pollinator + antagonist observation — `sampling/aim2_capitulum_observation_bout_ledger_v1.csv`;
4. plant-season display/predation — `sampling/aim2_plant_display_predation_ledger_v1.csv`.

Repeated bouts are not biological replicates. Final achene/seed output remains in the focal-head table. Pollinator and antagonist channels stay separate.

Detailed protocol:

`docs/AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md`

## What must be secured during flowering

- immutable individual/population IDs and voucher-linked phenotype;
- calibrated visible/UV colour plus focal `colour_class`;
- natural orientation and direct phyllary/spine traits;
- time-stamped head-scale microclimate where measurable;
- focal display, quantitative local density and local colour availability;
- pollinator visits, heads probed and effective contacts as separate quantities;
- antagonist records on the same functional individuals/heads;
- total and filled achenes / mature seed output;
- Aim 3 floral RNA at late bud/pigmentation onset and pre-anthesis/fresh anthesis;
- separate pigment tissue linked to the same individual.

## Stop rules

- no heavy tree prerequisite for field sampling;
- no more broad climate-only preliminary models;
- no SRA/BLAST fishing as a substitute for morph-linked population/floral data;
- no broad interaction pooling simply because several studies exist;
- do not re-test whether insect antagonists can reduce *Cirsium* seed output; test **which module changes the cost**;
- no unpooled year/site pollinator parameter from four context slopes;
- no `white always preferred` parameter from significance-conditioned *C. palustre* cases;
- no colour-preference claim without local morph availability;
- no “adaptive radiation” claim until Aim 2 links a focal trait through interaction/protection to reproductive fitness.
