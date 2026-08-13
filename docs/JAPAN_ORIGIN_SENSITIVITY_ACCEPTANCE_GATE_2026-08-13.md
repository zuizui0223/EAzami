# Japan-origin four-scenario sensitivity acceptance gate

## Resolution target

Classify whether the published main Japanese *Cirsium* radiation and all currently sampled Japanese lineages are monophyletic across the predeclared mapping and tree-method sensitivities. Report Ryukyu Arenicola and the *C. dipsacolepis* / *C. lineare* anchors separately.

This is a monophyly gate, not a one-colonisation test. Even unanimous monophyly cannot by itself establish colonisation count, direction, timing, direct ancestry or absence of introgression.

## Authoritative inventory

The executable v2 panel contains:

- 294 deduplicated biological individuals;
- 295 unique public SRRs;
- 256 Moreyra target-capture individuals;
- 38 unique Chang RNA-seq individuals after collapsing eight cross-paper reused BioSamples;
- three *C. brevicaule* and three *C. irumtiense* public individuals.

The historical 302-tip / 303-run v1 inventory is superseded and is not an admissible sensitivity input.

## Required scenarios

| Scenario | Mapping | Tree unit |
|---|---|---|
| `bwa_concat` | BWA | 294 individual tips, concatenated IQ-TREE |
| `bwa_astral` | BWA | source-label tips retaining 294 constituent individuals, ASTRAL-III |
| `blastx_concat` | BLASTx | 294 individual tips, concatenated IQ-TREE |
| `blastx_astral` | BLASTx | source-label tips retaining 294 constituent individuals, ASTRAL-III |

ASTRAL serialization is treated as unrooted. Interpretation re-roots the tree on the edge separating the declared reference tips; failure to recover that reference clade is fatal.

## Fail-closed rules

`analysis/integrate_japan_origin_topology_sensitivities.py` rejects the run when:

- any required scenario is missing or duplicated;
- a scenario is not SHA-bound to an accepted tree artifact;
- the v2 constituent-individual count is not 294;
- the tree unit does not match the scenario;
- candidate rows do not match their interpretation summary;
- an upstream single-tree result already claims dispersal, ancestry, introgression or sampling freeze.

Biological disagreement does not cause a software error. It produces `unresolved_sensitivity_conflict` and keeps sampling frozen.

## Stable-neighbour rule

A public sister candidate is stable only when the same focal group, `immediate_sibling_branch`, taxon and region occur in all four scenarios. Source-study and tip provenance are retained but may differ between individual and source-label trees.

Candidates with `name_review_required=true` remain blocked unless the optional review ledger records `confirmed_source_label` with an exact evidence locator. `excluded_from_sampling` retains the audit row but never promotes it.

## Outputs

- `sensitivity_acceptance.json`: scenario hashes, monophyly classifications, Arenicola consensus, anchor relationships and blockers.
- `stable_sister_candidates.csv`: four-scenario intersection with name-review and promotion states.

`new_china_sampling_freeze_allowed=true` appears only when both monophyly questions are sensitivity-stable, Arenicola and both exception anchors are stable, every focal group has a stable sister neighbourhood and all relevant name reviews are resolved.

## Execution wiring

The v2 HPC bundle now produces individual and ASTRAL interpretation outputs for both mapping modes. After both mode-specific tree chains finish:

```bash
sbatch 10_integrate_sensitivity_gate_slurm.sh
```

Set `NAME_REVIEW=/path/to/review.csv` when a reviewed ledger is needed. The schema contracts are:

- `data/schema/japan_origin_topology_sensitivity_scenarios.csv`
- `data/schema/japan_origin_name_review.csv`
