# EAzami current state — 2026-08-14

This is the operational source of truth for the repository. It separates accepted scientific conclusions, ready-but-not-promoted public candidates, active execution paths, completed cleanup, and remaining blockers. Historical implementations remain recoverable from Git history and topic-specific evidence documents.

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

Both successful candidates duplicate analysis taxon labels already present in the 294-tip baseline. They provide biological/cross-study replication and backbone-stability tests, not taxonomic expansion.

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

## 3. Durable 294-tip baseline reconstruction

The 294-tip rebuild no longer depends on the expiring Moreyra Actions artifact `9067368059`.

The exact subset consumed by the v2 builder is frozen under:

- `data/evidence/moreyra2025_cirsium_reconciliation_v1/manifest.json`
- `data/evidence/moreyra2025_cirsium_reconciliation_v1/part_001.csv` … `part_008.csv`
- `analysis/materialize_frozen_moreyra_reconciliation.py`

The durable copy contains **258 linked *Cirsium* reconciliation rows** and only the 11 columns consumed by the v2 builder. The manifest retains the original workflow run, artifact ID, source-file checksum, artifact ZIP checksum, per-shard checksums and canonical reconstructed-CSV checksum.

Canonical reconstructed CSV SHA256:

`cf3af71a1a77eee5bd177cef9cf8106b749b949eaacc0ad82bbb331978084505`

The panel-v2, HPC-v2, EA01/EA02 and CNIPG validation workflows rebuild the real 294/295 baseline from this repository evidence. The generic Moreyra metadata-recovery workflow can remain for source re-audit but is no longer a runtime dependency of the primary nuclear-tree CI path.

## 4. Active implementation paths

### Primary 294-tip nuclear backbone

- `analysis/build_japan_origin_global_public_panel_v2.py`
- `analysis/materialize_frozen_moreyra_reconciliation.py`
- `analysis/build_japan_origin_global_hpc_bundle_v2.py`
- `analysis/japan_origin_global_hpc_primitives.py`
- `.github/workflows/build-japan-origin-global-public-panel-v2.yml`
- `.github/workflows/validate-japan-origin-global-hpc-bundle-v2.yml`
- `data/evidence/japan_origin_global_public_panel_contract_v2.json`

The live Slurm-generation primitives are parameterized. Historical 302-sample counts and `0-301` arrays are no longer embedded in a live helper and corrected later by string replacement.

### EA01 / EA02 augmentation

- `analysis/prepare_east_asia_public_augmentation_tree_inputs.py`
- `analysis/evaluate_east_asia_public_augmentation_tree_pair.py`
- `analysis/compare_east_asia_public_augmentation_astral_backbone.py`
- `analysis/summarize_east_asia_public_augmentation_sensitivities.py`
- `analysis/build_east_asia_public_augmentation_hpc_bundle.py`
- `analysis/build_east_asia_public_full_hpc_handoff.py`
- `.github/workflows/validate-east-asia-public-augmentation-gate.yml`
- `data/evidence/east_asia_public_tree_augmentation_contract_v1.json`
- `docs/EAST_ASIA_PUBLIC_TREE_AUGMENTATION_GATE_2026-08-13.md`

### CNIPG augmentation

- `data/evidence/cirsium_nipponicum_public_genome_comp1061_contract_v1.json`
- `data/evidence/cirsium_nipponicum_comp1061_locus_pack_result_2026-08-13.json`
- `data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json`
- `analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py`
- `analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py`
- `analysis/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py`
- `.github/workflows/validate-cirsium-nipponicum-public-genome-gate.yml`
- `docs/CIRSIUM_NIPPONICUM_PUBLIC_GENOME_AUGMENTATION_GATE_2026-08-13.md`

The tree-pair evaluator is gate-generic and shared across the SRA and CNIPG paths.

### Flower-colour state and rate bridge

The active flower-colour atlas generation is v0.3. The frozen v0.2 atlas CSV remains because v0.3 explicitly consumes it as its evidence base.

The flower-colour Compositae1061 bridge now has **one supported public entry point**:

- `analysis/build_colour_rate_comp1061_bridge_panel.py`
- `analysis/colour_rate_comp1061_bridge_primitives.py`
- `tests/test_build_colour_rate_comp1061_bridge_panel.py`
- `.github/workflows/build-colour-rate-comp1061-bridge-panel.yml`

The corrected empirical source partition is frozen directly as Chang2025=3, Chang2026=10, Moreyra2025=7. The old `_v0_2.py` wrapper that temporarily overwrote an older constant has been removed.

### var. takaoense focused topology/provenance work

The var. *takaoense* workstream is secondary to the maximum public backbone but scientifically live.

