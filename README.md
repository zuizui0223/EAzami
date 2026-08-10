# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic, population-genomic and molecular framework needed to test those transitions.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project starts with Japan, the Ryukyu Islands, Taiwan and China and expands through Korea, Sakhalin and the Russian Far East when those populations change a flower-colour history. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Current biological inference

Existing nuclear phylogenies plus source-backed flower-colour states make **repeated white-flower evolution** the leading hypothesis. **True coloured regain/reactivation is not yet demonstrated.**

- Taiwanese Nipponocirsium supports an independent white loss in *C. kawakamii*.
- Published sister context around Arenicola favours white loss in *C. brevicaule*, not regain in *C. irumtiense*.
- Bluish-purple var. *takaoense* is the strongest current regain candidate, but two parallel white losses are equally parsimonious with one shared loss plus one regain.
- Population-aware coding is essential: splitting white and coloured var. *takaoense* populations increases the minimum transition count relative to one ambiguous species tip.

A regain claim requires a population-aware nuclear history, exclusion or modelling of introgression, evidence that the anthocyanin pathway remained recoverable in the white lineage and a derived functional or regulatory change linked to phenotype in the same individuals.

See:

- `docs/PRELIMINARY_HYPOTHESES_2026-08-09.md`
- `docs/ARENICOLA_DIRECTION_UPDATE_2026-08-10.md`
- `docs/SINOCIRSIUM_DIRECTION_UPDATE_2026-08-10.md`
- `analysis/fitch_transition_sensitivity.csv`

## Linked objectives

1. **Flower-colour atlas:** retain population/morph-level white, pink and purple evidence instead of collapsing every taxon to one species mean.
2. **Evolutionary history:** reconstruct independent loss, ancestral polymorphism, introgression and candidate regain across a topology ensemble.
3. **East Asian species backbone:** reuse existing nuclear phylogenomics and fill only genuine transition-critical gaps.
4. **Population history:** resolve white/coloured morphs, geographic bridges and local ancestry with RAD-seq or resequencing.
5. **Molecular mechanism:** combine anthocyanin chemistry, floral RNA-seq and candidate-region genomics.
6. **Selection:** test pollinator and abiotic fitness effects only after history and mechanism are sufficiently resolved.

## State of *Cirsium* phylogeny

The accurate current summary is neither “the phylogeny is solved” nor “almost nothing is known.”

### Strongly developed

- the deep Asteraceae/Cardueae/Carduinae backbone from target capture and Hyb-Seq;
- a broad, though incomplete, global species-level *Cirsium* nuclear backbone;
- modern regional frameworks for North America, Japan and focal Taiwan/Ryukyu lineages;
- empirical evidence for hybridization, incomplete lineage sorting, allopolyploidy, cytomixis and cytonuclear discordance;
- reusable target-capture matrices, tree archives, nuclear genomes, transcriptomes and plastomes.

### Still disputed or incomplete

- broad *Cirsium* versus *Lophiolepis* and other generic circumscriptions;
- exact sample/tree recovery for some published studies;
- one compatible nuclear framework densely spanning all East Asian regions;
- population placement of white and coloured morphs;
- introgression, standing variation and cytotype/homeolog structure within focal systems;
- the existence of any true white-to-coloured evolutionary regain.

Complete plastomes and plastid trees are retained as **maternal-history evidence**, not treated as substitutes for a multilocus nuclear species tree.

## Systematic phylogeny evidence map

Release v0.3 validates **54 curated primary studies or reusable public data resources** spanning 1999–2026.

| Tier | Records | Role |
|---|---:|---|
| A | 13 | phylogenomics, phylotranscriptomics, target capture, decisive genome-wide reticulation evidence and reusable tree/read resources |
| B | 14 | useful multilocus frameworks, species delimitation, historical biogeography and reusable nuclear/genomic references |
| C | 18 | cytogenetics, population hybridization, morphological cladistics and lower-locus regional evidence that constrains alternative histories |
| D | 9 | organelle-only, morphology/type-based and nomenclatural evidence retained for maternal history and name reconciliation |

The evidence history now runs continuously from foundational Carduinae morphology/ITS studies, through combined nuclear–plastid and biogeographic analyses, to Compositae target enrichment, global *Cirsium* target capture, focal phylotranscriptomics and 2025–2026 integrative phylogenomics.

Key synthesis files:

