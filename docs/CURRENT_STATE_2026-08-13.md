# EAzami current state — 2026-08-13

This is the operational entry point for EAzami. It records the scientific conclusions that must survive implementation cleanup, the active public-nuclear-tree path, and the remaining implementation debt. Historical code remains recoverable from Git history; superseded executable paths should not remain in the working tree merely for archaeology.

## 1. Biological conclusions that are currently supported

### Repeated white-flower evolution is the default interpretation

Current evidence supports repeated losses of floral anthocyanin pigmentation across East Asian *Cirsium* rather than one single white-flowered lineage.

Two focal interpretations remain important:

- the published Arenicola context favours a white-flower loss on the *C. brevicaule* lineage; it does **not** currently justify calling coloured *C. irumtiense* a regain;
- Taiwanese *C. japonicum* var. *takaoense* remains the strongest candidate regain because the published six-sample topology and directly documented W/BP morph states require a W-to-coloured transition under the current coloured-root minimum-change reconstruction.

For var. *takaoense*, this is a **topology-supported candidate regain**, not proof that an anthocyanin pathway was molecularly lost and then restored. Introgression, ancestral coloured variation, geographic structure, short internodes and reticulation remain viable alternatives.

A demonstrated molecular regain still requires population-aware nuclear history, explicit introgression/standing-variation tests, and a genotype-to-expression-to-pigment-to-phenotype mechanism.

## 2. Nuclear phylogeny: accepted primary state

The accepted public-data baseline is the deduplicated Japan-origin global panel v2:

- **294 unique biological tips**;
- **295 unique public SRRs**;
- Japan-38 membership is provenance/sensitivity metadata, not a topology constraint.

The old v1 inventory of 302 biological samples / 303 SRRs is obsolete. It double-counted eight Taiwan RNA-seq BioSamples reused across Chang 2025 and Chang 2026. Do not rebuild or cite the v1 inventory as current.

The primary tree remains 294 tips until additional samples pass explicit paired-tree promotion gates.

## 3. Ready public augmentation candidates

### EA01 / EA02 same-assay public-SRA gate

The successful frozen Compositae1061 pilot carries two candidates to paired-tree testing:

- EA01 / `PUBEA001` — *C. nipponicum* var. *yoshinoi*: **236/241** strict no-warning BWA loci;
- EA02 / `PUBEA002` — *C. sairamense*: **239/241** strict no-warning BWA loci.

EA01's strict locus set is a subset of EA02's, giving 236 candidate-side joint loci. EA03–EA05 recovered 0/241 and are not carried forward under the current rule.

Both EA01 and EA02 duplicate analysis taxon labels already present in the 294-tip baseline. They provide biological/cross-study replication, **not new analysis taxon labels**.

The active SRA scenarios are:

1. `baseline294`
2. `ea01_295`
3. `ea02_295`
4. `ea01_ea02_296`

Within each mapping mode, all scenarios use the exact same paired locus list. BWA and BLASTx are evaluated independently and symmetrically. Strict automatic promotion requires in both mapping modes and in the single- and joint-candidate scenarios:

- shared-294-tip concatenated RF = 0;
- the existing same-taxon baseline tip among the candidate's nearest baseline neighbours;
- shared-species ASTRAL RF = 0.

Failure of any criterion means manual biological review, not threshold relaxation.

### CNIPG natural-Ulleung public-genome gate

Cleanup exposed a third valid public nuclear candidate that had been omitted from the earlier maximum-public summary:

- CNIPG / `AUG_ULLEUNG_CNIP2024` — natural-Ulleung *Cirsium nipponicum* genome-derived CDS pack;
- **180/241 strict loci**;
- cross-locus subject collisions: `0`;
- locus pack ready: `true`;
- tree-tip promotion before paired trees: `false`.

This candidate is a different data type and is therefore **not folded into the EA01/EA02 SRA gate**. It has a separate cross-data-type sensitivity gate. For each accepted baseline mapping mode (`bwa`, `blastx`), `baseline294` and `cnipg_295` must use the exact intersection of that mode's baseline loci and the frozen 180 genome-derived loci, with at least 100 paired loci.

Automatic promotion requires in both baseline mapping modes:

- shared-294-tip concatenated RF = 0;
- an existing baseline *C. nipponicum* representation among the genome candidate's nearest baseline neighbours;
- shared-species ASTRAL RF = 0.

