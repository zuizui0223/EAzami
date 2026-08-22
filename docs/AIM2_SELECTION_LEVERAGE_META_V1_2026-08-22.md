# Aim 2 selection-leverage meta-analysis v1 — 2026-08-22

## Question

The current interaction-gate programme asks whether the strength of biotic selection can be predicted from a simple variable such as:

- interaction intensity alone (`pollen limitation`, enemy pressure);
- broad trait class alone (`attraction`, `efficiency`, `phenology`);

or whether realised selection requires a more local mechanism:

`interaction opportunity × trait-to-interaction functional leverage × downstream fitness gate`.

The multiplication sign is a conceptual factorisation, not a fitted mechanistic equation.

## Restricted experimental-gradient dataset

The primary registry contains exact published standardized directional selection gradients from six independent articles / six taxa:

1. *Dactylorhiza lapponica* — DOI `10.1111/j.1469-8137.2010.03296.x`;
2. *Anacamptis morio* — DOI `10.1111/evo.12881`;
3. *Primula alpicola* — DOI `10.1038/s41598-017-13340-0`;
4. *Gymnadenia conopsea* — DOI `10.1111/nph.15747`;
5. *Spiranthes sinensis* — DOI `10.1093/jpe/rtaa033`;
6. *Lobelia siphilitica* — DOI `10.1002/ece3.10706`.

There are 41 registry rows, of which 38 prospectively classified floral gradients enter the primary analysis. A vegetative condition covariate and an uncertain display-architecture trait are retained but excluded.

The sample is small and orchid-heavy. It is an independent restricted validation exercise, not a replacement for Caruso et al. 2019 (`10.1111/evo.13639`).

## Analysis

The response is the magnitude of experimentally isolated pollinator-mediated directional selection:

`|Δβpoll| = |βopen − βhand|`.

To prevent pseudo-replication by articles that measured more traits or contexts:

1. rows are first collapsed to one mean per `article × functional class`;
2. class contrasts use only articles containing both classes;
3. exact two-sided sign-flip tests operate on article-paired differences;
4. leave-one-article-out ranges assess dominance by a single article;
5. a truncated noise-subtracted magnitude is retained only as a sensitivity.

Repeated years in *Spiranthes* and ambient/reduced contexts in *Lobelia* remain nested within their article cluster.

## Result 1 — broad functional class does not identify a universal hierarchy in this restricted set

Article-balanced mean `|Δβpoll|`:

- pollination efficiency: **0.1437** (3 articles);
- flower sensory/display: **0.1180** (6);
- phenology: **0.0991** (4);
- plant-level display: **0.0952** (5).

No article-paired functional-class contrast is identified at `P < 0.05`.

Examples:

- efficiency − flower sensory: mean **+0.0599**, `n=3`, exact `P=1.0`; leave-one-article-out range reaches approximately zero;
- efficiency − plant display: **+0.0270**, `n=3`, exact `P=0.50`;
- plant display − flower sensory: **+0.0235**, `n=5`, exact `P=0.50`;
- phenology − plant display: **−0.0053**, `n=4`, exact `P=1.0`;
- phenology − flower sensory: **+0.0291**, `n=4`, exact `P=0.875`.

In the post-2018 sensitivity subset, article-balanced class means are even more similar (approximately **0.052–0.067**).

### Interpretation

This restricted result does **not** overturn the larger Caruso et al. meta-analysis, which found stronger average pollinator-mediated selection on efficiency traits. It does show that a broad trait label by itself is not a reliable local predictor in this independent small validation set.

For EAzami, `orientation`, `colour`, `display`, and validated `phyllary/spine` therefore should not receive fixed selection-strength priors merely because they belong to a presumed functional class.

## Result 2 — increasing pollen limitation does not strengthen every trait uniformly

Brown & Caruso 2023 experimentally reduced pollinator access in *Lobelia siphilitica*.

