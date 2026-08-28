# East Asian *Cirsium* independent nuclear-DNA evidence audit v1

Status date: 2026-08-28

Machine-readable ledger: `data/evidence/east_asia_independent_nuclear_evidence_audit_v1.csv`

## Audit question

**How much nuclear-DNA information exists for Japanese and East-Asian *Cirsium* independently of the Moreyra et al. (2025) global target-capture paper, and was the existing repository survey actually exhaustive?**

## Answer

The previous repository search protocol was systematic in design, but the integrated evidence state was **not exhaustive**. It concentrated on three modern species-backbone sources — Moreyra 2025, Chang 2025 and Chang 2026 — and therefore missed or under-propagated several older or differently scoped nuclear datasets.

The corrected evidence state is:

1. **Japan already had genome-wide reduced-representation nuclear analyses before Moreyra 2025.** The 2017–2021 JSPS project on Japanese *Cirsium* used RAD-seq/MIG-seq and included population-scale analyses of diploid Kaga-subsection taxa. The final report states that within-population genetic variation was large, interspecific differentiation was not significant in the examined diploid subsection, isolation by distance was present, and some named sectional/subsectional boundaries were contradicted by the MIG-seq tree. This is direct but grey-literature evidence; no reusable raw genotype matrix was recovered.
2. **A Japan38 species has reusable pre-2025 population nuclear data.** The 2022 Dryad dataset for *C. maritimum* contains a public MIG-seq Genepop matrix (`Genepop_Cmaritimum.txt`, 73.09 KB). This is the same accepted species name as Japan38 JPN_17, although the Awaji populations are not the Moreyra voucher and are not linked to Chapter 2 trait measurements.
3. **Northeast Asia had nuclear rDNA studies before 2025.** Korean studies in 2012 and 2015 sequenced 18S–ITS–5.8S–ITS2–partial 28S arrays across *C. pendulum*, *C. setidens*, *C. japonicum*, *C. nipponicum*, *C. shantarense* and *C. chanroenicum*. The 2015 result is particularly relevant to capitulum orientation: downward-headed *C. shantarense* clustered with upward-headed *C. japonicum* in the ITS tree despite their orientation difference.
4. **A full nuclear reference genome existed before 2025.** The 2024 Korean *C. nipponicum* genome is 929.4 Mb with 31,263 predicted protein-coding genes, public SRA reads (PRJNA1127082) and public assembly/annotation. It is a powerful reference resource but not a Japanese-radiation species tree.
5. **The strongest local independent phylogenomic checks are still Chang 2025 and Chang 2026.** Chang 2025 provides thousands of transcriptome orthogroups for Japanese/Taiwanese Nipponocirsium, while Chang 2026 provides multi-individual phylotranscriptomics and reticulation analysis for the Taiwan/Ryukyu *C. japonicum* complex and Arenicola. These are independent of Moreyra's global target-capture backbone but cover only subsets of the Japan38 radiation.
6. **The 2025 Ogasawara/Ryukyu MIG-seq study is real but incompletely reusable.** Its method and five-taxon comparison are now source-backed in the repository, but sample identities, topology values and genotype/raw-read archives remain unrecovered.

Therefore the correct statement is **not** “Moreyra 2025 is the only nuclear evidence.” The correct statement is:

> **Moreyra 2025 / the reconstructed Comp1061 scaffold is the only currently harmonized common-locus nuclear framework spanning the full Japan38 analysis set, but multiple independent nuclear datasets — including pre-2025 Japanese MIG-seq/RAD, Korean rDNA, a public *C. maritimum* MIG-seq population matrix and a *C. nipponicum* reference genome — provide external constraints on taxon delimitation, population compression and local topology.**

## Evidence recovered by period

### 2012 — Korean *C. pendulum* / *C. setidens* rDNA

Yoo & Bae sequenced genomic 18S rDNA, ITS1, 5.8S rDNA, ITS2 and part of 28S from six Korean *C. pendulum* collections and two *C. setidens* collections, compared them with a Hokkaido *C. pendulum* and Anhui *C. japonicum*, and reported three distinct groups. The article states that generated sequences were deposited in GenBank. A later Korean sequence-comparison source identifies *C. setidens* accessions JX274255–JX274258 and older *C. pendulum* accessions AB035977/AB035998.

**Use:** independent Northeast-Asian nuclear marker context, including an exact species-name match to JPN_38 *C. pendulum*.

