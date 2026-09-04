# Chapter 2 materials routing after H1–H4

**Status date:** 2026-09-04  
**Purpose:** resolve material overload by assigning every active evidence lane a single manuscript role.  
**Rule:** one biological question -> one primary estimand -> one main figure. Sensitivities, mechanism priors and legacy exploratory lanes do not compete with the primary result.

# Paper structure: three questions only

## Q1. How was the multidimensional capitulum assembled within the young radiation?

**Primary answer:** repeated mosaic assembly at unequal evolutionary depths.

### MAIN-TEXT / MAIN-FIGURE REQUIRED

1. **Radiation scaffold and configuration diversity**
   - `data/evidence/japan38_comp1061_primary_tree_acceptance_v1.json`
   - authority-backed orientation/phyllary/stickiness state matrix
   - result: 36/38 sampled Japanese concepts in the dominant radiation, with multiple capitulum configurations.

2. **Three discrete histories**
   - `data/evidence/japan38_relative_event_depth_v1.json`
   - orientation: ML 6, UFBoot 4–6;
   - phyllary: exactly 3;
   - stickiness: exactly 5.

3. **Paired depth ordering**
   - `data/evidence/chapter2_depth_ordering_robustness_result_v1.json`
   - phyllary < stickiness: 1000/1000;
   - phyllary < orientation: 993/1000;
   - orientation < stickiness: 905/1000;
   - full order: 898/1000.

4. **Shared-transition localization**
   - current multitrait history evidence;
   - 0/3 trait pairs pass the robust shared-localization rule.

### SUPPORTING, NOT CO-EQUAL

- `data/evidence/chapter2_depth_coverage_matched_sensitivity_result_v1.json`
  - central phyllary-deeper ordering retained at 97.5% / 96.5%;
  - deep q05 tails overlap.
- minimum-change burden audit (6/20, 3/10, 5/13): descriptive only.
- topology-specific forced-edge/localization summaries.

### BOUNDARY / FALSIFICATION

- reconstruction-aware continuous branch-change null:
  - P=0.3504 original;
  - P=0.1959 JPN29-excluded sensitivity.
- continuous-trait phylogenetic-retention negatives.

**Routing:** these explain why the paper uses discrete histories and why "coordinated remodeling" was abandoned. They belong in Methods/Discussion or SI, not the headline Results.

### SI-ONLY

- full 1,000-tree depth distributions;
- all coverage masks and topology × mask outputs;
- authority crosswalk details;
- full shared-localization matrices;
- species-tip polymorphism/resolution audits.

### ARCHIVE / FUTURE

- continuous Japan38 history requiring better scalar coverage;
- colour/lightness historical lanes;
- cytotype as a sparse explanatory lane;
- population-level ancestry needed to distinguish ancestral retention / independent origin / introgression.

---

## Q2. Does orientation track present ecological regimes, and is that tracking tied to state transitions?

**Primary answer:** yes, under the declared East-Asian panel orientation shows distributed bidirectional present-niche tracking of a fixed composite regime; it is not a single-variable BIO15 effect and is region/context sensitive.

### MAIN-TEXT / MAIN-FIGURE REQUIRED

1. **Cross-scale ecological context**
   - Azami within/among orientation evidence + East-Asian state contrasts.
   - BIO12: among-only;
   - BIO1: within-supported plus East-Asian D-U negative;
   - BIO15: East-Asian D-U +1.320 to +1.330 SD, 6/6 topology and 54/54 LOO sign stability, without a matching positive within-taxon Azami result.

2. **H1 transition-regime test**
   - `data/evidence/chapter2_orientation_transition_regime_hypothesis_result_v1.json`
   - fixed vector: U->D aligns with BIO15 up + BIO1 down;
   - n>=5: 16/792 = 2.02%;
   - n>=3: 19/1716 = 1.11%;
   - strict n>=10: 4/126 = 3.17%.

3. **H2 directional decomposition**
   - `data/evidence/chapter2_orientation_transition_directionality_result_v1.json`
   - U->D forward alignment median 0.320891;
   - D->U reverse alignment median 0.339529;
   - both positive 6/6 topologies;
   - bidirectional floor exact rank 3/126 = 2.38%.

