# GitHub Actions policy

EAzami pull-request CI is intentionally **lightweight and hypothesis-oriented**.

## Default PR rule

A workflow belongs in routine PR CI only when it:

- operates on committed/frozen evidence or small local fixtures;
- finishes with a deterministic scientific or contract assertion;
- maps to a live hypothesis in `data/evidence/preliminary_hypothesis_registry_v1.csv`;
- can change a current sampling, claim-boundary, or validity decision.

Typical active checks are small meta-analysis reproductions, evidence-ledger validation, taxon/cytotype/trait joins, and claim-boundary assertions.

## Not routine PR CI

Do not use normal pull requests to repeatedly perform:

- SRA or large remote-data downloads;
- VDB/BLAST screens whose result is already frozen;
- transcriptome assembly;
- HybPiper across large panels;
- IQ-TREE/ASTRAL/Read2Tree/large orthology reconstruction;
- HPC bundle reconstruction after the execution contract is already validated;
- broad exploratory resource planning that does not change the next sampling decision.

These lanes are deferred. See `docs/DEFERRED_HEAVY_ANALYSES.md`.

## Preliminary-analysis contract

Before adding a new preliminary workflow, record:

1. `hypothesis_id`;
2. `decision_if_positive`;
3. `decision_if_negative`;
4. `new_data_if_unresolved`;
5. a stop rule.

If the analysis cannot fill those fields, it should not become a routine workflow.

## Versioned synthesis rule

Only the current synthesis should remain active in PR CI. Older v1/v2 synthesis workflows are provenance history and belong in Git history or manual recovery, not as parallel required checks.

Current source of truth:

- `docs/PRELIMINARY_ANALYSIS_HYPOTHESIS_MAP.md`
- `data/evidence/preliminary_hypothesis_registry_v1.csv`
- `PROJECT_STATUS.md`

Historical workflow implementations are recoverable from Git history; deleting an active workflow file does not delete its scientific evidence or analysis code.
