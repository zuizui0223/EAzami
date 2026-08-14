# Japanese *Cirsium* origin meta-analysis — 2026-08-14

## Question

Do native Japanese *Cirsium* represent one biogeographic origin, or multiple colonization histories?

This document distinguishes **phylogenetic monophyly** from **biogeographic origin**. The primary claim concerns the number of colonization/range-expansion histories that produced the Japanese flora, not whether every Japanese taxon can be forced into a single taxonomic clade.

## Reproducible synthesis

Evidence matrix:

- `data/evidence/japan_cirsium_origin_evidence_matrix_v1.csv`
- `data/evidence/japan_cirsium_origin_priority_public_sequences_v1.csv`
- frozen result: `data/evidence/japan_cirsium_origin_meta_analysis_v1.json`

Summarizer:

- `analysis/summarize_japan_cirsium_origin_meta_analysis.py`

Validation workflow:

- `.github/workflows/validate-japan-cirsium-origin-meta-analysis.yml`

Successful run:

- GitHub Actions run `31803848478`
- result artifact `9220333175`
- artifact SHA256 `0f4152a32547330df04fa4d6fa7ff9598dbcc6e97e72102e19190e0b25c882ba`

The synthesis deliberately does not calculate a classical pooled effect size. These studies estimate trees and range histories rather than a common scalar effect, and the Chang 2025/2026 analyses partially belong to one transcriptome data-generation programme. We therefore aggregate both **analysis-level replication** and **independent data-generation groups**, while keeping direct ancestral-range reconstruction separate from phylogenetic compatibility.

## High-dimensional nuclear evidence

### Moreyra et al. 2025 — broad target capture

Primary source: Moreyra et al., *Molecular Phylogenetics and Evolution* 204:108285. DOI `10.1016/j.ympev.2025.108285`.

Public reads: BioProject `PRJNA957074`.

Key design:

- 266 *Cirsium* samples representing 248 species;
- 350 retained nuclear loci after orthology filtering;
- concatenated and coalescent phylogenies;
- probabilistic ancestral-range reconstruction and biogeographic stochastic mapping.

Japanese result:

- 38 Japanese species sampled, 30 endemic;
- **36/38 = 94.74%** form one Japanese clade;
- this dominant clade is inferred from one Middle-Asia-to-Japan jump at ~2.4 Ma (95% CI 1.7–3.6 Ma), followed by rapid radiation;
- *C. dipsacolepis* is inferred from a separate Japanese jump at ~1.0 Ma (0.4–2.2 Ma);
- *C. lineare* is inferred from an East-Asia-to-Japan range expansion at ~1.4 Ma (0.7–2.7 Ma).

This is currently the **only broad, direct nuclear biogeographic reconstruction** with extensive Japanese sampling. It directly rejects a strict one-colonization model, but its two exceptional event assignments still require lineage-specific replication.

The frozen Moreyra reconciliation now gives the exact public nuclear runs for the two critical exceptions:

- *C. dipsacolepis*: `SAMN44017836 / SRX26291339 / SRR30887259`, Japan, Shikoku, Tokushima Pref., Mt. Shiozuka-mine;
- *C. lineare*: `SAMN44017876 / SRX26291359 / SRR30887240`, Japan, voucher Miyoshi Furuse 52881 (`PE01293160`).

These are therefore direct falsification targets in the current 294→296 public nuclear analysis rather than merely literature-listed taxa.

### Chang et al. 2025 — Nipponocirsium phylotranscriptomics

Primary source: Chang et al., *Botanical Studies*. DOI `10.1186/s40529-025-00454-2`.

Public reads: BioProject `PRJNA1158676`.

The study sampled three Japanese Nipponocirsium taxa plus Taiwanese taxa and two *C. lineare* individuals. Transcriptome orthogroups were analyzed by individual gene trees, ASTRAL, concatenation and Bayesian dating.

Result relevant to Japanese origin:

