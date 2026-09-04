# BIO15 specificity and near-lineage contrast boundary

Status date: 2026-09-04  
Role: **validated post-result mechanism-discrimination boundary**

## Question

After the orientation–BIO15 correspondence survived removal of Taiwan and coarse latitude/longitude adjustment, can precipitation seasonality be isolated more specifically from the already-frozen temperature axis (BIO1), and does the same environmental direction recur in the closest opposite-orientation extant taxon pairs?

No new environmental variables were introduced.

## Test 1 — BIO15 conditional on BIO1 and geography

Brownian GLS across the same six accepted topologies:

`z(BIO15) ~ orientation + z(BIO1) + z(latitude) + z(longitude)`

Orientation coefficient:

- **+0.744 to +0.778 SD**;
- median **+0.761 SD**;
- P = **0.336–0.356**;
- topology sign agreement **6/6**;
- species-LOO sign agreement **48/54**;
- LOO coefficient range **−0.307 to +1.250**.

Thus BIO15 retains the observed direction on every full topology fit, but not under every species deletion. It does not pass the frozen specificity requirement.

## Reciprocal test — BIO1 conditional on BIO15 and geography

`z(BIO1) ~ orientation + z(BIO15) + z(latitude) + z(longitude)`

Orientation coefficient:

- **−0.490 to −0.487 SD**;
- P = **0.527–0.535**;
- topology sign agreement **6/6**;
- species-LOO sign agreement **54/54**.

BIO1 therefore retains a more deletion-stable direction than BIO15 in the mutually adjusted models, although neither adjusted coefficient crosses the inferential threshold.

## Test 2 — held-out incremental BIO15 prediction

Baseline prediction used BIO1 + latitude + longitude together with Brownian conditional prediction. Orientation was then added.

Across all six accepted topologies:

- ΔMSE = **−0.512 to −0.505**;
- median ΔMSE = **−0.508**;
- ΔMAE = **−0.293 to −0.287**;
- topologies with positive predictive improvement = **0/6** for both MSE and MAE.

Thus orientation does not add held-out BIO15 predictive information beyond BIO1, coarse geography and phylogenetic covariance in the current n=9 panel.

## Test 3 — environment-blind phylogenetic matching

Opposite-state extant taxa were paired solely by minimum total patristic distance, before examining climate differences.

### Full nine-taxon panel

The same matching was selected on all six topologies:

- *C. kamtschaticum* (D) — *C. japonicum* var. *japonicum* (U)
- *C. kawakamii* (D) — *C. brevicaule* (U)
- *C. suffultum* (D) — *C. irumtiense* (U)
- *C. yezoense* (D) — *C. alpicola* (U)

BIO15:

- positive D−U contrasts: **2/4** pairs;
- median D−U = **+1.073 SD**;
- range **−0.237 to +2.771 SD**.

BIO1:

- negative D−U contrasts: **3/4** pairs;
- median D−U = **−1.181 SD**;
- range **−2.065 to +0.170 SD**.

### Japan-only seven-taxon panel

The same three pairs occurred on all six topologies:

- *C. kamtschaticum* (D) — *C. brevicaule* (U)
- *C. suffultum* (D) — *C. irumtiense* (U)
- *C. yezoense* (D) — *C. alpicola* (U)

BIO15:

- positive contrasts: **2/3**;
- median **+0.586 SD**;
- range **−0.208 to +2.771 SD**.

BIO1:

- negative contrasts: **2/3**;
- median **−1.359 SD**;
- range **−2.420 to +0.170 SD**.

The near-lineage comparison is therefore directionally suggestive in its medians but explicitly mixed at the pair level.

## Classification

`bio15_direction_persists_without_axis_specificity`

## Interpretation

The new analysis rules out a stronger claim rather than producing a new single-axis mechanism.

BIO15 remains part of the present orientation-associated climatic regime, but it cannot currently be isolated from BIO1, coarse geography and lineage structure as a unique explanatory axis. The reciprocal BIO1 direction is at least as stable under taxon deletion, and neither BIO15 nor BIO1 reproduces its state contrast in every closest opposite-state pair.

The defensible biological description is therefore:

> **Orientation marks a composite present climatic/lineage regime rather than a uniquely identified precipitation-seasonality axis.**

This is consistent with the earlier scale- and history-conditioned result and further weakens a one-variable direct-gradient explanation.

## What this changes

- **Strengthened:** the East-Asian orientation state contrast is not simply a Taiwan/Japan or linear latitude/longitude artefact.
- **Not strengthened:** BIO15 as a uniquely specific explanatory climate axis.
- **Still unresolved:** which environmental or biotic process caused orientation differentiation historically.

The next meaningful causal evidence must discriminate mechanism or fitness, rather than add more correlated climate proxies.

## Frozen provenance

- contract: `data/evidence/chapter2_bio15_specificity_matched_contrast_contract_v1.json`
- result: `data/evidence/chapter2_bio15_specificity_matched_contrast_result_v1.json`
- analysis: `analysis/run_chapter2_bio15_specificity_matched_contrast_v1.py`
- workflow run: `33842648617`
- artifact: `9925423215`
- SHA256: `a20f742e2c6c1140598f9071f9f7b9835337643ea6ecff7d28d8529f677f7aa9`
