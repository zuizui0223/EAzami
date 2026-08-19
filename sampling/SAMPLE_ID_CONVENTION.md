# EAzami field sample ID convention

Status: 2026-08-19

## Principle

A biological plant receives **one immutable `individual_id`**. Phenotype, taxonomic interpretation, treatment and assay result are metadata and must not be encoded into the identity itself.

The tranche-1 population manifest is:

`sampling/doctoral_field_tranche1_population_manifest_v1.csv`

The cross-Aim individual ledger is:

`sampling/aim13_individual_sample_ledger_v1.csv`

## Population IDs

Core population IDs are `P001`–`P014` and are assigned before individual collection.

Example:

`P001` = the first required *C. brevicaule* population block in the tranche-1 manifest.

The population ID remains stable if the accepted taxon name or colour interpretation is later revised. Exact locality, coordinates and taxon determination live in the manifest/ledger rather than inside the ID string.

## Individual IDs

Pattern:

`EA26-P###-I###`

Examples:

- `EA26-P001-I001`
- `EA26-P001-I015`
- `EA26-P009-I003`

Rules:

- numbering restarts at `I001` within each population;
- never reuse an individual number after a sample is discarded or excluded;
- do not encode white/coloured state, treatment, sex expression, cytotype or provisional taxon name;
- corrections are made in metadata, not by silently renaming the biological individual.

## Material/sample IDs

Material IDs extend the immutable individual ID.

| Material | Pattern | Example |
|---|---|---|
| DNA tissue/extract source | `-DNA##` | `EA26-P001-I001-DNA01` |
| flow-cytometry tissue/run source | `-FCM##` | `EA26-P001-I001-FCM01` |
| late-bud floral RNA | `-RLB##` | `EA26-P001-I001-RLB01` |
| anthesis floral RNA | `-RAN##` | `EA26-P001-I001-RAN01` |
| pigment tissue | `-PIG##` | `EA26-P001-I001-PIG01` |
| focal capitulum | `-CAP##` | `EA26-P001-I001-CAP01` |
| voucher | `-VCH##` | `EA26-P001-I001-VCH01` |

Use `##` only when multiple independent samples of one material type exist from the same individual.

## Plastid identity

Plastid history usually derives from a DNA sample rather than a separate biological individual. `plastid_source_sample_id` therefore points to the actual DNA/material ID used. Do not create a new `individual_id` for a plastid library.

## Aim 2 linkage

Every focal capitulum has its own `CAP` ID and is recorded in:

`sampling/aim2_capitulum_field_ledger_v1.csv`

The corresponding plant remains the same `individual_id`. Orientation treatment is metadata attached to the capitulum and is never encoded in the plant ID.

Plant-level seasonal display/predation observations are keyed by the same biological `individual_id` in:

`sampling/aim2_plant_display_predation_ledger_v1.csv`

## Aim 3 linkage

RNA and pigment samples must be written into `sampling/aim13_individual_sample_ledger_v1.csv` at collection time, including:

- sample ID;
- developmental stage;
- collection time;
- preservation method.

Late-bud and anthesis RNA are intentionally different material IDs from the same biological individual.

## Field assignment order

1. verify the planned population/site;
2. activate the corresponding `P###` population ID;
3. assign `individual_id` before collecting any tissue;
4. photograph/voucher-link the plant;
5. collect DNA and cytotype material;
6. assign Aim 2 `CAP` IDs if the individual enters a functional experiment;
7. assign Aim 3 `RLB` / `RAN` / `PIG` IDs when flowering-stage material is collected;
8. record any exclusion without recycling the ID.

## Prohibited identity practices

- no phenotype-coded IDs such as `WHITE01` or `PINK01`;
- no treatment-coded biological IDs such as `UP01` / `DOWN01`;
- no taxon-name-only IDs that become ambiguous after taxonomic revision;
- no separate person-made spreadsheet key for RNA or pigment that cannot be joined to `individual_id`;
- no recycling of an excluded or failed sample ID.
