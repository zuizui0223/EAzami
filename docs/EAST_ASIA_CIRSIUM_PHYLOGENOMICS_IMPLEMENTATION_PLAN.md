# East Asian *Cirsium* phylogenomics implementation plan

Date: 2026-08-10  
Revision: v0.2 after exact Moreyra sample and public locus-filter audit

## Decision summary

The East Asian phylogeny should **not** be built as one giant RAD-seq experiment across all taxa. The defensible architecture has two linked layers:

1. **Species-level backbone:** Compositae1061-compatible target capture only for genuine transition-critical taxa missing from modern nuclear data.
2. **Population/morph history:** RAD-seq or resequencing within selected white/coloured systems whose species placement is already known.

The integrated Moreyra–Chang audit currently contains 33 transition-relevant taxa. Twenty-one have modern species-level nuclear placement, and no active Tier-A focal taxon remains a species-placement gap. The main unresolved questions concern morph identity, local ancestry, gene flow, standing variation, introgression, cytotype and molecular mechanism.

## 1. Existing data that should be reused

### 1.1 Deep and global backbone

Use:

- Herrando-Moraira et al. Cardueae Hyb-Seq matrices and trees;
- Moreyra et al. 2025 PRJNA957074 reads and Supplementary Table S1;
- Siniscalchi et al. North American Compositae target-capture data as a regional compatibility check;
- existing high-quality outgroups from the same target system.

### 1.2 Focal East Asian regional frameworks

Use the full Chang 2025/2026 phylotranscriptomic trees as regional topology constraints. Their non-Compositae orthogroups should not be discarded merely because they do not overlap the target-capture panel.

Current focal sample coverage includes:

- Sinocirsium and Arenicola in Chang 2026;
- Taiwanese and Japanese Nipponocirsium in Chang 2025;
- exact Moreyra target-capture tips for `C. pendulum`, `C. sieboldii`, `C. yezoense`, `C. dipsacolepis`, `C. domonii`, `C. lineare`, `C. nipponicum` and `C. vlassovianum`.

## 2. Marker choice

Use **Compositae1061-compatible target enrichment** for verified missing species-level lineages.

Reasons:

- it connects family-, tribe-, regional- and global-scale nuclear datasets;
- it was the capture framework used by Moreyra et al. 2025;
- it is more appropriate for cross-species backbone construction than one RAD panel across highly divergent taxa and cytotypes;
- it permits explicit paralog/homeolog analysis rather than treating all multi-copy recovery as missing data.

The paper's 350 loci are a filtered analysis subset, not a separate bait kit.

## 3. Correction from the Moreyra public locus audit

The corresponding author's public repository contains:

- `hybpiper_stats_exonerate.tsv`;
- `seq_lengths_exonerate.tsv`;
- `paralog_report.xlsx`.

It does not contain the final Newick trees, retained 350 alignments, per-locus gene trees or an explicit final 350-locus list.

The public files expose 1,061 named loci, whereas the paper reports 1,064 initially mapped loci. The three-locus difference remains unresolved.

The reproducible public screen yields:

| Stage | Loci |
|---|---:|
| Public named locus universe | 1,061 |
| More than 10 paralog-warning samples; automatic discard class | 478 |
| One to ten warnings; manual gene-tree review class | 307 |
| No warning | 276 |
| Raw sequence occupancy at least 0.80 | 1,001 |
| Warning count no more than 10 and occupancy at least 0.80 | 531 |
| No-warning and occupancy at least 0.80 | 241 |
| Paper-reported final alignments | 350 |

The exact reduction from 531 candidates to 350 cannot be reproduced because manual gene-tree orthology decisions and final alignment-level missingness are not publicly encoded.

Consequently, **`exact Moreyra 350 matrix` is a reserved, currently unavailable label.** No inferred 350-locus subset should be presented as the original set.

See:

- `docs/MOREYRA_2025_AUTHOR_REPOSITORY_LOCUS_AUDIT_2026-08-10.md`
- `data/evidence/moreyra2025_public_locus_filter_summary_2026-08-10.json`
- `analysis/recover_moreyra_author_repository.py`
- `analysis/summarize_moreyra_locus_filter.py`

## 4. Nuclear matrices to generate

For existing and new target-capture samples, generate at least four explicitly named matrices.

### 4.1 Public-universe matrix

Recover all usable loci from the public 1,061-locus universe. This maximizes overlap with the author-repository summaries and retains the broadest possible starting point.

### 4.2 Reproducible 531-candidate matrix

Apply the public-data screen:

- no more than ten paralog-warning samples in the Moreyra public matrix;
- raw sequence occupancy at least 0.80 in the public sequence-length matrix.

This is a reproducible pre-manual candidate set, not the final published matrix.

### 4.3 Conservative no-warning matrix

Use the no-warning, high-occupancy loci as a stringent primary/sensitivity set. The public Moreyra screen identifies 241 such loci.

For the expanded East Asian matrix, re-evaluate copy number and occupancy rather than assuming that a locus remains single-copy after adding polyploid taxa.

### 4.4 Paralog/homeolog-aware matrix

Retain labelled copies and homeolog evidence for:

- ASTRAL-Pro-style analyses;
- HybPhaser or related phasing diagnostics;
- topology weighting;
- network tests;
- identifying polyploid or introgressed histories hidden by one-copy filtering.

## 5. Primary assembly and QC

Use HybPiper or an equivalent versioned pipeline with:

- exact target-file version;
- read, mapping and assembly statistics per sample;
- all paralog warnings retained;
- sequence-length and occupancy summaries;
- no silent selection of one sequence when multiple strong copies exist;
- explicit sample inclusion and missingness rules;
- reproducible gene-tree and alignment archives for every retained locus.

