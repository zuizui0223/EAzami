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



## Frozen cross-study source-join progression (2026-10-24)

These are real molecular-source ↔ independently documented botanical-state
**coverage counts**, not CTMC reconstructions or statistically independent
biological replicate counts:

| Audit | Source molecular units | Exact evidence-name matches | Candidate U/D | Source-name holds |
| --- | ---: | ---: | ---: | ---: |
| Initial 20-tip East Asian source crosswalk | 256 Moreyra labels | 7 | 5 (3 U, 2 D) | Not separated |
| Multi-Flora world source census | 256 Moreyra labels | 41 | 30 (23 U, 7 D) | Not all resolved |
| Unified Moreyra+Chang public nuclear panel | 294 BioSamples, 270 source taxon labels | Taxon-specific from six-plus-one frozen tables | 42 labels (29 U, 13 D), covering 61 samples | 15 sample name-review holds |
| Unified panel, names not flagged by molecular source audit | 294 original BioSamples retained | Same exact source evidence | **35 labels** (24 U, 11 D), covering **46 samples** (30 U, 16 D) | 0 among this subset |

Scripts and reproducible source files:

- analysis/audit_global_nuclear_orientation_multisource_v2.py
- analysis/audit_global_nuclear_294_orientation_join_v3.py
- data/evidence/global_fna_head_orientation_evidence_v1.csv
- tests/test_global_orientation_multisource_join_v2.py
- tests/test_global_nuclear_294_orientation_join_v3.py

The North American Flora of North America source extension is explicit about
the flowering heads: *Cirsium vinaceum* has nodding heads; *C. ownbeyi*,
*C. flodmanii*, and *C. longistylum* have erect heads. *C. eatonii*
and *C. joannae* explicitly include **erect or nodding** heads and remain
ambiguous. The wording of stems or phyllary spines is never substituted for
head orientation. The exact FNA treatment URLs and short source clauses are
in the six-row evidence CSV. These records improve geographic coverage;
they do not establish worldwide representativeness.

The 294-BioSample manifest comes from the existing validated
build_japan_origin_global_public_panel_v2.py and preserves all
**eight cross-paper reused Chang BioSamples as single samples**.
Source-identified multiple BioSamples for the same botanical label
must not be counted as independent evolutionary origins. Nuclear-tree tips
and accepted taxon concepts remain different scientific units; no
one-to-one phylogenetic phenotype matching is claimed simply from
taxon-name agreement.

After name-review filtering, **35** botanical taxon label candidates remain;
they still require accepted-taxonomy decisions, independent U/D
trait-state validation, environmental occurrence provenance, source-sampling
balance and an independent branch-length-bearing global nuclear tree.
All 294 molecular records retain explicit provenance and exclusion status,
including the 15 name-review sample holds. Source name-review "false"
does **not** mean same-voucher phenotype or validated accepted taxonomy.

### Verified CI receipts

- Source join to 256 Moreyra labels: GitHub Actions run 40086814643 (success).
- Global 294-BioSample deduplicated source join: GitHub Actions runs
  40087087446 and 40087285065 (success).
- Result artifacts include a 294-row per-BioSample CSV, 270-row
  per-label CSV and JSON count/limitation receipts. These are
  **candidate metadata only**.

### Next empirical gate

The primary blocker has moved from "no machine-readable phenotypes at all"
to the **global nuclear-tree input** and independent, geographically
representative **nuclear tip ↔ accepted taxon ↔ U/D ↔ BIO15/BIO1** join.
In particular, no source here licenses grafting a synthetic global nuclear
tree or extrapolating the East-Asian CTMC statistic to worldwide lineages.
Any eventual global sign must be assessed against regional/phylogenetic
sampling nulls and withheld-area sensitivity, and should be considered
exploratory if the state support comes predominantly from East Asia.

## Prioritized source read acquisition and geography (October 24, 2026)

A reproducible reduced **read-acquisition** manifest now exists at:

- analysis/build_global_orientation_nuclear_priority_intake_v1.py
- tests/test_global_orientation_nuclear_priority_intake_v1.py

