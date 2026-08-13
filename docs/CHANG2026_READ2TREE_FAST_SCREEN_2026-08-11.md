# Chang 2026 var. *takaoense* Read2Tree fast topology screen

Date: 2026-08-11

## Goal

Use the six published morph-labelled *Cirsium japonicum* var. *takaoense* RNA-seq datasets for an assembly-free, reference-guided topology sensitivity screen before committing to the heavier Trinity/TransDecoder/OrthoFinder workflow.

This is an **independent sensitivity analysis**, not a replacement for the de novo gene-tree workflow.

## Frozen six samples

The active versioned panel is:

- `sampling/chang2026_takaoense6_read2tree_panel_v1.csv`

It is regenerated conceptually from the exact Figure 1 + NCBI evidence and is machine-validated against:

- `data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv`

The six samples are:

- FC `ccy3559` — BP — `SRR35152718`
- TJ `ccy3807` — BP — `SRR35152736`
- NH `ccy3835` — BP — `SRR35152735`
- WY `ccy3560` — W — `SRR35152717`
- FB `ccy3629` — W — `SRR35152738`
- LT `ccy3839` — W — `SRR35152734`

All six are official paired-end runs. `analysis/validate_chang2026_takaoense6_read2tree_panel.py` stops the workflow if run, BioSample, voucher or morph no longer agrees with the direct evidence table.

## Read2Tree method

Read2Tree maps sequencing reads directly to reference orthologous groups, reconstructs sample sequences, aligns the marker genes and can infer a species tree without the normal sequence of de novo transcriptome assembly, gene prediction and all-vs-all orthology inference.

For this screen:

```text
trimmed paired RNA-seq reads
→ Read2Tree marker mapping
→ reconstructed marker sequences
→ concatenated nucleotide alignment
→ IQ-TREE
→ focal-monophyly gate
→ corrected frozen 8-topology scoring
```

Nucleotide inference is used because the focal samples are very closely related.

## OMA reference set

The active reference manifest is:

- `sampling/read2tree_oma_reference_set_v0_2.csv`

It is pinned to the **May 2026 OMA release** and exactly three reference genomes:

- `CYNCS` — *Cynara cardunculus* var. *scolymus* — Cardueae anchor;
- `HELAN` — *Helianthus annuus* — Asteraceae reference;
- `DAUCS` — *Daucus carota* subsp. *sativus* — intended external root.

The older `v0_1` seed is superseded and must not be used for a new run.

## Two independent OMA marker profiles

Marker choice is now an explicit sensitivity dimension rather than one hidden external input.

Definitions are versioned in:

- `sampling/read2tree_oma_marker_profiles_v0_1.csv`

### Profile A — automated static broad-conservation 400

Preferred first screen:

`oma_static_broadconservation400_may2026_v1`

Implementation:

- `analysis/build_read2tree_oma_static_marker_pack.py`
- `docs/READ2TREE_OMA_STATIC_MARKER_RECONSTRUCTION_2026-08-11.md`
- `workflow/chang2026_read2tree/prepare_static_profile.sh`

The builder uses the pinned May 2026 `oma-groups.txt.gz`, requires the live OMA API to report the same release, identifies strict groups containing exactly one CYNCS, HELAN and DAUCS entry, ranks qualifying groups by total OMA-group membership and a stable membership fingerprint, and selects 400 groups.

Only the selected 1,200 protein records are requested through the OMA bulk API. The 5.6 GB complete protein FASTA and 8.6 GB complete CDS FASTA are not required.

This selection is fully specified and reproducible but **is not claimed to reproduce the Browser marker-ranking algorithm**.

### Profile B — OMA Browser export 400

Independent marker-selection sensitivity:

`oma_browser_export400_may2026_v1`

Use the OMA Browser with:

```text
minimum fraction of covered species = 1.0
maximum number of markers = 400
```

The Browser documents export of the most complete OMA Groups for selected species. Its exact tie/ranking behavior among groups that all have 100% coverage of these three references is not silently substituted for the static profile.

### Shared marker-pack contract

Both profiles must pass:

- `analysis/validate_read2tree_oma_marker_pack.py`
- `docs/READ2TREE_OMA_MARKER_CONTRACT_2026-08-11.md`

