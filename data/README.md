# Data layout

EAzami separates evidence from schema so that a plausible value cannot silently become a validated observation.

- `evidence/`: source-backed ledgers, exact public identifiers, reviewed extractions and validation summaries.
- `schema/`: empty or template contracts defining required fields and controlled states.
- `phylogeny/`: versionable tree inputs or compact phylogenetic products when present.

Every direct observation should retain a source citation and exact locator. Conflicts and missing values remain visible. Inferred or automatically extracted values must carry a non-validated evidence state until manual review.

The capitulum-trait seed contract is [schema/capitulum_trait_records.csv](schema/capitulum_trait_records.csv); its interpretation is defined in [the trait foundation](../docs/CAPITULUM_TRAIT_FOUNDATION.md).
