# *Cirsium* phylogeny literature screening — batch 02

Date searched and screened: 2026-08-10

## Purpose

Extend the v0.1 evidence map beyond the initial Chang/Moreyra-centred framework and test whether additional primary literature changes the current conclusion about what is resolved versus genuinely missing.

## Search extensions

The versioned search query file was expanded to include:

- Compositae target-enrichment development and family-scale use;
- reference nuclear genomes and Darwin Tree of Life assemblies;
- transcriptome resources relevant to floral flavonoid/anthocyanin annotation;
- Japan, Taiwan, Korea, China, Sakhalin, Russian Far East, Mongolia and Himalaya regional terms;
- species delimitation, phylogeography, introgression, ILS and allopolyploidy;
- B chromosomes, cytomixis, dysploidy and flow cytometry;
- plastome phylogeography and chloroplast population history;
- TreeBASE, Dryad, Mendeley Data, figshare, Zenodo, BioProject and SRA artifact terms.

Search discovery uses Crossref/Europe PMC automation plus manual primary-source and public-repository verification. Automated candidates are not promoted automatically.

## Newly promoted curated records

### Tier A

1. **Mandel et al. 2014** — original Compositae conserved-ortholog target-enrichment method; 763 recovered loci in the demonstration dataset.
2. **Mandel et al. 2019** — family-wide Asteraceae genomic backbone from 256 terminals.

These records close an important provenance gap: Moreyra 2025 should be understood as part of a continuous Compositae target-enrichment framework rather than as an isolated 350-locus bait panel.

### Tier B

3. **Choi et al. 2024** — draft nuclear genome of *C. nipponicum* (929.4 Mb; N50 about 0.7 Mb; 95.1% BUSCO). It is a mapping/annotation resource, not a dense internal *Cirsium* species tree.

### Tier C

4. **Kadota 2007** — historical Japanese diversification and infrageneric synthesis.
5. **Chang et al. 2019** — original *C. tatakaense* description, purplish-red corolla and `2n = 64` contrast with white *C. kawakamii*.
6. **Chang et al. 2021** — *C. taiwanense* description and `2n = 32` karyotype; an unusual yellow-flower state outside the core colour systems.
7. **Nouroozi et al. 2011** — 21 populations/17 Iranian species; B chromosomes, cytomixis and meiotic abnormalities.
8. **Michálková et al. 2023** — 235-individual AFLP/STRUCTURE, flow-cytometric and morphometric test of recurrent *C. bertolonii* hybridization.

### Tier D

9. **Kim et al. 2023** — complete *C. nipponicum* plastome and six-species maternal phylogeny. It is retained as organelle evidence and not promoted to a nuclear species-tree placement.

## Genomic resources kept in a separate registry

The following are scientifically useful but are not all independent species-tree studies, so they are maintained in `cirsium_genomic_and_phylogenetic_resources_2026-08-10.csv` rather than inflated into equivalent topology evidence:

- Moreyra, Chang and Herrando public read/tree projects;
- *C. nipponicum* nuclear genome and plastome;
- *C. rhinoceros* plastome;
- Korean *C. japonicum* var. *spinossimum* tissue transcriptome;
- Darwin Tree of Life assemblies/projects for *C. heterophyllum* and *C. dissectum*;
- original Compositae target-capture alignments/tree archives.

## Screening decisions and exclusions

- Secondary summaries, Wikipedia pages and commercial aggregators were used only to locate primary sources and were not curated as evidence.
- Medicinal chemistry papers without phylogenetic, genomic-resource, cytotype or pigment-pathway relevance were excluded.
- Single-accession plastome papers were retained only when they add a focal maternal reference or name/voucher anchor.
- Local morphological new-species descriptions were excluded unless they altered a focal taxon concept, flower-colour state, cytotype or sampling boundary.
- Family-scale target-capture papers were included because they define the locus/method framework used by later Cardueae and *Cirsium* analyses, not because they resolve internal East Asian relationships.
- A nuclear genome was not treated as a species tree merely because it contains a comparative ortholog tree.

## Resulting evidence-map size

After this screening batch:

- Tier A: 11
- Tier B: 11
- Tier C: 16
- Tier D: 9
- **Total curated records: 47**

## Does the expanded literature change the biological conclusion?

No major reversal occurs. It sharpens the conclusion.

### Strengthened conclusions

- Deep Asteraceae/Cardueae and broad *Cirsium* species-level nuclear frameworks are real and reusable.
- The Compositae target-capture lineage is methodologically continuous and should anchor new species-level sampling.
- Japanese and focal Taiwan/Ryukyu species frameworks are substantially resolved relative to older literature.
- Reticulation and cytotype variation are widespread enough that they must be explicit model alternatives.
- Whole-genome resources are now emerging and can support candidate-gene and reference-bias work.

### Gaps that remain genuine

- population-level white/coloured histories;
- local ancestry and gene flow;
- homeolog/cytotype structure;
- dense modern nuclear coverage in transition-relevant China–Korea–NE Asia lineages;
- exact machine-readable Moreyra/Chang tree/sample artifacts;
- causal regulatory versus structural changes in repeated white flowers;
- any rigorously demonstrated white-to-coloured regain.

## Immediate follow-up

1. Run the expanded automated searches and manually classify novel high-score candidates.
2. Recover exact assembly accessions for all nuclear reference genomes.
3. Build a locus-overlap table for original Compositae targets, Compositae1061 and the 350 loci retained by Moreyra.
4. Recover Moreyra/Chang exact trees and sample tables.
5. Join verified tips, synonyms, ploidy and population-aware flower colour.
6. Run full-tree ancestral-state and stochastic-mapping sensitivity before freezing sequencing panel v1.0.
