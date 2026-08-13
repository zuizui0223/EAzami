# EAzami current state — 2026-08-13

This file is the operational entry point for the repository. It records the conclusions that should survive implementation cleanup and identifies the active analysis path. Historical code remains recoverable from Git history; obsolete executable paths should not remain in the working tree merely for archaeology.

## 1. Biological conclusions that are currently supported

### Repeated white-flower evolution is the default interpretation

The current evidence supports repeated losses of floral anthocyanin pigmentation across East Asian *Cirsium* rather than one single white-flowered lineage.

Two focal interpretations are especially important:

- the published Arenicola context favours a white-flower loss on the *C. brevicaule* lineage; it does **not** currently justify calling coloured *C. irumtiense* a regain;
- Taiwanese *C. japonicum* var. *takaoense* remains the strongest candidate regain because the published six-sample topology and directly documented W/BP morph states require a W-to-coloured transition under the current coloured-root minimum-change reconstruction.

For var. *takaoense*, this is a **topology-supported candidate regain**, not proof that an anthocyanin pathway was molecularly lost and then restored. Introgression, ancestral coloured variation, geographic structure, short internodes and reticulation remain viable alternatives.

A demonstrated molecular regain still requires population-aware nuclear history, explicit introgression/standing-variation tests, and a genotype-to-expression-to-pigment-to-phenotype mechanism.

## 2. Nuclear phylogeny: current primary state

The accepted public-data baseline is the deduplicated Japan-origin global panel v2:

- **294 unique biological tips**;
- **295 unique public SRRs**;
- Japan-38 membership is provenance/sensitivity metadata, not a topology constraint.

The old v1 inventory of 302 biological samples / 303 SRRs is obsolete. It double-counted eight Taiwan RNA-seq BioSamples reused across Chang 2025 and Chang 2026. Do not rebuild or cite the v1 panel as the current sample inventory.

### East Asia public augmentation gate

The successful frozen Compositae1061 pilot currently admits only two candidates to paired-tree testing:

- EA01 / PUBEA001 — *C. nipponicum* var. *yoshinoi*: 236/241 strict no-warning BWA loci;
- EA02 / PUBEA002 — *C. sairamense*: 239/241 strict no-warning BWA loci.

EA01's strict locus set is a subset of EA02's, giving 236 candidate-side joint loci. EA03–EA05 recovered 0/241 and are not carried forward under the present gate.

Both EA01 and EA02 duplicate analysis taxon labels already present in the 294-tip baseline. They add biological/cross-study replication, **not new analysis taxon labels**.

The only active augmentation scenarios are:

1. `baseline294`
2. `ea01_295`
3. `ea02_295`
4. `ea01_ea02_296`

Within each mapping mode, the four trees must use the same paired locus list: accepted baseline loci intersected with both candidate strict-locus sets. BWA and BLASTx are evaluated independently and symmetrically.

The strict automatic promotion route requires, in both mapping modes and in the single- and joint-candidate scenarios:

- shared-294-tip concatenated RF = 0;
- the existing same-taxon baseline tip among the candidate's nearest baseline neighbours;
- shared-species ASTRAL RF = 0.

Failure of any criterion means manual biological review, not threshold relaxation.

Therefore the current sample-level ceiling is **at most 296 tips**, still with **0 newly added analysis taxon labels**. The 294-tip tree remains primary until the paired HPC analysis passes the frozen gate.

## 3. What is still blocked

The main empirical blocker is execution of the validated full HPC handoff for:

- baseline BWA and BLASTx recovery;
- fresh candidate BLASTx recovery;
- paired concatenated trees;
- source-label ASTRAL sensitivity;
- cross-mapping promotion summary.

New China sampling remains deliberately unfrozen. Public data are being exhausted first; a new sampling list should be chosen only after the maximum public nuclear tree identifies transition-critical gaps.

## 4. Active implementation paths

### Primary nuclear backbone / augmentation

Keep and develop:

- `analysis/build_japan_origin_global_public_panel_v2.py`
- `analysis/build_japan_origin_global_hpc_bundle_v2.py`
- `analysis/prepare_east_asia_public_augmentation_tree_inputs.py`
- `analysis/evaluate_east_asia_public_augmentation_tree_pair.py`
- `analysis/compare_east_asia_public_augmentation_astral_backbone.py`
- `analysis/summarize_east_asia_public_augmentation_sensitivities.py`
- `analysis/build_east_asia_public_augmentation_hpc_bundle.py`
- `analysis/build_east_asia_public_full_hpc_handoff.py`
- `.github/workflows/validate-east-asia-public-augmentation-gate.yml`
- `data/evidence/japan_origin_global_public_panel_contract_v2.json`
- `data/evidence/east_asia_public_tree_augmentation_contract_v1.json`
- `docs/EAST_ASIA_PUBLIC_TREE_AUGMENTATION_GATE_2026-08-13.md`

### Flower-colour state layer

The active atlas generation is v0.3. Earlier v0.1/v0.2 builders and validation workflows are historical prototypes and should not be executable from the current tree.

Keep:

- `analysis/build_cirsium_flower_colour_atlas_v0_3.py`
- `analysis/cirsium_flower_colour_atlas_v0_3_readiness.json`
- `tests/test_cirsium_flower_colour_atlas_v0_3.py`
- `.github/workflows/validate-cirsium-flower-colour-atlas-v0-3.yml`

### Chang 2026 / Read2Tree

The var. *takaoense* topology work remains a focused hypothesis test and provenance layer. It is useful, but it is secondary to the current 294-tip public nuclear backbone. Frozen morph assignments, topology hypotheses, marker contracts and source evidence should be retained even when superseded exploratory runners are later removed.

## 5. Cleanup rule

Keep:

- frozen observed evidence and checksums;
- current contracts and decision gates;
- current builders/runners;
- tests of live code;
- concise state/claim documentation.

Remove from the live tree when a replacement is validated:

- executable v1/v0.x pipelines superseded by a corrected later version;
- tests that only exercise deleted obsolete code;
- GitHub Actions workflows that can rebuild known-wrong or superseded states;
- one-off recovery workflows after their recovered artifacts are frozen and the recovery implementation no longer participates in current CI.

Do **not** delete a frozen scientific result merely because its generating implementation is retired. Historical source code remains available through Git history.

## 6. First cleanup applied with this state file

The first cleanup removes two closed obsolete families:

1. Japan-origin global panel **v1** executable path (302-sample inventory), because v2 explicitly corrects its cross-paper duplicate-sample error.
2. Flower-colour atlas **v0.1/v0.2** executable/test/workflow paths, because v0.3 is the active validated atlas generation.

This cleanup does not change any accepted biological conclusion, the 294-tip baseline, the EA01/EA02 augmentation gate, or any frozen source evidence used by the active path.
