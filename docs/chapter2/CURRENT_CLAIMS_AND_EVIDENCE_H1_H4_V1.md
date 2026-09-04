# Chapter 2 current claims and evidence after H1–H4

**Status date:** 2026-09-04  
**Role:** authoritative current-state synthesis for manuscript revision.  
**Active manuscript:** `MANUSCRIPT_JEB_V7_WORKING.md`.

## One-sentence paper claim

> **A multidimensional capitulum was repeatedly and mosaically assembled at unequal evolutionary depths within a young *Cirsium* radiation; orientation state changes additionally track a composite present-day niche regime in both directions, but that present regime does not persist across the uncertainty envelope of the only calendarized origin event.**

The paper therefore separates three increasingly difficult inferential layers:

```text
phenotypic assembly
→ present transition–niche tracking
→ historical origin environment
```

The first two are currently supported at different strengths. The third remains unresolved and, for the fixed H4 regime, is specifically not supported.

# Claim 1 — repeated mosaic assembly at unequal evolutionary depths

## Question

How was a multidimensional capitulum assembled within one young radiation?

## Materials

- 38 sampled Japanese paper concepts;
- 36/38 in the dominant Japanese radiation;
- independently reconstructed Compositae1061-compatible nuclear scaffold;
- 236 QC loci, 176 rootable loci, 161,654-bp concatenated alignment;
- IQ-TREE / ModelFinder, 1,000 UFBoot + 1,000 SH-aLRT;
- authority-backed state coverage:
  - orientation: 20 concepts;
  - phyllary posture: 10 concepts;
  - involucre stickiness: 13 concepts.

## Analysis

- unordered minimum-change reconstruction on ML + 1,000 UFBoot topologies;
- exact dynamic-programming lower/upper mean relative-lineage-depth bounds across all globally minimum-cost histories;
- paired depth ordering on the same 1,000 topology realizations;
- deterministic coverage-matched missing-state masking;
- pairwise shared-transition-localization diagnostics.

## Positive results

Minimum changes:

- orientation: ML 6; UFBoot 4–6, median 5;
- phyllary posture: exactly 3;
- stickiness: exactly 5.

Paired lower-bound ordering:

- phyllary deeper-permissive than stickiness: **1000/1000**;
- phyllary deeper-permissive than orientation: **993/1000**;
- orientation deeper-permissive than stickiness: **905/1000**, 7 ties;
- complete `phyllary < orientation < stickiness`: **898/1000**.

Coverage matching:

- phyllary deeper than matched orientation median: **195/200 = 97.5%**;
- phyllary deeper than matched stickiness median: **193/200 = 96.5%**;
- strict q05 separation only **10.5–15.5%**, so deep tails overlap.

Shared transition localization:

- **0/3 trait pairs** pass the robust rule.

## Supported interpretation

> **The capitulum shows repeated mosaic historical assembly: component histories recur, occupy unequal central evolutionary depths, and are not repeatedly synchronized on the same branches.**

Do not convert this into independent origins, evolutionary rates, developmental independence, or adaptation.

# Claim 2 — present orientation ecology is scale-partitioned

## Question

Does orientation have one universal environmental response, or does ecological correspondence depend on biological scale?

## Materials

- frozen Azami within/among orientation–environment artifact;
- East-Asian orientation state panel;
- shared BIO12, BIO15, BIO1 axes.

## Positive results

- BIO12: among-taxon beta **+0.30436**, q **0.00640**; within beta +0.00533, q 0.874 → among-only.
- BIO1: within beta **+0.01715**, q **0.0349**; among unsupported; East-Asian D−U approximately **−0.975 to −0.967 SD**.
- BIO15: East-Asian D−U **+1.320 to +1.330 SD**, sign stable 6/6 topologies and 54/54 topology × species-LOO fits, but no corresponding positive within-taxon result.

## Supported interpretation

> **Orientation–environment correspondence is scale-partitioned rather than one universal reaction rule.**

# Claim 3 — H1: repeated orientation transitions track a fixed composite present niche regime

## Specific hypothesis

For U→D orientation change, branches with greater U→D than D→U transition probability should align with the predeclared vector:

```text
BIO15 ↑  +  BIO1 ↓
```

No other climate axis was screened after this hypothesis was frozen.

## Materials and estimator