Executed on the real 294-BioSample Moreyra+Chang panel, it retains 35 nuclear-source-name-clean U/D labels (24 U, 11 D), covering **46 molecular BioSamples**, and adds **48 taxon-distinct, trait-blind geographic anchor BioSamples** (12 each for four source-locality buckets). The **94-sample wave** retains the stable IDs used by the original full 294-panel builder: JOG0001..JOG0294 numbering is never reassigned by subsetting.

The source-only analysis detects a critical geographic caveat:

- 23 of the 35 source-name-clean U/D labels were assigned to East/Northeast Asia from the available source locality;
- 4 were assigned to North America;
- 8 retained **Other/unresolved** because the original country/locality text did not satisfy the strict geography parser;
- zero clean labels were classified as West Palearctic by the recorded locality parser.

The 48 trait-blind anchor specimens broaden *molecular placement coverage* but do not provide U/D phenotypes. They cannot repair the state-replication gap in Western Palearctic taxa or establish global generality. The East-Asian discovery sample remains the dominant region and is **not** an independent worldwide replication. Unresolved geography is not evidence that specimens are biologically outside East Asia.

The workflow persists:

- full 294-JOG-ID BioSample lookup with accession/run provenance;
- 94-BioSample priority-wave TSV for staged read acquisition;
- explicitly **unresolved** 294-tip future trait/climate join skeleton;
- SHA256 fingerprint over 35 taxon-name/U-D source pairs fixed **before opening climate**.

**No FASTQ was downloaded by the pilot builder and no tree was inferred.** This prioritized manifest can feed the existing HPC pipeline when compute/storage capacity is provisioned. Any reduced-tree screen must be rooted, locus-QC'd and checked for missing geographic lineage context; a 94-tip topology cannot be treated as the published 294-tip global nuclear tree.

## Independent global GBIF point-coverage gate

analysis/audit_global_orientation_gbif_point_coverage_v1.py implements a **climate-blind**, source-exact GBIF occurrence preflight for the 35-label frozen cohort. The script checks GBIF name matches and source scientificName identity, coordinate accuracy <=10 km, invalid geospatial issue flags, duplicate exact coordinates, and 0.1-degree spatial thinning. It labels incompletely paginated requests as censored. The first 500 records per taxon provide bounded **coverage information**, not necessarily full realized niches. Retained points preserve GBIF occurrence IDs, dataset IDs and license fields.

No native-versus-introduced range filtering, historical branch climate, CHELSA extraction or climate-associated inference is performed by this gate. Those stages remain blocked until accepted-taxonomy, source balance and global nuclear phylogeny are validated.

## Executed global GBIF point-coverage snapshot

The 35-taxon input list was frozen by the SHA256 fingerprint
6ebc890a28c622509292ef6adaa528864504aae9383b694252bda7037696d4f1
*before* the October 24 live GBIF query. The real query was executed
successfully in GitHub Actions run 40095787620 (artifact 12560318301;
sha256:800cca0bff1781ccacd0c53c62740a7d3ac10f730b6df49b0ca3b1795bdbb933).

The source-only results are:

| Criterion | Observed |
| --- | ---: |
| Source names submitted | 35 (U=24, D=11) |
| Exact GBIF name matches | 33 |
| Coordinate-bearing records fetched before cap | 9,592 |
| Records with original scientificName matching source | 8,550 |
| QC + exact-coordinate and 0.1-degree thinned source records | 1,011 |
| >=5 distinct grid cells, including censored searches | 26 taxa (19 U, 7 D) |
| >=5 grid cells with the source result completely enumerated | 16 taxa (11 U, 5 D) |
| Searches truncated at first 500 records | 11 taxa |

The frozen reproducibility receipts are:

- data/evidence/global_orientation_35taxon_gbif_source_gate_receipt_20261024.json
- analysis/audit_global_orientation_gbif_point_coverage_v1.py
- tests/test_global_orientation_gbif_point_coverage_v1.py

The GitHub Action retains the 35-taxon by-source QC CSV and 1,011
source-exact coordinate cells as a time-limited archived artifact.
The observed summary and per-taxon counts are also committed to the
repository, so the result is not silently replaced by new GBIF records.

