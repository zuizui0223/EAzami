# *Cirsium* phylogeny evidence map — release v0.1

Date: 2026-08-10

## Scope completed in this release

The curated map now contains **38 primary studies or public data resources** split across a core registry and a regional-additions registry. The validated builder merges them into one current table without silently overwriting duplicate citation keys or DOI records.

### Evidence-tier composition

| Evidence tier | Records | Meaning in this project |
|---|---:|---|
| A | 9 | Phylogenomics, transcriptomics, target capture, decisive genome-wide hybrid evidence, or reusable public tree/read data |
| B | 10 | Broad multilocus or well-supported regional species frameworks |
| C | 11 | Cytogenetic, AFLP, local hybrid, or taxonomic-debate evidence that constrains alternative histories |
| D | 8 | Plastome-only, morphology/type-based or historical-form evidence used for maternal history, names and candidate detection |
| **Total** | **38** | Core plus regional curated records; automated candidates are not included |

## What the literature now supports

### 1. Deep relationships are not the current bottleneck

Hyb-Seq work has produced a strongly supported Cardueae/Carduinae backbone with archived alignments, gene trees and species trees. For Chapter 2, the deep outgroup framework can be imported rather than regenerated.

### 2. A global species-level *Cirsium* tree exists but is not a population tree

Moreyra et al. (2025) used the **Compositae1061 target-enrichment probe set** and retained 350 nuclear loci after orthology assessment and filtering. The resulting tree is the current broad nuclear backbone. The 350 loci are therefore an analysed subset of Compositae1061—not a separate Moreyra bait panel.

This substantially changes the earlier assumption that Japan or the genus as a whole lacks nuclear coverage. Its main limitations for EAzami are incomplete taxon coverage, sparse accessions within most species, and incomplete recovery of exact supplementary tips, retained loci and tree files in the current repository.

### 3. Generic circumscription remains a genuine dispute

Reliable studies agree that several major Carduus–*Cirsium* lineages exist but disagree about their preferred generic names and ranks. *Lophiolepis* is the clearest disputed case. The genome-wide hybrid origin of tetraploid *C. vulgare* further shows that nomenclature cannot turn a reticulate lineage into a simple bifurcating history.

EAzami therefore stores accepted names, source names and alternative genera separately and performs topology/taxon-treatment sensitivity.

### 4. East Asian evidence is geographically uneven

#### Japan

A modern species-level nuclear backbone covers a large fraction of the Japanese radiation. Remaining Chapter 2 gaps are exact tip recovery, morph/population sampling and transregional bridges—not a wholesale Japanese species-tree rebuild.

#### Taiwan and Ryukyu

Phylotranscriptomic frameworks resolve the focal Sinocirsium, Arenicola and Nipponocirsium relationships, while karyotype studies reveal diploidy, tetraploidy and dysploidy. The main unresolved layer is population history: colour morphs, introgression, standing variation and causal haplotypes.

#### China

The evidence map recovered many recent taxonomic revisions, local ITS/plastid placements, new species and isolated complete plastomes. Recent examples include *C. medogense* in sect. Epitrachys, the reassignment of *Lamyropsis macracantha*, and revisions affecting *C. japonicum*, *C. sieboldii*, *C. yezoense*, *C. lipskyi* and related names.

This is valuable for accepted-name harmonization and local placement, but it is not yet equivalent to a dense China-wide multi-locus nuclear tree under one marker framework.

#### Korea

Karyotype work documents diploids, tetraploids, aneuploid series and B chromosomes. Historical white forms and multiple complete plastomes provide candidate and maternal-lineage evidence. Modern dense nuclear placement remains uncertain for several colour-relevant taxa until Moreyra tips/synonyms are fully recovered.

#### Korea–Manchuria–Russian Far East

Broad species such as *C. pendulum*, *C. schantarense* and *C. vlassovianum* are currently population-phylogeographic gaps. They are especially useful for distinguishing recent local white loss from old standing variation across continental populations.

### 5. Hybridization and cytotype history must be analysed explicitly

The curated evidence includes pollen-fertility studies, AFLP-confirmed F1/backcross systems, flow-cytometric hybrid studies and RAD-seq evidence for intergeneric allopolyploid origin. These make the following alternatives obligatory for apparent colour reversals:

1. parallel mutation;
2. ancestral polymorphism;
3. introgression of a colour allele;
4. allopolyploid/homeolog sorting;
5. chloroplast capture;
6. true reactivation after a white ancestor.

A single plastid tree or one concatenated species tree cannot distinguish all six.

## Current gap hierarchy

### Resolved enough to use now

- deep Cardueae/Carduinae nuclear backbone;
- broad global *Cirsium* nuclear topology;
- Japanese species-level radiation context;
- Sinocirsium/Arenicola/Nipponocirsium focal species framework;
- local direction of the *C. kawakamii* white transition;
- predominantly coloured sister context around *C. brevicaule*.

### File/data recovery gaps

- Moreyra Supplementary Data 1, exact tree artifacts and retained-locus information;
- Chang 2025/2026 machine-readable trees and branch lengths;
- exact accepted-name/synonym match for focal Japanese, Korean and Chinese tips;
- reusable topology ensemble with nuclear, plastid and network alternatives.

### Genuine biological gaps

- white versus coloured var. *takaoense* population history;
- Japanese and continental *C. pendulum* population structure;
- Japanese and Zhejiang *C. sieboldii* population structure;
- population gene flow within Arenicola;
- colour-associated ancestry in the *C. kawakamii* system;
- verified extant Korean white morphs and their nuclear placement;
- cytotype distributions within focal populations;
- molecular mechanism shared across independent white transitions.

## Sequencing consequence

### Target capture

Use **Compositae1061-compatible target capture** to fill genuine transition-critical missing species. This connects directly to the deep Cardueae, North American and global *Cirsium* studies. After the Moreyra artifacts are recovered, reproduce or intersect its orthology filtering and final 350 retained loci rather than treating those loci as a distinct capture kit.

### RAD-seq or resequencing

Use for population-scale morph histories, gene flow and local ancestry after species-level placement is known. Do not expect one RAD panel to replace a cross-region target-capture backbone across divergent cytotypes.

### Companion measurements

- flow cytometry and chromosome/cytotype metadata;
- plastid haplotypes as maternal history;
- standardized flower colour and anthocyanin chemistry;
- floral RNA-seq and candidate-region follow-up;
- vouchers and exact synonym mapping.

## Automation and review status

Added automation:

- Crossref/Europe PMC candidate recovery;
- query and search-log versioning;
- DOI/title deduplication;
- topic/evidence candidate scoring;
- monthly/manual GitHub Actions artifact generation;
- registry schema validation and conflict detection;
- offline unit tests.

The automated output is a discovery aid. The map is **not yet a completed PRISMA-style systematic review**. Release v1.0 requires manual screening of generated candidates, backward/forward citation snowballing for every Tier-A anchor, exact tree/data recovery and a frozen search log.

## Practical conclusion

The strongest current formulation is:

> Deep and broad species-level *Cirsium* phylogeny has advanced rapidly, but generic naming remains disputed and East Asian flower-colour evolution is limited by population-level reticulation, cytotype variation and uneven regional nuclear coverage rather than by a complete absence of phylogenetic knowledge.
