# EAzami — East Asian *Cirsium* flower-colour evolution

Chapter 2 project for reconstructing repeated loss and possible re-expression of floral anthocyanin pigmentation in East Asian *Cirsium*, while building the nuclear phylogenetic, population-genomic and molecular framework needed to test those transitions.

For the active decision gate, acceptance criteria and canonical workstream map, start with [`PROJECT_STATUS.md`](PROJECT_STATUS.md).

## Core question

> How repeatedly has floral anthocyanin pigmentation been lost and regained in East Asian *Cirsium*, and do repeated transitions use the same molecular mechanisms?

The project starts with Japan, the Ryukyu Islands, Taiwan and China and expands through Korea, Sakhalin, Mongolia and the Russian Far East only when those populations change a flower-colour history.

## Current biological inference

Existing nuclear phylogenies and source-backed flower-colour states support **repeated white-flower evolution** as the general pattern. Taiwanese var. *takaoense* is now a stronger and more precisely defined exception candidate:

- Taiwanese Nipponocirsium supports an independent white loss in *C. kawakamii*.
- The published Arenicola sister context favours white loss in *C. brevicaule*, not regain in *C. irumtiense*.
- All six published var. *takaoense* transcriptomes are now linked exactly to vouchers, SRA runs and BioSamples.
- The official Chang et al. 2026 Figure 1 directly labels three samples as bluish-purple—FC-3559, TJ-3807 and NH-3835—and three as white—WY-3560, FB-3629 and LT-3839.
- Figure 1 panel C displays the six-sample topology as `(((((NH_BP,TJ_BP),FC_BP),LT_W),FB_W),WY_W)`; panel B independently shows the same morph grouping in the Neighbor-Net.
- With the exact sample topology embedded in a coloured-root Sinocirsium context, the unique minimum-change history contains one white loss and one W-to-coloured transition. A no-regain history requires two additional changes.
- In the full focal East Asian topology, the minimum is three losses plus one regain; the best no-regain history again costs two extra changes.

The appropriate claim is therefore:

> **var. takaoense is a topology-supported candidate regain: a W-to-coloured transition is required by minimum-change reconstruction under the displayed exact sample topology and coloured-root model.**

This is not yet proof that an anthocyanin pathway was functionally lost and molecularly restored. Introgression, retention of ancestral coloured variation, geographic structure, weak short internodes and reticulation remain viable historical explanations.

A demonstrated regain still requires:

1. stable population-aware nuclear history across tree and network methods;
2. explicit tests of introgression and ancestral standing variation;
3. evidence that a white lineage retained or lost a recoverable anthocyanin pathway;
4. a derived functional or regulatory change linked to genotype, floral expression, pigment and phenotype in the same plants.

Key result files:

- `docs/CHANG2026_TAKAOENSE_MORPH_EVIDENCE_AUDIT_2026-08-11.md`
- `docs/CHANG2026_TAKAOENSE_SAMPLE_COLOUR_HISTORY_2026-08-11.md`
- `data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv`
- `analysis/chang2026_takaoense_sample_colour_history.csv`
- `data/evidence/chang2026_takaoense_sample_colour_history_summary_2026-08-11.json`

## Linked objectives

1. **Flower-colour atlas:** retain population/morph-level states instead of collapsing every taxon to one species mean.
2. **Evolutionary history:** distinguish independent loss, ancestral polymorphism, introgression and candidate regain across a topology ensemble.
3. **East Asian species backbone:** reuse existing nuclear phylogenomics and fill only genuine transition-critical gaps.
4. **Population history:** resolve white/coloured ancestry and geographic bridges with RAD-seq or resequencing.
5. **Molecular mechanism:** combine pigment chemistry, floral RNA-seq and causal-region genomics.
6. **Selection:** test pollinator and abiotic fitness effects only after history and mechanism are sufficiently resolved.
7. **Reusable trait foundation:** carry stable taxon, population, voucher and tree-tip identifiers into future capitulum-trait mapping without assuming adaptive radiation in advance.

