# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic, population-genomic and molecular framework needed to test those transitions.

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project starts with Japan, the Ryukyu Islands, Taiwan and China and expands through Korea, Sakhalin, Mongolia and the Russian Far East only when those populations change a flower-colour history.

## Current biological inference

Existing nuclear phylogenies and source-backed flower-colour states support **repeated white-flower evolution** as the leading hypothesis. **True coloured regain/reactivation is not yet demonstrated.**

- Taiwanese Nipponocirsium supports an independent white loss in *C. kawakamii*.
- The published sister context around Arenicola favours white loss in *C. brevicaule*, not regain in *C. irumtiense*.
- Bluish-purple var. *takaoense* is the strongest current regain candidate, but parallel white losses remain equally parsimonious with one shared loss plus one regain.
- Collapsing polymorphic *takaoense* to one ambiguous taxon tip undercounts transitions.
- The six published *takaoense* transcriptome vouchers are not labelled as white versus bluish-purple, so the published sample tree cannot yet be recoded as a morph-specific tree.

A regain claim requires:

1. a population-aware nuclear history that reconstructs a white ancestor or intermediate;
2. explicit tests of introgression and ancestral standing variation;
3. evidence that the white lineage retains a recoverable anthocyanin pathway;
4. a derived functional or regulatory restoration linked to genotype, expression, pigment and phenotype in the same plants.

## Linked objectives

1. **Flower-colour atlas:** retain population/morph-level states instead of collapsing every taxon to one species mean.
2. **Evolutionary history:** distinguish independent loss, ancestral polymorphism, introgression and candidate regain across a topology ensemble.
3. **East Asian species backbone:** reuse existing nuclear phylogenomics and fill only genuine transition-critical gaps.
4. **Population history:** resolve white/coloured morphs and geographic bridges with RAD-seq or resequencing.
5. **Molecular mechanism:** combine pigment chemistry, floral RNA-seq and causal-region genomics.
6. **Selection:** test pollinator and abiotic fitness effects only after history and mechanism are sufficiently resolved.

## State of *Cirsium* phylogeny

The accurate summary is neither “the phylogeny is solved” nor “almost nothing is known.”

### Strongly developed

- deep Asteraceae/Cardueae/Carduinae nuclear backbones from target capture and Hyb-Seq;
- a broad, incomplete global species-level *Cirsium* nuclear tree;
- modern regional frameworks for North America, Japan and focal Taiwan/Ryukyu clades;
- empirical evidence for hybridization, ILS, allopolyploidy, cytomixis and cytonuclear discordance;
- public reads, sample tables, target-recovery summaries, genomes, transcriptomes and plastomes.

### Still incomplete

- broad *Cirsium* versus *Lophiolepis* and other generic circumscriptions;
- complete machine-readable final trees and branch lengths for key studies;
- the exact final 350-locus Moreyra matrix;
- one densely sampled, compatible nuclear framework across all East Asian regions;
- white/coloured population ancestry, introgression and cytotype/homeolog history;
- the existence of any rigorously supported white-to-coloured regain.

Plastid evidence is retained as a separate maternal-history layer, not substituted for a nuclear species tree.

## Systematic evidence map

Release v0.3 validates **54 manually curated phylogeny/systematics studies or public resources** spanning 1999–2026.

| Tier | Records | Role |
|---|---:|---|
| A | 13 | phylogenomics, phylotranscriptomics, target capture, decisive genome-wide reticulation evidence and reusable tree/read resources |
| B | 14 | multilocus frameworks, species delimitation, historical biogeography and reusable nuclear/genomic references |
| C | 18 | cytogenetics, population hybridization, morphology and lower-locus evidence constraining alternative histories |
| D | 9 | organelle-only, type-based and nomenclatural evidence used for maternal history and name reconciliation |

A separate **seven-study population-history registry** covers range-edge structure, fragmentation, invasion/admixture, expression divergence, landscape genetics and recurrent hybridization.

Automated Crossref/Europe PMC results remain unreviewed candidates and never enter the curated registry without manual primary-source screening.

Key files:

- `docs/CIRSIUM_PHYLOGENY_EVIDENCE_MAP_RELEASE_V0_3.md`
- `docs/CIRSIUM_PHYLOGENY_STATE_OF_FIELD_2026-08-10.md`
- `docs/CIRSIUM_POPULATION_HISTORY_STATE_OF_FIELD_2026-08-10.md`
- `data/evidence/cirsium_phylogeny_literature_registry_*.csv`
- `data/evidence/cirsium_population_history_literature_2026-08-10.csv`

