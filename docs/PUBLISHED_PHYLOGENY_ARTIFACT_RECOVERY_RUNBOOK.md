# Published phylogeny artifact recovery runbook

Date: 2026-08-10

## Purpose

Recover exact public tree, sample and supplementary artifacts without confusing an inaccessible file with a biological data gap. Publisher files are downloaded to a GitHub Actions artifact, hashed and extracted, but are not automatically committed to the repository.

## Manifest

`data/evidence/published_phylogeny_artifact_manifest_2026-08-10.csv`

Each record stores:

- study/citation key;
- artifact type and host;
- landing page and verified direct URL where available;
- authentication requirement;
- license/reuse context;
- expected filename/size;
- retrieval status;
- extraction method and interpretation notes.

A blank `download_url` means the direct file URL has not been verified. The downloader skips it instead of guessing.

## Current directly recoverable artifacts

1. Mandel et al. 2014 Dryad concatenated 763-locus Newick tree.
2. Chang et al. 2025 Nipponocirsium Supplement DOCX.
3. Chang et al. 2026 Taiwan/Ryukyu Supplement DOCX.

## Known pending artifacts

- Herrando-Moraira 2019 Mendeley datasets: metadata and licenses verified; file enumeration/download requires the Mendeley API/OAuth or manual browser download.
- Moreyra 2025 Supplementary Data 1: article landing page and approximate 10-MB Word supplement verified; exact direct CDN URL remains to be recovered.
- Moreyra and Chang exact final Newick/tree files: not yet shown to be present in the article supplements; raw data and published topologies remain separately available.

## Local/offline validation

```bash
python -m py_compile analysis/recover_published_phylogeny_artifacts.py
python -m unittest tests/test_recover_published_phylogeny_artifacts.py -v
```

The tests generate a minimal DOCX fixture and verify:

- manifest schema and duplicate detection;
- SHA256 calculation;
- DOCX paragraph extraction;
- DOCX table extraction to CSV;
- explicit skips for authentication-required or unverified URLs.

## GitHub Actions recovery

Run the workflow:

`Recover published phylogeny artifacts`

Inputs:

- `fail_on_download_error = true` for a strict release run;
- use `false` only when diagnosing a host-specific outage.

The workflow:

1. runs the offline tests;
2. downloads every verified unauthenticated direct artifact;
3. records SHA256, size and extraction status;
4. extracts DOCX text and all tables to CSV;
5. uploads the entire generated directory as a 90-day Actions artifact.

## Output structure

```text
data/evidence/generated/published_phylogeny_artifacts/
├── artifact_recovery_summary.csv
├── mandel2014_763_loci_tree/
│   ├── 763_loci_tree_newick
│   └── published_text_preview.txt
├── chang2025_nipponocirsium_supplement/
│   ├── 40529_2025_454_MOESM1_ESM.docx
│   └── extracted/
│       ├── document.txt
│       ├── table_001.csv
│       └── ...
└── chang2026_taiwan_ryukyu_supplement/
    ├── 12870_2026_8097_MOESM1_ESM.docx
    └── extracted/
        ├── document.txt
        ├── table_001.csv
        └── ...
```

## Review after download

For every recovered supplement:

- identify sample/voucher/accession tables;
- identify taxon synonyms and localities;
- search for Newick/Nexus/XML/tree text embedded in the document or attached archive;
- compare exact sample names with NCBI BioProject metadata;
- add accepted-name mappings without overwriting source names;
- record whether the artifact closes a file-recovery gap, species-level gap or population-level gap;
- do not count a figure-only topology as a machine-readable tree unless it is explicitly transcribed and labeled as reconstructed from a figure.

## Commit policy

Commit only:

- hashes and recovery summaries;
- extracted metadata/tip tables when license and provenance permit;
- small machine-readable trees under a compatible reuse license;
- scripts, manifests and transformation logs.

Do not automatically commit:

- large publisher documents;
- copyrighted figures;
- raw sequence archives;
- files whose license or provenance is unclear.
