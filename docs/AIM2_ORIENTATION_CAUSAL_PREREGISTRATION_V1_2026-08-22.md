# Aim 2 orientation causal preregistration v1

Status: 2026-08-22

## Main question

Does capitulum orientation alter reproductive fitness in focal *Cirsium*, and if it does, which preregistered process channel carries the signal?

The generic interaction meta-analysis is now closed at its current decision ceiling. Orientation is the first focal causal system because existing evidence makes several distinguishable predictions while the current field ledgers already contain the necessary process measurements.

## Experimental contrast

Primary causal contrast:

`randomized non-destructive reorientation` vs `sham manipulation`

Prefer paired capitula within the same individual and phenological stage when at least two suitable heads are available. The plant is the biological block. Repeated observation bouts are repeated measurements, not independent biological replicates.

The treatment-assignment record is `sampling/aim2_orientation_treatment_assignment_v1.csv`. The existing focal-head and bout ledgers retain outcomes and process measurements.

### Randomization rules

- assign sham/reorientation before observing post-treatment visitor, wetting, damage or seed outcomes;
- pair heads within plant when feasible; record `matched_capitulum_id` and `randomization_block`;
- do not choose the visually best head for the active treatment;
- preserve natural, target and achieved orientation angles separately;
- record manipulation failure/attrition rather than silently dropping it;
- primary inference is intention-to-treat by assignment; achieved angle is a dose-response/per-protocol sensitivity.

No universal target angle is asserted here. The field operator must record the natural angle, preregistered target for that manipulation, and achieved angle. The scientific contrast is a controlled change in orientation relative to a sham, not an invented biological optimum.

## Preregistered hypotheses

Canonical machine-readable registry:

`data/evidence/aim2_orientation_causal_hypothesis_registry_v1.csv`

### ORI0 — null-compatible

No reproducible treatment effect is detected on candidate processes or final reproductive output.

Important boundary: failure to reject a treatment effect is not evidence for no orientation effect. An equivalence/null claim requires a smallest effect of interest frozen after a blinded variance pilot.

### ORI1 — time-window / thermal pollination

Prediction:

`orientation -> early head microclimate / early effective-contact efficiency -> seed fitness`

A whole-day visitation null does not falsify this mechanism. The preregistered discriminator is the early time window and effective contact, not total daily visitor count.

Working support requires both:

1. a treatment-linked early-window process shift; and
2. a final reproductive-output effect in a functionally coherent direction.

### ORI2 — wetting / pollen protection

Prediction:

`orientation -> wetting / pollen presentation or viability after wetting events -> seed fitness`

Dry observations are uninformative for this hypothesis. Evidence must come from actual wetting/rain contexts or a defensible standardized wetting contrast.

### ORI3 — antagonist exposure

Prediction:

`orientation -> antagonist exposure/damage -> seed fitness`

Low-enemy periods are low-information. The channel is supported only when the manipulation changes antagonist response/damage and reproductive output.

### ORI4 — combined partitioning / trade-off mitigation

At least two process families change and the combined change reaches reproductive output. This can be supported even when all-day pollinator visitation is unchanged.

This is the focal *Cirsium* test of the interaction-partitioning idea; it is not assumed in advance.

### ORI5 — unexplained direct or unmeasured pathway

If orientation changes reproductive output but none of ORI1–ORI3 shows a corresponding process shift, classify the mechanism as unresolved. Do not invent a new mediator after seeing the outcome.

## Primary estimand and model order

### 1. Total reproductive effect first

Primary endpoint: filled-achene output conditional on total achenes.

Planned model family:

`cbind(filled_achenes, total_achenes - filled_achenes) ~ assignment + preregistered baseline terms + population/block structure`

Use a binomial mixed model, with beta-binomial/overdispersion handling if diagnostics require it. Report total achenes and seed mass separately rather than collapsing all fitness components into one index.

Crucially, estimate the total assignment effect **before** conditioning on post-treatment mediators.

### 2. Process channels independently

Time-window pollination:
- effective contacts per observation time;
- treatment × `time_window_class` with the early window preregistered;
- head-surface temperature relative to air temperature;
- all-day visitor totals only as a secondary descriptor.

Wetting/protection:
- recent rainfall/wetting event context;
- capitulum and pollen wetting;
- pollen presentation and viability;
- link to final filled-achene output.

Antagonists:
- antagonist visits/events;
- florivory events/damage;
- seed-predator events/damage;
- link to final filled-achene output.

### 3. Mechanism classification

- ORI1/ORI2/ORI3 require a treatment-linked process shift plus a reproductive-output effect.
- ORI4 requires at least two preregistered process families plus reproductive output.
- ORI5 is used when fitness changes without a preregistered process signal.
- ORI0 remains `null-compatible` until an equivalence bound is frozen.

Do not report a formal mediated proportion unless the assumptions for causal mediation are separately justified. The initial goal is discriminating process consistency, not overclaiming mediation.

## Minimum repeated-bout structure

Every focal manipulated head should, where field conditions permit, have:

1. an early-day bout;
2. at least one later bout;
3. conditional follow-up after a genuine wetting/rain event if the head remains in the experiment;
4. antagonist follow-up over the relevant reproductive window;
5. final achene/seed outcome.

The assignment ledger records which follow-ups were required. Missingness and treatment integrity are part of the result.

## Attrition and integrity

Primary intention-to-treat set: all successfully randomized/initialized capitula for which the treatment was attempted.

Report separately:
- mechanical manipulation failure;
- head loss unrelated to the manipulation;
- herbivore destruction preventing final fitness measurement;
- observer/sensor failure;
- phenological mismatch discovered after assignment.

A per-protocol achieved-angle analysis is secondary and cannot replace the randomized contrast.

## What counts as a successful first tranche

The first tranche is successful even if the biological result is null or adverse, provided it does all of the following:

- preserves randomized treatment assignment and sham control;
- retains early and later time windows;
- separates visitor count from effective contacts;
- records wetting/viability when informative;
- records antagonist exposure separately;
- reaches total/filled achene outcomes;
- keeps plant and repeated-bout dependence explicit.

A null biological result is scientifically useful because it eliminates the preferred orientation mechanisms in the focal system rather than triggering post hoc model expansion.

## Stop rules

- no all-day-visitation shortcut;
- no visitor-count = fitness shortcut;
- no mediator-first model that conditions away the total treatment effect;
- no achieved-angle-only causal claim when assignment is randomized;
- no dry-period falsification of the wetting pathway;
- no low-enemy falsification of the antagonist pathway;
- no null claim without a frozen equivalence bound;
- no new mediator invented after inspecting seed outcomes;
- no adaptation claim unless an orientation treatment effect reaches reproductive output.

## Current state

The schema-level readiness validator is:

`analysis/validate_aim2_orientation_causal_design_v1.py`

It verifies that the existing ledgers plus the new treatment-assignment ledger contain all preregistered discriminators. Passing that validator means the design is ready to collect the required data; it does not mean any mechanism has been demonstrated.
