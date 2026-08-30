# Chapter 2 space × time public-data audit v1

- Azami SHA: `03ed29f1f476ca0d0a1ea8e14e75cb0050a213ef`
- EAzami SHA: `4b00195b4ed5b900b39aa04c022a15a1a401df8d`

## Purpose

Freeze the public-data interface between **Azami = spatial breadth** and **EAzami = phylogenetic/historical depth**. The audit searches for orientation–precipitation and colour–solar evidence without treating narrative mentions as statistical results.

## Candidate machine-readable tables

### orientation_precipitation

| repository | path | rows read | detected columns |
| --- | --- | ---: | --- |
| eazami | `data/evidence/japan_radiation_pre_tree_trait_environment_snapshot_v1.csv` | 9 | `{"bio12": "env_chelsa_bio12_species_median", "bio15": "env_chelsa_bio15_species_median", "colour": "corolla_lab_lightness_median_taxon_median", "orientation": "orientation_angle_degrees_median_taxon_median", "taxon": "taxon_name"}` |

### colour_solar

| repository | path | rows read | detected columns |
| --- | --- | ---: | --- |
| eazami | `data/evidence/japan38_global_lightness_worldclim_summary_v1.csv` | 6 | `{"colour": "corolla_lab_lightness_median_species_median", "solar": "worldclim_srad_annual_mean_kj_m2_day_species_median", "taxon": "taxon_name"}` |

### orientation_trait_table

| repository | path | rows read | detected columns |
| --- | --- | ---: | --- |
| azami | `manuscript/figures/v2_submission/source/Figure_1_real_photo_measurement_provenance.csv` | 3 | `{"colour": "corolla_lab_lightness", "orientation": "orientation_status", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan38_azami_exhaustive_detection_to_strict_coverage_v1.csv` | 36 | `{"orientation": "strict_orientation_n", "taxon": "n_japan38_paper_concepts"}` |
| eazami | `sampling/JAPAN_WIDE_PHYLOGENY_ORIENTATION_ADDITION_PANEL_V1.csv` | 33 | `{"orientation": "nmns_orientation", "taxon": "taxon"}` |
| eazami | `data/evidence/japan38_nmns_capitulum_trait_seed_v1.csv` | 22 | `{"orientation": "orientation_state", "taxon": "paper_taxon_concept"}` |
| eazami | `data/evidence/fdt4_existing_material_join_audit_v1.csv` | 20 | `{"orientation": "orientation_state", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/comp1061_display_size_direct_seed_v1.csv` | 15 | `{"orientation": "orientation", "taxon": "taxon"}` |
| eazami | `data/evidence/japan38_azami_exhaustive_primary_trait_coverage_v1.csv` | 15 | `{"orientation": "n_orientation", "taxon": "azami_taxon_name"}` |
| eazami | `sampling/doctoral_field_tranche1_population_manifest_v1.csv` | 14 | `{"latitude": "latitude", "longitude": "longitude", "orientation": "aim2_orientation_candidate", "taxon": "taxon"}` |
| eazami | `data/evidence/japan_radiation_pre_tree_trait_environment_snapshot_v1.csv` | 9 | `{"bio12": "env_chelsa_bio12_species_median", "bio15": "env_chelsa_bio15_species_median", "colour": "corolla_lab_lightness_median_taxon_median", "orientation": "orientation_angle_degrees_median_taxon_median", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan38_image_authority_orientation_validation_v1.csv` | 8 | `{"orientation": "image_orientation_median_degrees", "taxon": "taxon_name"}` |
| eazami | `data/evidence/fdt4_eastasia_orientation_niche_phase2_queue_v1.csv` | 7 | `{"orientation": "orientation_state", "taxon": "accepted_taxon"}` |
| eazami | `external/azami/manuscript/figures/v2_submission/source/Figure_1_real_photo_measurement_provenance.csv` | 3 | `{"colour": "corolla_lab_lightness", "orientation": "orientation_status", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan38_nmns_capitulum_trait_seed_extension_v2.csv` | 2 | `{"orientation": "orientation_state", "taxon": "paper_taxon_concept"}` |
| eazami | `data/evidence/japan_radiation_priority_taxon_trait_recovery_v1.csv` | 2 | `{"orientation": "head_orientation", "taxon": "taxon"}` |
| eazami | `data/evidence/japan38_nmns_capitulum_trait_seed_extension_v1.csv` | 1 | `{"orientation": "orientation_state", "taxon": "paper_taxon_concept"}` |
| eazami | `data/schema/capitulum_trait_records.csv` | 0 | `{"latitude": "latitude", "longitude": "longitude", "orientation": "orientation_class", "taxon": "accepted_taxon"}` |
| eazami | `sampling/aim13_individual_sample_ledger_v1.csv` | 0 | `{"colour": "pigment_sample_id", "latitude": "latitude", "longitude": "longitude", "orientation": "natural_orientation_deg", "taxon": "taxon"}` |
| eazami | `sampling/aim2_capitulum_field_ledger_v1.csv` | 0 | `{"colour": "pigment_sample_id", "latitude": "latitude", "longitude": "longitude", "orientation": "natural_orientation_deg", "taxon": "taxon"}` |
| eazami | `sampling/jpn36_phyllary_access_eligible_heads_v1.csv` | 0 | `{"orientation": "natural_head_orientation_deg", "taxon": "taxon_identity_confirmed"}` |

### colour_trait_table

