# Capitulum-trait foundation for future adaptive-radiation tests

## Purpose

EAzami's immediate question is flower-colour history, but the same population-aware nuclear backbone can support a later test of whether capitulum form diversified repeatedly with environment, pollination or lineage history. This document creates the data contract without claiming that adaptive radiation has already been shown.

The motivating observation is deliberately weak: *C. schantarense* was reported with nodding capitula and *C. japonicum* with upward-facing capitula despite close placement in one ITS neighbour-joining analysis. One linked multicopy genealogy cannot demonstrate repeated trait evolution. Dense nuclear loci, population sampling and explicit trait mapping are required.

## Unit of observation

Prefer an individual plant linked to a voucher and population. A published population or taxon summary may be entered when individual data are unavailable, but `observation_level` and `replicate_count` must make that aggregation explicit.

Identifiers are carried across both phylogenomic layers:

- `record_id`: immutable trait-record identifier;
- `individual_id` and `population_id`: population-history linkage;
- `voucher_id`: specimen and taxonomic audit linkage;
- `phylogeny_tip_id`: accepted nuclear-tree linkage;
- `accepted_taxon` and `source_taxon_name`: reconciled and verbatim names kept separately.

## Initial trait set

The seed schema records:

- capitulum position and orientation;
- orientation angle, defined as 0 degrees upward, 90 degrees horizontal and 180 degrees downward;
- capitulum and involucre dimensions;
- peduncle length;
- phyllary spine length and apex class;
- floret count;
- phenophase, elevation and habitat context;
- protocol, replicate count, evidence state and exact source locator.

Do not infer a continuous angle from a verbal category unless the record remains in an unreviewed or unresolved evidence state.

## Evidence states

Use one of these states:

- `direct_field_measurement`
- `direct_specimen_measurement`
- `direct_image_measurement`
- `source_reported`
- `source_backed_rule_extracted_unreviewed`
- `unresolved`

Automated extraction never becomes a model-ready direct observation without review. Missing values, conflicting descriptions and inaccessible sources remain explicit rather than being imputed in the evidence table.

## Phylogenetic acceptance gate

A record can be marked `model_eligible=true` only when it has an exact evidence locator, a documented measurement protocol and a reconciled `phylogeny_tip_id`. Model eligibility does not mean that the backbone itself is accepted: comparative analyses must additionally use trees that passed the sensitivity gate in [PROJECT_STATUS.md](../PROJECT_STATUS.md).

## Analysis sequence and claim ceiling

1. Validate the schema and identifier joins.
2. Quantify within-population and among-population variation before calculating species summaries.
3. Map traits over the accepted tree ensemble rather than one preferred tree.
4. Compare transition counts and rates across topology, ploidy and reticulation sensitivities.
5. Test trait-environment or trait-pollination associations with phylogenetic and spatial structure accounted for.
6. Call adaptive radiation only if diversification, repeated trait evolution and an ecological performance association are jointly supported.

Until step 6, permitted language is limited to trait variation, phylogenetic distribution, repeated-transition candidates and tested associations.

## Files

- Schema: [data/schema/capitulum_trait_records.csv](../data/schema/capitulum_trait_records.csv)
- Validator: [analysis/validate_capitulum_trait_records.py](../analysis/validate_capitulum_trait_records.py)
- Tests: [tests/test_validate_capitulum_trait_records.py](../tests/test_validate_capitulum_trait_records.py)