### SUPPORTING, NOT CO-EQUAL

- `data/evidence/chapter2_orientation_transition_directionality_single_deletion_result_v1.json`
  - both directions remain positive after 9/9 single-taxon deletions;
  - exact <=0.05 survives 3/9 only.
- strict-coverage robustness and n>=5/n>=3 panel expansion.
- geography-adjusted and Japan-only diagnostics.

### BOUNDARY / FALSIFICATION

1. **Japan-only boundary**
   - same fixed H1 vector: 10/56 = 17.86%;
   - therefore not a Japan-only universal rule.

2. **Axis-specificity failure**
   - BIO15 does not retain a robust ancestry-independent effect after BIO1/geography adjustment and panel expansion;
   - the supported object is the composite regime, not BIO15 alone.

3. **Single-taxon deletion exact-rank sensitivity**
   - H1 exact <=0.05 survives 2/9 deletions;
   - H2 exact <=0.05 survives 3/9 deletions;
   - direction is distributed, extremeness is multi-taxon-configuration dependent.

### SI-ONLY

1. **Counterfactual conditioning ladder**
   - `data/evidence/chapter2_orientation_environment_counterfactual_result_v1.json`
   - BIO15 5/126 -> 3/40 -> 3/10;
   - important methodological result, but no longer the main biological panel after H1/H2.

2. Full 126/792/1716 state-map tables.
3. All per-topology H1/H2 values.
4. All single-taxon deletion ranks.
5. Raw PGLS/geography/coverage-resolution diagnostics.
6. phyllary/stickiness occurrence-gate audit: confirms why no three-trait depth × ecology analysis is allowed.

### MECHANISM PRIOR ONLY

- *Cremanthodium* capitulum-orientation manipulation / abiotic-protection evidence;
- East-Asian/Japanese *Cirsium* antagonist regime evidence;
- reproductive-herbivory RR=2.674;
- pollinator/antagonist selection-mosaic literature.

**Routing:** one short Discussion paragraph. These are biological plausibility constraints, not focal East-Asian causal evidence.

### ARCHIVE / FUTURE

- broad colour × RSDS sister-system analyses;
- static pollinator/antagonist dominance simulations;
- further indiscriminate BIOCLIM screening.

---

## Q3. Does the present orientation–niche regime explain the historical origin of the orientation transition?

**Primary answer:** no. The current regime does not persist across the uncertainty envelope of the only calendarized U->D event; present ecological tracking and origin-time environment are decoupled under current evidence.

### MAIN-TEXT / MAIN-FIGURE REQUIRED

1. **Only bounded orientation event**
   - core-*Nipponocirsium* U->D event;
   - central chronology 0.79–0.74 Ma;
   - 94 admissible chronology pairs × four palaeolocation regions = 376 scenarios.

2. **H4 historical-regime persistence test**
   - `data/evidence/chapter2_orientation_historical_regime_persistence_result_v1.json`
   - fixed sign expectation: BIO15 delta > 0 AND BIO1 delta < 0;
   - overall match: 99/376 = 26.3%;
   - Taiwan 21.3%; Ryukyu 9.6%; southern Japan 43.6%; East-Asia core 30.9%;
   - only 6/94 chronology pairs match 4/4 regions;
   - central 0.79–0.74 Ma mismatches in all four regions because BIO15 decreases while BIO1 also decreases.

### SUPPORTING, NOT CO-EQUAL

- regional ranking:
  - southern Japan rank 1 = 48/94;
  - pairwise leading fractions 61/94, 61/94, 64/94;
  - none crosses 75% dominance.
- central chronology descriptive BIO1/BIO4/BIO12/BIO15 trajectory.

### BOUNDARY / FALSIFICATION

- full historical environment gate: no BIO1/BIO4/BIO12/BIO15 direction, level, absolute change or variability is robust across the complete chronology × palaeolocation envelope;
- broader 17-BIOCLIM atlas: 0/324 robust event-level classes;
- sea-level diagnostic: 0/21 robust classes.

**Routing:** H4 is main. `0/324` and `0/21` are boundary support, not separate headline discoveries.

### SI-ONLY

