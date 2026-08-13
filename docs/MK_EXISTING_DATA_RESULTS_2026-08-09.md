# Mk-model sensitivity using currently available published topologies

Date: 2026-08-09

## Scope

This is an exploratory two-state continuous-time Mk analysis using the focal published nuclear **topologies** already encoded in EAzami. Exact Newick trees and branch lengths from the source studies have not yet been recovered, so equal branch lengths were used and rescaled by 0.25, 0.5, 1 and 2 as a sensitivity test.

States are:

- `C`: anthocyanin-coloured
- `W`: white

The analysis compares:

- ER: `q(C->W) = q(W->C)`
- ARD: `q(C->W)` and `q(W->C)` estimated independently

See `analysis/mk_rate_sensitivity.py` and `analysis/mk_rate_sensitivity.csv`.

## Main result 1 — ARD is not supported by the current small topology set

Across Nipponocirsium, population-aware Sinocirsium, Arenicola, a Taiwan two-clade composite and an all-three-clade composite, ARD never beats ER by AIC. `delta_AIC_ARD_minus_ER` is approximately +1.5 to +2.0 across branch-length scalings.

This does **not** mean that biological loss and regain rates are equal. It means the current focal topology fragments contain too little information to justify an additional directional-rate parameter.

## Main result 2 — rate estimates are not identifiable with arbitrary equal branch lengths

For several scenarios the estimated rates hit the upper grid boundary. Changing the common branch scale changes the fitted numerical rates while leaving the likelihood/AIC effectively unchanged.

Therefore:

- absolute rate estimates in `mk_rate_sensitivity.csv` have no biological interpretation;
- the current analysis cannot support a claim that `q(C->W) > q(W->C)` or vice versa;
- exact published branch lengths and a much larger tip set are required before transition-rate asymmetry is tested biologically.

This is now tracked in Issue #7.

## What remains robust without branch lengths

### 1. Repeated white states are phylogenetically dispersed

White flower states occur in multiple distinct focal systems, including Arenicola, Sinocirsium and Nipponocirsium, plus documented within-species white morphs in Japan. This continues to motivate repeated white-flower evolution as the leading working hypothesis.

### 2. Nipponocirsium gives a strong local loss hypothesis

Published topology:

`pengii(C) -> [kawakamii(W), tatakaense(C)]`

Under parsimony, a coloured ancestral state gives one `C->W` event on the *C. kawakamii* lineage, whereas forcing a white ancestral state requires two `W->C` events. This makes independent white evolution in *C. kawakamii* a strong local hypothesis even before a full Mk analysis.

### 3. Population-aware coding changes the inferred transition burden

Treating var. *takaoense* as one ambiguous `{W,C}` species tip requires fewer minimum changes than separating white and bluish-purple population/morph tips. Therefore species-level colour means or ambiguous polymorphic coding can systematically erase transition information relevant to regain.

### 4. Arenicola remains directionally unresolved

The two-tip *C. brevicaule* (W) / *C. irumtiense* (C) comparison requires one transition but cannot identify its direction. Flanking nuclear taxa/populations determine whether the most parsimonious history is white loss in *brevicaule* or coloured regain in *irumtiense*.

## Updated hypothesis hierarchy

1. **Repeated white-flower evolution** — strongest existing-data hypothesis.
2. **Repeated regulatory suppression of an intact anthocyanin pathway** — mechanistically plausible but requires Issue #3 data.
3. **Ancestral polymorphism and/or introgression explains a subset of apparent transitions** — serious alternative, especially in young Taiwanese radiations.
4. **True regain/reactivation after a white ancestor** — high-value target, but not currently required by the known topology fragments.
5. **Directional transition-rate asymmetry (`loss > regain` or `regain > loss`)** — currently unidentifiable; defer until Issue #7 is resolved.

## Immediate analysis path that does not require new field data

1. Continue the flower-colour atlas and population-level coding (Issue #6).
2. Recover exact published nuclear tree artifacts and branch lengths (Issue #7).
3. Harmonize tip names and retain alternative nuclear topologies.
4. Fit full-tree ER/ARD Mk models and compare AICc/profile likelihoods.
5. Estimate marginal ancestral-state probabilities rather than relying only on parsimony.
6. Stochastic-map transition counts and identify branches with posterior support for `W->C` transitions.
7. Use missing-tip sensitivity to rank which future RAD-seq samples can actually change regain inference.

## Interpretation rule for Chapter 2

At the current stage, write **"candidate regain/reactivation"**, never "reactivation" as an established result. The strongest publishable preliminary statement is that white-flower states appear repeatedly across nuclear-separated East Asian *Cirsium* systems and that population-aware coding increases the inferred number of flower-colour transitions.
