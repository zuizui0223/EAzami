# Moreyra et al. 2025 final-tree and retained-locus recovery log

Date: 2026-08-10

## Objective

Recover the original machine-readable analysis artifacts needed to use the published global *Cirsium* phylogeny directly:

1. final concatenated nuclear tree with branch lengths and support;
2. final ASTRAL/coalescent tree;
3. dated tree used for biogeography/diversification;
4. exact 350 retained locus identifiers;
5. retained alignments and per-locus gene trees;
6. manual orthology retain/exclude decisions;
7. tip-label and voucher map.

This log records a **bounded, time-stamped public search**. “Not located” means that the artifact was not identified through the checked routes on the audit date. It does not prove that the file cannot exist in a private, unindexed or later-deposited location.

## Article identifiers

- Final DOI: `10.1016/j.ympev.2025.108285`
- Preprint DOI: `10.2139/ssrn.4983163`
- PII: `S1055790325000028`
- BioProject: `PRJNA957074`
- Title: *A thorny tale: The origin and diversification of Cirsium (Compositae)*

## 1. Publisher article and supplementary files

### Final article

The final article provides:

- the analysis description;
- counts of 1,064 initially mapped loci and 350 final alignments;
- published tree figures and textual topology descriptions;
- a Data Availability statement pointing to PRJNA957074;
- one listed Supplementary Data 1 document.

It does not expose a machine-readable final tree on the article page.

### Supplementary Data 1

The official Elsevier DOCX was recovered and validated:

- size: 10,761,775 bytes;
- SHA256: `34d15286b4ba0952932c55df3a03a286a0d3dc5fb26ead204e6a1ea16a35f4f1`;
- three extracted tables;
- sample/voucher/BioSample evidence and supplementary figures;
- no Newick/Nexus tree;
- no exact final 350-locus list;
- no retained alignments or gene-tree archive.

### Bounded Elsevier attachment enumeration

The repository workflow tested `mmc1` through `mmc20` across common supplementary and phylogenetic extensions:

- `docx`, `xlsx`, `zip`, `txt`, `csv`, `tsv`, `pdf`;
- `nex`, `nexus`, `nwk`, `newick`, `tre`, `tree`;
- `tar.gz`.

Only `mmc1.docx`, the already recovered Supplementary Data 1 file, was valid. No additional standard Elsevier attachment was located under those patterns.

Evidence:

- `data/evidence/moreyra2025_elsevier_supplement_enumeration_2026-08-11.csv`
- `analysis/enumerate_elsevier_supplements.py`

## 2. NCBI project and sample metadata

PRJNA957074 provides:

- 455 public SRA runs;
- 327 submitted scientific names;
- raw target-capture reads;
- BioSample metadata;
- enough information to reconcile 286 of 299 supplement samples to public runinfo.

It does not provide the final concatenated tree, ASTRAL tree, dated tree, retained alignments or the manual final 350-locus decision list in the audited project metadata.

Raw reads make an independent reconstruction possible. They do not reproduce the exact published result unless the missing orthology decisions, retained locus identities and branch-length outputs are obtained.

## 3. Corresponding-author GitHub repository

Repository audited: `ldmoreyra/A-thorny-tale`

The full visible public history was checked:

- branches: 1 (`main`);
- commits: 1;
- tags: 0;
- releases: 0;
- recursive repository tree: 3 files.

Files:

- `hybpiper_stats_exonerate.tsv`
- `seq_lengths_exonerate.tsv`
- `paralog_report.xlsx`

Because the repository has one public commit and no alternative branch, tag or release, there is no visible deleted public history in that repository from which a tree can be recovered.

No Newick/Nexus tree, alignment archive, gene-tree archive or explicit final 350-locus list was present.

## 4. What the public author files do reproduce

The public matrices contain 1,061 named loci, three fewer than the 1,064 initially mapped loci reported in the paper.

The automatic portions of the published filter can be reconstructed:

| Stage | Loci |
|---|---:|
| Public named locus universe | 1,061 |
| More than ten paralog-warning samples | 478 |
| One to ten warning samples; manual-review class | 307 |
| No warning | 276 |
| Raw sequence occupancy at least 0.80 | 1,001 |
| Warning count no more than ten and occupancy at least 0.80 | 531 |
| No-warning and occupancy at least 0.80 | 241 |
| Manual-review class and occupancy at least 0.80 | 290 |
| Paper-reported final alignments | 350 |

Thus the public files reproduce a **531-locus pre-manual candidate set**. The reduction from 531 to 350 depends on unavailable manual gene-tree orthology decisions and final alignment-level filtering.

Detailed audit:

- `docs/MOREYRA_2025_AUTHOR_REPOSITORY_LOCUS_AUDIT_2026-08-10.md`
- `data/evidence/moreyra2025_public_locus_filter_summary_2026-08-10.json`
- `data/evidence/moreyra2025_public_locus_filter_counts_2026-08-10.csv`