- all 376 H4 scenarios;
- complete regional rankings;
- all matched-window paleoclimate diagnostics;
- 17-BIOCLIM and sea-level tables;
- chronology/palaeolocation construction details.

### ARCHIVE / FUTURE

- dated-tree author request/recovery programme;
- local palaeogeographic reconstruction;
- assigning dates to multiple Japan38 transition-bearing branches;
- population genomics / RAD-seq ancestry discrimination.

---

# Main manuscript material budget

The main paper should now use only the following biological evidence blocks:

1. **Young-radiation diversity** — scaffold + configuration matrix.
2. **Mosaic assembly** — minimum histories + unequal depth + 0/3 shared localization.
3. **Present orientation tracking** — cross-scale context + H1 + H2.
4. **Origin decoupling** — one bounded event + H4.

Everything else must justify, falsify or bound one of these four blocks. No fifth biological storyline is admitted.

# Recommended main-figure reduction: 5 -> 4

## Figure 1 — Diversity within one young radiation
- accepted scaffold;
- 36/38 annotation;
- authority-backed configuration matrix.

## Figure 2 — Mosaic assembly at unequal evolutionary depths
- minimum changes;
- depth envelopes;
- paired ordering;
- one compact coverage-bound panel;
- 0/3 shared localization.

## Figure 3 — Orientation tracks a present composite regime in both directions
- small cross-scale context panel;
- H1 exact rank for strict/expanded panels;
- H2 forward versus reverse alignment;
- H3 deletion robustness as a compact strip.

**Remove from the main figure:** the old 5/126 -> 3/40 -> 3/10 counterfactual ladder. Keep it in SI/methodological supplement because H1/H2 now test the biological hypothesis more directly.

## Figure 4 — Present tracking does not identify the origin regime
- conceptual current-regime vector;
- H4 per-region match fractions;
- 99/376 overall;
- central chronology mismatch;
- small evidence-ceiling inset (`only one event calendarized`; 0/324 and 0/21 can be SI or a tiny boundary note).

**Drop old Figure 5 as a standalone main figure.** Its identifiability funnel remains useful in Discussion/SI but no longer deserves equal visual weight with H1/H2/H4.

# Material classes

## A. PRIMARY MAINLINE
- scaffold / configuration diversity;
- three discrete histories;
- relative-depth ordering;
- H1;
- H2;
- H4.

## B. ROBUSTNESS SUPPORT
- coverage matching;
- H1 strict/n>=3 sensitivity;
- H3 single-taxon deletion;
- geography adjustment;
- regional ranking.

## C. FALSIFICATION / CLAIM BOUNDARY
- reconstruction-aware null;
- BIO15 axis-specificity failure;
- Japan-only H1 failure;
- H4 non-persistence;
- 0/324 climate and 0/21 sea-level coarse-regime results.

## D. SI / AUDIT
- full masks, state maps, topology tables;
- occurrence gates;
- full paleoclimate scenario grids;
- old counterfactual conditioning ladder;
- exact authority/provenance ledgers.

## E. FUTURE / CHAPTER 3 / STOPPED
- direct wetting/radiation -> pollen/stigma -> achene-fitness experiment;
- population genomics / plastid / cytotype ancestry discrimination;
- dated reconciled topology ensemble;
- phyllary and stickiness ecology after state-balanced sampling;
- colour/RSDS side line;
- generic mechanism meta-analysis beyond its current prior role;
- additional broad climate-variable fishing.

# What should disappear from the V8 main text

These materials remain scientifically useful but should not receive standalone Results subsections:

- colour/RSDS sister-system results;
- cytotype/ploidy descriptive lane;
- colonization/secondary-arrival contextual synthesis;
- generic pollinator/antagonist meta-analysis;
- auxiliary simulation winner/adequacy results;
- pre-tree disparity and phylomorphospace pilots;
- old continuous-trait branch-correlation result except as a short methodological provenance point;
- broad 17-BIOCLIM and sea-level atlases except as one historical-cause boundary sentence.

# Final one-line routing rule

> **If a result does not directly answer assembly, present transition-regime tracking, or origin-regime persistence, it is not a main-text biological result in the current Chapter 2.**
