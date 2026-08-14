# EAzami current state — 2026-08-14

This is the operational source of truth for the repository. It separates accepted scientific conclusions, ready-but-not-promoted public candidates, durable evidence, supported execution paths, completed cleanup, and the remaining empirical/HPC work. Historical implementations remain recoverable from Git history and topic-specific evidence documents.

## 1. Accepted scientific state

### Flower-colour history

Current evidence supports repeated white-flower evolution across East Asian *Cirsium* rather than one single white-flowered lineage.

- Arenicola: the published context favours white-flower loss on the *C. brevicaule* lineage. Current evidence does **not** justify calling coloured *C. irumtiense* a regain.
- Taiwanese *C. japonicum* var. *takaoense*: the six directly morph-labelled W/BP samples and displayed topology make a W-to-coloured transition the minimum-change interpretation under the current coloured-root model. This is a **topology-supported candidate regain**, not molecular proof that an anthocyanin pathway was lost and restored.
- Introgression, ancestral coloured standing variation, geographic structure, short internodes and reticulation remain live alternatives.
- A demonstrated molecular regain still requires population-aware nuclear ancestry, explicit introgression/standing-variation tests, and a genotype → expression → pigment → phenotype mechanism.

### Accepted public nuclear baseline

The accepted public-data primary panel is:

- **294 unique biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

Japan-38 membership is provenance/sensitivity metadata, not a topology constraint.

The old 302-tip / 303-SRR inventory is obsolete because eight Taiwan RNA-seq BioSamples/SRRs reused across Chang 2025 and Chang 2026 had been counted twice. The current v2 builder collapses those reused biological samples while retaining source-paper provenance.

The accepted primary remains **294 tips** until additional samples pass explicit paired-tree promotion gates.

## 2. Ready public augmentation candidates

### EA01 / EA02 same-assay public-SRA gate

- EA01 / `PUBEA001` — *C. nipponicum* var. *yoshinoi*: **236/241** strict no-warning BWA loci.
- EA02 / `PUBEA002` — *C. sairamense*: **239/241** strict no-warning BWA loci.
- EA01's strict set is a complete subset of EA02's, giving 236 candidate-side joint BWA loci.
- EA03–EA05 recovered 0/241 and are not carried forward under the current rule.

Both successful candidates duplicate analysis taxon labels already present in the 294-tip baseline. They add biological/cross-study replication and backbone-stability tests, not new taxonomic coverage.

Active scenarios are `baseline294`, `ea01_295`, `ea02_295`, and `ea01_ea02_296`. Within each mapping mode every scenario uses the exact same paired locus list. BWA and BLASTx are evaluated independently and symmetrically.

Strict automatic promotion requires in both mapping modes and relevant single/joint scenarios:

1. shared-294-tip concatenated RF = 0;
2. an existing same-taxon baseline tip among the candidate's nearest baseline neighbours;
3. shared-species ASTRAL RF = 0.

Any failure routes the candidate to manual biological review. Thresholds are not relaxed post hoc.

### CNIPG natural-Ulleung public-genome gate

- CNIPG / `AUG_ULLEUNG_CNIP2024` — natural-Ulleung *C. nipponicum* genome-derived CDS;
- **180/241** strict loci;
- cross-locus subject collisions: **0**;
- locus pack ready: **true**;
- tree-tip promotion before paired trees: **false**.

CNIPG is a different data type and therefore has a separate cross-data-type sensitivity gate. For each accepted baseline mapping mode (`bwa`, `blastx`), `baseline294` and `cnipg_295` use the exact intersection of that mode's accepted baseline loci and the frozen 180-locus genome pack, with at least 100 paired loci.

Automatic promotion requires the same three safeguards: shared-294 RF=0, an existing baseline *C. nipponicum* tip among nearest neighbours, and shared-species ASTRAL RF=0 in both baseline mapping modes.

### Current maximum-public candidate ceiling

There are three ready public candidate samples beyond the accepted 294-tip baseline: EA01, EA02 and CNIPG.

If all independent gates pass, the current sample-level candidate ceiling is **297 tips**, still with **0 new analysis taxon labels**.

This is **not** an accepted combined 297-tip tree. A final combined state requires an explicit common paired-locus contract across independently admitted candidates. Until then, the accepted primary remains 294 tips.

## 3. Durable public evidence

### 294-tip baseline reconciliation

The 294-tip rebuild no longer depends on the former Moreyra Actions artifact `9067368059`.

The exact subset consumed by the v2 builder is frozen under:

- `data/evidence/moreyra2025_cirsium_reconciliation_v1/manifest.json`
- `data/evidence/moreyra2025_cirsium_reconciliation_v1/part_001.csv` … `part_008.csv`
- `analysis/materialize_frozen_moreyra_reconciliation.py`

