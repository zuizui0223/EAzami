# Aim 2 tranche-1 joint observation protocol

Status: 2026-08-21

## Purpose

Convert the quantified antagonist cost and mechanism-reduction results into field measurements without adding a new doctoral Aim.

The question is no longer whether insect antagonists can reduce *Cirsium* seed output. The direct meta-analysis already supports a large cost. The field question is which capitulum module changes antagonist cost, pollinator benefit or abiotic protection and whether that change reaches reproductive fitness.

## Data hierarchy

Keep four linked levels:

1. biological individual — `sampling/aim13_individual_sample_ledger_v1.csv`;
2. focal capitulum/treatment + final fitness — `sampling/aim2_capitulum_field_ledger_v1.csv`;
3. repeated observation bout — `sampling/aim2_capitulum_observation_bout_ledger_v1.csv`;
4. plant-season display/predation — `sampling/aim2_plant_display_predation_ledger_v1.csv`.

`individual_id` and `capitulum_id` are join keys. An observation bout is a repeated measurement, not a new biological replicate.

## Orientation-specific update

The reduced orientation screen showed that a static `orientation → pollinator preference` pathway is structurally insufficient for the current cross-study pattern.

The only model family that robustly reproduced all five core constraints combined:

- **time-window pollination/thermal timing**; and
- **rain/UV/wetting protection**.

This is a field-design prior, not proof of a Cirsium mechanism.

### Minimum bout record for orientation

Each orientation observation bout should now preserve:

- local start/end time and `time_window_class`;
- natural and achieved orientation angle;
- air temperature, head-surface temperature, relative humidity, wind and radiation when measurable;
- recent rainfall and capitulum wetness;
- pollen-presentation state;
- pollen wetting;
- pollen-viability sample ID and viability where feasible;
- pollinator visit count and effective contacts;
- antagonist visits/events separately;
- treatment integrity.

At minimum, retain an **early-day** window separately from later/all-day aggregation. Do not conclude that orientation has no pollinator effect merely because the whole-day visit total is null.

### Outcome link

The bout table stores process measurements. Final reproductive output remains in `aim2_capitulum_field_ledger_v1.csv`:

`orientation → timing/protection → pollen/contact → total/filled achenes`.

## Pollinator context / density update

The four published *C. purpuratum* probing slopes show residual when one annual mean and one density ratio are forced across 1997/1998. A follow-up shrinkage/leave-one-out check finds only about **2.3% predictive RMSE improvement** from adding year/context deviations, so unpooled temporal parameters are not promoted into the full simulation.

The field consequence is to collect the missing discriminator rather than make the model more complex now.

For comparable pollinator-response bouts, retain when feasible:

- `phenology_census_id` linking the bout to the plant-level census;
- `focal_open_capitula_current` as the contemporaneous focal display;
- `density_context_id`;
- `density_measurement_area_m2`;
- `local_conspecific_flowering_plants`;
- `local_conspecific_open_capitula`;
- `pollinator_visit_count` as plant-level foraging visits entering the focal individual/display;
- `heads_probed_total` across those visits;
- effective contacts separately.

This permits direct reconstruction of `heads probed per visit = heads_probed_total / pollinator_visit_count` and local plant/head density from counts plus measured area. Do not encode only a subjective `high/low density` label when quantitative counts and area can be obtained.

Repeated bouts across populations/time windows can later be analyzed with partial pooling. Until those replicated contexts exist, do not fit one unconstrained pollinator-response parameter per year or site.

## Colour-choice update

The *C. palustre* literature colour prior is now quantitative rather than sign-only. Reconstructed significant white-preference bee-type × population cases from Mogford Fig. 24 give

`white selection ratio = white visit share / white morph share`

with a conditional range **1.1516–1.6118** and geometric mean **1.3019** across six significant white-preference cases.

This is deliberately a **soft, significance-conditioned calibration**, not a pooled effect. The six cases are clustered within one study system and were selected because they showed significant white preference. They do not justify hard-coding `white always preferred` into the EAzami generator.

For the W/coloured tranche, preserve the quantities needed to calculate the same object directly:

- `colour_class` once per focal capitulum in `aim2_capitulum_field_ledger_v1.csv`, linked to the existing visible-colour standard, UV reflectance and pigment sample;
- `colour_choice_context_id` for a comparable local choice set;
- `local_open_capitula_same_colour_class`;
- `local_open_capitula_alternative_colour_class`;
- `pollinator_visit_count` and effective contact separately;
- the existing time-window, density and microclimate fields.

Do not substitute a subjective statement such as `pollinators preferred white` for availability-normalized counts. The analysis target is a population/time-context-specific selection ratio, with repeated contexts partially pooled. A null or reversed preference in the focal Ryukyu comparisons is a valid result.

## Channel separation

Never collapse these into one generic insect variable:

- pollinator visit count;
- heads probed per visit;
- effective pollination contact;
- antagonist visit/event count;
- florivory;
- pre-dispersal seed predation;
- final seed output.

Likewise, temperature/wetting, focal display, local density, local colour availability and visitor responses are separate candidate drivers/mediators; one is not used as a proxy for another.

## Field order

1. **Orientation first** — natural orientation + non-destructive reorientation/sham, with explicit early/later bouts and abiotic measurements.
2. **W/coloured second** — use `colour_class` plus quantitative local colour availability so selection ratios and effective contacts can be estimated in the same environmental/context frame.
3. **Phyllary/spine conditional third** — only after direct botanical validation and defensible manipulation.

## Analysis consequence

The first orientation field model should compare candidate mediation paths rather than fit one total-visitation coefficient:

- `orientation → head temperature/time-window visits → effective contact`;
- `orientation → wetting/pollen viability`;
- both paths → reproductive fitness.

The pollinator-context layer should test `focal display × local density/context → heads probed per visit / effective contact` with population/time context partially pooled rather than treated as four unrelated parameters.

The colour layer should test `focal colour × local colour availability/context → visit selection ratio → effective contact`, with the Mogford 1.15–1.61 interval used only as an external soft calibration, not as a required effect direction or magnitude.

Population/ancestry and individual/capitulum dependence must remain explicit.

## Stop rules

- bouts are not independent plants;
- no all-day-null shortcut;
- no visitor-count = fitness shortcut;
- no subjective density class when quantitative counts/area are feasible;
- no unpooled year/site pollinator parameter without replicated contexts;
- no `white always preferred` parameter from the Mogford cases;
- no colour-preference claim without local morph availability;
- no environment raster substitution for missing head-scale measurements;
- no adaptation claim until a focal trait effect reaches reproductive output;
- no claim that the comparison-system mechanism operates in *Cirsium* until tested directly.
