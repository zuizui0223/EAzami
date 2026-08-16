# Japanese Cirsium adaptive-radiation evidence status — 2026-08-16

## Headline

Current EAzami evidence supports **rapid radiation** strongly, supports **ecological/phenotypic diversification within young East-Asian lineages** locally, and motivates an **adaptive-radiation / evolvability hypothesis**, but does not yet demonstrate adaptive radiation of the dominant Japanese radiation as a whole.

The main unresolved transition is:

```text
rapid radiation
    ↓ already strong
radiation-success asymmetry
    ↓ already strong as an EAzami meta-pattern
ecology / trait divergence across the dominant radiation
    ↓ not yet quantified on the accepted nuclear tree
reticulation / standing variation / ploidy as evolvability
    ↓ present, but coupling to radiation success not yet tested
adaptive function / fitness
    ↓ requires focal empirical tests
adaptive radiation
```

## Evidence ladder

### E1 — Rapid Japanese radiation: strong / published conclusion

Moreyra et al. 2025 used 350 retained nuclear loci from target capture and explicitly inferred rapid Pleistocene radiations in Japan and North America, with geographic and ecological speciation invoked as diversification drivers.

EAzami treats the existence of a young Japanese radiation as established enough to test downstream hypotheses; it does not treat every internal branch as resolved.

### E2 — Diversification-success asymmetry among Japanese arrivals: strong EAzami meta-result

EAzami's source-typed Japanese-origin synthesis reconstructs 38 Japanese paper taxon concepts, with 36/38 assigned by the broad nuclear analysis to one dominant Japanese radiation.

Current history hierarchy:

- dominant radiation: 36/38 sampled Japanese taxa;
- *C. lineare*: replicated phylogenetic exception in 3/3 high-dimensional analyses and 2/2 independent high-dimensional data-generation groups;
- *C. dipsacolepis*: strong but single-data-generation-group secondary-arrival hypothesis;
- Arenicola: not established as an additional Japanese colonization.

This creates a real macroevolutionary problem: **colonization count is not diversification success**. One arrival generated most sampled Japanese diversity while rare secondary histories did not.

### E3 — Phenotypic and ecological differentiation in young lineages: locally supported, radiation-wide unresolved

Published East-Asian phylotranscriptomic studies show that lineages diverged during the Quaternary while also differing in morphology, corolla colour, genome size, geographic ranges and ecological niches.

Examples include:

- *C. brevicaule* vs *C. irumtiense*: clear species/geographic break and strong morphology/genome-size differentiation;
- Taiwanese *C. japonicum* varieties: lineage-specific morphology, genome-size trajectories, colour polymorphism and ecological-niche contrasts;
- Nipponocirsium: recent Japanese/Taiwanese divergence accompanied by chromosome-number/dysploid/polyploid differentiation.

These examples show that substantial phenotype/ecology can diverge on short evolutionary timescales. They do **not** yet quantify whether the dominant Japanese 36-taxon radiation has elevated trait or niche divergence relative to *C. lineare* / *C. dipsacolepis*.

### E4 — Trait modularity / phenotypic disparity: suggestive, not evolutionary-rate evidence

The independent `zuizui0223/azami` Chapter 1 image-phenomics result shows substantial visible variation below assigned-species means across multiple capitulum endpoints and no common cross-module mapping between visible dispersion and within-species spatial climate association after precision correction.

This supports the idea that colour, orientation, outline and involucral architecture should be treated as partly independent modules.

Boundary: the current Azami result is not genetic variance, adaptation or an evolutionary-rate test, and most Chapter-1 taxa are not direct tips in a resolved *Cirsium* species tree.

### E5 — ILS / reticulation / gene flow: presence supported, radiation-success coupling unresolved

Moreyra 2025 reports phylogenomic incongruence consistent with hybridization and incomplete lineage sorting.

Chang 2026 independently shows reticulate patterns and possible gene flow within the Taiwanese *C. japonicum* complex, including dense network structure in some varieties and colour polymorphism that does not map perfectly onto the taxon tree.

Thus genomic discordance is a real biological feature, not merely a technical nuisance.

What is not yet known is whether the dominant Japanese radiation has **more** discordance/reticulation than secondary histories, or whether lineages with higher discordance show more trait transitions.

### E6 — Ploidy / chromosome / genome-size dynamics: presence supported, causal role unresolved

East-Asian *Cirsium* contains diploid, tetraploid and higher-ploidy lineages; Japanese focal records include 2x, 4x and 6x states. Nipponocirsium shows recent dysploid/polyploid evolution, while Chang 2026 demonstrates large independent 2C genome-size shifts even without chromosome-number change.

This establishes cytogenetic dynamism during recent lineage formation.

It does not show that ploidy/genome-size change caused the dominant Japanese radiation or increased diversification rate.

### E7 — Repeated flower-colour transitions: pattern supported, rate/mechanism incompletely resolved

Repeated white or W/C-polymorphic states occur in separated East-Asian nuclear contexts.

EAzami HMM2 analysis shows:

