# Ecological reassortment held-out confirmation preregistration v1

Status: **FROZEN BEFORE HELD-OUT ECOLOGICAL OUTCOME EXTRACTION**  
Freeze date: 2026-09-18  
Repository: `zuizui0223/EAzami`

## Purpose

This contract separates already observed discovery results from a single prospective held-out confirmation.

The manuscript-level question is:

> **Does ecological diversification act on the capitulum as one coordinated syndrome, or are component traits repeatedly reassorted across distinct ecological interfaces?**

Three evidence layers are kept separate:

1. **fitness stakes / selection mosaic** — literature synthesis establishes that pollination, antagonism and abiotic exposure can all matter, without identifying one universal dominant agent;
2. **historical decoupling** — orientation, phyllary posture and involucre stickiness have different repeated-state histories and no robust shared-transition pair in the current frozen analysis;
3. **trait-specific ecological correspondence** — the existing discovery panel suggests different ecological signals, which are not all confirmatory.

This preregistration concerns layer 3 only. It does not reopen or refit the already frozen Japan–Taiwan discovery analyses.

## Existing evidence is discovery, not prospective confirmation

The following results were known before this freeze and must never be presented as prospective tests:

### Orientation

The frozen phylogeny-conditioned result associates downward/nodding transitions with:

- higher precipitation seasonality (BIO15);
- lower annual mean temperature (BIO1).

The common9 static tip-state screen did not show an exceptional D-versus-U split in the common Japan provenance panel, so the transition-conditioned result remains the relevant discovery evidence.

### Stickiness

The common9 discovery screen found a coherent precipitation lead:

- BIO12: sticky - nonsticky = +1.311 SD;
- GSP: sticky - nonsticky = +1.278 SD;
- BIO15: sticky - nonsticky = +1.048 SD.

BIO12 and GSP did not survive the frozen 27-row BH multiplicity correction and remain exploratory discovery leads.

### Phyllary posture

Public state replication is insufficient for a useful abiotic confirmation. Climate/common9 cannot directly test antagonist access.

**Therefore no directional abiotic confirmatory hypothesis is registered for phyllary posture.**

## Held-out population

The held-out panel must be assembled without inspecting held-out environmental outcomes.

### Geographic scope

Primary candidate pool:

- Korean Peninsula;
- mainland China;
- other East Asian `Cirsium` taxa outside the frozen Japan–Taiwan discovery concepts, only if the same eligibility rules can be applied.

### Independence rule

A taxon is ineligible if it is:

- one of the frozen discovery concepts;
- a synonym, rank variant or taxonomic reassignment of a frozen discovery concept;
- represented only by occurrence records that cannot be separated from a frozen discovery concept.

The exact eligible taxon list and trait-state provenance must be committed **before** occurrence-derived climate summaries are inspected.

### Trait-state coding gate

Trait states must be coded from botanical/floristic/herbarium sources without using climate values.

Required provenance fields:

- accepted analysis name;
- source name as published;
- source citation / stable URL or accession;
- verbatim diagnostic text or scored character;
- binary/state mapping rule;
- ambiguity flag;
- coder note.

Ambiguous taxa are excluded from the primary confirmation rather than resolved using ecological information.

A confirmatory trait must retain **at least two eligible taxa in each compared state after the frozen occurrence gate**. A 1-vs-many or 1-vs-1 contrast is lineage-confounded and is reported as not confirmatory, regardless of its numerical effect.

## Occurrence and environment contract

After the taxon/state inventory is frozen, occurrences are extracted under the existing EAzami provenance philosophy:

- exact accepted names plus a source-backed alias table;
- geographic filtering to the registered held-out provenance frame (China/Korean Peninsula are provenance filters, not biological region classes);
- coordinate uncertainty <= 10,000 m;
- removal of records lacking usable coordinates;
- exact-coordinate deduplication before thinning;
- 0.1-degree spatial thinning using one deterministic representative per grid cell;
- primary minimum gate = >=3 independent thinned occurrences per taxon;
- CHELSA/current environmental extraction using the same variable definitions as the discovery analysis.

No taxon may be added, removed or recoded based on the direction of its climate niche.

## Prospective confirmatory hypotheses

### H-O: orientation confirmation

**Primary ecological hypothesis**

Held-out downward/nodding taxa occupy a climate niche shifted toward the same frozen discovery direction:

`BIO15(D-U) > 0` and `BIO1(D-U) < 0`.

