# FDT1 stickiness primary-manipulation evidence audit (2026-08-26)

## Disposition

The bounded search recovered **two independent primary experiments outside the already-used Aquilegia, Bejaria, Datura and Cirsium systems**:

1. *Passiflora foetida*: removal of sticky, glandular bracts increased damage to developing buds, but the manipulation removed the entire bract package and did not isolate adhesion from physical enclosure. The quantitative result is usable as a **compound defensive-envelope/stickiness calibration**, not as a pure glandular-trichome effect.
2. *Erica plukenetii*: experimentally added corolla stickiness sharply reduced nectar-robbing damage, whereas adding stickiness only to the inflorescence base did not. This is the cleaner **stickiness-location manipulation**, but the accessible primary materials do not report a fruit or seed endpoint.

Therefore FDT1 can add an independent causal calibration for `stickiness / sticky reproductive envelope -> reproductive-enemy damage or access`. It still cannot infer `stickiness -> fruit or seed fitness` from these studies. No new fitness effect-size row should be created from either experiment.

## Admission rule used here

A study had to:

- be a primary experimental report;
- manipulate stickiness, glandular reproductive structures, or a reproductive structure whose sticky glands are part of the removed treatment;
- report damage or access by an antagonist to buds, flowers, inflorescences or developing fruit;
- be independent of the four systems named above;
- provide numerical results directly in the primary article or its publisher-hosted supplement.

P-values were not converted into effect sizes. Values visible only through secondary summaries were not extracted.

## Study 1 — *Passiflora foetida*: sticky glandular-bract removal

### Identity and primary source

