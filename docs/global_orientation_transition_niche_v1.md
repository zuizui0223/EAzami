# Global nuclear U→D × branchwise climate workflow v1

> **SOURCE-ID ERRATUM / 2026-10-25 — THIS OVERRIDES EARLIER WORLD53 CLAIMS.**
> The apparent two *Cirsium kamtschaticum* populations `J38S038` and
> `GLB2_SRR30887251_Cirsium_kamtschaticum` are the **same original**
> `SAMN44017865` **BioSample** and `SRR30887251` **molecular run**.
> The original Japanese taxonomic study panel included a **Siberian
> Chukotka/Kamchatka original voucher**, not a second physically Japan-sampled
> *C. kamtschaticum* individual. Two computational read-processing pipelines
> yielded 282 different calls in 46,971 jointly called ACGT positions
> (0.600%), with technical-locus discrepancy up to 74/466 (15.88%)
> in At1g02170. **This is computational pipeline mismatch, not population
> differentiation, reticulation or multiple independent floral origins.**
> Prior 53-tip and same-species-non-sister topology statements are
> **superseded for inference**; original source sequences and logs remain
> archived as transparent historical audit material.
>
> The corrected intake freezes **52 molecular tips** = **51 unique Cirsium
> BioSamples + 1 Carthamus outgroup**, 19 observed U / 8 D / 24 unresolved
> taxon-level head states. The original higher-coverage `J38S038`
> alignment was retained. Under a 40% per-gene ACGT gate on the **12
> unique external samples**, **75 original nuclear loci / 62,810 bp**
> are eligible, selected without reference to flower heads or tree topology.
> **No global 294-tip 350-gene world species tree is complete.**
>
> Frozen evidence: `data/evidence/world53_same_SRR_pseudoreplication_retraction_and52_unique_20261025.json`
> and `analysis/rebuild_world52_unique_biosample_original176_and75_v1.py`.
> The corrected original 52-tip IQ-TREE and original Moreyra S1 model results
> supersede numerical results attributed to the old 53-tip panel when available.

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

### Branch-level caution: the five North American pendent taxa differ

Named molecular-tip endpoint posterior diagnostics from the **executed**
North American source tree are frozen in
`data/evidence/independent_na_nuclear_five_D_edge_diagnostics_20261024.json`.
The five original D-labelled terminal tips have high fitted
`P(parent U, child D)` (0.965–1.000), but their **reconstructed
present-day BIO15** branch deltas are **positive in three** taxa and
**negative in two**. The corresponding BIO1 deltas are positive in two,
negative in three. Consequently the net positive BIO15 composite is
not an invariant rain-seasonality response at every D tip.

Named-tip posterior probabilities are conditional *endpoint state*
distributions under fitted ER Mk, **not proof that exactly five distinct
historical U→D changes occurred on their terminal branches**. Fitch
parsimony's four-step minimum is a different estimand.

**S1 clarification:** Moreyra et al. (2025) Supplementary Table S1
contains nuclear sample/voucher/BioSample provenance; it does **not**
supply the nine categorical head/flower phenotypes. The full nine-trait
dataset reused above is Siniscalchi et al. (2023)'s separate published
`traits.csv` with its own R codebook. The two sources are never
silently treated as one specimen phenotype table.

## Newly inferred REAL transcontinental nuclear Cirsium tree (24 October 2026)

Result now exists: new 67-tip source-voucher nuclear ITS+ETS ML phylogram fitted directly from GenBank nucleotide sequences, NOT grafted from previously made regional trees.

- Primary accession source: Slotta, Horvath & Foley (2012), Plants DOI 10.3390/plants1020061, Table 1, EuropePMC PMC4844267 full-text XML (source SHA256 cbae6a078071f0fa57f0525a260b566e0ab1343494a6850ac8b7423110ec05b0).
- Source DNA pairs: 73 specimens with both ITS and ETS from the SAME original publication row; 143 GenBank accessions queried, 141 sequences recovered.
- Molecular QC admitted **67 specimens** = 65 Cirsium + 2 Carduus outgroup; **46** source genus/species binomials overall (45 Cirsium). Exclusions: four mismatched GenBank descriptions, one cross-species accession conflict, one missing nucleotide sequence pair. No missing sequences were fabricated.
- Real alignment: ITS **759 bp**, ETS **614 bp**, concatenated **1,373 bp**, **309 variable sites**. Separately MAFFT aligned then inferred with partitioned IQ-TREE 2 ModelFinder, 1000 SH-aLRT and 1000 UFBoot. Rooted with source Carduus nutans. Branches in substitutions/site, not Ma.
- Frozen real Newick SHA256 **f8a38a71c68ba3cc4c12789f4a29e44dc27ae926c5da8938ff56ccc8841ad837**.
- Execution and nucleotide data artifact: https://github.com/zuizui0223/EAzami/actions/runs/40103021756/artifacts/12563577567 (SHA256 bc70b79fa13bd774e73f17ff88d12d798b0861be395271ea4f7b7c5a3375841b). All original FASTA, specimen/QC receipts, MAFFT alignments, IQ-TREE input, output, likelihood reports and Newick included.