**These are not native-range-filtered, taxon-balanced climate centroids.**
Eleven queries are right-censored for occurrence retrieval, two taxon
keys were not exact, and the available source records reflect observer
effort, species prevalence, invasions and uneven geographic coverage.
No new climate coefficient, climate response, or evolutionary result
may be claimed from this coverage gate.

## Prospective independent Western Palearctic extension (separate v2 cohort)

A separate botanically source-backed extension was frozen **without
editing the original 35 taxa or opening their new climate outcomes**:

- *Cirsium erisithales*: nodding heads (**D**), World Flora Online
  morphological account; Moreyra exact taxon label, but the nuclear
  plant was documented from a botanical garden.
- *C. oleraceum*: erect heads (**U**), Austrian Burgenland Flora;
  Moreyra exact taxon name.
- *C. eriophorum*: erect heads (**U**), Tofts (1999), *Journal of Ecology*;
  molecular source's submitted scientific-name discrepancy requires
  manual taxonomic review. The British morphological account also
  cannot automatically validate the sequenced Spanish voucher.

Source and executed validator:

- data/evidence/global_west_palearctic_head_orientation_external_v2.csv
- analysis/audit_global_west_palearctic_orientation_extension_v2.py
- tests/test_global_west_palearctic_orientation_extension_v2.py
- GitHub Actions run 40096368252 (success)

Of three exact Moreyra tree-code matches, **two** pass the current
source-name-review screen (one U, one D) and one remains held. These
are *prospective independent external-source records*, not a
posthoc change to the October 24 35-taxon GBIF cohort. If the
additional two pass all subsequent orthology, taxonomy and sampling
gates, the pre-climate name-clean evidence roster could expand
to 37 taxon labels (25 U, 12 D); that is NOT yet an accepted inference
cohort or a new historical transition.

## Completed independent North American REAL nuclear-tree + U/D × niche analysis (2026-10-24)

