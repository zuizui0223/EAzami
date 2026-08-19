# Japanese *Cirsium* origin meta-analysis — 2026-08-14

## Question

Do native Japanese *Cirsium* represent one biogeographic origin, or multiple colonization histories?

This document distinguishes **phylogenetic monophyly** from **biogeographic origin**. The primary claim concerns the number of colonization/range-expansion histories that produced the Japanese flora, not whether every Japanese taxon can be forced into a single taxonomic clade.

## Reproducible synthesis

Evidence and accession ledgers:

- `data/evidence/japan_cirsium_origin_evidence_matrix_v1.csv`
- `data/evidence/japan_cirsium_origin_priority_public_sequences_v1.csv`
- frozen meta-analysis result: `data/evidence/japan_cirsium_origin_meta_analysis_v1.json`
- frozen accession-level falsification panel: `data/evidence/japan_cirsium_origin_falsification_panel_v2.json`

Analysis code:

- `analysis/summarize_japan_cirsium_origin_meta_analysis.py`
- `analysis/build_japan_cirsium_origin_falsification_panel.py`

Validation workflows:

- `.github/workflows/validate-japan-cirsium-origin-meta-analysis.yml`
- `.github/workflows/validate-japan-cirsium-origin-falsification-panel.yml`

Validated runs:

- meta-analysis run `31803848478`; artifact `9220333175`; SHA256 `0f4152a32547330df04fa4d6fa7ff9598dbcc6e97e72102e19190e0b25c882ba`
- accession-level falsification run `31806752296`; artifact `9221472767`; SHA256 `705094d675a883918e47d38f686fe0f544eb96ebf2515fb8e2dd32c1e4d967f7`

The synthesis deliberately does not calculate a classical pooled effect size. These studies estimate trees and range histories rather than a common scalar effect, and the Chang 2025/2026 analyses partly belong to one transcriptome data-generation programme. We therefore aggregate both **analysis-level replication** and **independent data-generation groups**, while keeping direct ancestral-range reconstruction separate from phylogenetic compatibility.

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

This remains the **only broad, direct nuclear biogeographic reconstruction** with extensive Japanese sampling. It directly rejects a strict one-colonization model, but its two exceptional event assignments still require lineage-specific replication.

The frozen Moreyra reconciliation gives exact public nuclear runs for both critical exceptions:

- *C. dipsacolepis*: `SAMN44017836 / SRX26291339 / SRR30887259`, Japan, Shikoku, Tokushima Pref., Mt. Shiozuka-mine;
- *C. lineare*: `SAMN44017876 / SRX26291359 / SRR30887240`, Japan, voucher Miyoshi Furuse 52881 (`PE01293160`).

These are direct falsification targets in the current 294→296 public nuclear analysis rather than merely literature-listed taxa.

### Chang et al. 2025 — Nipponocirsium phylotranscriptomics

Primary source: Chang et al., *Botanical Studies*. DOI `10.1186/s40529-025-00454-2`.

Public reads: BioProject `PRJNA1158676`.

The study sampled three Japanese Nipponocirsium taxa plus Taiwanese taxa and two *C. lineare* individuals. Transcriptome orthogroups were analysed by individual gene trees, ASTRAL, concatenation and Bayesian dating.

Result relevant to Japanese origin:

- *C. lineare* forms the basal/distant *Cirsium* subclade relative to subsect. Nipponocirsium;
- Japanese Nipponocirsium taxa form a coherent Japanese clade;
- *C. lineare*–Nipponocirsium divergence is estimated at ~2.27 Ma (95% CI 1.85–2.69 Ma).

The two *C. lineare* public RNA-seq samples are now accession-frozen:

- `SAMN43544261 / SRX26039659 / SRR30617342`, voucher `ccy3446`, Taiwan: Miaoli County, Xihu;
- `SAMN43544259 / SRX26039654 / SRR30617347`, voucher `ccy2770`, Taiwan: Miaoli County, Tongxiao.

Together with the Japanese Moreyra target-capture tip, these provide **Japan + Taiwan high-dimensional geographic replication**. They still count as only two independent high-dimensional data-generation groups: the Moreyra target-capture programme and the Chang transcriptome programme.

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

The exact public Arenicola panel is now fixed as three *C. brevicaule* runs (`SRR35152730`, `SRR35152729`, `SRR35152725`) and three *C. irumtiense* runs (`SRR35152732`, `SRR35152731`, `SRR35152724`). Two Japanese *C. japonicum* var. *japonicum* bridge samples (`SRR35152727`, `SRR35152726`) are retained to test whether Japanese Sinocirsium shares the dominant Japanese radiation ancestry or a separate East-Asian bridge history.

## Lower-weight / orthogonal evidence

### Chloroplast structure in Japanese *Cirsium*

The completed Japanese KAKEN project on phylogenetic analysis and taxonomic review reported that chloroplast-genome relationships do not match the traditional section/subsection classification and broadly separate Japanese material into Hokkaido and south-of-Honshu maternal lineages.

This is useful evidence for maternal-history heterogeneity, chloroplast capture, historical subdivision, or hybridization. It is **not counted as an independent colonization event**, because organellar lineage boundaries need not equal nuclear species-history boundaries.

### Legacy *C. lineare* nuclear markers

Kelch & Baldwin's nrDNA dataset provides a continental Chinese anchor from Hubei (voucher UC 1490729):

