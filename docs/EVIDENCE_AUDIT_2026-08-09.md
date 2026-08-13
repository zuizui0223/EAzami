# Evidence audit — East Asian Cirsium phylogeny and flower-colour targets

Date: 2026-08-09

This audit records what is already resolved by recent nuclear phylogenomics and what remains missing for the Chapter 2 flower-colour transition question. It is deliberately source-backed and distinguishes known nuclear coverage from gaps that should drive RAD-seq sampling.

## 1. Chang et al. 2026: Sinocirsium + Arenicola + selected Nipponocirsium backbone

Source: Chang C-Y et al. (2026), BMC Plant Biology 26:545, DOI 10.1186/s12870-026-08097-6.

Key coverage:

- 12 Cirsium taxa, 33 Cirsium samples; 16 taxa / 37 samples including non-Cirsium calibration taxa.
- 25 newly sampled focal samples: four Taiwanese C. japonicum varieties, Japanese var. japonicum, C. morii, C. brevicaule, and C. irumtiense; 2–6 individuals per taxon.
- three Nipponocirsium species and C. lineare were additionally incorporated from prior transcriptomic data.
- 4,083 orthogroups were used for the main ASTRAL reconstruction.
- raw reads deposited under NCBI BioProject PRJNA1311153.

Resolved relationships relevant to flower colour:

- C. brevicaule and C. irumtiense are distinct Arenicola lineages.
- Taiwanese C. japonicum complex forms five lineages: Japanese var. japonicum plus four Taiwanese varieties.
- var. albescens is sister to var. takaoense; var. australe is sister to var. fukienense.
- C. brevicaule is white, C. irumtiense bluish-purple, var. albescens white, var. australe bluish-purple, and var. takaoense contains white and bluish-purple morphs.
- the paper explicitly notes reticulation / possible incomplete lineage sorting or historical introgression inside the Taiwanese complex, so a single bifurcating tree should not be treated as the only historical model.

Important limitation for EAzami:

This is a strong local backbone, not a comprehensive East Asian Cirsium tree. The paper itself states that East Asian taxa are underrepresented in broader Cirsium phylogenies. Its 12 Cirsium taxa cover only a small fraction of the reported regional diversity (~64 species in Japan and 46 in China, with additional Taiwanese taxa).

### Consequence

Do not prioritize RAD-seq merely to re-establish C. brevicaule / C. irumtiense or the four Taiwanese C. japonicum varieties as lineages. Prioritize population replication, unsampled sister lineages, and taxa whose placement changes the inferred direction/number of colour transitions.

## 2. Chang et al. 2025: Nipponocirsium nuclear backbone and ploidy complexity

Source: Chang C-Y et al. (2025), Botanical Studies 66:8, DOI 10.1186/s40529-025-00454-2.

Key coverage:

- 13 sampled individuals representing seven Cirsium species.
- all three Taiwanese Nipponocirsium species sampled with 2–3 individuals each.
- three Japanese Nipponocirsium species sampled with one individual each.
- C. lineare sampled as outgroup.
- raw reads deposited under NCBI BioProject PRJNA1158676.
- 3,321 orthogroups retained for the Cirsium phylogenetic analysis.

Taxa explicitly named in the study:

Taiwan:
- C. pengii
- C. kawakamii
- C. tatakaense

Japan:
- C. suffultum
- C. nipponicum var. incomptum
- C. kujuense

Outgroup:
- C. lineare

Ploidy/chromosome signal:

- Japanese Nipponocirsium are predominantly tetraploid 2n = 4x = 68.
- Taiwanese Nipponocirsium are predominantly 2n = 4x = 64.
- C. pengii is diploid 2n = 32.
- the paper therefore documents both polyploidization and descending dysploidy in the East Asian group.

### Consequence

Nipponocirsium is not a generic 'phylogeny gap'. It is a useful existing nuclear anchor and a test case for how RAD-seq behaves across ploidy levels. If flower-colour transitions are found in this clade, allele dosage/homeolog handling and network-aware inference become mandatory.

## 3. Immediate RAD-seq priorities after this audit

### Tier A1 — transition-direction critical

1. C. brevicaule: multiple populations across the Central Ryukyus, not because species placement is unknown, but to resolve within-species structure and test whether the white state is associated with one or multiple haplotypic backgrounds.
2. C. irumtiense: multiple southern Ryukyu populations for the same reason and for gene-flow tests against C. brevicaule-like ancestry.
3. C. japonicum var. takaoense: paired white and bluish-purple populations / individuals. This is currently the highest-information within-lineage target because colour polymorphism occurs inside one supported lineage.
4. C. japonicum var. albescens: multiple Hengchun samples to test whether fixed white shares the same genomic mechanism/haplotype as white takaoense.

### Tier A2 — missing sister/bridge lineages discovered by the colour atlas

Any Japanese or Chinese taxon that satisfies one of the following should jump directly to Tier A:

- white taxon adjacent to a coloured clade but absent from nuclear trees;
- coloured taxon nested among white taxa but absent from nuclear trees;
- within-taxon white/coloured polymorphism;
- taxon whose alternative placements change a coloured -> white -> coloured reconstruction into simple independent losses.

### Tier B — backbone completion

- Japanese and Chinese species absent from both Chang transcriptomic backbones and from modern broad nuclear phylogenomics.
- priority within Tier B should be given to one representative per major infrageneric/geographic lineage before dense within-species sampling.

### Tier C — replication / lower information gain

- taxa already strongly placed by nuclear transcriptomics and uniform in flower colour, unless needed as flanking controls for a transition.

## 4. Important correction to the original Chapter 2 plan

The project should not assume that Taiwan var. takaoense is an untouched mechanistic system. Chang et al. 2026 explicitly states that the study links its flower-colour polymorphism to anthocyanin expression and pollinator preference. The main-text HTML available during this audit clearly documents the white and bluish-purple morphs and their phylogenetic treatment, but detailed expression/pollinator methods were not recoverable from the parsed main text. Therefore EAzami should treat takaoense as:

- a high-value replication / causal-genomics target;
- a within-lineage comparison for identifying colour-associated alleles;
- not automatically as a novel first demonstration of anthocyanin expression differences.

## 5. Next executable data task

Build a regional master taxon table for Japan, Ryukyu, Taiwan and China and join four evidence layers:

1. accepted taxonomy;
2. flower-colour evidence;
3. nuclear phylogenomic coverage;
4. chromosome/ploidy information.

Then calculate the RAD-seq priority score at taxon/population level. The purpose is not maximum taxon count; it is maximum information gain about the number and direction of anthocyanin loss/regain events while simultaneously improving the East Asian nuclear backbone.