**Limit:** one linked ribosomal repeat region cannot validate a genome-wide species tree.

### 2015 — Korean ITS/rDNA across several *Cirsium*

Bae sampled *C. japonicum* from eight Korean localities and one each of *C. chanroenicum*, *C. nipponicum* and *C. shantarense*. A neighbor-joining ITS analysis separated several taxa but placed downward-headed *C. shantarense* with upward-headed *C. japonicum*.

**Use:** a directly relevant independent observation that a major capitulum orientation difference need not coincide with strong ITS separation.

**Limit:** sparse taxon sampling and concerted evolution/linkage of nrDNA.

### 2017–2021 — Japanese genome-wide MIG-seq/RAD project

The JSPS project `17K07524`, led by Koichi Uehara with Motomi Ito and Yoichi Watanabe, explicitly used next-generation RAD-seq/MIG-seq to examine Japanese *Cirsium*. The final report records broad sampling of diploid Kaga-subsection taxa from Toyama through Yamaguchi, DAPC and phylogenetic analyses, significant isolation by distance, large within-population variation and no significant interspecific variation in the examined diploid subsection. It also reports mixed named-species clades and placement of *C. microspicatum* with the *C. kiotoense* group despite subsectional classification differences.

At least two taxa overlap directly with the Japan38 concept list:

- JPN_14 — *C. kiotoense*;
- JPN_34 — *C. microspicatum*.

**Use:** strong independent support for treating one-species/one-tip coding as a resolution assumption rather than biological truth. It is especially relevant to the Chapter 2 species-tip compression boundary.

**Limit:** the accessible final report is grey literature, the exact sample/genotype matrix is not archived in the recovered repository, and the broad project combined nuclear and plastid analyses. It must not be substituted for the Comp1061 tree.

### 2018 — Korean *C. japonicum* var. *spinossimum* transcriptome

RNA-seq yielded 51,133 unigenes from flower, leaf and root tissue.

**Use:** nuclear functional/reference resource for future floral pathway work.

**Limit:** single-taxon transcriptomics, not a phylogenetic framework.

### 2022 — public *C. maritimum* MIG-seq population genotypes

Dryad DOI `10.5061/dryad.tb2rbp03j` exposes `Genepop_Cmaritimum.txt` (73.09 KB) and README. The dataset compares past wild, current wild and ex-situ Awaji Island material using MIG-seq and reports loss of alleles from current wild populations.

JPN_17 is *C. maritimum*, so this is a direct species-level overlap with the Chapter 2 panel.

**Use now:** reanalyse within-species genetic structure and temporal/population diversity as an empirical demonstration of information compressed by a species tip.

**Limit:** it cannot independently place JPN_17 in the Japan38 species tree and is not linked to the exact sequenced voucher or capitulum state observation.

### 2024 — *C. nipponicum* nuclear reference genome

The Korean Ulleung accession provides a 929.4-Mb genome, N50 0.7 Mb, 95.1% BUSCO completeness, 31,263 predicted genes, SRA PRJNA1127082 and a public assembly/annotation.

**Use:** mapping, orthology, candidate-gene and probe-design resource.

**Limit:** the phylogenetic analysis compares one *Cirsium* genome against other plant species, so it does not resolve the Japanese *Cirsium* radiation. The Korean accession must not be treated as the Japanese JPN_35 individual.

### 2024 — Chinese nuclear ITS/ETS taxonomic evidence

Jin & Chen used nuclear ITS/ETS to place *Lamyropsis macracantha* in *Cirsium*.

**Use:** confirms that older exact-name/generic searches alone can miss usable nuclear evidence because taxonomic names change.

**Limit:** narrow generic-placement question, not an East-Asian radiation tree.

### 2025 — Chang phylotranscriptomics independent of Moreyra

Chang et al. reconstructed Nipponocirsium using thousands of single-copy transcriptome orthogroups, ASTRAL species trees and networks. Japanese taxa include *C. kujuense*, *C. suffultum* and *C. nipponicum* var. *incomptum*. Public reads are in PRJNA1158676.

**Use:** strongest independent local topology/cytotype sensitivity for this subsection.

**Limit:** only a subset of Japan38/EAzami and sparse Japanese within-taxon replication.

### 2025 — Ogasawara/Ryukyu/coastal MIG-seq

