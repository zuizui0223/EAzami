# EAzami current state — 2026-08-14

This is the operational source of truth for the repository. It separates accepted scientific conclusions, empirical candidate disposition, current executable gates and remaining heavy-compute work. Historical implementations and superseded planning states remain recoverable from Git history and dated evidence.

## 1. Accepted scientific state

### Flower-colour history

Current evidence supports repeated white-flower evolution across East Asian *Cirsium* rather than one single white-flowered lineage.

- Arenicola: published context currently favours white-flower loss on the *C. brevicaule* lineage. Current evidence does **not** establish regain in coloured *C. irumtiense*.
- Taiwanese *C. japonicum* var. *takaoense*: directly morph-labelled W/BP samples plus the displayed topology make a W-to-coloured transition the current minimum-change interpretation under a coloured-root model. This remains a **topology-supported candidate regain**, not molecular proof of pathway loss and restoration.
- Introgression, ancestral coloured standing variation, geographic structure, short internodes and reticulation remain live alternatives.
- A demonstrated molecular regain still requires population-aware nuclear ancestry, explicit introgression/standing-variation tests and a genotype → expression → pigment → phenotype mechanism.

### Accepted public nuclear baseline

The accepted primary remains:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

Japan-38 membership is provenance/sensitivity metadata, not a topology constraint. The old 302-tip / 303-SRR inventory is obsolete because eight Taiwan RNA-seq BioSamples/SRRs reused across Chang 2025 and Chang 2026 had been double-counted.

No downstream result has yet superseded the accepted **294-tip** primary tree.

## 2. Real-read candidate audit

