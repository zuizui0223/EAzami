# East Asia public-SRA nuclear-tree augmentation gate — 2026-08-13

## Purpose

Continue the public-data-only maximum nuclear phylogeny before defining any new China field-sampling list. The baseline remains the deduplicated Japan-origin global panel v2: **294 unique biological tips / 295 unique public SRRs**. Japan-38 membership is provenance/sensitivity metadata, not a topology constraint.

This document defines the **EA01/EA02 public-SRA same-assay gate**. A separate natural-Ulleung *Cirsium nipponicum* genome-derived candidate is now handled by `docs/CIRSIUM_NIPPONICUM_PUBLIC_GENOME_AUGMENTATION_GATE_2026-08-13.md`; it is intentionally not mixed into this SRA mapping-sensitivity contract.

## Public SRA pilot result now frozen in-repo

Successful workflow run `31684233834` recovered the five audited East Asian candidates against the frozen Compositae1061 241-locus universe after fixing the HybPiper `paralog_report.tsv` path contract.

- EA01 — `PUBEA001`, *Cirsium nipponicum var. yoshinoi*: **236/241 strict no-warning loci**, pilot-ready.
- EA02 — `PUBEA002`, *Cirsium sairamense*: **239/241 strict no-warning loci**, pilot-ready.
- EA03 — *C. japonicum* var. *spinossimum*: **0/241**, not pilot-ready.
- EA04 — *C. setidens*: **0/241**, not pilot-ready.
- EA05 — *C. japonicum* var. *ussuriense*: **0/241**, not pilot-ready.

EA01's BWA strict locus set is a complete subset of EA02's; their BWA candidate-only joint set is therefore **236 loci**. EA03–EA05 are not carried forward under the present Compositae1061 admission rule. Their workflow success is retained as evidence that the zero-locus outcome is a data/recovery result rather than a pipeline crash.

Machine-readable evidence is `data/evidence/east_asia_public_sra_comp1061_pilot_results_2026-08-13.csv`. Artifact IDs and SHA256 digests are frozen there.

## Baseline taxon reconciliation

Both successful candidates duplicate analysis taxon labels already present in the 294-tip baseline.

- EA01 is an independent *C. nipponicum* var. *yoshinoi* sample. The baseline Moreyra sample is `SAMN44017955` / `SRR30887222`.
- EA02 is an independent cross-study *C. sairamense* sample. The baseline Moreyra sample is `SAMN34240330` / `SRR25265647`, with the published locality `Tajikistan: Maijora`.

Thus the SRA pilot adds potentially useful biological replicates and cross-study placement tests, but **adds zero new analysis taxon labels** to the 294-tip baseline.

## Paired-tree rule

No candidate is promoted from locus recovery alone. The next tree stage uses four scenarios:

1. `baseline294`
2. `ea01_295`
3. `ea02_295`
4. `ea01_ea02_296`

Within each mapping mode, all four use the exact same locus list:

`accepted baseline-294 loci for that mapping ∩ EA01 strict loci for that mapping ∩ EA02 strict loci for that mapping`.

At least 100 joint paired loci are required separately for BWA and BLASTx. The BWA and BLASTx accepted locus sets are allowed to differ because mapping sensitivity is itself part of the test. No post-hoc filter relaxation is allowed.

EA01 is an independent same-taxon target-capture replicate. Its role is assay/placement replication: it should recover the neighbourhood of the existing *C. nipponicum* var. *yoshinoi* public tip across mapping/tree sensitivities. EA02 is an independent cross-study same-taxon *C. sairamense* replicate, not a new taxon label. It should reproduce the existing *C. sairamense* neighbourhood across BWA and BLASTx concatenated trees and source-label ASTRAL sensitivity.

For every augmented concatenated tree, the 294 shared baseline focal tips are pruned conceptually and their unrooted Robinson–Foulds distance from the paired `baseline294` tree is recorded. RF is a diagnostic, not a loophole: a non-zero value must be interpreted rather than hidden by changing the locus set. The source-label ASTRAL backbone is evaluated separately on the baseline species IDs.

## Candidate-side mapping sensitivity

The original successful public-SRA pilot used HybPiper/BWA for EA01 and EA02. Reusing those same candidate sequences in the BLASTx tree would test only the baseline mapping sensitivity and would therefore be asymmetric.

