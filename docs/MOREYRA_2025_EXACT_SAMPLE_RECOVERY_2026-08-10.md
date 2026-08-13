# Moreyra et al. 2025 exact sample recovery and East Asian gap correction

Date: 2026-08-10

## Purpose

The global Moreyra et al. nuclear phylogeny had previously been used only through article-level summaries, one directly verified `C. domonii` accession and incomplete search-engine indexing. That was insufficient for deciding whether a focal East Asian taxon was truly missing from modern nuclear phylogenomics.

This audit recovers the official Supplementary Data 1, reconstructs all public runs from BioProject `PRJNA957074`, joins the two sources by BioSample accession and preserves conflicting tree, published and NCBI names rather than silently choosing one.

## Official supplement recovery

Article DOI:

`10.1016/j.ympev.2025.108285`

Verified Elsevier supplementary URL:

`https://ars.els-cdn.com/content/image/1-s2.0-S1055790325000028-mmc1.docx`

Recovery result:

- valid DOCX;
- size: **10,761,775 bytes**;
- SHA256: `34d15286b4ba0952932c55df3a03a286a0d3dc5fb26ead204e6a1ea16a35f4f1`;
- three supplementary tables extracted;
- Supplementary Table S1 contains **299 sampled plants**;
- 263 rows use a tree code beginning with `Cirsium`;
- no final machine-readable Newick/Nexus tree was present in the recovered DOCX.

The distinction between 263 `Cirsium` tree-code rows and article-level counts using broader or alternative generic circumscriptions is retained. It is not silently resolved by changing names.

## Complete PRJNA957074 recovery

The official NCBI pipeline recovered:

- **455 SRA runs**;
- **327 unique submitted scientific names**;
- run, experiment, BioSample and library identifiers;
- BioSample geographic metadata where publicly available.

The reproducible workflow is:

- `analysis/recover_ncbi_project_runs.py`
- `.github/workflows/recover-ncbi-project-metadata.yml`

The NCBI artifact from the successful full recovery is:

- workflow run `31397812940`;
- artifact ID `9066344851`;
- digest `sha256:14c09d55e6791b71b3b7ee35ff52ce0b0c1f7481e533d9cadf187d5d2105396c`.

## Supplement-to-SRA reconciliation

The join is implemented in:

- `analysis/build_moreyra2025_sample_audit.py`
- `tests/test_build_moreyra2025_sample_audit.py`

It generates:

- complete sample reconciliation;
- East/Northeast Asia subset;
- focal-taxon audit;
- name-discrepancy audit;
- supplement samples lacking linked public runs;
- machine-readable summary JSON.

Verified counts:

| Quantity | Count |
|---|---:|
| Supplement sample rows | 299 |
| PRJNA957074 runs | 455 |
| Unique NCBI scientific names | 327 |
| Supplement samples linked to public runinfo | 286 |
| Supplement samples without a linked public run | 13 |
| Core East Asian sample rows | 43 |
| Northeast Asian bridge sample rows | 7 |
| Focal taxa audited | 32 |
| Exact focal scientific-name matches | 10 |

The 13 unlinked sample rows include one `C. brevifolium` BioSample without a recovered run and five `Cirsium` rows with no accession recorded in Supplementary Table S1 (`C. handaniae`, `C. hypoleucum`, `C. daghestanicum`, `C. leuconeurum`, `C. remotifolium`). These are tree/sample-table evidence but not public-run evidence.

## Exact focal taxa newly verified

The following Chapter 2 focal or comparison taxa now have exact Supplementary Table S1 plus PRJNA957074 scientific-name matches:

| Taxon | BioSample | Run | Consequence |
|---|---|---|---|
| `C. domonii` | `SAMN34240283` | `SRR25265717` | nuclear anchor confirmed |
| `C. dipsacolepis` | `SAMN44017836` | `SRR30887259` | species-level placement is not a new sequencing gap |
| `C. pendulum` | `SAMN34240327` | `SRR25265649` | species placement exists; white/coloured population history remains missing |
| `C. sieboldii` | `SAMN44017917` | `SRR30887308` | species placement exists; Japanese morphs and Zhejiang bridge remain missing |
| `C. yezoense` | `SAMN44017952` | `SRR30887226` | coloured bridge/control placement confirmed |
| `C. japonicum` | `SAMN44017885` | `SRR30887271` | broad Japanese/continental reference confirmed |
| `C. nipponicum` | `SAMN34240318` | `SRR25265660` | Moreyra tip plus separate Korean genome/plastome resources available |
| `C. nipponicum var. incomptum` | `SAMN44017937` | `SRR30887286` | exact NCBI match; published/tree names still require reconciliation |
| `C. lineare` | `SAMN44017876` | `SRR30887240` | nuclear outgroup/backbone anchor confirmed |
| `C. vlassovianum` | `SAMN34240275`, `SAMN34240350` | `SRR25265601`, `SRR25265666` | two public runs; one row intersects the `coryletorum` name problem |

