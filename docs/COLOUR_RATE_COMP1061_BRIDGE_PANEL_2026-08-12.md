# Cross-study Compositae1061 bridge for the flower-colour rate tree

Date: 2026-08-12

## Why a bridge is necessary

Flower-colour atlas v0.3 has 20 fixed-state eligible taxa, but they do not come from one sequencing study:

- 13 taxa are represented by Chang leaf RNA-seq;
- 7 taxa are represented by Moreyra target-capture data.

A Moreyra-only reanalysis would therefore not contain the full atlas state set. The recovered original Compositae1061 HybPiper reference provides a common 1,061-locus coordinate system that can be used to project both data sources into one explicitly labelled compatibility analysis.

This is a bridge design, not an assumption that RNA-seq and target-capture have identical missing-data properties.

## Primary 20-tip rule

The primary analysis uses one predeclared public run per fixed-state taxon. Sample selection is frozen **before** HybPiper/locus-recovery results are seen:

1. taxon/run identity must be source-backed and verified against official SRA metadata;
2. among multiple eligible source-backed runs for one taxon, select the run with the largest official `Spots` value;
3. ties use voucher/sample-code/run lexical order;
4. flower colour and inferred topology are not sample-selection inputs.

The larger-run rule is intended to favour locus recovery rather than minimize compute. All other eligible runs remain in a replicate-sensitivity manifest.

Expected primary composition:

- 20 taxa;
- C=17, W=3;
- 13 leaf-RNA-seq tips;
- 7 target-capture tips;
- Chang 2026 = 7;
- Chang 2025 = 6;
- Moreyra 2025 = 7.

Polymorphic var. `takaoense`, `C. pendulum`, `C. sieboldii`, `C. aomorense` and `C. amplexifolium` are not forced into the fixed-state primary tree.

## Run recovery

The CI does not hard-code Chang SRR values for the bridge.

- Chang 2026 plus inherited Chang 2025 samples are re-reconciled with `recover_chang2026_published_runinfo.py` and `reconcile_chang2026_complete_runs.py`; geography and flower colour are not used for run matching.
- `PRJNA1158676` is independently recovered to obtain the three additional Chang 2025 taxa (`C. suffultum`, `C. nipponicum var. incomptum`, `C. kujuense`).
- `PRJNA957074` is independently recovered and its run metadata are joined back to the frozen Moreyra voucher/sample audit for the seven target-capture taxa.

## Shared reference

The panel is pinned to:

- `data/evidence/comp1061_original_reference_contract_v1.json`
- 1,061 loci;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

This is the original public Compositae1061 HybPiper reference. It is **not** the unrecovered Moreyra-specific reference augmented with `Cirsium tioganum` exons.

## Required downstream sensitivities

A branch-length compatibility tree should not be accepted from one concatenated matrix without diagnostics. The execution stage must report at least:

1. all 1,061 public reference loci;
2. the reproducible 531 warning/occupancy candidate set where locus names can be joined;
3. the conservative 241 no-warning high-occupancy set where locus names can be joined;
4. replicate-inclusive or alternative-sample sensitivity for taxa with multiple public runs;
5. occupancy/missingness by `target_capture` versus `leaf_rnaseq`;
6. paralog/copy-conflict diagnostics;
7. concatenated ML topology with substitution-per-site branch lengths;
8. gene-tree/coalescent topology sensitivity separately from the branch-length tree used for discrete-trait Mk models.

## Interpretation boundary

Using the same reference coordinates does not make the two library types equivalent. Leaf RNA-seq can miss low/unexpressed loci, while target capture has assay-specific enrichment and dropout. Differential occupancy must therefore be quantified before treating cross-study branch lengths as biologically comparable.

The bridge panel itself does **not** remove the project blockers:

```text
atlas_minimum_white_tips
branch_length_tree_unavailable
```

It only makes the second blocker executable from public data. Empirical transition-rate fitting remains disabled until the tree is actually inferred/validated and the fixed-white gate is also cleared.
