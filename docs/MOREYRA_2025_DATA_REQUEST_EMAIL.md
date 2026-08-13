# Draft data request: Moreyra et al. 2025 final phylogeny artifacts

Status: ready to send after the project lead adds affiliation/signature details.

## Suggested recipient

Corresponding author: Lucía D. Moreyra  
Publicly listed contact in subsequent corresponding-author publication: `luciad.moreyra@ibb.csic.es`

The address should be verified on the current institutional or journal page immediately before sending.

## Subject

Request for machine-readable trees and retained-locus information from Moreyra et al. (2025) *Cirsium* phylogeny

## Email draft

Dear Dr Moreyra,

I am developing a comparative study of flower-colour evolution in East Asian *Cirsium*, with particular interest in repeated loss of floral anthocyanin pigmentation and possible reactivation in colour-polymorphic lineages.

Your 2025 paper, “A thorny tale: The origin and diversification of *Cirsium* (Compositae)” (Molecular Phylogenetics and Evolution 204:108285), provides the essential global nuclear backbone for this work. I have recovered and reconciled Supplementary Data 1 with BioProject PRJNA957074, and I also found the public GitHub repository `ldmoreyra/A-thorny-tale`, containing the HybPiper statistics, sequence-length matrix and paralog report.

To use the published phylogeny without reconstructing branch lengths or orthology decisions from figures, may I ask whether you could share any of the following original analysis outputs?

1. the final concatenated nuclear tree in Newick/Nexus format, including branch lengths and BS/TBE support;
2. the final ASTRAL/coalescent species tree, including branch lengths where defined and LPP support;
3. the dated tree used for ancestral-range and diversification analyses;
4. the 350 retained alignments and/or a text list of their Compositae1061/HybPiper locus identifiers;
5. the corresponding per-locus gene trees;
6. any table or log recording manual retain/exclude decisions for loci with 1–10 HybPiper paralog warnings;
7. the exact rooting/outgroup and tip-label mapping used for the final published trees.

For transparency, the public summary files allowed me to reproduce the automatic part of the locus screen: 1,061 named public loci, of which 478 have more than ten warning samples, 307 have one to ten warnings, and 276 have no warning. Combining warning count with raw sequence occupancy of at least 80% leaves 531 reproducible pre-manual candidates. However, I cannot identify the exact final 350 without the manual gene-tree decisions and final alignment-level filtering, and I do not want to mislabel an inferred subset as the published matrix.

The requested files would be used to:

- join published tree tips to vouchers and BioSamples;
- run ancestral-state analyses across the original concatenated/coalescent topology alternatives;
- avoid inventing branch lengths from published figures;
- design any new East Asian Compositae1061 sampling to be genuinely compatible with the published framework.

I would cite the paper and any public data repository or data descriptor you prefer. I would also be happy to return a cleaned tip/voucher/name-reconciliation table derived from Supplementary Data 1 if it would be useful.

Thank you very much for considering the request, and for making the raw reads and recovery summaries publicly available.

Best regards,

[Name]  
[Affiliation]  
[Position / programme]  
[Email]  
[Project or repository link, if appropriate]

## Minimal version

Dear Dr Moreyra,

I am using the global *Cirsium* phylogeny from Moreyra et al. (2025) for a study of repeated flower-colour evolution in East Asia. I have recovered Supplementary Data 1, PRJNA957074 and the public `ldmoreyra/A-thorny-tale` summary files, but I could not locate the final machine-readable trees, retained 350-locus list/alignments or per-locus gene trees.

Would it be possible to share the final concatenated, ASTRAL and dated trees (with branch lengths/support), together with the retained 350 locus identifiers or alignments and any available manual paralog-screen decision log? These files would let me use the published topology directly rather than infer branch lengths or orthology decisions from figures.

I will cite the paper and any preferred repository/data descriptor. I would be glad to share the cleaned tip–voucher–BioSample reconciliation table in return.

Best regards,

[Name / affiliation]

## Requested-file checklist for attachment or follow-up

| Artifact | Preferred format | Essential metadata |
|---|---|---|
| Concatenated tree | `.treefile`, `.nwk` or `.nex` | substitution branch lengths; BS and TBE labels |
| ASTRAL tree | `.tre` or `.nwk` | LPP/local support; branch-length definition |
| Dated tree | `.tre`, `.nex` or BEAST/MCMCTree output | time units; calibration/model identity |
| Retained locus list | `.txt`, `.csv` or `.tsv` | Compositae1061/HybPiper target IDs |
| Final alignments | FASTA/PHYLIP archive | one file per locus; sample labels |
| Gene trees | Newick archive | one tree per retained locus |
| Manual orthology decisions | `.csv` or notes | retained/excluded reason for 1–10-warning loci |
| Tip map | `.csv` | tree tip, published name, voucher, BioSample |

## Repository tracking

Tracked under EAzami Issue #12. The issue should remain open until either:

- the exact artifacts are recovered and validated; or
- the authors confirm that they are unavailable, in which case the response date and permitted substitute workflow are documented.
