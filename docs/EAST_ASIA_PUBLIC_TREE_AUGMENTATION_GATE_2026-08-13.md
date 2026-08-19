# East Asia public-SRA nuclear-tree augmentation gate — 2026-08-13

## Status — superseded biologically on 2026-08-14

This document records the historical EA01/EA02 v1 design and the empirical audit that superseded its assumption that both candidates were independent biological replicates.

The **current biological same-assay gate is EA01-only** and is defined by:

- `data/evidence/ea01_public_tree_augmentation_contract_v2.json`;
- `analysis/prepare_ea01_public_augmentation_tree_inputs.py`;
- `analysis/summarize_ea01_public_augmentation_sensitivities.py`;
- `analysis/build_ea01_public_augmentation_hpc_bundle.py`;
- `analysis/build_ea01_public_full_hpc_handoff.py`.

The current top-level maximum-public execution graph is documented in `docs/CURRENT_STATE_2026-08-14.md`.

## Original public-SRA pilot

Run `31684233834` recovered:

- EA01 / `PUBEA001` — *Cirsium nipponicum* var. *yoshinoi*: **236/241** strict no-warning BWA loci;
- EA02 / `PUBEA002` — *Cirsium sairamense*: **239/241** strict no-warning BWA loci;
- EA03–EA05: **0/241**, not carried forward.

The original v1 design compared `baseline294`, `ea01_295`, `ea02_295` and `ea01_ea02_296` on an identical joint locus set within each mapping mode. The v1 code and durable packs remain useful for provenance and duplicate-control regression, but they no longer define the biological-tip promotion graph.

## Real-read empirical audit

Frozen evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`;
- `data/evidence/east_asia_public_candidate_disposition_v2.json`.

The exact same-taxon baseline samples were re-downloaded and rerun through the pinned Compositae1061/HybPiper 2.3.4 BWA path:

- `MRY_YOSHINOI`, `SRR30887222`: **236/241** strict loci;
- `MRY_SAIRAMENSE`, `SRR25265647`: **239/241** strict loci.

The baseline pairs plus EA01/EA02 yielded:

- **235** four-way common strict loci;
- **231** informative gene-tree loci;
- **105,086 nt** concatenated alignment;
- **2,769** variable sites;
- **2,199** parsimony-informative sites.

All **231/231** informative ML gene trees supported

`(MRY_YOSHINOI, PUBEA001) | (MRY_SAIRAMENSE, PUBEA002)`

and the concatenated tree agreed with **SH-aLRT/UFBoot = 100/100**, model `TIM3+F+G4`.

## EA01 — independent candidate retained

EA01 and the baseline *C. nipponicum* var. *yoshinoi* sample are clearly different public libraries. EA01 remains an independent same-taxon candidate.

The current EA01 v2 gate has only two biological scenarios:

1. `baseline294`;
2. `ea01_295`.

Within BWA and BLASTx separately, both scenarios must use one identical paired locus set. Automatic promotion requires:

1. at least 100 paired loci;
2. shared-294 concatenated RF = 0;
3. the existing same-taxon baseline tip among nearest neighbours;
4. shared-species ASTRAL RF = 0;
5. agreement across BWA and BLASTx without post-hoc threshold relaxation.

The frozen BWA EA01 pack is used for the BWA branch; EA01 is freshly recovered from `SRR30887223` under BLASTx for the BLASTx branch.

## EA02 — duplicate-control only

EA02 and the accepted baseline *C. sairamense* sample have:

- identical before-filtering **10,779,802 reads** and **1,088,760,002 bases**;
- identical Q20/Q30 raw counts and rates;
- identical read lengths and GC;
- identical complete R1/R2 before-filtering quality/base-content profiles;
- identical duplication and insert-size profiles;
- identical **239/241** strict-locus sets;
- effectively zero terminal separation in the empirical concatenated tree.

These signatures are overwhelmingly consistent with reuse/re-deposition of the same underlying raw read library. They do **not** alone prove identity of the physical herbarium specimen.

Current disposition:

`duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance`

EA02 is retained as frozen evidence and may be used as a pipeline duplicate-control, but it **cannot increment biological-tip count**. The current EA01 v2 handoff does not download EA02 and cannot place `PUBEA002` into biological tree inputs.

## Current boundary

- accepted primary: **294 biological tips / 295 SRRs / 270 labels**;
- EA01: independent same-assay candidate;
- EA02: duplicate-control only;
- CNIPG: independent cross-data-type candidate;
- current maximum-public candidate ceiling if EA01 and CNIPG both pass: **296 tips / 0 new labels**.

The live top-level v2 handoff is implemented in `analysis/build_maximum_public_nuclear_hpc_handoff.py` and submitted through `workflow/public_nuclear_maximum/prepare_and_submit.sh`.

GitHub Actions run `31794226173` validated the 296-ceiling graph, explicit EA02 exclusion, current unit tests, the prepare-only wrapper and the final EA01+CNIPG collector. Validation artifact `9216698035` has SHA256 `f63ccb87c652b0b4bc8ec02f6486f40295e7e4f623a1dbb38155d5319b788fd4`.

This validates the execution graph, not the still-unrun full 294-tip heavy analysis. The accepted primary remains 294 until the full gates complete.

New broad China sampling remains deliberately unfrozen until the public-only 294→296 ceiling is empirically resolved.
