# Deferred heavy analyses

Status: 2026-08-17

EAzami no longer treats heavy reconstruction as a default preliminary-analysis requirement.

The scientific outputs, contracts, analysis scripts and frozen evidence remain in the repository. The active GitHub Actions surface is reduced so that pull requests validate **current hypothesis decisions**, not repeatedly reacquire raw public data or rebuild large computational plans.

## Deferred from routine PR CI

The following former GitHub Actions lanes are removed from the active workflow directory in this cleanup. Their prior implementations remain recoverable from Git history.

### Chang 2026 / public RNA and gene-tree reconstruction

- `build-chang2026-gene-tree-panel.yml`
- `plan-chang2026-gene-tree-resources.yml`
- `validate-chang2026-restartable-pilot.yml`
- `pilot-takaoense-targeted-sra-vdb.yml`
- `screen-takaoense-six-dfr-ans-sra-vdb.yml`

Reason: the relevant preliminary conclusions are already frozen. Additional SRA retrieval, VDB searching, transcriptome planning or broad gene-tree reconstruction is not required to choose the next biological samples.

### Public nuclear / HPC reconstruction

- `validate-maximum-public-nuclear-handoff.yml`
- `validate-maximum-public-combined-handoff.yml`
- `validate-japan-origin-global-hpc-bundle-v2.yml`
- `validate-colour-rate-comp1061-hpc-bundle.yml`
- `validate-chang2026-read2tree-hpc-bundle.yml`
- `build-east-asia-public-sra-comp1061-pilot.yml`
- `build-cirsium-nipponicum-comp1061-locus-pack.yml`

Reason: these are execution/handoff lanes, not current preliminary hypothesis tests. The actual heavy work remains available under `workflow/`, `analysis/`, frozen contracts, and Git history. It should be run only when a branch-scaled or candidate-admission result becomes decision-critical.

### Superseded hypothesis-program validation

- `validate-micro-to-macro-hypothesis-program.yml`
- `validate-micro-to-macro-hypothesis-program-v2.yml`

Reason: v1 and v2 are provenance history. The current lightweight v3 synthesis plus the new canonical preliminary-hypothesis registry supersede them for active CI.

### Repeated pathway-candidate retrieval

- `retrieve-cnipponicum-flavonoid-sequence-candidates.yml`

Reason: the candidate-homology summary is already frozen. Re-downloading the proteome and re-running BLAST does not resolve floral regulation or causation. The next decisive data are matched coding haplotypes, floral RNA, pigment and phenotype.

## Still active as lightweight preliminary CI

Examples of analyses that remain appropriate for pull-request validation:

- Japanese-origin evidence/meta summaries;
- pre-tree trait disparity;
- pre-tree environmental disparity;
- total and module-specific trait×environment coupling;
- Japan-38 authority module combinations;
- cytotype×trait descriptive overlap;
- image-authority orientation sensitivity;
- HMM2 population-aware colour transition sensitivity;
- HMM3 focal cytotype synthesis;
- the current micro-to-macro v3 frozen synthesis;
- the canonical preliminary-hypothesis registry.

These checks use committed evidence or small deterministic calculations and directly correspond to a live hypothesis decision.

## Reopening a heavy lane

A deferred heavy analysis is reopened only when all three are written down first:

1. hypothesis ID from `data/evidence/preliminary_hypothesis_registry_v1.csv`;
2. the decision that the heavy result will change;
3. why the same decision cannot be made from the frozen evidence or a smaller biological sample.

If those conditions are absent, the heavy analysis remains deferred.
