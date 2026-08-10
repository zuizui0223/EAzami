# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic and population-genomic framework needed to test those transitions.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project starts with Japan, the Ryukyu Islands, Taiwan and China and expands through Korea, Sakhalin and the Russian Far East when those populations change a flower-colour history. It is the fine-scale evolutionary follow-up to the global image-derived trait work in `zuizui0223/azami`.

## Current biological inference

Existing nuclear phylogenies plus source-backed flower-colour states make **repeated white-flower evolution** the leading hypothesis. **True coloured regain/reactivation is not yet demonstrated.**

- Taiwanese Nipponocirsium supports a local independent white loss in *C. kawakamii*.
- The published sister context around Arenicola favours white loss in *C. brevicaule*, not regain in *C. irumtiense*.
- Bluish-purple var. *takaoense* is the strongest current regain candidate, but parallel losses remain equally parsimonious with one shared loss plus one regain.
- Population-aware coding is essential: splitting white and coloured var. *takaoense* populations increases the minimum transition count relative to one ambiguous species tip.

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

- the deep Cardueae/Carduinae backbone from Hyb-Seq;
- a broad global species-level *Cirsium* nuclear backbone;
- modern regional frameworks for North America, Japan and focal Taiwan/Ryukyu lineages;
- empirical evidence for hybridization, incomplete lineage sorting, allopolyploidy and cytonuclear discordance.

### Still disputed or incomplete

- broad *Cirsium* versus *Lophiolepis* and other generic circumscriptions;
- exact sample/tree recovery for some published studies;
- one compatible nuclear framework densely spanning all East Asian regions;
- population placement of white and coloured morphs;
- introgression, standing variation and cytotype structure within focal systems;
- the existence of any true white-to-coloured evolutionary regain.

Complete plastomes and small plastid trees are retained as **maternal-history evidence**, not treated as substitutes for a multilocus nuclear species tree.

## Comprehensive phylogeny evidence map

The repository no longer relies only on Chang and Moreyra. Release v0.1 contains **38 curated primary studies or public data resources**:

| Tier | Records | Role |
|---|---:|---|
| A | 9 | phylogenomics, transcriptomics, target capture, decisive genome-wide hybrid evidence and reusable public data |
| B | 10 | broad multilocus or regional species frameworks |
| C | 11 | cytogenetic, AFLP, local hybrid and taxonomic-debate evidence |
| D | 8 | organelle-only, morphology/type-based and historical-form evidence |

Curated files and synthesis:

- `data/evidence/cirsium_phylogeny_literature_registry_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_literature_registry_additions_2026-08-10.csv`
- `data/evidence/cirsium_phylogeny_consensus_and_gaps_2026-08-10.csv`
- `data/evidence/east_asia_phylogenomics_method_registry_2026-08-10.csv`
- `docs/CIRSIUM_PHYLOGENY_STATE_OF_FIELD_2026-08-10.md`
- `docs/CIRSIUM_PHYLOGENY_EVIDENCE_MAP_RELEASE_V0_1.md`
- `docs/CIRSIUM_PHYLOGENY_SYSTEMATIC_SEARCH_PROTOCOL.md`

Automation:

- `analysis/build_cirsium_phylogeny_registry.py` validates and merges curated registries and fails on DOI/key conflicts.
- `analysis/recover_cirsium_phylogeny_literature.py` queries official Crossref and Europe PMC APIs, deduplicates records and outputs **unreviewed candidates only**.
- `.github/workflows/recover-cirsium-phylogeny-literature.yml` runs offline tests on pull requests and monthly/manual candidate recovery.
- `tests/test_recover_cirsium_phylogeny_literature.py`
- `tests/test_build_cirsium_phylogeny_registry.py`

Automated candidates never enter the curated registry without manual screening and source verification.

## Current nuclear anchors

### Herrando-Moraira et al. 2019 — deep Cardueae

Compositae1061 Hyb-Seq provides the deep nuclear species-tree/outgroup framework and openly archived alignments, gene trees, species trees and dating materials. Nuclear and plastid histories are retained separately.

### Moreyra et al. 2023/2025 — Carduinae and global *Cirsium*

The 2025 study used **Compositae1061 target enrichment** and retained **350 nuclear loci after orthology assessment and filtering**. It sampled 299 plants representing 251 taxa, including 266 *Cirsium* accessions representing 248 species and 38 Japanese species. The 350 loci are an analysed subset of Compositae1061, not evidence of a separate bait kit.

Raw reads are under BioProject `PRJNA957074`. New species-level sequencing should therefore connect to Compositae1061 and reproduce/intersect the published retained-locus filters rather than blindly rebuilding the global or Japanese tree.

### Chang et al. 2025/2026 — focal East Asia

Phylotranscriptomic data provide the current local frameworks for Nipponocirsium, Sinocirsium and Arenicola and document genome-size, chromosome and reticulation complexity. Raw reads are under `PRJNA1158676` and `PRJNA1311153`.

The unresolved layer is population structure, colour-associated ancestry and cytotype variation—not the basic species placement of the core Ryukyu and Taiwan taxa.

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
- ASTRAL-Pro 2 sensitivity;
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

Analyses retain paralog/homeolog evidence rather than silently forcing one sequence per locus. HybPiper paralog warnings, conservative filtering, ASTRAL-Pro 2, HybPhaser-style phasing and reduced-taxon network analyses are treated as complementary sensitivities.

## Reproducible recovery of published samples

`analysis/recover_ncbi_project_runs.py` reconstructs public sample sets from official NCBI SRA metadata and outputs:

- run-level metadata;
- unique-taxon summary;
- exact focal-name audit;
- optional BioSample locality/date enrichment.

The directly verified Moreyra anchor is *C. domonii* (`SAMN34240283`, `SRS18284452`, `SRX21011499`, `SRR25265717`). A project non-match is not treated as biological absence until accepted names, synonyms, unsequenced supplementary tips and other nuclear datasets are checked.

See:

- `docs/PRJNA957074_RECOVERY_UPDATE_2026-08-10.md`
- `docs/PRJNA957074_RECOVERY_RUNBOOK.md`
- `.github/workflows/recover-ncbi-project-metadata.yml`

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times.
- **H2 — regain/reactivation:** at least one coloured lineage descends from a white ancestor or intermediate.
- **H3 — regulatory reuse:** independent white transitions repeatedly suppress a conserved anthocyanin regulatory network.
- **H4 — repeated molecular route:** independent transitions target homologous regulatory modules even when exact mutations differ.
- **H5 — historical alternatives:** some apparent loss/regain events reflect ancestral polymorphism, introgression or polyploid/reticulate history.

`Regain` and `reactivation` are hypotheses, not assumed states. A regain claim requires concordant ancestral-state, population-history and molecular evidence.

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

1. Screen automated literature candidates and complete backward/forward citation snowballing.
2. Recover exact Moreyra, Herrando-Moraira and Chang tree/sample/locus artifacts.
3. Complete accepted-name, synonym and alternative-genus harmonization.
4. Complete the East Asian population-aware flower-colour atlas.
5. Join nuclear, plastid, ploidy and reticulation evidence without collapsing their evidence levels.
6. Run full-tree ML/stochastic ancestral-state reconstruction across alternative nuclear topologies.
7. Quantify which missing taxon or population changes transition count/direction most strongly.
8. Freeze target-capture/RAD panel v1.0 from information gain rather than raw taxon count.

No large WGS cohort should be finalized before this transition/gap screen is complete.
