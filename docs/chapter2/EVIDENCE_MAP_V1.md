# Chapter 2 evidence map v1

This file separates manuscript-grade results from supporting context, pending updates and prohibited interpretations.

## A. Core manuscript evidence — include in main Results

| Evidence layer | Frozen source | Result | Manuscript role | Boundary |
|---|---|---|---|---|
| Azami → EAzami observational handoff | PR #108; `data/evidence/azami_capitulum_space_handoff_report_v1.json`; committed source target CSVs | 62 observational targets; source run 33035785120 / artifact 9632715852 | Defines `P_present` as a reproducible target bundle | Observational/noncausal only |
| Exact 62-estimand adapter | PR #115 | 62/62 estimands regenerable from matching 18D observation schema | Shows empirical present and model output use identical statistics | Same statistic ≠ same causal mechanism |
| Conditional v3 generator interface | PR #118 | 14/14 frozen model families generate 18D phenotype → 62 estimands on the 1,874-row/124-taxon environment design | Makes generative comparison technically commensurate | No target-distance ranking at this stage |
| Preregistered scalar-target one-shot | PR #119; `data/evidence/azami_capitulum_v3_one_shot_decision_v1.json` | `NULL_COUPLED` robust leader; median 2.2133; 16/16 primary ranks first; min paired-win 1.0; min2 also first | Main Result 1: scalar present does not require explicit environment in tested families | Prior-predictive structural sufficiency, not likelihood or “environment absent” |
| Held-out support falsification | PR #120; `data/evidence/azami_capitulum_v3_null_heldout_support_decision_v1.json` | primary 8-cell pattern 0/64; exact 20-cell 0/64; median 14/20 | Main Result 2: scalar winner fails richer hierarchy | Cannot re-rank PR #119 |
| Held-out cell diagnostics | PR #120; `data/evidence/azami_capitulum_v3_null_heldout_support_cell_frequencies_v1.csv` | among omnibus support 6/64 at each threshold; among GSP support 0/64 min5 and 1/64 min2 | Localizes mismatch to among-taxon process support | Binary support geometry, not exact P-value reproduction |
| Post-heldout diagnostic | PR #123; canonical decision/family summary | no adequate family; best `PROCESS_AMONG_ONLY_SHARED_COUPLED`: median 6/8, 6/24 full pattern, 22/24 better than NULL | Main Result 3: among-only direction improves but remains insufficient | Hypothesis-generating; not confirmatory model selection |

## B. Supporting historical bridge — use in main text briefly, details in supplement/thesis

| Evidence | Current support | Use | Do not claim |
|---|---|---|---|
| Japan38 conservative nuclear phylogenomic topology | Comp1061 ML + 1000 UFBoot, frozen tree artifact | Provides realized-history topology ensemble orthogonal to v3 simulation | Exact absolute chronology |
| Orientation history | 20 resolved; ML minimum 6; UFBoot 4–6 | Demonstrates repeated historical state change | 4–6 adaptive convergences |
| Phyllary history | 10 resolved; exactly 3 steps across UFBoot | Demonstrates a second module has a distinct recurrence history | Validated defence module or adaptive transition count |
| Stickiness history | canonical main plus authority extensions | Demonstrates repeated sticky/nonsticky history | Generic positive defence effect |
| Common-lability analysis | no pair consistently positive across branch-length-aware and topology-only layers | Rejects simple one-shared-whole-capitulum lability as a sufficient account | Positive proof of developmental/genetic modularity |

### JPN24 update handling

PR #124 has independently validated an exact-concept NMNS assignment `C. pseudosuffultum = sticky`, producing 13 resolved stickiness concepts, ML = 5, root = sticky and 5 steps in all 1,000 UFBoot trees. Until PR #124 is merged into `main`, the manuscript must either:

1. report the current merged canonical stickiness result, or
2. label the PR #124 result as a validated pending update.

Do not silently mix the pending result into a manuscript claimed to be generated from current `main`.

## C. Next-data evidence — Discussion / thesis bridge, not current Results

### Population ancestry gate

Source: `docs/DOCTORAL_NEXT_DATA_GATE_2026-08-19.md`.

Collect linked per-individual:

- nuclear population-genomic DNA;
- same-individual or tightly matched plastid haplotype;
- flow-cytometry cytotype/genome size;
- voucher-linked standardized phenotype.

Question:

> Are repeated present states generated from ancestral standing variation, introgression/gene flow, or lineage-specific origin?

This is the next realized-history discriminator and should be presented as **future evidence required by the Chapter 2 inverse problem**, not as evidence already available.

### Functional gate

Current literature/meta layer supports candidate functional annotations and strong antagonist fitness costs in harmonizable experiments. It does not yet supply ancestry-linked causal chains for focal capitulum modules. Main Chapter 2 claim stops before adaptation.

Required downstream chain:

`trait → pollinator/antagonist/abiotic pathway → reproductive fitness`.

### Molecular flower-colour gate

The previous Chapter 2 colour-loss/regain plan is retained as a downstream mechanistic subprogram, not the current Chapter 2 core. Public homolog/young-leaf data can establish pathway-retention plausibility but not floral-stage regulation or causal reactivation.

## D. Evidence explicitly excluded from the Chapter 2 main claim

- Absolute-time DTT or transition dating using an unvalidated ~2.4 Ma Japan38 crown calibration.
- Colour anti-phylogenetic rescue after the frozen Japan7 source-balanced failure.
- A claim that current snapshot residual coupling = common evolutionary lability.
- A claim that image trait modules are functional modules without independent evidence.
- A claim that repeated parsimony changes = adaptive convergence.
- A claim that the post-heldout diagnostic identifies GSP as the causal driver.
- A claim that `NULL_COUPLED` is the true historical model.
- A claim that the v3 families exhaust all biologically possible histories.

## E. Manuscript evidence hierarchy

Use this order in writing and figures:

1. **Observed present** — directly reconstructed Azami phenotype/environment structure.
2. **Frozen compression** — 62 exact estimands.
3. **Structural sufficiency** — preregistered prior-predictive comparison.
4. **Independent falsification** — held-out inferential-support geometry.
5. **Post-heldout diagnosis** — directional but exploratory mechanism constraint.
6. **Realized-history evidence** — nuclear topology + trait-state histories.
7. **Next discriminating data** — nuclear population genomics + plastid + cytotype + functional intervention.

Moving a result upward in this hierarchy without new evidence is prohibited.
