# Original Compositae1061 HybPiper reference — compatibility recovery

Date: 2026-08-12

## Result being tested

The public repository accompanying Siniscalchi et al. 2021, *Lineage-specific vs. universal: a comparison of the Compositae-1061 and Angiosperms-353 enrichment panels in the sunflower family*, contains:

- `comp1061_hybpiper_reference.fasta`
- repository: `carol-siniscalchi/Comp1061-Angio353`
- pinned commit: `c340244907c39579dca42060769678bf8759fa1d`
- Git blob SHA1: `4f89e234007f367ffa8aa5e2be536bc44f31f445`
- GitHub-reported size: 1,162,856 bytes.

The same repository's analysis script passes its generic `reference_file.fasta` directly to HybPiper `reads_first.py -b`, `get_seq_lengths.py` and `retrieve_sequences.py`, and then aligns retrieved FNA loci, infers gene trees and runs ASTRAL. The file is therefore an appropriate public original Compositae1061 HybPiper reference candidate.

## Why this matters for EAzami

Issue #16 previously had two logically different missing objects bundled together:

1. a usable original/compatible Compositae1061 HybPiper reference;
2. the exact **Moreyra-augmented** reference used for *A thorny tale*.

Moreyra et al. 2025 explicitly state that their reference was the original Compositae1061 target file **plus exons recovered from their highest-coverage `Cirsium tioganum` sample**. Therefore recovering the original reference does not recover the augmented Moreyra file.

If the pinned public reference passes the automated 1061-locus/header/sequence audit, EAzami may use it for a clearly labelled **compatibility reanalysis** of PRJNA957074 and for same-assay new samples. It must not be described as an exact reproduction of Moreyra's raw-read preprocessing.

## Automated contract

`analysis/recover_comp1061_original_hybpiper_reference.py` requires:

- exact pinned Git blob SHA;
- exact GitHub-reported byte size;
- ASCII FASTA;
- non-empty IUPAC-DNA sequences;
- HybPiper-style `<reference>-<locus>` headers;
- exactly 1,061 unique loci;
- reference prefixes exactly `lett`, `saff`, `sunf`;
- no duplicate reference/locus pair.

The workflow emits:

- the recovered FASTA;
- `comp1061_original_reference_contract.json` with SHA256 and observed structure.

## Scientific boundary

A successful recovery changes the project state from:

> no usable Compositae1061 target/reference recovered

to:

> original public Compositae1061 HybPiper reference recovered and usable for compatibility analysis; Moreyra-specific C. tioganum augmentation still missing.

This is sufficient to unblock an **independent compatibility tree** once raw-read processing and orthology/locus-filter sensitivities are executed. It is not sufficient to claim exact reproduction of the published Moreyra species tree.
