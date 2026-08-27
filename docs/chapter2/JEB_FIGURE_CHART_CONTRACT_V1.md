# JEB figure chart contract v1

## Surface and renderer

- Final surface: static journal figures embedded in the JEB manuscript.
- Renderer: deterministic Matplotlib script under `analysis/`.
- Exports: vector PDF plus 300-dpi PNG for repository QA; TIFF conversion may be made from the same canvas at submission.
- Figure footprint: 180 mm maximum width; white background; no decorative frame.
- Final QA: inspect every PNG at full resolution and verify PDF opens.

## Palette and non-colour encodings

- Palette policy: hard two-root cap.
- Blue (`#2F5D8A`) marks present/observed evidence.
- Gold (`#C58A1C`) marks comparison/null context.
- Dark charcoal (`#222222`) carries text, outlines, zero lines and decision annotations.
- Light grey (`#D9DDE3`) carries intervals, null distributions and non-primary context.
- FAIL and `not_evaluable` are encoded by direct text, outline/fill differences and hatch or line style, never colour alone.

## Figure contracts

### Figure 1

- Question: Is registered present-day integration comparable within and among taxa?
- Takeaway: within-taxon module contrasts exceed among-taxon contrasts at both frozen thresholds; matrix similarity is partial.
- Family/variant: faceted dot-and-interval comparison plus one annotated scalar.
- Data sufficiency: four interval estimates from one frozen handoff and one matrix-similarity value; a scatter is inappropriate.
- Source: `data/evidence/source/azami_capitulum_space_eazami_targets_run33035785120.csv` and frozen v3.1 summary.

### Figure 2

- Question: Do recurrence counts and transition-placement identifiability agree?
- Takeaway: all three traits recur, but forced-edge support differs strongly.
- Family/variant: small categorical range plot plus horizontal dot plot and decision strip.
- Data sufficiency: three recurrence distributions, four forced-edge fractions and three state-structure decisions.
- Source: JPN24 parsimony result, multitrait history summary and continuous state tables.

### Figure 3

- Question: Do observed continuous branch correlations exceed reconstruction-aware nulls?
- Takeaway: both the original and fixed JPN29-excluded results lie within their null distributions and FAIL.
- Family/variant: paired histograms with observed reference lines and a separate diagnostic inset.
- Data sufficiency: 9,999 null draws per panel; topology diagnostic n=1,000.
- Source: original and provenance-sensitivity null distributions plus continuous topology JSON.

### Figure 4

- Question: Is shared discrete transition localization stable across topologies?
- Takeaway: pairwise distributions differ and no pair is consistently positive across evidence layers.
- Family/variant: horizontal interval/density comparison centered on zero plus maximum-likelihood point markers.
- Data sufficiency: 969–1,000 topology values per pair, summarized by q05/median/q95 and positive fraction.
- Source: latest module-overlap topology sensitivity and branch-length-aware overlap JSON.

## QA gates

- All plotted numerical values are read from frozen files or asserted against the headline table.
- Standard magnitude axes include zero.
- Histograms use the same binning and x scale when comparisons share units.
- Scientific decision text is adjacent to the evidence, not inferred from colour.
- No title or annotation contains `coordinated evolutionary remodeling`, `independent origins`, `convergence`, `adaptation` or `rate`.
- Every figure has matching legend and alternative text in `JEB_QUESTION_RESULT_FIGURE_MAP_V1.md`.
