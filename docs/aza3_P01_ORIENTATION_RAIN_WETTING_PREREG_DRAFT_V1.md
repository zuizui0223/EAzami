# aza3 P01 — orientation × rain/wetting causal test — preregistration draft

Status: **DRAFT — NOT FIELD AUTHORIZATION**  
Parent evidence: EAzami V10  
Date: 2026-10-04

## Question

Does downward capitulum orientation protect *Cirsium* reproductive performance specifically under rain/wetting exposure?

## Primary hypothesis

The causal hypothesis is an interaction:

`orientation manipulation × wetting exposure → reproductive process → filled viable achenes`.

The hypothesis does not predict a necessary downward-orientation fitness advantage under dry conditions.

## Experimental unit

One focal capitulum is the experimental unit.

Plant identity, population, date/block and phenological stage must be recorded before treatment assignment.

Use one experimental capitulum per individual unless a separate pre-field validation establishes that within-plant paired heads do not create resource-coupling or treatment-spillover problems.

## Arms

Minimum three-arm design:

1. natural downward control;
2. experimentally reoriented upward;
3. sham-handled downward.

The reorientation method must be reversible, must not damage peduncle vascular tissue and must pass a pre-field mechanical validation showing that the achieved angle remains separated from control/sham for the declared observation window.

## Eligibility

Before randomization:

- naturally downward focal state verified in the live population;
- capitulum in the preregistered phenological window;
- no severe pre-existing damage;
- plant/capitulum unique ID assigned;
- required permissions and conservation constraints satisfied;
- expected sample size feasible without exceeding the declared population fraction.

No replacement after treatment assignment.

## Orientation measurement

Record gravity-referenced angle, not image-frame angle.

Required times:

- baseline before treatment;
- immediately after treatment;
- each mechanistic observation window;
- after major rain events;
- final pre-harvest check.

Manipulation fidelity is a mediator/QC endpoint, not a reason to silently exclude assigned heads.

## Wetting exposure

The preferred primary mediator is **wetness duration** at or within the capitulum.

Before field execution, choose one validated implementation:

- miniature wetness sensor;
- standardized absorbent/indicator proxy;
- repeated direct wetness score with calibration against a sensor subset.

Rainfall from a nearby weather station alone is insufficient as the primary mediator because treatment is hypothesized to alter actual head exposure.

Record rainfall amount/event identity as environmental context.

## Reproductive-process mediators

Primary mediator family:

- wetness duration / water retention;
- pollen viability or validated pollen-performance assay after exposure;
- stigma pollen deposition.

Secondary competing pathways:

- effective pollinator contact;
- florivore/seed-predator visitation;
- internal/head temperature and humidity.

The final preregistration must select one primary mechanistic chain before outcome opening.

## Primary fitness outcome

Filled/viable achene proportion per experimental capitulum.

Required denominator definition must be frozen before harvest scoring.

Secondary:

- filled/viable achene count;
- total achene count;
- seed mass.

## Primary estimand

Treatment × wetting interaction on the primary fitness outcome.

The primary biological prediction is:

`upward manipulation becomes increasingly costly as wetting exposure increases`.

A treatment main effect without the interaction is secondary.

## Mechanistic confirmation rule

The rain/wetting-protection mechanism requires both:

1. upward manipulation increases the preregistered wetting mediator relative to sham/control; and
2. the increased mediator predicts deterioration in the preregistered reproductive-process endpoint and/or the treatment × wetting interaction predicts reduced filled-achene performance in the declared direction.

A seed effect alone is not sufficient to call rain protection confirmed.

## Falsification hierarchy

### F0 — manipulation failure
Gravity-referenced orientation does not separate among arms.

Interpretation: experiment mechanically non-informative.

### F1 — exposure failure
Orientation separates, but wetting exposure does not.

Interpretation: rain/wetting mechanism not supported in the tested implementation/context.

### F2 — process failure
Orientation changes wetting, but the preregistered reproductive-process mediator does not respond.

Interpretation: exposure changes but the proposed reproductive mechanism is not supported.

### F3 — fitness failure
Exposure/process mediators respond, but filled-achene performance does not.

Interpretation: mechanism exists but adaptive fitness consequence is not demonstrated.

### F4 — causal-chain support
Trait, exposure mediator, reproductive process and fitness move in the preregistered causal direction.

Only F4 supports the full focal adaptation mechanism in the tested population/context.

## Rain-event analysis

Rain events must be defined without reference to reproductive outcomes.

If event-level repeated measurements are used, event ID is a repeated-measure grouping variable; heads/plants are not treated as independent at each event.

Dry versus wet categorization, if used, must be defined before seed outcomes are opened.

## Randomization and blocking

Randomize treatment only after eligibility and baseline variables are frozen.

At minimum block/stratify by:

- population/site;
- date or phenological cohort;
- capitulum size class if strongly predictive.

The exact randomization seed and algorithm must be committed before assignment.

## Sample-size gate

No numerical target is frozen in this draft.

Before field authorization:

1. choose the primary outcome distribution;
2. define the minimum biologically relevant treatment × wetting interaction;
3. estimate variance/ICC from pilot or defensible prior data;
4. simulate power/precision under rain-event imbalance;
5. check population/conservation constraints.

Do not select sample size from the smallest value yielding nominal significance in retrospective data.

## Analysis skeleton

Primary model family must match the frozen outcome:

- filled-achene count with denominator/total available: binomial or beta-binomial mixed model where appropriate;
- count without valid denominator: declared count model;
- plant/site/event random effects only where design supports them.

Primary fixed effects:

`treatment + wetting + treatment × wetting`.

Predeclared covariates may include baseline capitulum size and phenological stage.

## Claim ceiling

Even a successful P01 establishes adaptation only for the manipulated orientation mechanism in the tested ecological context.

It does not prove:

- that every historical U→D transition had the same cause;
- that BIO15 itself was the selective agent;
- that historical climate generated the original state;
- that orientation has no pollination or antagonist function.

## Field-authorization gate

This document is a design draft, not permission to manipulate plants.

Field execution requires:

- focal taxon/population selection;
- live-state confirmation;
- permissions/conservation review;
- manipulation-feasibility pilot;
- sensor/mediator validation;
- sample-size and population-fraction contract;
- frozen randomization and analysis contract.
