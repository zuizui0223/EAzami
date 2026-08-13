# Read2Tree OMA static marker reconstruction

Date: 2026-08-11

## Purpose

The first Read2Tree design required a manual OMA Browser export for CYNCS, HELAN and DAUCS. That path remains useful as an independent sensitivity profile, but it leaves a manual external input between the published Chang reads and the topology screen.

This document defines a second, fully specified profile:

`oma_static_broadconservation400_may2026_v1`

It is built only from the pinned May 2026 OMA release and the documented OMA REST API.

## Source artifacts

Pinned release: `All.May2026`.

Primary group source:

- `oma-groups.txt.gz`
- expected MD5: `9ba959acbece7547b59eb8e6bc1b7947`

Reference genomes:

- `CYNCS` — *Cynara cardunculus* var. *scolymus*
- `HELAN` — *Helianthus annuus*
- `DAUCS` — *Daucus carota* subsp. *sativus*

The script requires the live OMA API `/api/version/` response to identify the same May 2026 database release before retrieving any sequence. If the live OMA release advances, the build stops instead of combining May 2026 group membership with sequences from a later release.

## Group parsing

`oma-groups.txt.gz` is treated as a release-pinned strict-group membership file. The parser does not assume a tabular column position or a particular group-number prefix. It extracts OMA identifiers with the documented five-character genome code plus five-digit protein-number form.

A group qualifies only when it contains exactly one identifier from each of:

- CYNCS
- HELAN
- DAUCS

OMA Groups are strict orthologous groups with at most one sequence per species, but the EAzami parser checks the one-per-reference condition independently.

## Deterministic selection

All complete-coverage groups are ranked by:

1. total number of OMA members in the group, descending;
2. SHA256 fingerprint of the sorted complete membership list;
3. source line number.

The first 400 are selected.

This ranking deliberately favors groups that are conserved across a broader set of OMA genomes after satisfying 100% focal-reference coverage.

### Important distinction from Browser export

OMA Browser documents its marker export as returning the most complete OMA Groups for the selected species. When minimum selected-species coverage is 1.0, every qualifying group contains all three selected references. The exact tie/ranking behavior used by the Browser among these groups is not treated as documented here.

Therefore the static profile is **not** labelled as an exact reconstruction of the Browser 400-marker export. The two profiles are independent topology sensitivities.

## Sequence retrieval

Only the 1,200 selected OMA proteins are requested.

The builder uses:

- `GET /api/version/`
- `POST /api/protein/bulk_retrieve/`

The bulk endpoint is called in batches below the documented 1,000-ID limit. API 1.7 tuple-shaped results and direct-object forms are normalized explicitly.

For each requested OMA ID, the builder requires:

- exact OMA ID match;
- protein sequence;
- coding DNA (`cdna`/equivalent API field);
- valid alphabets;
- CDS length divisible by three;
- protein/CDS length consistency allowing a terminal stop codon.

Responses are cached per OMA ID.

## Reproducible output

The static builder writes:

- `static_marker_selection.csv`
- `oma_static_broadconservation_marker_export.tar.gz`
- `static_marker_source_contract.json`
- API cache

The tarball is byte-reproducible:

- sorted filenames;
- UID/GID 0;
- empty user/group names;
- file mtime 0;
- gzip mtime 0.

The tarball then passes through the same `validate_read2tree_oma_marker_pack.py` used by the Browser profile. That second validation produces the standard:

- `marker_pack_contract.json`
- `marker_genes/*.fa`
- `marker_genes/*.fna`
- `dna_ref.fa`
- per-locus audit and deterministic normalized-pack hash.

Only that normalized contract is accepted by `build_chang2026_read2tree_pilot.py`.

## Command

```bash
python analysis/build_read2tree_oma_static_marker_pack.py \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_2.csv \
  --outdir results/oma_static400
```

If `oma-groups.txt.gz` is already cached:

```bash
python analysis/build_read2tree_oma_static_marker_pack.py \
  --group-file /path/to/oma-groups.txt.gz \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_2.csv \
  --outdir results/oma_static400
```

Then normalize using the existing contract validator:

```bash
python analysis/validate_read2tree_oma_marker_pack.py \
  --archive results/oma_static400/oma_static_broadconservation_marker_export.tar.gz \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_2.csv \
  --outdir results/oma_static400/validated \
  --oma-release May2026 \
  --export-date 2026-08-11 \
  --export-url "static-profile:oma_may2026_static_broadconservation400_v1" \
  --minimum-species-coverage 1.0 \
  --maximum-markers 400 \
  --expected-marker-count 400
```

The resulting `validated/marker_pack_contract.json` can then be passed directly to the six-sample Read2Tree plan builder.

## Scientific use

Run both profiles when possible:

1. static broad-conservation 400;
2. OMA Browser export 400.

If the candidate-regain versus corrected loss-only conclusion is stable across both independently selected marker packs, reference-marker selection is less likely to be driving the result.

Disagreement is itself informative and should trigger per-marker support, mapping completeness and reference-distance diagnostics rather than choosing the profile with the preferred biological answer.

## Claim limit

Neither marker profile tests floral expression, pigment biochemistry, local ancestry or functional restoration of anthocyanin synthesis. They are only reference-guided nuclear topology screens.