Frozen evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`
- `data/evidence/east_asia_public_candidate_disposition_v2.json`

Two exact same-taxon samples already inside the 294-tip baseline were re-downloaded from SRA and rerun through the pinned Compositae1061/HybPiper 2.3.4 BWA path:

- `MRY_YOSHINOI` — *C. nipponicum* var. *yoshinoi*, `SRR30887222`: **236/241** strict loci;
- `MRY_SAIRAMENSE` — *C. sairamense*, `SRR25265647`: **239/241** strict loci.

The four-tip comparison against EA01/EA02 used:

- **235** four-way common strict loci;
- **231** informative gene-tree loci;
- **105,086 nt** concatenated alignment;
- **2,769** variable sites;
- **2,199** parsimony-informative sites.

All **231/231** informative ML gene trees supported

`(MRY_YOSHINOI, PUBEA001) | (MRY_SAIRAMENSE, PUBEA002)`

and the concatenated IQ-TREE gave the same split with **SH-aLRT/UFBoot 100/100**, BIC-selected model `TIM3+F+G4`.

### EA01 disposition

EA01 / `PUBEA001` remains an independent candidate. Its raw library differs clearly from the baseline *yoshinoi* library and its empirical placement is consistently same-taxon.

**Current role:** independent same-taxon SRA candidate. The full 294-tip BWA/BLASTx concatenated-RF + same-taxon-neighbour + source-label-ASTRAL gate is still required.

### EA02 disposition

EA02 / `PUBEA002` and the accepted baseline *C. sairamense* sample share identical raw before-filtering read/base/Q20/Q30/read-length/GC summaries, identical full R1/R2 before-filtering profiles, identical duplication/insert-size profiles, identical 239-locus strict sets and effectively zero terminal separation.

This is overwhelmingly consistent with reuse/re-deposition of the same underlying raw read library. It does **not** by itself prove the same physical herbarium specimen.

**Current role:** `duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance`. EA02 is retained as frozen evidence/duplicate-control but cannot increment biological-tip count.

## 3. Current independent public candidates and ceiling

The defensible independent candidates beyond the accepted 294 are now only:

- EA01 / `PUBEA001`, *C. nipponicum* var. *yoshinoi*: **236/241** strict loci;
- CNIPG / `AUG_ULLEUNG_CNIP2024`, natural-Ulleung *C. nipponicum* genome-derived CDS: **180/241** strict loci, zero cross-locus subject collisions.

If both pass their independent gates, the current public sample-level ceiling is:

- **296 biological tips**;
- **0 new analysis taxon labels**.

This is **not** an accepted combined 296-tip tree. A common paired-locus combined analysis is still required after independent admission.

The old 297-tip ceiling is a superseded pre-empirical planning state.

## 4. Durable evidence

### Baseline

The 294-tip rebuild is artifact-independent:

- `data/evidence/moreyra2025_cirsium_reconciliation_v1/`
- `analysis/materialize_frozen_moreyra_reconciliation.py`

Canonical reconstructed Moreyra input SHA256:

`cf3af71a1a77eee5bd177cef9cf8106b749b949eaacc0ad82bbb331978084505`

### Candidate packs

Durable repository materialization remains available for:

- EA01: **236** strict FASTAs;
- EA02: **239** strict FASTAs, retained only as duplicate-control evidence;
- CNIPG: **180** strict FASTAs.

### Empirical quartet

- real-read recovery run: `31788828923`;
- final quartet ML run: `31792170949`;
- result artifact digest: `sha256:a8069ba48efd89d1e922b5ff5f2b71f1db763e1f1ae32622c5bd995a15031ccf`.

## 5. Current maximum-public execution path — implemented

The post-empirical maximum-public v2 graph is now implemented and validated.

Top-level entry point:

```bash
export REPO_ROOT=/path/to/EAzami
bash workflow/public_nuclear_maximum/prepare_and_submit.sh
```

`PREPARE_ONLY=1` builds/validates the handoff without Slurm submission.

### EA01 same-assay gate

Current files:

- `data/evidence/ea01_public_tree_augmentation_contract_v2.json`
- `analysis/prepare_ea01_public_augmentation_tree_inputs.py`
- `analysis/summarize_ea01_public_augmentation_sensitivities.py`
- `analysis/build_ea01_public_augmentation_hpc_bundle.py`
- `analysis/build_ea01_public_full_hpc_handoff.py`

The biological tree scenarios are now only:

- `baseline294`;
- `ea01_295`.

Within BWA and BLASTx separately, both scenarios use an identical paired locus list. EA01 gets a fresh BLASTx recovery from `SRR30887223`; the frozen successful BWA pack is used for BWA. **EA02 is not downloaded and never enters these tree inputs.**

EA01 automatic admission requires in both mapping modes:

1. at least 100 paired loci;
2. shared-294 concatenated RF = 0;
3. existing same-taxon baseline tip among nearest neighbours;
4. shared-species ASTRAL RF = 0.

Any failure triggers manual biological review without threshold relaxation.

### CNIPG cross-data-type gate

Current files:

- `analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py`
- `analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py`
- `analysis/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py`
- `data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json`

CNIPG is evaluated independently against both accepted baseline mapping modes with the same RF / same-taxon-neighbour / ASTRAL safeguards.

### Top-level v2 handoff

`analysis/build_maximum_public_nuclear_hpc_handoff.py` now builds:

- `ea01_handoff/` — EA01-only same-assay gate;
- `cnipg_bundle/` — CNIPG cross-data-type gate;
- `submit_all_independent_public_gates.sh` — shares the 295-SRR baseline BWA/BLASTx execution across both candidate gates;
- `90_collect_independent_gate_summaries_slurm.sh` — emits `maximum_public_nuclear_independent_gate_summary_v2`.

The final independent summary contains only `{EA01, CNIPG}` as candidate gates and records EA02 separately as an excluded duplicate-control. If both candidates pass, it reports a **296-tip candidate ceiling**, but keeps `combined_296_tree_accepted=false`.

### Post-admission combined-tree input gate

`analysis/prepare_maximum_public_combined_tree_inputs.py` is now v2 and can run only after EA01 and CNIPG both pass independently. It constructs one identical baseline∩EA01∩CNIPG locus set for exactly four scenarios:

- `baseline294`;
- `ea01_295`;
- `cnipg_295`;
- `ea01_cnipg_296`.

EA02 cannot enter the combined-tree builder.

## 6. Validation state

GitHub Actions run `31794226173` — **Validate maximum public nuclear HPC handoff** — passed completely at head `040816c2f5e2cc593c7f13de0d57ce615ed6b4be`.

Validated steps included:

- build current 296-ceiling handoff;
- updated handoff and combined-tree unit tests;
- explicit 296 ceiling and EA02 exclusion checks;
- supported `PREPARE_ONLY=1` wrapper;
- mocked final collector with both EA01 and CNIPG passing.

Generated validation artifact:

- artifact ID `9216698035`;
- SHA256 `f63ccb87c652b0b4bc8ec02f6486f40295e7e4f623a1dbb38155d5319b788fd4`.

This CI validates the execution graph and contracts; it does **not** claim that the heavy 294-tip BWA/BLASTx/ASTRAL analyses themselves have run.

## 7. Japanese-origin meta-hypothesis — now a predeclared tree test

Reproducible synthesis:

- `docs/JAPAN_CIRSIUM_ORIGIN_META_ANALYSIS_2026-08-14.md`
- `data/evidence/japan_cirsium_origin_evidence_matrix_v1.csv`
- `data/evidence/japan_cirsium_origin_meta_analysis_v1.json`
- `data/evidence/japan_cirsium_origin_priority_public_sequences_v1.csv`
- `data/evidence/japan_cirsium_origin_falsification_panel_v2.json`

The literature/public-sequence synthesis rejects a strict one-origin model for all Japanese *Cirsium* and instead supports an **oligophyletic colonization history dominated by one major Pleistocene radiation**.

Current hierarchy:

- **minimum defensible histories = 2**: dominant Japanese radiation + *C. lineare* lineage;
- **best current point hypothesis = 3**: dominant radiation + *C. lineare* + *C. dipsacolepis* secondary arrival;
- **4 or more histories = unresolved and currently unsupported**.

Evidence asymmetry is explicit:

- Moreyra's broad nuclear analysis places **36/38 Japanese species (94.74%)** in one dominant radiation;
- *C. lineare* is the strongest replicated exception: 3/3 high-dimensional analyses support its exceptional placement across 2/2 independent high-dimensional data-generation groups;
- *C. lineare* now has exact geographic sequence anchors from Japan target capture (`SRR30887240`), Taiwan transcriptomes (`SRR30617342`, `SRR30617347`) and mainland-China Hubei nrDNA (`AF443727`, `AF443779`);
- *C. dipsacolepis* has exact Moreyra target-capture data (`SRR30887259`) but still lacks a second independent high-dimensional nuclear dataset, so the third-history state remains a working hypothesis rather than an established event count;
- Arenicola is currently sister to Nipponocirsium in the focused phylotranscriptome and is **not** counted as a fourth colonization.

The accession-level falsification panel contains **12 unique critical SRA runs** plus the Hubei *lineare* ITS/ETS anchors. Validation run `31806752296` passed; artifact `9221472767`, SHA256 `705094d675a883918e47d38f686fe0f544eb96ebf2515fb8e2dd32c1e4d967f7`.

Predeclared origin-count decision rules for the maximum-public tree:

1. retain *C. lineare* outside the main Japanese radiation across BWA/BLASTx and concatenation/ASTRAL → minimum **two histories** remains supported;
2. additionally retain *C. dipsacolepis* outside the main radiation with a stable continental nearest-neighbour bracket → promote **three histories**;
3. count a fourth or later history only if another Japanese lineage, such as Arenicola, is independently bracketed by a distinct continental source lineage;
4. chloroplast structure alone never increments origin count;
5. no topology/locus gate may be relaxed after seeing the result.

This reframes the 294→296 heavy tree from a generic “largest tree” exercise into a direct falsification of **2 vs 3 vs 4+ Japanese colonization histories**.

## 8. Reference boundary

The active compatibility target remains the pinned original public Compositae1061 HybPiper reference:

- **1,061 loci**;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

The Moreyra-specific *C. tioganum* augmented target remains unrecovered. Current analyses are compatibility reanalyses rather than exact reproduction of Moreyra preprocessing.

Useful public locus sets remain 1,061 / reproducible 531-candidate / conservative 241.

## 9. Remaining empirical blockers

The implementation blocker is resolved. The main public-nuclear blocker is now **actual heavy execution**:

1. execute the validated v2 maximum-public handoff on HPC/large-memory local compute;
2. obtain accepted baseline BWA and BLASTx trees;
3. complete EA01 BWA/BLASTx paired concatenated + ASTRAL gates;
4. complete CNIPG paired gates against both baseline modes;
5. score the frozen Japanese-origin falsification panel, especially `SRR30887240` (*lineare*), `SRR30887259` (*dipsacolepis*) and the six Arenicola transcriptomes;
6. if EA01 and CNIPG both pass, execute the explicit common-locus `ea01_cnipg_296` combined-tree analysis before changing the accepted primary;
7. freeze Japan-38, *dipsacolepis*, *lineare*, Arenicola and continental-neighbour placements with explicit uncertainty.

Separately, the Chang transcriptome/gene-tree heavy workflow remains an optional downstream mechanism task for var. *takaoense*.

**New broad China sampling remains deliberately unfrozen** until the public tree identifies the continental branches that actually bracket the unresolved Japanese histories.

## 10. Cleanup / safety rule

Keep frozen evidence even when later analysis changes its interpretation. Retire or replace obsolete execution assumptions without deleting the observed data that exposed them.

EA02's durable pack and historical EA01/EA02 contract therefore remain useful provenance/duplicate-control evidence, while the current biological execution graph is strictly EA01 + CNIPG.
