# EAzami — East Asian *Cirsium* flower-colour evolution

EAzami tests repeated floral anthocyanin loss and possible re-expression in East Asian *Cirsium*, while building the public nuclear framework needed to distinguish loss, regain, ancestral variation and reticulation.

## Start here

The operational source of truth is:

**[`docs/CURRENT_STATE_2026-08-14.md`](docs/CURRENT_STATE_2026-08-14.md)**

Do not infer current sample counts or supported execution paths from older versioned filenames alone.

## Current scientific state

### Flower-colour history

- Repeated white-flower evolution remains the general interpretation across East Asian *Cirsium*.
- Arenicola currently favours white loss on the *C. brevicaule* lineage; current evidence does **not** establish regain in coloured *C. irumtiense*.
- Taiwanese *C. japonicum* var. *takaoense* remains a **topology-supported candidate regain**, not molecular proof of anthocyanin-pathway loss/restoration. Introgression, standing variation and reticulation remain alternatives.

### Accepted public nuclear backbone

The accepted primary remains:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

The old 302/303 inventory is obsolete because eight public Taiwan RNA-seq samples had been double-counted across Chang 2025/2026.

## Real-read candidate audit — 2026-08-14

A real public-SRA/HybPiper/MAFFT/IQ-TREE pilot was run before launching the full 294-tip augmentation analysis.

Four tips were compared:

- accepted baseline *C. nipponicum* var. *yoshinoi* + EA01 / `PUBEA001`;
- accepted baseline *C. sairamense* + EA02 / `PUBEA002`.

The exact four-way intersection contained **235 strict loci**; **231** were gene-tree informative. The concatenated alignment contained **105,086 nt**, 2,769 variable sites and 2,199 parsimony-informative sites.

All **231/231** informative ML gene trees supported the same-taxon split, and the concatenated tree supported it with **SH-aLRT/UFBoot 100/100**.

The crucial provenance result is asymmetric:

- **EA01 is an independent public library** and remains a valid full-tree candidate.
- **EA02 is overwhelmingly consistent with the same underlying raw read library already present in the 294-tip baseline**: identical raw before-filtering read/base/Q20/Q30/GC statistics, identical R1/R2 before-filtering profiles, identical duplication and insert-size profiles, identical 239-locus strict set, and effectively zero terminal distance in the empirical ML tree.

EA02 is therefore frozen as `duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance`. Its data remain useful as a duplicate-control, but it no longer counts as an independent biological tip.

Evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`
- `data/evidence/east_asia_public_candidate_disposition_v2.json`

## Revised public candidate ceiling

Current defensible independent candidates beyond the accepted 294 are:

| Candidate | Source | Strict loci | Current role |
|---|---|---:|---|
| EA01 / `PUBEA001` | *C. nipponicum* var. *yoshinoi* public SRA | 236/241 | independent same-taxon candidate |
| CNIPG / `AUG_ULLEUNG_CNIP2024` | natural-Ulleung *C. nipponicum* public genome | 180/241 | independent cross-data-type candidate |
| EA02 / `PUBEA002` | *C. sairamense* public SRA | 239/241 | duplicate-control only; not a biological tip |

If EA01 and CNIPG both pass their full independent gates, the current public ceiling is therefore **296 biological tips / 0 new analysis taxon labels**.

That is still not an accepted combined 296-tip tree. A common paired-locus combined analysis is required before replacing the accepted 294-tip primary.

## Full promotion rules still required

For EA01, BWA and BLASTx must each pass:

1. shared-294 concatenated RF = 0;
2. same-taxon baseline placement among nearest neighbours;
3. shared-species ASTRAL RF = 0.

CNIPG uses the same safeguards in its separate cross-data-type comparison against both accepted baseline mapping modes.

The real four-tip pilot validates the candidate identities/placement signal; it does **not** authorize full-tree promotion.

## Execution status

The old top-level 297-tip orchestration is now a **reproducibility-only pre-empirical state**. `workflow/public_nuclear_maximum/prepare_and_submit.sh` can reconstruct it with `PREPARE_ONLY=1`, but real Slurm submission is fail-closed because EA02 is no longer an independent candidate.

The next heavy-compute task is to build/run the post-empirical **EA01 + CNIPG** maximum-public handoff against the 294-tip baseline.

## Reference boundary

The active compatibility target remains the pinned public Compositae1061 reference:

- 1,061 loci;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

The Moreyra-specific *C. tioganum* augmented target remains unrecovered, so current raw-read runs are compatibility reanalyses rather than exact Moreyra preprocessing reproduction.

## What is deliberately not frozen

**A new broad China sampling list is still not frozen.**

Public-data nuclear inference is exhausted first; new mainland sampling should target only branch-specific gaps that remain important after the revised 294→296 public analysis.

## Repository layout

- `analysis/` — live deterministic analysis/build/evaluation code
- `data/evidence/` — frozen evidence, contracts and checksums
- `docs/` — claim boundaries and current-state notes
- `sampling/` — sampling/reference sets
- `workflow/` — HPC/orchestration entry points
- `tests/` — tests for live code
- `.github/workflows/` — lightweight CI and empirical public-data pilots

Historical implementations and superseded planning states remain recoverable from Git history.
