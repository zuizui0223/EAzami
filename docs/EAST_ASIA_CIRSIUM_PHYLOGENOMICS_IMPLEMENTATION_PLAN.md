# East Asian *Cirsium* phylogenomics implementation plan

Date: 2026-08-10

## Decision summary

The East Asian phylogeny should **not** be built as one giant RAD-seq experiment across all taxa. The most defensible design is a linked two-layer framework:

1. **Species-level backbone:** Compositae1061-compatible target capture, merged with the existing Herrando-Moraira, Siniscalchi and Moreyra datasets.
2. **Population/morph history:** RAD-seq or resequencing within selected white/coloured systems after their species-level placement is known.

This separation follows directly from the current literature map. Deep and broad species relationships already have reusable target-capture data, whereas the unresolved flower-colour questions concern within-species polymorphism, local ancestry, introgression and cytotypes.

## 1. Species-level East Asian backbone

### 1.1 Geographic scope

Build one explicit East Asian sampling frame covering:

- Japan and the Ryukyu Islands;
- Taiwan;
- China, including southeastern, northeastern and southwestern sectors;
- Korea;
- Sakhalin and the Russian Far East;
- Mongolia where it supplies the continental sister/bridge context;
- a small number of western Eurasian and North American anchors already present in the global tree.

The first target is not every named *Cirsium*, but every lineage needed to:

- connect the regional trees under one marker framework;
- orient a white/coloured transition;
- test whether a candidate white form is independent;
- provide parental/sister context for an introgression test;
- represent a distinct cytotype or disputed taxonomic entity.

### 1.2 Marker choice

Use **Compositae1061-compatible target enrichment**.

Reasons:

- it generated the deep Cardueae Hyb-Seq framework;
- it was used in the North American *Cirsium* radiation study;
- Moreyra et al. 2025 also used Compositae1061 and retained 350 loci after orthology assessment/filtering;
- the family-specific panel recovers more loci in Asteraceae than Angiosperms353, although paralogy is correspondingly more frequent;
- a documented 30-locus overlap permits limited integration with Angiosperms353 data if useful.

Do **not** refer to a separate “Moreyra 350-locus bait set” unless an actual distinct probe design is recovered. The 350 loci are the filtered analysis subset, not currently evidence of an independent capture kit.

### 1.3 Sampling density

#### Existing, well-placed taxa

- one high-quality representative may be sufficient for backbone reuse;
- add a second representative when taxonomic identification, geography or cytotype is uncertain;
- add three representatives for broad, morphologically variable or suspected hybrid taxa.

#### Genuine missing taxa that affect colour history

- 2–3 individuals from separate populations;
- include one fresh high-molecular-weight DNA sample where possible;
- retain voucher, locality, flower colour and ploidy metadata.

#### Known/suspected polyploids

- minimum three individuals per cytotype/population class;
- fresh material for flow cytometry is mandatory where feasible;
- avoid pooling cytotypes under one species tip.

### 1.4 Existing data to integrate before new sequencing

1. Herrando-Moraira et al. 2019 archived Cardueae matrices, gene trees and species trees.
2. Moreyra et al. 2025 PRJNA957074 Compositae1061 raw reads and exact Supplementary Table S1/tree artifacts.
3. Siniscalchi et al. 2023 North American Compositae1061 data as an independent regional compatibility check.
4. Chang 2025/2026 transcriptome reads/orthogroups for focal Taiwan–Ryukyu–Japan taxa.
5. Angiosperms353 samples only through explicitly shared/recoverable loci or as a separate sensitivity matrix.

For Chang transcriptomes, identify orthologs that map to Compositae1061 targets. Retain the full phylotranscriptomic trees as separate high-information regional topology constraints rather than discarding non-overlapping orthogroups.

## 2. Raw-read and locus-recovery workflow

### 2.1 Primary assembly

Use HybPiper with:

- versioned target file;
- per-sample read and assembly statistics;
- intronerate output where informative;
- all paralog warnings retained;
- no silent choice of a single sequence for a locus with multiple strong copies.

Run a second pipeline or a controlled subset through HybPhyloMaker/Captus as a robustness check if topology-sensitive discrepancies appear.