## 5. Institutional and preprint records

### FRIS research portal

The publication record exposes:

- an accepted-author-manuscript PDF;
- the final ScienceDirect version;
- the SSRN preprint DOI;
- one dataset entry linked to NCBI PRJNA957074.

No separate tree/alignment/locus-list dataset is listed in the record.

### SSRN

The SSRN record provides the submitted manuscript/preprint. No public analysis-file or tree attachment was identified on the audited landing record.

### Other institutional publication portals

NIBIO, Universidad Autónoma de Madrid, İnönü University and author/coauthor publication profiles were checked as bibliographic discovery routes. They exposed article metadata or DOI links, not an independent tree/alignment repository.

## 6. Bibliographic and data-repository API audit

A versioned workflow queries:

- Crossref;
- DataCite;
- Zenodo;
- Dryad;
- Figshare;
- the full public GitHub author-repository history.

Workflow run `31407990241` produced:

- six services attempted;
- five services queried successfully;
- matching records in Crossref and GitHub only;
- zero tree-like file candidates;
- zero machine-readable final trees recovered;
- zero exact final-350 lists recovered.

Service-level result:

| Service | Result |
|---|---|
| Crossref | article DOI record; no linked tree file |
| DataCite | zero matching dataset records |
| Dryad | zero matching datasets |
| Figshare | zero matching records |
| GitHub | matching author repository; three summary files; no tree-like file |
| Zenodo | the first exact-title API query returned HTTP 400; independent title/DOI web searches did not identify a matching record, but the failed API call remains explicitly recorded rather than converted to a successful zero result |

Artifact:

- workflow run: `31407990241`;
- artifact ID: `9070483791`;
- artifact SHA256: `7c87487553c34a70fab04e3f4b451253368b97707101c273d1a87564ddf3071c`.

Implementation:

- `analysis/audit_moreyra_final_tree_repositories.py`
- `tests/test_audit_moreyra_final_tree_repositories.py`
- `.github/workflows/audit-moreyra-final-tree-repositories.yml`

## 7. Additional repository discovery

Searches by exact title, final DOI, preprint DOI, BioProject, sample identifiers and likely tree-file terms did not identify an article-specific dataset in:

- TreeBASE;
- Dryad;
- Zenodo;
- Figshare;
- Mendeley Data;
- OSF;
- general GitHub code/repository discovery.

The author account contains other project repositories, including Afrocarduus analyses, but no second public repository clearly corresponding to the 2025 global *Cirsium* final tree was identified.

## 8. Current recovery classification

### Recovered

- final article and accepted/preprint manuscript records;
- official Supplementary Data 1;
- 299-sample table and voucher/BioSample information;
- PRJNA957074 raw reads and metadata;
- public HybPiper recovery statistics;
- public sequence-length matrix;
- public paralog report;
- reproducible 1,061-locus universe;
- reproducible 531-locus pre-manual candidate screen;
- reproducible conservative 241-locus no-warning/high-occupancy subset.

### Not located publicly

- final concatenated Newick/Nexus tree;
- final ASTRAL/coalescent tree;
- dated tree;
- exact final 350-locus identifiers;
- retained 350 alignments;
- per-locus gene trees;
- manual orthology retain/exclude log;
- complete final tip-to-support/branch-length mapping.

## 9. Consequence for EAzami analyses

Until original branch-length trees are obtained:

- use source-backed topology fragments for transparent parsimony diagnostics;
- do not infer numerical branch lengths from published figures;
- do not present exploratory equal-branch Mk estimates as published-tree estimates;
- do not run final stochastic mapping under an invented tree;
- preserve alternative concatenated/coalescent/network scenarios qualitatively;
- reserve the label `exact Moreyra 350` for the original retained set only.

For new target-capture data, permitted matrix labels are:

1. public 1,061-locus universe;
2. reproducible 531-candidate screen;
3. conservative 241 no-warning/high-occupancy set;
4. new, fully documented orthology-filtered matrix;
5. paralog/homeolog-aware matrix.

## 10. Next action

The remaining efficient route is direct author contact. A ready-to-send request has been prepared:

- `docs/MOREYRA_2025_DATA_REQUEST_EMAIL.md`

The request asks specifically for:

- concatenated, ASTRAL and dated trees;
- exact 350 retained locus identifiers or alignments;
- per-locus gene trees;
- manual paralog-screen decisions;
- rooting, support and tip-map metadata.

Issue #12 remains open until either:

1. the original artifacts are recovered and validated; or
2. the authors confirm that they are unavailable, in which case EAzami documents the response and proceeds with a newly reproducible reconstruction rather than calling it the published 350-locus analysis.

## Bottom line

> The public record is sufficient to reconstruct sample membership, raw sequence recovery and a 531-locus automatic pre-screen, but it is not sufficient to reproduce the exact final 350-locus phylogeny or its branch lengths. The original final tree and manual orthology outputs were not located in the bounded public search completed on 2026-08-10.
