# EAzami current state — 2026-08-14

This is the operational source of truth for the repository. It separates accepted scientific conclusions, empirical public-candidate disposition, durable evidence, supported execution paths and remaining heavy-compute work. Historical implementations and superseded planning states remain recoverable from Git history and dated evidence files.

## 1. Accepted scientific state

### Flower-colour history

Current evidence supports repeated white-flower evolution across East Asian *Cirsium* rather than one single white-flowered lineage.

- Arenicola: current published context favours white-flower loss on the *C. brevicaule* lineage. Current evidence does **not** establish regain in coloured *C. irumtiense*.
- Taiwanese *C. japonicum* var. *takaoense*: directly morph-labelled W/BP samples plus the displayed topology make a W-to-coloured transition the current minimum-change interpretation under a coloured-root model. This remains a **topology-supported candidate regain**, not molecular proof of pathway loss and restoration.
- Introgression, ancestral coloured standing variation, geographic structure, short internodes and reticulation remain live alternatives.
- A demonstrated molecular regain still requires population-aware nuclear ancestry, explicit introgression/standing-variation tests, and a genotype → expression → pigment → phenotype mechanism.

### Accepted public nuclear baseline

The accepted public-data primary panel remains:

- **294 unique biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

Japan-38 membership is provenance/sensitivity metadata, not a topology constraint. The old 302-tip / 303-SRR inventory remains obsolete because eight Taiwan RNA-seq BioSamples/SRRs reused across Chang 2025 and Chang 2026 had been double-counted.

No result below has yet superseded the accepted **294-tip** primary tree.

## 2. Real-read public-candidate audit — new empirical result

The pre-HPC candidate list originally treated EA01 and EA02 as two independent public-SRA replicates. A real-read empirical audit on 2026-08-14 changed that interpretation.

Frozen evidence:

- `data/evidence/public_candidate_empirical_quartet_2026-08-14.json`
- `data/evidence/east_asia_public_candidate_disposition_v2.json`

### Real baseline recovery

Two exact same-taxon samples already inside the accepted 294-tip baseline were recovered directly from public SRA and rerun through the pinned Compositae1061/HybPiper 2.3.4 BWA path:

- `MRY_YOSHINOI` — *C. nipponicum* var. *yoshinoi*, `SRR30887222`: **236/241** strict no-warning loci;
- `MRY_SAIRAMENSE` — *C. sairamense*, `SRR25265647`: **239/241** strict no-warning loci.

Both had zero current paralog-warning loci under the strict pilot rule.

### Four-tip empirical ML analysis

The recovered baseline packs were compared to frozen real candidate packs EA01 and EA02 on one exact four-way locus intersection:

- four-way common strict loci: **235**;
- gene-tree-informative loci: **231**;
- concatenated alignment: **105,086 nt**;
- variable sites: **2,769**;
- parsimony-informative sites: **2,199**.

All **231/231** informative per-locus ML trees supported the same unrooted split:

`(MRY_YOSHINOI, PUBEA001) | (MRY_SAIRAMENSE, PUBEA002)`

The concatenated IQ-TREE analysis supported the same topology with **SH-aLRT/UFBoot = 100/100**. The BIC-selected model was `TIM3+F+G4`.

This strongly validates that EA01 and EA02 both fall with their expected same-taxon baseline sample. It does **not** by itself test the full shared-294 backbone or source-label ASTRAL stability.

### EA01 disposition — retain

EA01 / `PUBEA001` remains a genuine independent candidate:

- taxon: *C. nipponicum* var. *yoshinoi*;
- strict loci: **236/241**;
- baseline same-taxon sample: **236/241**;
- raw public libraries are clearly different: before-filtering read counts, base counts, quality totals and GC differ substantially;
- the empirical quartet gives 231/231 same-taxon gene-tree support.

**Disposition:** retain EA01 for the full 294-tip BWA/BLASTx concatenated-RF + same-taxon-neighbour + source-label-ASTRAL gate. The quartet does not pre-authorize promotion.

### EA02 disposition — exclude as independent tip

EA02 / `PUBEA002` no longer counts as an independent biological augmentation candidate.

Against the accepted baseline *C. sairamense* sample:

- both recover exactly **239/241** strict loci;
- strict-locus sets are identical;
- before-filtering `fastp` summary is identical: **10,779,802 reads**, **1,088,760,002 bases**, identical Q20/Q30 counts and rates, read lengths and GC;
- the complete raw R1 and R2 before-filtering quality/base-content objects are identical;
- duplication and insert-size profiles are identical;
- the concatenated ML tree gives effectively zero terminal branches for the *sairamense* pair.

These independent signatures are overwhelmingly consistent with reuse/re-deposition of the same underlying raw read library rather than an independent biological replicate. We do **not** claim the same physical specimen without explicit source provenance proving that identity.

**Disposition:** `duplicate_readset_pseudoreplicate_excluded_pending_explicit_provenance`. EA02 may remain as a pipeline duplicate-control, but it must not increment biological-tip count and must not be promoted as a second *C. sairamense* sample.

## 3. Current public augmentation candidates

### EA01 — independent public-SRA candidate

- `PUBEA001`, *C. nipponicum* var. *yoshinoi*;
- **236/241** strict loci;
- independent raw public library confirmed by empirical audit;
- full 294-tip BWA/BLASTx + concatenated/ASTRAL gate still required.