The Chiba University institutional publication explicitly states MIG-seq analysis of *C. boninense* with *C. brevicaule*, indexed *C. irimtiense*, *C. spinosum* and *C. maritimum*. The repository had already recovered this study on 2026-08-21.

**Use:** local-origin hypothesis and sampling design.

**Limit:** public summary does not expose sample counts, exact topology, retained SNPs or a genotype archive.

### 2026 — Taiwan/Ryukyu multi-individual phylotranscriptomics

Chang et al. used 33 *Cirsium* samples, with ASTRAL from 2,999 orthogroups and Neighbor-Net from 2,599 orthogroups, and reported reticulation within the *C. japonicum* complex. PRJNA1311153 is public.

**Use:** strongest local independent species-tree/network evidence for Ryukyu/Taiwan and direct evidence that tree-only interpretation should be checked against reticulation.

**Limit:** does not span the full Japanese radiation and does not consistently link transcriptome individuals to colour morph.

## What was wrong with the existing integrated coverage table

`data/evidence/east_asia_nuclear_coverage_v1_2026-08-10.csv` was internally reproducible, but its evidence universe was deliberately narrow: Moreyra 2025 + Chang 2025 + Chang 2026. As a result, rows such as *C. pendulum*, *C. setidens*, *C. shantarense*, *C. maritimum* and Korean *C. nipponicum* could be described as lacking integrated modern nuclear evidence even though older nuclear markers, genome-wide population data or genome resources existed.

The v1 table should remain frozen for provenance. This audit is the correction layer and must be consulted before declaring a taxon a nuclear-data gap.

## Consequence for Chapter 2

### What changes

1. The paper must not imply that the Moreyra-derived scaffold is the sole nuclear evidence for Japanese/East-Asian *Cirsium*.
2. Species-tip compression gains an independent genome-wide precedent from Japanese MIG-seq/RAD work and a reusable *C. maritimum* population dataset.
3. The orientation interpretation gains an independent older nuclear marker observation: large head-orientation difference with weak ITS separation in *C. shantarense* versus *C. japonicum*.
4. Local topology/network sensitivity is independently supported by Chang 2025/2026 rather than being merely a future-data request.

### What does not change

1. The accepted Japan38 Comp1061 scaffold remains the primary historical scaffold because it is the only harmonized common-locus framework spanning the complete admitted Japan38 analysis set.
2. Older rDNA, MIG-seq and reference-genome resources are not combinable as branch lengths in the same tree without a new explicit data model.
3. None of the independent sources identifies the environmental cause, fitness effect or independent-origin count of orientation, phyllary posture or stickiness.

## Current completeness assessment

After this audit, nuclear evidence has been queried across:

- Japan: modern target capture, pre-2025 MIG-seq/RAD project reports, population MIG-seq datasets, transcriptome/genome resources and conference outputs;
- Ryukyu/Ogasawara: 2025 MIG-seq plus 2026 phylotranscriptomics;
- Taiwan: 2025/2026 phylotranscriptomics plus current ITS/barcode evidence;
- Korea: 2012/2015 nrDNA, 2018 transcriptome, 2024 nuclear genome and modern regional context;
- China: older/narrow nrDNA/ITS-ETS and broad/global phylogenomic inclusion, but no dense China-wide pre-2025 *Cirsium* nuclear species framework was recovered;
- Russian Far East/Sakhalin: taxonomic/cytological occurrence literature is recoverable, but no dense regional multi-locus nuclear *Cirsium* framework was recovered in the bounded systematic search.

Thus the remaining major geographic nuclear gap is **not Japan as a whole**. It is **dense, population-aware, homologous-locus coverage across the complete Japan–Korea–China–Russian Far East bridge**, especially with same-individual capitulum traits.

## Stop rule / claim ceiling

This audit is considered complete enough for the current Chapter 2 literature claim when all of the following are true:

- every source above is represented in the machine ledger;
- `17K07524`, `10.5352/JLS.2012.22.8.1120` and `10.5061/dryad.tb2rbp03j` no longer return zero repository hits;
- the manuscript calls Comp1061 the primary **harmonized common-locus scaffold**, not the only nuclear evidence;
- older markers and population data are used only for the estimands they actually measure.

No bounded search can prove that unpublished or unindexed nuclear data do not exist. “No dense regional framework recovered” is therefore the maximum admissible absence claim.