This materially changes the sequencing plan. `C. pendulum`, `C. sieboldii`, `C. yezoense`, `C. japonicum`, `C. nipponicum`, `C. lineare`, `C. vlassovianum` and `C. dipsacolepis` should not be promoted for new target capture merely to establish species placement.

Their remaining value lies in:

- white versus coloured population structure;
- transregional bridge sampling;
- local ancestry and gene flow;
- cytotype/homeolog history;
- causal colour-associated genomic regions.

## Genuine or still-unresolved focal gaps

No exact Moreyra Supplementary Table S1 or PRJNA957074 scientific-name match was recovered for:

- `C. setidens`;
- `C. rhinoceros`;
- `C. schantarense`;
- `C. tamastoloniferum`;
- multiple Taiwan/Ryukyu focal taxa already covered by separate Chang transcriptome datasets;
- several Taiwanese taxa outside those focal Chang clades.

A Moreyra non-match is not yet proof of a complete nuclear-data absence. Before target capture is approved, accepted names, synonyms, alternative genera and other deposited nuclear datasets must still be exhausted.

The strongest residual Korean candidates remain `C. setidens` and `C. rhinoceros`, but only after extant voucher-backed white morphs are confirmed. `C. schantarense` remains important for Korea–Manchuria–Russian Far East standing-variation tests.

## Name reconciliation is a biological-data requirement

Across the full joined table, the relationship between Moreyra tree code and NCBI scientific name was:

| Relationship | Joined rows |
|---|---:|
| exact | 186 |
| generic reassignment only | 24 |
| different submitted or published name | 77 |
| no comparable public-run name | 13 |

Examples relevant to East Asia include:

- `C. coryletorum` versus NCBI `C. vlassovianum`;
- `C. maackii` versus `C. japonicum var. maackii`;
- `C. verutum` versus `Lophiolepis veruta`;
- `C. subulariforme` versus `Lophiolepis subulariformis`;
- `C. tanakae` versus a published-species assignment to `C. nipponicum var. incomptum`;
- `C. nipponicum var. yoshinoi` versus NCBI `C. yuki-uenoanum`.

Therefore an accepted-name exact-string search cannot define a phylogeny gap. Tree code, published species, NCBI name, voucher and current accepted name must be retained as separate fields.

## Geographic metadata conflict retained

One sample cannot be safely interpreted without manual resolution:

- tree code: `Cirsium yuki-uenoanum`;
- supplement voucher geography: Japan;
- BioSample: `SAMN44017949`;
- NCBI scientific name: `Cirsium waldsteinii`;
- NCBI geography: Ukraine.

The pipeline marks this as `metadata_conflict_requires_manual_resolution`. It is not counted as a clean Japanese nuclear tip.

## Consequence for Chapter 2

### Species-backbone layer

New Compositae1061 target capture should be restricted to:

1. a transition-critical taxon absent after synonym and public-data reconciliation;
2. a missing bridge whose placement changes colour-transition direction;
3. a cytotype/reticulate lineage for which one existing tip is biologically inadequate.

### Population layer

The exact recovery strengthens the case for RAD-seq or resequencing—not species-level target capture—for:

- Japanese white versus purple `C. pendulum`, plus continental populations;
- Japanese white versus coloured `C. sieboldii`, plus Zhejiang populations;
- `C. vlassovianum` / `coryletorum` transregional name and population structure;
- focal Taiwan/Ryukyu colour morphs already placed by Chang.

## Remaining blocker for formal ancestral-state models

The recovered Moreyra supplement provides exact sample metadata but no final Newick tree or branch lengths. Therefore:

- exact taxon inclusion is now substantially recoverable;
- exact sister relationships and branch lengths are still not machine-readable in the repository;
- formal Mk likelihood comparison and stochastic mapping across the global tree remain pending;
- topology-only parsimony remains a transparent diagnostic, not the final rate analysis.

The next tree-recovery task is to obtain the final concatenated/coalescent tree files and the retained 350-locus list from a data repository or the authors. If no machine-readable tree was deposited, a versioned figure-derived topology may be used only as a clearly labelled fallback without invented branch lengths.

## Versioned evidence files

- `data/evidence/prjna957074_focal_tip_recovery_2026-08-10.csv`
- `data/evidence/moreyra2025_sample_audit_summary_2026-08-10.json`
- `data/evidence/moreyra2025_east_ne_asia_tip_decisions_2026-08-10.csv`
- `data/moreyra_japan_backbone_audit.csv`
- `data/evidence/published_phylogeny_artifact_manifest_2026-08-10.csv`

Publisher files are not committed. Hashes, source-derived audit tables, reproducible code and 90-day Actions artifacts preserve provenance.
