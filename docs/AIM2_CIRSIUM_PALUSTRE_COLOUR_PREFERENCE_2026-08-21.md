# Aim 2 colour-preference quantitative calibration

Status: 2026-08-21

## Question

Can the existing *Cirsium palustre* literature colour prior be represented as a quantitative target rather than only `white preferred`?

## Source and reconstruction

The published *Heredity* paper reports preferential pollination of the white morph. Mogford's 1972 Oxford DPhil thesis preserves the underlying Fig. 24 morph-frequency and bee-visit-frequency summaries.

For six bee-type × population cases reported as significant white preference and with reconstructable shares, define

`white selection ratio = white visit share / white morph share`.

Reconstructed ratios:

- 1.1569
- 1.6118
- 1.1516
- 1.2734
- 1.3813
- 1.2891

Summary:

- geometric mean = **1.3019**;
- median = **1.2813**;
- conditional range = **1.1516–1.6118**.

Canonical machine-readable files:

- `data/evidence/cirsium_palustre_colour_preference_fig24_v1.csv`;
- `data/evidence/cirsium_palustre_colour_preference_fig24_v1.json`;
- `analysis/reconstruct_cirsium_palustre_colour_preference_v1.py`.

## Interpretation boundary

This is **not a pooled effect size**. The six observations come from one study system, are clustered by population and bee type, and are included because significant white preference was reported. The range is therefore a significance-conditioned mechanistic calibration.

The correct use is:

- upgrade the target registry from a sign-only statement to a numerical soft range;
- do not hard-code `white always preferred`;
- do not interpret the geometric mean as a genus-wide average effect;
- allow the focal Ryukyu system to show weaker, null or reversed preference.

## Field consequence

The W/coloured comparison must estimate preference relative to local availability rather than compare raw visitor totals alone.

For each comparable observation context retain:

- focal `colour_class` linked to calibrated visible/UV/pigment data;
- `colour_choice_context_id`;
- local open capitula of the same colour class;
- local open capitula of the alternative colour class;
- pollinator visits and effective contacts separately;
- time window, local density and microclimate.

The target field quantity is a population/time-context-specific availability-normalized selection ratio, analyzed with repeated contexts partially pooled.

## Development decision

The colour gap is now **quantitative and field-testable**, but it is not yet a new scored degree of freedom in the full macro-interaction generator. Direct focal-system replication comes before adding a morph-specific colour-choice parameter to the full simulation.