### 2.2 Orthology and paralogy matrices

Generate at least three nuclear datasets:

1. **Conservative single-copy matrix**
   - remove loci/samples with strong paralog conflict;
   - suitable for the primary ASTRAL and concatenated trees.

2. **Moreyra-compatible retained-locus matrix**
   - intersect with the recovered 350-locus set and comparable filtering;
   - maximizes direct reuse of the global tree.

3. **Multi-copy/paralog-aware matrix**
   - retain labeled copies/homeologs;
   - analyse with ASTRAL-Pro 2 and hybrid/phasing workflows.

Use PPD-style criteria and explicit sensitivity thresholds rather than treating every HybPiper paralog warning as either automatically fatal or automatically harmless.

### 2.3 Plastid data

Recover off-target plastid reads or existing plastomes, but store them as an independent maternal-history analysis.

Outputs:

- plastid tree/haplotype network;
- nuclear–plastid discordance table;
- candidate chloroplast-capture events.

Never substitute the plastid topology for the nuclear species tree in ancestral flower-colour reconstruction.

## 3. Tree and network analyses

### 3.1 Gene-tree estimation

For every locus:

- alignment QC and trimming;
- model selection and maximum-likelihood gene tree;
- branch support and informative-site summary;
- collapse very weak gene-tree branches before coalescent analysis as a sensitivity;
- flag samples/loci with unusual copy number or long branches.

### 3.2 Primary species-tree set

Create a versioned topology ensemble:

1. concatenated maximum-likelihood tree;
2. ASTRAL species tree from conservative single-copy loci;
3. ASTRAL-Pro 2 tree from labeled multi-copy gene families;
4. Moreyra-compatible 350-locus tree;
5. regional Chang transcriptome trees;
6. plastid tree as a separate maternal topology.

Use quartet support/local posterior probabilities, gene concordance factors and polytomy tests. Weak rapid-radiation internodes should remain unresolved when the data do not reject a polytomy.

### 3.3 Reticulation tests

Use different tools for different scales:

- HybPhaser or related allele-phasing diagnostics for target-capture hybrid detection;
- PhyloNetworks/SNaQ on a reduced, biologically justified taxon set;
- D/f-statistics or local ancestry on population-level RAD/resequencing data;
- topology weighting/gene-tree discordance around specific candidate hybrid branches.

Do not search an unrestricted network with every East Asian taxon and many hybrid nodes. Start from hypotheses generated by geography, cytotype, nuclear–plastid discordance and the colour-associated region.

## 4. Population layer for flower-colour evolution

### 4.1 Highest-priority systems

1. var. *takaoense*: white versus bluish-purple populations/individuals.
2. *C. pendulum*: Japanese white/purple plus Korean–Chinese–Russian-Far-East bridge populations.
3. *C. sieboldii*: Japanese white/purple plus Zhejiang populations.
4. *C. kawakamii* versus *C. tatakaense*: matched tetraploid white/coloured comparison.
5. *C. brevicaule* versus *C. irumtiense*: independent white-loss mechanism, structure and gene flow.
6. verified Korean white forms of *C. setidens*, *C. rhinoceros*, *C. schantarense* or *C. vlassovianum*.

### 4.2 RAD-seq role

RAD-seq is used to estimate:

- population structure and admixture;
- whether colour morphs form genomic clusters;
- local versus genome-wide ancestry;
- FST, dXY and diversity around candidate regions after those regions are known;
- demographic alternatives such as retained polymorphism versus secondary introgression.

RAD-seq is **not** the preferred tool for merging every divergent East Asian species into one backbone because restriction-site dropout and non-homologous locus sets can increase with divergence.

### 4.3 When resequencing is preferable

Escalate a focal system from RAD-seq to low/medium-coverage whole-genome resequencing when:

- a reference-quality or good draft genome exists;
- structural or promoter variants are plausible;
- local ancestry must be resolved at fine scale;
- polyploid allele dosage can be modelled;
- a RAD locus cannot span the causal region.

## 5. Ploidy-aware handling

### 5.1 Field metadata

For each population:

