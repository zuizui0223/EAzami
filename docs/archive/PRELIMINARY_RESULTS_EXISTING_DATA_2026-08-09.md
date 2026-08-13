# Preliminary results from existing data only

Date: 2026-08-09

This document summarizes analyses that can be completed before new field, RAD-seq, RNA-seq or pigment data are available. All results are conditional on currently source-backed flower-colour coding and focal published nuclear topologies.

## 1. Main result: repeated white-flower evolution is currently better supported than repeated regain

Source-backed white states occur in multiple separated East Asian Cirsium systems (Arenicola, Sinocirsium, Nipponocirsium) and also as within-species white morphs in Japan. This pattern is already inconsistent with treating white flowers as a single local peculiarity.

However, current topology/state combinations do not yet force a W->C regain event. Regain appears only under particular ancestral/root-state assumptions.

## 2. Directional parsimony screen

`analysis/directional_transition_sensitivity.py` conditions each focal topology on a coloured (C) or white (W) root and counts the minimum directional events.

### Taiwanese Nipponocirsium
Topology: `pengii(C) -> [kawakamii(W), tatakaense(C)]`

- root C: 1 total change = 1 C->W loss, 0 regains
- root W: 2 total changes = 0 losses, 2 W->C regains

Interpretation: with the observed coloured states flanking the white taxon, independent white evolution on the kawakamii lineage is substantially more parsimonious than a white ancestor followed by two colour regains. This is currently the cleanest directional white-loss replicate.

### Taiwanese Sinocirsium with population-aware takaoense coding
Topology approximation: `[albescens(W), [takaoense_W(W), takaoense_C(C)]]` versus `[australe(C), fukienense(C)]`

- root C: 2 total changes = 2 C->W losses, 0 regains
- root W: 2 total changes = 0 losses, 2 W->C regains

Interpretation: parsimony alone cannot choose between repeated loss and repeated regain because both ancestral-state assumptions require two changes. This is precisely why population history and denser flanking taxa are required before calling takaoense a reactivation system.

### Arenicola
Topology: `brevicaule(W)` vs `irumtiense(C)`

- root C: 1 loss
- root W: 1 regain

Interpretation: the two-tip comparison contains no directional information by itself. Any claim that irumtiense represents re-expression is premature without flanking taxa / broader topology / population history.

## 3. Species-level coding underestimates transitions

When polymorphic takaoense is coded as one ambiguous species tip `{W,C}`, the focal Sinocirsium tree requires only 1 minimum transition. When white and bluish-purple takaoense are represented as separate population tips, the same focal system requires 2 minimum transitions.

Therefore the Chapter 2 atlas and ancestral-state analyses must be population-aware wherever polymorphism is documented. Collapsing a polymorphic species to a single mean or ambiguous species state can systematically erase the very repeated loss/regain signal being studied.

## 4. Missing-flanking-taxon sensitivity is biologically important

For a simple three-tip Arenicola screen `(outgroup, (brevicaule_W, irumtiense_C))`, the state of the flanking/outgroup lineage determines the parsimonious ancestral direction:

- coloured flanking lineage -> coloured root -> brevicaule loss
- white flanking lineage -> white root -> irumtiense regain

Thus transition-critical phylogenetic sampling should prioritize sister/flanking lineages whose state changes direction, rather than indiscriminately increasing taxon count.

## 5. Current hypothesis ranking

### H1. Repeated anthocyanin loss/suppression — strongest current hypothesis
Prediction: complete nuclear-tree ancestral-state reconstruction will require multiple independent entries into the white state.

### H2. Repeated regulatory suppression of an intact pathway — plausible but not yet tested
Prediction: independent white systems retain anthocyanin structural genes but repeatedly alter homologous regulatory nodes (for example MBW-network components or cis-regulatory modules).

### H3. Ancestral colour polymorphism / introgression explains part of the pattern — serious competing hypothesis
Especially important for young Taiwanese radiations and any population-polymorphic system.

Prediction: colour-associated haplotypes may be older than species splits or show local ancestry discordant with the genome-wide tree.

### H4. True regain/reactivation — high-value but currently unproven
A regain should not be claimed until a white ancestor/intermediate is supported and ancestral polymorphism / introgression are rejected.

Current best candidate for testing (not proof): colour-polymorphic takaoense in the albescens–takaoense part of Sinocirsium.

### H5. Single ancient white origin followed by many regains — currently low priority
It is less economical under the current scattered white states, but only a complete East Asian topology with explicit transition-rate models can reject it formally.

## 6. Analyses that should now proceed before new samples

1. Complete the source-backed colour atlas for all tips available in modern nuclear phylogenies.
2. Recover a machine-readable East Asian nuclear topology set (Chang 2025, Chang 2026, Moreyra 2025 where possible).
3. Run population-aware ancestral-state reconstruction under multiple models: equal rates, asymmetric C->W/W->C rates, and topology sensitivity.
4. Run leave-one-taxon / hypothetical-placement sensitivity to rank missing taxa by expected change in transition count or direction.
5. Use those results to freeze RAD-seq panel v1.0.

## 7. Interpretation discipline

Current defensible statement:

> Existing nuclear phylogenies and source-backed flower-colour data support repeated evolution of white flowers in East Asian Cirsium, whereas true restoration of anthocyanin pigmentation after a white ancestor remains a testable but unproven hypothesis.

This distinction should be maintained in the manuscript and sampling plan until Issues #2–#6 provide the necessary population and molecular evidence.
