# Orientation causal triangulation v3

Status date: 2026-09-04  
Role: **current causal boundary / mechanism prioritization for Chapter 2**

## Current answer

The public-data programme now rules out a simple interpretation more strongly than before: **precipitation seasonality (BIO15) is not isolated as a specific explanatory axis for nodding/downward orientation, and that failure is not explained by the original n=9 panel alone.**

The best current description is:

> **present orientation corresponds to a composite climatic/lineage regime; rain/wetting and radiation protection remain the strongest experimentally grounded functional prior, but the focal East-Asian Cirsium causal chain is unmeasured.**

## 1. The present association is not a trivial geography artefact

BIO15 remains positive after coarse geographic falsification:

- Japan-only n=7: beta **+1.057 to +1.103 SD**, 6/6 topology and 42/42 LOO positive;
- all-nine latitude/longitude-adjusted model: beta **+1.118 to +1.125 SD**, 6/6 topology and 54/54 LOO positive;
- Taiwan-indicator sensitivity: beta **+1.089 to +1.116 SD**, also 6/6 and 54/54 positive.

Thus a simple Taiwan-versus-Japan split or linear centroid latitude/longitude alone does not explain the observed direction.

## 2. History and geography jointly absorb the apparent extremeness

Among all 126 state-count-preserving maps, observed BIO15 was unusually positive (5/126 = 3.97%). That rarity weakened to 3/40 = 7.5% among exact recurrence matches and to 3/10 = 30% among near-history maps.

Conditioning recurrence matches on coarse geography produces the same boundary: 3/10 geography-nearest and 3/10 joint history+geography-nearest maps are at least as positive as observed. The magnitude is therefore not exceptional within the closest declared history/geography class.

## 3. BIO15 specificity does not recover when panel size is expanded

The frozen n>=10 panel had nine taxa. Existing occurrence assets allowed two result-blind resolution sensitivities without adding sources or predictors:

- n>=5: **12 taxa, 7 U / 5 D**;
- n>=3: **13 taxa, 7 U / 6 D**.

The same mutually adjusted Brownian model was repeated:

`z(BIO15) ~ orientation + z(BIO1) + z(latitude) + z(longitude)`.

### BIO15 adjusted orientation coefficient

| panel | beta range | median | P range | topology sign | LOO sign |
| --- | ---: | ---: | ---: | ---: | ---: |
| n>=10, n=9 | +0.744 to +0.778 | +0.761 | 0.336–0.356 | 6/6 | 48/54 |
| n>=5, n=12 | +0.157 to +0.194 | +0.176 | 0.780–0.820 | 6/6 | 60/72 |
| n>=3, n=13 | +0.265 to +0.285 | +0.275 | 0.659–0.682 | 6/6 | 66/78 |

The full-fit sign stays positive, but the coefficient becomes much smaller and deletion stability does not reach the frozen specificity rule.

Orientation also adds **no held-out BIO15 predictive value** beyond BIO1 + latitude + longitude + Brownian covariance:

- n=9: positive prediction improvement on 0/6 topologies;
- n=12: 0/6, median delta MSE **-0.671**;
- n=13: 0/6, median delta MSE **-0.396**.

Therefore the original n=9 panel size is not the main reason BIO15 specificity failed.

## 4. BIO1 is more deletion-stable, but is still not a cause

The reciprocal model was:

`z(BIO1) ~ orientation + z(BIO15) + z(latitude) + z(longitude)`.

| panel | beta range | P range | topology sign | LOO sign |
| --- | ---: | ---: | ---: | ---: |
| n=9 | -0.490 to -0.487 | 0.527–0.535 | 6/6 | 54/54 |
| n=12 | -0.741 to -0.733 | 0.118–0.125 | 6/6 | 72/72 |
| n=13 | -0.742 to -0.737 | 0.105–0.110 | 6/6 | 78/78 |

BIO1 is therefore the more deletion-stable component after mutual adjustment. This does **not** establish annual mean temperature as a causal agent: the P values remain above conventional thresholds, BIO1 remains a present-day centroid variable, and lineage/geography confounding is not eliminated.

## 5. Closest-lineage contrasts are mixed

Environment-blind minimum-patristic U/D pairing did not recover one universal climate contrast:

- full9: BIO15 positive in **2/4** closest pairs; BIO1 negative in **3/4**;
- Japan7: BIO15 positive in **2/3**; BIO1 negative in **2/3**.

The present climate signal is therefore not a simple repeated pairwise rule across the closest extant lineages.

## 6. External experiment narrows the mechanism space

The strongest directly relevant external experiment remains *Cremanthodium campanulatum* (Asteraceae). Natural nodding capitula compared with artificially erect capitula showed:

- achene set **56.3 ± 3.9%** versus **15.7 ± 3.6%**;
- ratio approximately **3.59**;
- water exposure and UV-B reduced pollen viability;
- no detected pollinator orientation preference.

DOI: `10.1080/17550874.2012.702793`.

This demonstrates that an orientation -> abiotic reproductive protection -> fitness pathway is biologically real at the capitulum level in Asteraceae. The effect magnitude is not transferred to *Cirsium*.

A 2026 *Polygonatum cyrtonema* manipulation independently supports the general possibility that downward orientation integrates rain/radiation protection, pollination and reproductive output (`10.1002/ece3.73221`), but it is retained only as broad mechanism plausibility.

## 7. Candidate ranking after all current falsifications

| Candidate explanation | Current status |
| --- | --- |
| BIO15 as a unique direct driver | **not supported** |
| BIO1 / temperature as a unique direct driver | **not supported**, though more deletion-stable than BIO15 |
| simple Taiwan/Japan geography artefact | **weakened** |
| static pollinator preference alone | **weakened** |
| rain/wetting + UV/radiation protection | **strongest external functional prior** |
| thermal/time-window pollination | **plausible parallel pathway** |
| integrated abiotic + biotic orientation function | **plausible** |
| one recurring historical coarse climate trigger | **not identified** |

## 8. Decisive missing focal chain

The remaining experiment is no longer “which BIOCLIM variable should be added?” It is:

```text
orientation
-> rain / wetting and radiation exposure
-> pollen viability / retention and stigma function
-> effective pollen transfer
-> viable achene set
```

measured in ancestry-matched *Cirsium*.

Until this chain is observed directly, Chapter 2 should describe rain/wetting protection as an experimentally grounded **mechanism candidate**, not a historical cause.

## Stop rule

Further correlated coarse-climate screening is not justified by the current results. New causal resolution must come from:

1. focal mediator + reproductive-fitness experiments;
2. new event-linked ancestry / trait-transition chronology;
3. local palaeogeographic or exposure data that can be linked to the same transition.

## Machine-readable source

`data/evidence/chapter2_orientation_causal_triangulation_v3.json`
