# Supporting Information for Chapter 2 JEB V10

## Article

**A young Cirsium radiation repeatedly rebuilt its reproductive head from functionally distinct components**

Status: **ACTIVE V10 SUPPORTING INFORMATION**

This Supporting Information preserves the uncertainty, negative results and resolution ceilings behind the active five-figure manuscript without reopening exploratory analysis.

The evidence order is:

`repeated change → mosaic assembly → functional interfaces → orientation transition ecology → historical-origin falsification`.

Historical counts, relative depth, branch localization, static ecology, transition-conditioned ecology and causal mechanism are treated as distinct estimands.

---

# Supplementary Methods S1 — Nuclear scaffold, taxon admission and discrete trait ontology

The historical analysis uses the frozen Japan38 Compositae1061-compatible nuclear scaffold.

- sampled Japanese taxon concepts: 38;
- concepts in the published dominant Japanese radiation: 36;
- biological samples in the Japan38 reconstruction: 39;
- quality-controlled loci: 236;
- rootable loci: 176;
- concatenated alignment: 161,654 bp;
- phylogram branch lengths: substitutions per site.

Branch lengths are not calendar time.

JPN20 is represented by two non-monophyletic sequence samples in the compatibility reconstruction and is not silently collapsed. JPN31 remains excluded from primary trait history because the frozen identity/locality conflict prevents a safe phenotype–sequence join.

Three source-backed capitulum components are analysed as discrete traits:

1. **orientation** — upward/erect versus downward/nodding, with ambiguous/source-conflicting concepts unresolved;
2. **phyllary posture** — appressed, ascending, spreading or recurved, retaining composite authority descriptions where necessary;
3. **involucre stickiness** — sticky versus nonsticky/nearly nonsticky.

Resolved historical coverage is:

| Trait | Resolved concepts |
|---|---:|
| Orientation | 20 |
| Phyllary posture | 10 |
| Stickiness | 13 |

The ontology is taxon-concept level. It is not a same-voucher phenotype dataset and cannot establish individual-level genetic linkage.

---

# Supplementary Section S2 / Table S2 — Repeated state change and relative evolutionary depth

## S2.1 Minimum-change counts

Unordered Sankoff/parsimony minima were calculated on the maximum-likelihood topology and propagated across 1,000 UFBoot topology realizations.

| Trait | ML minimum | UFBoot minimum range | UFBoot median |
|---|---:|---:|---:|
| Orientation | 6 | 4–6 | 5 |
| Phyllary posture | 3 | 3–3 | 3 |
| Stickiness | 5 | 5–5 | 5 |

These are lower bounds on required state change, not counts of independent adaptive origins, convergence events or evolutionary rates.

## S2.2 Relative lineage depth

For an edge subtending d descendants among N admitted tips, relative lineage depth is D = (N-d)/(N-1). D=1 is terminal; smaller values permit deeper placement.

Frozen median UFBoot depth envelopes are:

| Trait | Median relative-depth envelope |
|---|---|
| Orientation | 0.795–0.994 |
| Phyllary posture | 0.695–1.000 |
| Stickiness | 0.937–0.954 |

## S2.3 Paired same-topology depth ordering

| Ordering | Topologies retaining ordering | Fraction |
|---|---:|---:|
| Phyllary deeper-permissive than stickiness | 1000/1000 | 1.000 |
| Phyllary deeper-permissive than orientation | 993/1000 | 0.993 |
| Orientation deeper-permissive than stickiness | 905/1000 | 0.905 |
| Complete phyllary < orientation < stickiness | 898/1000 | 0.898 |

These fractions quantify topology sensitivity; they are not probabilities, posterior support values or independent biological replicate frequencies.

## S2.4 Coverage-matched sensitivity

Because observed-state coverage differs among traits, a post-result masking sensitivity tested whether the central ordering was merely a missing-data artifact.

| Comparison | Matched-median ordering | Strict q05 ordering |
|---|---:|---:|
| Phyllary < orientation | 195/200 = 97.5% | 21/200 = 10.5% |
| Phyllary < stickiness, 5/5 mask | 193/200 = 96.5% | 22/200 = 11.0% |
| Phyllary < stickiness, 6/4 mask | 193/200 = 96.5% | 31/200 = 15.5% |

