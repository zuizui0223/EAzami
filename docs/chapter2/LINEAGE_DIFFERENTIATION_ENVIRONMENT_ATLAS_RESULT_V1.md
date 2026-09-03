# Lineage-differentiation environment atlas result v1

Status date: 2026-09-03  
Status: **COMPLETED INTERNAL EXPLORATORY DIAGNOSTIC**

## Question

Before attributing the Pleistocene radiation to one climatic regime, we asked a broader lineage-level question independently of any present-day trait–environment result:

> **Do dated East-Asian *Cirsium* lineage differentiations repeatedly occur in unusual historical climate states, during unusually large climate changes, or during unusually variable climate?**

This is deliberately **not** a capitulum-trait transition test. It sits above the trait-event level and is used only to test whether the frequently invoked Pleistocene climate background itself shows one recurring quantitative signature across multiple lineage divergences.

## Design

All 17 BIOCLIM variables supplied by the public PALEO-PGEM-Series record were used:

`BIO1, BIO4–BIO19`.

No environmental variable was chosen from Azami or from a present-day EAzami association.

Six published dated lineage contexts were evaluated. To prevent nested Taiwanese/Nipponocirsium divergences from inflating recurrence, the cross-group synthesis used only three predeclared representatives:

1. Japanese–Taiwanese Nipponocirsium (~0.74 Ma; 0.60–0.87 Ma);
2. Arenicola *C. brevicaule*–*C. irumtiense* (~0.93 Ma; 0.71–1.33 Ma);
3. Japanese–Taiwanese Sinocirsium (~0.44 Ma; 0.31–0.66 Ma).

Each published age interval was represented by 31 deterministic age scenarios plus the exact central estimate. Alternative regional boxes were retained where ancestral location was not uniquely known. Each scenario was evaluated against two background horizons (0–1.5 Ma and 0–3.6 Ma).

For every BIOCLIM variable we measured:

- climate level at the candidate divergence age;
- absolute climate change across 50- and 100-kyr windows;
- temporal variability across 50- and 100-kyr windows.

Because BIOCLIM variables are strongly correlated, a second analysis standardized all 17 variables, retained PCA axes explaining at least 95% of temporal variance, whitened those axes, and measured multivariate climate-state distance, short-window displacement and multivariate temporal variability.

A result had to survive the full age interval, every allowed regional scenario, both background horizons and—where applicable—both 50- and 100-kyr windows. Cross-group recurrence required the same robust class in at least two of the three representative clades.

## Formal result

Workflow run `33704837646` completed successfully. Artifact `9874890222`, SHA256 `a9ded89c5da641fd3aac19b5c352b6672bde829cbe912721131c714245750e62`.

The formal decision was:

`no_recurring_lineage_differentiation_context_survives_age_region_background_gates`

- 17 historical climate variables evaluated;
- 6 dated lineage contexts;
- 3 representative broad clade groups;
- 324 event-level univariate/multivariate classes;
- **0 robust event-level classes**;
- **0 recurring climate-context candidates across the three representative clades**.

Thus neither a single BIOCLIM regime nor a multivariate all-climate state, transition magnitude or variability pattern is robustly shared across the dated lineage differentiations once age, regional and background uncertainty are retained.

## Descriptive tendencies below the formal threshold

The negative formal result does not mean every lineage has identical climate history. The scenario medians show a useful heterogeneity pattern.

### Japanese–Taiwanese Nipponocirsium

A cold-side tendency is visible in several temperature variables:

- BIO1 median-of-scenario-median percentile ≈ 0.189;
- BIO11 ≈ 0.198;
- BIO6 ≈ 0.206.

Temperature variability is comparatively high-side:

- BIO1 ≈ 0.757;
- BIO10 ≈ 0.754;
- BIO11 ≈ 0.745.

### Japanese–Taiwanese Sinocirsium

A similar, but still non-robust, tendency occurs:

- BIO6 level ≈ 0.229;
- BIO11 ≈ 0.233;
- BIO1 ≈ 0.263;
- BIO11 variability ≈ 0.816;
- BIO1 variability ≈ 0.802;
- BIO8 variability ≈ 0.784.

### Arenicola

The same tendency is not reproduced. Temperature levels and variability are closer to background centers; for example BIO1 level ≈ 0.432 and BIO1 variability ≈ 0.506.

Therefore the two Japan–Taiwan contrasts may share a cold/variable historical tendency, but the Arenicola differentiation does not support treating that tendency as one general East-Asian *Cirsium* differentiation regime.

## Multivariate all-climate result

The 17-variable whitened climate state is also ordinary at the representative divergences. Median scenario percentiles for multivariate state distance are approximately 0.525 (Nipponocirsium), 0.514 (Arenicola) and 0.527 (Sinocirsium). Short-window displacement and multivariate variability are likewise not extreme.

This is useful because it prevents a correlated set of individual BIOCLIM variables from being counted as multiple independent pieces of evidence for one climatic event.

## Interpretation

The current reading is:

> **The Pleistocene is a shared temporal backdrop for East-Asian thistle diversification, but the dated lineage divergences do not resolve one recurring quantitative climate regime. Historical differentiation context is heterogeneous across lineages.**

This strengthens the distinction already visible at the trait level. A broad statement that Pleistocene climate and island reorganization structured the radiation can remain valid, while a stronger statement that the same climate regime repeatedly triggered the focal lineage divergences is not supported by this exploratory atlas.

The result does **not** imply climate was biologically irrelevant. The tested intervals are broad, ancestral geography is uncertain for several nodes, PALEO-PGEM is 1° and this analysis uses the public mean fields rather than the complete emulator/downscaling uncertainty. Local topography, island connectivity and biotic interactions can also create lineage-specific differentiation without a common coarse-climate signature.

## Role in Chapter 2

This diagnostic is not required in the main manuscript Results. Its strongest use is to enforce the causal boundary:

`shared Pleistocene radiation context ≠ one shared climatic differentiation trigger ≠ one capitulum-trait selective cause`.

It also motivates the next test: whether a **geographic isolation/connectivity opportunity**, rather than one climate regime, recurs across the independently dated lineage divergences.

## Claim boundary

- lineage divergence dates are not capitulum-trait transition dates;
- nested Nipponocirsium nodes are not independent repeated events;
- node-age grids are deterministic uncertainty scenarios, not posterior samples;
- regional boxes are sensitivity regions, not ancestral-area probabilities;
- a recurring lineage climate context, if later detected, would still not establish natural selection or adaptation;
- absence of a robust shared regime is not evidence that climate had no role in individual lineages.
