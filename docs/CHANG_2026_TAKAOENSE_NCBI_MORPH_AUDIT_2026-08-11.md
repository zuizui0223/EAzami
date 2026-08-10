# Chang et al. 2026 var. *takaoense* voucher-to-NCBI morph audit

Date: 2026-08-11

## Question

Chang et al. (2026; DOI `10.1186/s12870-026-08097-6`) display six sampled `Cirsium japonicum var. takaoense` tips in Figure 1 and identify tips in that figure as white-corolla `(W)` or bluish-purple-corolla `(BP)`. Supplementary Table S1 gives six collection localities, sample codes and voucher numbers, but does not provide the W/BP state of each row.

The immediate question was therefore split into two independent tasks:

1. can each published voucher be linked to an exact public sequence accession?;
2. does official NCBI metadata expose the W/BP phenotype of that accession?

The first is now solved. The second remains unresolved.

## Reproducible public-data audit

The workflow recovered all public SRA metadata for BioProject `PRJNA1311153`, then fetched the complete BioSample attribute dictionary for each `takaoense` sample.

Frozen implementation:

- `analysis/audit_chang2026_biosample_morph_metadata.py`
- `tests/test_audit_chang2026_biosample_morph_metadata.py`
- `.github/workflows/audit-chang2026-biosample-morph.yml`

Frozen outputs:

- `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_ncbi_public_sample_context_2026-08-11.csv`
- `data/evidence/chang2026_takaoense_ncbi_morph_audit_summary_2026-08-11.json`

## Exact voucher-to-public-accession mapping

| Voucher | Published locality | Herbarium | Run | BioSample | Public SampleName |
|---|---|---|---|---|---|
| `ccy3559` | Fenchihu | TNM | `SRR35152718` | `SAMN50798021` | `Cirsium japonicum var. takaoense-3559` |
| `ccy3560` | Wutai | TNM | `SRR35152717` | `SAMN50798022` | `Cirsium japonicum var. takaoense-3560` |
| `ccy3629` | Fengbin | TNM | `SRR35152738` | `SAMN50798024` | `Cirsium japonicum var. takaoense-3629` |
| `ccy3807` | Tengji | TCF | `SRR35152736` | `SAMN50798026` | `Cirsium japonicum var. takaoense-3807` |
| `ccy3835` | Nanheng | TCF | `SRR35152735` | `SAMN50798027` | `Cirsium japonicum var. takaoense-3835` |
| `ccy3839` | Ludao | TCF | `SRR35152734` | `SAMN50798028` | `Cirsium japonicum var. takaoense-3839` |

The linkage is not inferred from geography. Each public `SampleName` ends with the exact numeric portion of the voucher, and the BioSample `isolate` attribute independently contains the same number. All six mappings are one-to-one and have no alternative candidate run.

## NCBI attributes present

Each of the six BioSamples exposes the same six attribute types:

- submitted organism;
- collection date;
- developmental stage;
- geographic locality;
- isolate;
- tissue.

The tissue is recorded as young leaves. Across 36 attribute rows, there are zero explicit values for:

- flower or corolla colour;
- white versus bluish-purple state;
- floral morph or phenotype;
- pigment or anthocyanin state.

Therefore the audit makes **zero W/BP assignments**.

## Important taxonomic/provenance distinction

NCBI stores the broad submitted scientific name as `Cirsium japonicum var. japonicum`, while `SampleName` stores `Cirsium japonicum var. takaoense-<isolate>`. The broad submitted organism name is not used to overwrite the taxon identification in the paper and Supplementary Table S1. Both names are retained as separate provenance fields.

## What is now known

- The six published `takaoense` voucher specimens correspond to six exact public transcriptome runs.
- Those runs can be reused immediately once W/BP labels are recovered.
- No additional sequencing is required merely to discover which public accession belongs to each voucher.

## What remains unknown

Official NCBI runinfo and BioSample XML do not reveal which of the six specimens is `(W)` or `(BP)`. Therefore:

- the published transcriptome tree still cannot be recoded as a morph-specific tree from NCBI metadata alone;
- no flower-colour state may be inferred from locality, elevation, herbarium, library number, read count or topology;
- all six vouchers remain unresolved in the flower-colour ledger.

## Next evidence ladder

The remaining W/BP mapping should be recovered, in order, from:

1. a high-resolution official Figure 1 or its editable source, where the paper states that tips are labelled `(W)` and `(BP)`;
2. direct author confirmation linking the six voucher numbers to Figure 1 labels;
3. TNM/TCF voucher images, herbarium labels, collector field photographs or collection notebooks;
4. new morph-linked sampling if the states of the published vouchers cannot be reconstructed reliably.

## Consequence for the sampling design

The Stage 0 task for `var. takaoense` is now narrower:

> recover W/BP labels for six already identified public transcriptome samples.

If both morphs occur among those six accessions, the existing transcriptome topology can be used immediately for a first morph-aware history test. If only one morph was sequenced, or if the labels remain irrecoverable, new paired white/coloured sampling is required.

No locality-based assignment is allowed because it would circularly convert geography into the phenotype later tested against population history.

## Validation provenance

GitHub Actions run `31427871328` completed successfully:

- 16 offline tests passed;
- 25 project run rows recovered;
- six `takaoense` runs recovered;
- six one-to-one voucher/run/BioSample links verified;
- zero ambiguous links;
- six BioSample dictionaries and 36 attributes audited;
- zero morph-relevant attributes;
- zero direct W/BP assignments.

Artifact:

- ID: `9077891898`
- digest: `sha256:e00d724f51c7d6fe0286a083d80b578ab0511e0b0fc65016918fbf14c0d209e0`