A second pipeline such as Captus or HybPhyloMaker can be used on a controlled subset when topology-sensitive discrepancies occur.

## 6. Species-tree and network ensemble

Create and version:

1. concatenated maximum-likelihood tree from a conservative matrix;
2. ASTRAL tree from conservative single-copy gene trees;
3. multi-copy/paralog-aware species tree;
4. tree from the reproducible public 531-candidate set;
5. tree from the stringent no-warning set;
6. Chang regional phylotranscriptomic topologies;
7. separate plastid maternal topology;
8. reduced-taxon network analyses for specific reticulation hypotheses.

Use quartet/local posterior support, gene and site concordance factors, and polytomy tests. Weak internodes should remain unresolved when the data do not reject a polytomy.

Do not infer branch lengths from published figures. Formal Mk and stochastic mapping require a documented branch-length source.

## 7. Plastid layer

Recover off-target plastid reads and existing plastomes as a separate maternal-history layer.

Outputs:

- plastid tree or haplotype network;
- nuclear–plastid discordance table;
- candidate chloroplast-capture events.

The plastid topology must not substitute for the nuclear species tree in flower-colour ancestral-state reconstruction.

## 8. Population layer for flower-colour history

### 8.1 var. *takaoense*

First recover the white/coloured identity of the six published transcriptome vouchers. Then sample multiple populations per morph, prioritizing mixed populations when present.

Distinguish:

- parallel white losses;
- shared white origin plus coloured reactivation;
- ancestral white/coloured polymorphism;
- coloured-haplotype introgression from related Sinocirsium ancestry.

### 8.2 *C. pendulum*

Reuse the Moreyra Trans-Baikal tip as a continental species anchor. New data should cover Japanese white and purple populations plus Korea, Northeast China and Primorye bridges.

### 8.3 *C. sieboldii*

The exact Moreyra tip was cultivated and has unresolved wild provenance. Sample Japanese white/purple populations and the Zhejiang bridge explicitly.

### 8.4 *C. kawakamii–C. tatakaense*

Both are 2n=64 and have modern phylotranscriptomic placement. Use ploidy-aware population genomics, floral RNA and pigment chemistry to test independent regulatory loss, homeolog sorting and introgression.

### 8.5 *C. brevicaule–C. irumtiense*

The published sister context favours white loss in `C. brevicaule`. Test gene flow, ancestral polymorphism and whether its white mechanism is homologous to other independent white lineages.

### 8.6 Conditional Korean and Northeast Asian systems

Do not promote a historical white-form name to sequencing priority until extant natural material or repeated voucher-backed occurrence is verified.

- `C. vlassovianum`: species placement exists; use population genomics if white populations are verified.
- `C. setidens` and `C. rhinoceros`: obtain Compositae1061 placement only if white material is verified and no other modern nuclear data exist.
- `C. schantarense`: verify white records and taxonomy before target capture or population genomics.

## 9. Ploidy-aware field and bioinformatic policy

For every focal population:

- retain voucher and source/accepted names;
- obtain fresh-leaf flow cytometry where feasible;
- store chromosome and cytotype provenance;
- separate mixed cytotypes before genotype calling;
- link standardized colour, pigment, floral RNA and leaf DNA to the same plant;
- retain allele balance, depth and excess-heterozygosity diagnostics;
- compare diploid and ploidy-aware genotype models;
- analyse single-copy and multi-copy matrices separately.

## 10. Mechanism layer

The phylogeny determines **where** a transition occurred. It does not identify **how**.

For matched individuals, collect:

- visible and UV reflectance;
- anthocyanin/flavonoid chemistry;
- floral RNA-seq at matched developmental stages;
- leaf DNA;
- candidate regulatory and structural loci;
- ploidy and voucher metadata.

Test:

1. independent disruptive mutations;
2. repeated suppression of homologous MBW-network nodes;
3. shared ancestral white haplotypes;
4. introgressed white or coloured haplotypes;
5. derived functional restoration on a white genetic background.

## 11. Deliverables before ordering species-backbone libraries

Required:

- frozen East Asian accepted-name/synonym table;
- integrated nuclear-coverage table;
- transition information-gain classification;
- exact vouchers and cytotypes for proposed samples;
- recovered public 1,061-locus universe;
- reproducible 531-candidate and conservative no-warning definitions;
- Herrando-Moraira tree/data archive;
- Chang sample/topology provenance;
- explicit statement that the original final 350 list and final Moreyra trees are unavailable unless subsequently recovered.

Select a 24–48-sample pilot only from taxa that remain genuine, transition-critical species gaps after this audit.

## 12. Pilot population decision

The first population pilot should include:

- one within-lineage white/coloured system: `var. takaoense`, after morph-linked sampling;
- one polyploid interspecific replicate: `C. kawakamii–C. tatakaense`.

Success criteria include:

- adequate loci after ploidy-aware QC;
- stable technical/biological replicate placement;
- interpretable population structure;
- ability to distinguish local from genome-wide ancestry;
- matched pigment and floral expression for mechanism.

## Final implementation decision

> **Compositae1061 target capture is the conditional species-backbone technology; RAD-seq or resequencing is the core morph/population technology; transcriptomics and pigment chemistry establish mechanism; cytogenetics determines how all genomic results are interpreted.**

The project will reuse the strongest available phylogenetic evidence, avoid paying to rediscover resolved species placements, and will not label a reconstructed locus set or a coloured lineage as `exact Moreyra 350` or `true regain` without the required evidence.