| repository | path | rows read | detected columns |
| --- | --- | ---: | --- |
| azami | `manuscript/figures/v2_submission/source/Figure_1_real_photo_measurement_provenance.csv` | 3 | `{"colour": "corolla_lab_lightness", "orientation": "orientation_status", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan38_global_colour_observation_coordinates_v1.csv` | 187 | `{"colour": "corolla_lab_lightness_median", "latitude": "latitude", "longitude": "longitude", "taxon": "taxon_name"}` |
| eazami | `data/evidence/east_asia_nuclear_coverage_v1_2026-08-10.csv` | 33 | `{"colour": "flower_colour_state", "taxon": "accepted_taxon"}` |
| eazami | `data/regional_master_taxa_seed.csv` | 33 | `{"colour": "flower_colour_state", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/cirsium_flower_colour_atlas_v0_2.csv` | 25 | `{"colour": "anthocyanin_visible", "latitude": "latitude", "longitude": "longitude", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/orientation_comp1061_20tip_source_crosswalk_v1.csv` | 20 | `{"colour": "state_label", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/cirsium_flower_colour_atlas_v0_1.csv` | 19 | `{"colour": "anthocyanin_visible", "latitude": "latitude", "longitude": "longitude", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/cnipponicum_flavonoid_family_reference_panel_v1.csv` | 18 | `{"colour": "function_label", "taxon": "reference_taxon"}` |
| eazami | `data/evidence/eazami_direct_colour_crop_per_head_v1.csv` | 18 | `{"colour": "median_lab_lightness", "taxon": "taxon_name"}` |
| eazami | `data/evidence/published_nuclear_phylogeny_coverage_seed.csv` | 15 | `{"colour": "flower_colour_state", "taxon": "taxon"}` |
| eazami | `data/evidence/japan38_colour_continuous_bridge_v1.csv` | 14 | `{"colour": "corolla_lab_lightness_species_median", "taxon": "paper_taxon_concept"}` |
| eazami | `data/evidence/eazami_direct_colour_crop_per_image_v1.csv` | 13 | `{"colour": "image_lightness_median", "taxon": "taxon_name"}` |
| eazami | `data/schema/phylogeny_gap_audit.csv` | 12 | `{"colour": "flower_colour_state", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/japan38_open_candidate_colour_measurement_per_image_v1.csv` | 10 | `{"colour": "median_lab_lightness", "latitude": "latitude", "longitude": "longitude", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan7_sparse_observation_lightness_v1.csv` | 10 | `{"colour": "corolla_lab_lightness_median", "latitude": "latitude", "longitude": "longitude", "taxon": "taxon_name"}` |
| eazami | `data/moreyra_japan_backbone_audit.csv` | 10 | `{"colour": "flower_colour_status", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/japan_radiation_pre_tree_trait_environment_snapshot_v1.csv` | 9 | `{"bio12": "env_chelsa_bio12_species_median", "bio15": "env_chelsa_bio15_species_median", "colour": "corolla_lab_lightness_median_taxon_median", "orientation": "orientation_angle_degrees_median_taxon_median", "taxon": "taxon_name"}` |
| eazami | `data/evidence/korea_cirsium_audit_2026-08-10.csv` | 9 | `{"colour": "flower_colour_evidence", "taxon": "taxon"}` |
| eazami | `data/evidence/japan7_source_balanced_lightness_input_v1.csv` | 7 | `{"colour": "local_lightness", "taxon": "taxon_name"}` |
| eazami | `data/evidence/korea_neasia_phylogeny_gap_matrix_2026-08-10.csv` | 7 | `{"colour": "flower_colour_role", "taxon": "taxon"}` |
| eazami | `data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv` | 6 | `{"colour": "figure1_panel_b_label", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv` | 6 | `{"colour": "published_figure_label", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv` | 6 | `{"colour": "direct_ncbi_colour_label", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv` | 6 | `{"colour": "direct_sample_morph_label", "taxon": "accepted_taxon"}` |
| eazami | `data/evidence/japan38_colour_geographic_provenance_summary_v1.csv` | 6 | `{"colour": "global_lightness_median", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan38_global_lightness_worldclim_summary_v1.csv` | 6 | `{"colour": "corolla_lab_lightness_median_species_median", "solar": "worldclim_srad_annual_mean_kj_m2_day_species_median", "taxon": "taxon_name"}` |
| eazami | `data/evidence/japan38_lightness_paired_environment_summary_v1.csv` | 6 | `{"bio12": "n_chelsa_bio12", "bio15": "n_chelsa_bio15", "colour": "corolla_lab_lightness_species_median", "taxon": "taxon_name"}` |
| eazami | `sampling/FIXED_WHITE_A1_SAMPLE_INTAKE_V0_1.csv` | 6 | `{"colour": "flower_colour_link_status", "taxon": "taxon"}` |
| eazami | `data/evidence/japan5_population_matched_lightness_input_v1.csv` | 5 | `{"colour": "local_lightness", "taxon": "taxon_name"}` |
| eazami | `sampling/FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv` | 5 | `{"colour": "flower_colour_link_required", "taxon": "taxon"}` |

### georeferenced_environment

No strict schema match found.

## Admission decision

Strict machine-readable candidates exist for both questions. Freeze exact paths and checksums in the next model contract before fitting joint spatial/phylogenetic models.

## Claim boundary

This inventory identifies reusable inputs and existing result statements. It does not make a new adaptive claim. BIO12 and BIO15 must be compared in the same admitted panel and colour–solar analysis must use a directly linked colour metric and radiation layer before cross-scale consistency is evaluated.
