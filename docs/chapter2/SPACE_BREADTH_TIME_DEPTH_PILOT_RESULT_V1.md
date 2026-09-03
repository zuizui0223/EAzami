# Chapter 2 spatial breadth × temporal depth pilot result v1

Status date: 2026-09-01  
Status: **INTERNAL FEASIBILITY RESULT — NOT A REQUIRED MANUSCRIPT RESULT**

## Decision

The two-axis Chapter 2 frame is empirically usable without using any trait × environment result as an entry condition.

The environment-free spatial pilot was run on the same authority-backed discrete trait ontologies used by the frozen temporal-depth analysis. Public GBIF geography was source-name guarded, filtered to Japan, spatially thinned at 0.1°, and summarized at the taxon level. A taxon required at least three thinned occurrence records for the primary spatial centroid.

Workflow: `33480007180`  
Artifact: `9789577849`  
Artifact SHA256: `315d0bedf241a7492ad2fcb26271bd459ab6f5d46a01a3ce032553d033f3aeb9`

The joined space × time synthesis was validated in workflow `33480348070`, artifact `9789676516`.

## Orientation

Spatial axis:

- 17 singleton-state taxa with usable geography;
- downward/nodding state: q90 taxon-centroid separation 925.6 km, maximum 1001.2 km;
- upward/erect state: q90 separation 1108.8 km, maximum 1420.5 km;
- spatial-segregation statistic = −96.7 km;
- permutation P = 0.370.

The sign of the segregation statistic means same-state taxon centroids are not more geographically clustered than different-state centroids in this pilot. Both states are geographically broad.

Temporal axis:

- ML minimum changes = 6;
- UFBoot minimum changes = 4–6, median 5;
- median relative-depth lower bound = 0.795;
- median upper bound = 0.994;
- fraction of UFBoot trees requiring at least one internal change in every minimum reconstruction = 0.628;
- fraction requiring at least one terminal change = 0.307.

Interpretation: orientation is spatially broad while its minimum-history depth remains mixed rather than purely terminal.

## Stickiness

Spatial axis:

- 12 singleton-state taxa with usable geography;
- nonsticky: q90 centroid separation 747.0 km, maximum 1044.4 km;
- sticky: q90 separation 823.4 km, maximum 982.7 km;
- spatial-segregation statistic = +146.2 km;
- permutation P = 0.131.

Both states remain geographically broad; the positive segregation tendency is not supported at the pilot threshold.

Temporal axis:

- ML and all UFBoot minimum changes = 5;
- median relative-depth interval = 0.937–0.954;
- every UFBoot tree requires at least one terminal and at least one internal change in every minimum reconstruction.

Interpretation: stickiness can be broadly distributed in current space while its repeated-change burden is concentrated toward relatively shallow lineage depth.

## Phyllary posture

Spatial axis:

- only four singleton-state taxa pass the spatial-support gate;
- the current primary space metric is therefore coverage-limited;
- the three ascending taxa alone span q90 1043.6 km and maximum 1117.1 km, but this is not enough for a balanced multi-state spatial inference.

Temporal axis:

- ML and all UFBoot minimum changes = 3;
- median relative-depth lower bound = 0.695;
- upper bound = 1.000.

Interpretation: the temporal history is well defined, but the comparable spatial breadth remains `not_evaluable`/limited under the singleton-state pilot.

## What the pilot establishes

It establishes only that **space breadth and time depth are separable empirical dimensions**.

Orientation and stickiness are both geographically broad under the current state-level geography, yet they differ in temporal-depth structure. Phyllary posture shows the complementary case: useful temporal information but insufficient primary spatial-state coverage.

No regression or correlation is fitted across only three modules, and no composite breadth-depth score is constructed.

## What this does not establish

- adaptation or environmental causation;
- historical range from current GBIF occurrences;
- trait state at every occurrence locality (authority state is taxon-level);
- convergence from repeated minimum changes;
- a requirement that these pilot numbers appear in the final paper.

The pilot's role is to validate the **spatial breadth × evolutionary depth** architecture before the final manuscript is rebuilt.
