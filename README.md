# EAzami — East Asian *Cirsium* evolutionary reconstruction

EAzami is the phylogenetic and mechanistic-resolution layer that follows the global public-image macro screen in `zuizui0223/azami`. It tests repeated floral anthocyanin loss and possible re-expression, reconstructs Japanese and East Asian nuclear history, and provides the species-tree framework needed to move from global trait patterns to explicit transition histories and focal population mechanisms.

## Start here

Operational source of truth:

**[`docs/CURRENT_STATE_2026-08-14.md`](docs/CURRENT_STATE_2026-08-14.md)**

Cross-project research program:

**[`docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md`](docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md)**

Machine-readable stage / stop-rule contract:

**[`data/evidence/azami_eazami_macro_to_micro_contract_v1.json`](data/evidence/azami_eazami_macro_to_micro_contract_v1.json)**

Do not infer current sample counts or supported execution paths from older versioned filenames alone.

## Cross-project role

The program is intentionally staged:

```text
azami / Chapter 1
Global public-image macro screen
        ↓ hypothesis generation
EAzami
East Asian nuclear history + trait-transition reconstruction
        ↓ replicated focal transitions
population / mechanism studies
Ancestry + gene flow + floral expression + pigment + interaction + fitness
```

Chapter 1 is not reopened to force a resolved phylogeny, ancestral-state reconstruction or causal adaptation claim into the global image analysis. EAzami receives those hypotheses and tests them on an accepted nuclear-tree / topology ensemble. New capitulum traits such as phyllary angle, spine architecture and stickiness belong to a next-generation comparative layer rather than to the frozen Chapter 1 analysis unless they are needed to repair a validity problem.

## Current scientific state

### Flower-colour history

- Repeated white-flower evolution remains the general interpretation across East Asian *Cirsium*.
- Arenicola currently favours white loss on the *C. brevicaule* lineage; current evidence does **not** establish regain in coloured *C. irumtiense*.
- Taiwanese *C. japonicum* var. *takaoense* remains a **topology-supported candidate regain**, not molecular proof of anthocyanin-pathway loss/restoration. Introgression, standing variation and reticulation remain live alternatives.
- The next historical layer is not restricted to colour: after the accepted nuclear tree is available, colour, orientation and continuous head-shape traits from the Azami macro screen are to be projected onto the same supported topology ensemble.

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

Latest validation on the current 296-tip contract:

- `Validate maximum public nuclear HPC handoff` run `31937355788` — success; artifact `9261030108`, digest `sha256:d8c4c3ff219a56f87e1deb411c02684b0d843e38096c3d144d78e1bc902a5d68`;
- `Validate maximum public combined-tree handoff` run `31937355816` — success; artifact `9261031804`, digest `sha256:e353612e5db39ac0416a1b3292074f0e58355dbfedfb6dee835eb7938d5f42ea`.

These CI runs validate the execution graph and fail-closed contracts. They do not claim that the heavy 294-tip BWA/BLASTx + IQ-TREE + ASTRAL analyses themselves have run.

### Promotion gates

EA01 must pass independently in BWA and BLASTx:

1. shared-294 concatenated RF = 0;
2. same-taxon baseline tip among nearest neighbours;
3. shared-species ASTRAL RF = 0.

CNIPG uses the equivalent safeguards in its separate cross-data-type gate against both accepted baseline mapping modes. Any failure means manual biological review; thresholds are not relaxed after seeing results.

## Immediate scientific work after the accepted nuclear tree

1. freeze the supported topology ensemble and taxon crosswalk for Japan-38, *C. lineare*, *C. dipsacolepis*, Arenicola and continental neighbours;
2. build an Azami→EAzami trait-tip bridge retaining observation/state uncertainty and explicit polymorphism;
3. reconstruct flower-colour transitions first;
4. reconstruct orientation on the same nuclear framework;
5. add continuous head-shape history without treating image variance as evolutionary variance;
6. test whether trait modules evolve independently or repeatedly form correlated ecological combinations;
7. promote only replicated/high-information transitions to population genomics, floral expression, pigment, interaction and fitness experiments.

## Reference boundary

The active compatibility target remains the pinned public Compositae1061 reference:

- **1,061 loci**;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

The Moreyra-specific *C. tioganum* augmented target remains unrecovered, so current raw-read runs are compatibility reanalyses rather than exact Moreyra preprocessing reproduction.

## What is deliberately not frozen

**A new broad China sampling list is still not frozen.** Public-data nuclear inference is exhausted first; new mainland sampling should target only branch-specific gaps that remain important after the revised 294→296 public analysis.

Likewise, a new global phyllary/spine/stickiness classifier is **not** part of the Chapter 1 submission path. Those traits first require a defensible ontology, assessability rules and separation of literature-level taxon knowledge from image-level observations.

## Repository layout

- `analysis/` — live deterministic analysis/build/evaluation code
- `data/evidence/` — frozen evidence, contracts and checksums
- `docs/` — claim boundaries, program roadmap and current-state notes
- `sampling/` — sampling/reference sets
- `workflow/` — HPC/orchestration entry points
- `tests/` — tests for live code
- `.github/workflows/` — lightweight CI/validation

Historical implementations and superseded planning states remain recoverable from Git history.
