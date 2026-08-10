# Moreyra et al. 2025 author-repository and locus-filter audit

Date: 2026-08-10

## Purpose

The Moreyra et al. 2025 paper reports a global *Cirsium* phylogeny based on 350 retained nuclear alignments after Compositae target enrichment, paralog screening, manual gene-tree inspection and missing-data filtering. Recovering the exact 350 loci and final tree is important for EAzami because it would allow new East Asian target-capture data to be processed in a directly compatible matrix.

The journal supplement and PRJNA957074 recover sample membership and raw reads, but they do not contain the final tree or retained-locus list. A separate public repository owned by the corresponding author was therefore audited:

- repository: `ldmoreyra/A-thorny-tale`
- files visible at the repository root on 2026-08-10:
  - `hybpiper_stats_exonerate.tsv`
  - `seq_lengths_exonerate.tsv`
  - `paralog_report.xlsx`

No Newick/Nexus tree, final alignments, per-locus gene-tree archive or explicit 350-locus list was present in that repository.

## Reproducible implementation

Added:

- `analysis/recover_moreyra_author_repository.py`
- `analysis/summarize_moreyra_locus_filter.py`
- `tests/test_recover_moreyra_author_repository.py`
- `tests/test_summarize_moreyra_locus_filter.py`
- `.github/workflows/recover-moreyra-author-repository.yml`
- `data/evidence/moreyra2025_public_locus_filter_summary_2026-08-10.json`

The workflow:

1. downloads the three public files from the author's repository;
2. records Git blob identifiers, file sizes and SHA256 hashes;
3. parses HybPiper recovery statistics;
4. parses the sample-by-locus sequence-length matrix;
5. extracts the XLSX paralog matrix with the Python standard library;
6. reconstructs the warning-count and raw-occupancy portions of the published filtering logic;
7. explicitly leaves manual gene-tree decisions and final 350-locus membership unresolved.

## Source-file provenance

| File | Size | SHA256 |
|---|---:|---|
| `hybpiper_stats_exonerate.tsv` | 28,241 bytes | `deb845dbaef8f3d40155f69f29b7bb590b07af14f915c3937afdff5b00a39bd7` |
| `seq_lengths_exonerate.tsv` | 1,272,484 bytes | `d98168c1fcc204a491a2f4a804635488c748e0a7a7fed1272f8c04e220285eda` |
| `paralog_report.xlsx` | 1,045,621 bytes | `e3cfbfc28c91fa7cd23a2a942865327a9a3dd2f3b25154b9c2872a9af3c08e5d` |

The publisher files themselves and the author's XLSX/TSV files are not committed to EAzami. Derived checksums, summaries, parsing code and decision rules are versioned.

## Sample-matrix differences

The public files do not contain identical sample sets:

- HybPiper statistics: **295 sample rows**;
- sequence-length matrix: **302 biological sample rows**, plus one `MeanLength` reference row;
- paralog report: **280 sample rows**.

Seven samples occur in the sequence-length matrix but not in the HybPiper statistics table:

- `Cirsium-cosmelii_MA425`
- `Cirsium-kiotoense_FJ333`
- `Cirsium-montanum_WG150`
- `Cirsium-scabrum_MA420`
- `Cirsium-valdespinulosum_MA421`
- `Cirsium-vulgare_R114`
- `Echinops-karatavicus_S142`

No HybPiper-statistics sample was absent from the sequence-length matrix.

These differences mean that raw occupancy denominators must be stated explicitly. The current reconstruction uses the 302 biological rows in the public sequence-length matrix and excludes the `MeanLength` reference row.

## Public locus universe

The paper reports **1,064 initially mapped loci**. The two public locus matrices contain **1,061 named locus columns**. The three-locus difference is retained as an unresolved provenance discrepancy rather than silently corrected.

The public paralog workbook contains:

- 280 sample rows;
- 1,061 named loci;
- two trailing blank columns.

## Reconstructed paralog-warning classes

For each locus, a value greater than one in a sample was treated as a HybPiper paralog warning/copy count. The public matrix yields:

| Reproducible class | Loci | Relation to published procedure |
|---|---:|---|
| More than 10 warning samples | **478** | automatic discard class |
| 1–10 warning samples | **307** | manual gene-tree review class |
| No warning samples | **276** | no paralog warning |
| **Total** | **1,061** | public named locus universe |

This reproduces the warning-count partition, not the outcome of manual gene-tree inspection.

## Reconstructed raw occupancy screen

Using positive sequence length in the 302 biological rows as raw sequence recovery:

- loci with occupancy at least 0.80: **1,001**;
- loci with no more than 10 warnings and occupancy at least 0.80: **531**;
- among those 531:
  - no-warning loci: **241**;
  - manual-review loci: **290**.

Thus the public files support a reproducible **531-locus pre-manual candidate set** under warning-count and raw occupancy criteria.

## Why 531 cannot be converted into the exact 350

The paper reports **350 final alignments**, but the remaining reduction cannot be reproduced from the public summary files alone.

For loci with 1–10 paralog warnings, the authors manually inspected gene trees to decide whether multiple sequences represented:

- clear recent intraspecific paralogs;
- interspecific paralogy;
- deeper duplications;
- or orthologous sequences suitable for retention.

The final procedure also used alignment-level missingness and species-presence thresholds. The public repository does not contain:

- the complete per-locus gene trees used for those decisions;
- a log of manual retain/exclude decisions;
- the final 350-locus name list;
- the retained 350 alignments;
- the final concatenated/coalescent Newick files.

Because 290 high-occupancy loci remain in the manual-review class, guessing which of them were retained would falsely convert subjective orthology decisions into a reproducible rule.

## Allowed and disallowed interpretation

### Supported

> Public author-repository summaries reproduce 1,061 named loci and a 531-locus set passing the published automatic warning-count and raw occupancy screens.

### Not supported

> The exact Moreyra 350-locus set has been reconstructed.

No inferred subset in EAzami should be labelled `Moreyra-compatible 350` until the original retained-locus list or full gene-tree/alignment archive is obtained.

## Consequence for new East Asian sequencing

The species-backbone strategy remains Compositae1061-compatible target capture, but matrix naming is revised:

1. **public-universe matrix** — all recoverable public Compositae target loci;
2. **reproducible 531-candidate matrix** — warning count ≤10 and raw occupancy ≥0.80 in the public Moreyra summary;
3. **conservative no-warning matrix** — especially the 241 no-warning, high-occupancy loci;
4. **paralog/homeolog-aware matrix** — retains multi-copy evidence for ASTRAL-Pro/network sensitivity;
5. **exact Moreyra 350 matrix** — reserved name, currently unavailable.

For the first new target-capture samples, all available Compositae1061 loci should be recovered. Analyses can then compare the reproducible public screens and a newly documented orthology workflow rather than pretending to recreate unpublished manual decisions.

## Relationship to the Chapter 2 priority

This audit does not change the main sampling conclusion:

- all active Tier-A focal taxa already have modern species-level placement;
- their main gap is morph/population ancestry;
- RAD-seq or resequencing remains the first new genomic data type for `takaoense`, `pendulum`, `sieboldii`, Arenicola and the Taiwanese polyploid comparison;
- Compositae1061 target capture is reserved for verified transition-critical taxa absent from modern nuclear data.

The original research logic also remains valid: two contrasting focal taxa alone cannot orient a flower-colour transition, so near relatives and population-level states are required.

## Validation

GitHub Actions run `31405513598` completed successfully:

- 11 offline tests passed;
- 3 public source files recovered;
- 295 HybPiper-statistics samples parsed;
- 302 biological sequence-length samples identified;
- 1,061 named loci audited;
- 478 / 307 / 276 warning classes reproduced;
- 1,001 high-occupancy loci identified;
- 531 reproducible pre-manual candidate loci identified;
- exact final 350-locus membership remained explicitly unresolved.

Artifact:

- ID: `9069417959`
- SHA256: `ce149e2740216ad13038ae89ec159d75790146a952a416129908b1e32b5befa2`

## Remaining action

Issue #12 remains open for:

- exact final 350-locus identities;
- retained alignments and gene trees;
- concatenated, coalescent and dated final trees;
- branch lengths and support definitions;
- direct author/data-repository follow-up if these files are not publicly archived.
