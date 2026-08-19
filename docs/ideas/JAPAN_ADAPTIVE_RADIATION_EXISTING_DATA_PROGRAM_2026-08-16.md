# Japanese adaptive-radiation existing-data program — 2026-08-16

## Main question

Why did one Japanese *Cirsium* history generate most sampled Japanese diversity while other arrivals did not, and did rapid lineage accumulation coincide with rapid ecological/phenotypic diversification enabled by standing variation, reticulation and cytogenetic flexibility?

This document sharpens HMM3/HMM4/HMM6 without adding another headline hypothesis family.

## Existing-data meta-result before the heavy tree

The reproducible summary is frozen in:

- `analysis/summarize_japan_radiation_existing_data_meta.py`
- `data/evidence/japan_radiation_existing_data_meta_v1.json`
- `data/evidence/japan_adaptive_radiation_evidence_ladder_v1.csv`

Current descriptive results:

1. **Radiation-success asymmetry is extreme.** Of 38 sampled Japanese paper taxon concepts, 36 occur in the dominant radiation and 2 are current exceptions. The dominant history therefore contains 94.7% of sampled Japanese concepts and 18 times as many sampled taxa as all exceptions combined. Under the current 3-history point hypothesis the occupancy is 36:1:1. This is a sampled-richness asymmetry, not a diversification-rate estimate.
2. **The strongest secondary history is genuinely replicated phylogenetically.** *C. lineare* is exceptional in 3/3 high-dimensional analyses and 2/2 independent high-dimensional data-generation groups. *C. dipsacolepis* remains a strong but single-group candidate secondary arrival.
3. **Species-tip coding visibly compresses recent trait history.** All 4 reviewed W/C-polymorphic systems lose state multiplicity when reduced to one taxon-level `P` state. Only 1/4 currently has direct morph↔high-dimensional-genotype linkage. In var. *takaoense*, keeping W/C samples separate changes the minimum count from 1 to 2.
4. **Cytogenetic diversity is already present inside the focal dominant radiation.** The current sparse focal audit contains 2x, 4x and 6x states among four dominant-radiation taxa. This establishes heterogeneity but cannot estimate transition density or show a diversification effect.
5. **Macroscopic trait variation is large but not one-dimensional.** The independent Azami snapshot spans 216 taxa, 3,725 observations, 6,626 heads and 9 endpoints; visible variance below assigned-species means remains large, while the precision-aware cross-module variation–climate coupling is near zero. This motivates modular trait analyses but is not evolutionary-rate or adaptation evidence.
6. **Reticulation/ILS and genome-size/ploidy change are real components of the system, but their coupling to radiation success is not yet quantified.** They remain candidate enabling processes, not demonstrated drivers.

## The sharpened HMM3 question

HMM3 should no longer be phrased vaguely as “the dominant radiation was more evolvable.” It becomes a sequence of falsifiable comparisons:

### HMM3-A — radiation-success asymmetry

After age and sampling correction, does the dominant Japanese radiation still show greater lineage accumulation than secondary Japanese histories?

### HMM3-B — ecological/phenotypic divergence

Does the dominant radiation show greater or faster niche-space and capitulum-trait divergence than the *lineare* and *dipsacolepis* histories and their continental comparators?

### HMM3-C — enabling genomic/cytogenetic processes

Are gene-tree/cytonuclear discordance, reticulation support, ploidy transitions or genome-size shifts enriched in the dominant radiation relative to non-radiating histories?

### HMM3-D — phenotypic diversification versus lineage sorting

Do large trait differences occur on branches/internodes that still show high gene-tree discordance, consistent with phenotype/ecology diverging before complete lineage sorting?

This last pattern would support rapid phenotypic divergence during an incompletely sorted radiation. It does not by itself prove adaptation or identify the causal allele source.

## What to finish with existing/public data first

No new biological sampling is required for the first pass of these analyses once the accepted 294/296 branch-length topology ensemble exists.

1. **Radiation structure:** descendant richness, branch-length structure, internode compression and lineage accumulation for the dominant radiation versus *lineare* / *dipsacolepis* histories.
2. **Gene-tree discordance:** extract quantitative concordance/discordance metrics from recoverable gene trees instead of binary “hybridization present” literature flags.
3. **Trait bridge:** join Azami colour, orientation, outline and existing involucre/spine proxies to reconciled direct EAzami tips while retaining uncertainty/polymorphism.
4. **Niche bridge:** build comparable public-occurrence niche summaries for dominant Japanese radiation, secondary histories and continental sisters under the same filtering/variable scheme.
5. **Cytogenetic sensitivity:** map source-backed chromosome/ploidy/genome-size states onto the accepted tree, explicitly treating missing population cytotypes as unknown.
6. **Cross-scale model:** compare descendant richness, trait/niche divergence, discordance and cytogenetic shifts with clade age and sampling controls. HMM3/HMM4 are supported only if the relationships survive topology and leave-one-clade-out sensitivity.

## What cannot be learned reliably without new data

The machine-readable stop/gate table is `data/evidence/japan_radiation_data_requirement_gates_v1.csv`.

### Population ancestry / morph history

Public species-level tips do not reveal whether unsampled white/coloured populations represent standing variation, introgression or recurrent mutation. This requires morph-linked population RAD/resequencing, with plastid and ploidy companions.

### Population cytotypes

Taxon-level 2n/ploidy records cannot establish the cytotype of the sequenced field individuals. Flow cytometry/genome-size measurement must be linked to the same population-genomic samples where possible.

### Adaptive function

Global or phylogenetic trait–environment correlation cannot establish that a trait increased fitness. Representative repeated transitions require field/common-garden tests connecting orientation/colour/phyllary-spines to pollination, abiotic protection, antagonists and reproductive output.

### Repeated molecular mechanism

Homolog recovery or young-leaf RNA is insufficient. Replicated systems require ancestry + coding/haplotype + floral-stage expression + pigment + phenotype in linked individuals.

## Current claim hierarchy

### Strong now

- rapid Japanese radiation;
- strong sampled radiation-success asymmetry;
- real ILS/reticulation and cytogenetic dynamism in the broader young East-Asian system.

### Partial now

- young-lineage ecological/phenotypic divergence;
- trait modularity/decoupling;
- under-resolution of recent W/C transitions under species-tip coding.

### Still unresolved

- elevated trait-diversification rate of the dominant radiation;
- elevated niche-diversification rate;
- reticulation/ploidy as causal or predictive evolvability drivers;
- strict adaptive radiation.

## Promotion rule

Do not write “Japanese *Cirsium* is an adaptive radiation” until comparative tree/niche/trait evidence and representative replicated fitness tests both support it. Until then use:

- **rapid Japanese radiation**;
- **radiation-success asymmetry**;
- **ecological/phenotypic radiation candidate**;
- **adaptive-radiation / evolvability hypothesis**.
