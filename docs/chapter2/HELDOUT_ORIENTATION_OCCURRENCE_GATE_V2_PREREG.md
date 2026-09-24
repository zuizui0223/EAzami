# V2 held-out orientation occurrence gate preregistration

Status: **FROZEN BEFORE GBIF OCCURRENCE QUERY**  
Date: 2026-09-24

The source-complete trait census has already been frozen. Thirteen external orientation taxa (3 D, 10 U) are eligible to enter this gate.

This gate is deliberately **climate-blind**.

## Primary rules

All 13 taxa are queried under the mainland-China provenance frame because every accepted V2 orientation candidate came from the complete Flora of China lane.

A taxon passes only if:

- GBIF strict species matching returns an exact match;
- occurrence status is PRESENT;
- coordinates exist;
- coordinate uncertainty is explicitly reported and <=10 km;
- severe coordinate-quality issues are absent;
- exact coordinates are deduplicated;
- records are deterministically thinned to 0.1-degree cells;
- >=3 thinned records remain.

The surviving panel is confirmatorily evaluable only if >=2 downward/nodding and >=2 upward/erect taxa remain.

## Stop rule

If the state-replication gate fails, V2 stops and BIO1/BIO15 are not opened.

If it passes, the exact surviving panel is committed first. Only after that freeze may the already-registered BIO15-up/BIO1-down test be executed.

No taxon is added, removed, renamed or recoded based on its occurrence count.
