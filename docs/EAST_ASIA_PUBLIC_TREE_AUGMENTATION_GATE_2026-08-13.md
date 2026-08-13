# East Asia public nuclear-tree augmentation gate — 2026-08-13

## Purpose

Continue the public-data-only maximum nuclear phylogeny before defining any new China field-sampling list. The baseline remains the deduplicated Japan-origin global panel v2: **294 unique biological tips / 295 unique public SRRs**. Japan-38 membership is provenance/sensitivity metadata, not a topology constraint.

## Public SRA pilot result now frozen in-repo

Successful workflow run `31684233834` recovered the five audited East Asian candidates against the frozen Compositae1061 241-locus universe after fixing the HybPiper `paralog_report.tsv` path contract.

- EA01 — `PUBEA001`, *Cirsium nipponicum var. yoshinoi*: **236/241 strict no-warning loci**, pilot-ready.
- EA02 — `PUBEA002`, *Cirsium sairamense*: **239/241 strict no-warning loci**, pilot-ready.
- EA03 — *C. japonicum* var. *spinossimum*: **0/241**, not pilot-ready.
- EA04 — *C. setidens*: **0/241**, not pilot-ready.
- EA05 — *C. japonicum* var. *ussuriense*: **0/241**, not pilot-ready.

EA01's strict locus set is a complete subset of EA02's; their candidate-only joint set is therefore **236 loci**. EA03–EA05 are not carried forward under the present Compositae1061 admission rule. Their workflow success is retained as evidence that the zero-locus outcome is a data/recovery result rather than a pipeline crash.

Machine-readable evidence is `data/evidence/east_asia_public_sra_comp1061_pilot_results_2026-08-13.csv`. Artifact IDs and SHA256 digests are frozen there.

## Baseline taxon reconciliation

Both successful candidates duplicate analysis taxon labels already present in the 294-tip baseline.

- EA01 is an independent *C. nipponicum* var. *yoshinoi* sample. The baseline Moreyra sample is `SAMN44017955` / `SRR30887222`.
- EA02 is an independent cross-study *C. sairamense* sample. The baseline Moreyra sample is `SAMN34240330` / `SRR25265647`, with the published locality `Tajikistan: Maijora`.

Thus the pilot adds potentially useful biological replicates and cross-study placement tests, but **adds zero new analysis taxon labels** to the 294-tip baseline.

## Paired-tree rule

No candidate is promoted from locus recovery alone. The next tree stage uses four scenarios:

1. `baseline294`
2. `ea01_295`
3. `ea02_295`
4. `ea01_ea02_296`

Within each mapping mode, all four use the exact same locus list:

`accepted baseline-294 loci for that mapping ∩ EA01 strict loci ∩ EA02 strict loci`.

At least 100 joint paired loci are required separately for BWA and BLASTx. The BWA and BLASTx accepted locus sets are allowed to differ because mapping sensitivity is itself part of the test. No post-hoc filter relaxation is allowed.

EA01 is an independent same-taxon target-capture replicate. Its role is assay/placement replication: it should recover the neighbourhood of the existing *C. nipponicum* var. *yoshinoi* public tip across mapping/tree sensitivities. EA02 is an independent cross-study same-taxon *C. sairamense* replicate, not a new taxon label. It should reproduce the existing *C. sairamense* neighbourhood across BWA and BLASTx concatenated trees and source-label ASTRAL sensitivity.

For every augmented concatenated tree, the 294 shared baseline focal tips are pruned conceptually and their unrooted Robinson–Foulds distance from the paired `baseline294` tree is recorded. RF is a diagnostic, not a loophole: a non-zero value must be interpreted rather than hidden by changing the locus set. The source-label ASTRAL backbone is evaluated separately on the baseline species IDs.

## Frozen cross-mapping promotion gate

`analysis/summarize_east_asia_public_augmentation_sensitivities.py` consumes both mapping-mode result sets after the paired trees finish. A candidate gets the strict automatic sample-tip promotion route only when all of the following hold in **both BWA and BLASTx**, in both its single-candidate and joint-candidate scenario:

- concatenated shared-294-tip RF = 0;
- the existing same-taxon baseline tip is among the nearest baseline neighbours of the candidate;
- source-label ASTRAL shared-species RF = 0.

If any check fails, the script returns `manual_review_required=true`; it does **not** relax an RF threshold or alter the locus gate automatically. This conservative rule distinguishes “safe replicate enrichment” from a candidate that changes the inferred backbone enough to require biological interpretation.

## Execution bundle

`analysis/build_east_asia_public_augmentation_hpc_bundle.py` packages the two successful candidate locus packs with the existing v2 baseline bundle and writes a restartable Slurm stage for:

- paired input preparation;
- MAFFT for all four scenarios;
- per-locus IQ-TREE gene trees;
- concatenated IQ-TREE trees;
- source-label ASTRAL trees;
- concatenated shared-tip RF and candidate-neighbour diagnostics;
- ASTRAL shared-species backbone RF diagnostics;
- frozen cross-mapping promotion summary.

Run the ordinary v2 baseline recovery/tree-input stage first for both `bwa` and `blastx`. Then run `submit_paired_augmentation_chain.sh` once per mapping mode. After both mode-specific evaluation jobs have succeeded, run `16_summarize_cross_mapping_sensitivities_slurm.sh` to generate `cross_mapping_sensitivity_summary.json`.

The heavy read recovery/tree inference remains an HPC/local task. GitHub Actions validates real artifacts, manifests, generated bundles, decision logic, and shell/Python contracts rather than serving as the heavy phylogenomics runner.

## Current boundary

The public-data **sample-level** ceiling supported by the current pilot is **at most 296 tips**, not 299: 294 baseline + EA01 + EA02. However, both admitted candidates duplicate analysis taxon labels already present in the 294-tip baseline, so they add **0 new taxon labels** at this gate. The 296 state is therefore a replicate-enriched candidate tree, not an expansion of unique taxonomic coverage and not a final accepted primary tree.

The remaining empirical blocker is the heavy 294-tip Compositae1061 recovery/tree run itself. This repository change removes the downstream design ambiguity so that, once `tree_bwa/inputs` and `tree_blastx/inputs` exist, the augmentation comparison can start without changing scientific rules.

New China sampling remains deliberately unfrozen.
