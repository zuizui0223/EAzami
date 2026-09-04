# Orientation transition-regime hypothesis v1

Status: **validated specific hypothesis test**  
Date: 2026-09-04

## Question

Do repeated changes from upward/erect (U) toward downward/nodding (D) orientation repeatedly align with the same environmental regime direction, rather than merely producing a terminal-state mean contrast?

The hypothesis was fixed before the expanded-panel result was inspected:

> branches carrying greater U->D than D->U transition probability should align with **higher precipitation seasonality (BIO15) and lower annual mean temperature (BIO1)**.

This was a two-axis hypothesis. It was not a search across climate variables and did not posit BIO15 or BIO1 individually as the cause.

## Analysis

For each of six accepted nuclear topologies:

1. fit a symmetric two-state CTMC to orientation states;
2. compute exact edge joint posteriors `P(U,D)` and `P(D,U)`;
3. reconstruct standardized BIO15 and BIO1 by Brownian squared-change minimization;
4. weight each environmental branch shift by `P(U,D)-P(D,U)`;
5. project the two branchwise statistics onto the predeclared vector `(+BIO15, -BIO1)`;
6. summarize each state map by the median over the six topology sensitivities.

For the 12-taxon n>=5 panel (7 U, 5 D), every one of the `C(12,5)=792` count-preserving state maps was enumerated. For the 13-taxon n>=3 sensitivity (7 U, 6 D), all 1,716 maps were enumerated.

Before interpreting these panels, the implementation had to reproduce the legacy n=9 branchwise estimator. It did essentially exactly:

- BIO15: new **0.267907–0.269417**, legacy **0.267907–0.269417**;
- BIO1: new **-0.199306 to -0.199151**, legacy **-0.199306 to -0.199151**.

The fail-closed method check therefore passed.

## Primary result: n>=5, 12 taxa

The composite transition-regime statistic was positive on all six accepted topologies:

`0.252565–0.253692`, median **0.253119**.

The observed component medians were:

- BIO15 branchwise direction: **+0.117305**;
- BIO1 branchwise direction: **-0.240615**.

Only **16/792 = 2.02%** of all count-preserving state maps had a six-topology median composite statistic at least as large as observed.

The frozen decision rule was therefore passed:

**`repeated_u_to_d_transition_regime_concordance_supported`**.

## Axis decomposition

The positive result should not be rewritten as a BIO15 result.

- BIO15 alone: **123/792 = 15.53%** at least as strong as observed;
- lower-BIO1 direction: **15/792 = 1.89%** at least as strong as observed.

Thus the declared two-axis regime is unusual, but its stronger individual contribution comes from the **lower-BIO1 / cooler present-niche direction**, not from precipitation seasonality alone.

## n>=3 sensitivity

The 13-taxon panel reproduced the same qualitative result:

- composite median **0.311342**;
- exact composite rank **19/1,716 = 1.11%**;
- BIO15-only rank **123/1,716 = 7.17%**;
- lower-BIO1 rank **16/1,716 = 0.93%**.

This is a resolution sensitivity and does not replace the n>=5 primary hypothesis test or the frozen n>=10 present-day ecology panel.

## Biological conclusion

The supported statement is:

> **Repeated U-to-D orientation transition probability is aligned with a recurring composite present-day niche direction—higher BIO15 and, more strongly, lower BIO1—more strongly than expected under exhaustive count-preserving alternative trait maps.**

This is stronger than a terminal-state comparison because the statistic is branchwise and transition-probability weighted.

It is still not a causal result. Present-day niche centroids are not historical environments at the moment of transition. The analysis therefore does not establish that cold, precipitation seasonality, rain/wetting, UV exposure, pollinators, or any other agent selected downward orientation.

## Next falsification

The same fixed vector and estimator should now be challenged under two stricter conditions, without changing predictors:

1. the strict n>=10 nine-taxon panel with all 126 state maps;
2. a Japan-only n>=5 panel with all count-preserving maps.

These tests ask whether the positive H1 depends on relaxed occurrence coverage or the Taiwan/Japan composition.

## Provenance

Workflow run: `33845826254`  
Artifact: `9926532782`  
SHA256: `f82733d5a3f9b5783267ee8c67b6ed2f4105f4a42d9359b66df9a94f92057110`
