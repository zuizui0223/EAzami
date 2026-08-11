# Read2Tree output scoring against the eight pre-registered takaoense histories

Date: 2026-08-11

## Purpose

The Read2Tree fast screen should not be interpreted by visually comparing a tree figure with Chang et al. (2026). The output is instead scored mechanically against the same eight rooted six-tip hypotheses already frozen for the de novo gene-tree workflow:

- `H_REG_PUBLISHED`: the displayed nested-BP candidate-regain topology;
- `H_LOSS_ONLY_RF4_01`–`07`: all nearest rooted loss-only alternatives at RF distance four.

The scorer is:

- `analysis/score_chang2026_read2tree_topology.py`
- `tests/test_score_chang2026_read2tree_topology.py`

## Three-stage gate

### 1. Leaf and reference contract

The Read2Tree tree must contain every frozen W/BP sample exactly once. Non-focal leaves must belong to the frozen OMA reference manifest. Unknown or duplicated focal leaves stop the analysis.

### 2. Root and focal monophyly

The tree is rerooted on the source-declared OMA outgroup, currently `DAUCS` (*Daucus carota* subsp. *sativus*).

Before reference taxa are removed, the six var. *takaoense* samples must form an exact clade relative to all OMA reference taxa. If a reference taxon is nested among the six focal samples, the result is reported as `focal_not_monophyletic_raw_tree` and none of the eight within-takaoense histories is scored.

This rule prevents a poor reference-guided tree from being made to look supportive simply by deleting the conflicting reference leaves.

### 3. Support-threshold gate and hypothesis ranking

At support thresholds 0, 50, 70 and 90, low-support internal branches are collapsed. The six focal samples must still be monophyletic after collapse. If the focal stem becomes unresolved, the threshold is reported as `focal_monophyly_unresolved_at_threshold`.

Only retained focal clades are relabelled to the exact hypothesis labels and scored.

The ranking is identical to the per-gene topology scorer:

1. fewest supported focal clusters conflicting with the hypothesis;
2. smallest rooted Robinson–Foulds distance;
3. greatest number of hypothesis clusters recovered.

An unresolved six-tip star therefore ties all hypotheses rather than generating evidence for either regain or loss-only histories.

## Outputs

For every support threshold the scorer reports:

- whether focal monophyly is present;
- number of supported focal clusters;
- best hypothesis ID(s) and history class(es);
- `published_best`, `loss_only_best`, `tie_published_loss_only`, or `unresolved_all_hypotheses_tie`;
- conflict and rooted-RF scores for `H_REG_PUBLISHED`;
- best loss-only conflict and RF scores;
- exact hypothesis match when present.

A separate table retains the score for all eight hypotheses.

## Example

```bash
python analysis/score_chang2026_read2tree_topology.py \
  --tree /work/read2tree_output/takaoense6_read2tree_dna.treefile \
  --panel /work/chang2026_takaoense6_assembly_pilot.csv \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_1.csv \
  --outgroup DAUCS \
  --output /work/read2tree_score/read2tree_topology_score.csv \
  --hypothesis-output /work/read2tree_score/read2tree_hypothesis_scores.csv \
  --summary-json /work/read2tree_score/read2tree_topology_score.json
```

## Interpretation

### Strongest existing-data outcome

If the six focal samples remain monophyletic and `H_REG_PUBLISHED` is best at high support thresholds, the displayed candidate-regain ordering has independent raw-read/reference-guided support.

### Loss-only outcome

If a nearest loss-only topology is best, the published displayed tree is not a sufficient basis for a regain narrative. The full per-gene and reticulation analyses become mandatory before evolutionary direction is discussed.

### Focal-monophyly failure

If the focal six are not monophyletic relative to OMA references, this is first treated as a reference/marker/RNA-coverage or tree-quality warning. The reference taxa are not silently pruned to force a six-tip result.

## Claim boundary

Even an exact, strongly supported match to `H_REG_PUBLISHED` is **not** evidence by itself for molecular anthocyanin reactivation. A concatenated reference-guided tree does not distinguish introgression from incomplete lineage sorting or ancestral polymorphism, and the input libraries are leaf RNA rather than floral RNA.

The output is therefore an **independent topology sensitivity result** only.