The durable copy contains **258 linked *Cirsium* reconciliation rows** and only the 11 columns consumed by the v2 builder. Canonical reconstructed CSV SHA256:

`cf3af71a1a77eee5bd177cef9cf8106b749b949eaacc0ad82bbb331978084505`

### EA01 / EA02 / CNIPG locus packs

The successful candidate locus packs are also durable and no longer require expiring Actions artifacts at runtime.

Repository evidence:

- `data/evidence/public_candidate_locus_packs_v1/manifest.json`
- sharded base64(gzip(TSV)) payloads for EA01, EA02 and CNIPG;
- `analysis/materialize_frozen_public_candidate_locus_pack.py`
- `tests/test_materialize_frozen_public_candidate_locus_pack.py`

The manifest retains original artifact IDs/ZIP checksums, strict-locus-list hashes, source-summary hashes, canonical TSV hashes and every source per-locus FASTA hash. The original 2026-11-11 artifact expiry is provenance only.

The freeze audit first verified the source artifact ZIP hashes and then proved byte identity for:

- EA01: all **236** strict FASTAs plus strict locus list and source summary;
- EA02: all **239** strict FASTAs plus strict locus list and source summary;
- CNIPG: all **180** strict FASTAs plus strict locus list and source summary.

Thus **655/655 source locus FASTAs** are exactly reconstructable from repository evidence. Normal EA01/EA02 and CNIPG validation no longer uses `actions: read`, `GH_TOKEN`, or `/actions/artifacts/.../zip` downloads.

For CNIPG, the frozen summary, strict 180-locus list and all 180 locus FASTAs remain mandatory tree inputs. The historical per-locus audit CSV is diagnostic-only; its presence/absence is recorded explicitly in the execution manifest.

## 4. Supported execution paths

### Primary 294-tip nuclear backbone

- `analysis/build_japan_origin_global_public_panel_v2.py`
- `analysis/materialize_frozen_moreyra_reconciliation.py`
- `analysis/build_japan_origin_global_hpc_bundle_v2.py`
- `analysis/japan_origin_global_hpc_primitives.py`
- `.github/workflows/build-japan-origin-global-public-panel-v2.yml`
- `.github/workflows/validate-japan-origin-global-hpc-bundle-v2.yml`
- `data/evidence/japan_origin_global_public_panel_contract_v2.json`

The Slurm-generation primitives are parameterized. Historical 302-sample counts and `0-301` arrays are not embedded in the live helper and patched afterward.

### EA01 / EA02 augmentation

- `analysis/prepare_east_asia_public_augmentation_tree_inputs.py`
- `analysis/evaluate_east_asia_public_augmentation_tree_pair.py`
- `analysis/compare_east_asia_public_augmentation_astral_backbone.py`
- `analysis/summarize_east_asia_public_augmentation_sensitivities.py`
- `analysis/build_east_asia_public_augmentation_hpc_bundle.py`
- `analysis/build_east_asia_public_full_hpc_handoff.py`
- `.github/workflows/validate-east-asia-public-augmentation-gate.yml`
- `data/evidence/east_asia_public_tree_augmentation_contract_v1.json`

### CNIPG augmentation

- `analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py`
- `analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py`
- `analysis/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py`
- `.github/workflows/validate-cirsium-nipponicum-public-genome-gate.yml`
- `data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json`

The tree-pair evaluator is gate-generic and shared across the SRA and CNIPG paths.

### Flower-colour state and colour-rate compatibility path

The active flower-colour atlas generation is v0.3. The frozen v0.2 atlas CSV remains because v0.3 explicitly consumes it as evidence input.

The Compositae1061 bridge has one supported public entry point:

- `analysis/build_colour_rate_comp1061_bridge_panel.py`
- `analysis/colour_rate_comp1061_bridge_primitives.py`

The corrected empirical source partition is Chang2025=3, Chang2026=10, Moreyra2025=7. The former `_v0_2` wrapper is retired.

The HPC compatibility bundle likewise has one supported public entry point:

- `analysis/build_colour_rate_comp1061_hpc_bundle.py`
- `analysis/colour_rate_comp1061_hpc_primitives.py`
- `workflow/colour_rate_comp1061/prepare_hpc_bundle.sh`

The internal primitive modules are now pure helpers: the bridge primitive module has no stale CLI/build path, and the HPC builder no longer monkey-patches an older implementation. The corrected stage-0 contract is owned directly by the canonical builder. Both bridge and HPC validation pass after this simplification.

