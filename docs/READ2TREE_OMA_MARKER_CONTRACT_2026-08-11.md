# Read2Tree OMA marker-pack contract

Date: 2026-08-11

## Purpose

The Chang 2026 `var. takaoense` Read2Tree analysis is an assembly-free topology sensitivity screen. Its result is only interpretable if the reference marker export is fixed independently of the six focal W/BP samples.

This contract blocks Read2Tree execution until an OMA Browser marker export has been downloaded, checksummed, structurally audited and normalized.

## Frozen OMA settings

Use the OMA Browser **May 2026** release and select exactly:

- `CYNCS` — *Cynara cardunculus* var. *scolymus* — closest Cardueae reference;
- `HELAN` — *Helianthus annuus* — Asteraceae reference outside Cardueae;
- `DAUCS` — *Daucus carota* subsp. *sativus* — campanulid reference / intended external root.

Versioned provenance is stored in `sampling/read2tree_oma_reference_set_v0_2.csv`.

Export settings are frozen before viewing any `takaoense` result:

```text
minimum fraction of covered species = 1.0
maximum number of markers = 400
```

The expected export therefore contains exactly 400 OMA marker groups with all three selected genomes represented.

## Why no undocumented export API is used

The public OMA documentation exposes the Browser marker-export workflow and explains how to save the generated archive URL. The documented REST explorer does not provide a stable marker-export endpoint equivalent to that UI workflow.

EAzami does not reverse-engineer a hidden request. The generated OMA archive is treated as an external scientific input and is accepted only after validation.

## Validation

```bash
python analysis/validate_read2tree_oma_marker_pack.py \
  --archive /path/to/oma_marker_export.tgz \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_2.csv \
  --oma-release May2026 \
  --export-date YYYY-MM-DD \
  --export-url 'PASTE_THE_GENERATED_OMA_DOWNLOAD_URL' \
  --minimum-species-coverage 1.0 \
  --maximum-markers 400 \
  --expected-marker-count 400 \
  --outdir /work/oma_takaoense400
```

The validator requires:

1. a safe tar archive with no path traversal or links;
2. exactly 400 marker IDs;
3. paired amino-acid and coding-DNA FASTA files for every marker;
4. exactly one `CYNCS`, one `HELAN` and one `DAUCS` sequence per marker;
5. identical OMA sequence IDs between each AA/DNA pair;
6. compatible nucleotide/protein alphabets;
7. coding-DNA lengths in frame and compatible with AA sequence lengths;
8. no OMA sequence ID reused across markers.

If the current OMA export format does not contain sufficient DNA/AA information, validation stops. Coding DNA must not be synthesized from protein sequence and a different reference must not be substituted silently.

## Deterministic outputs

```text
/work/oma_takaoense400/
├── marker_genes/
│   ├── OMAGroup_*.fa
│   └── OMAGroup_*.fna
├── dna_ref.fa
├── marker_pack_locus_audit.csv
└── marker_pack_contract.json
```

The contract records OMA release/export settings, selected taxon IDs, source archive SHA256, normalized marker-pack SHA256, `dna_ref.fa` SHA256, marker count and normalized paths. `execution_allowed: true` appears only after all checks pass.

## Read2Tree gate

The fast-screen builder now requires this validated contract:

```bash
python analysis/build_chang2026_read2tree_pilot.py \
  --panel /work/chang2026_takaoense6_assembly_pilot.csv \
  --reference-manifest sampling/read2tree_oma_reference_set_v0_2.csv \
  --marker-contract /work/oma_takaoense400/marker_pack_contract.json \
  --reads-root /work/chang2026_takaoense_pilot \
  --reads-stage trimmed \
  --output-dir /work/chang2026_read2tree/output \
  --plan-outdir /work/chang2026_read2tree/plan \
  --threads 16 \
  --check-inputs
```

Before generating commands it verifies contract version, OMA release, reference codes, export settings, exact marker count, normalized marker-file counts and `dna_ref.fa` SHA256.

## Downstream topology gate

The Read2Tree nucleotide tree is not scored simply by deleting OMA references. The scorer first checks whether the six `takaoense` samples form a clade relative to the references. If not, the eight colour-history hypotheses are not scored. After support collapse, focal monophyly is checked again before comparison with `analysis/chang2026_takaoense_gene_tree_hypotheses_v1.csv`.

## Interpretation limit

This validated pack is a **May2026 OMA three-reference Read2Tree marker set**. It is not the Moreyra Compositae1061 target set, the unavailable exact Moreyra 350-locus matrix, the Chang phylotranscriptomic orthogroup set, or a causal anthocyanin panel.

Read2Tree is an independent reference-guided topology sensitivity screen. Agreement with Figure 1 justifies deeper gene-tree/reticulation work; disagreement or loss of focal monophyly weakens the candidate-regain interpretation. Neither outcome alone distinguishes introgression, ancestral polymorphism or molecular anthocyanin reactivation.