The baseline already contains the *C. nipponicum* analysis taxon label, so CNIPG also adds **0 new analysis taxon labels**. Its particular value is the natural-Ulleung versus cultivated/garden-provenance comparison.

The gate, real 180-locus artifact, real 294-tip baseline reconstruction, paired-input builder, generalized RF evaluator, ASTRAL metadata and cross-data-type promotion summary have all passed GitHub CI. Heavy tree inference itself remains an HPC/large-memory-local task.

Key files:

- `data/evidence/cirsium_nipponicum_public_genome_comp1061_contract_v1.json`
- `data/evidence/cirsium_nipponicum_comp1061_locus_pack_result_2026-08-13.json`
- `data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json`
- `analysis/prepare_cirsium_nipponicum_augmentation_tree_inputs.py`
- `analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py`
- `analysis/summarize_cirsium_nipponicum_genome_augmentation_sensitivities.py`
- `.github/workflows/validate-cirsium-nipponicum-public-genome-gate.yml`
- `docs/CIRSIUM_NIPPONICUM_PUBLIC_GENOME_AUGMENTATION_GATE_2026-08-13.md`

### Current public-tree ceiling

There are now **three ready public candidate samples** beyond the accepted 294-tip baseline: EA01, EA02 and CNIPG.

If all independent promotion gates eventually pass, the current sample-level public candidate ceiling is **297 tips**, still with **0 new analysis taxon labels**.

This is **not** an accepted combined 297-tip tree. A final combined tree requires an explicit common paired-locus contract across all independently admitted candidates. Until then, the accepted primary remains 294 tips.

## 4. Remaining empirical blockers

The same-assay SRA gate still requires execution of the validated full HPC handoff for:

- baseline BWA and BLASTx recovery;
- fresh EA01/EA02 BLASTx recovery;
- paired concatenated trees;
- source-label ASTRAL sensitivity;
- cross-mapping promotion summary.

The natural-Ulleung genome gate separately requires execution of its paired 294-vs-295 tree bundle against both accepted baseline mapping modes.

New China sampling remains deliberately unfrozen. Public data are being exhausted first; a new sampling list should be chosen only after the maximum public nuclear tree identifies transition-critical gaps.

## 5. Active implementation paths

### Primary nuclear backbone

Keep and develop:

- `analysis/build_japan_origin_global_public_panel_v2.py`
- `analysis/build_japan_origin_global_hpc_bundle_v2.py`
- `analysis/japan_origin_global_hpc_primitives.py`
- `.github/workflows/validate-japan-origin-global-hpc-bundle-v2.yml`
- `data/evidence/japan_origin_global_public_panel_contract_v2.json`

The shared Slurm primitives are parameterized by the active builder. Historical 302-sample counts and `0-301` arrays are no longer embedded in a live helper and corrected by string replacement.

### EA01 / EA02 augmentation

Keep:

- `analysis/prepare_east_asia_public_augmentation_tree_inputs.py`
- `analysis/evaluate_east_asia_public_augmentation_tree_pair.py`
- `analysis/compare_east_asia_public_augmentation_astral_backbone.py`
- `analysis/summarize_east_asia_public_augmentation_sensitivities.py`
- `analysis/build_east_asia_public_augmentation_hpc_bundle.py`
- `analysis/build_east_asia_public_full_hpc_handoff.py`
- `.github/workflows/validate-east-asia-public-augmentation-gate.yml`
- `data/evidence/east_asia_public_tree_augmentation_contract_v1.json`
- `docs/EAST_ASIA_PUBLIC_TREE_AUGMENTATION_GATE_2026-08-13.md`

The paired-tree evaluator is now augmentation-gate-generic and is also reused by the CNIPG cross-data-type gate.

### Flower-colour state layer

The active atlas generation is v0.3. The frozen v0.2 atlas CSV remains because v0.3 uses it as its explicit base evidence layer.

Keep:

- `analysis/build_cirsium_flower_colour_atlas_v0_3.py`
- `analysis/cirsium_flower_colour_atlas_v0_3_readiness.json`
- `tests/test_cirsium_flower_colour_atlas_v0_3.py`
- `.github/workflows/validate-cirsium-flower-colour-atlas-v0-3.yml`
- `data/evidence/cirsium_flower_colour_atlas_v0_2.csv`

