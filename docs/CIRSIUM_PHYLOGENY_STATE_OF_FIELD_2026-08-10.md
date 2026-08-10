# State of the field: phylogeny, reticulation and cytogenetic evolution of *Cirsium*

Date: 2026-08-10

This document replaces the earlier practice of treating a few regional papers as if they represented the whole state of *Cirsium* phylogenetics. It synthesizes evidence at four distinct levels:

1. deep Cardueae/Carduinae backbone;
2. generic circumscription in the Carduus–*Cirsium* group;
3. global and regional species-level radiations;
4. population history, hybridization, polyploidy and organelle capture.

The underlying curated records are in `data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv`. The registry is deliberately evidence-typed: a plastome paper is not counted as equivalent to a multilocus nuclear species tree, and cytology is not converted into a topology.

## 1. Evidence hierarchy used by EAzami

### Tier A — primary backbone or decisive reticulation evidence

- hundreds to thousands of independent nuclear loci;
- transcriptome orthogroups or target capture with species-tree/coalescent analysis;
- RAD-seq when used for a narrowly defined hybrid/population question with explicit admixture analysis;
- public matrices, gene trees or raw reads where available.

Tier A can orient a colour transition, establish a local species backbone or reject a simple bifurcating history. It does not automatically solve population history if sampling is one accession per species.

### Tier B — useful multilocus framework

- multiple nuclear and plastid Sanger markers;
- genome-size/chromosome analyses mapped to a multilocus tree;
- broad regional species-complex studies.

Tier B remains informative for nomenclature, candidate sister relationships and historical hypotheses, but weak or conflicting nodes are not frozen as truth when Tier A evidence is available.

### Tier C — supporting reticulation or cytotype evidence

- AFLP, flow cytometry, chromosome counts, pollen fertility, local hybrid confirmation;
- critical taxonomic arguments that interpret existing trees.

Tier C determines which alternative histories must be tested, especially introgression, allopolyploidy and mixed cytotypes.

### Tier D — organelle-only, morphology-only or single-accession evidence

- complete chloroplast genomes and small plastome trees;
- morphological revisions and historical forms;
- single-locus barcode placement.

Tier D is valuable for vouchers, maternal lineages, synonyms and candidate discovery. It must never be treated as a complete species tree in a group with recurrent hybridization.

## 2. What is now well resolved

### 2.1 The deep Cardueae backbone

Early ITS/plastid studies established the broad tribal framework but left difficult nodes weakly supported. Herrando-Moraira et al. (2019; DOI `10.1016/j.ympev.2019.05.001`) used Hyb-Seq across 76 Cardueae species, targeting the Compositae1061 conserved ortholog set and recovering nuclear and plastid datasets. This greatly improved support for the tribal backbone and produced a 12-subtribe classification. The associated Mendeley dataset (`10.17632/bhvv6rmyt6.1`) includes alignments, gene trees, species trees and dating materials.

**Consensus:** the placement of the Carduus–*Cirsium* group within Carduinae and the deeper outgroup structure are no longer the main bottleneck for EAzami.

**Remaining caution:** cytonuclear discordance persists even at this scale. The deep tree should therefore be drawn from nuclear species-tree analyses, while plastid trees are retained as a separate maternal-history layer.

### 2.2 A broad global *Cirsium* nuclear backbone now exists

Moreyra et al. (2025; DOI `10.1016/j.ympev.2025.108285`) sampled 299 plants representing 251 taxa and inferred phylogenies from 350 nuclear loci. The study contains 266 *Cirsium* accessions representing 248 species, making it the largest species-level nuclear framework for the genus to date. It supports a Western Palearctic origin of the Carduus–*Cirsium* group and identifies Pleistocene radiations following dispersal to Japan and North America.

**Consensus:** it is no longer defensible to describe the global *Cirsium* nuclear backbone as almost wholly unknown.

**Remaining limitations:**

- the study covers roughly 60% of the genus rather than all accepted taxa;
- many taxa are represented by one or very few individuals;
- accession-level population structure, colour polymorphism and local introgression are largely outside its design;
- the exact Supplementary Table S1 and machine-readable final tree remain recovery targets in this repository;
- a missing accepted-name hit in PRJNA957074 is not proof that a taxon is absent from the published tree until synonyms and unsequenced supplement-only tips are checked.

## 3. Generic boundaries are still actively debated

The major unresolved issue at the generic level is not whether large clades exist, but how those clades should be named and delimited.

Ackerfield et al. (2020; DOI `10.1002/tax.12288`) showed that the Carduus–*Cirsium* group contains several major lineages and explicitly offered alternative monophyletic classifications: a broadly consolidated genus or several segregate genera.

