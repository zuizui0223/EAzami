# *Cirsium* phylogeny evidence map — release v0.2.1

Date: 2026-08-10

This release supersedes the record counts in v0.2 while preserving its substantive synthesis.

## Curated evidence size

The validated evidence registry now merges three human-screened source files and contains **49 primary studies or reusable public data resources**.

| Evidence tier | Records | Role in EAzami |
|---|---:|---|
| A | 11 | Phylogenomics, phylotranscriptomics, target-capture/tree resources and decisive genome-wide reticulation evidence |
| B | 12 | Useful multilocus frameworks, regional species delimitation, historical biogeographic trees and reusable nuclear references |
| C | 17 | Cytogenetics, population hybridization, karyotype-supported taxonomy and low-locus regional evidence that constrains alternative histories |
| D | 9 | Plastome-only, morphology/type-based and nomenclatural evidence retained for maternal history and name reconciliation |
| **Total** | **49** | Automated candidates are excluded until manually screened |

The two records added after v0.2 are:

1. **Barres et al. 2013** (`10.3732/ajb.1200058`) — the major pre-Hyb-Seq Cardueae phylogeny, divergence-time and biogeographic reconstruction. It supplies the historical temporal hypothesis against which modern nuclear phylogenomics should be compared.
2. **Bae et al. 2015** (`10.5352/JLS.2015.25.2.243`) — Korean nuclear-rDNA sampling across several *Cirsium* taxa. Its notable result is that nodding *C. schantarense* grouped with upward-flowered *C. japonicum* in the ITS tree, illustrating that conspicuous capitulum orientation can differ without corresponding deep separation in a linked-rDNA genealogy.

## Current state of the field

### What is substantially resolved

- The Asteraceae and Cardueae deep nuclear backbone is strongly resolved with target capture/Hyb-Seq.
- A broad global species-level *Cirsium* nuclear tree exists, although taxon and population coverage remain incomplete.
- Japan has a substantial modern species-level framework rather than a blank phylogenetic slate.
- Focal Taiwan–Ryukyu lineages have strong phylotranscriptomic species frameworks.
- North America has an independent modern regional target-capture radiation analysis.

### What remains debated

- Generic circumscription in the Carduus–*Cirsium* group, especially broad *Cirsium* versus *Lophiolepis* and other segregates.
- The interpretation of known hybrid/allopolyploid taxa in any strictly bifurcating classification.
- Relationships within some rapid regional radiations where concatenated, coalescent, plastid and network results differ.

### What remains genuinely unresolved for Chapter 2

- white versus coloured population histories;
- introgression versus standing ancestral variation;
- cytotype and homeolog structure within focal populations;
- exact nuclear placement of transition-relevant taxa in the weakest China–Korea–Russian-Far-East sectors;
- causal regulatory versus structural changes producing repeated white flowers;
- any rigorously demonstrated white-to-coloured regain.

## Consequence for the flower-colour hypotheses

The broader literature does not support treating *C. irumtiense* as an established regain. Under the currently published Arenicola sister context, white loss in *C. brevicaule* remains simpler.

Bluish-purple var. *takaoense* remains the strongest current regain candidate because two histories remain equally parsimonious:

- independent white losses in var. *albescens* and white var. *takaoense*;
- one shared white transition followed by a coloured regain within var. *takaoense*.

Population genomic evidence is required to distinguish restoration, ancestral coloured haplotype retention and introgression. This is why a two-taxon contrast alone cannot establish evolutionary direction; near relatives, population-level states and alternative histories are required.

## Updated sequencing logic

### Species-level framework

Use Compositae1061-compatible target capture for genuine transition-critical taxa absent from modern nuclear datasets. Reuse public reads and compare:

- conservative single-copy matrices;
- the Moreyra-compatible retained-locus subset;
- paralog/homeolog-aware matrices;
- concatenated, ASTRAL and ASTRAL-Pro-style analyses;
- separate plastid maternal histories;
- reduced-taxon network sensitivity.

### Population-level histories

Use RAD-seq or resequencing for:

- white and coloured var. *takaoense*;
- Japanese and continental *C. pendulum*;
- Japanese and Zhejiang *C. sieboldii*;
- *C. kawakamii*–*C. tatakaense*;
- *C. brevicaule*–*C. irumtiense*;
- verified Korean white morphs.

Ploidy, chromosome/cytotype evidence, voucher provenance, standardized colour, pigment chemistry, floral RNA and leaf DNA remain required companion data.

## New supporting products

- `data/evidence/cirsium_phylogeny_literature_registry_batch02b_2026-08-10.csv`
- `data/evidence/cirsium_genomic_and_phylogenetic_resources_2026-08-10.csv`
- `data/evidence/east_asia_cirsium_phylogeny_coverage_v0_2.csv`
- `docs/CIRSIUM_PHYLOGENY_LITERATURE_SCREENING_BATCH_02_2026-08-10.md`
- expanded query families and consensus/gap matrix

## Next milestone

1. Recover exact Moreyra and Chang tip tables, Newick trees and branch lengths.
2. Quantify overlap among the original Compositae targets, Compositae1061 and Moreyra's retained 350 loci.
3. Harmonize accepted names, submitted names, historical synonyms, cytotypes and colour states.
4. Build a versioned nuclear-topology ensemble.
5. Run population-aware ancestral-state reconstruction and stochastic mapping across that ensemble.
6. Freeze target-capture and population-genomic panels only after the evidence/gap audit.