Reduced coverage does not erase the central phyllary-deeper ordering, but strict deepest tails overlap. The result is not described as coverage-independent.

---

# Supplementary Section S3 / Table S3 — Shared transition localization

Two localization diagnostics are retained because branch-length geometry can itself induce apparent overlap:

- a branch-length-aware equal-rates Mk layer, summarized by transition-posterior excess over branch prior;
- an equal-branch topology-only sensitivity across the UFBoot ensemble.

| Pair | Branch-aware excess rho | Equal-branch median rho | Equal-branch q05 | Equal-branch fraction >0 | Robust shared-localization rule |
|---|---:|---:|---:|---:|---|
| Orientation × phyllary | +0.362 | −0.059 | −0.206 | 34.9% | fail |
| Orientation × stickiness | +0.202 | −0.387 | −0.392 | 0.9% | fail |
| Phyllary × stickiness | +0.084 | +0.184 | −0.073 | 78.2% | fail |

**Zero of three** trait pairs passes the frozen cross-treatment rule requiring robust positive localization.

This constrains a simple synchronized whole-capitulum history. It does not demonstrate complete evolutionary independence, developmental modularity or different selective agents.

---

# Supplementary Section S4 / Table S4 — Common nine-variable present-environment comparison

All three historical traits were passed through one trait-blind workflow with the same occurrence/QC logic and the same nine variables:

BIO1, BIO4, BIO12, BIO15, RSDS, VPD, WIND, GSP and NPP.

The primary occurrence gate required at least three thinned occurrences per taxon. State separation was ranked against every admissible finite state-label map preserving observed state counts.

## S4.1 Omnibus results

| Trait | n taxa | State counts | Nine-variable omnibus rank | Interpretation |
|---|---:|---|---|---|
| Orientation | 17 | 5 D / 12 U | 2138/6188 = 34.55% | weak static state separation |
| Phyllary posture | 4 | 1 appressed / 3 ascending | 4/4 = 100% | not identifiable as a trait effect |
| Stickiness | 12 | 6 sticky / 6 nonsticky | 116/924 = 12.55% | replicated but non-exceptional omnibus |

Phyllary minimum-one-record sensitivity reaches six taxa, but appressed and spreading remain singleton lineages and the omnibus rank is 28/30 = 93.33%. Lowering the record gate does not create biological state replication.

## S4.2 Stickiness exploratory precipitation leads

| Axis | Sticky − nonsticky standardized difference | Exact rank | BH q across 27 rows |
|---|---:|---:|---:|
| GSP | +1.2781 | 18/924 = 1.95% | 0.3214 |
| BIO12 | +1.3110 | 22/924 = 2.38% | 0.3214 |
| BIO15 | +1.0485 | 70/924 = 7.58% | 0.6818 |

No primary trait × environment row survives q<0.05 across the 27-row family.

The common9 result does not identify one shared abiotic syndrome and does not directly test visitor access, antagonist pressure or arthropod-community mechanisms.

---

# Supplementary Section S5 / Table S5 — Orientation transition-regime analysis

The transition analysis tests a different estimand from static D/U separation.

The fixed U→D environmental vector is **BIO15 higher + BIO1 lower**.

Present-day taxon niche centroids are combined with CTMC transition probabilities and Brownian environmental reconstruction. The finite-map statistic is ranked among all count-preserving state maps. It is a conditional exact rank, not a P value from biological replicates.

## S5.1 Coverage panels

| Panel | n taxa | State counts | Exact composite rank |
|---|---:|---|---:|
| Primary n≥5 | 12 | 7 U / 5 D | 16/792 = 2.02% |
| Sensitivity n≥3 | 13 | 7 U / 6 D | 19/1716 = 1.11% |
| Strict n≥10 | 9 | 5 U / 4 D | 4/126 = 3.17% |

In the strict panel:

- BIO15 alone: 7/126 = 5.56%;
- lower BIO1 alone: 8/126 = 6.35%;
- composite: 4/126 = 3.17%.

The supported object is the fixed two-axis transition-regime vector, not a unique single-variable driver.