Pollen-limitation log response ratio increased from:

- ambient: **0.062 ± 0.065**;
- reduced pollinator access: **0.259 ± 0.072**.

Using the seed-per-plant pollinator-mediated selection gradients for the same six traits:

- mean change in `|Δβpoll|` = **+0.0198**;
- **4/6** traits became stronger;
- **2/6** became weaker;
- exploratory exact paired sign-flip `P=0.25`.

The largest increases were for inflorescence height and petal chroma, while corolla tube length weakened.

Thus higher pollen limitation increased the opportunity for pollinator-mediated selection but did not impose a uniform response across traits.

## External triangulation

Two independent published analyses sharpen the interpretation.

### Across species — interaction intensity matters

Trunschke et al. 2017 (`10.1111/nph.14479`) compared 12 orchid species. Pollen limitation strongly predicted the strength of pollinator-mediated selection (`F=18.79`, `P<0.001`), while their five-trait factor was not significant (`F=0.42`, `P=0.793`) and the pollen-limitation × trait interaction was not significant (`F=0.69`, `P=0.604`).

This supports interaction intensity as a source of **opportunity for selection** across species.

### Within species — intensity is not enough

Sletvold & Ågren 2014 (`10.1111/evo.12405`) found that within-species variation in pollen limitation did not explain variation in pollinator-mediated selection for any trait. They concluded that variation in the functional relationship between trait expression and pollination success explains an important part of spatial and temporal variation in selection.

This is the key reason not to use pollen limitation, visitation, or enemy abundance as a stand-alone selection proxy.

## Refined EAzami hypothesis — local functional leverage

The current best working mechanism is:

> **interaction intensity opens an opportunity for selection, but the realised trait-specific selection gradient depends on how strongly local trait variation changes effective interaction success and whether that interaction difference is transmitted to fitness.**

Operationally:

### Pollination side

`trait variation -> effective contact / pollen delivery -> filled achenes`

Functional leverage is the local slope or treatment contrast linking the focal trait to effective pollination, not the trait's broad category.

### Antagonist side

`trait variation -> antagonist access/damage -> filled achenes`

Enemy pressure can be high while selection on a trait remains weak if that trait does not change enemy access or if compensation/gating prevents damage from reaching fitness.

### Downstream demographic side

`seed difference -> safe-site / disturbance / density gate -> recruitment`

A strong seed-fitness contrast can still disappear downstream.

## Model comparison to run on focal field data

The field programme should compare, in order:

1. **broad-environment model** — climate/microclimate predicts fitness directly;
2. **interaction-intensity model** — pollinator/antagonist abundance predicts fitness;
3. **broad-functional-class model** — module labels carry fixed effects;
4. **local-leverage model** — module-specific `trait -> effective interaction -> seed fitness` paths with local context;
5. **shared vs module-specific response model** — tests common lability against multi-stage modularity.

The local-leverage model is supported only if it improves out-of-sample prediction / information criterion relative to the simpler alternatives without proliferating unpooled population parameters.

## Focal predictions

- **Orientation:** total daily visitation may remain unchanged while time-window effective contacts, head temperature, wetting or pollen viability change strongly; this is high local leverage despite a weak all-day attraction effect.
- **Colour:** leverage should depend on local colour availability and pollinator composition; a fixed `white preferred` coefficient is not expected.
- **Display:** leverage can be bidirectional because display changes both probing and antagonist exposure.
- **Phyllary/spine:** enemy pressure is not enough; direct botanical variation must first predict antagonist access/damage before a defence-selection interpretation is allowed.

## Claim boundary

This meta-analysis identifies what is **not sufficient**: broad trait class and interaction intensity alone. It does not yet estimate a universal multiplicative selection function, and it contains no direct *Cirsium* selection-gradient experiment. The new leverage hypothesis remains to be tested in ancestry-resolved focal populations using the existing Aim 2 ledgers and factorial treatments.
