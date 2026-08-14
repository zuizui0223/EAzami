# Heavy-compute workflow bundles

This directory contains portable execution bundles for analyses that exceed ordinary CI or local validation:

- `chang2026_gene_trees/`: per-locus/gene-tree reconstruction for the labelled transcriptomes.
- `chang2026_read2tree/`: static-marker Read2Tree screens and restartable execution.
- `colour_rate_comp1061/`: common-locus bridge and colour-rate workflow stages.

Each bundle should expose versioned inputs, a restartable command, resource assumptions, completion markers and checksums. Raw reads, large assemblies and transient work directories are not committed. Accepted summaries return to `analysis/`, `data/evidence/` or a current decision document.