- *C. lineare* forms the basal/distant *Cirsium* subclade relative to subsect. Nipponocirsium;
- Japanese Nipponocirsium taxa form a coherent Japanese clade;
- *C. lineare*–Nipponocirsium divergence is estimated at ~2.27 Ma (95% CI 1.85–2.69 Ma).

This does **not** independently reconstruct a Japanese colonization event, but it independently supports the phylogenetic exceptional status of *C. lineare*.

### Chang et al. 2026 — Sinocirsium/Arenicola/Nipponocirsium phylotranscriptomics

Primary source: Chang et al., *BMC Plant Biology*. DOI `10.1186/s12870-026-08097-6`.

Public reads: BioProject `PRJNA1311153`.

Key analyses include an ASTRAL species tree from 2,999 OGs, a Neighbor-Net based on 2,599 single-copy OGs, and a time-calibrated analysis of 50 OGs.

Relevant topology:

- Arenicola + Nipponocirsium form a clade with PP=1;
- this clade is sister to Sinocirsium;
- all three subsections are monophyletic;
- *C. lineare* is used as a distant/basal intrageneric outgroup;
- Sinocirsium vs. (Arenicola + Nipponocirsium) split ~1.30 Ma;
- Arenicola vs. Nipponocirsium split ~1.02 Ma;
- *C. brevicaule* vs. *C. irumtiense* split ~0.93 Ma.

Therefore current high-dimensional evidence does **not** justify counting Arenicola as a fourth independent Japanese colonization. Its phylogenetic position is compatible with ancestry shared with the derived East-Asian/Japanese lineages; a broad range reconstruction is still needed.

## Lower-weight / orthogonal evidence

### Chloroplast structure in Japanese *Cirsium*

The completed Japanese KAKEN project on phylogenetic analysis and taxonomic review reported that chloroplast-genome relationships do not match the traditional section/subsection classification and broadly separate Japanese material into Hokkaido and south-of-Honshu maternal lineages.

This is useful evidence for maternal-history heterogeneity, chloroplast capture, historical subdivision, or hybridization. It is **not counted as an independent colonization event**, because organellar lineage boundaries need not equal nuclear species-history boundaries.

### Legacy *C. lineare* nuclear markers

Public nrDNA accessions:

- ITS `AF443727`
- ETS `AF443779`

These provide a pre-phylogenomic public sequence anchor for *C. lineare*. They are not counted as an independent Japanese-origin test because sparse-marker trees do not provide the same range/orthology resolution as the current nuclear genomic datasets.

### Public plastomes useful for discordance tests

- *C. nipponicum* chloroplast: `MW248139`;
- *C. japonicum* chloroplast resources include `MW035606` / `NC_053767` and `MH778960`;
- additional comparative *Cirsium* plastomes include *C. rhinoceros* `NC_044423`, *C. japonicum* var. spinosissimum `NC_050046`, *C. arvense* `NC_036965`, and *C. vulgare* `NC_036967`.

The Ulleung *C. nipponicum* plastome groups with *C. arvense*/*C. vulgare* rather than Korean *C. japonicum*/*C. rhinoceros*. This is retained as a nuclear–plastid discordance hypothesis, not as evidence for an additional Japanese colonization.

## Meta-analysis result

The reproducible synthesis returned:

- evidence units: **6**;
- high-dimensional nuclear analyses: **3**;
- independent high-dimensional nuclear data-generation groups: **2**;
- broad direct nuclear biogeographic analyses: **1**;
- dominant main radiation: **36/38 = 94.74%** of the sampled Japanese species;
- focused high-dimensional nuclear analyses compatible with a coherent derived Japanese/East-Asian structure: **2**;
- *C. lineare* exceptional placement: **3/3 analyses**, **2/2 independent nuclear data-generation groups**;
- *C. dipsacolepis* separate-arrival support: **1/1 relevant high-dimensional analysis**, but only one data-generation group;
- Arenicola as an additional colonization: **0/1** relevant high-dimensional analysis; current topology instead links it to Nipponocirsium.

### Model comparison

