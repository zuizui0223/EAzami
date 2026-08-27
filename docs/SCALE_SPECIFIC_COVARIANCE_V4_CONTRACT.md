# Scale-specific covariance v4 contract

Status: **frozen before any v4 family outcome is generated**.

## Why v4 is necessary

The registered v3.1 screen did not identify an adequate mechanism family. Every declared family produced too much integration among taxa. The observed capitulum-space pattern instead combines:

- moderate registered-module organization within taxa (`0.1645`);
- much weaker registered-module organization among taxa (`0.0885`);
- only partial correspondence between the two association matrices (`Spearman = 0.3663`);
- almost no process-environment increment beyond BIO1/BIO4/BIO12/BIO15 within taxa (`partial R2 = 0.0135`);
- substantial process-environment information beyond the same core among taxa (`partial R2 = 0.2150`);
- a growing-season-water increment that is negligible within taxa but detectable among taxa (`0.0020` versus `0.0787`).

The v3.1 result therefore changed the next question. Adding another environmental, pollinator or antagonist driver is not the immediate need. The missing structure is a way for covariance to form differently at different biological scales.

Version 4 asks:

> **Which predeclared covariance architecture can produce moderate within-taxon organization, weak among-taxon integration and stronger among-taxon process-environment structure without endpoint-specific tuning?**

The answer, if any, is a sufficient statistical architecture under declared priors. It is not automatically a biological mechanism.

## Shared layer

All five v4 families inherit the same full environmental + pollinator + antagonist interaction layer. That layer is not reopened, because v4 is designed to isolate the structural failure detected by v3.1 rather than confound covariance architecture with driver presence or absence.

All families must:

- generate 17 inferential units and 18 endpoint columns, with hue treated jointly;
- derive within- and among-taxon summaries from the same simulated taxa;
- retain signed endpoint values before association-strength matrices are constructed;
- use the same priors for all parameters they share;
- prohibit endpoint-specific tuning and outcome-conditioned prior truncation;
- introduce new parameters only globally, by registered module or exchangeably by inferential unit.

## Five nested structural families

### 1. `shared_scale_baseline`

The v3.1 common-lability covariance generator is retained unchanged. It is the failure reference against which every extension is judged.

### 2. `within_only_module_factor`

A module-level latent factor is added to local observations and is centred to exactly zero within every taxon. It can increase covariance within taxa but cannot enter taxon medians directly.

The current Azami data cannot tell whether such a factor is:

- local biological or developmental covariance;
- shared image/measurement covariance;
- or a mixture of both.

These interpretations are intentionally not split into separate families because they are statistically unidentifiable from the current seven targets. Repeat-photo remeasurement, developmental-stage labels and independent reference traits are the data needed to separate them.

### 3. `among_unit_mosaic_loadings`

Taxon-level process-environment effects use exchangeable inferential-unit loadings rather than one shared loading per registered module. The unit loadings are centred to zero mean within modules before use.

This allows environmental information to be strong in the full multivariate response without forcing all traits assigned to one module to move in the same direction among taxa. No unit is selected or assigned a prior based on its observed Azami loading or residual.

### 4. `combined_scale_decoupling`

The within-only module factor and among-unit mosaic loadings are combined. This is the minimal family that can independently alter both sides of the v3.1 failure: it can sustain within-taxon module organization while weakening module-wide among-taxon coherence.

### 5. `combined_scale_decoupling_with_rotation`

The combined family receives an additional low-rank taxon-level trait rotation. Its loading columns are orthonormal and independent of both environment and registered module labels; rank is drawn from one to three.

This is a generic historical/mosaic covariance term, not a phylogenetic model. It must not be called phylogeny without an explicit tree and phylogenetic covariance process.

## Primary fit layer

The same seven main-scope estimands used in v3.1 are retained without modification:

1. within-taxon module contrast;
2. among-taxon module contrast;
3. within/among association-matrix similarity;
4. all-process partial R2 beyond the four-variable core within taxa;
5. the same all-process partial R2 among taxa;
6. growing-season-water partial R2 within taxa;
7. the same growing-season-water partial R2 among taxa.

The v3.1 distance definition is reused exactly. The >=2 rows remain replication checks and are not counted again in the fit distance.

## Out-of-fit validation

Two validation layers are predeclared.

### Replication scope

The >=2 scope must retain six qualitative patterns:

- positive module contrast within taxa;
- positive module contrast among taxa;
- positive within/among matrix similarity;
- unsupported all-process extension within taxa;
- supported all-process extension among taxa;
- supported growing-season-water extension among taxa.

### Stand-alone environment-block context

Twelve main-scope stand-alone R2 values—six environmental blocks at each biological scale—are held outside the seven-target fit layer. Their root-mean-squared error is used only as a context-validation gate. Cross-scale coefficient cosines are excluded because their Azami bootstrap intervals are too uncertain for this purpose.

All v4 families inherit the same independent literature-heldout interaction score from the unchanged full-tradeoff common-lability interaction layer. That score is a safety check, not a discriminator among v4 covariance structures.

## Registered screen

- 750 draws per seed per family;
- four deterministic seeds;
- top 5% acceptance;
- at least 100 accepted draws per family;
- accepted median primary distance <= 1.0;
- accepted replication-pattern rate >= 0.75;
- each nonbaseline family must improve its declared parent by at least 15% in accepted median primary distance;
- stand-alone environment-block R2 RMSE may be no more than 5% worse than the parent;
- the nonbaseline family must be no worse than its parent in at least three of four seed-wise accepted medians.

If more than one nonnested family is adequate and their accepted median distances differ by less than 5%, the result is structural non-identifiability rather than a single winner. Among adequate near-tied families that are nested, the lower declared complexity level is preferred.

The baseline can never be promoted merely because extensions are worse; it must independently satisfy absolute adequacy.

## What a positive v4 result would and would not mean

An adequate family would identify a covariance architecture sufficient to reproduce the frozen Azami pattern bundle under the declared priors. It would not establish that:

- the within-only factor is biological rather than photographic;
- unit-mosaic environment loadings are caused by local adaptation;
- the rotation term is phylogenetic or historical;
- registered image modules are functional or genetic modules;
- growing-season precipitation is a causal selective agent;
- the adequate structure is the unique ecological or evolutionary mechanism.

The model result would instead determine which additional data should be collected next.

## Data needed to distinguish interpretations

To separate a within-only biological factor from an observation layer:

- remeasure traits across repeat photographs;
- label developmental stage;
- obtain independent reference measurements for the same endpoints.

To interpret an among-taxon rotation historically:

- use a resolved species tree;
- fit an explicit phylogenetic covariance model;
- incorporate ploidy and hybridization information.

## Machine-readable implementation boundary

- contract: `data/contracts/scale_specific_covariance_v4_contract.json`;
- validator: `analysis/validate_scale_specific_covariance_v4_contract.py`;
- tests: `tests/test_scale_specific_covariance_v4_contract.py`.

This contract PR validates the frozen sources, family nesting, structural constraints, seven unchanged fit targets, six replication patterns, twelve context R2 values and all promotion gates. It does not simulate or rank v4 families.
