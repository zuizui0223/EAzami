# Japan-origin topology decision contract — 2026-08-13

## Why this layer exists

The maximal public-data panel now contains 302 biological samples / 303 public runs from Moreyra 2025, Chang 2025 and Chang 2026. That is enough to place the published Japanese radiation, the two published separate Japanese invasion anchors (`C. dipsacolepis`, `C. lineare`), and the 3 + 3 public Ryukyu Arenicola samples into one Compositae1061-compatible reconstruction.

The heavy tree has **not** yet been executed. This document defines what will be extracted from it once the accepted tree exists.

## Questions extracted from the accepted tree

1. Does the Moreyra Japan-38 main-radiation membership (Japan-38 minus `C. dipsacolepis` and `C. lineare`) remain monophyletic in the cross-assay public reconstruction?
2. Are `C. brevicaule` and `C. irumtiense` each monophyletic, and is Arenicola as a whole monophyletic?
3. Is Arenicola:
   - nested inside the published main-radiation MRCA,
   - an immediate/exclusive sister of the main radiation,
   - or topologically separate from it?
4. Which already-public taxa occupy the immediate neighbourhoods of:
   - Arenicola,
   - the main Japanese radiation,
   - `C. dipsacolepis`, and
   - `C. lineare`?

## What is deliberately not inferred

A single concatenated topology is not allowed to establish:

- dispersal direction;
- number or timing of colonisation events;
- direct ancestry;
- introgression;
- a final China sampling panel.

`analysis/analyze_japan_origin_global_tree.py` therefore always leaves `new_china_sampling_freeze_allowed=false` after a single-tree analysis.

## Sampling-decision gate

A topological sister-neighbourhood can enter the **candidate** continental sampling shortlist after the accepted global public tree is analysed. A final new China/Korea/Russian sampling panel is frozen only after:

1. BWA-primary and BLASTx mapping-sensitivity topologies are compared;
2. concatenated and per-locus/coalescent topology sensitivity is checked;
3. any name-conflicted tips in the relevant sister neighbourhood are reviewed;
4. only stable public-data gaps are converted into new collection targets.

This makes the public-data reconstruction the screening step and new field sampling the gap-filling step, rather than sampling China broadly before the source neighbourhood is known.
