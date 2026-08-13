# Chang et al. 2026 `var. takaoense` morph-linked existing-data screen

Date: 2026-08-11

## Result that changed the immediate plan

The official Springer Nature Figure 1 image was recovered directly and its source was frozen:

- DOI: `10.1186/s12870-026-08097-6`
- image: `12870_2026_8097_Fig1_HTML.png`
- dimensions: 1,945 × 2,400 px
- SHA256: `10375f1d79a4799babdebffca84301f602adfa0aabc825b852de84177bbb878c`

Figure 1 panels B and C independently print the same morph suffixes for all six published `Cirsium japonicum var. takaoense` transcriptome tips.

| Morph | Published tips | Public runs |
|---|---|---|
| White `(W)` | `WY-3560`, `FB-3629`, `LT-3839` | `SRR35152717`, `SRR35152738`, `SRR35152734` |
| Bluish-purple `(BP)` | `FC-3559`, `TJ-3807`, `NH-3835` | `SRR35152718`, `SRR35152736`, `SRR35152735` |

The numeric portions of the figure labels correspond exactly to Supplementary Table S1 vouchers, NCBI `SampleName` suffixes and BioSample `isolate` attributes. The accession and morph linkage is therefore complete for all six published plants.

Frozen evidence:

- `data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv`
- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv`

## What the published topology now establishes

The exact labels confirm that both morphs were included in the same sampled `var. takaoense` lineage. The paper describes white- and bluish-purple-corolla groups as a paraphyletic assemblage and emphasizes reticulation within the Taiwanese complex. Consequently:

- flower colour is not equivalent to the current taxonomic lineages;
- the six samples should no longer be collapsed to one ambiguous species-level colour state;
- the published evidence does not require a single monophyletic white or coloured morph lineage;
- a coloured regain remains possible but is not identified by the figure alone;
- introgression, ancestral polymorphism and repeated mutation remain live alternatives.

The exact final Newick and branch lengths are still unavailable. The published figure can support direct tip identities and topology-level interpretation, but it must not be converted into invented numerical branches.

## Metadata screen of the six published samples

The direct W/BP labels were joined to Supplementary Table S1 altitude and NCBI accessions. In this six-sample set:

| Quantity | Result |
|---|---:|
| Mean altitude, BP | 1,160.67 m |
| Mean altitude, W | 357.00 m |
| BP − W mean difference | 803.67 m |
| Median altitude, BP | 1,127 m |
| Median altitude, W | 73 m |
| Minimum BP altitude | 991 m |
| Maximum W altitude | 977 m |

The three BP samples are all above the three W samples in altitude rank. Enumerating all `choose(6,3) = 20` possible assignments of three BP labels gives:

- one-sided descriptive permutation tail: `1/20 = 0.05`;
- two-sided absolute-difference tail: `2/20 = 0.10`.

Deleting any one sample leaves a positive BP-minus-W mean difference, ranging from 635.67 to 1,113.67 m.

Reproducible outputs:

- `analysis/takaoense_published_morph_metadata_screen.py`
- `analysis/takaoense_published_morph_altitude_screen.csv`
- `analysis/takaoense_published_morph_altitude_permutations.csv`
- `analysis/takaoense_published_morph_altitude_leave_one_out.csv`
- `analysis/takaoense_published_morph_metadata_screen_summary.json`

## Interpretation boundary

### Supported

> The six published transcriptome samples contain a strong altitude-stratified morph pattern that should inform balanced sampling and competing ancestry models.

### Not supported

The six samples do not establish:

- altitude-dependent natural selection;
- an environmental reaction norm;
- a causal climatic effect;
- an adaptive advantage of either colour;
- the direction of the white/coloured evolutionary transition.

Reasons:

- one plant was sequenced per locality;
- the samples were not randomly selected for an altitude test;
- altitude is confounded with geography, island/coastal context and population history;
- there is no within-population replication;
- the apparent threshold is defined by six observations.

The result is a sampling and model-design signal, not a selection result.

## What the existing transcriptomes can now test

The six samples are young-leaf RNA-seq, not floral RNA-seq. Their most defensible uses are:

1. **Morph-aware genome-wide ancestry screen**
   - assemble homologous expressed loci;
   - estimate PCA/kinship or gene-tree clustering;
   - test whether W/BP ancestry is genome-wide or largely geographic.

2. **Reticulation and source-lineage screen**
   - include `var. albescens`, `var. australe`, `var. fukienense` and `var. japonicum` controls;
   - test whether BP `takaoense` is locally closer to coloured neighbouring lineages than W `takaoense` is;
   - distinguish a broad introgression signal from one restricted to candidate pathways.

3. **Candidate coding-variation screen**
   - recover expressed anthocyanin-pathway structural and regulatory genes where present;
   - search for morph-associated coding changes, stop codons or homeolog patterns;
   - retain absence as missing expression/coverage, not as a deleted gene.

4. **Topology sensitivity**
   - recode all six published tips by morph;
   - test results across the ASTRAL figure topology, an unresolved `takaoense` polytomy and network-compatible alternatives;
   - do not treat weak internal branches as settled history.

## What the existing transcriptomes cannot establish

Young-leaf transcriptomes cannot directly establish:

- floral anthocyanin expression;
- petal/floret-specific regulatory suppression;
- developmental reactivation in the corolla;
- the causal promoter/enhancer state;
- whether an unexpressed floral gene is absent from the genome.

A true molecular reactivation claim still requires matched floral tissue, pigment chemistry and genomic causal-region evidence from the same plants or populations.

## Revised field sampling priorities

The metadata pattern makes simple high-versus-low elevation sampling dangerous. A discriminating design should deliberately obtain:

1. W and BP individuals from the same population where polymorphism occurs;
2. replicated high-elevation W populations;
3. replicated low-elevation BP populations;
4. geographically close W/BP population pairs;
5. cytotype and voucher information for every individual;
6. matched flower pigment, floral RNA and leaf DNA.

This design separates colour from altitude and geography instead of reproducing the confounding already present in the six published samples.

## Current hypothesis ordering

1. **Repeated/standing regulatory variation** — remains the broad working model.
2. **Ancestral polymorphism plus geographic sorting** — strengthened as a necessary alternative because morph and geography are structured.
3. **Introgression of a coloured or white haplotype** — remains plausible given the published reticulate context.
4. **True coloured reactivation** — remains the most interesting directional hypothesis, but requires white ancestry plus a derived restoration after the alternatives above are tested.
5. **Simple altitude adaptation** — hypothesis-generating only and not supported as a causal conclusion by the current six samples.

## Immediate next existing-data analysis

Build a morph-aware PRJNA1311153 analysis set containing:

- the six labelled `takaoense` samples;
- two white `albescens` samples;
- coloured `australe`, `fukienense` and Japanese `japonicum` controls;
- appropriate outgroups.

The first outputs should be sample identity/QC, expressed-locus occupancy, ancestry/PCA, gene-tree concordance and candidate-pathway coverage. Floral expression and causal reactivation remain new-data tasks.
