# Orientation transition directionality H2 — reversible regime tracking

## Question

Does the fixed orientation transition-regime correspondence occur only for U->D changes, or do D->U transition probabilities track the exact opposite present-day niche direction as well?

The hypothesis and environmental axes were frozen before execution:

- U->D: `BIO15 up + BIO1 down`;
- D->U: `BIO15 down + BIO1 up`.

The analysis used the strict n>=10 East-Asian panel (9 taxa, 5 U / 4 D), the same six accepted topologies, the same Brownian BIO15/BIO1 reconstructions, a symmetric two-state CTMC, and all 126 count-preserving state maps. The previous strict-panel H1 statistic had to be reproduced exactly before H2 was interpreted.

## Result

Classification:

`bidirectional_reversible_regime_supported`

H1 reproduction passed exactly: **0.3308536811**.

Directional alignments:

- U->D forward alignment median = **0.320891**; positive on **6/6** topologies.
- D->U reverse alignment median = **0.339529**; positive on **6/6** topologies.
- Median bidirectional floor = **0.320891**.
- Exact finite-map rank of the bidirectional floor = **3/126 = 2.38%**.

Thus both directions track opposite sides of the same fixed two-axis niche regime under the declared estimator, and the weaker of the two alignments remains exceptional relative to all count-preserving alternatives.

## Interpretation

This result is stronger than a one-way terminal-state contrast. It supports **bidirectional reversible present-niche transition-regime tracking**: branches with greater U->D transition probability align with the higher-BIO15/lower-BIO1 direction, while branches with greater D->U transition probability align with the reverse direction.

It does **not** establish historical climate at transition time, climate-driven selection, adaptation, plasticity, or a wetting/UV/temperature mediator. The result is a post-result mechanistic falsification of H1 and remains conditioned on the declared East-Asian panel and CTMC/Brownian reconstruction.

## Provenance

Workflow `33850432620` succeeded. Artifact `9928126499`, SHA256 `838ed0bd7c05419beba390767131ec53475a236926e8514949060bfc01eec9b3`.
