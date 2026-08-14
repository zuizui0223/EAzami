# EAzami — East Asian *Cirsium* flower-colour evolution

EAzami tests repeated floral anthocyanin loss and possible re-expression in East Asian *Cirsium*, while building the public nuclear framework needed to distinguish loss, regain, ancestral variation and reticulation.

## Start here

Operational source of truth:

**[`docs/CURRENT_STATE_2026-08-14.md`](docs/CURRENT_STATE_2026-08-14.md)**

Do not infer current sample counts or supported execution paths from older versioned filenames alone.

## Current scientific state

### Flower-colour history

- Repeated white-flower evolution remains the general interpretation across East Asian *Cirsium*.
- Arenicola currently favours white loss on the *C. brevicaule* lineage; current evidence does **not** establish regain in coloured *C. irumtiense*.
- Taiwanese *C. japonicum* var. *takaoense* remains a **topology-supported candidate regain**, not molecular proof of anthocyanin-pathway loss/restoration. Introgression, standing variation and reticulation remain live alternatives.

### Accepted public nuclear backbone

The accepted primary remains:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

The old 302/303 inventory is obsolete because eight public Taiwan RNA-seq samples had been double-counted across Chang 2025/2026.

## Real-read candidate audit — 2026-08-14

A real public-SRA → fastp → HybPiper 2.3.4/BWA → MAFFT → IQ-TREE audit compared the accepted same-taxon baseline samples to EA01 and EA02.

- four-way common strict loci: **235**;
- informative gene-tree loci: **231**;
- concatenated alignment: **105,086 nt**;
- variable sites: **2,769**;
- parsimony-informative sites: **2,199**;
- same-taxon topology: **231/231 gene trees**;
- concatenated support: **SH-aLRT/UFBoot 100/100** (`TIM3+F+G4`).

The provenance result is asymmetric:

- **EA01 / `PUBEA001` is an independent public library** and remains a full-tree candidate.
- **EA02 / `PUBEA002` is overwhelmingly consistent with re-deposition/reuse of the same raw read library already represented by the baseline *C. sairamense***. It is frozen as `duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance` and may be retained only as a duplicate-control.

Evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`
- `data/evidence/east_asia_public_candidate_disposition_v2.json`

## Current public candidate ceiling

| Candidate | Source | Strict loci | Current role |
|---|---|---:|---|
| EA01 / `PUBEA001` | *C. nipponicum* var. *yoshinoi* public SRA | 236/241 | independent same-taxon candidate |
| CNIPG / `AUG_ULLEUNG_CNIP2024` | natural-Ulleung *C. nipponicum* public genome | 180/241 | independent cross-data-type candidate |
| EA02 / `PUBEA002` | *C. sairamense* public SRA | 239/241 | duplicate-control only; not a biological tip |

If EA01 and CNIPG both pass their independent gates, the maximum public ceiling is **296 biological tips / 0 new analysis taxon labels**. This is not an accepted combined 296-tip tree; an explicit common paired-locus combined analysis is still required.

## Current maximum-public execution path

The post-empirical 296-ceiling execution graph is implemented and CI-validated.

Main entry point:

```bash
export REPO_ROOT=/path/to/EAzami
bash workflow/public_nuclear_maximum/prepare_and_submit.sh
```

Use `PREPARE_ONLY=1` to build and validate the handoff without Slurm submission.

The generated v2 graph:

1. reconstructs the accepted 294-tip / 295-SRR baseline;
2. downloads the baseline SRRs once and runs BWA and BLASTx branches;
3. runs **EA01 only** under the same-assay two-scenario gate (`baseline294`, `ea01_295`), including fresh EA01 BLASTx recovery;
4. runs CNIPG independently against both accepted baseline mapping modes;
5. emits `maximum_public_nuclear_independent_gate_summary_v2`;
6. if EA01 and CNIPG both pass, requires a fresh common-locus `ea01_cnipg_296` combined tree before any 296-tip acceptance.

EA02 is not downloaded by the current augmentation handoff and never enters biological tree inputs.

Validation workflow `Validate maximum public nuclear HPC handoff` passed on run `31794226173`; the generated handoff artifact was `9216698035`, SHA256 `f63ccb87c652b0b4bc8ec02f6486f40295e7e4f623a1dbb38155d5319b788fd4`.

### Promotion gates

EA01 must pass independently in BWA and BLASTx:

1. shared-294 concatenated RF = 0;
2. same-taxon baseline tip among nearest neighbours;
3. shared-species ASTRAL RF = 0.

CNIPG uses the equivalent safeguards in its separate cross-data-type gate against both accepted baseline mapping modes. Any failure means manual biological review; thresholds are not relaxed after seeing results.

## Reference boundary

The active compatibility target remains the pinned public Compositae1061 reference:

- **1,061 loci**;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

The Moreyra-specific *C. tioganum* augmented target remains unrecovered, so current raw-read runs are compatibility reanalyses rather than exact Moreyra preprocessing reproduction.

## What is deliberately not frozen

**A new broad China sampling list is still not frozen.** Public-data nuclear inference is exhausted first; new mainland sampling should target only branch-specific gaps that remain important after the revised 294→296 public analysis.

## Repository layout

- `analysis/` — live deterministic analysis/build/evaluation code
- `data/evidence/` — frozen evidence, contracts and checksums
- `docs/` — claim boundaries and current-state notes
- `sampling/` — sampling/reference sets
- `workflow/` — HPC/orchestration entry points
- `tests/` — tests for live code
- `.github/workflows/` — lightweight CI/validation

Historical implementations and superseded planning states remain recoverable from Git history.
