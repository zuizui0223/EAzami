# Global nuclear U→D × branchwise climate workflow v1

**Status:** executable **synthetic-tested methods**, not a global empirical result. Separate from the frozen EAzami Chapter 2 JEB V10 manuscript and Azami Chapter 1 GEB v3.

## Target

Test whether **independently observed worldwide** upward/erect (U) versus downward/nodding (D) capitulum states have a phylogenetically distributed association with the **frozen** environmental vector **(+BIO15, −BIO1)**. This is an out-of-sample test of an East-Asian *present-niche* association, not a test of historical selective causes.

The East-Asian design is implemented at:

- analysis/run_chapter2_orientation_transition_regime_hypothesis_v1.py
- data/evidence/chapter2_orientation_transition_regime_hypothesis_result_v1.json
- docs/chapter2/ORIENTATION_TRANSITION_REGIME_ROBUSTNESS_V1.md

East-Asian boundary to preserve:

- 12 taxa, 6 nuclear topologies: composite rank 16/792 (2.02%);
- strict 9 taxa: 4/126 (3.17%);
- Japan-only 8 taxa: 10/56 (17.86%), **not** supported;
- historic regime congruence for the sole bounded event: 99/376 (26.3%);
- no inference that BIO15, BIO1, or rainfall *caused* U→D.

## Observed readiness

- Moreyra/Chang all-public source registry: **294 deduplicated biological samples, 295 SRRs, 270 source-preserving taxon labels**. These are **not** all shape-scored accepted species, nor are they yet a shared phylogenetic tip panel.
- The 302-tipped global common-locus builder counts source samples plus references, **not 302 independent resolved floral species**.
- The complete real-data, branch-length-bearing **global nuclear tree ensemble has not passed the source/QC/placement gate** and is not a repository-frozen validated input.
- A worldwide **accepted-taxonomy + specimen ↔ nuclear-tip + observed U/D + independent modern BIO15/BIO1 centroid** one-row-per-taxon join remains unavailable.
- A worldwide **dated-tree + palaeolocation + period-specific palaeoclimate** branch table remains unavailable.

Thus no worldwide transition-effect size, p value or global historical climate interpretation is reported. The Python runner fails closed when inputs are incomplete.

### First executed real-source join gate

The reproducible exact-label source-overlap audit lives at
analysis/audit_global_nuclear_orientation_source_overlap_v1.py. It compares
the eight frozen Moreyra 2025 sample reconciliation parts to the **20-tip
East-Asian authority/literature orientation crosswalk**, **not** to a complete
worldwide botanical traits dataset.

The current direct-match inventory is:

- 257 linked nuclear-source rows, representing 256 distinct BioSamples and 256 distinct Moreyra tree-code labels after source conflict exclusion;
- 7 exact tree-code ↔ accepted-taxon label matches;
- 5 exact labels with source-backed U/D states (U=3; D=2);
- 2 of the seven label matches explicitly retain unresolved state;
- 249 source labels are not represented in **this small East-Asian crosswalk**. This is **not evidence that those taxa lack botanical descriptions or cannot be scored worldwide**.

No synonym guesses, extrapolation to global trait prevalence, or pseudo-label imputation were performed.
The source-overlap audit blocks inference and identifies independent worldwide
orientation coding and taxonomic reconciliation as the next gating work.

Run directly:

~~~bash
python analysis/audit_global_nuclear_orientation_source_overlap_v1.py \
  --outdir results/global_source_overlap_v1
~~~


## Input contract

A UTF-8 CSV with one row per *nuclear tree tip* (including explicitly excluded/unresolved ingroup tips); required columns:

| Column | Meaning |
| --- | --- |
| tip_id | Unique Newick-safe molecular specimen ID; exact match to tree leaf |
| accepted_taxon | Resolved taxonomic concept; **only one included nuclear representative per accepted taxon** |
| orientation_state | U, D, or unresolved; use published or independently verified morphological state |
| bio15 | Mean present precipitation seasonality of independently QC'd occurrences for that taxon |
| bio1 | Mean present annual temperature of independently QC'd occurrences for that taxon |
| biogeographic_region | Preassigned region for the restricted null permutation |
| orientation_source | Exact provenance for the state; do not use unverified species knowledge as independent confirmation |
| climate_source | Provenance, environmental dataset version, sampling and geographic QC |
| exclusion_reason | Required for unresolved tips; empty for included tips |

Important: include **unresolved** tips explicitly in the CSV with exclusion_reason, not silently removed from the tree. Do not code unassessable as U, D, or absence. If a species is polymorphic, retain that fact and exclude it from this species-tip pilot until a population-aware model is used. Ensure continent/lineage coverage and geography/sample-size are independently audited.