The primary confirmatory statistic is the preregistered composite

`S_O = (z(BIO15) - z(BIO1)) / sqrt(2)`, with the prediction `S_O(D) > S_O(U)`.

BIO15 and BIO1 component effects are always reported separately with uncertainty.

**Confirmation rule**

The orientation confirmation passes only if:

1. the held-out composite effect is positive in the preregistered direction;
2. BIO15 has a positive D-U sign;
3. BIO1 has a negative D-U sign; and
4. the one-sided randomization/permutation test for the composite crosses alpha = 0.05 under the frozen eligible panel.

A result with the correct composite but a reversed component sign is reported as partial directional agreement, not confirmation.

### H-K: stickiness confirmation

**Primary ecological hypothesis**

Held-out sticky taxa occupy wetter niches than nonsticky taxa.

The **single primary endpoint is BIO12**:

`BIO12(sticky-nonsticky) > 0`.

GSP is a preregistered secondary directional endpoint:

`GSP(sticky-nonsticky) > 0`.

BIO15 is exploratory only.

**Confirmation rule**

The stickiness confirmation passes only if:

1. the held-out BIO12 effect is positive; and
2. the one-sided randomization/permutation test for BIO12 crosses alpha = 0.05.

GSP agreement strengthens interpretation but cannot rescue a failed BIO12 primary test.

### H-P: phyllary posture

There is **no confirmatory abiotic direction**.

Any climate association is exploratory.

The mechanistic hypothesis remains biotic/mechanical:

> validated phyllary/spine architecture may alter antagonist access, with a possible pollinator-access cost.

Public occurrence climate is not a direct test of that mechanism.

## Analysis hierarchy

Primary analyses are taxon-level and outcome-blind with respect to trait coding.

1. compute each eligible taxon's thinned occurrence-based environmental niche summary;
2. standardize environmental endpoints within the frozen held-out analysis frame;
3. compute the preregistered orientation composite and stickiness BIO12 contrast;
4. use exact/randomization label tests where feasible;
5. report raw effect sizes and uncertainty regardless of threshold crossing.

If a defensible broader East-Asian phylogeny covering the held-out taxa is available without outcome-dependent taxon selection, an ancestry-aware model is added as a **predeclared robustness analysis**, not used to redefine the primary endpoint after results are seen.

Region-stratified sensitivity analyses are also secondary robustness checks. They do not replace the primary held-out test.

## Manuscript prediction hierarchy

The manuscript distinguishes three levels:

### P1 — historical decoupling

Already observed/frozen, not prospective:

> component traits do not share one synchronized transition history.

### P2 — trait-specific ecological correspondence

Discovery-level evidence:

> component traits differ in the ecological evidence currently associated with them.

Orientation has a transition-conditioned climate direction; stickiness has an exploratory wetness lead; phyllary posture lacks adequate public abiotic state replication.

### P3 — out-of-sample confirmation

Prospective test frozen here:

> preregistered ecological directions for orientation and stickiness replicate in taxa excluded from the discovery panel.

Only P3 can be described as held-out confirmation.

## Claim boundaries

Even if both confirmatory tests pass, this study may claim:

- repeated historical reassortment of component traits;
- trait-specific ecological correspondence;
- out-of-sample recurrence of preregistered ecological directions;
- consistency with partially independent ecological interfaces.

It may **not** claim from these data alone:

- adaptation;
- direct natural selection;
- convergence;
- historical climatic causation;
- a proven antagonist mechanism for phyllary posture;
- a universal defensive mechanism for stickiness;
- modular evolvability as an established causal property.

Those require mechanism / fitness evidence or stronger evolutionary tests.

## Failure is informative

The held-out confirmation must be retained and reported if it fails.

Examples:

- orientation fails but stickiness passes -> ecological correspondence is trait-specific but not generally transportable;
- stickiness fails -> the common9 precipitation lead remains discovery-only;
- both fail -> historical decoupling remains, but current ecological reassortment lacks external confirmation;
- phyllary remains unresolved -> do not convert absence of climate signal into evidence for a biotic mechanism.

## Execution lock

Before any held-out climate outcome is inspected, commit:

1. exact taxon eligibility table;
2. trait-state provenance table;
3. alias registry;
4. minimum occurrence gate and thinning/QC rules;
5. exact analysis script implementing the tests above.

After those are frozen, execute the held-out analysis once. Any later deviations must be versioned and labelled sensitivity/exploratory.
