# JEB V7 figure map — positive assembly first

Status date: 2026-09-04  
Status: **VALIDATED MAP FOR V7 SCIENTIFIC TEXT**

## Paper spine

`diversity within dominant radiation -> repeated component histories -> unequal evolutionary depth / mosaic assembly -> scale- and history-conditioned present ecology -> calendar-time and historical-cause ceiling`

Historical-trigger failure is the terminal discrimination layer, not the opening biological result.

| Figure | Main question | Primary evidence | Main conclusion | Hard boundary |
| --- | --- | --- | --- | --- |
| Figure 1 | What diversity is being assembled? | dominant-radiation membership + authority configurations | substantial capitulum diversity occurs within one young radiation | descriptive diversity, not transition history or diversification rate |
| Figure 2 | How were three components assembled through the radiation? | minimum steps + depth envelopes + paired topology ordering + coverage-matched sensitivity + shared localization | repeated changes occupy unequal central depths and do not form one synchronized history | no independent origins, rates, coverage independence, adaptation or genetic modularity |
| Figure 3 | Is present ecological correspondence independent of biological scale and historical placement? | Azami within/among + EAzami orientation contrasts + nested counterfactual conditioning | orientation–environment correspondence is scale-partitioned and history-embedded | no pooling of estimands, ancestry-independent climate effect, selection or historical-cause claim |
| Figure 4 | What can the best-bounded orientation event tell us historically? | 94 chronologies × 4 regions + regional ranking + BIOCLIM | descriptive tendencies exist but do not survive the full uncertainty gate | scenario robustness is not ancestral-area probability |
| Figure 5 | How far does historical identifiability extend? | climate/sea-level decision counts + evidence hierarchy | phenotypic assembly is better identified than one recurring coarse historical cause | no environmental irrelevance; no local land-bridge inference |

# Figure 1 — Diversity within the dominant radiation

### Panel 1A — nuclear radiation context
- compact accepted Japan38/Comp1061 scaffold;
- annotate `36 / 38 sampled Japanese concepts in dominant radiation`;
- keep admission/provenance exceptions in a small note.

### Panel 1B — authority-backed configuration matrix
Rows are admitted taxon concepts; columns are orientation, phyllary posture and stickiness. Missing/ambiguous states remain explicit.

### Panel 1C — observed configuration summary
Show multiple capitulum configurations within the dominant radiation. Do not imply correlated evolution.

**Figure 1 claim:** Multiple capitulum configurations occur within the same dominant young radiation.

# Figure 2 — Repeated mosaic assembly at unequal evolutionary depths

This is the headline figure.

### Panel 2A — minimum-change distributions
- orientation: ML 6; UFBoot 4–6, median 5;
- phyllary: exactly 3;
- stickiness: exactly 5.

Caption: `minimum changes are lower bounds, not independent origins or rates`.

### Panel 2B — exact relative-depth envelopes
Source: `japan38_relative_event_depth_v1.json`.

UFBoot median envelopes:
- orientation 0.795–0.994;
- phyllary 0.695–1.000;
- stickiness 0.937–0.954.

Axis: `relative lineage depth (1 = terminal; topology only, not time)`.

### Panel 2C — validated paired-topology ordering
Source: `chapter2_depth_ordering_robustness_result_v1.json`.

Show the exact topology-sensitivity fractions:
- phyllary < stickiness: **1000/1000 = 1.000**;
- phyllary < orientation: **993/1000 = 0.993**;
- orientation < stickiness: **905/1000 = 0.905**, with 7 ties;
- complete `phyllary < orientation < stickiness`: **898/1000 = 0.898**.

Optionally annotate median paired lower-bound differences:
- phyllary − stickiness −0.24762;
- phyllary − orientation −0.11905;
- orientation − stickiness −0.10857.

These are topology-sensitivity descriptors, not probabilities.

### Panel 2D — coverage-matched missing-state bound
Source: `chapter2_depth_coverage_matched_sensitivity_result_v1.json`.

Equalize known states to n=10 while keeping the 36-tip topology fixed.
- phyllary deeper than coverage-matched orientation median: **195/200 = 97.5%**;
- phyllary deeper than coverage-matched stickiness median: **193/200 = 96.5%** for both 5/5 and 6/4 profiles;
- phyllary deeper than orientation matched q05: **10.5%**;
- phyllary deeper than stickiness matched q05: **11.0–15.5%**.

Visual message: **central ordering retained; strict tail overlap remains**. Do not label the result coverage-independent.