## S5.2 Bidirectional directionality

Under the strict nine-taxon panel:

- U→D forward alignment median = 0.320891;
- D→U reverse alignment median = 0.339529;
- both positive on 6/6 accepted topologies;
- exact bidirectional-floor rank = 3/126 = 2.38%.

This is a post-result directional decomposition of H1, not independent confirmation or evidence of genetic reversibility.

## S5.3 Single-taxon deletion

For the fixed U→D composite (H1), deleting each strict-panel taxon once:

- direction remains positive on all six topologies in 9/9 deletion panels;
- exact ≤0.05 finite-map exceptionality survives only 2/9 deletions.

For the bidirectional forward/reverse decomposition (H2):

- both U→D forward and D→U reverse alignments remain positive on all six topologies after every one of the 9/9 deletions;
- the exact ≤0.05 bidirectional-floor rank survives 3/9 deletions.

Thus neither directional result is generated by one taxon, whereas exact finite-map extremeness is deletion-sensitive and belongs to the multi-taxon configuration.

## S5.4 Geography residualization

After residualizing BIO15 and BIO1 against a linear 1 + latitude + longitude model:

- strict n≥10: 5/126 = 3.97%, positive on 6/6 topologies;
- n≥5: 41/792 = 5.18%, borderline.

This rules out only the simplest linear geographic gradient.

## S5.5 Internal-edge-only scoring

With full CTMC/Brownian reconstruction retained but terminal child edges excluded from the scored statistic:

- strict n≥10: 3/126 = 2.38%;
- n≥5: 29/792 = 3.66%;
- both panels remain positive on 6/6 topologies.

## S5.6 Combined geography + terminal-edge stress

Applying both restrictions simultaneously:

- strict n≥10: 3/126 = 2.38%;
- n≥5: 29/792 = 3.66%;
- both remain positive on 6/6 topologies.

This was the final declared coarse public-data stress. No further correlated climate predictors or post-result robustness variants are opened to strengthen H1.

Internal environmental values remain Brownian reconstructions from present taxon niche centroids, not observed ancestral environments.

---

# Supplementary Section S6 / Table S6 — Preregistered external-taxon confirmation ceiling

The external programme was separated from discovery before held-out climate outcomes were opened.

## S7.1 V1

Under the first strict occurrence gate:

- *Cirsium schantarense* — D — 8 thinned records;
- *C. vlassovianum* — U — 8 thinned records.

This left one lineage per state, below the frozen minimum of two taxa per state, so V1 was not evaluable.

Stickiness V1 retained only *C. setidens* as sticky and no evaluable external nonsticky comparison. No held-out environmental outcome was opened.

## S7.2 Source-complete V2

The final expansion attempt was preregistered as a source-complete census rather than an occurrence-driven rescue.

It recovered:

- 46/46 lower taxa linked from the Flora of China *Cirsium* genus page;
- 19 printed *Cirsium* concepts in the selected NIBR national checklist lane.

External stickiness remained structurally blocked because the source-complete candidate set had no nonsticky comparison under the frozen ontology.

The final frozen Flora of China orientation panel contained:

- 13 taxa total;
- 3 downward/nodding;
- 10 upward/erect.

## S7.3 Strict V2 GBIF gate

Primary rules were exact accepted name, GBIF EXACT match, mainland-China provenance, PRESENT records, coordinates, explicit coordinate uncertainty ≤10 km, frozen issue exclusions, exact-coordinate deduplication, deterministic 0.1-degree thinning, ≥3 thinned records per taxon and ≥2 surviving taxa per state.

Only one taxon passed:

- *Cirsium vulgare* — upward/erect — 16 deterministic 0.1-degree thinned records.

Final state replication was downward/nodding 0 taxa and upward/erect 1 taxon.

Therefore:

> **external-taxon orientation confirmation is not evaluable with current public GBIF metadata.**

BIO1 and BIO15 were not extracted for the held-out V2 panel.

The stop rule is binding. No V3 public taxon rescue, QC relaxation or opportunistic climate-variable search is permitted.

This is an occurrence-metadata resolution ceiling, not an ecological null and not evidence against the Japan–Taiwan discovery result.