### Chang 2026 / Read2Tree

The var. *takaoense* topology work remains a focused hypothesis/provenance workstream. It is secondary to the maximum public nuclear backbone but is not dead code.

For Figure 1 morph provenance, the live CI is validation-only: `.github/workflows/validate-chang2026-takaoense-figure-evidence.yml` checks the six vouchers, W/BP 3+3 assignment, panel B/C direct labels and the frozen official-image SHA256 without repeatedly re-downloading Springer or Research Square content.

The restartable transcriptome/gene-tree runner chain and Read2Tree sensitivity are still referenced by live workflow contracts and should not be deleted until those imports/contracts are refactored.

## 6. Reference/locus-space state

The active compatibility reference is the pinned original public Compositae1061 HybPiper reference:

- 1,061 loci;
- SHA256 `77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`;
- native HybPiper 2.3.4 target-file validation is retained as a live gate.

The Moreyra-specific *C. tioganum* augmentation remains unrecovered, so current runs are compatibility reanalyses rather than exact reproduction of Moreyra preprocessing.

The useful public locus sets remain 1,061 / reproducible 531-candidate / conservative 241. The active 294-tip and augmentation paths use the conservative frozen rule plus current-sample QC rather than the retired broad target-discovery experiments.

## 7. Cleanup applied

The cleanup has removed executable paths that were either known-wrong, superseded by a validated replacement, or closed one-shot discovery stages while retaining frozen evidence needed for scientific audit.

Removed families include:

- Japan-origin global v1 302/303 inventory builder, contract and workflows;
- flower-colour atlas v0.1/v0.2 builders, tests, validation workflows and stale readiness summaries;
- old 302-sample HPC helper after extracting parameterized shared primitives;
- old 96-row `Japan-origin max public panel` and its Chang/Arenicola augmenters;
- old Moreyra 12-sample reanalysis pilot and its target-approval layer;
- broad/expanded Compositae1061 target-discovery implementations, runners and tests after direct pinned-reference recovery succeeded;
- obsolete COS763-as-target-readiness work after the real original Compositae1061 reference was recovered;
- monthly Moreyra final-tree repository monitor after the project moved to independent public-read reconstruction;
- one-shot Elsevier supplement enumeration and Moreyra supplement recovery wrappers;
- standalone Chang 2025 runinfo recovery Action duplicated by the generic live recovery path;
- Chang 2026 Figure 1 live redownload/preprint fallbacks after freezing source evidence and replacing them with validation-only CI;
- one-shot *C. nipponicum* Figshare source-discovery workflow/script/test after freezing the source contract and validating the real 180-locus pack.

No accepted biological conclusion was weakened by these removals. Historical implementations remain available in Git history.

## 8. Cleanup rule going forward

Keep:

- frozen observed evidence and checksums;
- current contracts and promotion gates;
- current builders/runners;
- tests of live code;
- concise state/claim documentation;
- implementation modules directly imported by a live workflow.

Remove only after a replacement is validated:

- executable v1/v0.x entry points superseded by corrected later versions;
- tests that exercise only deleted obsolete entry points;
- Actions that rebuild a known-wrong or superseded state;
- one-shot recovery/audit code after its evidence products are frozen and no live bundle invokes it.

Do **not** delete frozen scientific results simply because their generating implementation is retired.

## 9. Remaining implementation debt

### Moreyra reconciliation artifact

The 294-tip panel rebuild currently depends on the frozen Moreyra full-reconciliation Actions artifact from run `31400324674` / artifact `9067368059`. It is a small final reconciliation CSV but the Actions artifact is time-limited. Before its 2026-11 expiry, the deterministic minimal reconciliation input needed by v2 should be frozen into a durable repository/source-backed form, then the large metadata-recovery Action can be reconsidered.

Do not delete that recovery path before this dependency is removed.

### Colour-rate bridge wrapper

`build_colour_rate_comp1061_bridge_panel_v0_2.py` still wraps/imports the older implementation and overrides an old study-count constant. Refactor the corrected 3/10/7 source partition into one canonical builder before deleting the base/wrapper pair.

### Chang transcriptome runner generations

The current restartable layout-aware runner still imports earlier runner layers and the workflow contract deliberately hashes/tests them. Consolidate the runner implementation first; only then retire the old generation.