### var. takaoense transcriptome/gene-tree path

There is now one supported transcriptome execution entry point:

- `analysis/run_chang2026_restartable_transcriptome_assembly.py`

The former `run_chang2026_layout_aware_transcriptome_assembly.py` adapter and `run_chang2026_transcriptome_assembly.py` paired runner have been retired. Their live gates were moved into the canonical runner rather than discarded.

The canonical runner directly requires:

- exact expected panel size;
- unique sample IDs and official runs;
- verified/probable run reconciliation;
- official `LibraryLayout=PAIRED`;
- `de_novo_required=true` and `preferred_sequence_source == matched_run`;
- for the six-sample pilot, exactly six focal rows and exactly **BP=3 / W=3**;
- explicit failure on a future official `SINGLE` layout until a tested single-end branch exists.

The current workflow contract is:

`chang2026_gene_tree_workflow_v4_canonical_restartable_sra`

The Snakemake DAG hashes only the live assembly/prefix/orthogroup/gene-tree/scoring scripts. After retirement of the two older runners, both the complete gene-tree workflow CI and restartable-pilot CI pass from source-backed public metadata through dry-run validation.

The Figure 1 provenance path remains validation-only and does not repeatedly download publisher content.

## 5. Reference and locus-space boundary

The active compatibility target is the pinned original public Compositae1061 HybPiper reference:

- 1,061 loci;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`;
- native HybPiper 2.3.4 target-file validation retained as a live gate.

The Moreyra-specific *C. tioganum* augmentation remains unrecovered, so current runs are compatibility reanalyses rather than exact reproduction of Moreyra preprocessing.

Useful public locus sets remain 1,061 / reproducible 531-candidate / conservative 241.

## 6. Cleanup already applied

Major retired executable families include:

- incorrect Japan-origin global v1 302/303 inventory builder, contract and workflows;
- old 302-sample HPC helper after extraction of parameterized primitives;
- old 96-row Japan-origin intermediate panel and its Chang/Arenicola augmenters;
- flower-colour atlas v0.1/v0.2 builders, tests, workflows and stale readiness outputs;
- old Moreyra 12-sample pilot and target-approval layer;
- broad/expanded Compositae1061 target-discovery implementations and tests;
- obsolete COS763-as-target-readiness work;
- monthly Moreyra final-tree repository monitor;
- closed one-shot Elsevier/Moreyra supplement and source-recovery wrappers;
- live Chang 2026 Figure 1 re-download/preprint fallback code;
- one-shot *C. nipponicum* Figshare discovery and obsolete BioSample morph-discovery code;
- colour-rate bridge/HPC `_v0_2` public wrapper generations;
- one-shot candidate-pack freeze/migration workflows after durable evidence was committed;
- the two superseded Chang transcriptome runner generations and their adapter-specific test.

The repository retains the useful organizational structure from main: workstream navigation, data/schema documentation, capitulum-trait foundation, archived historical decision notes and separated request drafts. Frozen scientific evidence and checksums required by current analyses were retained. Historical code remains recoverable from Git history.

## 7. Remaining empirical blockers

1. Run the validated EA01/EA02 full HPC/local handoff: baseline BWA + BLASTx recovery, fresh candidate BLASTx recovery, paired concatenated trees, source-label ASTRAL and cross-mapping summary.
2. Run the CNIPG paired 294-vs-295 bundle against both accepted baseline mapping modes.
3. If candidates pass independently, construct the explicit common paired-locus combined tree before promoting a 296/297 state.
4. Separately, execute the Chang transcriptome/gene-tree heavy workflow if the var. *takaoense* candidate-regain mechanism workstream is advanced; CI currently validates its inputs, gates and DAG only.

New China sampling remains deliberately unfrozen until the public nuclear candidate ceiling is evaluated.

## 8. Remaining implementation debt

For the audited active execution paths above, the known superseded wrapper/runner-generation debt has been removed. No threshold or accepted scientific result was changed to achieve the cleanup.

Future cleanup should be evidence-driven: if another executable looks old, first prove that no current workflow, contract, frozen result or downstream builder depends on it. Do not delete scientific outputs merely because their original generating implementation is historical.

The main unresolved work is now empirical/heavy-compute rather than another versioned-wrapper migration.

## 9. Navigation

- Repository entry point: `README.md`
- Higher-level workstream/decision map: `PROJECT_STATUS.md`
- Documentation map: `docs/README.md`
- Current operational state: this file

## Cleanup rule

Keep frozen evidence, checksums, current contracts, promotion gates, live builders/runners and tests of live code. Remove an old executable path only after its replacement is validated. Never delete an observed scientific result merely because its generating implementation has been retired.
