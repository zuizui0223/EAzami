# EAzami current resolution goal

Status date: 2026-08-13

## Goal

Produce an accepted, sensitivity-tested common-locus nuclear backbone that decides whether the main Japanese *Cirsium* radiation is recovered as monophyletic while retaining the separate histories of *C. dipsacolepis*, *C. lineare* and Ryukyu Arenicola. Freeze new RAD-seq or target-capture priorities only from topological gaps that remain stable across the accepted sensitivity analyses.

This is the next decision gate because flower-colour direction, the priority of continental bridge samples and future trait mapping all depend on a defensible phylogenetic backbone. A single concatenated tree is a screening result, not an accepted answer.

## Current claim ceiling

- Repeated white-flower evolution is the best-supported general pattern in the current East Asian evidence.
- var. *takaoense* is a topology-supported candidate regain under the displayed sample topology and coloured-root model.
- Anthocyanin re-expression is not demonstrated until population history, pathway state, expression, pigment and genotype are linked in the same plants.
- The public-data prior places 36 of 38 sampled Japanese taxa in a main rapid radiation and treats *C. dipsacolepis* and *C. lineare* as separate invasion histories. The cross-assay common-locus reconstruction needed to test that prior has not yet been accepted.
- One tree cannot establish dispersal direction, colonisation count or timing, direct ancestry, or introgression.

## Acceptance gate

The Japan-origin result becomes decision-grade only when all of the following are versioned and pass validation:

1. The maximal public panel manifest and sample-name reconciliation are complete and reproducible.
2. BWA-primary and BLASTx mapping-sensitivity results are compared.
3. Concatenated and per-locus/coalescent results are compared, with support and discordance retained.
4. The main Japanese radiation is classified as `supported_monophyletic`, `rejected`, or `unresolved`; Arenicola, *C. dipsacolepis* and *C. lineare* are reported separately.
5. Name-conflicted tips affecting the relevant sister neighbourhoods are reviewed.
6. Only gaps stable across those checks are promoted to new sampling targets.

Until all six conditions pass, `new_china_sampling_freeze_allowed` remains false.

## Execution order

1. Build and validate the common-locus public panel.
2. Run the primary mapping and accepted-tree workflow.
3. Run mapping and tree-method sensitivities.
4. Apply the Japan-origin topology decision contract.
5. Freeze the smallest informative Layer 1 and Layer 2 sampling updates.
6. Re-evaluate flower-colour transitions, then advance var. *takaoense* and the other population-level systems to mechanism tests.

## Two-layer research backbone

| Layer | Question | Data | Decision |
|---|---|---|---|
| 1. Common-locus species backbone | Which Japanese and East Asian lineages are stably placed? | Public reads and Compositae1061-compatible target capture | Species placement and genuine backbone gaps |
| 2. Population and morph history | Are apparent loss/regain histories caused by ancestry, gene flow, standing variation or transition? | RAD-seq/resequencing plus linked vouchers, colour, pigment and ploidy | Focal population sampling and molecular tests |

Layer 2 does not substitute for missing species placement, and Layer 1 does not resolve local ancestry by itself.

## Future capitulum-trait foundation

The same stable taxon, population, voucher and phylogeny-tip identifiers will support future tests of capitulum-trait adaptive radiation. The initial contract records orientation, size and supporting evidence without asserting repeated adaptation. See [the capitulum trait foundation](docs/CAPITULUM_TRAIT_FOUNDATION.md) and [its machine-readable schema](data/schema/capitulum_trait_records.csv).

## Canonical navigation

- Repository and workstream map: [docs/README.md](docs/README.md)
- Durable research aims: [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)
- Phylogenomics implementation: [docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md](docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md)
- Japan-origin decision contract: [docs/JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md](docs/JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md)
- Current sampling decisions: [docs/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.md](docs/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.md)
