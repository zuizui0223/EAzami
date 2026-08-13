# Moreyra et al. 2025 exact tip, name and geographic audit

Date: 2026-08-10

## Scope

This audit reconciles three evidence layers that must not be conflated:

1. Supplementary Table S1 tree codes, published taxon names, BioSamples and vouchers;
2. official PRJNA957074 SRA/BioSample metadata;
3. the Chapter 2 focal taxon list and its flower-colour hypotheses.

The source supplement is the verified 10,761,775-byte Elsevier DOCX with SHA256:

`34d15286b4ba0952932c55df3a03a286a0d3dc5fb26ead204e6a1ea16a35f4f1`

Publisher files are retained only in versioned GitHub Actions artifacts. Reconciled evidence tables and provenance are versioned in the repository.

## Recovery totals

The reproducible workflow recovered:

- **299 Supplementary Table S1 sample rows**;
- **263 Cirsium rows** in the supplement;
- **455 public PRJNA957074 runs**;
- **327 submitted scientific names** in runinfo;
- **286 supplement samples linked to public runinfo**;
- **13 supplement samples without a recovered public run**;
- **43 core East Asian supplement samples**;
- **7 Northeast Asian bridge samples**;
- **10 exact focal accepted-name matches** after supplement/runinfo reconciliation.

The run-level East/Northeast Asian table has additional rows where one supplement BioSample is linked to more than one run. Counts of biological supplement samples and run-level rows are therefore stored separately.

## Exact focal matches

The ten exact focal accepted-name matches are:

1. `Cirsium domonii`
2. `Cirsium dipsacolepis`
3. `Cirsium pendulum`
4. `Cirsium sieboldii`
5. `Cirsium yezoense`
6. `Cirsium japonicum`
7. `Cirsium nipponicum`
8. `Cirsium nipponicum var. incomptum`
9. `Cirsium lineare`
10. `Cirsium vlassovianum`

Exact match means that the accepted query name is directly represented in PRJNA957074 runinfo and linked to Supplementary Table S1. It does **not** mean that every geographic population, colour morph or synonym attached to that accepted name is sampled.

Structured focal outputs:

- `data/evidence/prjna957074_focal_tip_recovery_2026-08-10.csv`
- `data/evidence/moreyra2025_focal_sample_context_2026-08-10.csv`

## Corrections to the previous sampling interpretation

### Cirsium pendulum

`C. pendulum` is an exact Moreyra/PRJNA957074 tip:

- BioSample `SAMN34240327`
- Experiment `SRX21011568`
- Run `SRR25265649`
- voucher from the Trans-Baikal Territory, Russia

This closes the **species-placement** question in the broad nuclear backbone. It does not sample the Japanese white form, Japanese purple populations or a paired Japanese–continental colour transect.

**Consequence:** do not use target capture merely to place the species. Use population RAD/resequencing for Japanese white/purple populations and continental bridges.

### Cirsium sieboldii

`C. sieboldii` is also an exact target-capture tip:

- BioSample `SAMN44017917`
- Experiment `SRX26291290`
- Run `SRR30887308`

However, Supplementary Table S1 records the material as cultivated at the Botanical Garden of Barcelona, and the original wild source is unresolved in the recovered metadata.

**Consequence:** species placement exists, but this sample cannot replace Japanese white/purple population sampling or the Zhejiang bridge.

### Cirsium yezoense

`C. yezoense` is represented by a wild Honshu sample from Fukushima:

- BioSample `SAMN44017952`
- Run `SRR30887226`

It is therefore a reusable modern nuclear coloured control. The Zhejiang population remains a population-geographic gap rather than a species-tree gap.

### Cirsium dipsacolepis

The previous `tree_verified` status is superseded by an exact public sample:

- BioSample `SAMN44017836`
- Run `SRR30887259`
- voucher from Shikoku, Japan

### Cirsium vlassovianum

Two continental samples are represented:

- a southern Sikhote-Alin sample with tree code `C. coryletorum` submitted to SRA as `C. vlassovianum`;
- a Mongolian sample under `C. vlassovianum`.

This is biologically useful for a Korea–Manchuria–Russian Far East standing-variation analysis, but the synonym hypothesis must remain explicit. Historical white-form populations are not represented by these two tips.

### Cirsium nipponicum and var. incomptum

The Moreyra sample table contains multiple tree codes and submitted names around the broad `C. nipponicum` concept, including `C. tanakae`, `C. tonense`, `C. nipponicum var. incomptum`, `C. nipponicum var. yoshinoi` and `C. yuki-uenoanum`.

