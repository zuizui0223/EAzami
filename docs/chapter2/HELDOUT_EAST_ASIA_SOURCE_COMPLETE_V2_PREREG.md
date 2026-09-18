# Held-out East-Asia source-complete expansion preregistration v2

Status: **FROZEN BEFORE V2 TRAIT CENSUS AND BEFORE ANY HELD-OUT ENVIRONMENT EXTRACTION**  
Date: 2026-09-18

## Why v2 exists

V1 remains frozen and failed only at the occurrence/state-replication gate:

- orientation retained one downward and one upward lineage;
- stickiness retained one sticky lineage and no nonsticky lineage;
- no ecological endpoint was opened.

V2 is not allowed to relax that result or cherry-pick taxa that are known to have good GBIF coverage.

Instead, V2 changes only the **trait-candidate ascertainment frame** from a hand-assembled candidate list to a source-complete census.

## Source-complete census rule

Before any V2 occurrence query:

1. enumerate every `Cirsium` taxon in the current Flora of China treatment whose accepted concept is in mainland China;
2. enumerate every accepted Korean `Cirsium` taxon available through the selected NIBR national flora/taxonomic source lane;
3. retain exact source concepts and explicit source-backed synonyms in a separate provenance table;
4. remove any taxon that is the same biological concept as a frozen Japan–Taiwan discovery taxon;
5. code capitulum orientation from description text only;
6. freeze the complete coded/uncoded census before checking GBIF occurrence support.

No taxon may enter or leave the V2 trait census because of its occurrence count, climate niche or expected hypothesis direction.

## Orientation ontology

Primary binary states are deliberately narrow:

- `downward_or_nodding`: the source explicitly says nodding, pendulous/hanging, downward, or an unambiguous equivalent;
- `upward_or_erect`: the source explicitly says erect/upright, or an unambiguous equivalent.

Exclude from the primary binary panel:

- "erect or nodding";
- "nodding to erect";
- "± nodding", "sometimes/rarely nodding" when no stable taxon state is given;
- lateral/oblique states not safely mappable to the binary ontology;
- descriptions with no explicit capitulum-orientation statement.

A taxon-level state is not silently inferred from a photograph, locality, habitat or related species.

## Stickiness ontology

V2 also records explicit involucre/phyllary stickiness where the source says sticky, glutinous, adhesive or an unambiguous equivalent.

A resinous/dark gland **does not equal stickiness** unless the source explicitly states an adhesive/glutinous phenotype.

Stickiness remains confirmatory only if >=2 eligible taxa per state later pass the unchanged strict occurrence gate.

## V2 occurrence gate

After the source-complete trait census is frozen, apply the **unchanged V1 primary occurrence QC**:

- exact accepted name plus source-backed, non-overlapping aliases only;
- occurrence provenance restricted to CN/KR as appropriate;
- present records with coordinates;
- explicit coordinate uncertainty <=10,000 m;
- reject frozen coordinate-quality issues;
- exact-coordinate deduplication;
- deterministic 0.1-degree thinning;
- >=3 thinned occurrences per taxon;
- >=2 taxa per compared state.

Missing coordinate uncertainty remains ineligible for the primary V2 test. V1 is not weakened.

## V2 ecological test

Only if the occurrence gate is evaluable:

### Orientation

Reuse the already-frozen V1 endpoints and statistic without modification:

- BIO15 D-U > 0;
- BIO1 D-U < 0;
- `S_O = (z(BIO15) - z(BIO1))/sqrt(2)`;
- one-sided exact/randomization test;
- alpha = 0.05;
- both component signs must agree.

### Stickiness

Reuse:

- BIO12 sticky-nonsticky > 0 as primary;
- GSP > 0 as secondary direction;
- same one-sided exact/randomization rule;
- >=2 taxa per state.

No new environmental predictor is introduced in V2.

## Interpretation hierarchy

- V1 = strict hand-assembled external panel, not evaluable.
- V2 = prospectively source-complete external panel after V1's resolution failure.
- If V2 is evaluable and passes, call it **prospective source-complete external confirmation**, while reporting that V2 was initiated after the V1 coverage failure.
- If V2 is not evaluable, stop external-taxon confirmation and do not keep iterating taxon lists.
- If V2 is evaluable and fails, report the failure; do not open V3 with another taxon-selection scheme.

## Stop rule

V2 is the final taxon-expansion attempt for this paper.

After the complete trait census and strict occurrence gate:

- evaluable -> execute the frozen ecological test once;
- not evaluable -> external confirmation is unavailable with current public occurrence metadata.

No climate is sampled until the V2 taxon census and occurrence-support result are separately frozen.
