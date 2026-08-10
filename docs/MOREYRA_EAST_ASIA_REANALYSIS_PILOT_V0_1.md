# Moreyra 2025 East Asia raw-read reconstruction pilot v0.1

Date: 2026-08-11

## Purpose

The Moreyra supplement, PRJNA957074 sample metadata and the corresponding-author summary matrices are now recoverable. The next useful step is not an immediate 299-sample rerun. It is a controlled smoke test that answers four practical questions:

1. can the public runs be recovered under stable sample identities;
2. can the Compositae target loci be assembled reproducibly across representative East Asian regions;
3. do newly assembled recovery statistics agree with the public HybPiper summaries closely enough to justify a larger reconstruction;
4. can tree codes, submitted names and vouchers remain joined without silently resolving synonyms.

This pilot prepares exact sample/run and locus manifests. Pull-request CI does not download the raw-read cohort.

## Implemented files

- `analysis/build_moreyra_reanalysis_pilot.py`
- `analysis/export_moreyra_locus_manifests.py`
- `tests/test_build_moreyra_reanalysis_pilot.py`
- `tests/test_export_moreyra_locus_manifests.py`
- `.github/workflows/prepare-moreyra-reanalysis-pilot.yml`

Generated workflow artifact:

```text
data/evidence/generated/moreyra_reanalysis_pilot/
  moreyra_east_asia_12_sample_pilot.csv
  moreyra_east_asia_12_sample_runs.txt
  download_public_reads.sh
  pilot_summary.json

data/evidence/generated/moreyra_author_repository/locus_sets/
  moreyra_public_1061_loci.txt
  moreyra_reproducible_531_candidate_loci.txt
  moreyra_conservative_241_no_warning_loci.txt
  moreyra_manual_review_290_candidate_loci.txt
  locus_set_manifest.csv
  locus_set_manifest.json
```

## Twelve-sample panel

The panel is deliberately small enough for an initial HPC or workstation run, but broad enough to expose geographic, taxonomic and name-reconciliation failures.

| Order | Tree code | Region | Pilot role |
|---:|---|---|---|
| 1 | `Cirsium domonii` | Japan | main Japanese radiation anchor |
| 2 | `Cirsium dipsacolepis` | Japan | separate Japanese invasion anchor |
| 3 | `Cirsium lineare` | Japan | cross-study coloured/root anchor |
| 4 | `Cirsium yezoense` | Japan | coloured Japan–Zhejiang bridge control |
| 5 | `Cirsium argyracanthum` | China/Tibet | distant Chinese lineage anchor |
| 6 | `Cirsium fanjingshanense` | China/Guizhou | southwest China recovery test |
| 7 | `Cirsium fargesii` | China/Hubei | central China recovery test |
| 8 | `Cirsium kamtschaticum` | Russian Far East | northern bridge lineage |
| 9 | `Cirsium coryletorum` | Russian Far East | deliberate tree-code/SRA-name reconciliation test |
| 10 | `Cirsium pendulum` | Trans-Baikal | continental anchor for the Japanese white/purple system |
| 11 | `Cirsium serratuloides` | Inner Northeast Asia | Buryatia bridge lineage |
| 12 | `Cirsium vlassovianum` | Mongolia | continental counterpart to the Sikhote-Alin sample |

The deliberate conflict is:

```text
published tree code: Cirsium coryletorum
NCBI submitted name: Cirsium vlassovianum
BioSample: SAMN34240275
Run: SRR25265601
```

It is retained because a successful reconstruction pipeline must preserve, not erase, this distinction.

## Exported locus sets

The public author-repository matrices support four named outputs.

| Set | Count | Meaning |
|---|---:|---|
| `public_1061` | 1,061 | every named public locus |
| `reproducible_531` | 531 | warning count ≤10 and raw occupancy ≥0.80 |
| `conservative_241` | 241 | no public paralog warning and raw occupancy ≥0.80 |
| `manual_review_290` | 290 | high occupancy but the original manual gene-tree decision is unavailable |

The exporter writes sorted locus names and SHA256 values. It refuses to emit an `exact Moreyra 350` set, because that retained list is not present in the located public artifacts.

## Execution stages outside pull-request CI

### Stage A — raw-read retrieval

Use the generated `download_public_reads.sh` on a local workstation or HPC node with SRA Toolkit. The script:

- uses exact run accessions;
- calls `prefetch` and `fasterq-dump --split-files`;
- compresses output with `pigz` when available;
- does not choose taxonomic synonyms or merge biological samples.

### Stage B — target recovery

Run a versioned HybPiper environment with the exact Compositae target file used for the reconstruction. Preserve:

- software and target-file versions;
- read counts and mapping percentage;
- genes mapped, assembled and recovered at 25/50/75 percent;
- every paralog and chimera warning;
- unstitched sequences and intronerate output where used;
- sample names linked to tree code, BioSample and voucher.

Do not begin by restricting assembly to 241 loci. Recover the available Compositae locus universe, then subset analytically.

### Stage C — comparison with public summaries

For each sample and locus, compare the new run against:

- `hybpiper_stats_exonerate.tsv`;
- `seq_lengths_exonerate.tsv`;
- `paralog_report.xlsx`.

Expected differences must be interpreted in light of:

- HybPiper and dependency versions;
- target-file version;
- read preprocessing;
- seven samples present in the public sequence-length matrix but absent from its HybPiper statistics table;
- different sample counts in the three public matrices.

### Stage D — pilot trees

Estimate, at minimum:

1. a concatenated tree from the conservative high-occupancy set;
2. an ASTRAL tree from its gene trees;
3. a tree from the 531-candidate set after a newly documented orthology review;
4. a copy-aware sensitivity retaining the `coryletorum/vlassovianum` name distinction.

The smoke test should not be used for ancestral flower-colour inference. Its purpose is to validate data compatibility, sample identity and pipeline behaviour.

## Acceptance criteria for scaling beyond 12 samples

The pilot is ready to scale when:

- all 12 BioSamples and runs are downloaded without identity substitution;
- each output sample maps back to one tree code, voucher and public accession;
- public and newly generated recovery summaries are quantitatively compared, not merely described as similar;
- no high-priority name conflict is silently collapsed;
- conservative and copy-aware matrices both run to completion;
- software, target file, filtering and exclusions are fully versioned;
- disagreements with public recovery statistics have an explicit cause or remain flagged;
- the generated tree is treated as a pipeline diagnostic, not the recovered final Moreyra tree.

## Scaling decision

If the 12-sample panel passes, proceed in two steps:

1. all recoverable East/Northeast Asian Moreyra tips;
2. the full public Moreyra sample set only when required to reconstruct the global topology and branch lengths.

The immediate Chapter 2 sequencing priority remains population/morph data for `takaoense`, `pendulum`, `sieboldii`, `kawakamii–tatakaense` and `brevicaule–irumtiense`. This pilot supports the backbone and compatibility layer; it does not replace those population samples.
