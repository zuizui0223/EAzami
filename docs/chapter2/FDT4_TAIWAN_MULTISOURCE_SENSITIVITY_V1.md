# FDT4 Taiwan multi-source orientation sensitivity v1

Status date: 2026-08-29

## Question

The merged Chapter 2 ecological result classified orientation as `unresolved` because the frozen GBIF-only East-Asian panel contained nine taxa and the stable BIO15/BIO1 directions did not cross the frozen PGLS threshold on every accepted topology.

This audit asks a narrower question:

> **If Taiwan occurrence coverage is expanded with an independent public source while the n>=10 gate, source-name guard, coordinate-quality gate, spatial thinning and six accepted Comp1061 topologies are left unchanged, does the orientation-climate support class remain the same?**

This is an occurrence-source sensitivity analysis. It is not a new historical niche reconstruction and does not change the frozen primary result by itself.

## Frozen primary: GBIF only

The current primary remains the merged GBIF-only panel:

- n=9, U=5/D=4;
- BIO1 D−U = −0.975 to −0.967 SD, P=0.09604–0.09793;
- BIO15 D−U = +1.320 to +1.330 SD, P=0.05054–0.05239;
- accepted-topology sign agreement = 6/6 for both axes;
- species-LOO sign agreement = 54/54 for both axes;
- status = **`unresolved`**.

A live GBIF refresh on 2026-08-29 did not increase the two threshold-limiting taxa: *Cirsium morii* and *C. tatakaense* remained at nine independent thinned environment-complete records each.

## Independent Taiwan Biodiversity Network audit

All seven Taiwan orientation taxa were queried with the same TBN v2.6 rules rather than harvesting records only for the two leverage taxa.

The TBN audit recovered:

- *C. kawakamii*: 40 strict <=10 km TBN cells not represented by the GBIF primary cells;
- *C. morii*: 4 new strict cells;
- *C. tatakaense*: 2 new strict cells.

Three direct TBN Plant records were then admitted to a deliberately conservative `native` tier: one new cell each for *C. kawakamii*, *C. morii* and *C. tatakaense*. All three have direct TBN occurrence URLs, `tbn.dp.plant` external identifiers, CC BY licensing, <=10 km uncertainty, and occupy 0.05-degree cells absent from the GBIF panel.

This moves *C. morii* from 9 to 10 cells and *C. tatakaense* from 9 to 10 without changing the frozen threshold.

## Sensitivity A — direct TBN-native additions only

The resulting East-Asian panel contains 11 taxa (U=6/D=5).

Across all six accepted optimized Comp1061 topologies:

| Axis | D−U effect | P range | topology sign | species LOO sign |
| --- | ---: | ---: | ---: | ---: |
| BIO1 annual mean temperature | −1.001 to −0.994 SD | 0.04819–0.04904 | 6/6 | 66/66 |
| BIO15 precipitation seasonality | +1.136 to +1.143 SD | 0.03789–0.03980 | 6/6 | 66/66 |

Under the already-frozen Chapter 2 rule, this tier is **`tendency_supported`**.

The result is notable because support is gained without lowering `n>=10`, relaxing coordinate uncertainty, reducing spatial thinning, changing orientation states or selecting a different topology.

## Sensitivity B — broader TBN records excluding explicit GBIF mirrors

A second tier admitted all strict source-name-guarded TBN records in new GBIF cells except records explicitly marked with `gbif:` external identifiers. This produced 35 environment-complete additions and the same 11-taxon U=6/D=5 panel.

| Axis | D−U effect | P range | topology sign | species LOO sign |
| --- | ---: | ---: | ---: | ---: |
| BIO1 annual mean temperature | −0.915 to −0.909 SD | 0.06525–0.06598 | 6/6 | 66/66 |
| BIO15 precipitation seasonality | +1.078 to +1.084 SD | 0.04874–0.05110 | 6/6 | 66/66 |

Under the same frozen rule, this broader tier is **`unresolved`**.

## What this resolves

The orientation-climate pattern is no longer best described as uncertain because of topology instability or one influential species:

- BIO1 remains negative in every accepted topology and every species-LOO fit across both multi-source tiers;
- BIO15 remains positive in every accepted topology and every species-LOO fit across both tiers;
- adding *C. morii* and *C. tatakaense* raises the panel to 11 taxa without changing the direction;
- the threshold-based support class changes with the occurrence-source definition used to estimate present-day niche centroids.

Therefore the remaining uncertainty is specifically:

> **effect direction is phylogenetically and taxonomically robust, whereas threshold crossing is occurrence-source / niche-centroid sensitive.**

This is a more informative result than the original generic `unresolved` label.

## Decision for Chapter 2

The merged GBIF-only primary is **not replaced** by the direct-TBN tier merely because that tier crosses P<0.05. Doing so would select the occurrence definition by outcome.

The current decision is:

- primary GBIF-only status: **`unresolved`**;
- direct TBN-native sensitivity: **`tendency_supported`**;
- broader non-GBIF TBN sensitivity: **`unresolved`**;
- cross-tier biological direction: **stable**.

A future primary update should first freeze an outcome-independent multi-source occurrence harmonization contract, then rebuild all Taiwan taxa under that contract. Until then, the appropriate interpretation is **source-sensitive support class with a robust orientation-climate direction**.

## Claim ceiling

This sensitivity does not establish ancestral climate, timing of an orientation transition, independent origins, ecological convergence, adaptation, selection or fitness mechanism. It also does not mean that the broader TBN tier is biologically superior to the direct-TBN tier. The result identifies a present-day occurrence-sampling sensitivity that must be separated from the much stronger sign robustness across phylogenies and taxa.

## Machine-readable evidence

- `data/evidence/fdt4_taiwan_multisource_orientation_sensitivity_v1.json`
- source workflow run: 33225237163
- source artifact: 9706631737
- artifact SHA-256: `ee59391e1d55654ccc7bd5e429d03c71c72532d90097aacbbd66f1a7fad07e3a`
