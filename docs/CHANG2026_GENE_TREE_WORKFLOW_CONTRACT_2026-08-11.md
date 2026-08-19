# Chang 2026 gene-tree workflow contract

Original freeze date: 2026-08-11  
Canonical runner update: 2026-08-14

## Scope

This contract defines the reproducible public-data workflow for testing the displayed *Cirsium japonicum* var. *takaoense* candidate-regain topology against the seven nearest loss-only alternatives.

It covers public-run recovery, voucher/run reconciliation, public-assembly auditing, the 19-sample panel, the eight-hypothesis table, the single canonical restartable transcriptome runner and the downstream Snakemake DAG. It does **not** claim that the heavy transcriptome, orthology or empirical gene-tree computation has already been executed.

## Public input and identity gates

Chang 2026 has **33 unique public transcriptome runs** after supplement identifiers are resolved to official SRA records. The current reconciliation requires:

- 33/33 verified or probable mappings;
- 33 unique matched runs;
- zero run-assignment collisions;
- official SRA `LibraryLayout=PAIRED` for all 33 runs.

The six directly morph-linked var. *takaoense* anchors remain:

| Code | Voucher | Morph | Run | BioSample |
|---|---|---|---|---|
| FC | `ccy3559` | BP | `SRR35152718` | `SAMN50798021` |
| TJ | `ccy3807` | BP | `SRR35152736` | `SAMN50798026` |
| NH | `ccy3835` | BP | `SRR35152735` | `SAMN50798027` |
| WY | `ccy3560` | W | `SRR35152717` | `SAMN50798022` |
| FB | `ccy3629` | W | `SRR35152738` | `SAMN50798024` |
| LT | `ccy3839` | W | `SRR35152734` | `SAMN50798028` |

Flower colour is joined only after voucher/run identity is fixed. Locality and colour do not participate in run matching.

The current NCBI TSA/Assembly audit recovered no linked public assembly for these 33 BioSamples, so the current workflow treats all 33 as de-novo-from-SRA candidates. This is an audit result, not proof that no author-held or differently indexed assembly exists.

## Nineteen-sample analysis panel

The first gene-tree panel is:

| Component | Samples | Role |
|---|---:|---|
| *C. japonicum* | 2 | coloured root context |
| var. *albescens* | 2 | white sister control |
| var. *takaoense* | 6 | focal BP3/W3 |
| var. *australe* | 3 | coloured flanking / introgression control |
| var. *fukienense* | 4 | coloured flanking / introgression control |
| *C. lineare* | 2 | outgroup |
| **Total** | **19** | Sinocirsium 17 + outgroup 2 |

Hard panel invariants:

- 19 unique official runs;
- 19/19 official `LibraryLayout=PAIRED`;
- all 19 de novo under the current public-assembly audit;
- focal morph balance exactly **BP=3 / W=3**;
- exactly two *C. lineare* outgroups.

Read-count discrepancies remain provenance diagnostics. They never override official SRA `LibraryLayout`.

## Frozen competing hypotheses

The workflow accepts exactly eight six-tip hypotheses:

1. `H_REG_PUBLISHED`, the displayed topology whose coloured-root minimum-change reconstruction contains one loss and one candidate regain;
2. seven `H_LOSS_ONLY_RF4_*` nearest rooted RF-distance-4 alternatives in which a no-regain history ties the optimum.

The hypotheses are frozen before empirical gene-tree inference. Duplicate topology strings, a missing published hypothesis or a loss-only alternative outside the frozen class fails validation.

## Canonical transcriptome runner

As of 2026-08-14 there is **one supported assembly entry point**:

`analysis/run_chang2026_restartable_transcriptome_assembly.py`

The former `run_chang2026_layout_aware_transcriptome_assembly.py` adapter and `run_chang2026_transcriptome_assembly.py` paired runner were retired after their live validation logic was moved into the canonical restartable runner.

The canonical runner directly enforces:

- expected panel size;
- unique sample IDs and official runs;
- verified/probable run reconciliation;
- `de_novo_required=true` and `preferred_sequence_source == matched_run`;
- official SRA layout present and **PAIRED-only**;
- for the six-sample pilot, exactly six `focal_colour_morph` rows and exactly **BP3/W3**;
- stable sample-ID subset selection.

