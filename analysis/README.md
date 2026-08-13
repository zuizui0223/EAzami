# Analysis contracts and frozen results

`analysis/` contains reproducible builders, auditors, validators and small derived outputs used by project decisions.

## Script roles

- `recover_*`: acquire or reconstruct public artifacts while retaining source lineage.
- `build_*` and `prepare_*`: create deterministic panels, manifests or workflow bundles.
- `audit_*` and `reconcile_*`: expose identity, metadata, repository and naming conflicts.
- `validate_*`: fail closed on schema drift, missing evidence or unmet decision gates.
- `run_*`: execute a defined analysis from versioned inputs.
- `summarize_*`, `score_*` and `analyze_*`: produce reviewable decision outputs without changing source evidence.

## Output policy

Small CSV and JSON outputs may be committed beside their generating script when all of the following hold:

1. the generating command and inputs are recoverable;
2. a current document or test uses the output;
3. source identifiers and uncertainty are retained;
4. regeneration does not require committing restricted or oversized source material.

Generated output is not deleted merely because no Python import points to it. Scientific references, workflow artifacts and decision documents must also be checked. Large intermediates stay in versioned workflow artifacts and are represented here by manifests, hashes and summaries.
