# Japan38 colour–climate gate v1

Status: **executed; current four-axis climate tracking not supported**.

## Question

The canonical Japan38 colour analysis found a stable anti-phylogenetic / overdispersed pattern in image-derived corolla LAB lightness, strongest in the higher-evidence subsets. This gate asked one narrower question:

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

Present-day four-axis climate tracking was defined as supported only if:

1. multivariate climate distance was positively associated with lightness difference in the n>=5 subset;
2. the exact positive-tail permutation p-value was <=0.05;
3. the n>=10 subset had the same positive direction; and
4. every leave-one-out n>=5 analysis remained positive.

The rule was fixed in `japan38_colour_climate_gate_contract_v1.json` before the real-data CI result was interpreted.

## Result

### n>=5 colour observations: 6 concepts

JPN_17, JPN_23, JPN_29, JPN_36, JPN_37 and JPN_38.

- patristic distance vs absolute lightness difference: rho = **-0.7071**;
- patristic distance vs four-axis climate distance: rho = **0.075**;
- four-axis climate distance vs absolute lightness difference: rho = **-0.3286**;
- exhaustive permutations: **720**;
- exact positive-tail p = **0.8222**;
- exact two-sided p = **0.4083**;
- partial rho controlling patristic distance = **-0.3908**, two-sided p = **0.3875**;
- all six leave-one-taxon-out primary associations remained negative, rho range **-0.4303 to -0.0667**.

### n>=10 colour observations: 5 concepts

JPN_17, JPN_23, JPN_36, JPN_37 and JPN_38.

- patristic distance vs absolute lightness difference: rho = **-0.8545**;
- patristic distance vs four-axis climate distance: rho = **-0.0424**;
- four-axis climate distance vs absolute lightness difference: rho = **-0.2970**;
- exhaustive permutations: **120**;
- exact positive-tail p = **0.6917**;
- exact two-sided p = **0.6333**;
- partial rho controlling patristic distance = **-0.6422**, two-sided p = **0.1083**.

No single BIO axis showed a directional association that passed a two-sided 0.05 screen in both subsets. BIO15 was directionally negative in both subsets (rho -0.714 and -0.800), but its exact two-sided p-values were 0.136 and 0.133, so it remains a descriptive lead rather than a supported mechanism.

## Interpretation

The frozen gate fails clearly. The simplest current-climate convergence model predicts that taxa with similar current climates should occupy similar lightness states and that greater climate separation should therefore accompany greater lightness separation. The observed primary associations have the **opposite sign** in both evidence-depth subsets, and the six-taxon result stays negative after every leave-one-out removal.

Therefore the currently available **BIO1/BIO4/BIO12/BIO15 species-level climate summary does not explain the Japan38 lightness overdispersion**.

This result sharpens the next mechanism search rather than ending it. The remaining live classes are:

1. **unmeasured current abiotic axes** such as radiation, vapour-pressure/aridity, wind and potentially substrate/soil;
2. **historical rather than current climate**, especially if repeated lightness shifts track past regime changes;
3. **biotic interactions**, including pollinator and floral-enemy regimes;
4. **population-level colour variation / taxon-level averaging**, because image-derived species medians are not fixed species states;
5. other forms of **module-specific evolutionary history** unrelated to one shared whole-capitulum lability axis.

## Boundaries

This is not a causal climate-adaptation test. Colour and climate are separate species-level evidence layers, not measurements on the same individuals. The four CHELSA variables represent current climate only; historical climate, biotic interactions, soil, radiation, wind and other unmeasured environments remain outside this gate. Secondary axis screens are exploratory and are not confirmatory multiple-hypothesis tests. The result does not establish convergence, adaptation, evolutionary rate or ancestral colour.
