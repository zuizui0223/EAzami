# Orientation transition-regime robustness v1

Status: **validated post-result falsification**  
Date: 2026-09-04

## Fixed hypothesis

The already-supported H1 was not altered:

> U→D orientation transition probability aligns with the composite present-day niche direction **(+BIO15, −BIO1)**.

The CTMC/Brownian branchwise estimator and the ≤0.05 exact finite-map rank rule were also unchanged.

## Strict n>=10 coverage test

Using only the original nine taxa meeting the frozen n>=10 occurrence gate (5 U, 4 D), all 126 count-preserving orientation maps were enumerated.

Observed composite:

- positive on **6/6** accepted topologies;
- median **0.330854**;
- exact rank **4/126 = 3.17%**.

Therefore H1 **passes** under the original strict occurrence gate. The positive 12-taxon result is not an artefact of relaxing the occurrence threshold to n>=5.

Single-axis decomposition did not pass the same threshold:

- BIO15 alone: **7/126 = 5.56%**;
- lower BIO1 alone: **8/126 = 6.35%**.

Thus the strict-panel result specifically supports the **predeclared composite regime**, not either single climate variable.

## Japan-only n>=5 test

After removing Taiwan taxa, eight Japanese taxa remained at n>=5 (5 U, 3 D). All 56 count-preserving maps were enumerated.

Observed composite:

- positive on **6/6** topologies;
- median **0.175918**;
- exact rank **10/56 = 17.86%**.

This does **not** pass the frozen ≤0.05 rule.

The component ranks were also non-exceptional:

- BIO15: **18/56 = 32.14%**;
- lower BIO1: **7/56 = 12.5%**.

## Boundary reached

Classification:

**`transition_regime_concordance_strict_coverage_robust_but_region_sensitive`**.

The concrete inference is therefore:

> **The composite U→D transition-regime concordance is robust to the original strict occurrence threshold, but its exceptional rank depends on the broader East-Asian panel and is not recovered as a Japan-only rule.**

This makes the result more specific, not weaker in an undefined way. It rules out relaxed coverage as the main explanation while identifying regional/lineage composition as a real boundary.

It still does not identify historical climate at transition time, a selective agent, adaptation, or a physiological mediator.

## Provenance

Workflow `33846549634`  
Artifact `9926735895`  
SHA256 `374723152d39b79c5e15b8f459268f6d4a1498e4d294b609a293003548865da7`
