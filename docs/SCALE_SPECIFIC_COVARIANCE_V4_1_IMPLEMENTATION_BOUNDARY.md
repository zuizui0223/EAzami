# Scale-specific covariance v4.1 implementation boundary

Status: **implementation correction made before any v4 family outcome was inspected**.

## Superseded run

The first v4 implementation workflow, run `33043095287`, had entered the full-screen step when an estimand mismatch was identified. No result, job log or artifact from that run was inspected. The run is superseded and must not be interpreted or recorded as a scientific result.

## The mismatch

The frozen v4 contract defines `within_only_module_factor` as a local factor that can change within-taxon covariance but cannot enter taxon-level summaries directly. The first implementation generated normal factor values and centred them to exact zero **mean** within each taxon.

Azami's among-taxon phenotype estimand uses taxon **medians**, not means. A sample can have zero mean but nonzero median, especially with five or six observations per taxon. Mean-centering therefore did not guarantee that the supposedly within-only factor was absent from the among-taxon median geometry.

This was an implementation inconsistency, not an outcome-dependent scientific revision.

## v4.1 correction

The only changed component is the local factor generator. Within each taxon and registered module, values are now generated in `+x/-x` pairs; odd replication receives one exact zero. Rows are randomly assigned to population observations within the taxon.

Consequently, before unit loadings are applied, each local factor has:

- exact taxon mean `0`;
- exact taxon median `0`.

Multiplication by a taxon-constant unit loading preserves both properties. The latent hue effect is still added before sine/cosine endpoints are reconstructed.

## Unchanged scientific design

The following remain exactly as frozen before the superseded run:

- five nested structural families;
- shared full environment + pollinator + antagonist baseline;
- all numerical prior ranges;
- 17 inferential units / 18 endpoints;
- seven main-scope fit targets and their distance;
- six >=2 replication patterns;
- twelve stand-alone environment-block R2 context targets;
- 750 draws per seed, four seeds and top-5% acceptance;
- absolute adequacy, replication, parent-improvement, context and seed-wise gates;
- complexity and structural-non-identifiability rules;
- all claim boundaries.

The amended implementation-prior version is `scale_specific_covariance_v4_1_implementation_priors_2026-08-27`. Only a workflow using `analysis/simulate_scale_specific_covariance_v4_1.py` is interpretable.

## Claim boundary

This correction guarantees alignment between the declared within-only factor and the taxon-median estimand. It does not make the factor biological. If a v4.1 family containing this factor is adequate, current Azami data still cannot separate local biological/developmental covariance from shared photographic or measurement covariance. Repeat-photo trait remeasurement, developmental-stage labels and independent reference traits remain necessary for that distinction.