- 4/4 reviewed polymorphic systems lose state multiplicity when compressed to a single species-tip `P` state;
- only var. *takaoense* currently has direct W/C morph-linked high-dimensional nuclear samples;
- in that one testable system, population/sample-aware coding increases the minimum transition count from 1 to 2;
- replicated transition-rate comparison remains unresolved because morph↔genotype linkage exists for only 1/4 reviewed polymorphic systems.

Thus the current data support under-resolution of recent trait history, not a demonstrated radiation-wide acceleration of colour evolution.

## Current adaptive-radiation verdict

### Supported now

1. A young, rapid Japanese *Cirsium* radiation exists.
2. Diversification success is strongly asymmetric among Japanese colonization histories.
3. Young East-Asian *Cirsium* lineages can accumulate substantial morphological, colour, ecological and genome-size differences rapidly.
4. ILS/reticulation and cytogenetic change are real in the group.
5. Species-tip trait coding can erase recent within-lineage trait change.

### Not supported yet

1. The dominant Japanese radiation has a statistically elevated trait-diversification rate relative to secondary histories.
2. The dominant radiation occupies more or faster-diverging niche space after clade-age/sampling correction.
3. Reticulation/discordance or ploidy dynamics predict diversification success.
4. Specific capitulum traits drove speciation or fitness differences across the radiation.
5. The radiation meets a strict causal definition of adaptive radiation rather than rapid geographic/ecological radiation with later trait divergence.

## Existing-data analyses that should precede new sampling

### A. Accepted nuclear tree / time structure

From the 294/296 maximum-public analysis recover:

- accepted topology ensemble;
- branch lengths;
- internode compression / lineage accumulation in the dominant Japanese radiation;
- robust placement of *C. lineare*, *C. dipsacolepis* and Arenicola;
- gene-tree concordance/discordance metrics where possible.

This is the single largest current computational blocker.

### B. Radiation-level trait bridge

Join Azami traits to direct/reconciled EAzami nuclear tips:

- colour;
- orientation;
- outline shape;
- existing auxiliary involucre/spine proxies.

Retain within-taxon uncertainty and polymorphism rather than one forced species value.

Then test whether the dominant radiation has greater trait disparity or inferred transition density than secondary Japanese histories after age/sampling correction.

### C. Public-occurrence niche analysis

Using reconciled species/taxon concepts and spatially cleaned public occurrences, build comparable niche summaries for:

- dominant Japanese radiation;
- *C. lineare* history;
- *C. dipsacolepis* history;
- relevant continental sisters.

Primary question: does descendant richness covary with niche-space expansion/divergence rather than arrival age alone?

### D. Discordance × trait-transition table

For each supported East-Asian subclade estimate:

- gene-tree discordance/concordance proxy;
- nuclear–plastid discordance;
- ploidy/genome-size shifts;
- population-aware trait transitions;
- clade age;
- sampled richness.

HMM3/HMM4 are not promoted until these are quantified rather than coded as generic literature flags.

## New data required after existing-data ceiling

### Gate 1 — population ancestry and morph linkage

Needed to distinguish standing variation, recurrent mutation and introgression and to replicate HMM2/HMM4.

Current Phase-A target:

- *C. pendulum* Japan;
- *C. sieboldii* Japan;
- *C. lineare*;
- *C. dipsacolepis*;
- *C. brevicaule*;
- *C. irumtiense*.

Frozen population-RAD target: **222 minimum / 298 recommended individuals**, with voucher, phenotype, plastid companion and ploidy/genome-size metadata.

### Gate 2 — cytotype-complete sampling

Flow cytometry should be linked to the same RAD individuals where feasible. Taxon-level chromosome counts cannot substitute for population cytotype data.

This is required before testing whether ploidy/genome-size dynamics correlate with genomic ancestry or trait transitions.

### Gate 3 — causal morphology / ecological function

For high-information independent transitions, validate image-derived traits in the field/herbarium and test function:

- orientation manipulation → pollination vs rain/UV/thermal protection;
- colour morph comparisons → pollinator/abiotic effects + reproductive fitness;
- phyllary/spine manipulation → florivory/seed predation vs pollinator-access cost.

A radiation-wide comparative correlation is not sufficient to claim these traits are adaptive.

### Gate 4 — molecular mechanism

For replicated colour transitions:

- same-individual DNA ancestry;
- candidate coding/haplotype state;
- floral-stage RNA;
- pigment chemistry;
- phenotype;
- fitness/interaction.

This tests whether repeated phenotype uses retained regulatory machinery, introgressed alleles, standing variation or independent molecular routes.

## Minimum evidence needed to promote the phrase "adaptive radiation"

EAzami should require all of the following at least at a comparative + replicated-focal level:

1. rapid lineage diversification relative to an explicit comparator;
2. ecological/niche divergence among descendants;
3. trait divergence associated with those ecological differences on a supported tree ensemble;
4. evidence that at least representative repeated trait–environment associations affect performance/fitness;
5. sensitivity showing the result is not explained solely by colonization age, sampling, ILS/reticulation artefacts or ploidy miscalling.

Until then use: **rapid Japanese radiation**, **radiation-success asymmetry**, and **adaptive-radiation/evolvability hypothesis** rather than a demonstrated adaptive radiation.