- `docs/CIRSIUM_PHYLOGENY_EVIDENCE_MAP_RELEASE_V0_3.md`
- `docs/CIRSIUM_PHYLOGENY_STATE_OF_FIELD_2026-08-10.md`
- `docs/CIRSIUM_PHYLOGENY_SYSTEMATIC_SEARCH_PROTOCOL.md`
- `data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_literature_registry_additions_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_literature_registry_batch02b_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_literature_registry_batch03_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_consensus_and_gaps_2026-08-10.csv`
- `data/evidence/east_asia_cirsium_phylogeny_coverage_v0_2.csv`
- `data/evidence/cirsium_genomic_and_phylogenetic_resources_2026-08-10.csv`

Automated Crossref/Europe PMC candidates never enter the curated registry without manual screening and primary-source verification.

## Population-history evidence is a separate layer

Species trees and population histories answer different questions. The repository therefore stores a separate curated population-history registry rather than inflating microsatellite, landscape-genetic or expression studies into species-tree evidence.

Current registry:

- `data/evidence/cirsium_population_history_literature_2026-08-10.csv`
- `docs/CIRSIUM_POPULATION_HISTORY_STATE_OF_FIELD_2026-08-10.md`

Its initial seven studies show that:

- similar present-day demography can produce very different genetic geography;
- multiple introductions and admixture can mimic a newly derived response;
- historical corridors and current geographic distance are not interchangeable;
- expression divergence can track ancestry as well as environment;
- cytotype and introgression can decouple morphology from a species-tree tip.

This evidence defines the model alternatives required before any coloured morph is called a regain.

## Current nuclear anchors

### Foundational Compositae target enrichment

Mandel et al. developed conserved-ortholog target enrichment for Asteraceae and public 763-locus demonstration data. Later family-, tribe- and genus-scale studies establish the methodological continuity of Compositae target capture.

### Herrando-Moraira et al. 2019 — deep Cardueae

Compositae1061 Hyb-Seq provides the deep nuclear species-tree/outgroup framework and openly archived alignments, gene trees, species trees and dating materials. Nuclear and plastid histories are retained separately.

### Moreyra et al. 2023/2025 — Carduinae and global *Cirsium*

The 2025 study used **Compositae1061 target enrichment** and retained **350 nuclear loci after orthology assessment and filtering**. It sampled 299 plants representing 251 taxa, including 266 *Cirsium* accessions representing 248 species and 38 Japanese species. The 350 loci are an analysed subset of Compositae1061, not a separate bait kit.

Raw reads are under BioProject `PRJNA957074`. New species-level sequencing should connect to Compositae1061 and reproduce/intersect the published retained-locus filters rather than blindly rebuilding the global or Japanese tree.

### Chang et al. 2025/2026 — focal East Asia

Phylotranscriptomic data provide the current local frameworks for Nipponocirsium, Sinocirsium and Arenicola and document genome-size, chromosome and reticulation complexity. Raw reads are under `PRJNA1158676` and `PRJNA1311153`.

The unresolved layer is population structure, colour-associated ancestry and cytotype variation—not the basic species placement of the core Ryukyu and Taiwan taxa.

### Nuclear-genome and transcript resources

The *C. nipponicum* draft nuclear genome and emerging Darwin Tree of Life *Cirsium* assemblies provide mapping, orthology, synteny and candidate-gene references. A Korean floral/leaf/root transcriptome supplies flavonoid-pathway annotation. These resources do not by themselves constitute a dense East Asian species tree.

## Two-layer phylogenomics design

The East Asian tree should **not** be generated as one giant RAD-seq dataset across all species.

### Layer 1 — species backbone

Use **Compositae1061-compatible target capture** for genuine missing East Asian taxa and merge it with existing public data.

Primary outputs:

- conservative single-copy matrix;
- Moreyra-compatible retained-locus matrix;
- multi-copy/paralog-aware matrix;
- concatenated tree;
- ASTRAL species tree;
- ASTRAL-Pro-style sensitivity;
- separate plastid maternal tree;
- reduced-taxon network analyses.

### Layer 2 — focal population history

Use RAD-seq or resequencing for:

- white versus coloured var. *takaoense*;
- Japanese and continental *C. pendulum*;
- Japanese and Zhejiang *C. sieboldii*;
- *C. kawakamii* versus *C. tatakaense*;
- *C. brevicaule* versus *C. irumtiense*;
- verified Korean white forms.

