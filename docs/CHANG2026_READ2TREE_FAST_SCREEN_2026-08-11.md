# Chang 2026 var. *takaoense* Read2Tree fast topology screen

Date: 2026-08-11

## Goal

Use the six published morph-labelled *Cirsium japonicum* var. *takaoense* RNA-seq datasets for an assembly-free, reference-guided topology sensitivity screen before committing to the heavier Trinity/TransDecoder/OrthoFinder workflow.

This is an **independent sensitivity analysis**, not a replacement for the de novo gene-tree workflow.

## Frozen six samples

The input remains the exact Figure 1 morph-linked SRA set:

- FC `ccy3559` — BP — `SRR35152718`
- TJ `ccy3807` — BP — `SRR35152736`
- NH `ccy3835` — BP — `SRR35152735`
- WY `ccy3560` — W — `SRR35152717`
- FB `ccy3629` — W — `SRR35152738`
- LT `ccy3839` — W — `SRR35152734`

All six are official paired-end runs.

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

## Marker export is now contract-gated

Do not pass an arbitrary marker directory to Read2Tree.

Export from the OMA Browser with:

```text
minimum fraction of covered species = 1.0
maximum number of markers = 400
```

Then validate the downloaded archive using:

- `analysis/validate_read2tree_oma_marker_pack.py`
- `docs/READ2TREE_OMA_MARKER_CONTRACT_2026-08-11.md`

A successful pack must contain exactly 400 paired AA/DNA marker groups, one sequence from each of the three reference genomes per marker, frame-compatible coding DNA, deterministic hashes and `execution_allowed: true` in `marker_pack_contract.json`.

The plan builder now **requires** that contract:

```text
analysis/build_chang2026_read2tree_pilot.py
```

It rechecks the contract version, OMA release, reference codes, export settings, marker count, normalized file counts and `dna_ref.fa` SHA256 before generating any mapping command.

## Corrected hypothesis set

The output tree is compared with the frozen current scientific input:

- `analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv`

This contains:

1. `H_REG_PUBLISHED`, the exact displayed Figure 1 candidate-regain topology;
2. the **corrected** seven nearest rooted RF=4 no-regain alternatives.

The previous stale T0064/T0066/T0070/T0079/T0083/T0102/T0375 set is superseded and must not be used.

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

## Relationship to the heavier analysis

### If Read2Tree supports the displayed topology

Proceed to the 19-sample de novo workflow to ask whether the same result is distributed across independent gene trees and whether particular loci or flanking Sinocirsium lineages drive discordance.

### If Read2Tree supports a nearest no-regain topology

The displayed-tree candidate regain becomes substantially weaker and the heavy workflow should prioritize the conflict rather than assuming the displayed order.

### If Read2Tree is unresolved or focal samples are not monophyletic

Do not force a regain/loss classification. Continue with de novo orthogroup/gene-tree and network analyses because the reference-guided concatenated screen is insufficient.

## Claim limit

This screen does **not** test flower-specific anthocyanin expression because Chang 2026 RNA was sampled from leaves. It also does not distinguish introgression from incomplete lineage sorting or ancestral polymorphism, and it cannot establish functional reactivation of the anthocyanin pathway.

Its purpose is narrower: obtain a fast, reproducible, independently constructed empirical weight on the six-tip topology before spending more computation on full transcriptome reconstruction.
