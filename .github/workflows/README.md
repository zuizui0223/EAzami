# Workflow index and retention policy

The workflow set is intentionally evidence-lane oriented:

- `recover-*` and `enumerate-*`: public artifact acquisition and source discovery;
- `audit-*` and `reconcile-*`: metadata, identity and repository checks;
- `build-*`, `prepare-*` and `plan-*`: deterministic panels and HPC bundles;
- `validate-*`, `test-*` and `analyze-*`: schema, scientific-gate and result checks.

Do not merge workflows based only on similar names. Before retiring a workflow, confirm that its source artifact, output contract, retention period and decision consumer are all superseded. A successful job is not evidence completion unless its final artifact and reported identifiers were validated.
