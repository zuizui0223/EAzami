# Japan38 colour–climate gate v1

Status: exploratory follow-up to the frozen continuous-colour history result.

## Question

The canonical Japan38 colour analysis found a stable anti-phylogenetic / overdispersed pattern in image-derived corolla LAB lightness, strongest in the higher-evidence subsets. This gate asks one narrower question:

> Do taxa occupying more different present-day climates also differ more in corolla lightness, such that current climate could plausibly account for the observed anti-phylogenetic lightness placement?

## Primary analysis

- exact Japan38 concepts only;
- corolla LAB lightness comes from `japan38_colour_continuous_bridge_v1.csv`;
- current climate uses species-median CHELSA BIO1, BIO4, BIO12 and BIO15 from `japan_radiation_pre_tree_trait_environment_snapshot_v1.csv`;
- minimum environment evidence depth: 10 balanced observations;
- colour evidence thresholds: at least 5 and at least 10 usable colour observations;
- primary predictor: Euclidean distance in four-axis climate space after within-subset z-standardization;
- response: absolute pairwise LAB-lightness difference;
- inference: exhaustive permutation of lightness labels across taxa;
- sensitivity: partial Spearman controlling canonical Japan38 patristic distance, axis-specific distance tests, directional single-axis rank tests and leave-one-taxon-out recomputation.

## Frozen decision rule

Present-day four-axis climate tracking is supported only if:

1. multivariate climate distance is positively associated with lightness difference in the n>=5 subset;
2. the exact positive-tail permutation p-value is <=0.05;
3. the n>=10 subset has the same positive direction; and
4. every leave-one-out n>=5 analysis remains positive.

This intentionally makes the climate explanation earn support rather than treating any environment correlation as sufficient.

## Boundaries

This is not a causal climate-adaptation test. Colour and climate are separate species-level evidence layers, not measurements on the same individuals. The four CHELSA variables represent current climate only; historical climate, biotic interactions, soil, radiation, wind and unmeasured environments remain outside this gate. Secondary axis screens are exploratory and are not confirmatory multiple-hypothesis tests.