## State of *Cirsium* phylogeny

The accurate summary is neither “the phylogeny is solved” nor “almost nothing is known.”

### Strongly developed

- deep Asteraceae/Cardueae/Carduinae nuclear backbones from target capture and Hyb-Seq;
- a broad, incomplete global species-level *Cirsium* nuclear tree;
- modern regional frameworks for North America, Japan and focal Taiwan/Ryukyu clades;
- empirical evidence for hybridization, incomplete lineage sorting, allopolyploidy, cytomixis and cytonuclear discordance;
- public reads, sample tables, target-recovery summaries, genomes, transcriptomes and plastomes.

### Still incomplete

- broad *Cirsium* versus *Lophiolepis* and other generic circumscriptions;
- complete machine-readable final trees and branch lengths for key studies;
- the exact final 350-locus Moreyra matrix;
- one densely sampled, compatible nuclear framework across all East Asian regions;
- population ancestry, local introgression and cytotype/homeolog history within focal colour systems;
- molecular evidence for true anthocyanin loss and restoration.

Plastid evidence is retained as a separate maternal-history layer, not substituted for a nuclear species tree.

## Systematic evidence map

Release v0.3 validates **54 manually curated phylogeny/systematics studies or public resources** spanning 1999–2026.

| Tier | Records | Role |
|---|---:|---|
| A | 13 | phylogenomics, phylotranscriptomics, target capture, decisive genome-wide reticulation evidence and reusable tree/read resources |
| B | 14 | multilocus frameworks, species delimitation, historical biogeography and reusable nuclear/genomic references |
| C | 18 | cytogenetics, population hybridization, morphology and lower-locus evidence constraining alternative histories |
| D | 9 | organelle-only, type-based and nomenclatural evidence used for maternal history and name reconciliation |

A separate seven-study population-history registry covers range-edge structure, fragmentation, invasion/admixture, expression divergence, landscape genetics and recurrent hybridization. Automated Crossref/Europe PMC results remain unreviewed candidates and never enter the curated registry without manual primary-source screening.

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
- six var. *takaoense* public transcriptomes linked one-to-one to collector vouchers, runs and BioSamples;
- direct W/BP labels recovered from the official Figure 1 image;
- no machine-readable Newick in the supplement.

The six var. *takaoense* accessions are:

| Code | Voucher | Run | BioSample | Morph |
|---|---|---|---|---|
| FC | `ccy3559` | `SRR35152718` | `SAMN50798021` | BP |
| WY | `ccy3560` | `SRR35152717` | `SAMN50798022` | W |
| FB | `ccy3629` | `SRR35152738` | `SAMN50798024` | W |
| TJ | `ccy3807` | `SRR35152736` | `SAMN50798026` | BP |
| NH | `ccy3835` | `SRR35152735` | `SAMN50798027` | BP |
| LT | `ccy3839` | `SRR35152734` | `SAMN50798028` | W |

NCBI metadata preserve collector numbers but contain no colour, corolla, phenotype, morph, pigment or anthocyanin attribute. The phenotype evidence comes directly from Figure 1 panels B and C.

The official Figure 1 PNG is frozen by provenance:

- dimensions: `1945 × 2400`;
- SHA256: `10375f1d79a4799babdebffca84301f602adfa0aabc825b852de84177bbb878c`;
- Actions run: `31429139819`;
- artifact: `9078372622`.

A source conflict remains for collector `ccy3839`: Supplementary Table S1 lists TCF, whereas Table S6 lists TNM.

The accessible article and official supplement do not contain located methods/results supporting a completed anthocyanin-expression or pollinator-preference experiment. Same-variety colour polymorphism and reticulation alternatives are supported; causal pigment regulation and pollinator preference remain open unless a separate primary experiment is identified.

Files:

