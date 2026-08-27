# Meta-analysis and simulation disposition v1

Purpose: preserve existing EAzami work without letting material that answers a different question obscure the Chapter 2 phenotype × time estimand.

Canonical routing table: `data/evidence/chapter2_analysis_disposition_v1.csv`.

## 1. Chapter 2 main paper: keep only evidence that directly locates phenotype in evolutionary history

Main-text material:

- accepted Japan38 nuclear tree and topology uncertainty;
- Japanese origin/radiation context;
- large phenotype disparity within the dominant radiation;
- orientation repeated history;
- phyllary-posture repeated history;
- stickiness repeated history;
- updated cross-trait historical-overlap diagnostic;
- continuous-colour phylogenetic analysis and the source-balanced negative replication;
- new all-18 continuous-trait phylogenetic structure/history analysis.

The core Chapter 2 question is not whether a phenotype is functional. It is whether the same continuous phenotype dimensions defined in Chapter 1 show different degrees of phylogenetic conservatism, recurrence and historical coupling.

## 2. Chapter 2 Supplement

### Japanese colonization evidence ledger

The origin meta-analysis is valuable but should not dominate the main results. Main text needs the conclusion — one dominant Pleistocene radiation with rare exceptions — while accession-level evidence, independent-data-generation accounting and alternative origin models belong in Supplement.

### Absolute-time calibration audit

The failed/blocked chronogram work from PR #92 is useful as a transparent limitation. It shows why the current Comp1061 branch lengths remain substitutions/site and why absolute Ma transition timing is not forced. This belongs in Supplement rather than being silently omitted.

### FDT3 cross-plant repeated-evolution synthesis

If completed with a defensible event-level dataset, FDT3 can serve as an external benchmark for whether recurrence observed in Cirsium is unusual or typical. It is not required for the core Cirsium history paper and must not delay it.

## 3. Route current covariance simulations back toward Chapter 1 Supplement / thesis methods

The existing v3/v4 programme — including v3.1, `NULL_COUPLED`, held-out 0/64 failure, among-only process diagnostics and provisional v4.1 scale-specific covariance — does **not** use evolutionary branches or transition history.

It asks:

> Which statistical covariance architecture can reproduce the observed present-day within/among phenotype field?

That question is a structural robustness extension of Chapter 1, not the primary estimand of Chapter 2.

Disposition:

- v3.1 mechanism-family gap → Chapter 1 Supplement;
- PR #119 scalar `NULL_COUPLED` winner → Chapter 1 Supplement;
- PR #120 held-out 0/64 falsification → Chapter 1 Supplement;
- PR #123 among-only process improvement but inadequacy → Chapter 1 Supplement;
- draft PR #122 v4.1 scale-specific covariance → retain as provisional; only use in Supplement or thesis synthesis after independent held-out validation.

This preserves the important non-identifiability result without relabelling present-state covariance generation as evolutionary history.

## 4. Move functional meta-analysis to the next function/fitness chapter

The following are scientifically strong but answer `phenotype × function/fitness`, not `phenotype × time`:

- direct Cirsium reproductive-herbivory meta-analysis, RR 2.674;
- pollinator × antagonist selection-mosaic synthesis;
- selection-leverage meta-analysis;
- demographic transmission gate;
- display trade-off evidence;
- orientation functional calibration;
- stickiness benefit/null/cost comparison;
- phyllary/protective-envelope analog evidence.

These should become the empirical/literature foundation of the next chapter asking **why particular phenotypes matter**, rather than being reduced to a large Chapter 2 supplement.

Chapter 2 Discussion may briefly use them to motivate candidate explanations, but no functional meta result is required to establish the historical pattern.

## 5. Separate phenotypic disparity-through-time from functional disparity-through-time

The existing FDT5 design is explicitly **functional** disparity through time and depends on a literature-derived trait → function matrix.

For the revised Chapter 2, first implement:

> continuous phenotype → phylogeny → phenotypic disparity through relative evolutionary history.

This uses the measured Azami phenotype directly and remains independent of functional assumptions.

Functional DTT can then move to the next function chapter or a later synthesis after function loadings are validated.

## 6. Distinguish two kinds of simulation

### Existing v3/v4 covariance simulations

Present-state statistical architecture only → Chapter 1 Supplement / synthesis.

### Planned FDT7 evolutionary simulations

Potentially true historical model discrimination because they would use an empirical tree, trait histories, niche histories and transition/event summaries.

These can become Chapter 2 Supplement or thesis synthesis **only after** the empirical continuous-trait histories are frozen. They must not be used to manufacture the historical pattern they are meant to explain.

## 7. Downstream chapter flow

A clean dissertation progression is now:

```text
Chapter 1 — phenotype × space/environment
    continuous phenomics, within/among variation, geography, environment

Chapter 2 — phenotype × evolutionary time/history
    phylogenetic signal, ancestral/branch change, recurrence, historical coupling, phenotypic DTT

Next chapter — phenotype × function/fitness
    meta-analysis, manipulation, selection mosaic, antagonist/pollinator/abiotic pathways

Later empirical/history extension
    nuclear population ancestry + plastid + cytotype → origin of repeated states

Synthesis
    niche/event correspondence, evolutionary simulation, functional/adaptive convergence
```

This arrangement keeps every major EAzami result but restores one question per chapter.
