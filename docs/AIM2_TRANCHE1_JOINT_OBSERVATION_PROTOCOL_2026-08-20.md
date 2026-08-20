# Aim 2 tranche-1 joint observation protocol

Status: 2026-08-20

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

## Channel separation

Never collapse these into one generic insect variable:

- pollinator visit count;
- effective pollination contact;
- antagonist visit/event count;
- florivory;
- pre-dispersal seed predation;
- final seed output.

Likewise, temperature/wetting and visitor responses are separate candidate mediators; one is not used as a proxy for the other.

## Field order

1. **Orientation first** — natural orientation + non-destructive reorientation/sham, with explicit early/later bouts and abiotic measurements.
2. **W/coloured second** — reuse the joint bout structure so colour effects are not inferred from visitor counts without contemporaneous environment/effective contact.
3. **Phyllary/spine conditional third** — only after direct botanical validation and defensible manipulation.

## Analysis consequence

The first orientation field model should compare candidate mediation paths rather than fit one total-visitation coefficient:

- `orientation → head temperature/time-window visits → effective contact`;
- `orientation → wetting/pollen viability`;
- both paths → reproductive fitness.

Population/ancestry and individual/capitulum dependence must remain explicit.

## Stop rules

- bouts are not independent plants;
- no all-day-null shortcut;
- no visitor-count = fitness shortcut;
- no environment raster substitution for missing head-scale measurements;
- no adaptation claim until a focal orientation effect reaches reproductive output;
- no claim that the comparison-system mechanism operates in *Cirsium* until tested directly.
