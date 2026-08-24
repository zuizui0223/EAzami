# Sampling decisions

Current doctoral sampling source of truth:

1. `../data/evidence/doctoral_next_data_minimum_v1.csv` — the three unresolved new-data gates;
2. `SAMPLING_DESIGN.md` — field/material collection rules;
3. `doctoral_field_tranche1_population_manifest_v1.csv` — the 14 planned core populations summing to 190 individuals;
4. `SAMPLE_ID_CONVENTION.md` — immutable population/individual/material ID rules;
5. `../data/evidence/japan_radseq_phase_a_sampling_targets_v1.csv` — source counts and geographic constraints;
6. `aim13_individual_sample_ledger_v1.csv` — one biological individual linking DNA, plastid, cytotype, Aim 2 IDs, floral RNA and pigment;
7. `aim2_capitulum_field_ledger_v1.csv` — focal capitulum/treatment and final fitness outcomes, including standardized `colour_class`;
8. `aim2_capitulum_observation_bout_ledger_v1.csv` — repeated head-level time-window microclimate, display/density/colour-choice context, pollen state, pollinator-benefit and antagonist-cost observations;
9. `aim2_plant_display_predation_ledger_v1.csv` — plant-level seasonal display/predation outcomes;
10. `JAPAN_WIDE_PHYLOGENY_ORIENTATION_ADDITION_PANEL_V1.csv` — first-pass additions reverse-engineered from the current 38-taxon nuclear coverage, NMNS Japan-wide thistle inventory, origin exceptions, and orientation-state gaps.

Core rule: protect the 190-individual focal population panel before adding controls or sensitivity sampling.

## Japan-wide evolutionary-history layer

The Japan-wide backbone and the focal population layer answer different questions and use different sequencing designs.

### Backbone question

> Do the Japanese thistles represented in the much broader NMNS taxonomic/geographic inventory still resolve as one dominant Japanese radiation with rare secondary histories when the current 38-taxon Moreyra sampling is expanded, and how many independent orientation-state changes remain after northern/island gaps are filled?

For this layer, use **homologous nuclear target capture / Compositae1061-compatible data**, not RADseq as the primary species-tree assay. The first-pass addition panel prioritizes:

1. **northern Hokkaido orientation contrast** — missing upward and downward lineages from several NMNS subsections/series;
2. **origin falsifiers** — independent biological replication of `C. lineare` and `C. dipsacolepis`, plus clean wild replacement for conflicted/cultivated Japanese concepts;
3. **island/geographic extremes** — Izu, Ogasawara, Yakushima and southern coastal/island lineages;
4. **central/western orientation anchors** — upward and downward lineages from distinct NMNS subsections and substrates;
5. **wild replacement of existing tips** only after truly missing lineages are protected.

The target-capture rule is normally **two voucher-linked wild individuals per newly added taxon**, preferably from two localities for widespread taxa. Local or conservation-sensitive taxa may use herbarium/low-input DNA rather than destructive collection. Provisional NMNS `新称` concepts are hypotheses to test and require exact voucher/taxonomic verification before species-level promotion.

### Population-history question

RADseq remains a **population ancestry / gene-flow / standing-variation layer**, not a substitute for the common-locus Japan-wide species backbone. Use RADseq deeply only where it changes a doctoral decision: the core190 W/C systems, `C. lineare`, `C. dipsacolepis`, and selected contact/polymorphism systems such as the Rishiri `C. umezawanum`–`C. kamtschaticum` contact zone if feasible.

### Orientation rule

Do not code orientation only from a taxon name. Record the actual flowering head angle on the sequenced/vouchered plant wherever possible. NMNS is used to choose contrasts and prior states, but source conflicts or biomechanical drooping (for example heads hanging under their own weight rather than true nodding) remain explicit unresolved/alternative categories until voucher-level phenotyping resolves them.

Population-manifest rule: island/region and matching requirements may be predeclared, but an exact collection locality remains `TBD_field_verified` until the population is verified in the field or from a defensible current locality source. Do not invent coordinates to complete the planning table.

Identity rule: `individual_id` is immutable across Aims. RNA, pigment, cytotype and treatment IDs do not create new biological-individual identities. Phenotype and treatment are metadata and are not encoded in the biological ID.

Aim 2 joint-observation rule: repeated observations use `observation_bout_id` but remain linked to the same `capitulum_id`. Pollinator visits/effective contacts and antagonist events/damage stay as separate channels; final achene/seed output remains in the focal-capitulum ledger.

**Orientation timing rule:** retain `time_window_class` and do not collapse early-day bouts into an all-day visit total before testing the timing pathway. The same bout should retain head/air temperature, recent rain/wetness and pollen state where feasible so timing and abiotic protection can be evaluated separately.

**Pollinator context rule:** retain focal open-head display, quantitative local flowering-plant/open-head density and `heads_probed_total`. The four published *C. purpuratum* slopes do not justify unpooled year/site parameters; repeated contexts should later be partially pooled.

**Colour-choice rule:** record focal `colour_class` and local same/alternative-colour open-head availability within a defined `colour_choice_context_id`. Preference is evaluated as an availability-normalized selection ratio rather than raw visitor counts. The external *C. palustre* white-preference range is a soft calibration, not a `white always preferred` rule.

Detailed Aim 2 protocols:

- `../docs/AIM2_TRANCHE1_JOINT_OBSERVATION_PROTOCOL_2026-08-20.md`;
- `../docs/AIM2_FIELD_NESTING_PLAN_2026-08-18.md`.

Historical/conditional files remain for provenance but are not equal-priority sampling plans:

- `RADSEQ_PANEL_V0_1.csv`, `RADSEQ_PANEL_V0_2_EIG.csv` — earlier ranking lineage;
- `FIXED_WHITE_TARGET_CAPTURE_PANEL_V0_1.csv` — conditional target-capture layer;
- `SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv` — prior exact-coverage design;
- Chang/Read2Tree files — existing-data execution, not new field sampling.

Do not freeze broad continental collection targets until a current doctoral gate requires them.
