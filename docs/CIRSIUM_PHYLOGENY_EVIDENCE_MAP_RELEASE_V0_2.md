# *Cirsium* phylogeny evidence map — release v0.2

Date: 2026-08-10

## Release summary

The curated evidence map now contains **47 primary studies or reusable public data resources**. This release expands v0.1 beyond the initial global and East Asian anchors in four directions:

1. the methodological origin and family-scale use of Compositae target capture;
2. historical Japanese diversification hypotheses preceding modern target capture;
3. Taiwanese species/cytotype descriptions that define flower-colour contrasts later placed by phylotranscriptomics;
4. whole-genome, transcriptome, plastome, cytogenetic and population-hybrid resources that constrain how a species tree may be interpreted.

### Evidence-tier composition

| Evidence tier | Records | Interpretation in EAzami |
|---|---:|---|
| A | 11 | Deep or species-level phylogenomics, reusable target-capture/tree resources, decisive genome-wide reticulation evidence |
| B | 11 | Useful multilocus regional frameworks, species delimitation with molecular evidence, or a reusable nuclear reference genome that is not itself a dense species tree |
| C | 16 | Cytogenetics, population hybridization, karyotype-supported taxonomy and historical diversification hypotheses that define alternative histories |
| D | 9 | Plastome-only, morphology/type-based and nomenclatural evidence used for maternal history and taxon reconciliation |
| **Total** | **47** | Manually curated records; automated search candidates remain outside this count |

The validated registry builder merges the core and additions files and fails on duplicate citation keys, duplicate DOI assignments, malformed DOI values or invalid evidence tiers.

## 1. Revised historical view of the field

The development of present-day *Cirsium* phylogenomics is now represented as a sequence rather than a jump from a few Sanger trees directly to Moreyra and Chang.

### Phase 1 — low-copy and organelle molecular frameworks

Early ITS/ETS and chloroplast-region studies established broad Cardueae and regional hypotheses but left recent radiations and cytonuclear disagreement poorly resolved. These studies remain valuable for historical topology hypotheses and name matching, not as the preferred current backbone.

### Phase 2 — reusable Compositae target enrichment

Mandel et al. (2014; DOI `10.3732/apps.1300085`) developed conserved-ortholog capture probes for Asteraceae and recovered phylogenetic information from 763 loci in a family-wide demonstration. Mandel et al. (2019; DOI `10.1073/pnas.1903871116`) then used genomic data from 256 terminals to resolve the family backbone and diversification history.

Herrando-Moraira et al. (2019) brought Hyb-Seq and a large conserved-ortholog set into Cardueae, while Siniscalchi et al. (2023) and Moreyra et al. (2025) applied compatible target-enrichment logic to regional and global *Cirsium* radiation questions.

**Consequence:** Compositae1061-compatible target capture is the preferred route for genuine species-level East Asian gaps because it connects to existing family, tribe, North American and global *Cirsium* matrices. RAD-seq is retained for population history rather than used as the universal cross-species backbone.

### Phase 3 — local phylotranscriptomics and cytogenetic integration

Chang et al. (2025, 2026) used thousands of transcriptome orthogroups together with chromosomes, genome size and morphology to resolve focal Taiwan–Ryukyu–Japan lineages. Their studies demonstrate that a young local radiation can be well resolved at species level while still retaining unresolved population topology, introgression, incomplete lineage sorting and homeolog/cytotype questions.

## 2. Japan: historical radiation concept versus modern nuclear evidence

Kadota (2007; DOI `10.11110/kjpt.2007.37.4.335`) provided an influential taxonomic and biogeographic account of Japanese *Cirsium* diversification before genomic species trees were available. Moreyra et al. (2025) subsequently placed 38 Japanese species in a 350-retained-locus nuclear analysis derived from Compositae1061 target enrichment.

These sources have different roles:

- Kadota supplies the historical species concepts, infrageneric hypotheses and nomenclatural baseline;
- Moreyra supplies the current broad nuclear test of Japanese radiation history;
- neither resolves white versus coloured populations within *C. pendulum* or *C. sieboldii*;
- exact Moreyra tip names and sister relationships still require Supplementary Data 1 and tree-artifact recovery.

