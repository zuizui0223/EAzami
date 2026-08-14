# Heavy-compute workflow bundles

This directory contains portable execution entry points for analyses that exceed ordinary CI or local validation:

- `public_nuclear_maximum/`: top-level artifact-free handoff for the accepted 294-tip baseline plus EA01, EA02 and CNIPG independent promotion gates. This is the current issue #18 execution entry point; it shares the baseline download/recovery across all three candidates and never auto-promotes a combined 296/297 tree.
- `chang2026_gene_trees/`: per-locus/gene-tree reconstruction for the labelled transcriptomes.
- `chang2026_read2tree/`: static-marker Read2Tree screens and restartable execution.
- `colour_rate_comp1061/`: common-locus bridge and colour-rate workflow stages.

Each bundle should expose versioned inputs, a restartable command, resource assumptions, completion markers and checksums. Raw reads, large assemblies and transient work directories are not committed. Accepted summaries return to `analysis/`, `data/evidence/` or a current decision document.
