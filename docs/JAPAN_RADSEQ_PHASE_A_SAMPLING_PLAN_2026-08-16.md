# Japan RAD-seq Phase A sampling plan — 2026-08-16

## Decision

The primary Japanese/East Asian **species backbone is not assigned to RAD-seq**. Moreyra 2025 already provides a Compositae1061-compatible nuclear framework for 38 Japanese paper taxon concepts, and the current EAzami maximum-public analysis is designed to reconstruct/test that backbone with BWA/BLASTx, concatenation and ASTRAL.

RAD-seq is assigned to the shallower question that the species tree cannot answer well: population ancestry, colour-morph history, gene flow, reticulation and geographically structured lineages within the young Japanese radiation and Ryukyu systems.

A same-library Japan-wide RAD tree can be built as a **secondary sensitivity/network** if desired, but it must not replace the target-capture species tree, especially across mixed ploidy.

## Tissue-inventory boundary

No repository-grounded inventory of already collected fresh/silica-dried field tissue was found on 2026-08-16. Counts below are therefore **new-sampling targets from a zero-confirmed-tissue baseline**. Once a physical tissue inventory is recovered, subtract only samples whose individual identity, voucher/locality and DNA usability are verified.

## Two distinct sampling products

### Product A — population-aware evolutionary panel (recommended)

This is the panel that directly answers the current EAzami hypotheses.

| system | minimum defensible | recommended | geographic design | role |
|---|---:|---:|---|---|
| *C. pendulum* Japan | 40 | 60 | white 20–30 + nearby coloured 20–30; split across >=2 populations/state where possible | recent white loss vs standing variation |
| *C. sieboldii* Japan | 30 | 40 | white 15–20 + coloured 15–20; matched wetland regions | independent within-species replicate |
| *C. lineare* Japan | 16 | 24 | 2–3 populations spanning western Honshu/Shikoku/Kyushu | strongest replicated secondary-history anchor |
| *C. dipsacolepis* Japan | 16 | 24 | 2–3 grassland populations spanning separate regions, prioritizing verified extant sites | candidate secondary arrival + within-Japan structure |
| *C. brevicaule* | 60 | 75 | 4–5 island populations ×15; Amami Ōshima and Okinawa Honto mandatory endpoints | central-Ryukyu population history |
| *C. irumtiense* | 60 | 75 | 4–5 island populations ×15; Miyako and Yonaguni mandatory endpoints; Ishigaki/Iriomote core | southern-Ryukyu population history |
| **total** | **222** | **298** |  |  |

A lower-budget Arenicola pilot using 12 individuals/population would reduce the total, but it falls below the currently frozen 15–20/population target and must be labelled a pilot rather than the final population-genomic panel.

### Product B — all-Japan same-library RAD sensitivity tree (optional)

If a same-batch RAD dataset is wanted for all 38 Moreyra Japanese paper taxon concepts, use **>=3 independently collected wild individuals per concept** as a coarse minimum: 38 × 3 = **114 individuals**.

This product is a sensitivity/network, not the primary species tree. The 38 units are still paper taxon concepts rather than a final authority-backed accepted-name list, and several Moreyra representatives were cultivated, continental or metadata-conflicted. A wild-Japan RAD panel would therefore improve geographic provenance, but it does not solve mixed-ploidy orthology by itself.

If Product A is completed first, it already oversamples four Japan-38 focal concepts (*pendulum*, *sieboldii*, *lineare*, *dipsacolepis*). Completing a >=3-individual RAD representation of the remaining 34 paper concepts would then require approximately **102 additional individuals**, subject to accepted-name reconciliation.

## Field blocks

Exact protected/rare white-morph coordinates are deliberately not frozen here; verify current occurrence, collecting permission and voucher identity before field deployment.

### Block 1 — northern/eastern Honshu to Hokkaido: *C. pendulum*

- Secure reproducible Japanese white populations first.
- Pair each white population with the nearest feasible coloured population rather than contrasting distant colour states.
- Add a northern coloured anchor within the Japanese range to connect the Japanese population layer to the existing Trans-Baikal nuclear tip.

### Block 2 — Honshu/Shikoku wetlands: *C. sieboldii*

- Sample white and coloured morphs in matched wetland regions.
- Prefer repeated populations over one large locality.
- The existing Moreyra nuclear tip is cultivated; wild Japanese RAD sampling therefore adds real geographic information rather than species-placement novelty.

### Block 3 — western Japan: *C. lineare* + *C. dipsacolepis*

- *C. lineare*: target geographically separated western Honshu/Yamaguchi, Shikoku and Kyushu populations where current occurrence is verified.
- *C. dipsacolepis*: use separated grassland populations; do not rely on historical localities without current confirmation. The Moreyra target-capture sample already anchors Shikoku/Tokushima nuclear placement, so RAD should capture within-Japan structure rather than duplicate one accession.

