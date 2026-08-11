# Chang 2026 Read2Tree marker-profile comparison

Date: 2026-08-11

## Purpose

The first assembly-free var. *takaoense* topology screen now has two deliberately different May-2026 OMA marker profiles:

1. `oma_static_broadconservation400_may2026_v1`
2. `oma_browser_export400_may2026_v1`

The point is not to choose whichever marker set gives the preferred colour-history result. The profiles are used to measure how sensitive the Read2Tree topology is to reference-marker selection.

## Two independent comparisons

### A. Marker-set overlap

`analysis/compare_read2tree_oma_marker_packs.py`

Marker filenames are not compared, because the static profile uses deterministic synthetic marker names while the Browser export uses OMA group names.

Instead, each marker is identified by the exact sorted triplet of OMA IDs:

```text
CYNCS protein | DAUCS protein | HELAN protein
```

The comparator validates:

- May-2026 contracts;
- CYNCS/HELAN/DAUCS reference codes;
- 400 AA markers per pack;
- exactly one sequence from each reference per marker;
- no repeated OMA sequence ID across markers within a pack;
- unique marker signatures.

Outputs:

- exact marker-group intersection and union;
- marker-group Jaccard;
- overlap fraction relative to each 400-marker pack;
- individual OMA reference-sequence intersection/union/Jaccard;
- exact per-marker presence table.

Overlap classes are descriptive:

- `identical_marker_sets`: 400/400 exact group matches;
- `high_overlap`: at least 75%;
- `moderate_overlap`: at least 25%;
- `low_overlap`: below 25%.

High overlap means the two topology screens are not strongly independent in marker identity. Low overlap does not make either topology correct; it only makes agreement across profiles more informative about marker-selection sensitivity.

### B. Topology-decision concordance

`analysis/compare_chang2026_read2tree_profiles.py`

The two score tables are aligned at support thresholds:

```text
0 / 50 / 70 / 90
```

Each profile is normalized to one of:

- `candidate_regain`
- `loss_only`
- `unresolved`
- `not_scored`

`not_scored` includes failures of the focal-monophyly gate and is never converted to support for either colour-history class.

## Decision rules

### Direct conflict

One profile prefers `candidate_regain` and the other `loss_only` at the same support threshold.

Overall result:

`marker_profile_conflict`

Action: do not select either history. Audit marker overlap, mapping completeness and per-marker support, then continue to the de-novo gene-tree/network analysis.

### One profile decisive

One profile is decisive but the other is unresolved or not scored.

Overall result:

`marker_profile_partial_disagreement`

This is not marker-profile concordance.

### Concordant candidate regain

Both profiles prefer candidate regain at all decisive thresholds.

If all four support thresholds agree:

`concordant_candidate_regain_across_thresholds`

If high-support collapse makes both unresolved at some thresholds:

`support_sensitive_concordant_candidate_regain`

This strengthens the displayed topology as a target for de-novo gene-tree testing, but does not demonstrate evolutionary or molecular regain.

### Concordant loss-only

The equivalent loss-only states are:

- `concordant_loss_only_across_thresholds`
- `support_sensitive_concordant_loss_only`

This substantially weakens the displayed-tree regain hypothesis.

### Direction changes with support threshold

If both marker profiles agree with each other at each threshold, but the preferred decisive class changes from candidate regain to loss-only after support collapse:

`support_threshold_direction_change`

This is treated as topology-support instability rather than marker-profile concordance.

### Non-decisive

If neither marker profile provides a shared decisive history:

`concordant_nondecisive`

Continue to the de-novo gene-tree/network workflow without a regain/loss call.

## One-command comparison

After both profiles have normalized marker contracts and topology score CSVs:

```bash
STATIC_ROOT=/path/to/static400 \
BROWSER_ROOT=/path/to/browser400 \
bash workflow/chang2026_read2tree/compare_marker_profiles.sh
```

The command writes:

- `marker_group_overlap.csv`
- `marker_group_overlap_summary.json`
- `topology_profile_comparison.csv`
- `topology_profile_comparison_summary.json`

## Interpretation hierarchy

The fast-screen evidence hierarchy is now:

```text
one Read2Tree marker profile
    < two marker profiles with unknown/very high overlap
    < two materially different marker profiles with topology concordance
    < de-novo per-gene concordance / quartet support
    < population/network evidence excluding introgression and standing variation
    < molecular pigment-pathway restoration evidence
```

Thus even perfect marker-profile concordance is only an intermediate topology result.
