# Held-out East-Asia source-complete trait census v2 result

Status: **FROZEN BEFORE V2 OCCURRENCE QUERY**  
Date: 2026-09-24

Validated source-only workflow: **36014935082**  
Artifact: **10814118268**  
Artifact SHA256: `1db3a53fa9f5ca8faf3f92372b712850d92af681347b90730de8b7bf3193131d`

## What was completed

The preregistered source-complete expansion was executed without opening a V2 GBIF occurrence endpoint or any environmental raster.

- Flora of China: **46/46** linked *Cirsium* taxa recovered.
- NIBR checklist lane: **18** *Cirsium* concepts after removing the genus-author heading.
- Discovery overlap was excluded conservatively at binomial level.

The accepted coding is deliberately fail-closed. `± nodding` and mixed erect/nodding descriptions remain ambiguous, and orientation is read only from clauses whose grammatical subject is `Capitulum/Capitula`. Thus descriptions such as “stems erect ... below capitula” do not create an erect-head state.

## Orientation

Among held-out eligible rows:

- downward/nodding: **3 taxa**;
- upward/erect: **10 taxa**;
- ambiguous: **8 rows**;
- unknown: **33 rows**.

The 13 explicit-state taxa are frozen in `data/evidence/heldout_east_asia_orientation_candidate_panel_v2.csv`.

Therefore orientation has enough **trait-state replication** to proceed to the still-unopened strict occurrence gate.

## Stickiness

The source-complete census contains:

- sticky: **1 eligible taxon** (*Cirsium setidens*);
- nonsticky: **0**;
- unknown: **53**.

The sticky species state was not inherited by `C. setidens var. niveoaraneum`, and resinous/dark glands in Flora of China descriptions were not converted into stickiness.

Therefore:

> **V2 stickiness confirmation is blocked at the trait-replication gate before occurrence or climate analysis.**

This is not an ecological null result.

## Next gate

Only the frozen 13-taxon orientation panel proceeds.

The V2 occurrence step must retain the preregistered primary rules unchanged:

1. mainland-China provenance for the Flora of China candidate panel;
2. exact accepted taxon names plus only source-backed non-overlapping aliases;
3. PRESENT records with coordinates;
4. explicit coordinate uncertainty <=10 km;
5. coordinate-quality issue filtering;
6. exact-coordinate deduplication;
7. deterministic 0.1-degree thinning;
8. >=3 thinned occurrences per taxon;
9. >=2 taxa in both D and U after filtering.

No BIO1/BIO15 value may be sampled until the surviving occurrence panel itself has been frozen.

## Claim boundary

This result establishes only that a source-complete public trait census supplies a prospectively defined external orientation candidate panel. It does not establish ecological replication, adaptation, convergence or climate causation.