### CNIPG — independent cross-data-type genome candidate

- `AUG_ULLEUNG_CNIP2024`, natural-Ulleung *C. nipponicum* genome-derived CDS;
- **180/241** strict loci;
- zero cross-locus subject collisions;
- evaluated separately against both accepted baseline mapping modes;
- full paired 294-vs-295 cross-data-type gate still required.

### Revised maximum-public ceiling

There are now **two**, not three, defensible independent candidates beyond the accepted 294-tip primary: EA01 and CNIPG.

If both independently pass their full gates, the current public sample-level ceiling is therefore:

- **296 biological tips**;
- **0 new analysis taxon labels**.

This is **not** an accepted combined 296-tip tree. A common paired-locus combined analysis is still required after independent admission.

The old **297-tip** ceiling is a superseded pre-empirical planning state and must not be used as the current biological-tip ceiling.

## 4. Durable evidence

### 294-tip baseline reconciliation

The baseline rebuild is artifact-independent and uses:

- `data/evidence/moreyra2025_cirsium_reconciliation_v1/`
- `analysis/materialize_frozen_moreyra_reconciliation.py`

Canonical reconstructed Moreyra input SHA256:

`cf3af71a1a77eee5bd177cef9cf8106b749b949eaacc0ad82bbb331978084505`

### Candidate locus packs

All previously successful candidate packs remain reproducible from repository evidence:

- EA01: **236** strict FASTAs;
- EA02: **239** strict FASTAs — retained as duplicate-control evidence, not an independent tip;
- CNIPG: **180** strict FASTAs.

The original candidate pack archive remains useful provenance even when a candidate is biologically excluded after downstream audit.

### Empirical quartet outputs

Real-read recovery run: `31788828923`.

Final ML run: `31792170949`.

Frozen result artifact digest:

`sha256:a8069ba48efd89d1e922b5ff5f2b71f1db763e1f1ae32622c5bd995a15031ccf`

Important result-file hashes are recorded in `public_candidate_empirical_quartet_2026-08-14.json`.

## 5. Supported execution paths

### Primary baseline

- `analysis/build_japan_origin_global_public_panel_v2.py`
- `analysis/build_japan_origin_global_hpc_bundle_v2.py`
- `analysis/japan_origin_global_hpc_primitives.py`

### Same-assay candidate diagnostics

The existing EA01/EA02 scenario builder remains useful for reproducing the pre-empirical pair and for using EA02 as a duplicate-control. Its current summarizer now enforces the post-empirical rule:

- EA01 can pass/fail a biological sample-tip promotion gate;
- EA02 tree checks remain diagnostic;
- EA02 `sample_tip_promotion_allowed` is always false under the current disposition.

Key paths:

- `analysis/prepare_east_asia_public_augmentation_tree_inputs.py`
- `analysis/evaluate_east_asia_public_augmentation_tree_pair.py`
- `analysis/compare_east_asia_public_augmentation_astral_backbone.py`
- `analysis/summarize_east_asia_public_augmentation_sensitivities.py`

### CNIPG

- `analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py`
- `analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py`
- `analysis/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py`

### Maximum-public top-level wrapper

`workflow/public_nuclear_maximum/prepare_and_submit.sh` now treats the old 297-tip v1 orchestration as **reproducibility-only**. `PREPARE_ONLY=1` can still rebuild it, but real Slurm submission is fail-closed because that graph contains the superseded EA02-independent-tip assumption.

A post-empirical EA01+CNIPG execution handoff is the next implementation task before launching the maximum-public heavy run.

### var. takaoense and colour-rate work

The canonical restartable Chang transcriptome runner and colour-rate bridge/HPC paths remain unchanged by this public-candidate audit. No flower-colour history claim is modified by the EA02 disposition.

## 6. Reference and locus-space boundary

The active compatibility target remains the pinned original public Compositae1061 HybPiper reference:

- **1,061 loci**;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`.

The Moreyra-specific *C. tioganum* augmented target remains unrecovered. Current raw-read analyses are compatibility reanalyses, not exact reproduction of Moreyra preprocessing.

Useful public locus sets remain 1,061 / reproducible 531-candidate / conservative 241.

## 7. Remaining empirical blockers

1. Build the post-empirical **EA01-only** same-assay heavy handoff; retain EA02 only as an optional duplicate-control diagnostic.
2. Execute EA01 against the full 294-tip baseline under BWA and BLASTx, requiring shared-294 concatenated RF=0, same-taxon nearest-neighbour placement and shared-species ASTRAL RF=0.
3. Execute CNIPG against the full 294-tip baseline under both accepted baseline mapping modes with the existing cross-data-type gate.
4. If EA01 and CNIPG both pass independently, build a new explicit common paired-locus **296-tip** combined tree before changing the accepted primary.
5. Separately, execute the Chang transcriptome/gene-tree heavy workflow if the var. *takaoense* candidate-regain mechanism workstream is advanced.

New broad China sampling remains deliberately unfrozen until this revised public-only ceiling is empirically resolved.

## 8. Cleanup / safety rule

Keep frozen evidence even when later analysis changes its interpretation. Retire or block only the obsolete **claim or execution assumption**, not the underlying observed data.

In particular, EA02's pack and historical candidate contract are retained because they document how the duplicate was detected. The current disposition layer supersedes its use as an independent biological tip.
