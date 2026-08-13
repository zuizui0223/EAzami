# Draft data request: Moreyra et al. 2025 tree and retained-locus files

## Intended recipient

**Dr. Lucía D. Moreyra**  
Corresponding-author address reported in the article: `luciad.moreyra@ibb.csic.es`

This is a draft only. It has not been sent from this repository.

## Suggested subject

Request for machine-readable phylogenetic trees and retained-locus list from Moreyra et al. (2025)

## Email draft

Dear Dr. Moreyra,

I hope you are well. My name is Ruiqi Zhang, and I am developing a comparative study of repeated floral-colour loss and possible regain in East Asian *Cirsium*. Your paper, “A thorny tale: The origin and diversification of *Cirsium* (Compositae)” (Molecular Phylogenetics and Evolution 204:108285), provides the essential global nuclear backbone for this work.

I have recovered Supplementary Data 1 and linked its 299 sample records to the public reads in BioProject PRJNA957074. This has allowed me to verify taxon membership and vouchers, but I have not been able to locate the final machine-readable tree or the identities of the 350 retained nuclear loci in the article supplement, NCBI record, or the public repositories I searched.

Would you be willing to share, or point me to a repository containing, any of the following files?

1. the best RAxML-NG concatenated tree, preferably with branch lengths and BS/TBE support;
2. the ASTRAL-III species tree with local posterior probabilities and, if available, quartet-support annotations;
3. the RelTime time-calibrated tree used for the biogeographic analyses;
4. the 350 per-locus gene trees or their source alignments;
5. the list of the 350 retained Compositae1061 loci and any table describing occupancy, paralog screening, or other locus-filtering decisions;
6. any tree-tip/name map used after pruning duplicated individuals for the biogeographic analysis.

The highest-priority files for my current analysis are the concatenated tree, ASTRAL tree, dated tree, and retained-locus list; a repository link is entirely sufficient, and I would be grateful even if only those four items are available.

I would use the files to reconstruct floral-colour history across alternative nuclear topologies, explicitly account for the young Japanese radiation and possible gene-tree discordance, and identify which East Asian taxa genuinely remain missing before planning new target-capture sequencing. All files and the original article would be cited, and I would follow any preferred data-use or attribution conditions you specify.

For transparency, I have kept the published tree code, species name, voucher, BioSample name, and current taxonomic interpretation as separate fields rather than silently reconciling conflicting names. I would also appreciate any guidance on the few apparent metadata conflicts, particularly the row labelled *Cirsium yuki-uenoanum* in Supplementary Table S1 that links to an NCBI record named *C. waldsteinii* from Ukraine.

Thank you very much for considering this request, and especially for making the raw sequence data and sample metadata publicly available.

Best regards,

Ruiqi Zhang  
East Asian *Cirsium* flower-colour evolution project  
GitHub: `zuizui0223/EAzami`

## Minimal version

Dear Dr. Moreyra,

I am using Moreyra et al. (2025), “A thorny tale,” as the nuclear backbone for a study of repeated floral-colour evolution in East Asian *Cirsium*. I recovered Supplementary Data 1 and PRJNA957074, but I could not locate the machine-readable final trees or the retained 350-locus list.

Could you please share, or point me to a repository containing, the RAxML-NG concatenated tree, ASTRAL-III tree, RelTime dated tree, and list of the 350 retained Compositae1061 loci? Gene trees/alignments and the locus-filtering table would also be extremely helpful if available.

The files will be fully cited and used to compare flower-colour ancestral-state reconstructions across nuclear topologies and to avoid unnecessary sequencing of taxa already covered by your study.

Many thanks,

Ruiqi Zhang

## Before sending

- replace the generic project signature with current affiliation and preferred contact details;
- optionally include the PR or repository URL;
- do not attach publisher supplementary files;
- mention that a public repository deposit would be preferable if the authors are able to create one;
- retain the request for the `yuki-uenoanum` / `waldsteinii` metadata clarification, but remove it from the first message if a shorter initial contact is preferred.
