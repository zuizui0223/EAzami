# Orientation transition-regime H1 — single-taxon deletion falsification v1

## Question

Does the fixed East-Asian transition-regime result depend on any single taxon in the strict n>=10 panel?

The hypothesis was not changed:

`U -> D` transition weighting should align with the predeclared composite environmental direction `BIO15 up + BIO1 down`.

Each of the nine strict-panel taxa was deleted once. The remaining eight taxa were restandardized, the same CTMC/Brownian statistic was recalculated on the same six accepted topologies, and every count-preserving state map was enumerated (70 maps after deleting a U taxon; 56 after deleting a D taxon).

## Result

Classification:

`transition_regime_direction_not_single_taxon_dependent_but_exceptionality_sensitive`

- Direction remained positive on **all six topologies after all 9/9 single-taxon deletions**.
- Exact `<=0.05` exceptionality survived only **2/9** deletions.
- It survived deletion of `C. alpicola` (1/70 = **1.43%**) and `C. yezoense` (1/56 = **1.79%**).
- The remaining deletion ranks were narrowly to moderately above the frozen threshold: **5.36–7.14%** for most panels.

## Interpretation

The **directional transition-regime concordance is not driven by one taxon**. No single taxon is required for the composite statistic to remain positive across all accepted topologies.

However, the stronger claim that the observed configuration is exceptionally extreme relative to all count-preserving alternatives is **not deletion-stable**. That exceptionality is a property of the multi-taxon East-Asian configuration and is sensitive to the reduced finite-map panels after deletion.

This result therefore strengthens the directional statement but bounds the exact-rank statement:

- supported: repeated U->D history is consistently aligned with the fixed composite direction in the full strict East-Asian panel and under every one-taxon deletion;
- not supported: every reduced panel remains <=5% exceptional;
- not claimed: climatic causation, selection, adaptation, historical transition-time environment, or a wetting/UV/temperature mediator.

## Provenance

Workflow `33846927401` succeeded. Artifact `9926883514`, SHA256 `892a3f281ff324014dbbbd14b5171ddb275ccd143198a58eab92e9e8aac89216`.
