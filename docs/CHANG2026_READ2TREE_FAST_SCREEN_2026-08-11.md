# Chang 2026 Read2Tree fast screen

Date: 2026-08-11

## Why add this layer

The full public-data workflow reconstructs the six morph-labelled *Cirsium japonicum* var. *takaoense* transcriptomes by de novo Trinity assembly, protein prediction, OrthoFinder and per-gene trees. That remains the principal reusable gene-tree route, but it is computationally expensive.

Read2Tree provides an independent reference-guided route from raw sequencing reads directly to ortholog alignments and a species tree, bypassing whole-transcriptome assembly, annotation and all-versus-all orthology inference. Its published benchmarks explicitly include Illumina RNA-seq and show that RNA reads can recover phylogenetic signal without de novo assembly.

For Chapter 2 this is useful as a **fast topology screen**: ask whether the six W/BP samples recover the same nested-BP ordering before spending substantial CPU/RAM on all 19 de novo transcriptomes.

This is a sensitivity layer, not a replacement for Trinity/OrthoFinder.

## Reference set

The first source-backed OMA seed contains:

| OMA code | Species | Role |
|---|---|---|
| `CYNCS` | *Cynara cardunculus* var. *scolymus* | closest verified Cardueae reference in the seed |
| `HELAN` | *Helianthus annuus* | Asteraceae reference |
| `DAUCS` | *Daucus carota* subsp. *sativus* | campanulid outgroup |

Use the OMA marker-gene export to obtain a 200- or preferably 400-marker pack from these verified references. The downloaded marker archive must be retained with its date, OMA release/version if exposed by the export, SHA256 and the exact selected genome codes.

Do not substitute an unrecorded marker pack.

## Input samples

Use the same six exact Chang 2026 vouchers already fixed in the gene-tree panel:

- BP: `FC_ccy3559`, `TJ_ccy3807`, `NH_ccy3835`
- W: `WY_ccy3560`, `FB_ccy3629`, `LT_ccy3839`

All six official SRA runs are paired-end. Reuse trimmed reads from the restartable transcriptome pilot when available. This makes the fast screen an additional analysis of the same frozen input material rather than a separately preprocessed dataset.

## Planned execution

Generate a plan with:

```bash
python analysis/build_chang2026_read2tree_pilot.py \
  --panel /path/to/chang2026_takaoense6_assembly_pilot.csv \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_1.csv \
  --reads-root /path/to/chang2026_takaoense_pilot \
  --reads-stage trimmed \
  --marker-dir /path/to/marker_genes \
  --dna-reference /path/to/dna_ref.fa \
  --output-dir /path/to/read2tree_output \
  --plan-outdir /path/to/read2tree_plan \
  --threads 8
```

The generated shell plan runs:

1. Read2Tree `1marker` to prepare the reference marker set;
2. one independent `2map` job for each W/BP sample, with stable `sample_id` supplied explicitly;
3. `3combine` to build the merged alignments;
4. IQ-TREE on `concat_merge_dna.phy` with model selection, ultrafast bootstrap and SH-aLRT.

The nucleotide alignment is primary because the six focal samples are extremely closely related; an amino-acid tree can be retained as a secondary sensitivity analysis.

## Decision rule

### If the DNA tree recovers the displayed nested-BP topology

Proceed immediately to the full Trinity/OrthoFinder gene-tree workflow. Read2Tree then provides independent raw-read support that the displayed topology is not solely an assembly/orthology artefact.

### If Read2Tree instead places W as monophyletic or matches one of the nearest loss-only alternatives

Do not call regain. Prioritize full per-gene analysis and reticulation tests before interpreting the published displayed tree.

### If the six samples are weakly resolved

Treat this as insufficient marker/reference coverage rather than as evidence for a polytomy. Inspect per-marker completeness, reference distance and RNA-expression coverage, then enlarge the OMA reference set or proceed to de novo gene trees.

## Claim limits

Read2Tree is reference guided. Therefore:

- marker recovery depends on which genes are expressed in the leaf RNA libraries;
- missing sequence is not gene loss;
- the method does not test floral anthocyanin expression;
- a concatenated tree cannot by itself distinguish introgression from ancestral polymorphism;
- reference choice can influence which marker sequence is reconstructed;
- the result must be compared against the de novo and copy-aware analyses.

The valid claim is limited to **independent raw-read support, or lack of support, for the six-sample topology**.

## Why not use Mash/k-mer distance as the main shortcut

Alignment-free read distances are attractive computationally, but the Read2Tree benchmark found Mash trees less accurate than Read2Tree and conventional ortholog-based approaches. RNA-seq additionally has strong expression/composition heterogeneity. EAzami therefore uses an ortholog-guided raw-read shortcut rather than treating raw k-mer distance as the primary phylogenetic result.

## Reproducibility

- Read2Tree source is pinned to Git commit `e19ad8f32a438ff7a38d9ee1d41832e1fc326a3c` in the conda environment.
- Current Read2Tree v2 defaults to minimap2 short-read mapping with `-ax sr`; the plan records the preset explicitly.
- The OMA genome codes are frozen in `sampling/read2tree_oma_reference_set_v0_1.csv`.
- No GitHub Actions workflow is added at this stage because PR #1 currently has a large backlog of queued historical workflow runs.

## Files

- `analysis/build_chang2026_read2tree_pilot.py`
- `tests/test_build_chang2026_read2tree_pilot.py`
- `sampling/read2tree_oma_reference_set_v0_1.csv`
- `workflow/chang2026_read2tree/envs/read2tree.yml`