- n>=5 panel: 12 taxa, 7 U / 5 D;
- n>=3 sensitivity: 13 taxa, 7 U / 6 D;
- strict n>=10 panel: 9 taxa, 5 U / 4 D;
- six accepted AU topologies;
- symmetric two-state CTMC with edge joint transition posteriors;
- Brownian branch reconstruction of BIO15 and BIO1 niche centroids;
- exact exhaustive count-preserving state-map nulls.

## Positive results

Primary n>=5:

- composite positive 6/6 topologies;
- median **0.253119**;
- exact rank **16/792 = 2.02%**.

n>=3 sensitivity:

- composite positive 6/6;
- exact rank **19/1716 = 1.11%**.

Strict n>=10:

- composite positive 6/6;
- median **0.330854**;
- exact rank **4/126 = 3.17%**.

Axis decomposition demonstrates why the composite matters:

- strict BIO15 alone: **7/126 = 5.56%**;
- strict lower-BIO1 alone: **8/126 = 6.35%**;
- strict composite: **4/126 = 3.17%**.

The n>=5 result is driven more strongly by the lower-BIO1 component (15/792 = 1.89%) than by BIO15 alone (123/792 = 15.53%).

## Boundary

Japan-only n>=5 remains directionally positive but is not exceptional:

- **10/56 = 17.86%**.

Thus H1 is strict-coverage robust but region/lineage-context sensitive.

# Claim 4 — H2: the same present niche regime is tracked in both transition directions

## Specific hypothesis

If the association is a reversible state–regime correspondence rather than only a U→D pattern, then:

- U→D should align with `BIO15 ↑ + BIO1 ↓`;
- D→U should align with the exact reverse `BIO15 ↓ + BIO1 ↑`.

## Result

Strict 9-taxon panel:

- H1 reproduction: **0.3308536811**, exact pass;
- forward U→D alignment median: **0.320891**;
- reverse D→U alignment median: **0.339529**;
- both positive on **6/6** accepted topologies;
- median bidirectional floor: **0.320891**;
- exact floor rank: **3/126 = 2.38%**.

Classification:

`bidirectional_reversible_regime_supported`

## Single-taxon falsification

Delete each of the nine strict-panel taxa once and recompute both directions and the exhaustive null.

- forward and reverse remain positive on 6/6 topologies in **9/9 deletions**;
- exact floor <=0.05 survives **3/9** deletions only.

Classification:

`bidirectional_direction_not_single_taxon_dependent`

## Supported interpretation

> **Orientation states show distributed, bidirectional present-niche regime tracking under the declared CTMC/Brownian estimator. The direction does not require any single taxon, although the strength of exact finite-map exceptionality is multi-taxon/deletion-sensitive.**

This is not evidence for evolutionary irreversibility/reversibility of the trait mechanism, selection, or adaptation. “Reversible” here refers only to opposite-direction present-niche tracking under the declared estimator.

# Claim 5 — H4: the present regime is not supported as the historical origin regime

## Specific hypothesis

For the only calendarized core-*Nipponocirsium* U→D event, the historical endpoint signs should reproduce the current U→D regime:

```text
BIO15 delta > 0
AND
BIO1 delta < 0
```

## Materials

- event: `ORI_CORE_NIPPONO_STEM`;
- 94 admissible chronology pairs;
- four fixed palaeolocation regions;
- **376 chronology × region scenarios**;
- existing PALEO-PGEM historical BIO1/BIO15 rows only;
- sign-only test, no reweighting or rescaling;
- support criterion frozen at >=75% matching chronologies in each of all four regions.

## Result

Classification:

`historical_regime_persistence_not_supported`

Overall H4 match:

- **99/376 = 26.3%**.

Per region:

- Taiwan: **20/94 = 21.3%**;
- Ryukyu corridor: **9/94 = 9.6%**;
- southern Japan: **41/94 = 43.6%**;
- East-Asia core corridor: **29/94 = 30.9%**.

Only:

- **6/94** chronology pairs match in 4/4 regions;
- **14/94** match in >=3/4 regions.

Central 0.79→0.74 Ma chronology:

- BIO1 decreases in all four regions, consistent with one component of the present regime;
- BIO15 also decreases in all four regions, opposite the current U→D BIO15 direction;
- therefore H4 fails in 4/4 central regional scenarios.

## Supported interpretation

> **The present bidirectional orientation–niche regime should not be projected backward as the historical trigger of the bounded core-*Nipponocirsium* U→D event. Present ecological tracking and origin-time historical environment are decoupled under the available evidence.**

This is an **origin–maintenance/current-sorting decoupling** result, not evidence that environment was irrelevant at origin.