1. **Strict single origin of all Japanese *Cirsium*** — **rejected**.
2. **One dominant Pleistocene radiation plus rare secondary/independent entries** — **best supported**.
3. **Many independent colonizations with no dominant radiation** — **not supported**.

## Established working hypothesis

> **Japanese *Cirsium* has an oligophyletic colonization history rather than either a strict single origin or many equivalent independent invasions. One dominant Middle-Asian-derived Pleistocene founder lineage generated the overwhelming majority of sampled Japanese diversity through rapid in situ radiation. *C. lineare* represents a strongly replicated phylogenetic exception with a separately reconstructed East-Asian range-expansion history, while *C. dipsacolepis* is the best current candidate for a second secondary arrival but still lacks independent high-dimensional replication. Arenicola is not currently justified as an additional colonization.**

### Origin-count hierarchy

**Minimum defensible number of histories: 2**

1. dominant main Japanese radiation;
2. *C. lineare* lineage.

**Best current point hypothesis: 3**

1. dominant main Japanese radiation (~2.4 Ma);
2. *C. lineare* East-Asian lineage / Japanese range expansion (~1.4 Ma);
3. *C. dipsacolepis* secondary Japanese founder (~1.0 Ma).

**Four or more:** unresolved and currently unsupported by high-dimensional evidence.

## Why this is stronger than saying “Japan is polyphyletic”

The biologically informative pattern is extremely asymmetric. Roughly 95% of the sampled Japanese species belong to one radiation, while a few lineages violate strict single origin. The hypothesis is therefore not “many unrelated Japanese thistles”; it is **one dominant radiation with rare exceptions**.

That distinction predicts different processes:

- the main radiation should show rapid lineage accumulation, short internodes, incomplete lineage sorting, ecological differentiation and possible reticulation within Japan;
- exceptional lineages should retain closer nuclear affinity to different continental branches and have entry times distinct from the ~2.4 Ma radiation;
- plastid histories may disagree with the nuclear tree because hybridization and chloroplast capture are expected in *Cirsium*.

## Falsification tests for the current 294→296 public nuclear analysis

The current maximum-public tree should explicitly test:

1. whether the broad Japanese main radiation remains one coherent clade after the larger continental context is added;
2. whether *C. lineare* (`SRR30887240`) remains outside that radiation under both BWA and BLASTx and under concatenation and ASTRAL;
3. whether *C. dipsacolepis* (`SRR30887259`) remains outside the main radiation and which continental branch is its nearest nuclear neighbour;
4. whether Arenicola falls within/sister to the main Japanese radiation or instead becomes an independently bracketed continental-derived lineage;
5. whether Hokkaido-vs-southern chloroplast structure has a corresponding nuclear split or instead represents organellar capture/history;
6. whether the inferred exception count changes under a network/discordance view rather than a forced strictly bifurcating tree.

## Highest-value additional public/sample targets

1. **Replicate *C. dipsacolepis*** with an independent nuclear dataset or additional biological sample. This is the weakest link in the current three-history hypothesis. Its existing Moreyra target-capture run is `SRR30887259`.
2. **Geographic *C. lineare* replication** spanning Japan and continental East Asia. Its Japanese Moreyra run is `SRR30887240`, while the Chang transcriptome programme supplies independent phylogenetic replication; exact geographical replication should be the next provenance target.
3. **Arenicola + closest Nipponocirsium/continental relatives** to decide whether the Ryukyu lineage belongs to the dominant radiation's ancestry or represents another entry.
4. **Hokkaido boundary taxa** only after the nuclear tree identifies which chloroplast north–south split corresponds to a real nuclear branch.

Broad mainland-China sampling should still not be frozen by geography alone. New samples should target the continental branch that brackets each unresolved Japanese exception.

## Claim boundary

The direct number of historical dispersal events is not independently estimated by three separate studies. Only Moreyra 2025 currently performs the broad range reconstruction. The strength of the meta-analysis comes from independent replication of the **phylogenetic exception structure**, especially for *C. lineare*, plus explicit protection against double-counting partially shared transcriptome data.