**Status:** Japan does not need a blind species-tree rebuild. It needs exact tip reconciliation, transition-critical missing taxa where genuine, and population-scale sampling of colour polymorphisms and continental bridge populations.

## 3. Taiwan: phenotype and cytotype evidence now linked explicitly to the nuclear framework

The original descriptions of *C. tatakaense* and *C. taiwanense* are now included as separate evidence layers.

- *C. tatakaense* was described as purplish-red-flowered and tetraploid (`2n = 64`) relative to white-flowered *C. kawakamii* with the same chromosome count.
- *C. taiwanense* added a yellow-flowered dysploid state (`2n = 32`) outside the best-sampled focal colour systems.

These papers do not substitute for a nuclear species tree. They provide the type-linked phenotype, locality and cytotype evidence that gives biological meaning to the later Chang phylotranscriptomic placement.

**Consequence for flower-colour reconstruction:** colour coding should be accession/population aware and retain chromosome state. A taxon description and a nuclear tip must be joined through voucher/name provenance rather than assumed to refer to an interchangeable biological unit.

## 4. Nuclear genomes are emerging but remain sparse and uneven

The resource registry now distinguishes whole-genome assemblies from species-tree datasets.

### East Asian reference

The 2024 draft genome of *C. nipponicum* is 929.4 Mb, has a contig N50 of approximately 0.7 Mb and captures 95.1% of the tested eudicot BUSCO set. It is useful for:

- read mapping;
- gene annotation;
- anthocyanin-pathway candidate discovery;
- conserved-region and synteny comparisons.

Its comparative tree contains *C. nipponicum* plus ten other plant genomes rather than dense internal *Cirsium* sampling. It therefore does **not** close the Korean *Cirsium* species-tree gap.

### Western Palearctic references

Darwin Tree of Life projects now provide chromosome-level or emerging assemblies for *C. heterophyllum* and *C. dissectum*. These resources improve cross-species orthology, synteny and reference-bias assessment, but do not by themselves resolve East Asian population history.

### Transcriptome resource relevant to pigmentation

A Korean *C. japonicum* var. *spinossimum* flower/leaf/root RNA-seq resource recovered 51,133 unigenes and reported stronger floral expression of flavonoid-pathway genes. It is not a phylogenetic backbone, but it is directly useful for annotating pigment-pathway candidates before new floral RNA-seq.

## 5. Plastome evidence must remain a separate maternal layer

The *C. nipponicum* complete plastome study placed the Ulleung lineage closer to *C. arvense* and *C. vulgare* than to two Korean congeners in a six-species comparison. The study is a valid maternal-history hypothesis and supplies GenBank accession `MW248139`.

It cannot determine the organismal species tree because:

- one accession represents the focal taxon;
- plastids follow one nonrecombining maternal history;
- the within-genus sample is small;
- chloroplast capture is plausible in a hybridizing genus.

The same evidence rule applies to the many Chinese and Korean complete-plastome papers: a plastome record upgrades organelle coverage, not nuclear species-tree coverage.

## 6. Reticulation and cytogenetics are more pervasive than a tree-only view suggests

Two added evidence classes strengthen this conclusion.

- Iranian meiotic analysis of 21 populations from 17 species found B chromosomes, cytomixis and meiotic abnormalities, expanding the geographic evidence for variable reproductive/cytogenetic histories.
- Population analysis of *C. bertolonii* used AFLP, STRUCTURE, flow cytometry, chromosomes and morphometrics across 235 individuals and confirmed recurrent hybridization/introgression with two congeners.

These studies are not substitutes for a target-capture species tree. They show why apparent flower-colour reversal must be compared with:

1. parallel mutation;
2. standing ancestral polymorphism;
3. introgression;
4. allopolyploid/homeolog sorting;
5. chloroplast capture;
6. true regulatory reactivation after a white ancestor.

