# 20-tip Compositae1061 compatibility tree — HPC execution runbook

Date: 2026-08-12

## Scope and claim boundary

This is the **preflight branch-length compatibility tree** for the current fixed-state flower-colour atlas:

- 20 species-level tips;
- C=17 / W=3;
- 13 leaf-RNA-seq tips from Chang 2025/2026;
- 7 target-capture tips from Moreyra 2025;
- all primary runs paired-end and frozen by an official-SRA evidence contract.

The original public Compositae1061 HybPiper reference is source-frozen at SHA256:

`77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c`

This is an explicit **compatibility reanalysis**, not an exact Moreyra 2025 reproduction. Moreyra's augmented *Cirsium tioganum* reference, exact retained 350-locus list and final machine-readable trees remain unrecovered.

A successful 20-tip tree does **not** unlock empirical flower-colour ER/ARD fitting. The present atlas is still W=3. After two new fixed-white lineages pass their promotion gate, a final 22-species-tip C17/W5 tree must be rebuilt before the rate fit can run.

## One-command bundle preparation

From a checkout of the PR branch:

```bash
bash workflow/colour_rate_comp1061/prepare_hpc_bundle.sh /path/to/colour_rate_comp1061_hpc_bundle
```

The wrapper:

1. verifies the frozen 20-run bridge contract;
2. embeds the frozen Compositae1061 locus-set contract;
3. builds restartable read/HybPiper/QC Slurm scripts;
4. adds current-paralog-aware alignment/tree/acceptance stages;
5. checks every generated shell script with `bash -n`;
6. asserts the bundle remains `branch_length_tree_completed=false` and `rate_fit_execution_allowed=false` before external execution.

No SRA download or heavy phylogenomic computation occurs while preparing the bundle.

## Stage A — primary BWA compatibility recovery

BWA is the primary mapping mode because the original Compositae1061 workflow used HybPiper with BWA. The present environment uses HybPiper 2.3.4, so this remains a compatibility analysis rather than a historical software-stack reproduction.

On Slurm:

```bash
cd /path/to/colour_rate_comp1061_hpc_bundle
bash submit_bwa_chain.sh
```

This submits dependency-linked jobs for:

1. `00_prepare_inputs_slurm.sh`
   - recover and SHA-validate the original 1,061-locus reference;
   - reconstruct the public Moreyra 1,061 / 531 / 241 locus sets from the source audit;
2. `01_fetch_trim_slurm.sh`
   - 20-way array;
   - `prefetch -> vdb-validate -> fasterq-dump -> pigz -> fastp`;
3. `02_hybpiper_bwa_slurm.sh`
   - 20-way HybPiper 2.3.4 BWA recovery;
   - exonic output only (`--no_intronerate`);
4. `03_retrieve_qc_slurm.sh`
   - HybPiper stats;
   - recovered DNA FASTAs;
   - current paralog report.

All stages are restart-aware. Existing complete trimmed FASTQs and compressed HybPiper sample outputs are reused rather than silently replaced.

## Stage B — current 20-tip QC becomes a hard tree-input gate

The tree chain no longer assumes that a locus clean in the public Moreyra analysis is also clean in the present mixed RNA-seq/target-capture panel.

After the BWA QC job completes, submit:

```bash
MODE=bwa bash submit_tree_chain.sh
```

`04_prepare_tree_inputs_slurm.sh` first runs `analysis/summarize_colour_rate_comp1061_qc.py` against the **current** 20 recovered samples. Starting from the frozen public 241 no-warning/high-occupancy loci, a locus is admitted only when:

- current focal occupancy >=0.80, i.e. >=16/20 focal taxa;
- no current focal sample has a HybPiper >1-copy/paralog warning at that locus.

The current clean locus list is written under:

`results/colour_rate_comp1061/tree_bwa/current_qc/current_conservative_241_loci.txt`

A minimum of 100 current-qualified loci is a predeclared engineering launch gate. Fewer than 100 stops the tree chain rather than relaxing filters post hoc.

The QC output also preserves RNA-seq versus target-capture recovery fractions so cross-library missingness can be inspected rather than hidden.

## Stage C — alignment and trees

For the current-qualified subset:

5. `05_align_loci_slurm.sh`
   - MAFFT per locus;
   - focal sequences plus original Compositae1061 reference sequences;
   - `lett` and `sunf` are required on every admitted locus;
   - `saff` is retained wherever the original reference provides it;
6. `06_gene_trees_slurm.sh`
   - per-locus IQ-TREE ML;
   - ModelFinder;
   - UFBoot 1000;
   - SH-aLRT 1000;
   - root definition remains `OUTGROUP_lett,OUTGROUP_sunf`;
   - optional `OUTGROUP_saff` is a near Cardueae reference, not a root-defining taxon;
