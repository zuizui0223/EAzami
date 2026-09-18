# Held-out occurrence-support result v1

Status: **FROZEN POST-PREREGISTRATION, BEFORE ENVIRONMENT EXTRACTION**  
Date: 2026-09-18  
Workflow run: 35325837106  
Artifact: 10538343240  
Artifact SHA256: `ac644e7962058adf814bbdcb83961bbbea4e812d6d1a18d7560a7162915621a8`

## Result

The preregistered strict occurrence gate was executed without opening any environmental raster.

### Orientation

Only two candidate taxa passed the primary gate:

- *Cirsium schantarense* — downward/nodding — 8 thinned occurrences;
- *Cirsium vlassovianum* — upward/erect — 8 thinned occurrences.

This leaves one lineage per state. The frozen minimum is >=2 taxa per state.

**Primary held-out orientation confirmation status: `not_evaluable_state_replication`.**

No BIO15/BIO1 value is extracted or inspected under v1.

### Stickiness

Only *Cirsium setidens* passed:

- sticky — 25 thinned occurrences.

The only frozen nonsticky candidate, *C. reflexiphyllarium*, has no exact GBIF taxon match under the frozen rule.

**Primary held-out stickiness confirmation status: `not_evaluable_state_replication`.**

No BIO12/GSP value is extracted or inspected under v1.

## Why most Chinese candidates failed

The failure is mainly a coordinate-QC resolution ceiling rather than a lack of raw GBIF records. Examples:

- *C. lidjiangense*: 28 exact-name raw records, 0 records with explicit <=10 km uncertainty;
- *C. argyracanthum*: 26 exact-name raw records, 0 primary-quality records;
- *C. tianmushanicum*: 5 exact-name raw records, 0 primary-quality records.

The primary contract is not relaxed after seeing this result.

## Scientific interpretation

This is **not** a failed ecological prediction. The ecological endpoints were never opened.

The v1 result is only:

> the preregistered external taxon panel is too sparsely replicated under strict GBIF coordinate-uncertainty QC to provide a confirmatory ecological test.

Any later broader-source or broader-taxon analysis must be separately preregistered and labelled v2; it cannot overwrite v1.
