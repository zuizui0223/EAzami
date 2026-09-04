# H2 bidirectional transition-regime tracking — single-taxon falsification

## Question

Does the bidirectional H2 result depend on any one taxon in the strict n>=10 East-Asian panel?

Each of the nine taxa was deleted once. For each reduced panel the same U->D forward vector (`BIO15 up + BIO1 down`), D->U reverse vector, six topologies, CTMC/Brownian estimator and exhaustive count-preserving null were retained.

## Result

Classification: `bidirectional_direction_not_single_taxon_dependent`.

- Forward alignment remained positive on **6/6 topologies after all 9/9 deletions**.
- Reverse alignment also remained positive on **6/6 topologies after all 9/9 deletions**.
- Exact `<=0.05` bidirectional-floor rank survived **3/9** deletions: `C. alpicola` (2/70 = 2.86%), `C. kamtschaticum` (2/56 = 3.57%), and `C. yezoense` (1/56 = 1.79%).
- The other six reduced panels were 7.14% exact ranks.

## Interpretation

The **bidirectional direction itself is not carried by any single taxon**. Both U->D and D->U retain opposite environmental alignment after every single-taxon deletion.

The stronger finite-map exceptionality is not deletion-stable. It is therefore appropriate to separate two claims:

1. robust: bidirectional directionality is distributed across the strict East-Asian panel rather than driven by one taxon;
2. bounded: extreme exact rank is a property of the full multi-taxon configuration and some, but not all, reduced panels.

This remains present-niche transition-regime concordance. It does not identify historical climate at transition time, selection, adaptation, or a physical mediator.

## Provenance

Workflow `33850901353` succeeded. Artifact `9928305111`, SHA256 `d3a629e03b993f4da04b4ad753ade8cd2eb9de8bf296801641f5f44834032e8c`.