## Exact Chang 2025/2026 audit

Official supplements were recovered, checksummed and table-extracted.

### Chang 2025

- 13 *Cirsium* transcriptome samples;
- exact voucher/locality/assembly records;
- source-backed colour and cytotype comparisons for Nipponocirsium;
- no machine-readable Newick in the supplement.

### Chang 2026

- 33 *Cirsium* samples from 12 taxa;
- exact voucher, coordinate, altitude, assembly and genome-size provenance;
- six *takaoense* tips, but no sample-level white/bluish-purple labels;
- no machine-readable Newick in the supplement.

The accessible article and official supplement do not contain located methods/results for the abstract/conclusion claims about anthocyanin expression or pollinator preference. Same-variety colour polymorphism and reticulation alternatives are supported; the causal pigment mechanism and pollinator preference remain open unless a separate primary experiment is identified.

Files:

- `data/evidence/chang2025_nipponocirsium_accession_audit_2026-08-10.csv`
- `data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv`
- `data/evidence/chang2026_flower_colour_claim_audit_2026-08-10.csv`
- `data/phylogeny/published_topology_fragments_v0_1.csv`
- `docs/CHANG_PHYLOGENY_ARTIFACT_AUDIT_2026-08-10.md`

## Exact Moreyra 2025 sample coverage

The official Elsevier supplement and PRJNA957074 were reconciled reproducibly.

- 299 supplement sample rows;
- 455 public SRA runs;
- 327 submitted scientific names;
- 286 supplement samples linked to runinfo;
- 43 core East Asian samples;
- seven Northeast Asian bridge samples;
- ten exact focal accepted-name matches.

Important corrections:

- *C. pendulum* has an exact Trans-Baikal target-capture tip; its species placement is resolved, but Japanese white/purple history is not.
- *C. sieboldii* has an exact target-capture tip, but it was cultivated in Barcelona and wild provenance is unresolved.
- *C. vlassovianum* has Sikhote-Alin and Mongolian tips; one published tree code is `C. coryletorum`.
- *C. dipsacolepis*, *C. yezoense*, *C. lineare* and the broad *C. nipponicum* complex have modern nuclear evidence requiring varying levels of name/provenance reconciliation.

Files:

- `docs/MOREYRA_2025_EXACT_TIP_AUDIT_2026-08-10.md`
- `docs/MOREYRA_2025_JAPAN_38_MEMBERSHIP_AUDIT.md`
- `data/evidence/moreyra2025_east_ne_asia_sample_audit_2026-08-10.csv`
- `data/evidence/moreyra2025_focal_sample_context_2026-08-10.csv`
- `data/evidence/prjna957074_focal_tip_recovery_2026-08-10.csv`

## Integrated East Asian nuclear coverage

The current master screen evaluates **33 transition-relevant taxa**:

- 21 have species placement resolved in modern nuclear data;
- 12 remain candidate gaps pending synonym and other-dataset audit;
- **no active Tier-A focal taxon is currently a species-placement gap**.

Therefore, the first new genomic wave should emphasize morph/population history rather than rebuild known species placements.

Files:

- `analysis/build_east_asia_nuclear_coverage.py`
- `data/evidence/east_asia_nuclear_coverage_v1_2026-08-10.csv`
- `data/evidence/east_asia_nuclear_coverage_summary_v1_2026-08-10.json`
- `sampling/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv`
- `docs/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.md`

## Moreyra public locus-filter audit

The corresponding author's public repository contains:

- `hybpiper_stats_exonerate.tsv`;
- `seq_lengths_exonerate.tsv`;
- `paralog_report.xlsx`.

It does not contain the final Newick trees, retained alignments, per-locus gene-tree archive or explicit final 350-locus list.

The public summaries expose 1,061 named loci, compared with 1,064 initially mapped loci reported in the paper. Reproducible counts are:

| Stage | Loci |
|---|---:|
| More than 10 paralog-warning samples | 478 |
| One to ten warnings; manual gene-tree review class | 307 |
| No warning | 276 |
| Raw sequence occupancy at least 0.80 | 1,001 |
| Warning count no more than 10 and occupancy at least 0.80 | 531 |
| No-warning and occupancy at least 0.80 | 241 |
| Paper-reported final alignments | 350 |

The 531-locus set is a reproducible **pre-manual candidate screen**. It is not the final published 350. Manual gene-tree decisions and final alignment-level filtering are not encoded in the located public files.

Allowed downstream matrix names:

