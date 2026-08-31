# Chapter 2 environmental state–trajectory framework v1

Status: 2026-08-31

## Central question

The paired Azami–EAzami programme should not ask only whether the same climate variable is statistically associated with a trait twice. The stronger Chapter 2 question is:

> **Do the environmental gradients that sort capitulum phenotypes across present-day space also describe the environmental trajectories through which those phenotypes were repeatedly assembled, or are the drivers of origin and present maintenance/sorting decoupled?**

This turns the two repositories into complementary estimands rather than duplicate association screens:

- **Azami = environmental state space.** Where do continuous capitulum phenotypes occur now, and along which present environmental gradients are they sorted?
- **EAzami = environmental trajectory space.** How often did states change, where in relative/dated history could those changes occur, and what environmental direction, volatility and extremes occurred through those admissible transition windows?
- **Cross-axis inference = state–trajectory concordance.** Does environmental movement through a historical transition point in the same multivariate direction as present trait sorting?

## Three competing biological models

### ST1 — persistent-driver concordance

The same environmental domain contributes both to historical transition and present sorting/maintenance.

Expected pattern:

1. repeated trait history;
2. a present Azami gradient;
3. a dated EAzami event window;
4. historical environmental change through that window points in the direction predicted by the present trait–environment relationship;
5. the direction is robust to palaeolocation uncertainty and more unusual than duration-matched non-event climate windows.

A positive result strengthens a persistent selective-pressure hypothesis but remains observational until mechanism and fitness are tested.

### ST2 — origin–maintenance decoupling

The current environment sorts or maintains states, but the transition itself did not occur during a correspondingly directed environmental trajectory.

Expected pattern:

- strong present space/niche association;
- repeated history;
- historical event windows are typical, directionally opposite, or unrelated to the current gradient.

This is not a failed analysis. It predicts that present niche correspondence cannot be used as a proxy for the original transition driver. Possible biological explanations include post-origin range sorting, later niche tracking, changing selective agents, correlated environmental packages, or historical contingency.

The current local Taiwan orientation result already motivates this model: BIO15 changes strongly enough to approach the predeclared tail in absolute magnitude but decreases toward the descendant D lineage, whereas present D taxa occupy higher-BIO15 niches; BIO1 warms across the broad branch interval whereas present D taxa occupy cooler niches. Because the exact transition instant is unresolved within the 0.79–0.47 Ma branch, this is evidence against a simple same-direction historical story, not proof of decoupling.

### ST3 — driver switching / selection mosaic

Different transitions or geographic radiations are associated with different environmental dimensions.

Expected pattern:

- different event windows align with different environmental axes;
- present global sorting may reflect the aggregate distribution of multiple historical pathways;
- capitulum modules need not share one synchronized selective history.

This model is compatible with the existing asymmetry among orientation, colour, phyllary posture and stickiness, but it requires multiple dated transition windows before it can be tested as an event-level model.

## Environmental panel: mechanism before variable count

### A. Shared state–trajectory core

Use **BIO1, BIO4, BIO12 and BIO15** because all four are present in the frozen Azami atlas and PALEO-PGEM-Series. These four define the primary commensurate space for the multivariate state–trajectory test.

Do not select only individually significant Azami dimensions. The four-dimensional Azami orientation beta vector is frozen before seeing the historical trajectory result.

### B. Orientation wetting-mechanism refinement

Use:

- **BIO13** — precipitation of wettest month;
- **BIO16** — precipitation of wettest quarter.

These are closer to concentrated wet exposure than annual precipitation, although they remain monthly/quarterly climatic proxies rather than direct rainfall-on-flowers measurements.

Use as negative/control dimensions:

- **BIO14** — precipitation of driest month;
- **BIO17** — precipitation of driest quarter.

A wetting-specific explanation is more credible if wet-side environmental dynamics are exceptional relative to dry-side dynamics under the same event-window null.

### C. Secondary climate variables

BIO5/BIO6/BIO7 and BIO8–BIO11 can describe thermal extremes and seasonal thermal regimes. BIO18/BIO19 can describe precipitation in warm/cold quarters. They are not primary cross-axis tests because Azami does not currently use the exact same predictors, and BIO18/BIO19 must not be relabelled as flowering-season precipitation without taxon-specific phenology.

### D. Do not force false historical equivalents

The following Azami axes do not currently have a directly commensurate PALEO-PGEM time series:

- surface shortwave radiation (RSDS);
- VPD;
- surface wind;
- growing-season precipitation under the exact Azami definition;
- NPP.

Adding orbital insolation, humidity reconstruction, wind modelling, generic growing-season rules or vegetation productivity models would add a new model layer. Such analyses can be future sensitivities but must not be called direct replication of the Azami predictor.

## Resolution determines the estimand

PALEO-PGEM-Series has **1-kyr temporal resolution** but **1° spatial resolution**. The local Taiwan orientation event window is 320 kyr long, giving high temporal sampling but coarse palaeolocation resolution.

In the first BIO12/BIO15 local run:

- BIO12 Taiwan regional spatial IQR / within-window temporal SD ≈ 11.6;
- BIO15 Taiwan regional spatial IQR / within-window temporal SD ≈ 12.1.

Therefore Chapter 2 should not attempt pointwise mountain-palaeoclimate inference. The defensible estimands are:

1. regional event-window level;
2. direction of change;
3. temporal volatility and extremes;
4. duration-matched extremeness;
5. cellwise sign agreement across the palaeolocation uncertainty set;
6. multivariate trajectory direction.

A result that changes sign among plausible 1° cells is unresolved, even if the regional median is extreme.

## New primary statistic: state–trajectory concordance

For the shared variables BIO1/BIO4/BIO12/BIO15 define:

- **β_space** = the frozen standardized Azami among-taxon orientation slope vector;
- **ΔE_time** = the event-window young-minus-old environmental change vector, standardized against all duration-matched historical windows.

Then calculate:

`cosine(β_space, ΔE_time)`.

Interpretation:

- positive: historical environmental movement points in the same multivariate direction as current trait sorting;
- near zero: no directional state–trajectory correspondence;
- negative: historical movement is directionally discordant with current sorting.

Its reference distribution is the cosine calculated for every same-duration background climate window using the same frozen Azami vector. This tests the joint direction rather than manufacturing a result from whichever single BIOCLIM variable is most extreme.

## Chapter 2 contribution

The intended contribution is therefore broader than “orientation correlates with precipitation”:

> **Present phenotypic breadth and evolutionary depth are linked by testing whether contemporary environmental state-space structure is retained in, or decoupled from, the environmental trajectories surrounding repeated trait assembly.**

If ST1 is supported, multiple independent space–time views converge on a candidate pressure. If ST2 is supported, current ecological sorting is shown not to be a safe surrogate for transition causation. If later events support different axes, ST3 provides an explicit selection-mosaic explanation.

All three outcomes are informative and preserve unsupported traits rather than filtering the story to positive associations.

## Claim ceiling

State–trajectory concordance or discordance does not by itself establish natural selection, adaptation, convergence, ancestral niche, exact transition date, or reproductive fitness. Those require mechanism and fitness evidence downstream.
