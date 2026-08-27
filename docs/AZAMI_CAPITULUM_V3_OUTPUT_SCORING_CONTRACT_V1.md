# Azami capitulum v3 output/scoring contract v1

## Current decision

The 62 artifact-backed Azami targets are now statistically reproducible by an EAzami adapter, but they are **not yet scoreable from the current v2 simulator**.

This separates two previously conflated questions:

1. Can EAzami compute exactly the same estimands if a model emits compatible observation rows? **Yes.**
2. Does the current v2 generator emit those rows? **No.**

No semantic proxy is allowed to bridge that gap.

## Exact model observation interface

A scoreable model replicate must emit observation-level rows with `obs_id`, `taxon_name`, the same 18 continuous response endpoints, and the nine frozen environment columns used by Azami PR #72. Circular hue remains one inferential unit represented by sine/cosine.

The adapter then reproduces the Azami rules:

- response-complete cohorts at >=5 and >=2 observations per taxon;
- within-taxon centering with inverse taxon sample-size weights;
- among-taxon taxon medians;
- 17-unit association-strength matrices and registered-module contrasts;
- within-vs-among matrix Spearman similarity;
- six 18D environmental block R2 values at each biological scale;
- within-vs-among coefficient-matrix cosine for each environmental block;
- core4 vs process-extension nested multivariate delta-R2 and partial-R2.

The resulting model-side registry contains the same 62 `(target_id, scope, scale)` keys as the observational handoff.

## Current v2 blocker

`analysis/simulate_capitulum_pattern_reduction_v2.py` generates compact summaries from four synthetic module variables (`orientation`, `chroma`, `defence`, `shape`) and latent environmental variables. It does not emit:

- the frozen 18 endpoint names;
- the nine named CHELSA/process predictors on observation rows;
- min5/min2 complete-18 cohorts;
- the 17-unit association matrices;
- 18D block coefficient matrices;
- core4-vs-process-extension nested multivariate fits.

Therefore the current exact scoreability is 0/62 even though the statistics adapter is ready for 62/62.

In particular, the old cross-module-lability correlation is not a replacement for the 17-unit matrix similarity, and old scalar environment summaries are not replacements for 18D block R2.

## Next generator design

The next separately versioned generator should be **conditional on the frozen Azami environment design**, rather than estimating environmental covariances from the 62 response targets or inventing a new geographic distribution. Azami run `33035785120` already freezes a complete-18 observation cohort with the four core and five process predictors. The model should generate synthetic 18D phenotype rows on that fixed exogenous design, then pass those rows through the exact adapter.

Using the observed environmental design is not the same as using observed response phenotypes to tune the model. The response-side target summaries remain held out for model comparison.

The generator architecture, endpoint loadings, process-effect permissions and parameter priors must be frozen before model-family outcomes are inspected. In particular, do not tune loadings to reproduce the observed module contrast or environmental R2 values.

## Claim boundary

A low distance to these 62 observational targets would show that a model can reproduce selected multiscale phenotype/environment structure under a fixed design. It would not prove causal environmental mechanisms, adaptation, selection, plasticity, defensive function, or genetic/developmental modularity.
