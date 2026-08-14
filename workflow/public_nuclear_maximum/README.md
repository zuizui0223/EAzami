# Maximum public nuclear HPC entry point

This directory is the supported top-level entry point for issue #18 after the repository cleanup.

It does not replace the scientific component bundles. It composes the accepted 294-tip baseline, EA01/EA02 same-assay gates and CNIPG cross-data-type gate into one artifact-free execution handoff while preserving every predeclared promotion rule.

## Prepare only

From the repository checkout:

```bash
PREPARE_ONLY=1 bash workflow/public_nuclear_maximum/prepare_and_submit.sh /path/to/maximum_public_nuclear_handoff
```

This reconstructs the 294-tip baseline inputs and all three candidate locus packs from repository evidence, builds both component handoffs, validates generated shell syntax and checks the frozen inventory. No heavy SRA/tree computation is run.

## Prepare and submit on Slurm

```bash
export REPO_ROOT=/path/to/EAzami
bash workflow/public_nuclear_maximum/prepare_and_submit.sh /scratch/.../maximum_public_nuclear_handoff
```

The top-level orchestrator then:

1. submits the shared 295-SRR baseline recovery once;
2. runs baseline BWA and BLASTx branches;
3. runs EA01/EA02 same-assay paired-tree sensitivities;
4. starts each CNIPG mode only after the corresponding baseline tree acceptance job;
5. aggregates EA01/EA02 cross-mapping and CNIPG cross-data-type results;
6. writes `independent_gate_summary.json`.

The final collector can report independent candidate gate passage, but it always keeps `combined_296_or_297_tree_accepted=false`. If all three candidates pass, its next action is to build an explicit common paired-locus combined tree.

The candidate ceiling of 297 tips is therefore a planning ceiling, not an accepted tree. New broad China sampling also remains outside this execution entry point.
