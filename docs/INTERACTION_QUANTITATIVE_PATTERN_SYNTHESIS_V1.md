# Quantitative biological-interaction pattern synthesis

Status: 2026-08-20

## Purpose

This file is the biological-interaction counterpart to the frozen Azami observational pattern layer.

Azami asks:

> What global capitulum patterns are visible, and how are they environmentally structured?

This ledger asks:

> What quantitative constraints do pollinators, antagonists and abiotic protection impose on a generative mechanism that claims to explain those patterns?

Machine-readable source:

`data/evidence/interaction_quantitative_pattern_ledger_v1.csv`

The point is not to convert every paper into one pooled effect. The point is to retain the **recurrent numerical patterns, nonlinearities, nulls and scale dependencies** that a reduced mechanism must be able to generate.

## Six interaction patterns now supported

### 1. Pollinator benefit increases with floral display, but with diminishing return

*Cirsium purpuratum* provides the cleanest direct display experiment:

- display → relative bumblebee visitation: `R² = 0.637`, `n = 57`, saturating positive relationship;
- display → heads probed per plant visit: `R² = 0.533`, `n = 57`;
- predicted visitation per head was approximately independent of display within observation days.

Therefore a realistic mechanism should not use an indefinitely linear pollinator benefit. Larger displays attract more visits at the plant level, while per-head benefit can saturate.

### 2. The same advertisement can increase antagonist exposure

In *C. purpuratum*, seed predation increased with flower production:

- Nikko: `R² = 0.44`, `n = 13`;
- Kawamata: `R² = 0.26`, `n = 27`;
- in the Nikko multivariate model, floret number had standardized coefficient `0.86`, `t = 2.34`, `P = 0.048` for damaged-seed proportion.

The same principle occurs in a different signalling channel. Floral scent compounds of *C. arvense* attracted more than 10 pollinator species and 16 florivore species; the dominant scent components attracted both guilds.

Thus the trade-off is not restricted to one trait: **advertisement can be a shared mutualist/antagonist signal**.

### 3. Antagonist cost is large enough to be a primary fitness term

The direct *Cirsium* seed-output lnRR meta-analysis estimates:

- reduced-herbivory / ambient-herbivory seed output RR = **2.674**;
- 95% CI **2.388–2.993**;
- equivalent ambient-herbivory loss of potential seed output = **62.6%**;
- I² ≈ **1%** across the current harmonizable study set.

Independent held-out field patterns are compatible with a large cost:

- *C. canescens*: insects damaged **21–54%** of developing seeds across three sites; only **9–24%** matured;
- *C. pitcheri*: weevil-infested capitula produced **60% fewer mature seeds**;
- *C. altissimum*: a demographic fecundity model predicted **197 vs 44 seeds** for insecticide vs control plants of the same mean size (~4.48×), retained as context rather than a raw treatment mean.

This means Aim 2 no longer needs to establish that floral/reproductive herbivory matters in principle. It needs to identify **which capitulum module changes that cost**.

### 4. Orientation can act through abiotic protection independently of pollinator preference

In *Cremanthodium campanulatum*:

- natural nodding achene set = **56.3 ± 3.9%**;
- artificially erect achene set = **15.7 ± 3.6%**;
- `n = 30`, `F = 59.1`, `P < 0.01`;
- no significant pollinator preference was detected between orientations.

Water and UV-B reduced pollen viability. The natural/erect achene-set ratio is approximately **3.59×**.

In *Helianthus annuus*, orientation also alters floral temperature, pollen presentation, early pollinator visits and siring success. However, later all-day field work can show little or no overall azimuth effect on landings.

Therefore orientation cannot be represented by one static `orientation → pollinator visitation` coefficient. A sufficient model eventually needs **time-window and abiotic-protection pathways**.

### 5. Defensive-looking structures are not automatically functional defences

Neutralizing sticky inflorescence exudates in *C. discolor* did not increase seed predators or reduce successful seed production.

At the same time, broader Asteraceae studies and *C. decussatum* show that larger capitula can be preferentially selected by seed predators.

Therefore EAzami must distinguish:

- advertisement/size effects that increase encounter rate;
- a validated defence architecture that reduces successful attack;
- decorative or correlated traits with no measurable protective effect.

This is why Azami involucre/spine image proxies remain **candidate geometry**, not defence traits, until direct botanical validation and manipulation.

### 6. Pollinator dependence and tolerance are state dependent

Across *Cirsium*, reproductive assurance differs among taxa. Comparative work shows species-level differences in autonomous selfing, visitation and seed production; these do not map one-to-one onto pollen limitation.

Likewise *C. undulatum* showed compensatory potential after apical damage, but whether compensation restored annual seed production depended on year and subsequent floral-herbivore pressure.

Thus a final mechanism cannot assume one universal pollinator-dependence coefficient or one universal compensation response.

## Consequence for pattern reduction

The minimal mechanism family suggested by the evidence is no longer just:

`environment + pollinator + antagonist`

A biologically adequate next-stage reduction should eventually contain:

1. **environment → module response**;
2. **saturating mutualist attraction**;
3. **shared signal → antagonist exposure**;
4. **antagonist damage → seed-output cost**;
5. **orientation → time-dependent pollination and abiotic protection**;
6. **module-specific defence efficacy that can be zero**;
7. **mating-system / reproductive-assurance modifier**;
8. **year or state-dependent tolerance**;
9. **module-specific evolvability rather than forced common lability**.

The current v2 simulation does **not** add all nine processes. Instead it asks which held-out patterns are already explained by the compact v1 generator and marks the rest as structural gaps. Only gaps that discriminate viable full models should be promoted into the next mechanistic model.

## Claim boundary

These literature patterns constrain plausible mechanisms. They do not prove that the corresponding mechanism generated the Azami global environment–trait associations.

The causal chain still requires ancestry-resolved focal tests:

`trait / manipulation → interaction or protection → reproductive fitness`.