Del Guacchio et al. (2022; DOI `10.1080/11263504.2022.2131924`) restored *Lophiolepis* from *Cirsium* sect. *Eriolepis* and segregated *Epitrachys*. Bureš et al. (2023; DOI `10.23855/preslia.2023.185`) found genomic, cytological and marker-phylogenetic support for *Lophiolepis*. Moreyra et al. (2023; DOI `10.3390/plants12173083`) used Hyb-Seq to revise African Carduinae and described *Afrocarduus*, *Afrocirsium* and *Nuriaea*, but did not accept every earlier segregation. Del Guacchio et al. (2024; DOI `10.3390/plants13233399`) and Moreyra & Susanna (2024; DOI `10.3390/plants13233400`) then published an explicit comment–reply exchange over *Lophiolepis* and monophyly criteria.

Bureš et al. (2024; DOI `10.1111/plb.13653`) added decisive biological complexity: tetraploid *C. vulgare* has approximately equal nuclear ancestry from *Cirsium* and *Lophiolepis*, while its organellar signal groups with *Cirsium*. A strictly bifurcating generic classification cannot make a hybrid origin disappear.

**EAzami policy:**

- keep a stable `accepted_taxon` field for the working flora/taxonomic authority;
- retain `source_taxon_name`, synonyms and alternative generic combinations;
- run transition analyses on biological lineages, not on the assumption that one contested genus name is uniquely correct;
- exclude or model known hybrid-origin taxa rather than forcing them into a simple ancestral-state tree;
- report sensitivity to *Cirsium* sensu lato versus segregate-genera treatments when the taxon set reaches those clades.

## 4. Regional radiations: strong evidence in some regions, major gaps in others

### 4.1 North America

Kelch & Baldwin (2003; DOI `10.1046/j.1365-294X.2003.01710.x`) detected very low ITS/ETS divergence and proposed either rapid ecological radiation or unusually conservative rDNA evolution. Ackerfield et al. (2020; DOI `10.1111/jse.12692`) demonstrated polyphyly in multiple species–variety complexes and attributed the taxonomic difficulty to convergence, hybridization and incipient speciation among other factors.

Siniscalchi et al. (2023; DOI `10.1086/724310`) moved the region to target-capture scale with 64 taxa and Compositae1061. They inferred a North American origin around 2 Ma and several Pleistocene diversification bursts.

**Status:** North America has both a modern regional phylogenomic tree and an explicit diversification analysis. Population histories and difficult species complexes remain local rather than continent-wide gaps.

### 4.2 Japan

Moreyra et al. (2025) sampled 38 Japanese species, 30 endemic, and inferred that all but two sampled species belong to a Pleistocene radiation following one principal jump dispersal from continental Asia; a separate Japanese lineage represents another arrival.

**Status:** the statement “Japan lacks a nuclear species backbone” is obsolete.

**Remaining gaps for EAzami:**

- exact placement of focal polymorphic taxa such as *C. pendulum* and *C. sieboldii* must be verified from Supplementary Data 1/tree files rather than inferred from the main text;
- one-tip species placement does not resolve Japanese white versus coloured populations;
- the Japanese radiation is young, so weak internodes, ILS and gene flow require topology/network sensitivity;
- Japan–Korea–China bridge populations are largely absent from a population-aware analysis.

### 4.3 Taiwan and the Ryukyu Islands

Chang et al. (2025; DOI `10.1186/s40529-025-00454-2`) combined phylotranscriptomics, species delimitation, chromosomes, morphology and pollen to resolve subsect. Nipponocirsium. It identifies a Japanese–Taiwan split around 0.74 Ma and recent Taiwanese diploid/dysploid/polyploid differentiation.

Chang et al. (2026; DOI `10.1186/s12870-026-08097-6`) analysed 37 samples, including 33 *Cirsium* samples from 12 taxa, with thousands of transcriptome orthogroups. It provides the current local framework for Sinocirsium, Arenicola and Nipponocirsium, delimits *C. brevicaule* and *C. irumtiense*, and documents network/ILS or introgression signals in the Taiwanese *C. japonicum* complex.

Taiwanese karyotype work (DOI `10.1508/cytologia.90.207`) shows that most taxa are 2n=34 but 2n=30/32 and diagnostically different karyotypes/satellite chromosomes occur.

**Status:** focal Taiwanese and Ryukyu species-level relationships are substantially better resolved than previously assumed.

**Remaining gaps:**

- colour morphs and populations are not densely represented in a unified nuclear population tree;
- exact tree files/branch lengths must be recovered for formal Mk and stochastic mapping;
- introgression versus ancestral polymorphism in var. *takaoense* remains unresolved;
- causal colour haplotypes and their ancestry are unknown;
- several Taiwanese taxa outside the focal clades lack equivalent transcriptomic coverage.

### 4.4 Korea, eastern China and the Russian Far East

Korean chromosome work (DOI `10.1508/cytologia.86.375`) documents diploidy, tetraploidy, aneuploidy and B chromosomes across nine *Cirsium* taxa. Morphological revisions record historical white-flowered forms in several taxa, but those names are not evidence that extant natural populations still exist.

The literature is rich in complete plastomes for Korean and Chinese taxa, including *C. rhinoceros*, *C. setosum* and *C. shansiense*. These are useful maternal-lineage records but usually involve one focal accession and small plastome trees.

**Status:** this is the weakest major geographic sector for a modern, dense, multi-locus nuclear framework linked to vouchers, colour states and cytotypes.