- `data/evidence/chang2025_nipponocirsium_accession_audit_2026-08-10.csv`
- `data/evidence/chang2026_east_asia_accession_audit_2026-08-10.csv`
- `data/evidence/chang2026_flower_colour_claim_audit_2026-08-10.csv`
- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv`
- `data/phylogeny/published_topology_fragments_v0_1.csv`
- `docs/CHANG_PHYLOGENY_ARTIFACT_AUDIT_2026-08-10.md`

## Exact sample-topology colour-history analysis

The old generic sensitivity represented one W and one coloured var. *takaoense* tip as an unresolved sister pair. Under a coloured root it allowed equal-parsimony histories:

- four losses and no regain;
- three losses and one regain.

The exact Figure 1 sample topology changes that result.

| Scope | Fixed root | Minimum history | No-regain minimum | Penalty |
|---|---|---|---:|---:|
| six var. *takaoense* samples | W | 0 losses + 1 regain | impossible | — |
| six var. *takaoense* samples | C | 3 losses, or 2 losses + 1 regain | 3 | 0 |
| white var. *albescens* + exact var. *takaoense* | C | 2 losses + 1 regain | 4 | +1 |
| sample-aware Sinocirsium | C | 1 loss + 1 regain | 4 | +2 |
| full focal East Asian topology | C | 3 losses + 1 regain | 6 | +2 |

This is a topology-only diagnostic with no invented branch lengths. Formal Mk and stochastic mapping require exact machine-readable trees and branch lengths.

## Published-sample metadata screen

The six morph-labelled samples are also strongly altitude stratified:

- BP mean altitude: `1160.67 m`;
- W mean altitude: `357.00 m`;
- difference: `803.67 m`;
- complete rank separation;
- exact one-sided allocation probability: `0.05`;
- exact two-sided probability: `0.10`.

This does not establish altitude-dependent selection. There is one plant per non-random locality, and morph, altitude, geography and ancestry are confounded. It does determine the design requirement for future sampling: mixed populations or geographically matched W/BP populations are substantially more informative than adding more unbalanced high-versus-low localities.

Files:

- `analysis/takaoense_published_morph_metadata_screen.py`
- `analysis/takaoense_published_morph_metadata_screen_summary.json`
- `analysis/takaoense_published_morph_altitude_screen.csv`

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

- *C. pendulum* has an exact Trans-Baikal target-capture tip; species placement is resolved, but Japanese W/purple history is not.
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

The current master screen evaluates 33 transition-relevant taxa:

- 21 have species placement resolved in modern nuclear data;
- 12 remain candidate gaps pending synonym and other-dataset audit;
- no active Tier-A focal taxon is currently a species-placement gap.

The first new genomic wave should therefore emphasize morph/population history rather than rebuild known species placements.

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

The public summaries expose 1,061 named loci, compared with 1,064 initially mapped loci reported in the paper.

| Stage | Loci |
|---|---:|
| More than 10 paralog-warning samples | 478 |
| One to ten warnings; manual gene-tree review class | 307 |
| No warning | 276 |
| Raw sequence occupancy at least 0.80 | 1,001 |
| Warning count no more than 10 and occupancy at least 0.80 | 531 |
| No-warning and occupancy at least 0.80 | 241 |
| Paper-reported final alignments | 350 |

The 531-locus set is a reproducible pre-manual candidate screen. It is not the final published 350. Manual gene-tree decisions and final alignment-level filtering are not encoded in the located public files.

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

1. var. *takaoense*: reuse the six morph-labelled transcriptomes as anchors and densely sample geographically matched or mixed W/BP populations;
2. Japanese and continental *C. pendulum*;
3. Japanese and Zhejiang *C. sieboldii*;
4. *C. kawakamii* versus *C. tatakaense*;
5. *C. brevicaule* versus *C. irumtiense*;
6. verified Korean white forms.

Every focal plant should link voucher, standardized colour, pigment chemistry, floral RNA, leaf DNA and ploidy/cytotype material.

See `docs/EAST_ASIA_CIRSIUM_PHYLOGENOMICS_IMPLEMENTATION_PLAN.md`.

## Current focal priority

1. reanalyse the six public var. *takaoense* transcriptomes with exact W/BP labels, gene-tree concordance and network/local-ancestry sensitivities;
2. collect mixed or geographically matched var. *takaoense* populations with linked DNA/RNA/pigment/ploidy data;
3. sample *C. pendulum* Japanese W/purple populations plus continental bridges;
4. sample *C. sieboldii* Japanese W/purple populations plus Zhejiang;
5. use *C. kawakamii–C. tatakaense* as a matched polyploid loss/mechanism replicate;
6. test population history and repeated mechanism in *C. brevicaule–C. irumtiense*;
7. verify Korean white morphs before species-placement or population sequencing;
8. promote residual China/Korea/Russian-Far-East gaps only when placement changes a transition inference.

## Primary hypotheses

- **H1 — repeated loss:** floral anthocyanin loss evolved independently multiple times.
- **H2 — regain/reactivation:** at least one coloured lineage descends from a white ancestor or intermediate; exact var. *takaoense* topology now supports this as the minimum-change hypothesis under a coloured-root Sinocirsium model.
- **H3 — regulatory reuse:** independent white transitions repeatedly suppress a conserved anthocyanin regulatory network.
- **H4 — molecular parallelism:** independent transitions target homologous regulatory modules even when exact mutations differ.
- **H5 — historical alternatives:** some apparent losses/regains reflect standing variation, introgression or polyploid/reticulate history.

## Reproducibility

Core automated components include:

- literature candidate recovery and curated-registry validation;
- public supplement and NCBI metadata recovery;
- Chang and Moreyra sample/voucher audits;
- direct Figure 1 phenotype and topology validation;
- var. *takaoense* published-sample metadata/permutation screening;
- exact sample-topology directional-history reconstruction;
- Moreyra Japan-38 reconstruction;
- integrated 33-taxon East Asian coverage validation;
- author-repository and locus-filter audit;
- generic and exact-topology colour-history sensitivity tests.

Publisher/source files are retained in versioned Actions artifacts when licensing and size make repository commits inappropriate. Derived tables, hashes, scripts and decision rules are versioned.

## Work tracked as GitHub issues

- #2 — paired W/coloured field sampling
- #3 — pigment chemistry, floral RNA-seq and causal-region genotyping
- #4 — RAD-seq, ploidy and reticulation tests
- #5 — downstream selection tests
- #6 — complete flower-colour atlas
- #7 — exact published tree files and branch lengths
- #8 — Japan/Korea/Northeast Asia expansion
- #9 — systematic phylogeny, reticulation and cytogenetics evidence map
- #10 — population-history and demographic-model design
- #11 — six published var. *takaoense* morph identities — **completed**
- #12 — Moreyra/Chang final trees, gene trees and exact retained-locus artifacts

## Next resolution milestone

Accept or reject a stable topology class for the main Japanese radiation using the deduplicated 294-individual / 295-SRR common-locus public nuclear panel. BWA-primary versus BLASTx mapping sensitivity and concatenated versus ASTRAL/coalescent sensitivity must be compared before a final continental sampling panel is frozen. The exact gate and allowed conclusions are defined in [`PROJECT_STATUS.md`](PROJECT_STATUS.md), [`docs/JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md`](docs/JAPAN_ORIGIN_TOPOLOGY_DECISION_CONTRACT_2026-08-13.md) and [`docs/JAPAN_ORIGIN_SENSITIVITY_ACCEPTANCE_GATE_2026-08-13.md`](docs/JAPAN_ORIGIN_SENSITIVITY_ACCEPTANCE_GATE_2026-08-13.md).

No large WGS cohort should be finalized before the morph/population-history and ploidy sampling design is complete.
