# Deferred heavy analyses

Status: 2026-08-17

EAzami no longer treats heavy reconstruction as a default preliminary-analysis requirement. Scientific outputs, contracts, analysis scripts and frozen evidence remain in the repository; routine pull requests validate current hypothesis decisions rather than repeatedly reacquiring public data or rebuilding computational products.

## Removed from routine PR CI

### Chang 2026 / public RNA and gene-tree reconstruction

- `build-chang2026-gene-tree-panel.yml`
- `plan-chang2026-gene-tree-resources.yml`
- `validate-chang2026-restartable-pilot.yml`
- `pilot-takaoense-targeted-sra-vdb.yml`
- `screen-takaoense-six-dfr-ans-sra-vdb.yml`

The relevant preliminary conclusions are frozen. Additional SRA retrieval, VDB searching, transcriptome planning or broad gene-tree reconstruction is not needed to select the next biological samples.

### Public nuclear / HPC reconstruction

- `validate-maximum-public-nuclear-handoff.yml`
- `validate-maximum-public-combined-handoff.yml`
- `validate-japan-origin-global-hpc-bundle-v2.yml`
- `validate-colour-rate-comp1061-hpc-bundle.yml`
- `validate-chang2026-read2tree-hpc-bundle.yml`
- `build-east-asia-public-sra-comp1061-pilot.yml`
- `build-cirsium-nipponicum-comp1061-locus-pack.yml`

These are execution/handoff lanes, not current preliminary hypothesis tests. The Slurm/HPC code remains under `workflow/` and `analysis/` and can be restored/run only when branch-scaled or candidate-admission results become decision-critical.

### Superseded hypothesis-program validation

- `validate-micro-to-macro-hypothesis-program.yml`
- `validate-micro-to-macro-hypothesis-program-v2.yml`

v1/v2 are provenance history. The current v3 synthesis plus `data/evidence/preliminary_hypothesis_registry_v1.csv` is the active source of truth.

### Repeated molecular candidate reconstruction

- `retrieve-cnipponicum-flavonoid-sequence-candidates.yml`
- `validate-cnipponicum-flavonoid-family-discrimination.yml`

The homology/family-discrimination results are already frozen. Re-downloading C. nipponicum and Arabidopsis proteomes and rerunning BLAST/MAFFT/IQ-TREE does not resolve floral regulation or causation. The next decisive data are matched ancestry, coding haplotypes, floral RNA, pigment and phenotype.

## Still appropriate for lightweight PR CI

Active preliminary CI should be restricted to committed evidence or small deterministic calculations, including:

- Japanese-origin evidence/meta summaries;
- pre-tree trait and environmental disparity;
- total and module-specific trait×environment coupling;
- Japan-38 authority/cytotype/trait joins;
- HMM2 population-aware colour sensitivity;
- HMM3 focal cytotype synthesis;
- current micro-to-macro v3 synthesis;
- the canonical preliminary-hypothesis registry.

## Reopening a heavy lane

A deferred heavy analysis is reopened only after documenting:

1. a hypothesis ID from `data/evidence/preliminary_hypothesis_registry_v1.csv`;
2. the sampling or claim decision the result will change;
3. why frozen evidence or a smaller biological sample cannot make that decision.

Without those three items, the heavy analysis remains deferred. Historical workflow implementations remain recoverable from Git history.