Radhamani, T. R., Sudarshana, L. & Krishnan, R. (1995). Defense and carnivory: dual role of bracts in *Passiflora foetida*. *Journal of Biosciences* 20(5):657–664. DOI: [10.1007/BF02703305](https://doi.org/10.1007/BF02703305). [Primary article PDF hosted by Washington State University](https://rex.libraries.wsu.edu/view/pdfCoverPage?download=true&filePid=13332946560001842&instCode=01ALLIANCE_WSU); [repository record and provenance](https://rex.libraries.wsu.edu/esploro/outputs/journalArticle/Defense-and-carnivory-Dual-role-of/99900502417801842).

The author names in the repository metadata differ slightly from the names printed in the article. The identity above follows the version-of-record PDF.

### System and manipulation

- Study material: wild *P. foetida* on the University of Agricultural Sciences GKVK campus, Bangalore, India.
- Reproductive structure: three reticulate green bracts cover each unopened bud and developing fruit. Their vein tips bear glands that secrete an adhesive exudate; open one-day flowers are not covered.
- Experimental unit and blocking: 10 tagged plants. On one branch of each plant, the authors detached bracts from all developing reproductive stages; the adjacent branch with intact bracts served as the control.
- Observation window: developing buds and fruits were monitored for three consecutive days for predator damage.
- Independence: this is a distinct species, plant family, research group and experimental site from the four excluded systems.

### Exact quantitative result

Table 3 of the primary article reports:

| stage | bracts intact | bracts removed | test |
|---|---:|---:|---:|
| bud | `N = 92`; damage `17.65 ± 25.11%` | `N = 32`; damage `55.82 ± 35.82%` | `t = 5.95`, `p < 0.01` |
| developing fruit | `N = 29`; damage `66.66 ± 35.11%` | `N = 19`; damage `64.50 ± 38.50%` | `t = 0.18`, not significant |

The bud-stage contrast is a descriptive increase of 38.17 percentage points, or 3.16-fold relative to the intact-bract mean. These derived summaries are arithmetic descriptions, not cluster-adjusted effect estimates.

The same article reports that the bracts trapped insects from 10 families and that most trapped insects were phytophagous. It does not identify the organisms that caused the experimental bud or fruit damage.

### Extractability and independence boundary

The paper gives exact arm summaries and a test statistic, but the 10 plants—not the 92, 32, 29 or 19 reproductive structures—are the biological replicate clusters. It does not report plant-level paired outcomes, within-plant covariance, or cluster-adjusted standard errors. A conventional two-arm sampling variance calculated from the structure counts would therefore overstate independence.

Recommended FDT1 handling:

- admit the direction and exact descriptive contrast as an independent experimental calibration;
- code the intervention as `sticky_glandular_bract_package_removed`, not `stickiness_removed`;
- code the trait specificity as `compound: adhesion + physical enclosure + bract chemistry`;
- do not pool it as a precise inverse-variance effect until plant-level outcomes or their covariance are recovered.

### Claim boundary

This experiment shows that retaining the natural sticky glandular bract package protects developing buds over the three-day observation window. It does **not** isolate whether adhesion, the physical cage formed by the bracts, gland chemistry, or their combination caused the protection. It does not show which antagonist was excluded. Developing-fruit damage did not respond to bract removal, and the study measured neither final fruit set nor seed production.

## Study 2 — *Erica plukenetii*: added corolla stickiness

### Identity and primary sources

McCarren, S., Coetzee, A. & Midgley, J. (2021). Corolla stickiness prevents nectar robbing in *Erica*. *Journal of Plant Research* 134:963–970. DOI: [10.1007/s10265-021-01299-z](https://doi.org/10.1007/s10265-021-01299-z). [Publisher article record](https://link.springer.com/article/10.1007/s10265-021-01299-z); [publisher-hosted supplementary tables](https://static-content.springer.com/esm/art%3A10.1007%2Fs10265-021-01299-z/MediaObjects/10265_2021_1299_MOESM1_ESM.docx).

### System and manipulation

- Species and site: *Erica plukenetii* at Paarl Mountain Reserve, Western Cape, South Africa, in 2019.
- Experimental treatments: control, experimentally added stickiness on the corolla, and experimentally added stickiness at the base of the inflorescence (`sticky stem`).
- Endpoint: percentage of flowers damaged by nectar robbers.
- Design logic: the sticky-stem treatment is a location control. If an indiscriminate barrier on the approach path were sufficient, it should reduce damage; instead, only corolla-localized stickiness did so.
- Independence: distinct lineage, enemy process, site and research group from the excluded systems and from the *Passiflora* experiment.

The accessible abstract confirms the within-species experimental addition of stickiness. The publisher supplement identifies the treatment locations and supplies the exact model contrasts. The article body is subscription-restricted, so the experimental sample size, blocking level, adhesive material, and model-family/link details were not recoverable from the openly accessible primary materials.

### Exact quantitative result

Publisher Supplementary Table S4 reports Tukey contrasts for nectar-robbing damage:

| contrast | estimate | SE | z ratio | p |
|---|---:|---:|---:|---:|
| control - sticky stem | 0.06 | 0.05 | 1.14 | 0.489 |
| control - sticky corolla | 2.43 | 0.13 | 19.25 | <0.001 |
| sticky stem - sticky corolla | 2.37 | 0.13 | 18.74 | <0.001 |

The primary figure shows the same direction: corolla-localized stickiness sharply lowered the percentage of damaged flowers, while the sticky-stem treatment resembled the control.

### Extractability boundary

The contrast estimates and standard errors are exact. However, Supplementary Table S4 does not name the model family or link scale, and the accessible materials do not provide the allocation denominator or a raw event table. The estimates must therefore remain on the authors' unnamed model scale; they must not be exponentiated into odds ratios or converted to risk ratios by assumption.

Recommended FDT1 handling:

- admit the study as a clean causal direction for `corolla stickiness -> lower nectar-robbing damage`;
- retain all three treatment contrasts so the stem-location negative control is not discarded;
- mark a quantitative meta-analysis row `pending_full_methods_or_raw_counts` rather than guessing the effect metric;
- do not code nectar-robbing damage as seed fitness.

### Claim boundary

The experiment isolates a strong, location-specific effect of added corolla stickiness on nectar-robbing damage. It does not show that natural glandular trichomes produced the experimental adhesive, and it does not quantify fruit set, seed set, seed number or germination. The publisher abstract says the trait could potentially improve fitness; that is a hypothesis, not a measured fitness effect in this experiment.

## Near-eligible studies checked but not admitted to the strict manipulation set

- LoPresti, Krimmel & Pearse (2018), *Hemizonia congesta*, DOI [10.1111/oik.04806](https://doi.org/10.1111/oik.04806): carrion supplementation on a naturally sticky tarweed reduced herbivores and increased seeds per fruit, apparently through lower density of a seed-feeding weevil. This is valuable for the indirect-defence pathway, but it manipulates carrion provisioning rather than trichomes or stickiness, so it is not a direct trait-manipulation replicate. [Primary USGS publication record](https://www.usgs.gov/publications/entrapped-carrion-increases-indirect-plant-resistance-and-intra-guild-predation-a).
- Morais-Filho & Romero (2010), *Rhynchanthera dichotoma*, DOI [10.1111/j.1365-2311.2010.01205.x](https://doi.org/10.1111/j.1365-2311.2010.01205.x): reproductive damage and seeds per fruit were tested by manipulating spider presence, whereas the separate glandular-trichome removal experiment measured fly retention and spider residence on leaves. Because trait removal and reproductive outcomes were not crossed in the same experiment, it does not identify a trichome-to-reproductive-fitness effect. [Primary open article PDF](https://repositorio.unesp.br/server/api/core/bitstreams/280b7aac-3adf-41dd-8c88-f9e3a64e7c06/content).
- Monteiro & Macedo (2014), *Vriesea bituminosa*, DOI [10.1007/s11829-014-9332-1](https://doi.org/10.1007/s11829-014-9332-1): documents insects trapped by sticky inflorescence exudate but does not supply an experimental stickiness manipulation with reproductive damage or fitness.

## Bounded search routes

The search covered combinations of `floral stickiness`, `sticky inflorescence`, `glandular trichome removal`, `bract removal`, `nectar robbing`, `florivory`, `seed predator`, `fruit set` and `seed set`, followed through the references and publisher records of the 2022 floral-stickiness experiment and the 2025 sticky-plant review. Candidate articles were checked against their primary full text or publisher supplement before admission.

The search stopped after recovering two independent direct manipulations and auditing the most relevant adjacent carrion/spider/inflorescence systems. Within this bounded search, no additional non-excluded study both directly manipulated reproductive stickiness/trichomes **and** reported a final fruit or seed endpoint with an effect size safe to pool.

## FDT1 decision

Current defensible ladder:

1. `corolla-localized stickiness -> reduced nectar-robbing damage`: causally supported in *Erica*, with exact model contrasts but an unresolved effect scale;
2. `sticky glandular reproductive envelope -> reduced bud damage`: causally supported as a compound trait package in *Passiflora*, with exact descriptive means but unresolved cluster covariance;
3. `stickiness -> fruit/seed fitness`: **still open outside the already-used Bejaria system**;
4. `natural Cirsium capitulum stickiness -> antagonist exclusion -> seed fitness`: untested and must remain an empirical target, not an extrapolated result.

The next evidence action is not another broad search. It is recovery of the full *Erica* methods/raw counts or author data, and—if a fitness-scale replicate is required—a preregistered direct manipulation that retains a sham control and measures both antagonist damage and filled seed output on the same reproductive units.
