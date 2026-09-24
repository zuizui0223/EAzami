# Held-out East-Asia source-complete trait census v2 result

Status: **FROZEN BEFORE V2 OCCURRENCE QC AND BEFORE ANY ENVIRONMENT EXTRACTION**  
Date: 2026-09-24  
Workflow run: 36014106532  
Artifact: 10814305807  
Artifact SHA256: `505a4aeb797f677e0133bdaf212a45e70ea19aa792b793308b0aea865a241673`

## Census completeness

The preregistered source-complete census recovered:

- all **46/46** lower taxa linked from the Flora of China *Cirsium* genus page;
- **19** printed *Cirsium* concepts in the selected NIBR national checklist lane.

No GBIF occurrence query or environmental raster was opened during this step.

## Orientation

Across eligible source rows, explicit binary states were:

- 8 downward/nodding rows;
- 15 upward/erect rows.

Two taxa (*C. schantarense* and *C. vlassovianum*) occur in both source lanes. After exact-taxon deduplication, the frozen primary candidate set is:

- **7 downward/nodding taxa**;
- **14 upward/erect taxa**;
- **21 unique explicit-binary taxa total**.

Ambiguous descriptions remain excluded.

These 21 taxa now enter the unchanged strict V2 occurrence gate.

## Stickiness

The source-complete census recovered two explicit sticky concepts:

- *Cirsium setidens*;
- *C. setidens* var. *niveoaraneum*.

It recovered **zero explicit nonsticky held-out concepts** under the preregistered ontology.

Therefore stickiness is already:

`not_evaluable_no_nonsticky_source_complete_candidate`

before occurrence or environmental data.

The V2 stop rule is applied: no additional taxon-selection scheme and no ecological extraction will be used to rescue external stickiness confirmation.

## Next gate

Orientation only:

1. merge/freeze this complete census;
2. query GBIF for the 21 unique explicit-binary taxa;
3. apply the unchanged strict QC: explicit coordinate uncertainty <=10 km, coordinate-quality filters, exact-coordinate deduplication, deterministic 0.1-degree thinning, n>=3;
4. require >=2 surviving taxa per state;
5. only if that gate passes, freeze the surviving panel before opening BIO15/BIO1.

The environmental endpoints remain unopened.