- ITS `AF443727`
- ETS `AF443779`

Thus the current *C. lineare* evidence spans **Japan, Taiwan and mainland China**. The Hubei ITS/ETS sequences are low-dimensional geographic/concordance anchors only; they are not counted as a third independent high-dimensional origin test and cannot override target-capture or transcriptome topology.

### Public plastomes useful for discordance tests

- *C. nipponicum* chloroplast: `MW248139`;
- *C. japonicum* chloroplast resources include `MW035606` / `NC_053767` and `MH778960`;
- additional comparative *Cirsium* plastomes include *C. rhinoceros* `NC_044423`, *C. japonicum* var. spinosissimum `NC_050046`, *C. arvense* `NC_036965`, and *C. vulgare* `NC_036967`.

The Ulleung *C. nipponicum* plastome groups differently from some East-Asian *Cirsium* comparisons. This is retained as a nuclear–plastid discordance hypothesis, not as evidence for an additional Japanese colonization.

## Targeted re-search of the weakest exception: *C. dipsacolepis*

A renewed exact-name search on 2026-08-14 covered NCBI-indexed nucleotide/SRA/BioSample routes and molecular-phylogeny literature queries for `Cirsium dipsacolepis`, ITS, ETS, sequence, transcriptome and phylogeny. The search recovered the Moreyra target-capture record and taxonomic/chemical literature but **did not surface a second independent high-dimensional nuclear dataset or an independent phylogenetic nuclear marker record for this species**.

This is an absence-of-evidence audit, not proof that no unpublished or poorly indexed sequence exists. It strengthens the decision to keep the third-origin claim one level below the *C. lineare* exception until either:

1. another biological *C. dipsacolepis* sample is sequenced/recovered; or
2. the existing `SRR30887259` placement is independently bracketed by a sufficiently dense continental nuclear panel and remains stable across mapping/tree sensitivities.

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

> **Japanese *Cirsium* has an oligophyletic colonization history rather than either a strict single origin or many equivalent independent invasions. One dominant Middle-Asian-derived Pleistocene founder lineage generated the overwhelming majority of sampled Japanese diversity through rapid in situ radiation. *C. lineare* represents a strongly replicated phylogenetic exception with Japan–Taiwan high-dimensional replication and a mainland-China nrDNA anchor, while *C. dipsacolepis* is the best current candidate for a second secondary arrival but still lacks independent high-dimensional replication. Arenicola is not currently justified as an additional colonization.**

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

## Accession-level falsification contract for the current 294→296 analysis

The validated panel contains **12 unique critical SRA runs** plus the two Hubei nrDNA anchors. The current maximum-public tree must test the following before origin-count claims are promoted:

1. **Dominant radiation:** the broad Japanese main radiation must remain coherent after larger continental context is added.
2. ***C. lineare*:** Japanese `SRR30887240` must remain outside the dominant radiation under both BWA and BLASTx and under concatenation and ASTRAL; Taiwan `SRR30617342` and `SRR30617347` must remain in the same broad *lineare* lineage rather than falling within Nipponocirsium.
3. ***C. dipsacolepis*:** `SRR30887259` must remain outside the main radiation and acquire a stable continental nearest-neighbour bracket before the third history is promoted beyond working-hypothesis status.
4. **Arenicola:** the six Ryukyu transcriptomes must not be counted as a fourth colonization unless Arenicola becomes independently continental-bracketed outside the dominant Japanese radiation under broad nuclear tree/network sensitivity.
5. **Sinocirsium bridge:** Japanese `SRR35152727` and `SRR35152726` must be used to distinguish a main-radiation affinity from a separate Taiwan/East-Asian bridge.
6. **Organelle discordance:** Hokkaido/southern chloroplast structure and public plastomes remain discordance diagnostics, never stand-alone colonization counters.

Predeclared decision rule:

- retain *C. lineare* exception → **minimum two histories supported**;
- retain *C. lineare* + stable independent *C. dipsacolepis* placement → **three-history model promoted**;
- promote four or more histories only if another Japanese lineage, such as Arenicola, is independently bracketed by a distinct continental source lineage.

No locus or topology threshold may be relaxed after seeing the result.

## Highest-value additional samples after the public tree

1. **Independent *C. dipsacolepis* biological replicate** — highest value because it directly tests the weakest link in the three-history model.
2. **Mainland-East-Asian *C. lineare* genomic replicate** — the lineage already has Japan/Taiwan high-dimensional data and Hubei nrDNA; a comparable mainland genomic sample would turn geographic concordance into a direct high-dimensional test.
3. **Continental sister taxa selected from the actual nuclear bracket** around *dipsacolepis*, *lineare* and Arenicola — not a broad China list chosen in advance.
4. **Hokkaido boundary taxa** only if the nuclear tree indicates that the chloroplast north–south split corresponds to a real nuclear-history discontinuity.

Broad mainland-China sampling therefore remains deliberately unfrozen until the current public nuclear tree identifies the specific continental source branches.

## Claim boundary

The direct number of historical dispersal events is not independently estimated by three separate studies. Only Moreyra 2025 currently performs the broad range reconstruction. The strength of the meta-analysis comes from independent replication of the **phylogenetic exception structure**, especially for *C. lineare*, plus explicit protection against double-counting partially shared transcriptome data. The three-history state remains a working point hypothesis until *C. dipsacolepis* gains independent high-dimensional replication or an equivalently strong stable continental bracket.