A successful pack must contain exactly 400 paired AA/DNA marker groups, one sequence from each of the three reference genomes per marker, frame-compatible coding DNA, deterministic hashes and `execution_allowed: true` in `marker_pack_contract.json`.

The plan builder:

- `analysis/build_chang2026_read2tree_pilot.py`

requires that contract and rechecks its version, OMA release, reference codes, marker count, normalized file counts and `dna_ref.fa` SHA256 before generating any mapping command.

## Corrected hypothesis set

The output tree is compared with the frozen current scientific input:

- `analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv`

This contains:

1. `H_REG_PUBLISHED`, the exact displayed Figure 1 candidate-regain topology;
2. the **corrected** seven nearest rooted RF=4 no-regain alternatives.

The valid nearest null IDs are:

- T0403
- T0409
- T0755
- T0846
- T0894
- T0901
- T0944

The previous stale T0064/T0066/T0070/T0079/T0083/T0102/T0375 set is superseded and must not be used.

The frozen hypothesis CSV is additionally protected by byte-level SHA256 and by `analysis/validate_chang2026_takaoense_hypothesis_freeze.py`.

## Focal-monophyly gate

The Read2Tree tree contains the OMA reference taxa. It is not legitimate to delete them first and then ask which six-tip topology looks best.

The scorer therefore requires:

1. all six focal samples appear exactly once;
2. the six focal samples form a clade relative to the OMA references in the raw tree;
3. after support collapse, focal monophyly is retained;
4. only then may the reference tips be pruned and the six-tip topology compared with the eight frozen hypotheses.

If an OMA reference enters the focal clade, the result is `focal_not_monophyletic_raw_tree` and the colour-history hypotheses are **not scored**.

## Support sensitivity

Evaluate the topology at support thresholds:

```text
0 / 50 / 70 / 90
```

A topology that supports the candidate regain only when weak branches are retained is weaker evidence than one that remains candidate-regain-best after support collapse.

## Marker-profile sensitivity

The scientifically useful comparison is not “which marker set gives the preferred tree?” but whether the biological classification is stable across independently constructed references.

### Concordant result

If static400 and Browser400 both rank the displayed candidate-regain history best across comparable support thresholds, marker-selection dependence is reduced.

### Discordant result

If the two profiles disagree, do not choose the desired answer. Audit:

- per-marker mapping completeness;
- reconstructed sequence length and missingness;
- reference distance;
- which markers support each topology;
- support collapse behavior.

Then proceed to the de novo gene-tree workflow with the marker conflict recorded explicitly.

## One-command preparation for static400

With trimmed FASTQ already produced by the restartable runner:

```bash
READS_ROOT=/path/to/chang2026_takaoense_pilot \
RESULT_ROOT=/path/to/read2tree_static400 \
bash workflow/chang2026_read2tree/prepare_static_profile.sh
```

The script performs:

```text
six-sample evidence validation
→ May2026 static marker selection
→ 1,200 selected OMA sequence retrieval
→ standard marker-pack validation
→ Read2Tree command-plan generation
```

It does **not** automatically execute the heavy mapping/tree step. The generated `run_read2tree_fast_screen.sh` must be launched explicitly.

## Relationship to the heavier analysis

### If both Read2Tree profiles support the displayed topology

Proceed to the 19-sample de novo workflow to ask whether the same result is distributed across independent gene trees and whether particular loci or flanking Sinocirsium lineages drive discordance.

### If either profile supports a nearest no-regain topology

The displayed-tree candidate regain becomes weaker and the heavy workflow should prioritize the conflict rather than assuming the displayed order.

### If profiles disagree, are unresolved or focal samples are not monophyletic

Do not force a regain/loss classification. Continue with de novo orthogroup/gene-tree and network analyses because the reference-guided concatenated screen is insufficient.

## Claim limit

This screen does **not** test flower-specific anthocyanin expression because Chang 2026 RNA was sampled from leaves. It also does not distinguish introgression from incomplete lineage sorting or ancestral polymorphism, and it cannot establish functional reactivation of the anthocyanin pathway.

Its purpose is narrower: obtain fast, reproducible, independently marker-weighted empirical evidence on the six-tip topology before spending more computation on full transcriptome reconstruction.
