# East Asia public-SRA nuclear-tree augmentation gate — 2026-08-13

## Status update — 2026-08-14

The original v1 gate treated EA01 and EA02 as two potentially independent biological replicates beyond the accepted 294-tip baseline. A real-read empirical audit on 2026-08-14 supersedes that **biological independence assumption for EA02** while retaining the original pack and v1 contract as provenance.

Current evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`
- `data/evidence/east_asia_public_candidate_disposition_v2.json`

Current accepted primary remains **294 biological tips / 295 unique public SRRs / 270 analysis taxon labels**.

## Original public-SRA pilot

Run `31684233834` recovered:

- EA01 / `PUBEA001` — *Cirsium nipponicum* var. *yoshinoi*: **236/241** strict no-warning BWA loci;
- EA02 / `PUBEA002` — *Cirsium sairamense*: **239/241** strict no-warning BWA loci;
- EA03–EA05: 0/241, not carried forward.

The original v1 four-scenario design was:

1. `baseline294`;
2. `ea01_295`;
3. `ea02_295`;
4. `ea01_ea02_296`.

Within each mapping mode the scenarios use one exact paired locus set. BWA and BLASTx remain separate mapping sensitivities, and no post-hoc locus/RF relaxation is allowed.

## Real-read baseline audit

Before committing HPC resources to the full 294-tip augmentation run, the exact same-taxon samples already present in the accepted baseline were re-recovered from public SRA using the pinned Compositae1061 / HybPiper 2.3.4 BWA path:

- `MRY_YOSHINOI` — *C. nipponicum* var. *yoshinoi*, `SRR30887222`: **236/241** strict loci;
- `MRY_SAIRAMENSE` — *C. sairamense*, `SRR25265647`: **239/241** strict loci.

Both had zero strict paralog-warning loci.

The two baseline packs and the frozen EA01/EA02 packs yielded:

- **235** four-way common strict loci;
- **231** gene-tree-informative loci;
- **105,086 nt** concatenated alignment;
- **2,769** variable sites;
- **2,199** parsimony-informative sites.

All **231/231** per-locus ML trees supported:

`(MRY_YOSHINOI, PUBEA001) | (MRY_SAIRAMENSE, PUBEA002)`

The concatenated IQ-TREE topology agreed, with **SH-aLRT/UFBoot = 100/100** and BIC-selected model `TIM3+F+G4`.

This establishes strong expected same-taxon placement in the empirical four-tip sanity check. It is not a full 294-tip promotion test.

## EA01 — independent candidate retained

EA01 and the baseline *C. nipponicum* var. *yoshinoi* sample are clearly different public libraries. Their before-filtering read counts, total bases, Q20/Q30 counts and GC differ substantially.

EA01 therefore remains an independent same-taxon candidate and must still pass the full BWA/BLASTx gate:

1. shared-294 concatenated RF = 0;
2. existing same-taxon baseline tip among nearest neighbours;
3. shared-species ASTRAL RF = 0;
4. agreement across both mapping modes.

The original joint EA01+EA02 scenario may still be retained as a duplicate-control regression sensitivity, but it does not create a 296-tip biological state.

## EA02 — duplicate-control, not an independent tip

EA02 and the accepted baseline *C. sairamense* sample show multiple independent signatures of the same underlying public read data:

- identical before-filtering total reads: **10,779,802**;
- identical before-filtering total bases: **1,088,760,002**;
- identical Q20/Q30 raw counts and rates;
- identical read lengths and GC;
- identical complete R1 and R2 before-filtering quality/base-content objects;
- identical duplication profile;
- identical insert-size profile;
- identical **239/241** strict-locus set;
- effectively zero terminal separation in the empirical concatenated ML tree.

Together these are overwhelmingly consistent with reuse/re-deposition of the same underlying raw read library. This does **not** assert the same physical herbarium specimen without explicit source provenance.

Current disposition:

`duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance`

EA02 may be retained as a pipeline duplicate-control. Its topology checks are diagnostic only and **must not increment the biological-tip count**. `analysis/summarize_east_asia_public_augmentation_sensitivities.py` now enforces this disposition.

## Revised current boundary

For the same-assay SRA workstream:

- accepted primary: 294;
- EA01: independent candidate;
- EA02: duplicate-control only;
- maximum biological tip count from this workstream if EA01 passes: **295**;
- new analysis taxon labels: **0**.

Across all current public sources, CNIPG remains the second defensible independent candidate. Therefore the broader public sample-level ceiling is now **296**, not 297, if EA01 and CNIPG both pass their full independent gates.

A 296-tip state is not accepted by arithmetic. It requires an explicit common paired-locus combined analysis after independent admission.

## Execution safety

The historical EA01/EA02 v1 builders and packs are retained because they are needed to reproduce the empirical audit and can serve as duplicate-control regression tests.

However, the pre-empirical top-level 297-tip Slurm graph is no longer a supported heavy-execution route. `workflow/public_nuclear_maximum/prepare_and_submit.sh` now allows prepare-only reproduction but blocks real submission until a post-empirical EA01+CNIPG handoff is used.

## Claim boundary

The real-read quartet changes candidate provenance/accounting, not the flower-colour evolutionary conclusion. It does not test the whole 294-tip backbone, does not replace the BWA/BLASTx + ASTRAL gates, and does not authorize EA01 or CNIPG promotion.

New broad China sampling remains deliberately unfrozen until the revised public-only 294→296 ceiling is resolved.
