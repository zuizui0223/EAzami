# Aim 2 meta-analysis v3 — from reproductive herbivory to demographic transmission

## Why this layer was added

The existing strict seed-output meta-analysis already answers one question well:

> Experimental reduction of reproductive insect herbivory strongly increases viable/mature seed output in directly harmonizable *Cirsium* experiments (pooled RR = 2.674, 95% CI 2.388–2.993).

The next unresolved question is not whether reproductive antagonists can reduce maternal fitness. It is whether that loss is transmitted through recruitment strongly enough to alter population growth, and whether environmental context controls that transmission.

This meta-synthesis therefore separates two links:

1. `insect herbivory -> viable/mature seed output`;
2. `seed-output difference -> recruitment / population growth`.

## Evidence base

`data/evidence/cirsium_demographic_transmission_meta_v1.csv` freezes six independent study designs spanning four *Cirsium* taxa:

- *C. canescens* — central Sandhills life-cycle exclusion experiment;
- *C. occidentale* var. *occidentale* — old/new coastal dune experiment;
- *C. altissimum* — Nebraska productivity-gradient IPM experiment;
- *C. vulgare* — eight-site density-dependent demographic experiment;
- *C. altissimum* — independent Kansas seven-year fertilizer/herbivore experiment with prescribed fires;
- *C. canescens* — Colorado peripheral/elevation experiment.

Reused Arapaho *C. canescens* analyses are kept as one independent data-generation lineage rather than counted repeatedly.

## Structured quantitative result

Across the six independent designs:

- reproductive-insect fecundity cost supported: **6/6**;
- downstream population transmission:
  - **4/6 consistent**;
  - **1/6 context-dependent**;
  - **1/6 blocked**;
- broad abiotic/environmental context explicitly compared: **5/6**;
- evidence that productivity, fertility, elevation, or broad site heterogeneity is a general monotonic moderator: **0/5**;
- explicit demographic-gate tests: **4**;
- gate supported: **3/4**.

The supported demographic gates are:

1. density dependence (*C. vulgare*);
2. disturbance / recruitment microsite availability (*C. altissimum*);
3. safe-site / post-dispersal recruitment limitation (*C. canescens* peripheral populations).

The negative gate test is the Nebraska *C. altissimum* IPM, where density dependence did not cancel the fecundity effect and herbivory reduced population growth across all site × productivity combinations.

## Direct quantitative anchors

### Central *C. canescens*

Insect reduction increased viable seed release from about 41 to 105 seeds per plant in the classic life-cycle experiment, and later demographic synthesis estimated an approximately 0.33 reduction in population growth rate attributable to floral herbivory.

### *C. occidentale* coastal dunes

Maron et al. 2002 reports, from the same experiment:

- new dune: seed RR = 877/360 = **2.44**; seedling RR = 6.0/2.2 = **2.73**;
- old dune: seed RR = 1954/470 = **4.16**; seedling RR = 3.3/1.28 = **2.58**.

Thus large fecundity differences propagated to recruitment in two structurally different dune contexts.

### *C. altissimum* productivity gradient

The IPM study found `Delta lambda > 0` in every site × productivity-zone combination, ranging about **0.3–1.2**, while the productivity × herbivory interaction was essentially absent (`F1,16 = 0.05`, `P = 0.82`). Fecundity was the dominant pathway.

### *C. vulgare* heterogeneous sites

Across eight sites, herbivore exclusion permitted explosive low-density growth (`lambda > 5`), whereas herbivore access drove decline (`lambda < 1`). Environmental heterogeneity did not reverse the qualitative herbivore effect, although density dependence damped the effect at high density.

### *C. altissimum* seven-year field experiment

Insects significantly reduced seed production, but large seed differences often failed to change population growth. Herbivore effects on population growth appeared in **2/3** transitions containing prescribed fire versus **1/4** transitions without fire, whereas fertilizer moderated herbivore effects in only **1/7** transitions. This points to recruitment opportunity/disturbance rather than resource level alone.

### Peripheral *C. canescens*

Across five Colorado sites, insect herbivory reduced lifetime viable seed production, but increased seed production under insect reduction did **not** yield a proportional recruitment increase. Elevation affected phenology but did not explain insect damage, seed production, or recruitment. Post-dispersal safe-site limitation disconnected fecundity from recruitment.

## New conclusion

The current evidence supports a two-stage interpretation:

> **Reproductive antagonists impose a strong and repeatable direct fecundity cost, but environment does not appear to act mainly by monotonically strengthening or weakening that cost along broad gradients. Instead, environmental/demographic context often acts downstream by determining whether lost or gained seed can pass through the seed-to-recruitment bottleneck.**

In short:

`environment -> demographic opportunity gate -> transmission of interaction cost`

is currently better supported than the simple form

`environment -> strength of herbivory -> fitness`.

This is a meta-analytic hypothesis generated from *Cirsium* evidence, not yet a universal plant rule.

## New doctoral question generated by the meta-analysis

Aim 2 should distinguish two quantities that were previously easy to conflate:

1. **trait-level maternal fitness effect** — does orientation/colour/involucre change pollination, damage, and mature achene output?
2. **demographic transmission** — under what recruitment context would that achene difference matter beyond the maternal plant?

The first remains the mandatory tranche-1 endpoint. The second should be recorded as population context (e.g. bare ground/litter/disturbance/recruitment opportunity) rather than turning tranche 1 into a new long-term demography Aim.

## Consequence for the central modular-evolvability hypothesis

This result sharpens the environmental side of the hypothesis. Different capitulum modules may alter immediate mutualist/antagonist benefits, but the ecological consequence of those differences can be filtered by a second, partly independent environmental gate at recruitment.

Therefore a single common `environment -> trait fitness` coefficient is biologically too coarse. The field design should preserve:

`module -> interaction/protection -> maternal fitness`

separately from

`population environment -> recruitment opportunity`.

## Pooling boundary

A single pooled population-growth effect is **not** reported. The six studies mix raw recruitment ratios, intrinsic growth rates, IPM `lambda` differences and hierarchical density-dependent `lambda` outputs. Treating these as one numerical effect size would create false precision.

The quantitative synthesis is therefore:

- strict random-effects pooling only for the harmonized viable/mature seed-output RR;
- structured study-level meta-synthesis for downstream demographic transmission and moderators.

## Next meta-analysis lane

The next candidate is the mutualist analogue:

`pollinator access / effective contact -> seed output -> reproductive assurance`

with autonomous selfing/mating system treated as a moderator. It should only be formally pooled if independent studies expose a common open-vs-excluded or supplemented-vs-control seed-output estimand with recoverable uncertainty.
