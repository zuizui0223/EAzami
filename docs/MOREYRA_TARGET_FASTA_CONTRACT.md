# Moreyra reconstruction target FASTA contract

Date: 2026-08-11

## Purpose

A raw-read reconstruction is interpretable only when the target/reference FASTA is versioned. A change in target sequences can alter mapping, locus recovery, paralog warnings, stitched contigs and therefore the resulting tree even when every other software setting is identical.

EAzami therefore blocks the 12-sample Moreyra pilot until one explicit JSON contract links:

- the local target FASTA;
- its SHA256 checksum;
- public source and dataset version;
- sequence type and mapping mode;
- FASTA structure;
- overlap with the 1,061 public Moreyra locus IDs;
- exact-versus-compatible identity status;
- a human approval decision.

Implementation:

- template: `config/moreyra_target_contract.template.json`
- validator: `analysis/validate_moreyra_target_contract.py`
- tests: `tests/test_validate_moreyra_target_contract.py`
- CI gate: `.github/workflows/validate-moreyra-target-contract.yml`

## Identity classes

### `unresolved`

No executable target has been selected. This is the repository default.

An unresolved contract may be validated with `--allow-unapproved` to confirm schema and blocking behaviour. It can never permit pilot execution.

### `compatible_compositae1061_target`

A public Compositae1061-compatible target/reference FASTA has been recovered and versioned, but available evidence does not establish that this exact file/version was used by Moreyra et al. 2025.

A compatible target may be approved for a **compatibility reconstruction**. The approval basis must explicitly state that the run is not an exact reproduction of the published target configuration.

### `exact_moreyra_target`

The file and version are explicitly tied to the Moreyra analysis by the Methods, archived workflow, author documentation or direct author confirmation.

This class additionally requires `source.method_confirmation` in the contract.

Sequence counts, locus-name overlap or a plausible file name are not enough to assign this class.

## Target type

The executable type is:

```text
hybpiper_reference_fasta
```

The validator rejects:

```text
bait_probe_fasta
```

Capture baits/probes and HybPiper target/reference sequences are related resources, but they are not interchangeable inputs. Short oligo baits must not be passed to the assembly workflow as though they were the gene-reference target file.

## Sequence and mapping classes

Allowed sequence types:

- `dna`
- `protein`
- `unresolved`

Allowed mapping modes:

- DNA target: `bwa`
- protein target: `diamond` or `blastx`
- unresolved target: `unresolved`

The validator checks the observed FASTA alphabet against the declared sequence type. An approved contract cannot retain an unresolved sequence or mapping mode.

## Required provenance for approval

An approved contract records:

- repository or host;
- dataset/deposit identifier;
- dataset version;
- landing URL;
- direct download URL;
- license where available;
- candidate label;
- local path;
- SHA256;
- approval author, date and basis.

For an exact identity claim, it additionally records the evidence linking that file/version to the published Moreyra workflow.

## File-level checks

When the target exists locally, the validator reports:

- resolved path;
- SHA256;
- FASTA record count;
- unique first-header-token count;
- total, minimum, median and maximum sequence length;
- DNA/protein/invalid alphabet classification;
- number and proportion of the 1,061 public Moreyra locus IDs matched after conservative header normalization.

A declared checksum, record count or unique-token count becomes a hard invariant.

The default minimum normalized overlap is 0.95. This is a compatibility screen, not proof of exact identity. A target may legitimately contain multiple reference taxa per locus, so FASTA record count does not have to equal 1,061.

## Execution gate

The validator emits:

```json
{
  "contract_valid": true,
  "execution_allowed": false
}
```

for a structurally valid unresolved template.

Pilot execution is allowed only when all of the following are true:

1. `approval.approved_for_12_sample_pilot` is true;
2. identity is exact or explicitly compatible;
3. target type is the HybPiper reference FASTA;
4. sequence and mapping modes are resolved and coherent;
5. the local FASTA exists;
6. SHA256 matches;
7. declared structural invariants match;
8. locus overlap meets the declared threshold;
9. required provenance and approval fields are complete;
10. no bait/probe or alphabet warning remains.

The CI workflow validates the unresolved template and proves that it cannot authorize execution. When a reviewed `config/moreyra_target_contract.json` is eventually committed, the same workflow treats failure as a blocking error.

## Commands

Validate the unresolved template:

```bash
python analysis/validate_moreyra_target_contract.py \
  --contract config/moreyra_target_contract.template.json \
  --moreyra-loci data/evidence/generated/moreyra_author_repository/locus_sets/moreyra_public_1061_loci.txt \
  --report data/evidence/generated/moreyra_target_contract_template_validation.json \
  --allow-unapproved
```

Validate an approved candidate:

```bash
python analysis/validate_moreyra_target_contract.py \
  --contract config/moreyra_target_contract.json \
  --moreyra-loci data/evidence/generated/moreyra_author_repository/locus_sets/moreyra_public_1061_loci.txt \
  --report data/evidence/generated/moreyra_target_contract_validation.json
```

A nonzero exit from the second command means the raw-read assembly pilot must not start.

## Relationship to the unavailable final 350 loci

The target contract concerns the input reference FASTA used for locus recovery. It does not resolve the separate missing artifacts:

- the exact final 350 retained loci;
- manual gene-tree orthology decisions;
- final retained alignments;
- final concatenated, coalescent and dated trees.

The current reproducible public locus sets remain:

- public universe: 1,061;
- automatic warning/occupancy candidates: 531;
- conservative no-warning/high-occupancy: 241;
- high-occupancy manual-review class: 290.

No target contract may relabel one of those sets as the original final 350.