---

# Supplementary Section S7 / Table S7 — Historical environmental-cause boundary

Only one orientation event reaches the full calendar-age + palaeolocation + environment gate: the core-Nipponocirsium erect/upward → nodding/downward transition. The historical-persistence test was frozen before opening the result: support required the present BIO15-up/BIO1-down sign combination in at least 75% of chronology scenarios in **each** of the four palaeolocation regions.

- chronology pairs: 94;
- palaeolocation scenarios: 4;
- region × chronology scenarios: 376;
- central chronology: 0.79–0.74 Ma.

At the central chronology, BIO1, BIO4 and BIO15 decrease in all four regions, while BIO12 increases in three of four. Across the full envelope, no tested climate direction survives as a robust historical trigger.

For the present BIO15-up/BIO1-down regime:

- historical sign matches: 99/376 = 26.3%;
- Taiwan: 20/94 = 21.3%;
- Ryukyu corridor: 9/94 = 9.6%;
- southern Japan: 41/94 = 43.6%;
- East-Asian core corridor: 29/94 = 30.9%.

At the central chronology, BIO15 moves opposite to the present U→D direction in all four regions.

Broader audits remain negative at the frozen robustness gates:

- 17 BIOCLIM variables;
- 6 dated lineage contexts;
- 15,472 scenario × variable combinations;
- robust event-level climate classes: 0;
- global sea-level event-metric classes: 21;
- robust sea-level classes: 0.

This is an identifiability boundary, not evidence that historical climate, local geography, fragmentation, biotic interactions or selection were irrelevant.

---

# Supplementary Section S8 / Table S8 — Functional-interface evidence and reproductive-antagonist fitness magnitude

Functional evidence is kept separate from historical comparative estimands.

## S8.1 Reproductive herbivory meta-analysis

The estimand is mean viable/mature seed output under experimentally reduced insect herbivory divided by mean seed output under ambient herbivory.

Nine within-study contrasts are collapsed to four independent data-generation studies before pooling.

Frozen random-effects result:

- independent study clusters: 4;
- pooled RR = 2.67364;
- 95% CI = 2.38833–2.99302;
- equivalent ambient-herbivory loss of potential seed output = 62.6%;
- 95% interval for loss = 58.1–66.6%;
- I² = 1.02%;
- tau² on lnRR scale = 0.000219.

Leave-one-study-out pooled RRs range from 2.6046 to 2.7342.

This establishes that reproductive antagonists can impose a large fecundity cost in directly harmonizable *Cirsium* experiments. It does not identify which capitulum component mediates the cost.

## S8.2 Trait-specific mechanism proximity

**Orientation.** Direct angle manipulation in close Asteraceae and within-genus pollination studies make time-window presentation and abiotic protection plausible. East-Asian *Cirsium* manipulation is not yet available.

**Phyllary / spine architecture.** Close Cardueae evidence supports a possible mechanical-access trade-off. Current EAzami image geometry is not itself a validated botanical defence trait.

**Stickiness.** Direct *Cirsium* exudate studies show context dependence rather than one universal positive defence effect. Sticky morphology is not automatically interpreted as defensive adaptation.

The next test is focal manipulation linked to mediator and final filled-achene endpoints.

---

# Supplementary Table S9 — Claim hierarchy and causal ceiling

| Evidence layer | Supported statement | Prohibited escalation |
|---|---|---|
| Minimum changes | all three components repeatedly changed | independent origins, convergence, rate |
| Relative depth | central historical depth differs among components | calendar transition ages |
| Shared localization | one synchronized branch history is not required | complete genetic/developmental independence |
| Common9 | no one shared static abiotic syndrome | no ecology for phyllary; universal stickiness law |
| Orientation transition regime | present niche change aligns with fixed BIO15/BIO1 vector | climatic causation, selection, adaptation |
| External V2 | public metadata cannot support replicated held-out states | ecological null; failed biological hypothesis |
| Historical climate | one recurring tested coarse trigger not identified | environment was irrelevant |
| Functional literature | mechanisms plausible; antagonist fitness cost large | focal historical adaptation established |

---

# Supplementary Table S10 — Adaptation inference ladder

