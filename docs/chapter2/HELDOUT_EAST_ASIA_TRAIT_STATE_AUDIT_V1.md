# Held-out East-Asian trait-state audit v1

Status: **trait-only candidate pool frozen before occurrence-derived climate extraction**  
Date: 2026-09-18

## Result

The orientation candidate pool contains **11 explicit-state taxa** outside the frozen Japan–Taiwan discovery concepts:

- downward/nodding: 5;
- upward/erect: 6.

The pool was assembled from botanical/taxonomic descriptions only. Environmental outcomes were not used to choose taxa or states.

The stickiness pool currently contains only:

- one explicit sticky taxon: *Cirsium setidens*;
- one explicit nonsticky/non-glutinous taxon: *Cirsium reflexiphyllarium*.

Under the preregistered >=2 taxa per state rule, **stickiness is not yet confirmatory**. This is a resolution result, not evidence against a wetness association.

## Fail-closed decisions

- A dark or resinous phyllary gland is **not** automatically converted to the EAzami sticky state.
- “erect or nodding”, “nodding to erect”, and “± nodding” are treated as ambiguous, not majority-coded.
- exact discovery concepts and taxonomically entangled concepts are excluded from held-out confirmation;
- new species are queried under exact accepted names only; historical look-alike identifications are not reassigned without specimen-level redetermination.

## Next locked gate

Run occurrence-support QC only, without environmental extraction:

1. exact-name GBIF retrieval under the frozen alias registry;
2. CN/KR provenance filter where applicable;
3. coordinate uncertainty <=10 km;
4. exact-coordinate deduplication;
5. deterministic 0.1-degree thinning;
6. retain taxa with >=3 thinned records.

The surviving set is then the deterministic orientation primary panel. The ecological endpoints remain unopened until that panel and the exact test script are committed.

## Repository execution record

This frozen audit is carried by PR #233. The PR workflow is climate-blind and may only determine occurrence support under the rules above; it must not sample environmental rasters before the surviving primary panel is committed.
