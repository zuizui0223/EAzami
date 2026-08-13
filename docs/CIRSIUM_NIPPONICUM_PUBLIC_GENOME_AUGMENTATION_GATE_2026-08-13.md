# Natural-Ulleung *Cirsium nipponicum* public-genome augmentation gate — 2026-08-13

## Why this candidate matters

Repository cleanup exposed a valid public nuclear candidate that was not represented in the current EA01/EA02 augmentation summary. The 2024 natural-Ulleung *Cirsium nipponicum* genome has a frozen Compositae1061-derived locus pack with **180/241 strict loci** and no cross-locus subject collisions.

This is not a new analysis taxon label: the 294-tip baseline already contains a *Cirsium nipponicum* representation. Its value is different. The public genome is an independent natural-Ulleung sample and a different nuclear data type, while the baseline representation has cultivated/garden provenance.

Frozen evidence:

- source contract: `data/evidence/cirsium_nipponicum_public_genome_comp1061_contract_v1.json`;
- compact recovered-pack result: `data/evidence/cirsium_nipponicum_comp1061_locus_pack_result_2026-08-13.json`;
- gate: `data/evidence/cirsium_nipponicum_public_genome_augmentation_gate_v1.json`;
- successful pack workflow run: `31684233926`;
- artifact: `9174758977`;
- artifact SHA256: `079e3bfaab1d5041ebc2dcb1919532c75eefde7ffe1f766ab0473845f2f9dd69`;
- strict recovered loci: `180/241`;
- pack ready: `true`;
- tree-tip promotion before paired trees: `false`.

## Separate cross-data-type gate

This candidate is **not** inserted into the EA01/EA02 same-assay SRA gate. Its sequence pack comes from genome annotation-derived CDS and is therefore evaluated as a separate cross-data-type sensitivity.

For each accepted baseline mapping mode (`bwa`, `blastx`):

1. intersect that mode's accepted baseline loci with the frozen 180 genome-derived loci;
2. require at least 100 paired loci;
3. build `baseline294` and `cnipg_295` from the exact same paired locus list;
4. infer concatenated IQ-TREE trees and source-label ASTRAL trees;
5. compare the 294 shared baseline tips after pruning the augmentation;
6. evaluate whether an existing baseline *C. nipponicum* tip is among the augmentation's nearest baseline neighbours.

Strict automatic promotion requires in **both** baseline mapping modes:

- shared-294-tip concatenated RF = 0;
- same-taxon baseline representation among nearest neighbours;
- shared-species ASTRAL RF = 0.

Any failure routes the candidate to manual biological review. No locus, homology or topology threshold is relaxed automatically.

## Public-tree ceiling

The accepted primary tree remains **294 tips**.

There are now three independently ready public candidate samples awaiting tree-level promotion tests:

- EA01 — *C. nipponicum* var. *yoshinoi* target-capture replicate;
- EA02 — *C. sairamense* cross-study target-capture replicate;
- CNIPG — natural-Ulleung *C. nipponicum* genome-derived replicate.

If all independent gates eventually pass, the current sample-level public candidate ceiling is therefore **297 tips**, still with **0 new analysis taxon labels**. This is not yet an accepted combined 297-tip tree. A final combined tree requires an explicit common paired-locus contract across all candidates admitted by their independent gates.

## Executable handoff

`analysis/build_cirsium_nipponicum_genome_augmentation_hpc_bundle.py` builds the paired BWA/BLASTx baseline sensitivity bundle. The generated Slurm stage includes paired-input preparation, MAFFT, per-locus IQ-TREE, concatenated IQ-TREE, ASTRAL, RF/nearest-neighbour evaluation and cross-data-type summarization.

The gate/bundle CI exercises the real 180-locus artifact against a reconstructed real 294-tip baseline bundle and validates the decision logic offline. Heavy tree inference remains an HPC or large-memory-local task.

## Claim boundary

A successful gate would admit one additional public biological sample and strengthen the natural-versus-cultivated *C. nipponicum* placement comparison. It would not by itself change the repeated-white-loss interpretation, prove any flower-colour transition, admit EA01/EA02, or justify freezing new China sampling.
