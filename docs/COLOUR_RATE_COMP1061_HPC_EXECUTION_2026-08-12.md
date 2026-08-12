# 20-tip Compositae1061 compatibility tree — HPC execution contract

The successful official-SRA bridge is frozen in `colour_rate_comp1061_bridge_artifact_contract_v1.json`: 20 paired runs, C=17/W=3, 13 leaf-RNA-seq and 7 target-capture tips.

The generated HPC bundle runs two mapping modes. **BWA is primary** because the original Compositae1061 analysis used HybPiper 1.3.1 with `--bwa`; the current implementation uses HybPiper 2.3.4 and preserves BWA as the mapping choice rather than pretending to reproduce the old software stack exactly. **Default BLASTx is a sensitivity** using the same cleaned reads and original 1,061-locus DNA reference.

Stages:

1. recover and SHA-validate the original public Compositae1061 HybPiper reference; recreate the frozen 1061/531/241 locus lists from the public Moreyra stats/paralog source;
2. 20-way Slurm array: `prefetch -> vdb-validate -> fasterq-dump -> pigz -> fastp`;
3. 20-way HybPiper BWA primary array, exonic output only (`--no_intronerate`) and compressed sample folders;
4. parallel BLASTx sensitivity array;
5. per-mode HybPiper `stats`, `retrieve_sequences dna`, and `paralog_retriever`.

The bundle deliberately stops its accepted workflow at retrieved-sequence/QC output. The next promotion step must combine the **current** 20-tip occupancy and paralog results with the frozen public 241/531/1061 locus sets, append source-reference outgroups, run MAFFT/IQ-TREE gene trees, a concatenated IQ-TREE branch-length tree, and ASTRAL topology sensitivity.

A tree is not accepted for flower-colour rates merely because IQ-TREE finishes. Before promotion the project must test target-capture versus leaf-RNA occupancy, mapping-mode sensitivity, replicate alternatives, current paralog conflicts, Cirsium monophyly relative to the reference outgroups, and matrix-set stability. ASTRAL topology is a coalescent sensitivity; the concatenated ML substitution-per-site branch lengths are the candidate discrete-trait branch-length scale, subject to those gates.
