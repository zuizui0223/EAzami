# Chang 2026 exact species-tree / posterior-tree recovery audit — 2026-08-12

## Purpose

The Arenicola flower-colour analysis now has a source-backed topology-only parsimony screen and a partial-calibrated Mk sensitivity. The next promotion target is to replace nuisance branch ages and hand-coded topology variants with the **actual Chang et al. (2026) machine-readable trees/posterior trees**.

This note records what is publicly recoverable and prevents the project from treating a figure or textual divergence-time summary as though it were the authors' exact Newick/Nexus output.

Structured registry:

- `data/evidence/chang2026_exact_tree_recovery_audit_v1.csv`

## Public analyses reported by Chang et al. 2026

The final article reports multiple distinct phylogenetic products that must not be conflated:

1. an all-sample ASTRAL species tree from 2,999 retained OG gene trees (Fig. 1A);
2. a Cirsium-focused ASTRAL species tree used for SODA/PTP species delimitation (Fig. 1E);
3. a Cirsium-only Bayesian species-tree analysis used for DensiTree/GMYC (Fig. 1D), using 52 OGs;
4. a divergence-time StarBEAST3/BEAST analysis using 50 OGs (Fig. 2);
5. the underlying posterior tree distributions and RAxML gene-tree sets needed to reproduce uncertainty/discordance.

The open peer-review author response is particularly useful because it resolves an earlier 50-vs-52-locus ambiguity: the **divergence-time analysis used 50 OGs**, while the **Cirsium-only species-delimitation Bayesian analysis used 52 OGs**. The response states that an earlier '52' in the time-tree figure was a typographical error.

## What the final public Data Availability actually provides

During technical revision, the editor explicitly requested a relevant data link and consistency of the Data Availability statement. The authors responded by adding the NCBI BioProject URL and state that raw sequence reads are available under:

- `PRJNA1311153`

The final article retains this SRA-only Data Availability statement. In the final author response, the authors again state that BioProject `PRJNA1311153` is public and that all associated SRA data have been released.

No Newick/Nexus tree archive, BEAST `.trees` posterior, TreeAnnotator MCC file, ASTRAL gene-tree collection, alignment bundle, Dryad/Zenodo/TreeBASE/OSF repository, or author GitHub repository is identified in the final Data Availability text or in the recovered open peer-review responses.

## Supplementary material status

The final BMC page exposes one `Supplementary Material 1` DOCX. The repository's existing recovery audit already extracted its six supplementary tables and 13 supplementary figures. That DOCX does not contain a machine-readable Newick/Nexus tree archive.

Therefore the current status is:

> **exact author tree/posterior artifacts are not publicly recovered; raw reads and partial textual/tree-figure information are public.**

This is a recovery status, not a claim that the authors never retained those files.

## Research Square preprint

The manuscript also has Research Square preprint DOI:

- `10.21203/rs.3.rs-7470174/v1`

Current indexed searches identify the preprint but did not surface a machine-readable Newick/Nexus/BEAST `.trees` attachment. Because Research Square attachment indexing can be incomplete, this is recorded as `preprint_identified_tree_not_recovered`, not as proof that no attachment ever existed.

## Recoverable numerical constraints without the exact tree

The final Results text provides several node-age medians that are usable as **partial calibration constraints**:

- Arenicola + Nipponocirsium split: **1.02 Mya**;
- `C. brevicaule` + `C. irumtiense` MRCA: **~0.93 Mya**;
- `C. morii` versus remaining sampled Nipponocirsium: **~0.79 Mya**.

These are frozen separately in:

- `data/evidence/arenicola_published_node_age_constraints_v1.csv`

Two important caveats apply.

First, the reported marginal HPD intervals overlap strongly and cannot simply be assigned independently as node ages because independent draws can violate ancestor > descendant time order. Second, the Results and Discussion give different HPD ranges for the 1.02-Mya subsection split while retaining the same median. The partial-calibrated analysis therefore uses the printed **medians only** and treats younger unrecovered Nipponocirsium node ages as explicit nuisance grids.

## Current analytical bridge while the exact tree is unavailable

Implemented:

- `analysis/arenicola_colour_history_sensitivity.py` — exact equal-cost parsimony;
- `analysis/arenicola_partial_calibrated_mk_sensitivity.py` — exact two-state Mk internal-state summation using the three published median node ages and explicit nuisance/rate/root-prior grids.

The second analysis is deliberately **not fitted** to estimate loss/regain rates from the six tip states. One binary trait cannot identify `q(C->W)` and `q(W->C)` reliably. Instead it asks whether the loss-vs-regain direction survives plausible rate assumptions.

## Why the exact author tree still matters

The exact files would allow four things that the current bridge cannot:

1. replace nuisance node-age grids with the actual dated topology/branch lengths;
2. propagate the authors' posterior topology/age uncertainty rather than one displayed tree;
3. map the six colour states onto the same taxon-label system used in the published Bayesian analysis;
4. quantify whether candidate loss/regain direction is stable across posterior trees rather than only across hand-declared local resolutions.

Even then, a six-tip colour character alone would not identify a biologically realistic asymmetric transition-rate model. A broader flower-colour atlas remains necessary.

## Exact files to request from the authors

Minimum useful package:

1. all-sample ASTRAL final species tree (Fig. 1A) in Newick;
2. Cirsium ASTRAL tree used for SODA/PTP (Fig. 1E) in Newick;
3. Cirsium-only 52-OG Bayesian MCC tree used for Fig. 1D/GMYC in Nexus/Newick;
4. posterior `.trees` sample underlying the Fig. 1D DensiTree, if shareable;
5. 50-OG dated MCC tree used for Fig. 2 with node heights/HPDs;
6. posterior `.trees`, BEAST XML and `.log` for the 50-OG dated analysis, if shareable;
7. RAxML gene trees supplied to ASTRAL and the retained-locus/taxon mapping;
8. taxon-label ↔ voucher/run mapping used in each tree.

A ready-to-send request is stored in:

- `docs/CHANG2026_TREE_DATA_REQUEST_DRAFT.md`

## Claim boundary

Until one of those machine-readable tree products is actually recovered, EAzami must not describe the partial-calibrated Mk surface as a replication of Chang et al.'s posterior ancestral state. The valid label is:

> **source-informed branch-length/rate sensitivity using published node-age medians, with unrecovered node ages treated as nuisance parameters.**

The independent population/genomic and floral-mechanism gates remain unchanged: a topology or Mk state alone cannot demonstrate molecular anthocyanin reactivation in `C. irumtiense`.
