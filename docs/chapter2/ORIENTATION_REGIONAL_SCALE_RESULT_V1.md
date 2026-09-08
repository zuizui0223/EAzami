# Orientation transition-regime regional-scale result v1

**Status date:** 2026-09-08  
**Role:** post-result scale decomposition of the already-fixed `BIO15 up + BIO1 down` orientation transition-regime hypothesis.

## Question

The previous result was exceptional in the 12-taxon Japan+Taiwan panel (16/792) but not in the Japan-only panel (10/56). Does that mean the result is merely a coarse Japan-versus-Taiwan climate contrast?

## Fixed analysis

No environmental vector, taxon, occurrence source or topology was changed. The n>=5 panel contains 12 taxa: eight from the frozen Japan occurrence asset (5 U, 3 D) and four from the frozen Taiwan asset (2 U, 2 D).

Full-panel standardized BIO15 and BIO1 taxon centroids were decomposed additively:

`total = region mean + within-region deviation`.

The unchanged CTMC/Brownian transition-regime statistic was applied to total, between-region and within-region components. We also enumerated all 336 state maps that preserve the observed U/D counts separately in Japan and Taiwan.

## Result

### The coarse Japan-Taiwan contrast does not generate the signal

The full result reproduces exactly:

- total composite median: **0.253119**;
- exact rank: **16/792 = 2.02%**.

The between-region component points slightly in the **opposite** direction:

- composite median: **-0.020234**;
- negative on all 6 accepted topologies;
- exact rank: **502/792 = 63.38%**.

Therefore the original concordance is not a Japan-versus-Taiwan mean-climate artefact.

### The signal is retained within regional contexts

After removing Japan and Taiwan regional means, the within-region component is stronger than the total:

- composite median: **0.273352**;
- positive on **6/6** accepted topologies;
- exact rank: **20/792 = 2.53%**.

Axis decomposition remains asymmetric:

- BIO15-only: **99/792 = 12.50%**;
- lower BIO1: **15/792 = 1.89%**.

Thus the supported object remains a composite regime with especially strong contribution from the lower-temperature component.

### Regional state composition is insufficient

Conditioning the null on the observed orientation-state frequencies separately within Japan (3 D among 8 taxa) and Taiwan (2 D among 4 taxa) leaves **336** possible maps.

Within that constrained universe:

- total: **9/336 = 2.68%**;
- between-region: **296/336 = 88.10%**;
- within-region: **10/336 = 2.98%**.

The observed result therefore remains exceptional even after regional U/D composition is held fixed.

### Why the individual-region panels look weaker

Japan-only remains directionally positive on all six topologies but ranks **10/56 = 17.86%**. Taiwan-only is the most extreme of its possible assignments (**1/6**) and has a much larger observed composite (0.8613), but with only four taxa and two states per class, **1/6 = 16.67% is the finest possible exact rank**. Individual-region exact tests therefore have much coarser finite-map resolution than the pooled within-region decomposition.

## Biological interpretation

The orientation ecological result should no longer be described as arising mainly from a Japan-Taiwan regional contrast. The opposite is supported:

> **Orientation transition–niche concordance is carried by taxon-level climatic differences within the Japan and Taiwan regional contexts, rather than by their regional mean climate difference.**

This is useful because it distinguishes ecological sorting from coarse biogeographic composition. The signal persists after both regional mean removal and conditioning on region-specific orientation-state frequencies.

The result does not establish that the same process operates at every spatial scale. Japan-only is directionally consistent but not exceptional at its available map resolution, and Taiwan-only is too small for a <=0.05 exact rank. The scale analysis is therefore best described as **within-region structure retained across the combined Japan-Taiwan panel**, not as independent replication in two regions.

## Claim boundary

This analysis was designed after the original transition-regime and Japan-only results were known. It is a falsification/diagnostic, not a prospective independent confirmation. It does not identify BIO1 or BIO15 as causal drivers and does not establish historical climate, selection, adaptation or a physiological mediator.

## Provenance

- workflow run: `34196950068`;
- job: `101966691892`;
- artifact: `10044393882` (`chapter2-orientation-regional-scale-v1`);
- artifact SHA256: `e22e3a55dcac42fa3c21820b6206e27415dbc3c6f84501ac5dc4067da5eaa883`.
