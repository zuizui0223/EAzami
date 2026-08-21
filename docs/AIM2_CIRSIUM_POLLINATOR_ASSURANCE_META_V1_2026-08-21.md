# Aim 2 meta-analysis v4 — pollinator dependence versus reproductive assurance

## Question

The antagonist meta-analysis established a large direct reproductive-herbivory cost. The mutualist side requires a different distinction:

> Does a plant **depend on animal pollination** for seed production, and is it actually **pollen limited under current open field conditions**?

These are not the same quantity. Pollinator exclusion estimates dependence/reproductive assurance; pollen supplementation tests whether the currently delivered pollen is insufficient.

## Evidence base

`data/evidence/cirsium_pollinator_assurance_meta_v1.csv` freezes six independent Cirsium study designs:

1. Powell et al. 2011 — paired bagged/open heads and pollen supplementation across *C. vulgare* plus native congeners;
2. Bennett et al. 2018 — supplement/open/bagged experiment for *C. erisithales*;
3. LeFevre et al. 2025 — partial/complete pollinator exclusion in *C. discolor* with a *Carduus nutans* comparator;
4. Lalonde & Roitberg 1994 — pollen-donor distance and seed set in dioecious *C. arvense*;
5. Keddy/Keddy — bagged/open evidence for *C. pitcheri*, retained at sign level because the primary numeric table is not yet recovered;
6. Michaux 1989 — reproductive biology of *C. vulgare* in New Zealand, linking fertile seed production to cross-pollination, flowering synchrony and density.

## Quantitative anchor — *C. erisithales*

Bennett et al. report viable seeds per flower:

- pollen supplement: **41.75 ± 11.39**, n=8;
- open control: **47.88 ± 9.44**, n=8;
- pollinator excluded: **12.2 ± 3.57**, n=5.

Derived contrasts:

- open / bagged RR = **3.925**;
- bagged / open = **0.255**;
- therefore the open-pollinator contribution relative to the bagged state is about **74.5%** of observed open seed output on this simple scale;
- supplement / open = **0.872**, and the reported supplement-vs-open comparison showed no pollen limitation.

This is the cleanest demonstration of the central distinction: a species can receive a large fitness contribution from pollinators while not being pollen limited under the pollination service currently available.

## Structured result

Across the six independent study designs:

- **5/6** provide evidence of high pollinator dependence in their focal Cirsium context;
- the comparative Powell study shows strong **among-species variation** in dependence/autonomous selfing rather than one genus-wide state;
- only **1/6** currently provides a fully recovered numeric supplement/open/bagged Cirsium contrast suitable for all three components;
- the two designs that directly pair dependence/assurance with a test of open-field pollen limitation both show that current open pollen delivery is generally adequate despite measurable dependence.

The evidence therefore supports:

> **pollinator dependence != pollen limitation.**

A decline in visits can matter greatly, but present visitation rate alone does not reveal how much seed fitness is at risk.

## Reproductive-assurance modifiers recovered from the literature

### Autonomous selfing / mating system

Powell et al. found substantially greater autonomous self-pollination in invasive *C. vulgare* than in rare *C. andrewsii* and *C. fontinale*. This can buffer loss of pollinator service.

The New Zealand *C. vulgare* study instead concluded that cross-pollination was required for fertile seed in that study system. The correct synthesis is therefore not to average these into one fixed species coefficient, but to treat reproductive assurance as population/context dependent until the causal basis of the difference is resolved.

### Donor spacing

*C. arvense* is effectively dioecious. Female clones separated from males by at least about 50 m set far fewer achenes, and fertilization decreases with distance to an effective pollen donor. Here spatial population structure controls effective pollination even if floral visitors are present.

### Flowering synchrony and local density

The New Zealand *C. vulgare* study explicitly links successful contribution to the next generation to flowering during the main pollinator-active period or occurring at sufficient local density.

### Species-specific reproductive assurance

*C. pitcheri* is self-fertile, yet bagged heads produced much less seed than open heads. *C. discolor* likewise loses reproductive success under partial/complete pollinator exclusion. Thus self-compatibility cannot be used as a synonym for autonomous reproductive assurance.

## New ecological conclusion

Combining this mutualist synthesis with the antagonist and demographic-transmission syntheses gives a more precise causal structure:

`environment / population context`

`-> pollinator availability + donor availability + flowering overlap`

`-> effective pollen delivery`

`-> seed output, buffered by autonomous selfing / mating system`

while in parallel:

`capitulum traits -> antagonist exposure -> seed loss`

and downstream:

`recruitment opportunity / disturbance / density dependence -> transmission of seed differences to population growth`.

Thus environment is not best represented as a single direct trait-fitness coefficient. It can enter at multiple gates before and after the head-level mutualist-antagonist trade-off.

## Consequence for the focal doctoral experiment

Aim 2 should not use `visit count` as the mutualist endpoint. Preserve separately:

1. pollinator visits;
2. heads probed / effective contacts;
3. local same-taxon flowering density and flowering overlap;
4. for W/C comparisons, local morph availability;
5. reproductive-assurance state from a small paired bagged/open assay where feasible;
6. final total/filled achenes.

The causal target is:

`trait + local context -> effective pollination -> seed fitness`

not simply:

`trait -> visitation`.

For *C. pendulum*, the existing flowering-overlap gate becomes even more important: a white/coloured comparison without contemporaneous flowering cannot identify a pollinator-choice effect.

## Pooling boundary

No genus-wide pooled pollinator RR is currently justified. The available independent studies mix:

- bagged/open seed ratios;
- pollen-supplement/open contrasts;
- complete/partial exclusion failure probabilities;
- donor-distance gradients;
- autonomous-selfing indices;
- qualitative cross-pollination dependence.

Pooling these would conflate different biological questions.

The next numerical upgrade should recover original bagged/open means and uncertainty from independent *Cirsium* studies. Formal pooling should begin only after at least three independent studies share the same seed-output estimand and treatment contrast.

## New hypothesis generated

### Reproductive-assurance buffering hypothesis

The seed-fitness consequence of a change in pollinator service is predicted to be strongest where autonomous reproductive assurance is weak and where donor density/flowering overlap constrains effective pollen delivery.

A focal capitulum trait can therefore show a strong visitation effect but a weak seed-fitness effect in selfing-buffered populations, or the opposite when effective outcross pollen is limiting.

This is a testable moderator hypothesis for Aim 2, not an assumption to hard-code into the simulation before focal data exist.