7. `07_concat_tree_slurm.sh`
   - deterministic concatenation of exactly the admitted locus set;
   - explicit gap padding for missing focal sequences;
   - if `OUTGROUP_saff` occurs in at least one admitted alignment it is retained as a concatenated reference tip and gap-padded at loci where it is absent;
   - partition table retained;
   - concatenated IQ-TREE ML tree with branch lengths in substitutions/site, rooted with `lett+sunf`.

This separates two roles that must not be conflated:

- **root outgroups:** `OUTGROUP_lett`, `OUTGROUP_sunf`;
- **near-reference/monophyly anchor:** optional `OUTGROUP_saff`.

The concatenated ML branch lengths are the candidate scale for the later binary Mk analysis. Gene-tree/topology disagreement remains a sensitivity and is not converted into invented support or branch lengths.

## Stage D — branch-length tree acceptance

`08_accept_tree_slurm.sh` creates:

- `tip_map.csv`;
- `tree_provenance.json`;
- `tree_acceptance.json` only after validation.

`analysis/validate_colour_atlas_branch_length_tree.py` requires:

- a real machine-readable Newick tree;
- finite branch lengths on all non-root edges and at least one positive empirical length;
- tree SHA256 matching the provenance record;
- one-to-one mapping for every currently eligible atlas taxon;
- explicit branch-length interpretation, rooting, support semantics and pipeline provenance;
- `OUTGROUP_lett` and `OUTGROUP_sunf` present as the declared root-outgroup set;
- any retained `OUTGROUP_saff` explicitly declared as an additional reference;
- root outgroups to be a subset of the full declared reference set;
- no undeclared extra tips;
- **all focal Cirsium atlas tips monophyletic relative to every declared reference tip**.

If `lett`, `sunf`, or retained `saff` enters the focal clade, the tree is blocked. It is not pruned away after the fact to manufacture an acceptable *Cirsium* tree.

Tree acceptance is structural/scientific input validation only. It does not mean ARD is preferred over ER and does not satisfy the independent W>=5 state gate.

## Mapping-mode sensitivity

The same bundle contains a BLASTx/default-mapping sensitivity:

```bash
bash submit_blastx_chain.sh
MODE=blastx bash submit_tree_chain.sh
```

The fetch/trim stage is checkpointed, so already completed reads are reused. BWA remains primary; BLASTx is not selected post hoc according to which tree gives the preferred colour history.

A direct mapping-mode disagreement is a sensitivity result to report, not a reason to choose the more convenient topology.

## Expected important outputs

Primary BWA run:

```text
results/colour_rate_comp1061/
  reads/
  hybpiper_bwa/
  qc_bwa/
  tree_bwa/
    current_qc/
      current_qc_summary.json
      current_conservative_241_loci.txt
      locus_qc.csv
      sample_qc.csv
    inputs/
      eligible_loci.txt
      loci_unaligned/
      tree_input_summary.json
    alignments/
    gene_trees/
    concat/
      concat.fasta
      partitions.csv
      concat_summary.json
      colour_rate_comp1061_concat.treefile
    tip_map.csv
    tree_provenance.json
    tree_acceptance.json
```

The equivalent BLASTx path is under `qc_blastx/` and `tree_blastx/`.

## What this run can answer

If the real BWA tree passes all gates, it provides:

- an independently reconstructed common-locus branch-length tree for the current 20 fixed-state taxa;
- a preflight test of whether Chang leaf RNA-seq and Moreyra target-capture samples can coexist in the same conservative Compositae1061 tree;
- a direct placement of *C. brevicaule* and *C. irumtiense* in the broader colour atlas under an explicit branch-length model;
- a reference-intrusion diagnostic using distant and, where available, near Cardueae source references;
- a branch-length framework that can be extended to the two additional fixed-white taxa once their nuclear data are recovered.

It does **not** yet estimate empirical C->W versus W->C transition rates, because W=3 remains below the predeclared state gate.

## Final promotion after the two new fixed-white taxa

For *C. boninense* and *C. wulongense*:

1. require >=2 independent voucher/flower-colour-linked nuclear samples per species;
2. use a multi-individual placement tree to verify identity and concordance;
3. choose one species representative using the frozen QC rule, never the preferred topology/colour result;
4. rebuild the same common-locus branch-length analysis as a **22 species-tip C17/W5 tree**;
5. rerun the branch-length acceptance gate against the promoted atlas;
6. only then allow `analysis/fit_binary_flower_colour_mk_models.py` to fit ER and ARD.

The ER/ARD fitter itself is gated and currently refuses the real C17/W3 data.

## Current external dependencies

The remaining heavy step is actual Slurm/HPC execution. GitHub Actions only validates inputs, code, generated scripts and scientific stop rules; it does not claim the 20-sample HybPiper/tree computation has been performed.