A future official `SINGLE` run fails explicitly until a separately validated single-end path exists. It is never coerced into paired-end execution.

## Restartable execution order

The canonical runner uses:

```text
prefetch
  -> vdb-validate
  -> fasterq-dump --split-files with explicit threads and scratch
  -> pigz
  -> paired fastp
  -> Trinity with working directory retained and no --full_cleanup
  -> TransDecoder.LongOrfs
  -> TransDecoder.Predict --single_best_only
  -> stable sample_id-prefixed protein FASTA
```

Interrupted downloads/steps can reuse validated completed state. Partial paired FASTQ state is an error rather than an implicit overwrite.

## Snakemake DAG

The validated rule order remains:

1. `all`
2. `assemble_transcriptomes`
3. `orthofinder`
4. `prepare_single_copy_orthogroups`
5. `infer_rooted_gene_trees`
6. `score_competing_takaoense_histories`

The workflow contract hashes only the scripts that are part of the supported DAG interface:

- `run_chang2026_restartable_transcriptome_assembly.py`
- `prefix_fasta_headers.py`
- `prepare_chang2026_single_copy_orthogroups.py`
- `run_chang2026_single_copy_gene_trees.py`
- `score_chang2026_gene_tree_hypotheses.py`

It also freezes the panel, hypotheses, Snakefile and four conda environment specifications.

Current contract version:

```text
chang2026_gene_tree_workflow_v4_canonical_restartable_sra
```

CI performs offline unit/integration tests and a real Snakemake dry-run, but does not run the heavy public-read assembly or empirical phylogenomics.

## What is complete

- complete public-run recovery/reconciliation contract;
- official library-layout gate;
- current TSA/Assembly audit;
- 19-sample panel construction;
- BP3/W3 six-sample pilot freeze;
- eight competing topology hypotheses;
- canonical restartable command planning;
- single-runner workflow hashing;
- synthetic end-to-end interfaces;
- Snakemake DAG dry-run contract.

## What remains empirical

- actual SRA download for the analysis cohort;
- fastp/Trinity/TransDecoder execution;
- OrthoFinder;
- empirical one-to-one orthologue alignments;
- empirical IQ-TREE gene trees and concordance;
- copy-aware/homeolog/reticulation sensitivities;
- population ancestry and molecular anthocyanin mechanism.

The primary gene-tree analysis should use complete one-to-one orthologues. Multi-copy/homeolog trees remain a separate polyploid/reticulation sensitivity layer rather than being mixed into the primary topology count.

## Claim limit

A completed gene-tree analysis can test whether the displayed nested-BP ordering has broad gene-tree support, whether support is concentrated in a small locus subset, and whether coloured samples show excess affinity to var. *australe* or var. *fukienense*.

It cannot by itself demonstrate functional restoration of anthocyanin production. A demonstrated regain still requires population-aware ancestry plus linked pigment chemistry, floral expression and causal-variant evidence.

## Reproducible files

### Recovery and reconciliation

- `analysis/recover_chang2026_published_runinfo.py`
- `analysis/reconcile_chang2026_complete_runs.py`

### Panel and hypotheses

- `analysis/normalize_chang2026_panel_taxa.py`
- `analysis/build_chang2026_gene_tree_panel.py`

### Heavy execution and scoring

- `analysis/run_chang2026_restartable_transcriptome_assembly.py`
- `analysis/prefix_fasta_headers.py`
- `analysis/prepare_chang2026_single_copy_orthogroups.py`
- `analysis/run_chang2026_single_copy_gene_trees.py`
- `analysis/score_chang2026_gene_tree_hypotheses.py`
- `analysis/validate_chang2026_gene_tree_workflow_contract.py`
- `workflow/chang2026_gene_trees/Snakefile`
- `workflow/chang2026_gene_trees/envs/*.yml`
- `.github/workflows/build-chang2026-gene-tree-panel.yml`
- `.github/workflows/validate-chang2026-restartable-pilot.yml`
