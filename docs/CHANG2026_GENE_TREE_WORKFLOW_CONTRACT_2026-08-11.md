# Chang 2026 gene-tree workflow contract

Date: 2026-08-11

## Scope

This document freezes the reproducible input and execution contract for testing the displayed *Cirsium japonicum* var. *takaoense* candidate-regain topology against the seven nearest loss-only alternatives.

The contract covers public-data recovery, voucher/run reconciliation, public-assembly auditing, panel construction, command planning and Snakemake DAG validation. It does **not** claim that raw-read assembly, orthogroup inference or empirical gene-tree inference has already been executed.

## Complete public run universe

Chang et al. (2026) reported 33 transcriptome samples, but they are not all contained in a single BioProject query.

The complete public input set is:

```text
25 runs deposited directly under PRJNA1311153
+ 8 exact public identifiers reused in the supplement
  - 6 SRR run accessions
  - 2 SAMN BioSample accessions
= 33 unique public runs
```

The recovery layer resolves each supplement identifier according to its accession type. A SAMN accession is linked to the exact official SRA run carrying that BioSample; it is not treated as an SRR string.

## Exact reconciliation result

All 33 supplement rows are reconciled one-to-one to official SRA metadata.

- supplement samples: **33**;
- unique matched runs: **33**;
- verified or probable mappings: **33/33**;
- run-assignment collisions: **0**;
- numeric BioSample `isolate` values matching exact supplement vouchers: **33**;
- official SRA `LibraryLayout=PAIRED`: **33/33**.

The supplement raw-read count and SRA `spots` relation remains an independent reconciliation diagnostic. It is not used to infer sequencing layout when official `LibraryLayout` is available.

## Exact var. takaoense anchors

| Code | Voucher | Morph | Run | BioSample | Official layout |
|---|---|---|---|---|---|
| FC | `ccy3559` | BP | `SRR35152718` | `SAMN50798021` | PAIRED |
| TJ | `ccy3807` | BP | `SRR35152736` | `SAMN50798026` | PAIRED |
| NH | `ccy3835` | BP | `SRR35152735` | `SAMN50798027` | PAIRED |
| WY | `ccy3560` | W | `SRR35152717` | `SAMN50798022` | PAIRED |
| FB | `ccy3629` | W | `SRR35152738` | `SAMN50798024` | PAIRED |
| LT | `ccy3839` | W | `SRR35152734` | `SAMN50798028` | PAIRED |

Flower-colour state is joined only after voucher/run identity is resolved. Locality and flower colour do not participate in run matching.

## Public assembly audit

Every reconciled BioSample was queried against current official NCBI TSA and Assembly links.

- samples with a recovered TSA source: **0/33**;
- samples with a recovered Assembly source but no TSA: **0/33**;
- samples requiring de novo assembly from the official SRA run: **33/33**.

For var. *takaoense*, all six samples currently require de novo SRA assembly. This is a statement about the current BioSample/voucher-linked NCBI audit, not proof that no author-held or differently indexed assembly exists.

## Nineteen-sample analysis panel

The first gene-tree analysis uses the six focal samples plus white, coloured and rooting controls.

| Panel component | Samples | Role |
|---|---:|---|
| *C. japonicum* | 2 | coloured root context |
| var. *albescens* | 2 | white sister control |
| var. *takaoense* | 6 | three W and three BP focal tips |
| var. *australe* | 3 | coloured flanking / introgression control |
| var. *fukienense* | 4 | coloured flanking / introgression control |
| *C. lineare* | 2 | outgroup |
| **Total** | **19** | Sinocirsium 17 + outgroup 2 |

Panel invariants:

- unique official runs: **19**;
- official `LibraryLayout=PAIRED`: **19/19**;
- de novo assembly required: **19/19**;
- focal morph counts: **3 W + 3 BP**;
- outgroups: **2 C. lineare samples**.

The supplement names the two root-context samples FKK `ccy4204` and ASO `ccy4220` as var. *japonicum*. For this species-level panel role only, they are mapped to the panel label *C. japonicum*, while the original source name is retained in `source_taxon`. No other variety is collapsed.

## Read-count diagnostics versus official layout

Within the 19-sample panel:

- **9** samples have the exact diagnostic relation `reported raw reads = 2 × SRA spots`;
- **10** samples do not match the reported raw-read count exactly;
- **19/19** are nevertheless officially `LibraryLayout=PAIRED` in SRA runinfo.

The workflow therefore uses the official layout to choose the paired-end command path. Count discrepancies remain visible for provenance review and cannot silently turn a paired run into a single-end run.

## Frozen competing hypotheses

The workflow accepts exactly eight six-tip topology hypotheses:

