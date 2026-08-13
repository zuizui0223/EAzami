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
- `analysis/recover_compositae1061_target.py`
- `analysis/recover_compositae1061_target_expanded.py`
- `analysis/run_compositae1061_target_audit.py`
- `analysis/run_compositae1061_target_expanded_audit.py`
- `analysis/audit_cos763_hybpiper_readiness.py`
- `analysis/url_safe_download.py`
- `tests/test_build_moreyra_reanalysis_pilot.py`
- `tests/test_export_moreyra_locus_manifests.py`
- `tests/test_recover_compositae1061_target.py`
- `tests/test_recover_compositae1061_target_expanded.py`
- `tests/test_run_compositae1061_target_audit.py`
- `tests/test_run_compositae1061_target_expanded_audit.py`
- `tests/test_audit_cos763_hybpiper_readiness.py`
- `.github/workflows/prepare-moreyra-reanalysis-pilot.yml`
- `.github/workflows/audit-compositae1061-target.yml`
- `.github/workflows/audit-compositae1061-target-expanded.yml`
- `docs/COS763_HYBPIPER_READINESS_2026-08-11.md`

Generated workflow artifacts include:

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

data/evidence/generated/cos763_hybpiper_readiness/
  cos763_hybpiper_readiness_summary.json
  cos763_sequence_readiness.csv
  cos763_locus_readiness.csv
  cos763_unframed_multisource_mapping_reference.fasta
  cos763_direct_cds_candidate_subset.fasta
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

## Target/reference gate

The public locus-name sets above are analytical manifests. They do not supply the nucleotide or protein target sequences used by HybPiper.

Two reproducible audits searched Mendeley Data, Dryad, GitHub and linked public metadata. Both completed successfully after URL-normalising repository paths, but neither recovered a source-confirmed exact or compatible Moreyra Compositae1061 target/reference FASTA.

Current frozen decision:

```text
exact Moreyra Compositae1061 target recovered: false
source-confirmed compatible target recovered: false
exact target frozen: false
Issue: #16 remains open
```

The expanded audit recovered the foundational Mandel et al. Dryad COS763 alignment archive (`10.5061/dryad.gr93t`, version 1, CC0-1.0). A separate readiness audit found:

| Diagnostic | Result |
|---|---:|
| loci | 763 |
| source sequences | 5,699 |
| source taxa | 16 |
| mapping-reference sequences after length/ambiguity filters | 5,607 |
| direct frame-0 CDS candidate sequences | 410 |
| loci with at least one direct frame-0 CDS candidate | 200/763 |
| complete direct HybPiper nucleotide target ready | **false** |

The COS763 alignments are therefore retained as:

```text
mapping_reference_or_frame-correction_input_only
```

They must not be relabelled as Compositae1061 or supplied as a validated CDS target without explicit reading-frame, orthology and version correction. Full provenance and checksums are recorded in `docs/COS763_HYBPIPER_READINESS_2026-08-11.md`.

### Operational consequence

The 12-sample panel may be downloaded and raw-read integrity may be checked, but an **exact Moreyra HybPiper reproduction remains blocked at target recovery** until the authors or a documented repository provide the target/reference FASTA and version.

A run with another target is still possible, but it must be labelled a compatibility rerun and compare at least two plausible target versions before recovery differences are interpreted biologically.

This target gap does not block the Chang 2026 transcriptome gene-tree workflow, whose primary route is de novo Trinity assembly followed by orthology inference.

## Execution stages outside pull-request CI

### Stage A — raw-read retrieval

Use the generated `download_public_reads.sh` on a local workstation or HPC node with SRA Toolkit. The script:

- uses exact run accessions;
- calls `prefetch` and `fasterq-dump --split-files`;
- compresses output with `pigz` when available;
- does not choose taxonomic synonyms or merge biological samples.

This stage can be used to verify run availability and storage requirements before the target gate is resolved. It does not by itself constitute the Moreyra reconstruction.

### Stage B — target recovery and gated HybPiper execution

For an exact reproduction, first obtain the exact Compositae target/reference file and version used for the original reconstruction. Then run a versioned HybPiper environment and preserve:

- software and target-file versions;
- target-file checksum and source provenance;
- read counts and mapping percentage;
- genes mapped, assembled and recovered at 25/50/75 percent;
- every paralog and chimera warning;
- unstitched sequences and intronerate output where used;
- sample names linked to tree code, BioSample and voucher.

Do not begin by restricting assembly to 241 loci. Recover the available target universe, then subset analytically.

If an alternative target is used before the exact target is recovered, write the run name and manuscript claim as `compatibility rerun`, not `Moreyra exact reconstruction`. The unframed COS763 mapping reference may inform mapping or frame-correction diagnostics but is not a validated direct target.

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

Target identity is a primary explanatory variable, not a technical footnote.

### Stage D — pilot trees

Estimate, at minimum:

1. a concatenated tree from the conservative high-occupancy set;
2. an ASTRAL tree from its gene trees;
3. a tree from the 531-candidate set after a newly documented orthology review;
4. a copy-aware sensitivity retaining the `coryletorum/vlassovianum` name distinction;
5. when an alternative target is used, a target-version sensitivity before biological interpretation.

The smoke test should not be used for ancestral flower-colour inference. Its purpose is to validate data compatibility, sample identity and pipeline behaviour.

## Acceptance criteria for scaling beyond 12 samples

The pilot is ready to scale when:

- all 12 BioSamples and runs are downloaded without identity substitution;
- each output sample maps back to one tree code, voucher and public accession;
- an exact target is frozen, or the run is explicitly defined as a multi-target compatibility analysis;
- public and newly generated recovery summaries are quantitatively compared, not merely described as similar;
- no high-priority name conflict is silently collapsed;
- conservative and copy-aware matrices both run to completion;
- software, target file, filtering and exclusions are fully versioned;
- disagreements with public recovery statistics have an explicit cause or remain flagged;
- the generated tree is treated as a pipeline diagnostic, not the recovered final Moreyra tree.

## Scaling decision

If the 12-sample panel passes the target-aware criteria, proceed in two steps:

1. all recoverable East/Northeast Asian Moreyra tips;
2. the full public Moreyra sample set only when required to reconstruct the global topology and branch lengths.

The immediate Chapter 2 sequencing priority remains population/morph data for `takaoense`, `pendulum`, `sieboldii`, `kawakamii–tatakaense` and `brevicaule–irumtiense`. This pilot supports the backbone and compatibility layer; it does not replace those population samples.