The full HPC handoff fixes that problem:

- **BWA candidate side:** use the frozen successful EA01/EA02 BWA packs from run `31684233834` (236/241 and 239/241).
- **BLASTx candidate side:** download the original EA01/EA02 SRRs again on HPC, run fresh HybPiper 2.3.4 without `--bwa`, rebuild strict frozen-241 packs, and require `pilot_locus_pack_ready=true` before BLASTx paired trees start.

Thus each mapping mode uses baseline and candidate sequences recovered under the same mapping strategy. Candidate BLASTx recovery is deliberately performed on HPC/local compute, not inferred from the BWA pack.

## Frozen cross-mapping promotion gate

`analysis/summarize_east_asia_public_augmentation_sensitivities.py` consumes both mapping-mode result sets after the paired trees finish. A candidate gets the strict automatic sample-tip promotion route only when all of the following hold in **both BWA and BLASTx**, in both its single-candidate and joint-candidate scenario:

- concatenated shared-294-tip RF = 0;
- the existing same-taxon baseline tip is among the nearest baseline neighbours of the candidate;
- source-label ASTRAL shared-species RF = 0.

If any check fails, the script returns `manual_review_required=true`; it does **not** relax an RF threshold or alter the locus gate automatically. This conservative rule distinguishes safe replicate enrichment from a candidate that changes the inferred backbone enough to require biological interpretation.

## Execution bundles

`analysis/build_east_asia_public_augmentation_hpc_bundle.py` builds the paired-tree augmentation stage. `analysis/build_east_asia_public_full_hpc_handoff.py` then combines that stage with the validated 294-tip v2 baseline bundle and adds:

- EA01/EA02 public-read fetch for candidate BLASTx sensitivity;
- candidate HybPiper/BLASTx recovery and strict pack rebuilding;
- mapping-aware paired-input preparation;
- a **single Slurm orchestrator** for the complete SRA augmentation analysis.

The full orchestrator submits the following dependency graph:

1. prepare the frozen Compositae1061 reference/locus universe;
2. download/trim the 295 baseline SRRs **once**;
3. branch the same baseline reads into 294-tip BWA and BLASTx HybPiper recovery;
4. fetch the two extra candidate SRRs and run their fresh BLASTx recovery in parallel;
5. run mode-specific QC, locus admission, MAFFT, gene-tree IQ-TREE, concatenated IQ-TREE, ASTRAL and baseline acceptance;
6. run `baseline294`, `ea01_295`, `ea02_295`, `ea01_ea02_296` under BWA and BLASTx, with strict pairing inside each mapping mode;
7. evaluate shared-backbone RF and same-taxon neighbourhoods;
8. write the final `cross_mapping_sensitivity_summary.json`.

After building the full handoff, the intended HPC entry point is:

```bash
export REPO_ROOT=/path/to/EAzami
bash /path/to/full_handoff/submit_full_public_tree_and_augmentation.sh
```

Optional `RESULT_ROOT` and `AUGMENT_ROOT` environment variables redirect large outputs to scratch storage.

The heavy read recovery/tree inference remains an HPC/large-memory-local task. GitHub Actions validates real artifacts, manifests, generated bundles, decision logic, and shell/Python contracts rather than serving as the heavy phylogenomics runner.

## Current boundary

Within this **EA01/EA02 public-SRA gate**, the candidate sample-level ceiling is **296 tips**: 294 baseline + EA01 + EA02. Both candidates duplicate analysis taxon labels already present in the 294-tip baseline, so this gate adds **0 new taxon labels**. The 296 state is a replicate-enriched candidate tree, not a final accepted primary tree.

Across all currently ready public augmentation sources, the separate natural-Ulleung genome candidate adds a third possible biological sample. Therefore the broader current public candidate ceiling is **297 tips if all independent gates pass**, still with 0 new analysis taxon labels. That broader 297 state is also not yet an accepted combined tree; it requires an explicit common paired-locus contract after independent admissions.

The remaining empirical blocker for this SRA gate is execution of the validated full HPC handoff. Once both baseline mapping modes, candidate BLASTx packs, paired trees and the cross-mapping sensitivity summary complete, EA01/EA02 can either be automatically admitted under the frozen exact-backbone rule or sent to manual biological review without changing thresholds.

New China sampling remains deliberately unfrozen.
