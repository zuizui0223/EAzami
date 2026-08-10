# Chang et al. 2026 public RNA-seq run and assembly audit

Date: 2026-08-11

## Purpose

The six var. *takaoense* Figure 1 tips are now assigned directly to flower-colour morphs and their published topology supports a locally robust candidate regain. The next empirical question is whether public sequence material is sufficient to reconstruct gene trees and test alternative histories.

This audit resolves two separate questions:

1. Which official `PRJNA1311153` SRA run belongs to each of the 33 supplement samples?
2. Does NCBI already expose a reusable TSA or Assembly record, or is de novo transcriptome assembly required?

## Source tables

The reconciliation uses:

- the official Chang 2026 supplementary sample/voucher table;
- the morph assignments recovered directly from Figure 1;
- official NCBI SRA runinfo and BioSample metadata for `PRJNA1311153`.

No run is identified from geography alone.

## Run-reconciliation rules

`analysis/reconcile_chang2026_ncbi_runs.py` keeps independent evidence channels separate:

- exact supplement-embedded SRR accession;
- exact voucher token such as `ccy3559`;
- exact short sample code in sample/library metadata;
- exact or broad-species taxon agreement;
- exact relation between supplement raw-read count and SRA spots:
  - paired-end: raw reads = 2 × spots;
  - single-end: raw reads = spots;
- locality-token corroboration.

A match is verified only through:

1. exact SRR accession;
2. a unique exact voucher token; or
3. a unique exact read-count relation plus taxon agreement.

Short code or locality alone cannot verify a run. Candidate scores are deterministic reconciliation aids, not biological parameters.

## Run-reconciliation result

- supplement samples: **33**;
- verified or probable official run mappings: **33/33**;
- unique official run assignments: **33**;
- run-assignment collisions: **0**;
- var. *takaoense* samples: **6/6 mapped**;
- mapped morphs:
  - white: WY-3560, FB-3629, LT-3839;
  - bluish-purple: FC-3559, TJ-3807, NH-3835.

The exact SRR, SRX and BioSample identifiers are generated in:

- `chang2026_sample_run_reconciliation.csv`;
- `chang2026_takaoense_sra_manifest.csv`.

They are uploaded as versioned GitHub Actions artifacts by:

- `.github/workflows/reconcile-chang2026-ncbi-runs.yml`.

The workflow validates all supplement-embedded SRR accessions against official runinfo and fails on run collisions.

## Public transcriptome-assembly audit

`analysis/audit_chang2026_public_transcriptome_assemblies.py` queries official NCBI E-utilities for every verified BioSample:

1. `nuccore`: `BioSample AND tsa[filter]`;
2. `nuccore`: voucher-name TSA fallback when the BioSample query is empty;
3. `assembly`: BioSample-linked Assembly records.

The query distinguishes an empty result from an NCBI request error. A failed query is never reported as absence.

## Public assembly result

Across all 33 samples:

- BioSample- or voucher-linked TSA records recovered: **0**;
- BioSample-linked Assembly records without a TSA hit: **0**;
- samples requiring de novo assembly from official SRA reads: **33**.

For var. *takaoense*:

- public TSA records: **0/6**;
- public Assembly records: **0/6**;
- de novo assembly required: **6/6**.

This result means only that the current official BioSample/voucher-linked NCBI queries did not recover a reusable assembly. It does not exclude:

- an unlinked institutional repository;
- an author-held assembly;
- a repository indexed under a different identifier;
- future deposition.

## Why six samples alone are not enough

The six morph-labelled var. *takaoense* transcriptomes are the core topology test, but they cannot by themselves distinguish all plausible histories. A useful gene-tree/reticulation panel needs:

- white sister context;
- coloured flanking lineages that may donate ancestry;
- broader coloured root context;
- an external outgroup.

`analysis/build_chang2026_gene_tree_panel.py` therefore constructs:

| Taxon | Samples | Role |
|---|---:|---|
| *C. japonicum* | 2 | coloured root context |
| *C. japonicum* var. *albescens* | 2 | white sister control |
| *C. japonicum* var. *takaoense* | 6 | three white + three bluish-purple focal samples |
| *C. japonicum* var. *australe* | 3 | coloured flanking / possible ancestry control |
| *C. japonicum* var. *fukienense* | 4 | coloured flanking / possible ancestry control |
| *C. lineare* | 2 | outgroup |
| **Total** | **19** | Sinocirsium 17 + outgroup 2 |

All 19 currently require de novo assembly from unique official SRA runs.

## Competing topology hypotheses

The input package freezes eight six-tip hypotheses:

1. the published Figure 1 nested-bluish-purple topology, whose coloured-root optimum is `1 loss + 1 regain`;
2. the seven nearest rooted topologies at RF distance 4 in which a no-regain history ties the optimum.

This prevents a post hoc comparison against one hand-picked loss-only tree. Every closest loss-only escape topology enters the gene-tree test.

## Next computational workflow

The intended sequence is:

1. download reconciled SRA runs;
2. perform read QC and trimming;
3. assemble each transcriptome de novo;
4. predict coding sequences and proteins;
5. infer orthogroups across the 19 samples;
6. estimate per-orthogroup alignments and gene trees;
7. root gene trees on *C. lineare*;
8. prune to the six var. *takaoense* tips for topology scoring;
9. compare support for the published regain topology versus all seven nearest loss-only alternatives;
10. quantify gene/quartet concordance and identify topology-driving loci;
11. test whether bluish-purple samples show excess affinity to var. *australe* or var. *fukienense*.

A conservative primary matrix should use one-to-one orthologues. Multi-copy/homeolog evidence must be retained separately because polyploidy and reticulation are biologically relevant.

## Biological interpretation

The current result materially strengthens feasibility:

- the six morph-labelled tips are connected to exact official public reads;
- all necessary sister/flanking/outgroup samples are also connected to unique runs;
- the nearest loss-only alternatives are explicitly enumerated;
- no unpublished assembly is silently assumed.

But the inference remains:

> **topology-supported candidate regain**

not:

> demonstrated functional reactivation of floral anthocyanin production.

Gene-tree discordance can distinguish whether the published topology is broadly supported or driven by a subset of loci. It cannot alone exclude ancestral polymorphism or prove molecular pathway restoration. Those require dense populations and linked DNA, floral RNA, pigment and causal-variant evidence.

## Reproducible components

- `analysis/reconcile_chang2026_ncbi_runs.py`
- `tests/test_reconcile_chang2026_ncbi_runs.py`
- `.github/workflows/reconcile-chang2026-ncbi-runs.yml`
- `analysis/audit_chang2026_public_transcriptome_assemblies.py`
- `tests/test_audit_chang2026_public_transcriptome_assemblies.py`
- `.github/workflows/audit-chang2026-public-assemblies.yml`
- `analysis/build_chang2026_gene_tree_panel.py`
- `tests/test_build_chang2026_gene_tree_panel.py`
- `.github/workflows/build-chang2026-gene-tree-panel.yml`
- `data/evidence/chang2026_ncbi_public_assembly_audit_summary_2026-08-11.json`

All three workflows are validated on the current PR and upload the exact generated manifests as retained Actions artifacts.