These records demonstrate why accepted names, published species names, tree codes and SRA submitted names must remain separate fields. They should not be silently collapsed before comparing the Moreyra and Chang topologies.

## East Asian coverage revealed by Supplementary Table S1

The recovered East/Northeast Asian sample layer includes:

- a substantial Japanese radiation sample;
- Chinese taxa from Tibet, Xinjiang, Guizhou, Hubei, Sichuan, Yunnan and Henan;
- Russian Far East tips from Sikhote-Alin, Kamchatka/Chukotka and Primorskiy;
- inner Northeast Asian tips from Trans-Baikal, Tuva and Buryatia;
- a Mongolian `C. vlassovianum` tip.

This means that the broad East Asian nuclear backbone is considerably less empty than an accepted-name search alone suggested. The remaining gap is uneven taxon coverage and population/morph history, not a complete absence of modern nuclear data.

## Name reconciliation is a primary analytical object

Across the full supplement/runinfo join, 101 run-level records require medium or high name reconciliation:

- generic changes such as `Cirsium` versus `Lophiolepis`;
- spelling variants;
- infraspecific versus species-rank treatments;
- unpublished or provisional tree codes;
- cases such as `C. coryletorum` versus submitted `C. vlassovianum`;
- cases such as `C. maackii` versus submitted `C. japonicum var. maackii`.

Therefore, a missing exact accepted-name hit is not a valid sequencing justification until tree codes, published names and submitted names have been reconciled.

## Relationship to the Chang datasets

The Moreyra exact-tip audit does not recover the focal Taiwanese and Ryukyu taxa as exact tips. That does not make them nuclear gaps:

- `C. brevicaule`, `C. irumtiense`, `C. morii` and the Taiwanese `C. japonicum` varieties are resolved by Chang et al. 2026;
- `C. kawakamii`, `C. tatakaense`, `C. pengii`, `C. suffultum`, `C. nipponicum var. incomptum` and `C. kujuense` are resolved by Chang et al. 2025.

The correct unit of decision is therefore the **union of modern nuclear sources**, not PRJNA957074 alone.

The integrated builder is:

- `analysis/build_east_asia_nuclear_coverage.py`

It classifies each master-table taxon as:

1. species placement resolved in modern nuclear data;
2. published placement with file/accession recovery pending;
3. candidate species-level gap pending synonym and other-dataset audit;
4. population/morph history missing despite resolved species placement.

## What remains unrecovered

The Moreyra Supplementary Data 1 DOCX contains the sample table and supplementary figures/tables but no machine-readable final Newick/Nexus file. Exact branch lengths and the complete topology ensemble remain a separate recovery task.

Until the final tree is recovered or reconstructed from the published analysis files:

- Fitch/topology-only screens remain diagnostic;
- formal Mk rate estimates should not use invented branch lengths;
- stochastic mapping remains provisional;
- target-capture priorities should rely on exact tip presence and transition information, not on assumed sister relationships.

## Revised sequencing consequences

### Reuse existing species placement

Do not rebuild species placement for:

- `C. pendulum`
- `C. sieboldii`
- `C. yezoense`
- `C. dipsacolepis`
- `C. domonii`
- `C. lineare`
- focal Chang 2025/2026 taxa

unless a topology conflict itself becomes the research question.

### Population genomics remains necessary

Species placement does not answer the Chapter 2 question for:

- white versus coloured `var. takaoense`;
- Japanese white versus purple `C. pendulum`;
- Japanese white versus purple `C. sieboldii`;
- `C. brevicaule`–`C. irumtiense` gene flow;
- `C. kawakamii`–`C. tatakaense` homeolog/local-ancestry history;
- transregional `C. vlassovianum` standing variation.

### Target capture only for current-source gap candidates

A new Compositae1061 sample is justified only after:

1. accepted-name and synonym reconciliation;
2. Moreyra supplement/runinfo audit;
3. Chang 2025/2026 coverage check;
4. other modern nuclear datasets check;
5. confirmation that the missing placement changes a flower-colour transition inference.

## Reproducibility

The complete recovery was validated in GitHub Actions on the current Chapter 2 branch. The workflow freezes:

- 455 project runs;
- 327 submitted names;
- 299 supplement rows;
- 286 linked supplement samples;
- 43 core East Asian samples;
- 7 Northeast Asian bridge samples;
- 10 exact focal matches.

The downloaded publisher document itself is not committed. Source-derived audit tables, hashes, scripts and decision rules are versioned.
