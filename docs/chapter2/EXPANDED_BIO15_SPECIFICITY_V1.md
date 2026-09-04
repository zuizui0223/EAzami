# Expanded BIO15 specificity sensitivity — v1

Status: 2026-09-04

## Question

Was the failure to isolate precipitation seasonality (BIO15) as a specific orientation-associated climate axis mainly caused by the small frozen n>=10 panel of nine taxa?

## Design

No new occurrence source, alias or environmental variable was added. The same mutually adjusted Brownian models were repeated on state-diverse panels already present in the frozen occurrence assets:

- primary n>=10 panel: 9 taxa, 5 U / 4 D;
- n>=5 resolution sensitivity: 12 taxa, 7 U / 5 D;
- n>=3 boundary sensitivity: 13 taxa, 7 U / 6 D.

The specificity model was:

`z(BIO15) ~ orientation + z(BIO1) + z(latitude) + z(longitude)`

and the reciprocal model exchanged BIO15 and BIO1. Six accepted AU topologies and species leave-one-out were retained. BIO15 specificity was prespecified to recover only if the n>=5 panel retained the positive orientation coefficient in all 6 full fits and all 72 topology-by-species LOO fits.

## Result

Classification:

`expanded_panels_retain_bio15_direction_without_specificity`

### BIO15 after BIO1 + geography

| panel | beta range | median | P range | full topology sign | LOO sign |
|---|---:|---:|---:|---:|---:|
| n>=10, n=9 | +0.744 to +0.778 | +0.761 | 0.336–0.356 | 6/6 | 48/54 |
| n>=5, n=12 | +0.157 to +0.194 | +0.176 | 0.780–0.820 | 6/6 | 60/72 |
| n>=3, n=13 | +0.265 to +0.285 | +0.275 | 0.659–0.682 | 6/6 | 66/78 |

The positive full-fit direction remains, but the adjusted coefficient shrinks sharply in the expanded panels and deletion stability does not reach the frozen specificity rule.

Orientation also fails to improve held-out BIO15 prediction beyond BIO1 + latitude + longitude + Brownian covariance at every threshold:

- n>=10: positive MSE improvement on 0/6 topologies;
- n>=5: 0/6, median delta MSE = -0.671;
- n>=3: 0/6, median delta MSE = -0.396.

### Reciprocal BIO1 after BIO15 + geography

| panel | beta range | median | P range | full topology sign | LOO sign |
|---|---:|---:|---:|---:|---:|
| n>=10, n=9 | -0.490 to -0.487 | -0.488 | 0.527–0.535 | 6/6 | 54/54 |
| n>=5, n=12 | -0.741 to -0.733 | -0.737 | 0.118–0.125 | 6/6 | 72/72 |
| n>=3, n=13 | -0.742 to -0.737 | -0.739 | 0.105–0.110 | 6/6 | 78/78 |

BIO1 is therefore the more deletion-stable component of the mutually adjusted present-day climate regime. Its P values remain above conventional thresholds, so this does not identify temperature as a cause.

## Interpretation

The n=9 sample size was not the main reason BIO15 failed to become a specific explanatory axis. Expanding the panel with already-frozen occurrence information does not recover BIO15 specificity; instead, its adjusted coefficient becomes smaller while the reciprocal BIO1 direction remains more stable.

The appropriate biological description is therefore:

> **Present orientation corresponds to a composite climatic/lineage regime, not to a uniquely identified precipitation-seasonality driver.**

This strengthens the stop rule against further coarse climate-variable fishing. The next causal gain must come from a mechanistic chain such as orientation -> rain/wetting or radiation exposure -> pollen/stigma performance -> effective transfer -> viable achene fitness, not from adding more correlated climate proxies.

## Claim boundary

- relaxed occurrence thresholds are sensitivities, not replacements for the frozen n>=10 primary panel;
- BIO1 stability does not establish temperature causation;
- no result establishes climatic selection, adaptation, plasticity or transition-time cause;
- no new occurrence source, taxon alias or environmental predictor was added.