### Panel 2E — shared-transition localization
Compact matrix of the three trait pairs. Headline: `0 / 3 pass the robust shared-transition-localization rule`.

### Figure 2 side note — turnover burden
- orientation 6/20 = 0.300;
- phyllary 3/10 = 0.300;
- stickiness 5/13 = 0.385.

Because state ontologies differ, these are descriptive burdens, not rates. Do not say `same lability, different depth`.

**Figure 2 claim:** Three components changed repeatedly and retain a strong central depth ordering across topology and matched-state-coverage sensitivities, while deep tails overlap and the components do not repeatedly share one synchronized transition history.

# Figure 3 — Orientation ecology is scale- and history-conditioned

The figure now has four linked questions: at what biological scale does orientation correspond to environment; whether transition direction tracks a fixed present-niche regime; which falsifications that regime survives; and how the earlier history-conditioned null changes the interpretation of tip-level extremeness.

### Panel 3A — cross-scale effect/support matrix
Three rows = BIO12, BIO15, BIO1. Three evidence columns = Azami within-taxon, Azami among-taxon, EAzami East-Asian state comparison.

- BIO12: within +0.00533, q=0.874; among +0.30436, q=0.00640 — `among_only`.
- BIO15: within -0.00762, q=0.121; among +0.0670, q=0.599; East-Asian D-U +1.320 to +1.330 SD, sign stable 6/6 topologies and 54/54 topology x species-LOO fits.
- BIO1: within +0.01715, q=0.0349; among -0.03024, q=0.836; East-Asian D-U approximately -0.975 to -0.967 SD, 54/54 sign stable.

Keep the three columns visually distinct because they are non-exchangeable estimands.

### Panel 3B — fixed transition-regime test
Source: `chapter2_orientation_transition_regime_hypothesis_result_v1.json` plus the strict-panel robustness result.

Plot exact finite-map ranks for the predeclared `BIO15 up + BIO1 down` U->D composite:

- n>=5, 12 taxa: **16/792 = 2.02%**;
- n>=3, 13 taxa: **19/1716 = 1.11%**;
- strict n>=10, 9 taxa: **4/126 = 3.17%**.

Show strict single-axis ranks as a small annotation:

- BIO15 alone: **7/126 = 5.56%**;
- lower BIO1 alone: **8/126 = 6.35%**;
- composite: **4/126 = 3.17%**.

Also annotate the bidirectional strict result: U->D and D->U both positive on 6/6 topologies; exact bidirectional-floor rank **3/126 = 2.38%**. Label this `present-niche tracking`, not adaptation or climatic causation.

### Panel 3C — falsification ladder for U->D tracking
Use a compact stress-test matrix, not multiple hypothesis numbers.

- strict n>=10: **4/126 = 3.17%** — pass;
- Japan-only n>=5: **10/56 = 17.86%** — directional but not exceptional;
- delete each strict-panel taxon: direction retained in **9/9** deletion panels; exact extremeness deletion-sensitive;
- linear latitude/longitude residualization: **5/126 = 3.97%** — pass;
- internal-edge-only scoring: **3/126 = 2.38%** — pass;
- geography residualization + internal-edge-only: **3/126 = 2.38%** — pass;
- combined-stress n>=5 sensitivity: **29/792 = 3.66%** — pass.

Visual message: the transition-regime direction is not a one-taxon, simple linear geography, or terminal-edge artefact under the declared reconstruction, but it is region-sensitive.

### Panel 3D — history-conditioned tip-contrast calibration
Retain the earlier counterfactual conditioning ladder for BIO15 as a methodological boundary:

- same state frequency: **5/126 = 3.97%**;
- same recurrence: **3/40 = 7.5%**;
- recurrence + nearest relative depth: **3/10 = 30%**.

Label the x-axis `state frequency -> recurrence -> recurrence + relative depth`. These are finite conditional ranks, not P values. Note that a recurrence-matched reverse world reaches -1.784 but no reverse BIO15 world occurs in the nearest-history pool.

### Figure 3 boundary

The transition-regime analyses use reconstructed branches from present-day niche centroids. Geography residualization removes only linear latitude/longitude structure, and internal-edge support is not observed ancestral climate. The analyses do not establish selection, adaptation, historical exposure or a mediator. **No three-trait** depth x ecological-reach regression is allowed.

**Figure 3 claim:** Present orientation ecology is scale-partitioned and history-embedded, while transition direction additionally tracks a fixed East-Asian composite present-niche regime that survives the declared strict-coverage, single-taxon, simple-geography and internal-edge falsifications but is not a universal Japan-only rule.

