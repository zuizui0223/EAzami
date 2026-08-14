# EAzami current resolution goal

Status date: 2026-08-14

## Goal

Produce an accepted, sensitivity-tested common-locus nuclear backbone before freezing any broad new China sampling list. The immediate decision is whether the public-data tree preserves the main Japanese radiation and the separate histories of *C. dipsacolepis*, *C. lineare* and Ryukyu Arenicola while remaining stable to mapping, tree-method and replicate sensitivities.

## Accepted baseline

The current accepted public-data inventory is:

- **294 unique biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

The old 302/303 inventory is superseded because eight Taiwan RNA-seq BioSamples/SRRs reused across Chang 2025 and Chang 2026 had been double-counted.

The accepted primary remains 294 tips until explicit promotion gates pass.

## Ready public candidates

Three additional public samples are ready for paired-tree testing:

| Candidate | Source | Strict loci | New analysis label? |
|---|---|---:|---|
| EA01 / `PUBEA001` | *C. nipponicum* var. *yoshinoi* public SRA | 236/241 | no |
| EA02 / `PUBEA002` | *C. sairamense* public SRA | 239/241 | no |
| CNIPG / `AUG_ULLEUNG_CNIP2024` | natural-Ulleung *C. nipponicum* public genome | 180/241 | no |

If all independent gates pass, the current sample-level candidate ceiling is **297 tips**, but that is not an accepted combined tree until an explicit common paired-locus analysis is run across all admitted candidates.

## Promotion logic

For each candidate gate, augmented and baseline trees must be compared on the exact same paired locus set. Automatic promotion requires:

1. RF = 0 on the shared 294-tip concatenated backbone;
2. an existing same-taxon baseline tip among the candidate's nearest baseline neighbours;
3. RF = 0 on the shared-species ASTRAL backbone.

EA01/EA02 must satisfy this in both BWA and BLASTx mapping modes and in relevant single/joint scenarios. CNIPG is evaluated separately as a cross-data-type sensitivity against both accepted baseline mapping modes.

A failed criterion triggers manual biological review, not post-hoc threshold relaxation.

## Current claim ceiling

- Repeated white-flower evolution is the best-supported general pattern in the current East Asian evidence.
- Arenicola currently favours white loss on *C. brevicaule*; regain in *C. irumtiense* is not established.
- var. *takaoense* is a topology-supported candidate regain under the directly documented W/BP sample states and displayed topology.
- Molecular anthocyanin re-expression is not demonstrated until population history, introgression/standing variation, pathway state, expression, pigment and genotype are linked.
- A single concatenated tree cannot establish dispersal direction, colonisation count or timing, direct ancestry, or introgression.

## Durable public-first infrastructure

The 294-tip baseline no longer depends on the expiring Moreyra Actions reconciliation artifact. The exact 258-row *Cirsium* reconciliation subset used by the v2 builder is frozen under `data/evidence/moreyra2025_cirsium_reconciliation_v1/` with source and per-shard checksums and is materialized by `analysis/materialize_frozen_moreyra_reconciliation.py`.

The flower-colour Compositae1061 bridge also now has one supported canonical entry point with the corrected empirical source partition Chang2025=3, Chang2026=10, Moreyra2025=7; the old monkey-patch wrapper has been retired.

## Remaining empirical gates

1. Run the validated 294-tip baseline BWA and BLASTx workflows.
2. Run fresh EA01/EA02 BLASTx recovery and paired concatenated/ASTRAL sensitivities.
3. Run CNIPG paired 294-vs-295 sensitivities in both baseline mapping modes.
4. If independent candidates pass, run one explicit combined common-locus tree before promoting a 296/297 state.
5. Only then rank unresolved mainland gaps by information gain and freeze the smallest informative new sampling set.

Until these conditions pass, `new_china_sampling_freeze_allowed` remains false.

## Two-layer research backbone

| Layer | Question | Data | Decision |
|---|---|---|---|
| 1. Common-locus species backbone | Which Japanese and East Asian lineages are stably placed? | Public reads, public genome resources and Compositae1061-compatible recovery | Species placement and genuine backbone gaps |
| 2. Population and morph history | Are apparent loss/regain histories caused by ancestry, gene flow, standing variation or transition? | RAD-seq/resequencing plus linked vouchers, colour, pigment and ploidy | Focal population sampling and molecular tests |

Layer 2 does not substitute for missing species placement, and Layer 1 does not resolve local ancestry by itself.

## Navigation

- Operational source of truth: [docs/CURRENT_STATE_2026-08-14.md](docs/CURRENT_STATE_2026-08-14.md)
- Documentation/workstream map: [docs/README.md](docs/README.md)
- Phylogenomics implementation: [docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md](docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md)
- Japan-origin decision contract: [docs/JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md](docs/JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md)
- Current sampling decisions: [docs/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.md](docs/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.md)
- Capitulum-trait foundation: [docs/CAPITULUM_TRAIT_FOUNDATION.md](docs/CAPITULUM_TRAIT_FOUNDATION.md)
