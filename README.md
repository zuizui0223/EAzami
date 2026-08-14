# EAzami — East Asian *Cirsium* flower-colour evolution

EAzami tests the evolutionary history of repeated floral anthocyanin loss and possible re-expression in East Asian *Cirsium*, while building the public nuclear phylogenetic framework needed to distinguish loss, regain, ancestral variation and reticulation.

## Start here

The current operational state is:

**[`docs/CURRENT_STATE_2026-08-14.md`](docs/CURRENT_STATE_2026-08-14.md)**

That document is the source of truth for accepted conclusions, current sample counts, public augmentation gates, active code paths and remaining blockers. Older implementation states should not be inferred from historical filenames alone.

## Current scientific state

### Flower-colour history

- Repeated white-flower evolution is the current general interpretation across East Asian *Cirsium*.
- The Arenicola context favours white-flower loss on the *C. brevicaule* lineage; current evidence does **not** establish regain in coloured *C. irumtiense*.
- Taiwanese *C. japonicum* var. *takaoense* is a **topology-supported candidate regain**: the directly documented W/BP sample states and displayed topology require a W-to-coloured transition under the current coloured-root minimum-change model.
- This is not molecular proof of anthocyanin-pathway loss and restoration. Introgression, ancestral standing variation, geographic structure and reticulation remain alternatives.

### Public nuclear backbone

The accepted primary public-data panel is:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

The old 302-tip / 303-SRR inventory is obsolete because eight Taiwan RNA-seq BioSamples/SRRs reused across Chang 2025 and Chang 2026 had been double-counted.

Japan-38 membership is provenance/sensitivity metadata, not a topology constraint.

## Ready public augmentation gates

Three extra public samples are ready for paired-tree testing but are **not yet promoted**.

| Candidate | Source | Strict loci | Role |
|---|---|---:|---|
| EA01 / `PUBEA001` | *C. nipponicum* var. *yoshinoi* public SRA | 236/241 | same-taxon replicate |
| EA02 / `PUBEA002` | *C. sairamense* public SRA | 239/241 | cross-study same-taxon replicate |
| CNIPG / `AUG_ULLEUNG_CNIP2024` | natural-Ulleung *C. nipponicum* public genome | 180/241 | cross-data-type natural-island replicate |

All three analysis taxon labels already occur in the 294-tip baseline. Therefore, even if all independent gates pass, the current candidate ceiling is **297 sample tips but 0 new analysis taxon labels**.

The accepted primary remains 294 until the required paired concatenated/ASTRAL sensitivities pass. A combined 297-tip state is not accepted without an explicit common paired-locus analysis.

## Promotion rule

For the SRA candidates, BWA and BLASTx are evaluated separately and symmetrically. Within a mapping mode, baseline and augmented scenarios use exactly the same paired locus set.

Automatic promotion requires:

1. RF = 0 on the shared 294-tip concatenated backbone;
2. an existing same-taxon baseline tip among the candidate's nearest baseline neighbours;
3. RF = 0 on the shared-species ASTRAL backbone.

Any failure means manual biological review. Thresholds are not relaxed post hoc.

CNIPG uses the same logic as a separate cross-data-type sensitivity against both accepted baseline mapping modes.

## Durable baseline reconstruction

The 294-tip rebuild no longer depends on the expiring Moreyra Actions artifact.

The exact compact reconciliation input used by the current builder is frozen under:

- `data/evidence/moreyra2025_cirsium_reconciliation_v1/`
- `analysis/materialize_frozen_moreyra_reconciliation.py`

It contains 258 linked *Cirsium* reconciliation rows, preserves the known source-conflict exclusion, and carries source/artifact/per-shard checksums. The canonical reconstructed CSV SHA256 is:

`cf3af71a1a77eee5bd177cef9cf8106b749b949eaacc0ad82bbb331978084505`

The current panel-v2, HPC-v2, EA01/EA02 and CNIPG validation paths rebuild the 294/295 baseline from this repository evidence.

## Main execution paths

### 294-tip baseline

- `analysis/build_japan_origin_global_public_panel_v2.py`
- `analysis/build_japan_origin_global_hpc_bundle_v2.py`
- `analysis/japan_origin_global_hpc_primitives.py`
- `.github/workflows/build-japan-origin-global-public-panel-v2.yml`
- `.github/workflows/validate-japan-origin-global-hpc-bundle-v2.yml`

### EA01 / EA02

- `analysis/build_east_asia_public_full_hpc_handoff.py`
- `analysis/prepare_east_asia_public_augmentation_tree_inputs.py`
- `analysis/evaluate_east_asia_public_augmentation_tree_pair.py`
- `analysis/summarize_east_asia_public_augmentation_sensitivities.py`
- `.github/workflows/validate-east-asia-public-augmentation-gate.yml`
- [`docs/EAST_ASIA_PUBLIC_TREE_AUGMENTATION_GATE_2026-08-13.md`](docs/EAST_ASIA_PUBLIC_TREE_AUGMENTATION_GATE_2026-08-13.md)

### Natural-Ulleung genome sensitivity

- `analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py`
- `analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py`
- `analysis/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py`
- `.github/workflows/validate-cirsium-nipponicum-public-genome-gate.yml`
- [`docs/CIRSIUM_NIPPONICUM_PUBLIC_GENOME_AUGMENTATION_GATE_2026-08-13.md`](docs/CIRSIUM_NIPPONICUM_PUBLIC_GENOME_AUGMENTATION_GATE_2026-08-13.md)

## Focused var. *takaoense* work

The six published var. *takaoense* transcriptomes form a separate focused hypothesis/provenance workstream. Direct Figure 1 morph evidence is frozen and validated without repeatedly downloading publisher content.

Read2Tree and the restartable transcriptome/gene-tree workflow remain live sensitivity paths. They are secondary to the maximum public nuclear backbone and should not be treated as substitutes for population-aware ancestry or functional anthocyanin evidence.

## Reference and locus-space boundary

The current compatibility target is the pinned original public Compositae1061 HybPiper reference:

- 1,061 loci;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

The Moreyra-specific *C. tioganum* augmentation has not been recovered. Therefore current raw-read analyses are compatibility reanalyses, not exact reproduction of Moreyra preprocessing.

The useful public locus sets are 1,061 / reproducible 531-candidate / conservative 241.

## What is deliberately not frozen yet

**A new broad China sampling list is not frozen.**

The current priority is to exhaust the public-data nuclear tree first. New mainland sampling should target only branches that remain transition-critical after the public backbone and augmentation sensitivities are complete.

## Repository layout

- `analysis/` — live deterministic analysis/build/evaluation code
- `data/evidence/` — frozen evidence, contracts, checksums and compact provenance
- `docs/` — scientific claim boundaries and execution notes
- `sampling/` — proposed/frozen sampling and reference sets
- `workflow/` — larger workflow/HPC orchestration support
- `tests/` — tests for live code
- `.github/workflows/` — CI evidence/contract validation and lightweight bundle construction

Historical prototypes that have been removed from the working tree remain recoverable from Git history.