The sampled genetic lineages include East Asian C. henryi and C. lineare, western Eurasian C. canum, C. monspessulanum, C. palustre, C. spinosissimum and C. tymphaeum, and many North American and Mexican taxa. Native-range/source-geography is NOT proof of the individual GenBank voucher locality.

### Nine morphological variables and Moreyra S1 distinction

Moreyra 2025 supplementary S1 contains sampling, accession and voucher variables, not the nine morphological traits. Siniscalchi 2023 original nine-character matrix matches 16 of the 45 Cirsium binomial concepts (24 ITS/ETS specimen tips) by exact taxon spelling. One extra C. lineare U state is supported by independent NMNS morphology. The remainder must remain missing. A species with multiple molecular accessions represents one taxon-level trait claim, not independent origins.

**Critical negative coverage gate:** Current source-backed U/D overlap with the 67-tip nuclear tree contains NO resolved D-labelled specimen. Accordingly, a U→D transition-rate or historical climatic trigger analysis on this molecular tree is NOT estimable without more independent source phenotyping. Missing taxa must not be coded U or D by association.

Siniscalchi CorollaColor code 2 combines white/pink/purple. This cannot establish a white-flower origin or pigment pathway regain.

### Scientific limit

This is a genuine newly inferred broad North America–Eurasia nuclear ribosomal tree but ITS and ETS are physically linked multicopy loci, NOT Moreyra 2025's final 350 independent low-copy Compositae1061 genes. The full worldwide 294-BioSample/295-SRR target-capture tree remains unexecuted. Uncertainty from low genetic differentiation, hybridization and source taxon labels should be retained.

### Reproduction

- analysis/audit_slotta2012_nuclear_ITS_ETS_source_vouchers_v1.py
- analysis/recover_slotta2012_crosscontinent_nuclear_ITS_ETS_v1.py
- analysis/infer_slotta2012_crosscontinent_nuclear_ITS_ETS_ML_v1.py
- .github/workflows/infer-real-crosscontinent-cirsium-its-ets-v1.yml
- data/evidence/cirsium_real_transcontinental_67tip_nuclear_ITS_ETS_20261024.json

## Real crosscontinental 45-tip ancestral U/D model completed — October 25, 2026