# Claim 6 — historical cause remains less identifiable than assembly and present tracking

Only one current capitulum transition reaches the full chain:

```text
trait transition
→ bounded chronology
→ palaeolocation scenarios
→ historical environment
```

Other frozen historical diagnostics remain:

- 17-BIOCLIM lineage atlas: **0/324** robust event-level classes;
- global sea-level diagnostic: **0/21** robust event-metric classes;
- southern Japan is a descriptive leading palaeolocation scenario but does not cross the 75% dominance gate.

Thus the paper should no longer say only “cause is unresolved.” The stronger structure is:

```text
assembly history                    = strongly resolved
present transition–niche tracking  = specifically supported for orientation
persistence of that regime at origin = specifically not supported
historical causal mechanism        = not identified
```

# Current manuscript story

## Primary biological claim

> **Complex phenotype assembly is mosaic through evolutionary time.**

## Secondary biological claim

> **One component, orientation, is not merely correlated with current climate at the tips: its inferred U↔D transition directions align bidirectionally with opposite sides of a fixed present-niche regime, and that direction survives deletion of any single strict-panel taxon.**

## Critical historical contrast

> **The same present-niche regime does not persist through the uncertainty envelope of the only dated U→D origin event.**

Together:

> **Current ecological sorting/maintenance can be strongly coupled to an evolved phenotype without identifying—or even matching—the environmental regime under which that phenotype originated.**

# Methodological contribution

The active framework now has six linked components:

1. reconstruction-aware nulls for reconstructed branch-change correlations;
2. exact minimum-history relative-depth envelopes;
3. paired-topology robustness;
4. coverage-matched state masking;
5. exhaustive history-conditioned/counterfactual state-map tests;
6. directional transition–environment decomposition followed by a fixed historical persistence falsification.

The methodological message is not “a new ASR algorithm.” It is:

> **Different evolutionary questions require different nulls and different uncertainty conditioning; a present ecological association should not be promoted to a historical causal explanation without explicitly testing whether its regime persists at the transition event.**

# Main material inventory

| Material | Current use |
| --- | --- |
| Moreyra-compatible Japan38 nuclear scaffold | focal young-radiation backbone |
| 1,000 UFBoot topologies | minimum-change and depth uncertainty |
| authority orientation states, n=20 | repeated history + ecological bridge |
| authority phyllary states, n=10 | repeated/deeper-permissive component history |
| authority stickiness states, n=13 | repeated/shallow-biased component history |
| paired depth result | direct topology-wise depth ordering |
| coverage-matched masks | missing-state sensitivity |
| shared localization result | mosaic vs synchronized-history test |
| Azami within/among artifact | cross-scale present ecology |
| Japan/Taiwan thinned CHELSA occurrence assets | 9/12/13-taxon present-niche panels |
| six accepted AU topologies | ecology/transition-regime topology sensitivity |
| 126/792/1716 exact state-map universes | H1/H2 finite counterfactual tests |
| single-taxon deletion universes | distributed-vs-single-lineage falsification |
| core-*Nipponocirsium* chronology | only fully bounded orientation event |
| 94 chronology × 4 palaeolocation grid | H4 historical persistence falsification |
| PALEO-PGEM BIO1/BIO15 | bounded event historical sign test |
| 17-BIOCLIM / sea-level atlases | broader historical-cause ceiling |
| external *Cremanthodium* manipulation | mechanism prior only, not focal evidence |

# Claims that remain prohibited

Do not claim:

- minimum changes = independent origins or convergence;
- unequal relative depth = unequal evolutionary rates;
- H1/H2 = climatic selection or adaptation;
- “reversible tracking” = demonstrated genetic or developmental reversibility;
- present BIO15/BIO1 regime = historical origin driver;
- H4 failure = environment was irrelevant;
- palaeolocation fractions = ancestral-area probabilities;
- current evidence identifies rain/wetting, UV, temperature, or pollinator mechanism in East-Asian *Cirsium*;
- the external *Cremanthodium* effect size transfers to *Cirsium*.

# Manuscript revision consequence

The current V7 title can remain:

**Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation**

The abstract/results/discussion should now add the orientation-specific second result:

> **A fixed two-axis present-niche regime is tracked in both U→D and D→U directions, but the same regime is not supported across the historical uncertainty envelope of the only calendarized U→D event.**

This should replace the weaker terminal framing “present ecology is history-embedded and historical cause is unresolved” wherever space allows.
