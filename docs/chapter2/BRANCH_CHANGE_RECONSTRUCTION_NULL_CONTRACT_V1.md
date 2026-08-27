# Branch-change reconstruction-aware null contract v1

Status: **frozen before outcome inspection**  
Date: 2026-08-27

## Problem

The current continuous branch-change test reconstructs internal phenotype states on one tree, calculates standardized branch-wise change magnitudes for eight phenotype dimensions, and then tests their mean pairwise Spearman correlation by permuting already reconstructed branch values.

That null destroys cross-trait branch alignment, but it may also destroy branch-specific leverage introduced by using the same phylogeny and ancestral-reconstruction operator for every trait. A positive branch-change correlation could therefore be inflated if some branches are intrinsically more capable of receiving large reconstructed changes even for independently assigned tip traits.

## Primary question

> **Does the observed cross-trait branch-change coordination exceed the coordination expected solely from placing independent phenotype assignments through the same phylogeny and ancestral-state reconstruction procedure?**

## Frozen data

Use exactly the same inputs as the current primary continuous branch-change analysis:

- source continuous bridge frozen on the Chapter-2 branch;
- common >=2-observation panel of eight exact concepts;
- eight primary continuous inferential units;
- frozen Japan38 Comp1061 primary phylogram;
- branch lengths in substitutions/site;
- same Brownian conditional-state reconstruction;
- same standardization and branch-change definitions.

No additional taxa, endpoints or phenotype transformations may be introduced after the outcome is observed.

## Observed statistic

Use the existing statistic unchanged:

- reconstruct branch-change magnitude for all eight units;
- calculate all 28 pairwise Spearman correlations across branches;
- take their arithmetic mean.

The observed value must reproduce the current ML result (approximately 0.4080062794) before the null is evaluated.

## Null construction

For each of **9,999** permutations:

1. keep the phylogeny, branch lengths, taxon set and phenotype marginal values fixed;
2. independently permute the tip labels of each scalar phenotype dimension across the eight concepts;
3. treat circular hue as one phenotype unit: permute the paired normalized sine/cosine tip vector together, never its two components independently;
4. rerun Brownian conditional ancestral reconstruction from the permuted tip values;
5. recalculate standardized branch-change magnitudes with the same formula as the observed analysis;
6. recalculate the 28 pairwise branch-change Spearman correlations and their global mean.

This null preserves tree geometry and reconstructs every permutation through the same historical operator while destroying cross-trait concordance of the observed tip assignments.

## Primary test

One-sided P value:

`P = (1 + number(null >= observed)) / (9999 + 1)`.

Primary support requires **P < 0.05**.

Also report:

- null mean;
- null median;
- q05 / q95;
- observed-minus-null-median;
- empirical percentile of the observed statistic.

## Decision rule

### PASS

If P < 0.05:

The manuscript may retain the bounded statement:

> **Cross-trait coordination of reconstructed continuous change exceeds the coordination expected from common tree/reconstruction geometry alone.**

Topology robustness remains a separate requirement and does not become a mechanism claim.

### FAIL

If P >= 0.05:

- do **not** tune the null, branch statistic, endpoint set or common taxon panel;
- demote the observed 0.408 branch-change correlation to a descriptive ML-phylogram result;
- remove `coordinated evolutionary remodeling` as the primary JEB headline;
- retain the recurrence/state-conservation paper if still scientifically coherent;
- record that common phylogenetic reconstruction geometry is sufficient to explain the apparent broad branch-change coupling.

## Claim boundary

A PASS does not prove:

- shared developmental or genetic control;
- common selection;
- adaptation;
- convergence;
- absolute evolutionary rate;
- simultaneous change in calendar time.

It only strengthens the structural statement that the observed trait assignments carry more shared branch-localization information than expected under independently relabelled tip phenotypes processed through the same tree and reconstruction method.