## 7. Current consensus at each scale

### Strongly resolved enough for use

- deep Asteraceae and Cardueae nuclear backbone;
- major Carduinae lineages;
- a broad but incomplete global *Cirsium* species tree;
- a substantial Japanese species-level context;
- focal Sinocirsium, Arenicola and Nipponocirsium relationships in Taiwan/Ryukyu/Japan;
- independent-white-loss interpretation for *C. kawakamii* under the current local nuclear topology;
- predominantly coloured sister context favouring a white loss in *C. brevicaule* rather than a regain in *C. irumtiense*.

### Genuine or likely biological gaps

- population history of white and bluish-purple var. *takaoense*;
- Japanese and continental population structure of *C. pendulum*;
- Japanese and Zhejiang population structure of *C. sieboldii*;
- gene flow and colour-haplotype ancestry within Arenicola;
- local ancestry and homeolog history in the *C. kawakamii*–*C. tatakaense* system;
- modern nuclear placement of verified Korean white-form systems where absent after synonym checking;
- China–Korea–Russian-Far-East population phylogeography;
- population cytotype distributions;
- causal regulatory/structural mechanisms of independent white transitions.

### Data-recovery rather than biological gaps

- exact Moreyra Newick, branch lengths and Supplementary Table S1;
- machine-readable Chang 2025/2026 trees;
- accepted-name versus submitted-name reconciliation in public reads;
- exact tree versions and licenses for topology-ensemble analysis.

## 8. Updated interpretation of the regain hypothesis

The expanded literature does not restore support for an assumed *C. irumtiense* regain. Under the published local nuclear context, white loss in *C. brevicaule* remains the simpler existing-data explanation.

Bluish-purple var. *takaoense* remains the strongest candidate for genuine regain because a history with one shared white transition followed by coloured restoration is as parsimonious as two parallel white losses. It is not yet a demonstrated regain because ancestral polymorphism and introgression remain viable.

A true regain claim requires all of the following:

1. a population-aware nuclear history supporting a white ancestor/intermediate;
2. exclusion or explicit modelling of colour-allele introgression;
3. evidence that the anthocyanin pathway remained functionally recoverable in the white lineage;
4. identification of a derived change restoring expression or function;
5. phenotype, pigment chemistry, expression and genotype linked in the same individuals.

## 9. Revised sequencing strategy

### Species-level gaps

Use Compositae1061-compatible target capture, integrate public datasets and analyze:

- a conservative single-copy matrix;
- a Moreyra-compatible retained-locus matrix;
- a paralog-aware matrix;
- concatenated and coalescent trees;
- ASTRAL-Pro or equivalent multi-copy analysis;
- a separate plastid tree;
- reduced-taxon network sensitivities.

### Population-level colour systems

Use RAD-seq or resequencing for structure, gene flow and local ancestry after species placement is known. Require:

- ploidy/cytotype evidence;
- vouchers and synonym provenance;
- matched standardized flower colour;
- pigment chemistry;
- floral RNA and leaf DNA;
- population and geographic replication.

## 10. Next evidence-map milestone

1. rerun the expanded search queries and manually screen novel records;
2. complete backward and forward citation snowballing for every Tier-A anchor;
3. recover exact Moreyra and Chang tree/sample artifacts;
4. join genome/transcriptome resources to the accepted-name table;
5. quantify modern nuclear coverage by East Asian region and lineage;
6. build a versioned nuclear-topology ensemble;
7. rerun full-tree population-aware ancestral-state reconstruction and stochastic mapping;
8. freeze target-capture and RAD panels only after the evidence/gap audit.

## Bottom line

The expanded evidence map strengthens—not weakens—the current study design:

> The deep and broad species-level framework of *Cirsium* is now substantial, but it is neither taxonomically complete nor population aware. East Asian flower-colour evolution is limited mainly by morph-level population history, reticulation, cytotype variation and uneven nuclear coverage, while whole-genome and transcriptome resources are only beginning to provide the reference framework needed to identify causal pigmentation mechanisms.
