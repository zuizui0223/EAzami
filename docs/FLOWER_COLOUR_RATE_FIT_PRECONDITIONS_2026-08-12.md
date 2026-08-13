# Flower-colour transition-rate fit preconditions

Date: 2026-08-12

## Purpose

The Arenicola partial-calibrated Mk sensitivity shows that the inferred direction of the `C. brevicaule` / `C. irumtiense` colour transition depends on assumptions about C->W versus W->C transition rates. A broader source-backed character dataset and a defensible branch-length nuclear tree are therefore both load-bearing.

## Atlas gate

Flower-colour atlas v0.3 is CI-validated at:

- 20 eligible taxon-level tips;
- C=17;
- W=3;
- all coloured-tip and phylogeny-context breadth gates passed;
- polymorphic taxa retained as P rather than collapsed.

The only atlas engineering blocker is `minimum_white_tips`. The A1 fixed-white panel (`C. boninense` + `C. wulongense`) is designed so that two credible new nuclear placements would move W=3 to W=5.

## Tree gate

No accepted machine-readable branch-length tree route is complete yet.

### Published-tree route

Issue #12 tracks Moreyra 2025 final concatenated/coalescent/dated trees. Public archive searches and the author repository have not produced final Newick/Nexus files or the exact retained 350-locus matrix. Figure-derived topology must not be converted into invented branch lengths.

### Compatibility-reanalysis route: upstream reference recovered

The original public Compositae1061 HybPiper reference has now been recovered from `carol-siniscalchi/Comp1061-Angio353` and independently validated by EAzami CI.

Frozen contract:

- `data/evidence/comp1061_original_reference_contract_v1.json`
- source commit `c340244907c39579dca42060769678bf8759fa1d`
- Git blob SHA1 `4f89e234007f367ffa8aa5e2be536bc44f31f445`
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`
- 1,162,856 bytes;
- 2,597 reference sequences;
- exactly 1,061 loci;
- `lett` and `sunf` sequences for all 1,061 loci, `saff` for 475;
- 586 loci represented by two reference species and 475 by all three.

Recovery workflow run `31556924969` completed successfully. The source repository's own analysis script passes this reference structure directly to HybPiper and proceeds through sequence retrieval, alignment, gene trees and ASTRAL.

This changes the compatibility route from **target-blocked** to **execution-not-yet-completed**.

It does **not** recover the exact Moreyra preprocessing input. Moreyra et al. added exons recovered from their highest-coverage `Cirsium tioganum` sample to the original Compositae1061 reference. That augmented file remains unrecovered, as does the exact retained 350-locus set. Compatibility analyses must therefore remain explicitly labelled as such.

Public Moreyra locus diagnostics still provide predeclared sensitivity sets:

- 1,061 public named loci;
- 531 warning/occupancy candidates;
- 241 conservative no-warning high-occupancy loci.

The next tree step is to execute a common-locus compatibility analysis, not to keep treating the original target reference as missing.

## Mechanical execution rule

`analysis/validate_flower_colour_rate_fit_preconditions.py` allows empirical rate fitting only when both are true:

1. all atlas breadth/state gates pass, including W>=5;
2. an empirical machine-readable branch-length tree route passes the tree contract.

Current blockers remain exactly:

```text
atlas_minimum_white_tips
branch_length_tree_unavailable
```

Recovery of the original Compositae1061 reference does **not** remove either of those final blockers. It removes only an upstream compatibility-reanalysis input blocker.

## What `execution_allowed=true` would mean

It would mean only that an empirical ER/ARD/Mk analysis may start. It would not mean that ARD is favoured, C->W is faster, the Arenicola MRCA is coloured/white, `C. irumtiense` represents regain, or anthocyanin was molecularly reactivated. Those claims still require model comparison, topology/branch-length uncertainty, sampling-bias sensitivity, explicit polymorphism treatment, model adequacy, population ancestry and floral molecular evidence.