**Critical distinction:** some apparent gaps may vanish once Moreyra Supplementary Table S1 and PRJNA957074 synonyms are fully recovered. Only after this audit should new species-level RAD/target-capture sequencing be justified.

## 5. Reticulation and cytogenetics are central, not side issues

Central European studies show that natural *Cirsium* hybridization is frequent and can remain reproductively consequential:

- genome-size surveys documented diploid hybrids, triploidy, B-chromosome-associated variation and tetraploid *C. vulgare*;
- pollen and AFLP analyses found viable pollen in many natural hybrids and evidence consistent with backcrossing/introgression;
- *Cirsium × sudae* was confirmed as homoploid F1s plus a backcross;
- *C. vulgare* was demonstrated to be an intergeneric allotetraploid using RAD-seq.

Therefore, discordant colour-associated haplotypes may reflect:

1. independent mutations;
2. ancestral polymorphism retained through rapid radiation;
3. introgression after divergence;
4. allopolyploid ancestry/homeolog sorting;
5. chloroplast capture producing a misleading maternal topology.

EAzami must compare a nuclear species-tree ensemble with local ancestry/network analyses. A single plastid tree, and often a single concatenated nuclear tree, is insufficient for declaring a true colour regain.

## 6. Current consensus versus open questions

### High-confidence consensus

- Cardueae deep relationships are now well resolved with Hyb-Seq.
- A broad global *Cirsium* nuclear backbone exists and is substantially better than older barcode trees.
- Japan and North America each contain young Pleistocene radiations.
- Taiwan/Ryukyu focal clades have useful phylotranscriptomic backbones.
- hybridization, ILS and polyploidy are empirically real and can create strong cytonuclear conflict.
- plastome-only studies represent maternal history, not a sufficient species tree.

### Still unresolved

- the preferred generic circumscription of *Cirsium* versus *Lophiolepis* and other segregates;
- a nearly complete East Asian nuclear tree spanning Japan, Ryukyu, Taiwan, China, Korea and the Russian Far East under one locus framework;
- population-level placement of white and coloured morphs;
- the extent of introgression and ancestral polymorphism in the Taiwanese complex;
- exact nuclear placement of several Korean/Chinese white-form candidates;
- cytotype variation within focal populations;
- whether any coloured lineage truly descends from a white ancestor after gene flow is excluded.

## 7. Consequence for the Chapter 2 sequencing strategy

### Species-level backbone

Use target capture or a compatible high-copy nuclear framework for taxa genuinely missing from modern nuclear trees. Compositae1061 is attractive because it connects to the Cardueae and North American studies; the 350-locus Moreyra panel is attractive because it directly connects to the current global *Cirsium* tree. The exact bait/locus choice should be decided after recovering the Moreyra tree files and assessing overlap/data reuse.

### Population-level focal systems

Use RAD-seq or low-coverage resequencing for:

- white versus coloured var. *takaoense*;
- white versus purple *C. pendulum* and *C. sieboldii*;
- *C. brevicaule*–*C. irumtiense* population history;
- *C. kawakamii*–*C. tatakaense* gene flow and repeated mechanism;
- verified Korean white morphs.

RAD-seq should not be expected to provide the universal East Asian species backbone by itself. Across divergent taxa and cytotypes it risks restriction-site dropout, batch-specific locus sets, homeolog collapse and high missingness.

### Required companion data

Every focal population should carry:

- flow-cytometric ploidy/genome-size estimate where possible;
- chromosome/cytotype evidence from literature or new observations;
- voucher and accepted/synonym names;
- matched flower colour, pigment chemistry, RNA and DNA;
- plastid haplotype only as a separate maternal-history layer.

## 8. Immediate repository actions

1. Run the PRJNA957074 metadata recovery and harmonize all public tips.
2. Recover Moreyra Supplementary Data 1 and exact nuclear trees.
3. Download the openly archived Herrando-Moraira Cardueae tree set for deep outgroups.
4. Recover Chang 2025/2026 machine-readable trees or reconstruct versioned topology files from published outputs if none were deposited.
5. Expand the curated literature registry by backward/forward citation snowballing.
6. Build one unified table:

```text
accepted_taxon
source_taxon_name
alternative_genus
region
population_or_morph
flower_colour_state
ploidy
nuclear_evidence_tier
nuclear_tree_source
plastid_source
reticulation_evidence
sampling_gap_class
```

7. Run ancestral-state analyses across multiple nuclear topologies and population-aware coding schemes.

## Bottom line

The present field is neither “phylogeny already solved” nor “almost nothing is known.” The accurate formulation is:

> Deep and global species-level *Cirsium* phylogeny has advanced rapidly through Hyb-Seq and target capture, but the taxonomic treatment of major lineages remains debated, and East Asian colour evolution depends on unresolved population history, reticulation and cytotype variation within a young regional radiation.

That formulation determines the role of new data: **target capture closes genuine species-level gaps; RAD-seq/resequencing resolves morph and population history; cytogenetics and transcriptomics identify the mechanism.**
