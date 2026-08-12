# Flower-colour transition-rate fit preconditions

Date: 2026-08-12

## Purpose

The Arenicola partial-calibrated Mk sensitivity showed that the direction of the `C. brevicaule` / `C. irumtiense` colour transition depends on assumptions about the frequency and asymmetry of C->W versus W->C changes. A broader *Cirsium* colour dataset is therefore load-bearing for the Ryukyu inference.

However, increasing the number of colour-coded taxa is not enough. Empirical transition-rate fitting also requires a defensible branch-length nuclear tree or tree ensemble. This contract prevents either side from silently substituting for the other.

## Current atlas gate

The intended v0.3 atlas has:

- 20 eligible taxon-level tips;
- C=17;
- W=3;
- adequate coloured-tip and phylogeny-context breadth;
- polymorphic taxa retained as P rather than collapsed.

Therefore the only **atlas** engineering blocker is `minimum_white_tips`.

The A1 fixed-white target-capture panel (`C. boninense` + `C. wulongense`) is designed so that two credible new nuclear placements would move the numerical white-tip gate from W=3 to W=5. That still does not unlock rate fitting by itself.

## Current tree gate

No accepted machine-readable branch-length tree route is yet complete.

### Published-tree route

Issue #12 tracks the Moreyra 2025 final concatenated/coalescent/dated trees. Public archive searches and the recovered author repository have not produced the final Newick/Nexus files or the exact retained 350-locus matrix. Figure-derived topology must not be converted into invented branch lengths.

### Compatibility-reanalysis route

Public Moreyra locus diagnostics support reproducible 1061-locus, 531-candidate and 241 conservative locus universes, but the reanalysis tree has not been executed. Issue #16 currently reports that the exact or compatible Compositae1061 HybPiper target/reference FASTA was not recovered. The source-backed COS763 alignments are useful as mapping/frame-correction material only and are not relabelled as the missing Moreyra target.

This means choosing the same Compositae1061 **bait/assay concept** for new fixed-white material may maximize potential locus overlap, but it does not make the downstream pipeline an exact Moreyra reproduction. If target-reference/probe access remains a practical blocker, Angiosperms353 or low-coverage WGS remains a legitimate independent nuclear-placement route; the resulting tree must be labelled and analysed as such.

## Mechanical execution rule

`analysis/validate_flower_colour_rate_fit_preconditions.py` permits empirical rate fitting only when both are true:

1. all predeclared atlas breadth/state gates pass, including W>=5;
2. `data/evidence/flower_colour_rate_tree_contract_v0_1.json` records an accepted empirical branch-length tree route.

At the current state the expected blockers are exactly:

```text
atlas_minimum_white_tips
branch_length_tree_unavailable
```

## What execution_allowed=true would mean

It would mean only that an empirical ER/ARD/Mk analysis is allowed to start. It would **not** mean that:

- ARD is better than ER;
- C->W is faster than W->C;
- the Arenicola MRCA was coloured or white;
- `C. irumtiense` represents a regain;
- an anthocyanin pathway was molecularly reactivated.

Those claims require model comparison, topology/branch-length uncertainty, sampling-bias sensitivity, explicit treatment of polymorphic taxa, model adequacy, population ancestry and ultimately floral molecular evidence.