### Block 4 — central Ryukyus: *C. brevicaule*

Minimum four-island/population design:

1. Amami Ōshima — mandatory terminal/deep-divergence endpoint;
2. one Amami-group intermediate population (e.g. Tokunoshima/Kikai where verified);
3. one southern Amami-group population (Okinoerabu/Yoron where verified);
4. Okinawa Honto — mandatory main-island endpoint.

Recommended fifth population: one Okinawa-group satellite island with verified material.

### Block 5 — southern Ryukyus: *C. irumtiense*

Minimum four-island/population design:

1. Miyako — mandatory northern endpoint across the Miyako Strait;
2. Ishigaki;
3. Iriomote — type-area/core population;
4. Yonaguni — mandatory terminal/deep-divergence endpoint.

Recommended fifth population: Hateruma/Taketomi/Kohama or another verified Yaeyama satellite to separate island effects from simple endpoints.

## One-individual identity package

Every RAD individual must have one immutable `individual_id` linking:

- accepted/source taxon name and field determination;
- GPS/locality and population ID;
- voucher or voucher-linked photo;
- standardized flower-colour record and image;
- silica/fresh leaf DNA source;
- flow-cytometry/genome-size record where possible;
- chromosome/cytotype literature or direct observation status;
- plastid companion haplotype;
- optional floral RNA/pigment material for focal colour systems.

## Cytonuclear design

Do not concatenate plastid loci into the nuclear RAD/species tree and call the result one history.

Use two explicit layers:

1. **nuclear RAD ancestry/network** — population structure, admixture, genomic distances;
2. **plastid maternal haplotype layer** — same individuals or matched representatives.

Then quantify discordance by asking whether plastid haplotypes track the same geographic/morph clusters as nuclear ancestry. Discordance is a biological result to test for chloroplast capture, introgression or lineage sorting; it is not an error to be forced away.

## Ploidy rules

### 1. Cytotype before a shared SNP matrix

Taxon names are not sufficient proxies for ploidy. Measure relative genome size/flow cytometry on the same RAD individuals when feasible, or at minimum a representative subset from every population. Retain known chromosome counts as separate evidence.

### 2. Do not force mixed cytotypes into a diploid caller

- process diploid, tetraploid and higher-ploidy groups separately at the genotype-calling stage;
- use ploidy-aware genotype likelihood/calling and expected-allele-count filters;
- flag loci with excess depth, excess allele count or extreme heterozygosity as possible paralog/homeolog collapse;
- build strict shared-locus sensitivities before any cross-ploidy distance/tree interpretation.

### 3. Cross-ploidy organismal history comes from the target-capture backbone

RAD may reveal ancestry and reticulation within comparable cytotype groups. Across deeply divergent/mixed-ploidy taxa, use the Compositae1061 species-tree framework as the primary organismal scaffold and map RAD population clusters onto it.

### 4. Genome size is not automatically ploidy

Keep chromosome number/ploidy and 2C genome size as separate variables. Large genome-size differences can occur without chromosome-number change in East Asian *Cirsium*.

## Current known focal cytotypes

The frozen taxon-level NMNS records currently include:

- *C. aomorense*: 2n=34, diploid;
- *C. sieboldii*: 2n=34, diploid;
- *C. nipponicum*: 2n=68, tetraploid;
- *C. alpicola*: 2n=102, hexaploid;
- *C. dipsacolepis*: 2n=34, diploid.

These are taxon-level records and must not be assumed to be the cytotype of every new population or the exact Moreyra sequenced individual.

## What the present nuclear–plastid evidence does and does not say

- Deep Cardueae nuclear/plastid studies are broadly congruent with a small number of conflicts; cytonuclear discordance is not universal.
- At reticulate/polyploid taxa, conflict can be strong: *C. vulgare* provides a demonstrated case where the nuclear genome contains substantial *Cirsium* + *Lophiolepis* ancestry while organellar data group with *Cirsium*.
- For the Japanese radiation specifically, **the fraction/number of discordant nodes is not yet quantified**. EAzami currently treats the extent of East-Asian cytonuclear discordance as an open question because a matched Japan-wide nuclear-versus-plastid topology set is not yet frozen.
- Therefore no “X% different” claim should be made yet. Phase A should create individual-level nuclear + plastid data specifically so this can be measured rather than inferred from separate publications.

## Stop rules

- Do not call the optional 114-sample RAD sensitivity tree the definitive Japanese species tree.
- Do not pool all ploidies into one diploid SNP matrix.
- Do not infer ploidy from genome size alone.
- Do not treat plastid topology as a substitute for the nuclear species tree.
- Do not freeze exact white-morph collecting sites without current occurrence/permission confirmation.
- Do not expand to generic mainland-China RAD sampling until the public nuclear tree identifies a branch-specific information gap.
