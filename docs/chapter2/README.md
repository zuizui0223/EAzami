# Chapter 2 — from present phenotypic fields to admissible generative histories

## Status

This directory is the Chapter 2 source of truth for the current Azami → EAzami thesis line.

The dependency is one-way:

```text
Azami
reconstruct the present phenotypic field
        ↓
frozen empirical constraints
        ↓
EAzami
ask which generative-history classes remain admissible
        ↓
Japan38 / population genomics / functional experiments
constrain realized history and causal function
```

Azami and EAzami are **not parallel trait projects**. Azami defines the empirical object to be explained; EAzami receives that frozen object and rejects or retains generative-history classes.

## Core definition

- **Azami = phenotypic present**: a multivariate, hierarchical present-day capitulum field reconstructed from images and environmental context.
- **EAzami = constraints on admissible generative histories**: a fail-closed inverse problem over models capable or incapable of reproducing the frozen present.
- **Japan38 = realized-history evidence layer**: nuclear phylogenomic topology plus source-backed categorical trait states used to localize repeated historical changes. Repeated parsimony steps are not adaptive-convergence counts.
- **Next population layer = ancestry discrimination**: nuclear population-genomic DNA + same-individual/tightly matched plastid haplotype + cytotype/genome-size information to distinguish standing variation, introgression/gene flow and lineage-specific origin.

## Current frozen result chain

1. Azami hands off 62 observational estimands summarizing present-day structure and environment alignment.
2. In the preregistered 14-family prior-predictive screen, `NULL_COUPLED` is the robust scalar-target structural-sufficiency winner (PR #119).
3. The same winner fails the independently held-out scale-specific inferential-support geometry: primary pattern 0/64, exact 20-cell pattern 0/64 (PR #120).
4. A post-heldout diagnostic shows that among-taxon-only process structure is directionally closer, but no tested addition meets the preregistered adequacy rule; `PROCESS_AMONG_ONLY_SHARED_COUPLED` improves on NULL in 22/24 paired draws but has median 6/8 primary-cell matches, below the required 7/8 (PR #123).
5. Therefore the current conclusion is **not** that environment is absent. Scalar snapshot geometry alone does not identify environmental history, while the held-out hierarchical support geometry contains information absent from the snapshot-null generator.

## Manuscript files

- `MANUSCRIPT_V1.md` — answer-first full manuscript draft.
- `EVIDENCE_MAP_V1.md` — what is publishable, supporting, provisional or excluded.
- `FIGURE_TABLE_PLAN_V1.md` — figure/table architecture and exact source artifacts.
- `SUBMISSION_GATES_V1.md` — what must be finished before submission versus what belongs to later thesis chapters.
- `../../data/evidence/chapter2_claim_registry_v1.csv` — machine-readable claim boundary.

## Paper core versus thesis extension

**Paper core:** present phenotypic field → 62 frozen constraints → preregistered model discrimination → held-out falsification → post-heldout diagnostic.

**Thesis extension / bridge:** Japan38 repeated-history evidence, ancestry discrimination, functional manipulation and molecular mechanism. These layers motivate and constrain next observations but are not required to claim that the currently tested generative families are insufficient.

## Claims that remain prohibited

- `NULL_COUPLED` means climate has no biological effect.
- residual covariance coupling proves common evolutionary lability.
- repeated minimum-change steps prove adaptive convergence.
- image-derived modules are already validated functional modules.
- one true historical trajectory has been reconstructed.
- the post-heldout among-only diagnostic is confirmatory model selection.
- flower-colour loss/regain is the central Chapter 2 result; colour remains a secondary historical/mechanistic module under its existing stop rules.
