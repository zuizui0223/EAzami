# Sampling decisions

Current doctoral sampling source of truth:

1. `../data/evidence/doctoral_next_data_minimum_v1.csv` — the three unresolved new-data gates;
2. `SAMPLING_DESIGN.md` — field/material collection rules;
3. `doctoral_field_tranche1_population_manifest_v1.csv` — the 14 planned core populations summing to 190 individuals;
4. `SAMPLE_ID_CONVENTION.md` — immutable population/individual/material ID rules;
5. `../data/evidence/japan_radseq_phase_a_sampling_targets_v1.csv` — source counts and geographic constraints;
6. `aim13_individual_sample_ledger_v1.csv` — one biological individual linking DNA, plastid, cytotype, Aim 2 IDs, floral RNA and pigment;
7. `aim2_capitulum_field_ledger_v1.csv` — focal capitulum/treatment and final fitness outcomes;
8. `aim2_capitulum_observation_bout_ledger_v1.csv` — repeated head-level microclimate, pollinator-benefit and antagonist-cost observations;
9. `aim2_plant_display_predation_ledger_v1.csv` — plant-level seasonal display/predation outcomes.

Core rule: protect the 190-individual focal population panel before adding controls or sensitivity sampling.

Population-manifest rule: island/region and matching requirements may be predeclared, but an exact collection locality remains `TBD_field_verified` until the population is verified in the field or from a defensible current locality source. Do not invent coordinates to complete the planning table.

Identity rule: `individual_id` is immutable across Aims. RNA, pigment, cytotype and treatment IDs do not create new biological-individual identities. Phenotype and treatment are metadata and are not encoded in the biological ID.

Aim 2 joint-observation rule: repeated microclimate and interaction observations use `observation_bout_id` but remain linked to the same `capitulum_id`. Pollinator visits/effective contacts and antagonist events/damage stay as separate channels; do not collapse them into generic insect activity. Final achene/seed output remains in the focal-capitulum ledger.

Detailed Aim 2 protocol: `../docs/AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md`.

Historical/conditional files remain for provenance but are not equal-priority sampling plans:

- `RADSEQ_PANEL_V0_1.csv`, `RADSEQ_PANEL_V0_2_EIG.csv` — earlier ranking lineage;
- `FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv` — conditional target-capture layer;
- `SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv` — prior exact-coverage design;
- Chang/Read2Tree files — existing-data execution, not new field sampling.

Do not freeze broad continental collection targets until a current doctoral gate requires them.
