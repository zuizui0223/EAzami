# Chang et al. 2026 var. *takaoense* voucher and morph-evidence audit

Date: 2026-08-11  
Status: six of six sample-level W/BP labels recovered

## Question

Chang et al. 2026 sampled six transcriptomes of *Cirsium japonicum* var. *takaoense*. The taxon contains white-corolla and bluish-purple-corolla morphs, and Figure 1 defines the corresponding tip suffixes:

- `(W)` — white-corolla morph;
- `(BP)` — bluish-purple-corolla morph.

Supplementary Table S1 gives locality, coordinate, altitude, voucher and herbarium for the six samples but does not provide the sample-level W/BP mapping. This audit reconciles the supplement, official PRJNA1311153 metadata and the official Figure 1 image.

## Result in one sentence

> All six published vouchers map one-to-one to public runs and BioSamples, and direct labels printed concordantly in Figure 1 panels B and C identify FC/TJ/NH as bluish-purple and WY/FB/LT as white.

## Exact voucher, accession and morph mapping

| Code | Locality | Voucher | S1 herbarium | SRA run | BioSample | Figure 1 morph |
|---|---|---|---|---|---|---|
| FC | Fenchihu, Chiayi | `ccy3559` | TNM | `SRR35152718` | `SAMN50798021` | `BP` — bluish-purple |
| WY | Wutai, Pingtung | `ccy3560` | TNM | `SRR35152717` | `SAMN50798022` | `W` — white |
| FB | Fengbin, Hualien | `ccy3629` | TNM | `SRR35152738` | `SAMN50798024` | `W` — white |
| TJ | Tengji, Kaohsiung | `ccy3807` | TCF | `SRR35152736` | `SAMN50798026` | `BP` — bluish-purple |
| NH | Nanheng, Taitung | `ccy3835` | TCF | `SRR35152735` | `SAMN50798027` | `BP` — bluish-purple |
| LT | Ludao, Taitung | `ccy3839` | TCF | `SRR35152734` | `SAMN50798028` | `W` — white |

The accession match is supported independently by:

- the exact collector-number suffix in NCBI `SampleName`;
- the same number in the BioSample `isolate` attribute;
- one unique public run and BioSample per published voucher.

The morph assignment is supported independently within the published figure by two printed occurrences per sample:

### Figure 1 panel B — Neighbor-Net

- `var. takaoense_FC-3559(BP)`
- `var. takaoense_TJ-3807(BP)`
- `var. takaoense_NH-3835(BP)`
- `var. takaoense_WY-3560(W)`
- `var. takaoense_FB-3629(W)`
- `var. takaoense_LT-3839(W)`

### Figure 1 panel C — species-delimitation tree

- `C. japonicum var. takaoense_FC-3559(BP)`
- `C. japonicum var. takaoense_TJ-3807(BP)`
- `C. japonicum var. takaoense_NH-3835(BP)`
- `C. japonicum var. takaoense_WY-3560(W)`
- `C. japonicum var. takaoense_FB-3629(W)`
- `C. japonicum var. takaoense_LT-3839(W)`

No match or morph assignment relies on geography, altitude or an assumed evolutionary history.

## Official Figure 1 provenance

The full official Springer Nature Figure 1 PNG was recovered through the static-content endpoint.

- dimensions: `1945 × 2400` pixels;
- image size: 2,465,127 bytes;
- image SHA256: `10375f1d79a4799babdebffca84301f602adfa0aabc825b852de84177bbb878c`;
- Actions run: `31429139819`;
- artifact: `9078372622`;
- artifact SHA256: `6d5f8f4e1e059122629acce751adb8eb57cd3e5fa95ff9dfa92fcc72bb4ea68f`.

The image itself remains in the versioned Actions artifact. Repository tables retain the direct transcription, hash and provenance.

Frozen assignment table:

- `data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv`

Validator:

- `analysis/validate_chang2026_takaoense_figure1_assignments.py`

## Important NCBI naming distinction

The six runinfo rows use the broad submitted `ScientificName`:

`Cirsium japonicum var. japonicum`

However, their `SampleName` values explicitly contain:

`Cirsium japonicum var. takaoense-<collector number>`

The broad submitted scientific name should therefore not replace the more specific published voucher identity. The project retains:

- published taxon and voucher;
- NCBI submitted scientific name;
- NCBI SampleName and isolate;
- direct Figure 1 morph label.

## NCBI metadata result

The complete BioSample attribute dictionaries contain six attributes per sample:

- organism;
- collection date;
- developmental stage;
- geographic location;
- isolate;
- tissue.

Across the six BioSamples:

- morph-relevant attribute rows: **0**;
- direct NCBI white or bluish-purple assignments: **0**;
- ambiguous voucher-to-run matches: **0**.

NCBI resolves accession provenance but not colour. The W/BP evidence comes from the published Figure 1 labels, not from NCBI metadata.

Frozen NCBI outputs:

- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_ncbi_morph_audit_summary_2026-08-11.json`
- `analysis/audit_chang2026_biosample_morph_metadata.py`
- `.github/workflows/audit-chang2026-biosample-morph.yml`

## Supplementary Table S6 and main-text evidence

| Voucher | S6 result | Main-text result | Direct Figure 1 morph |
|---|---|---|---|
| `ccy3559` | exact collector record, TNM | none located | BP |
| `ccy3560` | exact collector record, TNM | none located | W |
| `ccy3629` | exact collector record, TNM | none located | W |
| `ccy3807` | collector number not recovered in S6 | none located | BP |
| `ccy3835` | collector number not recovered in S6 | specimen 3835 explicitly discussed near the *C. lidaoense* type locality | BP |
| `ccy3839` | exact collector record, TNM | none located | W |

The main-text mention of specimen 3835 confirms its taxonomic relevance but is not the source of its BP state.

Frozen source ledger:

- `data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv`
- `analysis/validate_chang2026_takaoense_voucher_evidence.py`

## Herbarium conflict for ccy3839

The source documents disagree on the repository of collector number 3839:

- Supplementary Table S1: `TCF`;
- Supplementary Table S6: `TNM`.

This conflict remains unresolved and is independent of the W assignment. It may reflect a transcription error, duplicate sheets, a repository change or different voucher/examined-specimen material. Do not silently harmonize it.

## Sample-topology observation

Figure 1 adds more than labels.

### Panel C

The three BP samples—NH, TJ and FC—form the terminal morph-homogeneous portion of the displayed var. *takaoense* sample topology. The three W samples—LT, FB and WY—occur on successive branches outside that BP grouping in the displayed tree.

### Panel B

The Neighbor-Net likewise places the three BP-labelled samples together and the three W-labelled samples together without cross-morph interspersion among the six labelled tips.

This is direct evidence of morph-associated genomic structure in the published sample set. It is **not yet proof of evolutionary regain**.

The displayed topology is compatible with a single transition separating the sampled W and BP groups under some root-state assumptions, but direction remains dependent on:

- the placement and ancestral state of white var. *albescens*;
- coloured var. *fukienense*, var. *australe* and var. *japonicum* context;
- uncertain/weak short internodes within the sample cluster;
- reticulation highlighted by the paper;
- geographic population structure;
- the distinction between a derived regulatory reactivation and retention or introgression of a coloured haplotype.

Therefore the valid new conclusion is:

> The six existing transcriptomes contain both morphs and show morph-associated clustering; they make a regain model more directly testable but do not by themselves demonstrate regain.

## What is now solved

1. all six Supplementary Table S1 samples have public transcriptome reads;
2. every voucher maps one-to-one to a run and BioSample;
3. the exact run/BioSample identities are reproducible from official metadata;
4. all six sample-level W/BP labels are directly recovered;
5. the existing transcriptome set contains three W and three BP samples;
6. panels B and C repeat the same six labels;
7. NCBI contains no competing sample-level colour attribute;
8. the S1/S6 repository conflict remains limited to `ccy3839`.

## Prohibited inferences

Do not infer evolutionary direction solely from:

- the order of tips in a single rendered tree;
- white var. *albescens* alone;
- locality or altitude;
- mainland versus island occurrence;
- herbarium repository;
- NCBI submitted scientific name;
- visual morph clustering without demographic or introgression tests.

Direct W/BP labels solve phenotype identity, not causal history.

## Next analysis

1. encode the six W/BP states on the published sample topology;
2. quantify morph monophyly/clustering and topology sensitivity;
3. include var. *albescens*, var. *fukienense*, var. *australe* and var. *japonicum* as state/root context;
4. retain the Neighbor-Net as reticulation evidence rather than forcing every relation into one tree;
5. reuse the six transcriptomes as labelled anchors in new population sampling;
6. test whether the coloured group carries a derived restoration, retained ancestral haplotype or introgressed ancestry;
7. resolve the `ccy3839` TCF/TNM repository conflict separately.

The prepared author request remains useful for machine-readable trees, branch lengths and the herbarium discrepancy, but it is no longer needed to obtain the six W/BP labels.

## Consequence for sequencing priority

Do not resequence these same six individuals merely to determine their morph identity or accession provenance. Both are now known.

The existing samples are geographically sparse—one plant per locality—so they do not replace population genomics. The next sequencing phase should:

- retain the six transcriptomes as labelled anchors;
- prioritize mixed or geographically matched W/BP populations;
- collect multiple plants per population;
- link leaf DNA, floral RNA, pigment chemistry, reflectance and ploidy to the same individuals;
- fit standing-variation, introgression, parallel-loss and restoration models explicitly.

## Validation status

### NCBI accession audit

GitHub Actions run `31428532005`:

- 16 tests passed;
- 25 PRJNA1311153 run rows;
- six *takaoense* candidate rows;
- six one-to-one voucher/run/BioSample links;
- 36 BioSample attribute rows;
- zero morph-relevant NCBI attributes.

Artifact:

- ID: `9078151170`
- SHA256: `8d319dadbe50696d142ec770777437312b5c73f4360be5420723d46b3ec69cbd`

### Official Figure 1 recovery

GitHub Actions run `31429139819`:

- official `1945 × 2400` PNG recovered;
- image hash frozen;
- panels B and C visually reconciled;
- six direct assignments recovered;
- W = `ccy3560`, `ccy3629`, `ccy3839`;
- BP = `ccy3559`, `ccy3807`, `ccy3835`.
