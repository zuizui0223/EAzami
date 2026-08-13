# Chang 2026 Read2Tree fast screen

This workflow is a lightweight, reference-guided topology sensitivity analysis for the six morph-labelled `C. japonicum var. takaoense` public RNA-seq samples.

## Required order

1. Export OMA markers from the **May 2026** OMA Browser release using exactly `CYNCS`, `HELAN`, and `DAUCS`, minimum species coverage `1.0`, maximum markers `400`.
2. Validate and normalize that archive with `analysis/validate_read2tree_oma_marker_pack.py`.
3. Require `execution_allowed: true` in the generated `marker_pack_contract.json`.
4. Build commands with `analysis/build_chang2026_read2tree_pilot.py`; this builder refuses an uncontracted marker directory.
5. Run Read2Tree using the environment pinned in `envs/read2tree.yml`.
6. Infer the concatenated nucleotide tree.
7. Score it through `analysis/run_chang2026_read2tree_scoring_contract.py`.

The final step first verifies that `analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv` still matches the current source-derived hypotheses and has exact SHA256:

```text
b3cf6ab230fba4e21dd06690580c49c0bfd759be2c1e30ac2fa576ff8e2b7082
```

Only after that gate does it invoke `analysis/score_chang2026_read2tree_topology.py`, and the scoring JSON is annotated with the frozen-input provenance and exact invocation.

## Scientific gates

The scoring script must retain all six focal tips exactly once and confirm that the six focal samples are monophyletic relative to the OMA references before reference pruning. If focal monophyly fails in the raw tree or after support collapse, the candidate-regain versus loss-only hypotheses are not scored.

The corrected frozen null set is the seven nearest rooted RF=4 no-regain alternatives derived from the current Figure 1 topology. The old stale T0064-series null set is superseded.

## Claim boundary

Read2Tree is an independent fast topology screen. It does not replace the 19-sample de novo Trinity/OrthoFinder gene-tree workflow, distinguish introgression from incomplete lineage sorting, or demonstrate floral anthocyanin reactivation.