The Figure 1 provenance CI is validation-only and verifies the six vouchers, W/BP 3+3 assignment, direct panel B/C labels and frozen official-image checksum without repeatedly downloading publisher content.

The Read2Tree and restartable transcriptome/gene-tree contracts remain live. The graph-aligned main-branch organization has been integrated, including the current frozen hypothesis table, scoring contract, Read2Tree path fixes and workflow navigation.

## 5. Reference and locus-space boundary

The active compatibility target is the pinned original public Compositae1061 HybPiper reference:

- 1,061 loci;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`;
- native HybPiper 2.3.4 target-file validation retained as a live gate.

The Moreyra-specific *C. tioganum* augmentation remains unrecovered, so current runs are compatibility reanalyses rather than exact reproduction of Moreyra preprocessing.

Useful public locus sets remain 1,061 / reproducible 531-candidate / conservative 241.

## 6. Cleanup already applied

Retired executable families include:

- incorrect Japan-origin global v1 302/303 inventory builder, contract and workflows;
- old 302-sample HPC helper after extraction of parameterized primitives;
- old 96-row Japan-origin intermediate panel and its Chang/Arenicola augmenters;
- flower-colour atlas v0.1/v0.2 builders, tests, workflows and stale readiness outputs;
- old Moreyra 12-sample pilot and target-approval layer;
- broad/expanded Compositae1061 target-discovery implementations and tests;
- obsolete COS763-as-target-readiness work;
- monthly Moreyra final-tree repository monitor;
- one-shot Elsevier/Moreyra supplement recovery wrappers and standalone Chang 2025 runinfo Action;
- live Chang 2026 Figure 1 re-download/preprint fallback code;
- one-shot *C. nipponicum* Figshare discovery code;
- obsolete Chang BioSample morph-discovery code after direct Figure 1 evidence was frozen;
- colour-rate bridge `_v0_2` monkey-patch wrapper and wrapper-only test.

The repository now also retains the useful organizational structure from main: workstream navigation, data/schema documentation, capitulum-trait foundation, archived historical decision notes and separated request drafts. Cleanup-specific deletions were preserved when that structure was merged.

Frozen scientific evidence and checksums required by current analyses were retained. Historical code remains recoverable from Git history.

## 7. Remaining empirical blockers

1. Run the validated EA01/EA02 full HPC/local handoff: baseline BWA + BLASTx recovery, fresh candidate BLASTx recovery, paired concatenated trees, source-label ASTRAL and cross-mapping summary.
2. Run the CNIPG paired 294-vs-295 bundle against both accepted baseline mapping modes.
3. If candidates pass independently, construct the explicit common paired-locus combined tree before promoting a 296/297 state.

New China sampling remains deliberately unfrozen until this public-data ceiling is evaluated.

## 8. Remaining implementation debt

### Candidate pack durability

EA01, EA02 and CNIPG validation still consume successful locus-pack Actions artifacts:

- EA01 artifact `9175870949`, SHA256 `275fecf31e202ae28914441faff70a7faede3c2b8912901221d84e4aa6ef2232`;
- EA02 artifact `9175876315`, SHA256 `6a9c0d91b2d98ed5ebc72bf96effd5f41c8c6f865747b1d1124ee3d59eb0d1bb`;
- CNIPG artifact `9174758977`, SHA256 `079e3bfaab1d5041ebc2dcb1919532c75eefde7ffe1f766ab0473845f2f9dd69`.

They currently expire on 2026-11-11. Provenance and compact result summaries are frozen, but the actual small locus packs still need a durable binary-capable repository/archive route or a deterministic durable source before expiry.

### Colour-rate bridge primitives

The public bridge entrypoint is now canonical, but `analysis/colour_rate_comp1061_bridge_primitives.py` was initially extracted from the old implementation wholesale. It still carries some historical entrypoint/build scaffolding that is no longer part of the supported interface. Slim that internal module only after the canonical bridge CI is stable.

### Colour-rate HPC generations

The colour-rate HPC path still has base/v0.2 builder generations. Inspect and consolidate that pair separately; do not assume it is identical to the bridge wrapper case.

### Chang transcriptome runner generations

The restartable layout-aware runner still imports earlier runner layers and the current workflow contract deliberately hashes/tests them. Consolidate first, then retire older generations.

## 9. Navigation

- Repository entry point: `README.md`
- Higher-level workstream/decision map: `PROJECT_STATUS.md`
- Documentation map: `docs/README.md`
- Current operational state: this file

## Cleanup rule

Keep frozen evidence, checksums, current contracts, promotion gates, live builders/runners and tests of live code. Remove an old executable path only after its replacement is validated. Never delete an observed scientific result merely because its generating implementation has been retired.
