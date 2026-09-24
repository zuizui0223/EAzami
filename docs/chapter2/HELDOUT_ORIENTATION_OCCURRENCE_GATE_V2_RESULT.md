# Held-out orientation occurrence gate v2 result

Status: **FROZEN; EXTERNAL-TAXON CONFIRMATION STOPPED BEFORE ENVIRONMENT EXTRACTION**  
Date: 2026-09-25  
Workflow run: 36070410995  
Artifact: 10838360802  
Artifact SHA256: `b58429771b03efdc33cd83327346a980a46419a00410fdb8c9f457e111aadd42`

## Result

The preregistered climate-blind GBIF occurrence gate was run on the frozen 13-taxon Flora of China orientation panel (3 downward/nodding, 10 upward/erect).

Only one taxon passed all primary occurrence rules:

- *Cirsium vulgare* — upward/erect — 16 deterministic 0.1-degree thinned records.

No downward/nodding taxon retained >=3 thinned records under the frozen requirement for explicit coordinate uncertainty <=10 km.

Final state replication after QC:

- downward/nodding: **0 taxa**;
- upward/erect: **1 taxon**.

The preregistered evaluability requirement was >=2 taxa in each state.

Therefore:

> **External-taxon orientation confirmation is not evaluable with the current public GBIF metadata.**

## Stop rule applied

The frozen V2 stop rule is now binding.

- No additional external taxon-selection scheme will be opened for this paper.
- BIO1 and BIO15 are **not extracted** for the held-out V2 panel.
- The outcome is not an ecological null result and does not contradict the Japan–Taiwan discovery direction.
- The failure is a public occurrence-metadata resolution ceiling.

## Diagnostic detail

Several taxa have many raw exact-name occurrences but virtually no records that meet the explicit <=10 km uncertainty requirement. Examples:

- *C. schantarense*: 96 exact-name records -> 1 primary-quality thinned record;
- *C. lidjiangense*: 28 -> 0;
- *C. vlassovianum*: 182 -> 0;
- *C. argyracanthum*: 26 -> 0.

Thus the failure is driven mainly by coordinate-metadata quality, not by absence of occurrence records.

## Consequence for the manuscript programme

P3 cannot be supplied by an independent external-taxon public-data panel.

The next independent test must use a different estimand rather than relaxing this gate. The pre-existing candidate is occurrence/image-level within-taxon orientation variation from the Azami image dataset, provided that its angle coding and environmental endpoints can be frozen without reopening the Azami paper's registered analysis surface.

The external-taxon V1 and V2 failures remain reportable resolution audits, not confirmatory ecological evidence.
