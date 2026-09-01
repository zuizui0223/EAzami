# Historical differentiation trigger result v1

Status date: 2026-09-01  
Status: **VALIDATED PUBLIC-DATA RESULT — historical differentiation only**

Source workflow: `33482748258`  
Source artifact: `9790559360`  
Artifact digest: `sha256:312688b31f5f987948a4210f95a3d55acda6b3fc32a61c4e23702ea84984e56e`

## Question

For the one orientation transition envelope that is currently bounded by both public chronology and explicit paleolocation alternatives, what environmental change occurred across the branch window **without using any present-day environmental effect as a prior**?

The focal event is the minimum erect/upward → nodding/downward change on the core-Nipponocirsium stem, after the erect *Cirsium morii* split and before the Japanese-core/Taiwan-core split.

The chronology envelope contains 94 admissible parent–child age pairs and four predeclared paleolocation regions, for 376 region × chronology scenarios. The chronology grid is a deterministic uncertainty envelope, not posterior samples.

## Result 1 — the central 0.79 → 0.74 Ma pair has an apparently coherent direction

At the central cross-study age pair, parent 0.79 Ma → child 0.74 Ma:

| Variable | Taiwan | Ryukyu corridor | Southern Japan | East-Asia core corridor |
| --- | ---: | ---: | ---: | ---: |
| BIO1 | −0.546 | −0.894 | −1.318 | −0.767 |
| BIO4 | −27.141 | −31.246 | −38.323 | −36.709 |
| BIO12 | +108.178 | +86.054 | −12.416 | +7.026 |
| BIO15 | −2.703 | −1.299 | −2.493 | −3.327 |

Thus the single central pair shows:

- BIO1 decrease in 4/4 regions;
- BIO4 decrease in 4/4;
- BIO15 decrease in 4/4;
- BIO12 increase in 3/4.

This central-pair pattern is descriptive only. It is not the uncertainty-propagated result.

## Result 2 — no tested climate-change direction survives the chronology × paleolocation envelope

Across all 94 chronology scenarios in every region, each variable's q05–q95 range crosses zero.

### BIO1

- Taiwan: q05 −3.250, median −0.892, q95 +1.482;
- Ryukyu: −4.092, −1.069, +2.075;
- Southern Japan: −5.489, −1.352, +3.096;
- East-Asia core corridor: −4.614, −1.253, +2.312.

Pooled across the 376 deterministic scenarios, 65.4% have negative BIO1 change and the median is −1.090. This is a directional tendency, but it is not robust to the full scenario envelope.

### BIO4

- Taiwan: q05 −78.840, median +27.349, q95 +139.530;
- Ryukyu: −73.350, +9.523, +107.774;
- Southern Japan: −88.198, +11.723, +139.378;
- East-Asia core corridor: −89.630, +19.156, +147.770.

The central 50-kyr pair is negative in all regions, but the broader chronology envelope is mostly positive. This is a direct example of why one central age pair cannot define a historical trigger.

### BIO12

- Taiwan: q05 −283.698, median +10.341, q95 +222.587;
- Ryukyu: −247.927, +2.768, +223.460;
- Southern Japan: −43.760, +6.039, +51.886;
- East-Asia core corridor: −51.447, −0.556, +51.956.

Pooled positive fraction = 0.521. There is no stable wetting or drying direction.

### BIO15

- Taiwan: q05 −6.789, median −0.820, q95 +5.852;
- Ryukyu: −5.488, −1.215, +2.276;
- Southern Japan: −6.044, +0.402, q95 +7.178;
- East-Asia core corridor: −5.362, −0.803, +4.014.

Again, no cross-region robust direction survives.

## Result 3 — matched-window background position is also unresolved

The same event changes were standardized against all same-duration windows stepped every 10 kyr within each paleolocation region. For BIO1/BIO4/BIO12/BIO15, the background-standardized q05–q95 ranges also cross zero in every region.

Therefore no variable is classified as consistently above or below same-duration background change under the full chronology × paleolocation envelope.

Machine decision:

`no_tested_climate_direction_survives_full_chronology_paleolocation_envelope`

## Can this identify a common differentiation trigger?

No — not yet.

The event ledger currently contains:

- **1** calendar + paleolocation + historical-environment evaluable transition envelope: orientation on the core-Nipponocirsium stem;
- **3** conditional flower-colour terminal branch envelopes whose transition timing/direction or historical driver is still conditional;
- **4** dated sister phenotype contrasts that are not reconstructed transitions;
- **2** dated range events whose ages are not the ages of stickiness transitions.

A repeated historical trigger requires at least two independently bounded homologous transition events. Orientation therefore remains:

`not_evaluable_single_dated_transition_event`

## Interpretation

The public data already support recurrence and relative evolutionary depth much more strongly than they support a common historical environmental trigger.

For the one orientation event that can be bounded in calendar time, a visually coherent central-age trajectory does **not** survive chronology and paleolocation uncertainty. The allowed conclusion is therefore:

> **The core-Nipponocirsium orientation differentiation can be placed within a young Pleistocene branch window, but no tested BIO1/BIO4/BIO12/BIO15 change direction is robust across the full public chronology × paleolocation envelope. A repeated environmental trigger remains unidentified because only one orientation transition is currently dateable at this resolution.**

This does not show that climate was irrelevant. A differentiation trigger could instead involve environmental level, extremes, variability, a shorter sub-window, range fragmentation, or a biotic variable. Those alternatives require separate tests.

## Claim boundary

- q05/q95 are summaries of a deterministic scenario grid, not credible intervals;
- the regional boxes are alternative paleolocations, not ancestral-area probabilities;
- the trait transition instant is unknown within the parent–child branch interval;
- historical alignment is not natural selection;
- one event cannot establish repeated environmental triggering;
- no Chapter 1 or present-day effect direction is used in this result.
