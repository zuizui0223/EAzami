# Documentation map

This index mirrors the project knowledge-graph backbone and separates current decision documents from evidence records, request drafts and historical snapshots.

## Current authority

Read these first, in order:

1. [Current resolution goal](../PROJECT_STATUS.md) — the active decision gate and acceptance criteria.
2. [Research plan](RESEARCH_PLAN.md) — durable scientific aims and claim limits.
3. [East Asia phylogenomics implementation plan](EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md) — the two-layer data design.
4. [Japan-origin topology decision contract](JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md) — permitted inferences from the accepted tree.
5. [Sequencing panel v0.3](SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.md) — current exact-coverage sampling decisions.

## Graph-aligned workstreams

| Workstream | Current entry point | Decision it supports |
|---|---|---|
| Evidence gates and phylogeny | [Evidence map v0.3](CIRSIUM_PHYLOGENY_EVIDENCE_MAP_RELEASE_V0_3.md) | Which sources and public artifacts are safe to use |
| Anthocyanin regain candidate | [Exact var. *takaoense* topology and uncertainty](CHANG_2026_TAKAOENSE_EXACT_TOPOLOGY_AND_UNCERTAINTY_2026-08-11.md) | Candidate regain versus historical alternatives |
| Japan origin topology | [Decision contract](JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md) and [four-scenario gate](JAPAN_ORIGIN_SENSITIVITY_ACCEPTANCE_GATE_2026-08-13.md) | Monophyly classification and stable continental gaps |
| RAD-seq priority | [Phylogeny-gap and RAD-seq plan](PHYLOGENY_GAP_AND_RADSEQ_PLAN.md) | Species placement versus population-history sequencing |
| Flower-colour evidence | [Flower-colour atlas v0.1](CIRSIUM_FLOWER_COLOUR_ATLAS_V0_1.md) | Population-aware colour states and transition candidates |
| Capitulum traits | [Capitulum trait foundation](CAPITULUM_TRAIT_FOUNDATION.md) | Future trait mapping without premature adaptation claims |

## Retention boundaries

- `archive/` contains superseded or dated snapshots retained for provenance. They are not current authority.
- `requests/` contains correspondence and data-request drafts. A request is not evidence that data were received.
- Source-backed tables remain under `data/evidence/`; contracts remain under `data/schema/`.
- Small, reviewable derived results may remain beside their generating scripts under `analysis/` when they are cited by a current decision document.
- Large or licensed source artifacts belong in versioned workflow artifacts, with checksums and recovery logs committed here.

Date-stamped documents can remain current when they are the latest evidence record for a workstream. Date alone is never a deletion rule.