1. public 1,061-locus universe;
2. reproducible 531-candidate screen;
3. conservative 241 no-warning/high-occupancy set;
4. paralog/homeolog-aware set.

`exact Moreyra 350` remains a reserved, unavailable label.

Files:

- `docs/MOREYRA_2025_AUTHOR_REPOSITORY_LOCUS_AUDIT_2026-08-10.md`
- `data/evidence/moreyra2025_public_locus_filter_summary_2026-08-10.json`
- `data/evidence/moreyra2025_public_locus_filter_counts_2026-08-10.csv`
- `analysis/recover_moreyra_author_repository.py`
- `analysis/summarize_moreyra_locus_filter.py`

## Two-layer phylogenomics design

### Layer 1 — conditional species backbone

Use Compositae1061-compatible target capture only for genuine, transition-critical species gaps.

Generate:

- public-universe matrix;
- reproducible 531-candidate matrix;
- conservative no-warning matrix;
- multi-copy/paralog-aware matrix;
- concatenated and ASTRAL-family trees;
- separate plastid maternal tree;
- reduced-taxon network analyses.

Do not claim an exact Moreyra 350 matrix unless the original retained list or full gene-tree/alignment archive is recovered.

### Layer 2 — focal population history

Use RAD-seq or resequencing for:

1. white versus coloured var. *takaoense*, after morph-linked voucher or new sampling;
2. Japanese and continental *C. pendulum*;
3. Japanese and Zhejiang *C. sieboldii*;
4. *C. kawakamii* versus *C. tatakaense*;
5. *C. brevicaule* versus *C. irumtiense*;
6. verified Korean white forms.

Every focal plant should link voucher, standardized colour, pigment chemistry, floral RNA, leaf DNA and ploidy/cytotype material.

See `docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md`.

## Current focal priority

1. recover or newly obtain morph-linked white/bluish-purple *takaoense* material;
2. sample *C. pendulum* Japanese white/purple populations plus continental bridges;
3. sample *C. sieboldii* Japanese white/purple populations plus Zhejiang;
4. use *C. kawakamii–C. tatakaense* as a matched polyploid loss/mechanism replicate;
5. test population history and repeated mechanism in *C. brevicaule–C. irumtiense*;
6. verify Korean white morphs before species-placement or population sequencing;
7. promote residual China/Korea/Russian-Far-East gaps only when their placement changes a colour-transition inference.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times.
- **H2 — regain/reactivation:** at least one coloured lineage descends from a white ancestor or intermediate.
- **H3 — regulatory reuse:** independent white transitions repeatedly suppress a conserved anthocyanin regulatory network.
- **H4 — molecular parallelism:** independent transitions target homologous regulatory modules even when exact mutations differ.
- **H5 — historical alternatives:** some apparent losses/regains reflect standing variation, introgression or polyploid/reticulate history.

## Reproducibility

Core automated components include:

- literature candidate recovery and curated-registry validation;
- public supplement and NCBI metadata recovery;
- Chang and Moreyra sample/voucher audits;
- Moreyra Japan-38 reconstruction;
- integrated 33-taxon East Asian coverage validation;
- author-repository and locus-filter audit;
- deterministic published-topology colour-history tests.

Publisher/source files are retained in versioned Actions artifacts when licensing and size make repository commits inappropriate. Derived tables, hashes, scripts and decision rules are versioned.

## Work tracked as GitHub issues

- #2 — paired white/coloured field sampling
- #3 — pigment chemistry, floral RNA-seq and causal-region genotyping
- #4 — RAD-seq, ploidy and reticulation tests
- #5 — downstream selection tests
- #6 — complete flower-colour atlas
- #7 — exact published tree files and branch lengths
- #8 — Japan/Korea/Northeast Asia expansion
- #9 — systematic phylogeny, reticulation and cytogenetics evidence map
- #10 — population-history and demographic-model design
- #11 — morph identity of six published *takaoense* vouchers
- #12 — Moreyra final trees, gene trees and exact retained 350 loci

## Next existing-data milestone

1. exhaust public repositories and author-linked resources for the final Moreyra trees and retained-locus decisions;
2. recover and version the Herrando-Moraira tree/data archive;
3. finish accepted-name, synonym and voucher reconciliation;
4. join colour and cytotypes to the topology ensemble;
5. run formal ancestral-state and stochastic-mapping analyses only with documented branch lengths;
6. freeze the first population and conditional target-capture panels from information gain rather than raw taxon count.

No large WGS cohort should be finalized before the morph/population-history screen is complete.