RAD-seq is for population structure, local ancestry and gene flow after species placement is known. It is not expected to remain homologous across every deeply divergent East Asian lineage or cytotype.

See `docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md`.

## Ploidy and reticulation policy

Every focal population should carry:

- voucher and accepted/synonym names;
- fresh-leaf flow cytometry where possible;
- chromosome/cytotype evidence;
- standardized flower-colour phenotype;
- matched pigment, RNA and DNA samples;
- plastid haplotype as a separate maternal layer.

Analyses retain paralog/homeolog evidence rather than silently forcing one sequence per locus. HybPiper paralog warnings, conservative filtering, ASTRAL-Pro-style analyses, phasing and reduced-taxon network analyses are complementary sensitivities.

## Reproducible evidence and artifact recovery

- `analysis/build_cirsium_phylogeny_registry.py` validates and merges the human-screened phylogeny evidence batches and fails on DOI/key conflicts.
- `analysis/validate_cirsium_population_history_registry.py` independently validates the population-history registry.
- `analysis/recover_cirsium_phylogeny_literature.py` queries Crossref and Europe PMC and outputs unreviewed candidates only.
- `analysis/recover_ncbi_project_runs.py` reconstructs public sample sets from official NCBI SRA metadata.
- `analysis/recover_published_phylogeny_artifacts.py` tracks/downloads legal public tree and supplement artifacts.
- `.github/workflows/recover-cirsium-phylogeny-literature.yml` validates both evidence layers and performs monthly/manual candidate recovery.

The directly verified Moreyra anchor is *C. domonii* (`SAMN34240283`, `SRS18284452`, `SRX21011499`, `SRR25265717`). A project non-match is not treated as biological absence until accepted names, synonyms, unsequenced supplementary tips and alternative nuclear datasets are checked.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times.
- **H2 — regain/reactivation:** at least one coloured lineage descends from a white ancestor or intermediate.
- **H3 — regulatory reuse:** independent white transitions repeatedly suppress a conserved anthocyanin regulatory network.
- **H4 — repeated molecular route:** independent transitions target homologous regulatory modules even when exact mutations differ.
- **H5 — historical alternatives:** some apparent loss/regain events reflect ancestral polymorphism, introgression or polyploid/reticulate history.

## Current focal systems

1. Taiwan var. *takaoense*: same-lineage white and bluish-purple morphs.
2. Japan/continent *C. pendulum*: documented Japanese white form against a broad coloured range.
3. Japan/Zhejiang *C. sieboldii*: white and reddish-purple Japanese forms plus continental populations.
4. Taiwan *C. kawakamii*–*C. tatakaense*: matched polyploid white/coloured replicate.
5. Ryukyu *C. brevicaule*–*C. irumtiense*: repeated white-loss mechanism and gene-flow test.
6. Korea–NE Asia historical white-form candidates pending extant/voucher verification.

## Work tracked as GitHub issues

- #2 — paired white/coloured field sampling
- #3 — pigment chemistry, floral RNA-seq and causal-region genotyping
- #4 — RAD-seq + ploidy sampling and reticulation tests
- #5 — downstream selection tests
- #6 — complete flower-colour atlas
- #7 — exact published tree files and branch lengths
- #8 — exact Japanese placements and Korea/NE Asia expansion
- #9 — systematic global phylogeny, reticulation and cytogenetics evidence map

## Analyses that continue before field data

1. Complete backward and forward citation snowballing for every Tier-A anchor.
2. Recover exact Moreyra, Herrando-Moraira, Chang and recent Cardueae tree/sample/locus artifacts.
3. Quantify overlap and filtering among the original Compositae targets, Compositae1061 and Moreyra's retained 350 loci.
4. Complete accepted-name, synonym, voucher and alternative-genus harmonization.
5. Complete the East Asian population-aware flower-colour atlas.
6. Join nuclear, plastid, ploidy, reticulation and population evidence without collapsing evidence levels.
7. Run full-tree ML/stochastic ancestral-state reconstruction across alternative nuclear topologies.
8. Quantify which missing taxon or population changes transition count/direction most strongly.
9. Freeze target-capture/RAD panel v1.0 from information gain rather than raw taxon count.

No large WGS cohort should be finalized before this transition/gap screen is complete.