# Figure 4 — Bounded orientation history: tendency versus uncertainty

### Panel 4A — chronology gate
Core-*Nipponocirsium* orientation bridge; central chronology 0.79–0.74 Ma; 94 admissible chronology pairs × four regions = 376 scenarios.

### Panel 4B — regional ordering
- southern Japan rank 1: 48/94;
- southern Japan > Taiwan: 61/94;
- > Ryukyu: 61/94;
- > East-Asian core: 64/94.

Show the frozen 75% dominance gate. Label these `scenario-wise ranking robustness`, not probabilities.

### Panel 4C — central climate trajectory
At 0.79–0.74 Ma, BIO1/BIO4/BIO15 decrease in all four regions; BIO12 increases in three of four. Explicitly descriptive.

### Panel 4D — present-regime persistence falsification
The fixed current U->D sign combination (`BIO15 delta > 0`, `BIO1 delta < 0`) matches only **99/376 = 26.3%** scenarios: Taiwan 20/94, Ryukyu 9/94, southern Japan 41/94, East-Asian core 29/94. At the central 0.79–0.74 Ma chronology, BIO1 decreases in all four regions but BIO15 also decreases in all four, so the current-regime sign test fails in 4/4 central regional scenarios. No broader tested BIO1/BIO4/BIO12/BIO15 direction, level, absolute change or variability class survives the full chronology x palaeolocation envelope.

**Figure 4 claim:** The best-bounded event contains regional and climate tendencies, but the fixed present transition-niche regime is not supported as a persistent origin regime across admitted timing and palaeolocation uncertainty.

# Figure 5 — Historical identifiability ceiling

### Panel 5A — evidence funnel
1. configuration diversity — resolved;
2. repeated minimum histories — resolved for three traits;
3. relative depth — resolved with topology and coverage sensitivity bounds;
4. present ecological correspondence — scale-partitioned, history-conditioned and transition-linked for orientation;
5. shared named/localized history — partial;
6. calendar-linked trait events — sparse;
7. recurring historical cause — not identified.

### Panel 5B — broader climate diagnostic
17 BIOCLIM variables; six dated lineage contexts; 15,472 scenario × variable combinations; **0/324** robust event-level classes.

### Panel 5C — global sea-level diagnostic
Three representative clades × seven metrics; **0/21** robust event-metric classes.

### Panel 5D — interpretation box
`phenotypic assembly is identifiable farther than recurring historical cause`.

**Figure 5 claim:** Public data resolve repeated mosaic assembly and unequal central evolutionary depth much more strongly than one recurring coarse historical cause.

# Supporting / companion routing

## SI — ecological resolution audit
`chapter2_discrete_trait_occurrence_gate_sensitivity_v1.json`
- n≥10 makes phyllary and stickiness state-degenerate;
- n≥5 restores stickiness diversity only through one sticky lineage;
- phyllary remains state-degenerate;
- broader environment-free occurrence support contains state-diverse phyllary and balanced 6/6 sticky/nonsticky panels.

## SI — coverage sensitivity details
Full mask distributions and topology summaries from `chapter2_depth_coverage_matched_sensitivity_result_v1.json` belong in SI even if Panel 2D shows the headline fractions.

## SI — counterfactual ecology details
Full 126 assignment table and BIO15/BIO1 signed statistics belong in SI. The main figure should show only the nested conditional ranks and reverse-direction availability.

## Companion mechanism prior
East-Asian *Cirsium* antagonist pathway/regime evidence remains a mechanistic prior. The RR=2.674 experimental anchor is not an East-Asian measured effect and does not identify a focal historical transition mechanism.

# Final display gates

1. Minimum changes are not independent origins or convergence.
2. Relative depth is not time, age or evolutionary rate.
3. UFBoot fractions are not posterior probabilities or independent replicate frequencies.
4. Coverage matching supports a central ordering but strict tail overlap prevents a coverage-independence claim.
5. Within/among/East-Asian ecological estimands are not pooled.
6. Counterfactual conditional ranks are not P values or independent confirmations.
7. Do not call BIO15 an ancestry-independent climate effect; the observed magnitude is not exceptional in the nearest-history pool.
8. No three-trait `depth × ecological reach` correlation is identified.
9. Regional scenario fractions are not ancestral-area probabilities.
10. Global sea level is not local palaeogeography.
11. `0/324` and `0/21` constrain tested coarse regimes, not the importance of environment generally.
12. Main visual emphasis remains on assembly history; mechanism priors and resolution audits stay supporting/companion.