- flow-cytometric genome size/ploidy from fresh leaf;
- literature chromosome count with voucher/cytotype provenance;
- mixed cytotypes recorded as separate population strata;
- standardized DNA concentration and quality;
- no pooling of cytotypes before genotype calling.

### 5.2 Bioinformatics

- retain allele balance and read-depth distributions;
- compare diploid and ploidy-aware genotype models;
- identify collapsed homeologs and loci with excess heterozygosity;
- run single-copy and multi-copy trees separately;
- use ASTRAL-Pro 2 and HybPhaser-style analyses as sensitivities;
- avoid interpreting an apparent heterozygous colour allele as simple diploid variation before cytotype checks.

## 6. Connection to the molecular flower-colour mechanism

The species/population trees determine **where** the colour transition occurred. They do not identify **how** it occurred.

For the same individuals, link:

- standardized visible and UV reflectance;
- anthocyanin/flavonoid chemistry;
- floral RNA-seq at matched developmental stages;
- leaf DNA;
- candidate regulatory and structural loci;
- voucher and population ID.

The mechanistic comparison should test:

1. independent disruptive mutations;
2. repeated regulatory suppression of homologous MBW-network nodes;
3. shared ancestral white haplotype;
4. introgressed white or coloured haplotype;
5. derived restoration/reactivation on a white background.

## 7. Deliverables before ordering new libraries

### Required existing-data deliverables

- exact Moreyra sample/tip table;
- exact Moreyra concatenated and coalescent trees;
- retained 350-locus names and orthology/filtering rules;
- Herrando-Moraira archived tree set downloaded and versioned;
- Chang 2025/2026 exact sample/tree files;
- accepted-name/synonym mapping for all candidate taxa;
- verified nuclear-coverage matrix;
- ploidy/cytotype evidence matrix;
- population-aware flower-colour atlas.

### Pilot target-capture decision

Only after those deliverables, select approximately 24–48 samples that maximize:

- true missing-lineage coverage;
- taxonomic/cytotype uncertainty resolution;
- bridge connectivity among regional trees;
- ability to orient a colour transition.

Pilot success criteria:

- high target recovery across regions and cytotypes;
- sufficient overlap with existing Compositae1061 data;
- manageable paralog/homeolog rates;
- stable placement of technical or biological replicates;
- no major batch-specific topology.

### Pilot population decision

Run the first RAD/resequencing panel on **one diploid within-lineage white/coloured system** and **one polyploid interspecific replicate**. The strongest current pair is:

- var. *takaoense* for the high-information same-lineage comparison;
- *C. kawakamii*–*C. tatakaense* for ploidy-aware replicated white loss.

## 8. Decision table

| Question | Primary data | Main analysis | Why |
|---|---|---|---|
| Where is an unsampled East Asian species placed? | Compositae1061 target capture | IQ-TREE + ASTRAL | Compatible with existing global/regional backbones |
| Are short internodes truly resolved? | hundreds of gene trees | quartet support + polytomy tests | Avoids false certainty in rapid radiations |
| Does polyploidy change placement? | multi-copy target loci + ploidy | ASTRAL-Pro 2 + phased/homeolog sensitivity | One-copy matrices can erase parental histories |
| Is the lineage reticulate? | target capture or population SNPs | HybPhaser/SNaQ/local ancestry | A tree alone cannot represent introgression |
| Is a colour morph derived or ancestral? | dense population SNPs | structure + demographic/local ancestry models | Requires within-taxon history, not one species tip |
| Is coloured *takaoense* a regain? | population SNPs + RNA/pigment + candidate locus | topology/history + functional restoration test | Must reject parallel loss and introgression first |
| Did independent white lineages use the same mechanism? | replicated RNA/chemistry/genomics | orthologous candidate comparison | Tests molecular parallelism rather than phenotype alone |

## Final implementation decision

> **Compositae1061 target capture is the backbone technology; RAD-seq/resequencing is the focal population technology; transcriptomics and pigment chemistry establish the colour mechanism; cytogenetics determines how all genomic analyses are interpreted.**

This architecture reuses the strongest existing data, avoids wasting RAD libraries on already resolved species placement, and keeps true regain as a falsifiable hypothesis rather than a narrative assumption.