**New executed result:** The 45-tip 176-Compositae1061-nuclear-locus genuine source phylogram has now been used for explicit ER and ARD two-state Mk ancestral-state inference across three *alternative tree-estimation models*, plus two independent D-tip omission sensitivities. GitHub Actions [run 40114987601](https://github.com/zuizui0223/EAzami/actions/runs/40114987601) passed; source result artifact **12568420241**, SHA256 `bae9309a73f2de78ae5d6a9ddf04fd83eb7435aa4fd0fdef7ad023a1de778f1a`.

Biologically distinct source tips: 39 Japan38 Moreyra + 3 North American Moreyra + 2 West Palearctic Moreyra = **44 ingroup specimens**, with *Carthamus* original nuclear outgroup providing molecular root. Head morphology from independent original botanical sources is **17 U / 7 D / 20 unresolved ingroup**; every unresolved or polymorphic source state enters the likelihood as `[1,1]`, never imputed. Source head shape is taxon-concept evidence, **not sequenced-voucher phenotype**. Source Moreyra S1 contains accession/voucher/BioSample metadata, not the Siniscalchi nine-trait phenotype table.

| True 176-locus molecular model | ModelFinder ML | Fixed GTR ML | FastTree approx ML |
|---|---:|---:|---:|
| Fitch minimum U/D state changes | 6 | 5 | 6 |
| Full 17U/7D panel: ΔAICc (ARD−ER) | −1.894 | −1.885 | −1.893 |
| *C. erisithales* D treated as missing (cultivation sensitivity): ΔAICc | −3.060 | −3.051 | −3.059 |
| *C. vinaceum* D treated as missing (North America sensitivity): ΔAICc | **+1.105** | **+1.899** | **+0.608** |

**Positive ecological/evolutionary result with boundary:** Multiple states (U and D) occur across three broad source areas and the real tree requires at least **5–6 categorical state changes**. Two external geographic contrasts (North America and Western Palearctic) appear across all three molecular trees, but they do not give known transition directions.

**Critical falsification:** The apparent weak support for direction-dependent rates **does not survive** the North American D-tip sensitivity; model selection flips from ARD to ER on *every* molecular topology after omitting *C. vinaceum*. Thus we cannot claim robust faster D→U or U→D evolutionary change. The fitted likelihood shows an ingroup root P(U) approximately **0.5** under both models: **ancestral root orientation is not identified** by this 45-tip source panel.

The root, internal ancestral-node posterior, and P(parent U, child D) are **fitted model endpoint states**, not a count or date of real historical transitions. No phenotype-linked rainfall niche was used here and no palaeoclimate/selective cause has been established. The 3 alternative molecular tree models are **not 3 independent dataset replications**, because they share the same 176-locus sequence matrix. The five added specimens have only ~25–32% confident base coverage; true whole-genus 294-tip/350-locus phylogenomics remains a separate uncompleted goal.

**Reproducible source**: `analysis/fit_real_world45_multitopology_U_D_mk_v1.py`, `tests/test_real_world45_multitopology_U_D_mk_v1.py`, `.github/workflows/fit-real-world45-nuclear-Mk-U-D-v1.yml`; compact result receipt `data/evidence/real_world45_176Comp1061_ER_ARD_Mk_ancestral_head_20261025.json`. The execution artifact contains all 18 ER/ARD fits, the explicit continental MRCA and D-terminal edge posteriors, and **source-tip omission reversal visualization**.

Original 40-tip source alignment was left identical. The original *Carthamus* sequence lacks adequate reference length for the exact two original loci `At1g26880` and `At5g62680`; the deployed successful five-readset workflow **masked those loci for the added samples**, rather than inventing replacement bases. **174/176 loci** have usable reference coordinates for the added samples; five-way stringent high-confidence intersection covers **87 loci**.

## 2026-10-25: world53 ORIGINAL DNA + Moreyra S1 + 9 flower traits (new accepted pilot)

**Genuine new result achieved:** The geographic expansion from 45 to 54 planned molecular samples was executed from original Moreyra S1 target-capture libraries. Eight of nine new SRRs passed the UNCHANGED source 70/176 nuclear-locus read-mapping gate. Chinese *Cirsium fargesii* SRR30887183 recovered 63 loci and 25,840 confident bases, therefore was rejected without changing locus thresholds or examining its phenotype. The eight passing samples recovered 86–102 loci each, totalling 355,179 confidently called bases. See `data/evidence/world54_source9_QC_failed_one_world53_acceptance_20261025.json`.

**Correct consequence:** 45 original real molecular tips + eight independent QC-pass nuclear specimen tips = **53 real source specimens**, including the original *Carthamus* molecular outgroup. Total original Compositae1061 locus universe **176**, 161,654 alignment columns; the entire 45-tip source alignment is byte-for-byte unchanged, and added low-confidence positions are `N`-masked. No source taxon/tree topology was inferred from floral morphology.

### Authentic newly inferred 53-tip IQ-TREE source topology

- Run [40148735969](https://github.com/zuizui0223/EAzami/actions/runs/40148735969), artifact 12582202210 (ZIP SHA256 `539fe41b2bcd0250b3d9929740aec93121b1ab5360be7b6b97be3b689b1faa05`), **success**.
- Original independently refitted ML tree, IQ-TREE ModelFinder BIC **TIM3+F+R3**, SH-aLRT 1000, UFBoot 1000; original outgroup fixed for root. Newick SHA256 **5828ccd9f4f0b083f804f87bfa7407a20ad5eb52647e92eb5a26e812bd6807a7**.
- **IMPORTANT permanent file:** `data/evidence/real_world53_176Comp1061_IQTREE_ModelFinder_UFBoot_SHaLRT_20261025.nwk` is now versioned in the GitHub branch, not only temporarily stored in Actions.

### Real floral morphology and the source S1 voucher contract

Run [40150037475](https://github.com/zuizui0223/EAzami/actions/runs/40150037475) successfully joined 39 Japan original Moreyra S1 genetic vouchers, five original external Moreyra genetic tips and eight QC-pass trait-blind external Moreyra S1 vouchers into the **same real 53-tip tree**, then mapped every available original Siniscalchi 2023 nine-character source record. Separate Japanese NMNS and FNA/European taxonomic head data are retained by source URL.

- Genuine Cirsium molecular ingroup: **52 individual tips** (39 original Japan38, 5 original external, 8 blind-recovered external).
- Source-level U=**19**, D=**9**, unresolved=**24**; only **27 distinct species binomial concepts** provide resolved U/D because *C. kamtschaticum* has a Japan-original and a separately sampled continental molecule with the same taxon-level D evidence.
- Six of the 53 molecular tips have complete **original Siniscalchi nine-variable categorical codes**; other missing categorical flower/leaf variables are **not imputed**. Moreyra S1 is DNA/voucher metadata, **not** a table of the same nine floral variables.
- Independent IQ-TREE topology Fitch U/D minimum category changes **9**. Pruning the new same-species *C. kamtschaticum* molecular individual reduces the minimum to **8**.
- ER/ARD source Mk AICc on the primary IQ-TREE (n≈27 phenotyped binomial concepts): **ER 40.659 / ARD 39.631**, Δ(ARD−ER)=**−1.029**. This is **weak**, not convincing support for faster D→U evolution. Ingroup root P(U) about **0.500**, ancestral direction unresolved.
- Model output, 9-trait color key and 53-tip original S1 crosswalk stored in artifact **12582068446**. Source renderer `analysis/annotate_real_world53_original_S1_nine_traits_Mk_v1.py`. The figure now focuses on **52 Cirsium tips** by omitting the long outgroup branch ONLY from the graphic: the full 53-tip Newick and sequence model retain the true *Carthamus* outgroup.

### Independent inference-algorithm sensitivity (same actual molecular reads)

- FastTree GTR+gamma **independently refit** on the identical original 53-tip, 176-locus aligned sequences: [run 40149393831](https://github.com/zuizui0223/EAzami/actions/runs/40149393831), artifact 12582477149. FastTree local SH support is NOT an IQ-TREE bootstrap.
- Original IQ-TREE vs FastTree: 50 nontrivial unrooted splits each, **26 shared; RF=48 of maximum 100**. High sensitivity in the global/japanese/internal phylogeny: no fixed global species tree accepted.
- All **six North-American** original+new source nuclear specimens form an exclusive regional clade in both source trees; IQ-TREE SH-aLRT/UFBoot **100/100**, FastTree local SH-like **1.0**. This supports regional molecular membership under these two modelers, not any pollinator mechanism or origin-time claim.
- All **five West-Palearctic** samples do **not** form one exclusive clade in either tree. *C. kamtschaticum* original Japan38 and added continental source tips are **not** an exclusive sister pair in either model; requires deeper sequencing/taxonomic/missingness audit, not an instantaneous hybridization/independent-origin assertion.
- Morphology Fitch minimum changes: **IQ-TREE 9**, **FastTree 8**. Both have weak ΔAICc(ARD−ER) approximately **−1.03** and **−0.99**. Three trees across two molecular estimation algorithms are **not** independent biological replication.
- A direct original 45-tip IQ-TREE vs new 53-tip IQ-TREE comparison after pruning eight added tips yields source-shared 45-tip unrooted RF **36/84** despite unchanged original DNA and unchanged preferred substitution model TIM3+F+R3. This is substantive source sampling sensitivity and prohibits interpreting unexpected Japanese root placements as one accepted global colonization history.
- [run 40149950497](https://github.com/zuizui0223/EAzami/actions/runs/40149950497), artifact **12582073279** stores independently executed topology/clade and ER/ARD comparisons.

**Persistent scientific receipt**: `data/evidence/world53_real_176Comp1061_ML_S1_nine_traits_topology_Mk_results_20261025.json` and permanently committed Newick. These are **pilot nuclear reference-projected** analyses with high missingness in the new specimens. The 294 independent biological samples / 350 published final nuclear loci of Moreyra et al. (2025) are still NOT jointly reconstructed as a complete global accepted topology. No U→D event age, distinct origin count, historic climate at origin, fitness or ecological adaptation has been inferred.

## Completed morphology-blind, all-external-samples-covered 74-gene nuclear sensitivity (2026-10-25)

**New actual original-DNA refit:** The genuine 53-tip/176-Compositae1061-gene high-missingness phylogram was subjected to a prespecified **genomic occupancy-only** locus-selection test: select a whole original aligned locus only if **all 13 molecular samples outside Japan** (6 North American, 5 western Palearctic, 2 continental eastern/central Asian) each carry at least **40% unambiguous ACGT characters**. The selection DID NOT consult floral head/colour states, latitude, climate, tree topology or informative site variation.

- Selection source: exact SHA-pinned authentic world53 53-tip full alignment `9179394190a3ab499a122439bca9c8bbe74e205a315440e4f7442b5ee225b237` and original 176 nuclear locus partition table SHA `30e6e5703a76b4065c3903c04b43179fb538d280539df66c7bf64706962a128e`.
- Selection result: **74 entire original nuclear loci**, **61,240 aligned bp** in precisely the same **53 real molecular individuals**, including original *Carthamus* outgroup. The selected sample-character FASTA SHA is `e8a60205d17cf1907fd8c31a999aa16a1d004cb87e5296bf8b02ea51ebd78bdc`. Gene names, new/old alignment positions and all 176 original source-coverage values are archived.
- Actual independent ML fitting to selected real nucleotide subset: IQ-TREE 2 `TIM3+F+R3`, same winning source model as original full176, 1000 UFBoot and 1000 SH-aLRT. GitHub Actions **[run 40151213259](https://github.com/zuizui0223/EAzami/actions/runs/40151213259)** finished **successfully**; full original source alignment / numerical QC / new ML topology / original source-phenotype model and branch support in artifact **12582996013**, ZIP SHA256 `4bfbe6035e77860580511c1f636579a7a24d216e6fad022324cd5ea783341bdd`.
- **Permanently committed actual empirical Newick:** `data/evidence/real_world53_74loci_all13ge40pct_IQTREE_TIM3_F_R3_ML_20261025.nwk`, original CI source Newick SHA256 `57483eb8f1232631a8160e7dfe8e9427a1a85f20a8957e5d23ea65bca08e5e64`, authenticated **exact Git blob SHA1 `4651901ab5605bb373200040259d999e65d32585`**.

| Genuine matched-source nuclear property | All 176 originally available genes | All 13 external-source-covered 74 genes |
| --- | ---: | ---: |
| Source molecular individual tips | 53 | 53 |
| Original nuclear gene alignments | 176 | 74 |
| Aligned bp | 161,654 | 61,240 |
| North-American six Moreyra samples, exclusive clade | YES, IQ-TREE 100/100 | **YES, IQ-TREE 100/100** |
| Western Palearctic five molecular tips, exclusive clade | No | No |
| Two same-labelled *C. kamtschaticum* molecular individuals, exclusive sister pair | No | No |
| Minimum Fitch U/D category steps, 19U / 9D / 24 unknown | 9 | 8 |
| AICc(ARD) minus AICc(ER) under same source categories | −1.029 | −1.107 |
| Root P(U), symmetric ER Mk | 0.50046 | 0.50027 |

**Topological turnover remains high:** the two 53-tip IQ-TREE phylograms, with exactly the same source 53 specimens, software, winning TIM3+F+R3 nucleotide model and character phenotypes, have **unrooted RF=48/100**, with 26 shared of 50 nontrivial splits. The only experimental change was which genuine original nuclear gene alignments met stringent joint across-region coverage. Thus parts of global and Japanese apparent lineage placement remain strongly dependent on marker occupancy. The result does NOT establish a true historical topology for west Palearctic origins, recurrent D/white flowers, polyploid reticulation or regional climate selection.

**Ecological interpretation:** The six North American samples form a stable group against full176, high-occupancy74, and the earlier full176 FastTree approximate ML; this is a reproducible but limited **regional molecular pattern** within the selected Cirsium source sampling. The western five are non-exclusive regardless of the filter. *C. kamtschaticum* pair is not exclusive, but per-gene genetic distances and source-name/orthology audits are required before an introgression/polyploidy interpretation. Nineteen U, nine D and 24 missing head states are merely original **species-level botanical references**, not directly phenotyped sequenced vouchers or 28 independent documented evolutionary origins.

**Next original molecular task:** expand beyond reference-mapped, missing-locus-stratified specimens toward independently reviewed low-copy nuclear orthology (HybPiper paralogs and/or alternative Cirsium-reference mapping) and broader global taxon coverage. Neither this 53-tip 74-gene QC subset nor the full176 analysis is the still-unavailable validated Moreyra et al. 2025 **294 public-BioSample, final 350-nuclear-gene worldwide species tree**.

Reproduction / durable original-source receipts:

- `analysis/build_real_world53_nuclear_74balanced_loci_v1.py`
- `analysis/audit_real_world53_nuclear_176_vs_balanced74_gene_tree_v1.py`
- `.github/workflows/real-world53-source-nuclear-74balanced-sensitivity-v1.yml` (now explicit dispatch only after successful first immutable source run)
- `data/evidence/world53_176vs74_source_coverage_nuclear_S1_phylogeny_20261025.json`
- `.github/workflows/validate-world53-74covered-nuclear-S1-v1.yml`

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