1. `H_REG_PUBLISHED`: the displayed Figure 1 topology, whose coloured-root optimum contains one loss and one regain;
2. seven `H_LOSS_ONLY_RF4_*` alternatives: every nearest rooted RF-distance-4 topology in which a no-regain history ties the optimum.

The hypotheses are frozen before gene-tree inference. Duplicate topology strings, a missing published hypothesis or any loss-only alternative outside rooted RF distance 4 causes validation failure.

## Layout-aware assembly command contract

The command planner validates the official SRA layout before emitting commands. For the current 19 samples it creates 19 paired-end plans containing:

1. `fasterq-dump --split-files`;
2. compression of both mates;
3. paired-end `fastp` QC and trimming;
4. Trinity de novo assembly;
5. TransDecoder LongOrfs and Predict;
6. stable sample-prefixed protein identifiers.

A future officially `SINGLE` run fails explicitly until a separately tested single-end branch is implemented. It is never coerced into the paired workflow.

Pull-request CI generated **19/19 `planned_dry_run` assembly records** without downloading reads or invoking the external assembly programs.

## Snakemake execution contract

The validated workflow contains the ordered rules:

1. `all`;
2. `assemble_transcriptomes`;
3. `orthofinder`;
4. `prepare_single_copy_orthogroups`;
5. `infer_rooted_gene_trees`;
6. `score_competing_takaoense_histories`.

The contract freezes SHA256 values for:

- the 19-sample panel;
- the eight-hypothesis table;
- the Snakefile;
- all runner scripts;
- all four conda environment specifications.

The latest pull-request validation used **Snakemake 9.23.1** and completed a true six-rule dry-run with **exit status 0**. The dry-run log contains `This was a dry-run` and no missing-input, workflow, rule, syntax or traceback error.

Contract version:

```text
chang2026_gene_tree_workflow_v2_official_layout
```

## What has and has not run

Completed:

- official metadata recovery for all 33 samples;
- one-to-one voucher/run reconciliation;
- official library-layout audit;
- TSA/Assembly audit;
- 19-sample panel construction;
- eight-hypothesis freeze;
- 19 paired-end command plans;
- script, environment and hash validation;
- synthetic end-to-end interface tests;
- Snakemake DAG dry-run.

Not yet executed:

- SRA read download for the 19-run cohort;
- read QC and trimming;
- Trinity assemblies;
- TransDecoder protein prediction;
- OrthoFinder;
- empirical one-to-one orthologue alignments;
- empirical IQ-TREE gene trees;
- empirical gene/quartet concordance;
- empirical introgression or homeolog-sorting tests.

## Next execution stage

On a sufficiently provisioned workstation or HPC system:

```bash
python analysis/validate_chang2026_gene_tree_workflow_contract.py \
  --panel /path/to/chang2026_sinocirsium_gene_tree_panel.csv \
  --hypotheses /path/to/chang2026_takaoense_gene_tree_hypotheses.csv \
  --config-output /path/to/config.json \
  --summary-output /path/to/contract.json

snakemake \
  --snakefile workflow/chang2026_gene_trees/Snakefile \
  --configfile /path/to/config.json \
  --use-conda \
  --cores 32
```

The primary empirical analysis will use complete one-to-one orthologues. Multi-copy and homeolog trees remain a separate reticulation/polyploid sensitivity layer.

## Claim limit

Successful execution can determine whether the displayed nested-BP ordering has broad gene-tree support, whether support is concentrated in a small locus subset, and whether coloured samples show excess affinity to var. *australe* or var. *fukienense*.

It cannot by itself demonstrate functional restoration of anthocyanin production. A demonstrated regain still requires population-aware ancestry plus linked pigment chemistry, floral expression and causal-variant evidence.

## Reproducible files

### Recovery and reconciliation

- `analysis/recover_chang2026_published_runinfo.py`
- `analysis/reconcile_chang2026_complete_runs.py`
- `.github/workflows/reconcile-chang2026-ncbi-runs.yml`

### Panel and hypothesis design

- `analysis/normalize_chang2026_panel_taxa.py`
- `analysis/build_chang2026_gene_tree_panel.py`

### Heavy-workflow planning

- `analysis/run_chang2026_layout_aware_transcriptome_assembly.py`
- `analysis/run_chang2026_transcriptome_assembly.py`
- `analysis/prepare_chang2026_single_copy_orthogroups.py`
- `analysis/run_chang2026_single_copy_gene_trees.py`
- `analysis/score_chang2026_gene_tree_hypotheses.py`
- `analysis/validate_chang2026_gene_tree_workflow_contract.py`
- `workflow/chang2026_gene_trees/Snakefile`
- `workflow/chang2026_gene_trees/envs/*.yml`
- `.github/workflows/build-chang2026-gene-tree-panel.yml`
