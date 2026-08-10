# Chang et al. 2026 var. *takaoense* voucher and morph-evidence audit

Date: 2026-08-11

## Question

Chang et al. 2026 sampled six transcriptomes of *Cirsium japonicum* var. *takaoense*. The taxon contains white-corolla and bluish-purple-corolla morphs, and Figure 1 defines the corresponding tip suffixes:

- `(W)` — white-corolla morph;
- `(BP)` — bluish-purple-corolla morph.

Supplementary Table S1 gives locality, coordinate, altitude, voucher and herbarium for the six samples, but does not provide the sample-level W/BP mapping. Recovering that mapping is potentially high information because it determines whether the published transcriptome topology already includes both morphs.

This audit separates three questions:

1. Which public run and BioSample belong to each published voucher?
2. Do Supplementary Table S6, the main text or NCBI metadata directly state the flower-colour morph?
3. What direct evidence is still required before the published tree can be treated as morph specific?

## Result in one sentence

> All six published vouchers now map one-to-one to public PRJNA1311153 runs and BioSamples, but none of the official NCBI attributes or accessible supplementary text provides the sample-level W/BP state; therefore all six morph identities remain unresolved.

## Six exact voucher-to-accession links

| Figure/locality code | Locality | Published voucher | S1 herbarium | SRA run | BioSample | NCBI SampleName | BioSample isolate |
|---|---|---|---|---|---|---|---|
| FC | Fenchihu, Chiayi | `ccy3559` | TNM | `SRR35152718` | `SAMN50798021` | `Cirsium japonicum var. takaoense-3559` | `3559` |
| WY | Wutai, Pingtung | `ccy3560` | TNM | `SRR35152717` | `SAMN50798022` | `Cirsium japonicum var. takaoense-3560` | `3560` |
| FB | Fengbin, Hualien | `ccy3629` | TNM | `SRR35152738` | `SAMN50798024` | `Cirsium japonicum var. takaoense-3629` | `3629` |
| TJ | Tengji, Kaohsiung | `ccy3807` | TCF | `SRR35152736` | `SAMN50798026` | `Cirsium japonicum var. takaoense-3807` | `3807` |
| NH | Nanheng, Taitung | `ccy3835` | TCF | `SRR35152735` | `SAMN50798027` | `Cirsium japonicum var. takaoense-3835` | `3835` |
| LT | Ludao, Taitung | `ccy3839` | TCF | `SRR35152734` | `SAMN50798028` | `Cirsium japonicum var. takaoense-3839` | `3839` |

The match is supported independently by:

- the exact collector-number suffix in `SampleName`;
- the same number in the BioSample `isolate` attribute;
- one unique public run and BioSample per published voucher.

No match relies on geography or an assumed flower colour.

## Important NCBI naming distinction

The six runinfo rows use the broad submitted `ScientificName`:

`Cirsium japonicum var. japonicum`

However, their `SampleName` values explicitly contain:

`Cirsium japonicum var. takaoense-<collector number>`

The broad submitted scientific name should therefore not replace the more specific published voucher identity. The project retains all three fields separately:

- published taxon/voucher;
- NCBI submitted scientific name;
- NCBI SampleName/isolate.

## NCBI morph-evidence result

The complete BioSample attribute dictionaries contain six attributes per sample:

- organism;
- collection date;
- developmental stage;
- geographic location;
- isolate;
- tissue.

Across the six BioSamples:

- morph-relevant attribute rows: **0**;
- direct white or bluish-purple assignments: **0**;
- ambiguous voucher-to-run matches: **0**.

No attribute mentions flower colour, corolla, phenotype, morph, pigment or anthocyanin. Consequently, NCBI resolves accession provenance but not the W/BP mapping.

Frozen outputs:

- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_ncbi_morph_audit_summary_2026-08-11.json`
- `analysis/audit_chang2026_biosample_morph_metadata.py`
- `.github/workflows/audit-chang2026-biosample-morph.yml`

## Supplementary Table S6 and main-text evidence

A separate source audit preserves evidence outside NCBI:

| Voucher | S6 result | Main-text result | Morph result |
|---|---|---|---|
| `ccy3559` | exact collector record, TNM | none located | unresolved |
| `ccy3560` | exact collector record, TNM | none located | unresolved |
| `ccy3629` | exact collector record, TNM | none located | unresolved |
| `ccy3807` | collector number not recovered in S6 | none located | unresolved |
| `ccy3835` | collector number not recovered in S6 | specimen 3835 explicitly discussed near the *C. lidaoense* type locality | unresolved |
| `ccy3839` | exact collector record, TNM | none located | unresolved |

The main-text mention of specimen 3835 confirms its taxonomic relevance but does not state its corolla colour.

Frozen source ledger:

- `data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv`
- `analysis/validate_chang2026_takaoense_voucher_evidence.py`

## Herbarium conflict for ccy3839

The source documents disagree on the repository of collector number 3839:

- Supplementary Table S1: `TCF`;
- Supplementary Table S6: `TNM`.

This is retained as a direct source conflict. It must not be silently harmonized. It may reflect:

- a transcription error;
- duplicate material deposited in more than one herbarium;
- a later repository change;
- different voucher and examined-specimen sheets.

The conflict does not provide flower-colour evidence, but it changes where the voucher image or label should be requested.

## Figure 1 recovery attempts

The article caption establishes that W/BP are sample-level tip labels. Parsers and recovery workflows were implemented for:

- the open-access Springer PDF;
- the official Springer Nature Figure 1 image endpoint;
- a Research Square preprint mirror.

Those live endpoints rejected automated GitHub Actions clients during the audit. The failure is treated as external-source unavailability, not as absence of a figure or absence of morph labels. Pull-request CI therefore validates the parser and unresolved evidence ledger offline, while live recovery remains a manual workflow.

No OCR-derived or locality-derived morph state has been committed.

## What is now solved

The following are no longer uncertain:

1. all six Supplementary Table S1 samples have public transcriptome reads;
2. every voucher maps one-to-one to a run and BioSample;
3. the exact run/BioSample identities are reproducible from official metadata;
4. NCBI contains no direct W/BP attribute;
5. the S1/S6 repository conflict is limited to `ccy3839` in the current ledger;
6. no sample-level morph assignment is currently supported outside the labelled figure or direct voucher/author evidence.

## What remains unresolved

For each of the six samples, the following field remains blank:

- `direct_sample_morph_label` — `W` or `BP`.

Until those values are recovered, the published sample tree cannot answer:

- whether white and bluish-purple morphs are each monophyletic;
- whether one morph is nested within the other;
- whether multiple independent colour transitions are visible among the six tips;
- whether the current transcriptomes already remove the need for a first morph-linked pilot.

## Prohibited inferences

Do not infer W/BP from:

- locality or altitude;
- mainland versus island occurrence;
- herbarium repository;
- NCBI library number;
- read count or assembly quality;
- tree position;
- the broad NCBI `ScientificName`;
- taxon-level statements that the variety is polymorphic.

A taxon-level colour range is not a sample-level morph label.

## Direct evidence required next

Use the following order:

1. read the `(W)` / `(BP)` suffix attached to FC, TJ, NH, WY, FB and LT in a high-resolution Figure 1 or figure source file;
2. obtain author confirmation of the six code/voucher assignments;
3. inspect TNM/TCF voucher images, labels or collector field records;
4. resolve whether `ccy3839` is deposited at TCF, TNM or both;
5. if published morph states cannot be recovered, collect new morph-linked DNA/RNA/pigment material.

## Consequence for sequencing priority

The current result does **not** justify resequencing these same six individuals merely to identify their accession provenance; that provenance is already solved.

The immediate high-information action remains morph recovery. After W/BP assignment:

- if both morphs are represented and their sample topology is informative, reuse the existing transcriptomes first;
- if only one morph is represented, proceed to paired morph-linked population sampling;
- if both morphs are represented but reticulation or geography dominates the sample topology, proceed to population RAD-seq or resequencing with explicit morph, ploidy, pigment and floral-RNA metadata.

## Validation status

### Voucher/source ledger

GitHub Actions run `31428532236`:

- 23 tests passed;
- six vouchers validated;
- four exact S6 collector records;
- two S6 non-recoveries;
- one retained S1/S6 herbarium conflict (`ccy3839`);
- zero invented morph assignments.

### NCBI accession audit

GitHub Actions run `31428532005`:

- 16 tests passed;
- 25 PRJNA1311153 run rows;
- six *takaoense* candidate rows;
- six one-to-one voucher/run/BioSample links;
- 36 BioSample attribute rows;
- zero morph-relevant attributes;
- zero direct sample-colour assignments.

Artifact:

- ID: `9078151170`
- SHA256: `8d319dadbe50696d142ec770777437312b5c73f4360be5420723d46b3ec69cbd`