Tree file: **one positive-branch-length nuclear Newick per line**, identical specimen-tip roster to the CSV **plus one explicit outgroup tip** (specified by CLI). Branch lengths are substitutions/site; these are not dated changes per Myr. Each tree is rooted using the supplied outgroup, and excluded tips are removed under the documented mask. Do not use the Azami 52 historical-placement/grafted sensitivity trees as though they were a measured, coherent worldwide nuclear ensemble.

## Estimator

For each accepted rooted nuclear tree:

1. Fit a **symmetric two-state continuous-time Markov model (ER CTMC)** to U/D leaf labels; root prior P(U)=P(D)=0.5.
2. Compute the **exact joint posterior for parent and child states**, conditional on all tip states. On edge e, report **P(parent U, child D)** and **P(parent D, child U)** separately.
3. Standardize modern taxon BIO15 and BIO1 niche centroids across the fixed tip panel, and reconstruct their internal-node values by Brownian squared-change minimization using the **same nuclear substitution branch lengths**.
4. For each edge, compute reconstructed niche shifts ΔzBIO15 and ΔzBIO1. These are **not observed climatic changes during that ancestral branch**.
5. Calculate the fixed-direction statistic:

   S = Σ_e {[P_e(U,D) − P_e(D,U)] × [Δ_e(zBIO15) − Δ_e(zBIO1)]} / {√2 × Σ_e [P_e(U,D)+P_e(D,U)]}.

6. Use the **median S over all eligible trees**, not the best tree. Test against count-preserving reassignment of U/D states within **predeclared biogeographic regions**. Enumerate every map if the state-map space has at most 3,000 elements, or use fixed-seed Monte Carlo otherwise.
7. Report both observed and null distributions and every edge's conditional posterior. No transition age, rate-per-Myr, or climate cause is inferred.

### Why endpoint posteriors are not transition counts

P(parent U, child D) is the *posterior probability of discordant endpoint states*, not the probability that exactly one transition happened somewhere along that branch; a CTMC can undergo hidden multiple changes. For actual counts/timings, separately perform stochastic mapping integrating over fitted rates and branch lengths. The denominator above is **endpoint discordance posterior mass**, not a count of all historical events.

### Why the world analysis is not simply the East-Asian result at larger n

Global tree coverage, regional sampling, provenance of U/D states, model stability, phylogenetic signal and Brownian climate reconstruction all change. Regional constrained nulls are a guard against the most obvious geographic-composition confounding, **not** proof of full spatial/phylogenetic null control. If one region has only one state, its members cannot be permuted under that restricted null: document this loss of effective null variation. Fit and compare asymmetric-rate models (ARD), region-deletion, independent species coding and alternative reconstructions **as prespecified sensitivity extensions**, not opportunistic tuning after seeing the fixed test.

## Invocation once the real data gates pass

~~~bash
python analysis/run_global_nuclear_orientation_transition_niche_v1.py \
  --trees private_inputs/frozen_global_nuclear_ensemble.nwk \
  --tip-table private_inputs/global_nuclear_u_d_bio15_bio1_join.csv \
  --outgroup OUTGROUP_lett \
  --permutation-strata region \
  --permutations 999 \
  --min-taxa 20 \
  --seed 2317 \
  --outdir results/global_u2d_nuclear_climate_v1
~~~

The example paths are **required future inputs, not present files**. The actual outgroup must be present in *every* global tree and identified by a source-backed rooting contract. The metadata cannot be backfilled by copying East-Asian model predictions.

Output: result.json, edge_joint_posteriors.csv, permutation_scores.csv, input_join_audit.csv, with SHA256s for the two input files and explicit scientific limits.

## Separate historical-origin follow-up (not implemented as an empirical result)

To test **climate change on an ancestral branch at the event time**, additionally require:

1. Independently estimated **dated** nuclear topology ensemble with calibrations and credible intervals;
2. Ancestral-geography/palaeolocation distributions rather than descendant coordinates;
3. Climate trajectories from palaeoclimate time slices covering each parent–child interval;
4. A model of time-heterogeneous transition hazard versus climate *including no-change edge exposure and uncertainty*;
5. A shift-on-branch sensitivity that samples transition times through stochastic mapping; compare alternative age/location and climate realizations.

Never relabel the present-tip Brownian reconstruction as measured historic ΔBIO15/ΔBIO1. The East-Asian bounded historical-envelope result warns precisely against that projection.

## Reproduction test

~~~bash
python -m pip install numpy scipy pandas biopython
python -m unittest discover -s tests -p 'test_global_orientation_transition_niche_v1.py' -v
~~~

These tests assert edge posterior validity, exact permutations, explicit provenance, rooting/branch-length integrity and failure on missing taxa/duplicate species/unsupported U/D labels. **Passing them validates the implementation contract, not an empirical global ecological conclusion.**