| Level | Current status | What it does not establish |
|---|---|---|
| Recurrent state change | established for all three components | repeated selection or independent adaptive origins |
| Mosaic assembly | established by unequal depth and 0/3 robust shared localization | genetic/developmental modularity |
| Functional interface | experimentally plausible; evidence strength differs by trait | focal East-Asian adaptation |
| Reproductive fitness leverage | large antagonist cost in *Cirsium* (RR 2.674) | trait-specific fitness effect |
| Orientation transition ecology | fixed BIO15-up/BIO1-down regime is exceptional under finite maps | climatic causation or selection |
| Historical trigger | present regime not persistent; no recurring coarse trigger identified | environmental irrelevance |

The manuscript therefore treats adaptation as a testable next step rather than a conclusion from recurrence.

# Supplementary Table S11 — Reproducibility and source map

Primary machine-readable sources for V10:

- `data/evidence/chapter2_historical_differentiation_final_summary_v1.json`;
- `data/evidence/chapter2_depth_ordering_robustness_result_v1.json`;
- `data/evidence/chapter2_depth_coverage_matched_sensitivity_result_v1.json`;
- `data/evidence/chapter2_time_axis_compute/japan38_latest_module_transition_overlap_v2.json`;
- `data/evidence/chapter2_time_axis_compute/japan38_latest_module_overlap_topology_sensitivity_v2.json`;
- `data/evidence/chapter2_three_trait_common9_result_v1.json`;
- `data/evidence/chapter2_orientation_transition_regime_hypothesis_result_v1.json`;
- `data/evidence/chapter2_orientation_transition_directionality_result_v1.json`;
- `data/evidence/chapter2_orientation_transition_regime_single_deletion_result_v1.json`;
- `data/evidence/chapter2_orientation_transition_regime_geography_residual_result_v1.json`;
- `data/evidence/chapter2_orientation_transition_regime_internal_edge_result_v1.json`;
- `data/evidence/chapter2_orientation_transition_regime_combined_stress_result_v1.json`;
- `data/evidence/heldout_orientation_occurrence_gate_v2_contract.json`;
- `docs/chapter2/HELDOUT_ORIENTATION_OCCURRENCE_GATE_V2_RESULT.md`;
- `data/evidence/cirsium_floral_herbivory_lnrr_meta_v2.json`.

Active manuscript / production sources:

- `docs/chapter2/MANUSCRIPT_JEB_V10_FUNCTIONAL_ASSEMBLY_ORIGIN_DECOUPLING.md`;
- `docs/chapter2/V10_FUNCTIONAL_ASSEMBLY_ORIGIN_DECOUPLING_SPINE.md`;
- `analysis/make_chapter2_jeb_figures145_v7_v3.py` and `analysis/make_chapter2_jeb_figure2_v7.py` for the frozen historical Figures 1–2;
- `analysis/make_chapter2_jeb_figures_v10_new.py` for Figures 3–5;
- `analysis/build_chapter2_jeb_docx_v10.py`;
- `analysis/validate_manuscript_jeb_v10.py` and `analysis/validate_chapter2_jeb_docx_v10.py`.

---

# Supporting-information audit checklist

- [x] minimum changes are lower bounds, not independent origins;
- [x] relative lineage depth is not calendar time or evolutionary rate;
- [x] topology fractions are sensitivity summaries, not probabilities;
- [x] branch-aware and equal-branch localization are shown separately;
- [x] common9 retains all negative/resolution-limited outcomes;
- [x] stickiness precipitation leads retain 27-row multiplicity context;
- [x] finite-map fractions are conditional exact ranks, not biological-replicate P values;
- [x] post-result stress tests are not called independent confirmations;
- [x] V1/V2 external failures are retained and climate remains unopened where the gate failed;
- [x] public-data rescue is stopped after V2;
- [x] present ecological correspondence is not called historical cause;
- [x] historical-cause negative audits do not imply environmental irrelevance;
- [x] antagonist RR estimates fitness pressure, not trait adaptation;
- [x] no public-data result establishes selection, adaptation, convergence or a causal mediator;
- [x] the next independent causal test is prospective aza3 field manipulation.
