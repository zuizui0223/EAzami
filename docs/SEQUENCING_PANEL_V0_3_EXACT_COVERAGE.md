# Sequencing panel v0.3: decisions after exact Moreyra–Chang coverage integration

Date: 2026-08-10  
Updated: 2026-08-11 after exact var. *takaoense* voucher–NCBI reconciliation

## Why the panel changed

Earlier panel versions mixed three different situations:

1. a species genuinely absent from modern nuclear trees;
2. a species already placed, but its white/coloured populations were not sampled;
3. a historical white-form name whose extant natural population had not been verified.

The exact recovery of Moreyra et al. 2025 Supplementary Table S1 and PRJNA957074, combined with the Chang 2025/2026 sample audits, now allows those situations to be separated.

The reproducible integrated screen currently covers **33 master-table taxa** after adding the Korean and Northeast Asian candidates. The central rule is:

> use target capture to close a genuine transition-critical species gap; use RAD-seq or resequencing to resolve morph/population history after species placement is known.

The machine-generated coverage table is produced by:

- `analysis/build_east_asia_nuclear_coverage.py`

The frozen sampling decision table is:

- `sampling/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv`

## Major correction: no active Tier-A species-placement gap

For the currently active Tier-A systems, modern species-level nuclear placement is already available from at least one source:

| System | Existing nuclear evidence | Remaining problem |
|---|---|---|
| `var. takaoense` | Chang 2026 phylotranscriptomics; six public transcriptomes now linked exactly to vouchers | W/BP labels and population ancestry unresolved |
| `C. brevicaule–C. irumtiense` | Chang 2026 | gene flow, local ancestry and repeated mechanism |
| `C. kawakamii–C. tatakaense–C. pengii` | Chang 2025 and 2026 | population ancestry, cytotype/homeolog and mechanism |
| `C. pendulum` | exact Moreyra target-capture tip | Japanese white/purple and continental bridge history |
| `C. sieboldii` | exact Moreyra target-capture tip | existing sample is cultivated; Japan/Zhejiang population history |
| `var. albescens/fukienense` | Chang 2026 | white-haplotype sharing and coloured-ancestry controls |

Therefore, the first sequencing wave should not spend samples on rebuilding these species placements.

## Stage 0: recover information before sequencing

### var. takaoense voucher morphs

The highest-information immediate action is still not sequencing. It is recovering the flower colour of the six existing transcriptome vouchers.

The accession identity problem is now solved:

| Code | Voucher | Run | BioSample | BioSample isolate | Morph |
|---|---|---|---|---|---|
| FC | `ccy3559` | `SRR35152718` | `SAMN50798021` | `3559` | unresolved |
| WY | `ccy3560` | `SRR35152717` | `SAMN50798022` | `3560` | unresolved |
| FB | `ccy3629` | `SRR35152738` | `SAMN50798024` | `3629` | unresolved |
| TJ | `ccy3807` | `SRR35152736` | `SAMN50798026` | `3807` | unresolved |
| NH | `ccy3835` | `SRR35152735` | `SAMN50798027` | `3835` | unresolved |
| LT | `ccy3839` | `SRR35152734` | `SAMN50798028` | `3839` | unresolved |

Each link is supported by the collector-number suffix in NCBI `SampleName` and the matching BioSample `isolate`. There are no ambiguous voucher-to-run matches.

However, official NCBI runinfo and BioSample metadata contain no flower-colour, corolla, phenotype, morph, pigment or anthocyanin attribute for these samples. They therefore resolve accession provenance but do not resolve `(W)` versus `(BP)`.

Supplementary Table S6 independently contains collector records for:

- `ccy3559`;
- `ccy3560`;
- `ccy3629`;
- `ccy3839`.

It does not expose a sample-level colour state. Collector number `ccy3839` also has a repository conflict:

- Supplementary Table S1: TCF;
- Supplementary Table S6: TNM.

This conflict must be resolved before requesting the correct voucher image or label.

The direct-evidence order is now:

1. read FC, TJ, NH, WY, FB and LT `(W)` / `(BP)` suffixes from a high-resolution Figure 1 or source tree;
2. obtain author confirmation;
3. inspect TNM/TCF voucher images, labels or collector field records;
4. resolve whether `ccy3839` is held at TCF, TNM or both.

Do not infer colour from locality, elevation, herbarium, library number, NCBI submitted scientific name or topology.

Files:

- `docs/CHANG2026_TAKAOENSE_MORPH_EVIDENCE_AUDIT_2026-08-11.md`
- `docs/CHANG2026_TAKAOENSE_MORPH_REQUEST_DRAFT.md`
- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_ncbi_morph_audit_summary_2026-08-11.json`
- `data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv`

If both morphs are already represented, the published sample topology may provide a first morph-history test. If only one morph is represented, new paired sampling remains mandatory. If both are represented but geography or reticulation dominates the six-tip pattern, dense population genomics is still required.

Tracked in Issue #11.

## Stage 1: population genomic core

### 1. var. takaoense

Use morph-linked RAD-seq or low-coverage resequencing after voucher recovery. The six existing transcriptomes should be reused as labelled anchors whenever their W/BP states can be verified, but one plant per locality cannot by itself distinguish population-demographic alternatives.

Sample multiple populations for each morph, prioritizing mixed populations because within-population contrasts reduce background geographic differentiation.

Competing models:

- two or more independent white losses;
- one shared white origin plus coloured reactivation;
- ancestral white/coloured polymorphism;
- coloured-haplotype introgression from `australe/fukienense` ancestry.

### 2. C. pendulum

The exact Moreyra sample is from Trans-Baikal and supplies a continental nuclear anchor. It does not replace:

- Japanese white populations;
- nearby Japanese purple controls;
- Korea, Northeast China or Primorye bridge populations.

The required new data are therefore population genomic, not species-level target capture.

### 3. C. sieboldii

The Moreyra tip is exact at the submitted-name level but was cultivated at the Botanical Garden of Barcelona, with wild provenance unresolved. The Japanese white/purple comparison and Zhejiang bridge remain open.

### 4. C. kawakamii–C. tatakaense

Both species are 2n=64 and represented in two modern phylotranscriptomic studies. This is one of the cleanest replicated loss/mechanism systems, but requires ploidy-aware local ancestry and matched floral expression/pigment data.

### 5. C. brevicaule–C. irumtiense

The existing sister context favours a white loss in `C. brevicaule`, not a regain in `C. irumtiense`. New population data should test gene flow, ancestral polymorphism and whether the white mechanism is homologous to independent white lineages.

## Stage 2: conditional Korean and Northeast Asian systems

Historical white-form names are candidate-discovery evidence, not proof of extant polymorphism.

### C. vlassovianum

Species-level nuclear evidence is already present from Sikhote-Alin and Mongolia. Therefore, if white populations are verified, proceed directly to geographically stratified population genomics after resolving the `C. coryletorum` name relationship.

### C. setidens and C. rhinoceros

These remain candidate species-level nuclear gaps, but they are not active sequencing priorities until extant natural white material is confirmed. If confirmed and no other modern nuclear dataset is found:

1. obtain Compositae1061 placement;
2. then sample white/coloured populations densely.

### C. schantarense

An older ITS placement exists, but no exact modern Moreyra/Chang tip was recovered. Its broad range makes it valuable for standing-variation questions only after white records and taxonomy are verified.

## Stage 3: broader colour and backbone candidates

### C. taiwanense

The yellow 2n=32 lineage may become important if Chapter 2 expands from white/anthocyanin loss to broader pigment-pathway evolution. Its target-capture placement is conditional on that expanded role.

### Chinese coloured taxa and other Taiwan gaps

`C. shansiense`, `C. leducii`, `C. ferum`, `C. suzukii`, `C. hosokawae` and the `C. arisanense` forms should not be sequenced merely because a current integrated-source tip is absent. First establish:

- accepted-name and synonym status;
- direct flower-colour evidence;
- whether placement changes a loss/regain count or anchors a focal branch.

## Modality decision rule

| Evidence state | New data |
|---|---|
| accession identity resolved; morph label missing | figure/voucher/author evidence before new sequencing |
| species placement verified; morph/population missing | RAD-seq or resequencing |
| species placement verified; colour mechanism missing | pigment chemistry + floral RNA + candidate-region analysis |
| extant white morph unverified | voucher/field verification before sequencing |
| transition-critical modern nuclear tip genuinely absent | Compositae1061 target capture |
| mixed or uncertain cytotypes | flow cytometry/chromosomes before genotype calling |
| plastome only | retain maternal history; obtain nuclear placement only when transition-informative |

## Implication for Chapter 2

The project has moved away from a generic goal of “constructing an East Asian RAD-seq tree.” The sharper design is:

1. reuse the existing Compositae1061/phylotranscriptomic species backbone;
2. recover missing sample metadata before generating redundant sequence data;
3. close only verified transition-critical taxon gaps with compatible target capture;
4. use population genomics to identify the ancestry of white and coloured alleles;
5. use pigment chemistry and floral expression to identify the molecular switch;
6. claim regain only after introgression and ancestral standing variation are disfavoured.

This design uses the available phylogenetic information rather than paying to rediscover it.