**Successful primary execution:** GitHub Actions [run 40100026609](https://github.com/zuizui0223/EAzami/actions/runs/40100026609), artifact [12562755175](https://github.com/zuizui0223/EAzami/actions/runs/40100026609/artifacts/12562755175), ZIP SHA256 `86f3c9d329a8394a4f9080b3cf3f304eaba2d84c606fc39821a8306d8f39f8f4`.

**Original independent nuclear and botanical data:** Siniscalchi, Ackerfield & Folk (2023), *International Journal of Plant Sciences*, DOI [10.1086/724310](https://doi.org/10.1086/724310). We accessed the authors' original [data repository](https://github.com/carol-siniscalchi/cirsium) at immutable commit `c925d4af86160064448f794a9715f70b917a2786` and validated the Git object hashes of their published **63-tip calibrated Compositae1061 nuclear tree**, complete `traits.csv`, original R morphology coding key and source BIOCLIM environment table. All 63 tip names join exactly.

The original trait categories contain 58 erect and 5 pendent heads; four **minimum** Fitch steps for orientation and 12 for the four-level corolla-colour character. Flower colour's main source class (code 2; 50 tips) **merges white, pink and purple** and cannot establish white-loss or colour-regain counts.

After holding out source outgroup *C. vulgare*, we ran the unchanged prespecified East-Asian `+BIO15/-BIO1` axis against published North American nuclear topology and source-specific taxon climate centroids, using conditional Mk exact **edge endpoint** joint probabilities and Brownian reconstruction of **modern** niche means. A second fit excluded *C. eatonii* and *C. joannae*, which Flora of North America explicitly describes as **erect or nodding** despite the original authors' single upright labels.

| True empirical model outcome | Published author code | Ambiguous two taxa excluded |
| --- | ---: | ---: |
| Independently published NA nuclear tree tips for source regression | 62 | 60 |
| State counts | U 57, D 5 | U 55, D 5 |
| Signed reconstructed contemporary BIO15 axis | +0.6370 | +0.6199 |
| Signed reconstructed contemporary BIO1 axis | **+0.0646** | **+0.0594** |
| Fixed +BIO15/-BIO1 composite | **+0.4048** | **+0.3963** |
| 999 global fixed-count tip-map null tests, one-sided p | **0.016** | **0.022** |
| Symmetric Mk q per calibration Myr (model-conditional) | 0.05361 | 0.05545 |

**Interpretation:** The preregistered **composite direction** is positive in this geographically independent nuclear dataset and stays positive after excluding the two mixed-head species. The independently reconstructed **BIO1 component does not show the expected negative branchwise sign**: it is slightly positive. This is therefore mainly a **precipitation-seasonality-linked** component association, not robust confirmation of a historical cooler-when-nodding directional mechanism. In simple original author source means (nonphylogenetic), D taxa have higher BIO15 (55.20 vs 39.54) and lower BIO1 (68.22 vs 76.40, as stored in the source's units). These different estimands must not be collapsed.

The reported one-sided p-values are 999 **fixed-D-count tip-label** Monte Carlo permutations within North America: this null is **not a full phylogenetic+spatial process-based null**. Five D tips, taxonomic/morphological context, external data coding, published molecular dating uncertainties and historical geography limit claims. No climate at a transition event was measured, and `P(parent U, child D)` is not probability of a specific dated state-change event.

The 63-tip annotated figure combines the **original molecular tree** with original source head position, corolla colour, glutinous ridge and phyllary position, labelled with the exact author categories. It is a separate validated North American tree **not a manually grafted world tree**. Moreyra et al. (2025)'s exact full-world 350-nuclear-locus Newick remains unrecovered and EAzami's 294-sample nuclear inference remains unexecuted.

**Reproducibility:**

- `analysis/run_siniscalchi_2023_real_nuclear_traits_v1.py`
- `analysis/run_global_nuclear_orientation_transition_niche_v1.py` (now also explicitly accepts calibrated-Myr branch lengths)
- `analysis/summarize_siniscalchi_2023_independent_na_u2d_v1.py`
- `tests/test_siniscalchi_2023_real_nuclear_traits_v1.py`
- `.github/workflows/real-siniscalchi-nuclear-u2d-v1.yml`
- `data/evidence/independent_north_america_2023_real_nuclear_u2d_result_20261024.json`


## Completed all-nine-character phylogram (original North American source)

All nine original categorical traits from Siniscalchi et al. (2023) have now
been mapped to **the same real 63-tip published calibrated nuclear tree**.
This reuses the previously authenticated original tree/trait tables and
author-published numeric codebook without adding placements or guessing
additional taxon states.

GitHub Actions [run 40100757609](https://github.com/zuizui0223/EAzami/actions/runs/40100757609) passed all source/state/figure tests. The
[complete nine-trait figure artifact](https://github.com/zuizui0223/EAzami/actions/runs/40100757609/artifacts/12562219896)
contains zoomable SVG, PNG, exact original numeric code legend and audit JSON.

| Original author's trait (character) | Source states | Fitch minimum steps |
| --- | --- | ---: |
| CorollaThroat | 0/1 | 4 |
| CorollaColor | red / red-purple / **white-pink-purple combined** / yellow | **12** |
| Duration | perennial / biennial | 14 |
| GlutinousRidge | absent / present | 11 |
| Habit | caulescent / acaulescent | 3 |
| HeadPosition | U erect / D pendent | **4** |
| InnerPhyllaryColor | green / purple / red / pink | 12 |
| OuterPhyllaryPosition | ascending / spreading / reflexed | 14 |
| StyleBranchColor | red / reddish-purple / white-pink-purple combined / yellow | 10 |

These are **lower bounds** on category transitions **on one source tree**;
they cannot estimate exact historical transition numbers, dates or directions.
Their differences support the decision to model **separate morphological
components**, not to force the whole capitulum into one evolutionary state.
All categorical codes are linked to the original authors' R legend.

Reproducibility:

- `analysis/render_siniscalchi_2023_nine_traits_v1.py`
- `tests/test_siniscalchi_2023_nine_traits_v1.py`
- `.github/workflows/render-siniscalchi-2023-nine-trait-tree-v1.yml`
- `data/evidence/independent_na_nuclear_nine_trait_parsimony_20261024.json`

The complete 350-locus Moreyra 2025 worldwide nuclear Newick is **still
not available in EAzami**. Do not merge dated North American and undated
Japanese/East-Asian trees by hand into a false worldwide molecular tree.

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
