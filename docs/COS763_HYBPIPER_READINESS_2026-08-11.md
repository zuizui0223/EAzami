# COS763 HybPiper-readiness and Compositae1061 target decision

Date: 2026-08-11

## Decision

The exact or source-confirmed compatible Moreyra et al. Compositae1061
HybPiper target/reference FASTA was **not recovered** from the audited public
sources. The recovered Mandel et al. COS763 alignments are retained as a
source-backed mapping and reading-frame-correction resource. They are **not**
renamed or frozen as the missing Moreyra Compositae1061 target.

Consequently:

1. an exact Moreyra pipeline reproduction remains gated on the target file and
   version used by the authors;
2. a future run using another target must be labelled a compatibility rerun and
   include target-version sensitivity;
3. the Chang 2026 transcriptome gene-tree analysis continues through de novo
   transcriptome assembly and orthology inference and is not blocked by this
   target-file gap.

## Public-source audit

Two independent discovery workflows now complete successfully.

### First-pass broad-link audit

- workflow run: `31456078865`;
- artifact: `9088162687`;
- artifact digest:
  `sha256:b0a20e07487f49b8935820350add37933cc8cba4ec14b0f3b4e20726eef7b26b`;
- source requests: 898;
- successful requests in that run: 893;
- discovered file candidates: 9;
- exact target frozen: `false`.

### Expanded metadata-aware audit

- workflow run: `31456886057`;
- artifact: `9088399851`;
- artifact digest:
  `sha256:6f511deb9123e414ad7a130e7537868089514051826a5b7036f811d7ed3ff350`;
- public source classes: Mendeley Data, Dryad and GitHub contents records;
- source requests: 22;
- successful requests: 16;
- filename/download-URL pairs: 37;
- download attempts/successes: 8/7;
- FASTA candidates audited as complete files: 1;
- source-confirmed exact or compatible Compositae1061 targets: 0;
- exact target frozen: `false`.

Request success counts are network-run diagnostics. The biological decision is
based on the recovered candidate contents and provenance, not on a fixed number
of successful web requests.

## Recovered COS763 source

The expanded audit recovered the foundational Compositae target-enrichment
archive from:

```text
Dryad DOI: 10.5061/dryad.gr93t
Dataset version: 1
Licence: CC0-1.0
Outer archive SHA256:
263f8a15c5f667028dbae2e011b8b42dba00e9ce4dcc90f9f84f87c9fdf6f26b
Nested COS alignment archive:
COS_alignment_files_NEW.zip
Nested archive SHA256:
f6b07b871143fdbd8dfdc7fc66e05ffb963a15931d6816404147156599de77f0
```

The archive contains 763 per-locus nucleotide alignments. It also contains a
concatenated 763-locus alignment, but a concatenated alignment is a derived
phylogenetic artifact rather than a HybPiper target/reference FASTA.

## Sequence-readiness result

The reproducible audit in
`analysis/audit_cos763_hybpiper_readiness.py` removed alignment gaps while
preserving locus and source identity, then evaluated minimum length, ambiguity,
length modulo three and internal frame-0 stop codons.

| Diagnostic | Result |
|---|---:|
| loci | 763 |
| source sequences | 5,699 |
| source taxa | 16 |
| median sources per locus | 7 |
| source range per locus | 3–15 |
| median ungapped length | 240 nt |
| ungapped-length range | 5–1,461 nt |
| sequences with length divisible by 3 | 1,913 (33.57%) |
| sequences without an internal stop in frame 0 | 1,221 (21.42%) |
| mapping-reference sequences after minimum-length/ambiguity filters | 5,607 |
| direct frame-0 CDS candidate sequences | 410 |
| loci with at least one direct frame-0 candidate | 200/763 |
| loci for which all source sequences are direct candidates | 2/763 |
| complete direct HybPiper nucleotide target ready | **false** |

The frame-0 test is intentionally conservative and does not infer the true
reading frame. A sequence that fails it may still become useful after
source-backed frame correction; a sequence that passes it is only a candidate,
not a validated CDS ortholog.

## Frozen outputs

The successful workflow artifact contains:

```text
data/evidence/generated/cos763_hybpiper_readiness/
  cos763_hybpiper_readiness_summary.json
  cos763_sequence_readiness.csv
  cos763_locus_readiness.csv
  cos763_unframed_multisource_mapping_reference.fasta
  cos763_direct_cds_candidate_subset.fasta
```

The unframed mapping reference keeps headers in `Taxon-locus` form and may be
used only for exploratory mapping, reference comparison or explicit reading-frame
correction. It must not be supplied as a validated CDS target without a separate
frame, orthology and target-version contract.

## Analysis consequences

### Moreyra 2025 reconstruction

The 12-sample Moreyra pilot remains prepared at the sample/run level. Its exact
HybPiper recovery stage should not be interpreted until one of these conditions
is met:

1. the authors or a documented repository provide the exact target/reference
   FASTA and version; or
2. a clearly named compatibility target is selected, validated and compared
   against at least one plausible alternative target version.

The public 1,061/531/241 locus manifests remain valid analytical subsets of the
public locus-name universe. They do not identify the target sequences used for
assembly.

### Chang 2026 var. takaoense test

The 19-sample Chang workflow does not depend on a Compositae target file. Its
primary path remains:

```text
official paired-end SRA reads
  -> fastp
  -> Trinity de novo transcriptomes
  -> TransDecoder
  -> OrthoFinder
  -> rooted single-copy gene trees
  -> published-regain versus seven nearest loss-only hypotheses
```

COS763 can later provide a secondary locus-annotation or mapping-sensitivity
layer, but it must not replace the de novo/orthology workflow merely because it
is publicly available.

## Claim boundary

The valid statement is:

> A source-backed 763-locus Compositae alignment resource was recovered and
> audited, but it is neither the exact Moreyra Compositae1061 target nor a
> complete directly usable nucleotide CDS target. The exact target remains an
> explicit provenance blocker for Moreyra compatibility reconstruction, while
> the Chang transcriptome gene-tree workflow remains executable through de novo
> assembly.
