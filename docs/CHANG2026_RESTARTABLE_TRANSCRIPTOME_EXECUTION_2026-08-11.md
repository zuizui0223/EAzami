# Chang 2026 restartable transcriptome execution contract

Date: 2026-08-11

## Purpose

This contract turns the validated Chang 2026 public-transcriptome panel into an auditable heavy-compute workflow. It is designed first for the six published *Cirsium japonicum* var. *takaoense* W/BP samples and then for the 19-sample Sinocirsium control panel.

The biological goal is to replace uniform weighting of 945 possible six-tip resolutions with empirical transcriptome gene-tree evidence. This is an ancestry/topology test, not a direct demonstration of anthocyanin-pathway reactivation.

## Why the previous dry-run execution path was revised

Two execution details were invisible to the Snakemake dry-run:

1. Trinity was called with `--full_cleanup` while the runner expected `<output_dir>/Trinity.fasta`. Full cleanup removes the working directory and changes the retained FASTA location, conflicting with the expected path and restart strategy.
2. SRA conversion was started directly from `fasterq-dump`. The heavy runner now uses a restartable `prefetch` accession directory, validates it with `vdb-validate`, and converts the local accession using explicit output and scratch paths.

The frozen input identities, official `LibraryLayout=PAIRED`, six-sample morph balance and eight topology hypotheses are unchanged.

## Restartable stage order

```text
prefetch
  -> vdb-validate
  -> fasterq-dump --split-files -e <threads> -t <scratch>
  -> pigz
  -> fastp
  -> Trinity (working directory retained; no --full_cleanup)
  -> TransDecoder.LongOrfs
  -> TransDecoder.Predict --single_best_only
  -> stable sample_id-prefixed protein FASTA
  -> mechanical QC
```

The runner writes stage-completion markers and GNU `time -v` diagnostics where available. `prefetch` is intentionally repeatable so an interrupted public-data download can resume. A partial paired FASTQ state is treated as an error rather than being overwritten silently.

## First sample

The first execution sample is chosen mechanically as the focal library with the smallest precomputed working-disk requirement:

- sample: `NH_ccy3835`
- morph: BP
- run: `SRR35152735`
- official layout: PAIRED
- spots: 16,254,562
- paired reads: 32,509,124
- sequenced bases: 4.909 Gb
- deposited SRA: 1.582 GiB
- estimated maximum uncompressed FASTQ: 13.7 GiB
- planning working disk: 34.3 GiB
- first-run preflight gate: 50 GiB free

The first run uses one sample at a time, 16 Trinity threads and 96 GiB Trinity memory; the provided Slurm template requests 120 GiB total job memory to retain overhead. SRA and raw FASTQ are preserved after this first success so measured disk usage can replace planning estimates.

## Mechanical QC gate

The first sample proceeds to the remaining five focal samples only after all of the following hold:

1. fastp input read count equals `2 x` official SRA spots;
2. reads remain after fastp;
3. `Trinity.fasta` is non-empty;
4. TransDecoder peptide FASTA is non-empty;
5. all prefixed protein headers begin with the stable `sample_id|` prefix.

The following are reported but have no post-hoc pass/fail threshold at this stage:

- read retention, Q20, Q30 and GC;
- transcript count, total bases, N50, median and maximum length;
- peptide count and length distribution;
- Trinity elapsed time and peak RSS where GNU time is available.

This avoids dropping a W or BP sample simply because an assembly-quality metric is lower than the others.

## Execution bundle

Generate the bundle from the source-backed six-sample panel and resource table:

```bash
python analysis/build_chang2026_hpc_pilot_bundle.py \
  --pilot-panel chang2026_takaoense6_assembly_pilot.csv \
  --resource-plan chang2026_sample_resource_plan.csv \
  --outdir chang2026_hpc_pilot_bundle
```

The bundle contains local and Slurm scripts, input hashes, resource metadata and a dry-run script. The scripts create/use `workflow/chang2026_gene_trees/envs/assembly.yml`, record the git commit and input hashes, run tool/disk preflight, execute `NH_ccy3835`, and immediately run mechanical QC.

## Full Snakemake route

The production `workflow/chang2026_gene_trees/Snakefile` now uses `analysis/run_chang2026_restartable_transcriptome_assembly.py` for the 19-sample assembly rule. When `keep_raw_reads=false`, full-panel execution may delete prefetched SRA and raw FASTQ only after a sample has successfully produced its stable prefixed proteome. The dedicated first-sample bundle does not delete them.

## Claim boundary

Successful completion of this execution contract establishes a reproducible EAzami reanalysis of public Chang RNA-seq data. It does not by itself establish:

- that the transcriptome is complete;
- that an orthogroup is a true single-copy orthologue in a polyploid/reticulate lineage;
- that candidate coloured ancestry is introgression rather than incomplete lineage sorting;
- that a white lineage genetically lost and then molecularly reactivated anthocyanin biosynthesis.

Those require the downstream gene-tree/copy-aware sensitivity and, ultimately, population ancestry plus linked pigment, floral expression, DNA and ploidy data.
