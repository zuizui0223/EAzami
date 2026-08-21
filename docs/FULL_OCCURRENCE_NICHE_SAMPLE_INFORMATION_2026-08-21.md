# Full-occurrence niche → sampling information gate

Status: 2026-08-21

## Question

Can public full-occurrence environmental information reduce or reposition the current doctoral sampling plan **before** adding new biological samples?

The answer is **yes for population placement, but mostly no for population-count expansion**.

This gate intentionally precedes any new broad sampling. It asks whether the existing P001–P014 design already spans the major public occurrence × CHELSA environmental strata and where the two still-unspecified *C. brevicaule* intermediate slots should be placed.

## Data and method

Live workflow:

- GitHub Actions run `32442704708`;
- artifact `9432992392`, `eazami-focal-occurrence-niche-sample-info-v1`;
- digest `sha256:dfc7a4fe8e3e83bb5e43954211fec93dfdac8c14a0704cc6205f05409b49797c`.

The audit uses:

- GBIF occurrence search, Japan, present records with coordinates;
- record-level **source `scientificName` preservation** before analysis;
- strict coordinate uncertainty <=10 km when >=10 such records exist, otherwise an explicitly labelled inclusive fallback;
- one record per taxon × 0.05 degree cell;
- CHELSA v2.1 BIO1/BIO4/BIO12/BIO15, 1981–2010;
- pooled standardized environmental PCA plus geographic coordinates;
- deterministic K-means/silhouette strata as a **sampling coverage diagnostic**, not a biological species-delimitation model.

## Critical taxonomy correction

GBIF synonym resolution cannot be used as the focal taxon definition for this question.

For example:

- *C. brevicaule* query: 253 downloaded records, but only **166** retained the source name *C. brevicaule*; **87** records were excluded after source-name checking;
- *C. sieboldii* query: 438 downloaded, **363** source-name matched and **75** synonym/other-source records were excluded.

The first unguarded run incorrectly promoted a Yonaguni *C. irumtiense* record as a *C. brevicaule* sampling candidate because GBIF treats *irumtiense* as a synonym under the accepted *brevicaule* concept. The source-name guard removes this failure.

A second guard rejects an isolated occurrence from becoming P003/P004 merely because it is environmentally extreme. Existing intermediate slots require:

1. source taxon-name match;
2. at least one corroborating public occurrence within 75 km;
3. positive intermediate bridge position between the declared Amami and Okinawa region anchors;
4. different environmental/geographic clusters and >=50 km separation between the two selected strata.

These guards protect field design; they are not new taxonomic or range definitions.

## Result by focal system

| taxon | planned populations | environment-complete thinned occurrences | best diagnostic clusters | current decision |
|---|---:|---:|---:|---|
| *C. brevicaule* | 4 | 35 | 3 | keep 4; position P003/P004 from the existing gap |
| *C. irumtiense* | 4 | 44 | 4 | keep 4; no niche-only expansion |
| *C. pendulum* | 4 | 19 | 4 | keep 4; W/C linkage is the next discriminator |
| *C. sieboldii* | 2 | 30 | 6 | conditional replication gap; do not expand until W/C states are linked to populations |
| *C. lineare* | conditional | 13 | 6 | too sparse for a six-population inference; retain conditional control status |
| *C. dipsacolepis* | conditional | 95 | 2 | two broad strata are compatible with a two-population control if activated |

The cluster number is an exploratory coverage diagnostic. It is **not** a population number estimator and is especially unstable for sparse taxa.

## P003/P004 reverse inference

After taxonomy and local-support guards, the live run selects two different *C. brevicaule* bridge strata:

- a **southern-Amami bridge stratum** around the Yoron/Okinoerabu part of the chain (the exact top public occurrence can move within this regional cluster under plausible weighting changes);
- **Tokunoshima** as the second, environmentally distinct intermediate stratum.

Weight sensitivity confirms that the exact public occurrence changes, but the regional solution remains one southern-Amami bridge cluster plus Tokunoshima.

Therefore the actionable design is:

> P003/P004 should target **Tokunoshima** and a **southern-Amami bridge population (Yoron/Okinoerabu corridor)**, with the exact locality still `TBD_field_verified`.

No public occurrence coordinate is promoted to a collecting site.

## What the niche result does to sample size

The result does **not** justify increasing core190 now.

- *brevicaule*, *irumtiense* and *pendulum* already have at least as many planned populations as the major public niche strata detected here.
- *sieboldii* is the only core system with a clear niche-coverage warning (2 planned versus 6 diagnostic strata), but GBIF occurrences do not reliably identify white versus coloured morphs. Adding four arbitrary populations would therefore answer the wrong question.

The next *sieboldii* decision is conditional:

> map verified W/C populations into the niche space first; add a **second matched W/C pair** only if P013/P014 do not provide an independent environmental/context replicate.

## Relation to ancestral-state reconstruction

This niche gate does not solve the Arenicola ancestral-colour direction.

Current ASR evidence remains:

- the *brevicaule–irumtiense* pair alone is directionally unresolved;
- the current coloured-rich sister context favors a coloured Arenicola ancestor / white loss in *brevicaule* by one parsimony step;
- the result reverses when deeper root state is forced white.

Thus the main deep-ASR information gap is **broader sister/root state and trusted branch-length topology**, not another arbitrary focal population.

The core190 population replication instead addresses the different historical question that species-level ASR cannot answer: retained ancestral variation versus introgression/gene flow versus lineage-specific change.

## What remains to join before a final sample-information score

The current niche-only score intentionally omits:

- ASR uncertainty reduction;
- same-environment/different-trait contrast;
- independent transition value;
- population-ancestry bridge value.

A future composite sample-value score must join those components rather than pretending environmental novelty alone is total information gain.

For now the sampling consequence is deliberately conservative:

1. keep core190;
2. position P003/P004 at the two supported bridge strata;
3. prioritize morph-linked niche placement for *pendulum* and especially *sieboldii*;
4. do not activate *lineare* / *dipsacolepis* controls until Aim 1 requires them;
5. do not add broad mainland sampling before the nuclear/ASR gate identifies a branch-specific information deficit.

## Claim boundary

This is a public-occurrence environmental coverage analysis. It does not infer adaptation, population ancestry, gene flow, colour morph, species limits or exact field localities. GBIF sampling bias and coordinate uncertainty remain explicit limitations; *C. irumtiense* in particular has only four records with reported coordinate uncertainty <=10 km, so its niche summary uses the predeclared inclusive fallback and requires field verification.
