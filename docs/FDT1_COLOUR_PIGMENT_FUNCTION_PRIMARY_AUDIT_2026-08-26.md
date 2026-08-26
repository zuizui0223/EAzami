# FDT1 colour/pigment-function primary audit (2026-08-26)

## Disposition

This bounded primary-source audit changes the Chapter 2 colour gate, but only after separating three estimands that must not be collapsed:

1. **Whole-pathway reproductive thermoprotection is directly supported.** In *Ipomoea purpurea*, a segregating chalcone-synthase-null allele was tested in a near-isogenic breeding design crossed with temperature and light treatments. At high temperature, the flavonoid-deficient genotype had lower maternal and paternal fertilization success; at low temperature the genotypes did not differ. The endpoint was mature fruit per hand pollination.
2. **A reproductive-tissue oxidative mechanism is directly supported, but it is a flavonol mechanism, not a demonstrated petal-anthocyanin mechanism.** In tomato, an `F3H` mutant, genetic complementation, antioxidant rescue and heat treatment close `low pollen flavonols -> excess ROS -> impaired pollen-tube performance`. An independent tomato study using three `hp2` alleles and corresponding isogenic backgrounds links higher pollen flavonols under chronic heat to preserved pollen viability and seed number.
3. **Visible petal anthocyanin itself is still not causally isolated from the rest of the flavonoid pathway or genetic background.** The qualifying genetic perturbations act in pollen, pistil and/or vegetative tissues and alter metabolites besides anthocyanins. They do not show that a darker petal surface, at fixed pollen chemistry and plant background, protects the flower.

Accordingly, the recommended FDT1 state is:

- **E13 (`colour -> abiotic pigment protection -> mechanism`): `CONDITIONAL_READY_FLAVONOL_REPRODUCTIVE_TISSUE`; exact petal-anthocyanin/visible-colour version remains `PARTIAL`.** Admit the tomato ROS-rescue evidence only with `pigment_class = flavonol`, `tissue = pollen`, and `visible_petals_not_manipulated = true`.
- **E14 (`colour -> net reproductive fitness`): `READY_FOR_BOUNDED_EFFECT_EXTRACTION`, not yet `READY_FOR_POOLED_META_ANALYSIS`.** The *I. purpurea* study is the first recovered direct genotype-by-abiotic reproductive calibration. Its temperature treatment has one chamber per temperature and its observation clusters are plant-day pollination pairs, so it belongs in a chamber-confounding sensitivity stratum. The tomato `hp2` study supplies an independent taxon and seed endpoint, but also uses one greenhouse per temperature and a pleiotropic upstream regulator.

This is not a universal `more anthocyanin = more abiotic fitness` result. A direct negative *Mimulus guttatus* experiment retained below found no predicted stress disadvantage of the anthocyanin-deficient genotype under UV or drought, and the nearest petal-specific sun experiment remains genetically confounded.

## Admission and extraction rules

A study was eligible for this audit if it was a primary experiment that:

- independently varied pigment genotype/level and UV, temperature or drought exposure, or directly manipulated a pigment/antioxidant mechanism under an abiotic exposure;
- used intact plants or reproductive tissues and measured a physiological reproductive mechanism or fruit/seed-related output;
- reported the biological unit and enough design information to preserve family, plant, flower, fruit, pollen-sample or chamber clustering; and
- was independent of the already registered *Silene littorea* UV-exclusion study and the *Ipomoea tricolor* excised-petal HBA study.

Environment-induced pigmentation by itself was not treated as pigment protection. A colour-morph comparison was not treated as a pigment effect when the morphs differed across uncontrolled genetic backgrounds. No numerical effect or variance was reconstructed from a P-value, F-statistic or secondary source. Graph-only values are labelled as such.

## Study 1 — *Ipomoea purpurea*: CHS-null genotype × temperature × light with mature-fruit success

### Identity and primary source

Coberly, L. C. & Rausher, M. D. (2003). Analysis of a chalcone synthase mutant in *Ipomoea purpurea* reveals a novel function for flavonoids: amelioration of heat stress. *Molecular Ecology* 12:1113–1124. DOI: [10.1046/j.1365-294X.2003.01786.x](https://doi.org/10.1046/j.1365-294X.2003.01786.x). [Primary author-hosted article PDF](https://people.duke.edu/~mrausher/Molecol.pdf); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/12694276/).

### Pigment contrast and background control

- The focal `A` locus encodes CHS-D. The white `a` allele carries an `Ac/Ds` insertion that prevents production of a functional transcript; `aa` plants lack flower pigmentation and pigmentation in most vegetative tissues. This is a whole-flavonoid-pathway perturbation, not an anthocyanin-only switch.
- Two independent experimental lines were constructed. Wild-type `AA` and mutant `aa` source lines had first undergone 13 generations of single-seed descent. Within each crossing unit, an `AA` and an `aa` plant were crossed, an F1 was selfed, and heterozygous descendants were propagated by single-seed descent for another three generations. Homozygous progeny of F4 heterozygotes supplied the experiment.
- The authors estimate each experimental line was `87.5%` homozygous and state that the cross randomized genetic background between flower-colour genotypes except at loci closely linked to `A`. Line was retained in the model. The two lines are biological background blocks, not two independent published studies.

### Abiotic manipulation and experimental units

- Plants were grown together until flowering, then randomly assigned to position and treatment and acclimated for one week.
- Full design factors were temperature, light, pollen-parent genotype, seed-parent genotype, cross parent and experimental line.
- Low temperature was `27/18 °C` day/night. High temperature was `36/24 °C` for the first two post-acclimation weeks, then `32/20 °C` for 16 days so plants continued flowering.
- High and low light were `1180` and `800 µmol m^-2 s^-1`, respectively. Humidity was adjusted and plants were saturated twice daily to reduce drought confounding.
- Each temperature had one chamber, divided into high- and low-light subchambers. Each of the four temperature × light combinations contained six plants of every line × genotype combination: `24 plants` per combination and `96 plants` total. Thus genotype replication is present within an exposure, but temperature is confounded with chamber and light with subchamber.
- Hand pollinations crossed all combinations of line, maternal/paternal genotype and maternal/paternal treatment. One or two flowers on a maternal plant were emasculated and hand-pollinated. The primary observation pooled the pair of flowers pollinated on one plant on one day; a plant was generally used once and rarely twice for a treatment combination. Fruits were collected at maturity.
- Fertilization success was `mature fruits / flowers pollinated` for a maternal-treatment × paternal-treatment combination. The study scored `1342` pollination pairs overall; Table 1 reports `n = 12–32` plant-day observations per detailed cell with its mean and SE. Flowers within the same pooled observation, repeated use of a plant and shared chamber must not be treated as independent.

### Exact reported effects

| endpoint | exact primary result | safe interpretation |
|---|---|---|
| female-side heat response | at high maternal temperature, `aa` pollen recipients had approximately `26%` lower fertilization success than `AA`; at low maternal temperature they were similar | pathway genotype modified the reproductive response to heat |
| male-side genotype under hot recipient environment | when recipients were hot, pollen from `aa` donors had an average `24%` lower fertilization success than pollen from `AA` donors; no pollen-genotype difference occurred on cool recipients | the genotype effect included a post-pollination interaction with the hot maternal environment |
| maternal genotype × maternal temperature | `F = 7.32`, `P = 0.0069` | registered only as the original interaction test; not converted into a sampling variance |
| paternal genotype × maternal temperature | `F = 4.85`, `P = 0.0278` | registered only as the original interaction test; not converted into a sampling variance |
| high vs low temperature | both maternal and paternal high temperature reduced fertilization success | stress manipulation check, not a pigment effect |
| light × genotype on fertilization success | no detected genotype-specific response to light | retained counter-result; high light did not reproduce the heat interaction for this endpoint |
| flower number | `aa` produced `15%` fewer flowers than `AA` at low temperature but not high temperature; under high light `aa` produced `20%` fewer flowers than `AA` | pleiotropic context; opposite to a simple high-temperature-only cost |

The exact `26%` and `24%` relative differences are statements in the primary Results, not values inferred from P-values. Table 1 supplies cell means and SEs, but the article does not report a single contrast estimate with covariance that corresponds exactly to either percentage. Effect extraction should therefore rebuild the prespecified interaction from the primary cell table only with an explicit model of shared plants and chambers; otherwise retain the author-reported relative differences as direction-and-magnitude evidence without an invented variance.

### Claim ceiling

This experiment directly supports `CHS-D/flavonoid-pathway competence -> reduced loss of fertilization under heat` in *I. purpurea*. It does not isolate anthocyanin from flavonols, corolla colour from pollen/pistil chemistry, or the `A` locus from tightly linked loci. Because only one chamber implemented each temperature, it does not by itself establish a general environmental effect independent of chamber. It is nevertheless the closest recovered E14 design because the genotype was segregated against a largely randomized background, the exposure was factorial and the response reached mature fruit.

## Study 2 — tomato `are`: genetic complementation and antioxidant rescue of a heat-sensitive ROS mechanism

### Identity and primary source

Muhlemann, J. K., Younts, T. L. B. & Muday, G. K. (2018). Flavonols control pollen tube growth and integrity by regulating ROS homeostasis during high-temperature stress. *Proceedings of the National Academy of Sciences USA* 115:E11188–E11197. DOI: [10.1073/pnas.1811492115](https://doi.org/10.1073/pnas.1811492115). [Primary full text and associated datasets in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6255205/).

### Exact perturbations and units

- The `anthocyanin reduced (are)` tomato mutant has a point mutation creating an early stop in `F3H`. It has reduced flavonol and downstream anthocyanin accumulation. Tomato pollen does not make anthocyanins, so the reproductive-tissue mechanism tested here is specifically a **flavonol** mechanism.
- The authors compared parental VF36, `are`, and independent `are-35S:F3H` complementation lines. Restoration of pollen flavonols, ROS state, viability, germination, tube growth and tube integrity by the wild-type transgene guards against treating the uncomplemented mutant as a simple background comparison.
- In the acute heat assay, pollen tubes first grew `1.5 h at 28 °C`, then remained at `28 °C` or were exposed to `34 °C for 2.5 h`.
- Heat-treated `are` pollen tubes were additionally exposed to ascorbic acid as an antioxidant rescue; the study also used the NADPH-oxidase inhibitor DPI to distinguish ROS sources.
- Pollen-tube analyses measured many tubes but were replicated across biological experiments. For the main tube-length comparisons the article reports approximately `127–140 tubes across three independent experiments`. The experiment, not each tube, is the defensible replication level.
- Final seed set was measured under standard greenhouse conditions, not crossed with the heat treatment: `10 fruits` per genotype, reported as mean ± SEM. The source does not identify whether those ten fruits came from ten independent plants; fruit-to-plant clustering is unresolved.

### Exact reported outcomes

| endpoint | exact primary result | readiness use |
|---|---|---|
| seed set at standard conditions | `are` seed set was reduced `2.9-fold` relative to VF36; mean ± SEM of `10 fruits` | reproductive consequence of the pathway lesion, but not an abiotic interaction and clustering is unresolved |
| VF36 tube length under acute heat | `34 °C` caused a `1.4-fold` reduction relative to continuous `28 °C` | heat manipulation effect |
| VF36 ROS under acute heat | DCF fluorescence increased `1.4-fold` | oxidative mechanism endpoint |
| `are` tube length under acute heat | `1.2-fold` reduction relative to its `28 °C` control | genotype-specific heat impairment; cell means and experimental clusters are in the associated datasets |
| `are` ROS under acute heat | DCF fluorescence increased `1.5-fold` | low-flavonol genotype accumulated more ROS under heat |
| ascorbic-acid rescue | heat-stressed `are` tube length was restored to a value not distinguishable from its `28 °C` control (`P = 0.41`) and exceeded untreated heat-stressed `are` (`P = 0.0002`) | pharmacological rescue supports ROS mediation; no effect magnitude or variance is inferred from these P-values |
| genetic rescue | the `35S:F3H` complementation lines reversed mutant flavonol, ROS and pollen-performance defects | strongest causal check that the F3H/flavonol lesion generated the phenotype |

The paper provides machine-readable associated datasets for the underlying observations. Extraction should use experiment-level summaries or a hierarchical reanalysis; treating every pollen tube as an independent replicate would be pseudoreplication.

### Claim ceiling

This is admissible for E13 as `flavonol abundance in pollen -> ROS homeostasis -> pollen performance under heat`. It is not evidence that anthocyanin pigment in the visible corolla performs that function. The mutant affects F3H products outside pollen, and antioxidant rescue shows that excess ROS mediates pollen-tube impairment, not that anthocyanin optical absorption is protective. Its standard-condition seed result cannot be used as an E14 heat-interaction effect.

## Study 3 — tomato `hp2`: three alleles × chronic heat with pollen flavonols and seed output

### Identity and primary source

Rutley, N., Miller, G., Wang, F., Harper, J. F., Miller, G. & Lieberman-Lazarovich, M. (2021). Enhanced reproductive thermotolerance of the tomato high pigment 2 mutant is associated with increased accumulation of flavonols in pollen. *Frontiers in Plant Science* 12:672368. DOI and [primary full text](https://doi.org/10.3389/fpls.2021.672368).

### Design, units and clustering

- Three natural `hp2/DET1` alleles (`hp2`, `hp2j`, `hp2dg`) were compared with their corresponding isogenic wild types: Moneymaker for the first two alleles and Manapal for `hp2dg`.
- Plants grew at `26/20 °C` day/night until flowering. One greenhouse then remained at control temperature and the other was set to reach at least `32/22 °C` during the reproductive period; the authors characterize the chronic treatment as approximately `34/24 °C` for `10–12 weeks`.
- Thus there are multiple alleles and genetic backgrounds within exposure, but only one greenhouse per temperature condition. Temperature is confounded with greenhouse.
- Seed-set sampling was `5–10 ripe fruits from 8–10 plants per genotype per condition`, analyzed in three replicates. The article does not provide a fruit-to-plant-to-replicate ledger in the main text; fruit is nested in plant and must not be the default independent unit.
- Pollen viability and flavonol measurements used `3–6 replicates`. Short-term in-vitro pollen germination used three replicates.

### Exact reported outcomes

| endpoint | exact primary result | inference-safe use |
|---|---|---|
| proportion of seeded fruits | chronic heat reduced this proportion `5.4-fold` in Moneymaker and `4-fold` in Manapal; it was maintained across all three `hp2` genotypes | independent intact-plant reproductive support for a genotype × heat pattern |
| seeds per fruit, control | all genotypes ranged from `56–80` | baseline overlap |
| seeds per fruit, chronic heat | `hp2` genotypes retained `79–87`; Moneymaker and Manapal declined to `44` and `52` | exact means/ranges; SEM is graphical, not reconstructed here |
| viable pollen, control | `71.1–79.3%` across genotypes | baseline overlap |
| viable pollen, chronic heat | wild types `1.6–3.2%`; `hp2` `13.8–24.6%` | reproductive mechanism under heat |
| in-vitro germination after `34 °C` for `30 min` | MicroTom wild type `2.5%`; introgressed `hp2dg` `9.9%`; heat caused `12.5-fold` and `5.9-fold` reductions, respectively | independent acute pollen-performance calibration |
| pollen flavonols under chronic heat | two mutant alleles had `18%` and `280%` higher levels than wild type, respectively | measured mediator, but allele-specific and not an anthocyanin measure |

### Claim ceiling

This study independently corroborates the sign of `higher reproductive-tissue flavonols -> better heat-stage reproduction`, and it reaches seed number. It does not isolate flavonols as the only causal `hp2` product: `DET1` is a pleiotropic photomorphogenic regulator affecting plastids, carotenoids, flavonoids and other stress responses. Association among mutant state, pollen flavonols and seed preservation is therefore not equivalent to a direct flavonol add-back. It is not visible-petal colour evidence. Effect extraction must either use plant-level data or retain published means in a chamber-confounding sensitivity stratum.

## Direct counterexample — *Mimulus guttatus*: anthocyanin genotype did not confer the predicted UV/drought response

### Primary source and design

Twyford, A. D., Caola, A. M., Choudhary, P., Raina, R. & Friedman, J. (2018). Loss of color pigmentation is maintained at high frequency in a monkey flower population. *The American Naturalist* 191:135–145. DOI and [primary full text](https://doi.org/10.1086/694853).

- A single recessive allele generated anthocyanin-deficient `aa` plants; floral and vegetative anthocyanin cosegregated. The authors constructed outcrossed `AA`, `Aa` and `aa` full-sib families.
- Separate UV and drought growth-chamber experiments used 12 crosses, four per genotype, with eight full siblings per family assigned to treatment. Family nested within genotype was random in the mixed models.
- UV was `10 µW cm^-2` in the regular-light control and `2360 µW cm^-2` with supplemental UV. Drought plants were watered every four days versus daily soaking controls.
- The stress experiments measured germination, flowering time, leaf length, stolons and flowering branches. **Seed set was measured only in the field common garden, not under UV or drought.**

### Exact negative result and ceiling

The predicted special vulnerability of `aa` plants was not observed. Genotypes generally responded similarly to the stressors; the detected genotype × treatment interaction was for stolon production, where `aa` increased stolon number under both UV and drought while other genotypes decreased or did not change. In the field common garden, seed set did not differ among genotypes (`F(2,11.54) = 0.89`).

This is a true counterexample to a universal stress-protection prior, not proof of no anthocyanin function: the population is from a permanently wet site, the mutation removes anthocyanin from multiple tissues, the experiments did not measure floral DNA/oxidative damage, and no reproductive endpoint was taken under the abiotic treatments. Retain it as a direct negative genotype × exposure study and do not code absent significance as a zero E13/E14 effect.

## Closest petal-specific near miss — *Saponaria officinalis* clones under sun and shade

Davis, S. L. et al. (2014). Sexual dimorphism of staminate- and pistillate-phase flowers of *Saponaria officinalis* affects pollinator behavior and seed set. *PLOS ONE* 9:e93615. DOI and [primary full text](https://doi.org/10.1371/journal.pone.0093615).

- Twenty-five field genets were clonally split in 2012. In 2013, the authors selected four genotypes whose flowers had responded least to sun in 2012 (`pale`) and four that had responded most (`pink`), made 30 clones of each and planted three clones per genotype in each of ten plots (`240 plants`); five plots had `60%` shade cloth and five clear mesh.
- Petal anthocyanin was directly measured. Sun increased anthocyanin, and pink-set genotypes contained more than pale-set genotypes, but treatment × set did not differ (`P = 0.141`).
- Both open- and hand-pollinated seed set differed between the preselected genotype sets. For hand-pollinated seed set, treatment × set was reported as Wald `chi-square = 3.87`, `df = 1`, `P = 0.049`; pink genotypes produced fewer seeds in sun than shade. Exact cell means/SEs are graphical, so no effect was reconstructed.

This experiment reaches seeds and directly measures petal anthocyanin, but it is not an E14 pigment-causal contrast. The pale/pink sets were selected post hoc for previous sun responsiveness; they are unrelated field genotypes and differed in hand-pollinated seed set even apart from pollinator attraction. Colour set therefore carries the entire genetic-background package. It remains a hypothesis-generating petal-specific near miss, not a substitute for a segregating or complemented pigment locus.

## Quantitative extraction and independence ledger

| study | independent study unit for synthesis | estimand that can be retained now | main block to pooled use |
|---|---|---|---|
| Coberly & Rausher 2003, *I. purpurea* | one study; two constructed lines are internal background blocks | genotype × temperature effect on mature-fruit success; author-reported `26%` female and `24%` male reductions | one chamber per temperature; repeated plant-day pollination clusters; CHS affects all flavonoids/tissues |
| Muhlemann et al. 2018, tomato `are` | one study | genotype/complementation/antioxidant effects on pollen ROS and heat-stage tube performance | tube-level pseudoreplication if datasets are not aggregated by experiment; no heat × genotype final seed endpoint |
| Rutley et al. 2021, tomato `hp2` | one independent study, even though three alleles are tested | chronic-heat genotype contrast for viable pollen, seeded-fruit proportion and seeds per fruit | one greenhouse per temperature; fruits nested in plants; DET1 pleiotropy |
| Twyford et al. 2018, *Mimulus* | one independent negative study | direction/counterexample for whole-plant anthocyanin genotype × UV/drought on growth traits | no mechanism endpoint and no reproductive response under exposure |
| Davis et al. 2014, *Saponaria* | one near-miss study | hypothesis-generating petal anthocyanin × sun pattern | genotype-set selection and uncontrolled genetic background; graph-only cell estimates |

Tomato `are` and `hp2` are independent papers, but both are tomato and both address flavonols in pollen. They are not two independent demonstrations of visible floral-colour adaptation. The 2018 `are` seed result and 2021 `hp2` seed result are also not interchangeable: the former is a standard-condition pathway defect, while the latter is a chronic-heat genotype contrast.

## Bounded search routes and STOP

The bounded search covered combinations of `floral anthocyanin`, `flower colour locus`, `near-isogenic`, `segregating`, `CHS mutant`, `F3H mutant`, `UV`, `heat`, `temperature`, `drought`, `ROS`, `pollen`, `fruit` and `seed set`. Candidate routes included *Ipomoea*, *Mimulus*, *Boechera*, *Antirrhinum*, petunia, tomato, lily, chrysanthemum, alpine colour-temperature studies and sun/shade petal-colour experiments. Primary full text, associated data and institutional/author-hosted primary copies were used where available. The excluded *S. littorea* and *I. tricolor* studies were not re-admitted.

The search stops because the gate can now be decided without expanding into horticultural temperature-induced colour-change literature:

- one near-isogenic/segregating whole-pathway study closes genotype × heat to mature fruit;
- a genetic-complementation plus antioxidant-rescue study closes flavonols to reproductive ROS control under heat;
- an independent isogenic multi-allele study connects pollen flavonols, pollen viability and seeds under chronic heat; and
- a direct anthocyanin-genotype counterexample prevents a universal positive prior.

No recovered study simultaneously provided **petal-restricted anthocyanin manipulation**, independently randomized abiotic exposure, a biochemical damage/temperature mediator, and plant-clustered final seed output. Broader searching should not be used to blur that missing design.

## FDT1 decision for Azami-series Chapter 2

1. Create a separate functional loading for **reproductive flavonoid thermoprotection**, not a generic `dark flower protection` loading.
2. Promote E14 from `NOT_READY` to **bounded extraction ready**, starting with the *I. purpurea* cell table and preserving its plant-day and chamber structure. Keep the estimate out of an inverse-variance pool until the environmental replication problem is represented explicitly.
3. Admit tomato `are` to E13 only as a **pollen-flavonol/ROS mechanism** and tomato `hp2` as an independent **pollen-flavonol/seed thermotolerance calibration**. Do not map either directly to visible capitulum lightness.
4. Keep the exact petal-anthocyanin E13 target `PARTIAL`: it still requires a petal-restricted pigment manipulation or segregating/complemented colour locus with a direct floral damage/temperature/ROS mediator.
5. Keep *Mimulus* as a counterexample and *Saponaria* as a genetically confounded near miss. These prevent coding colour as an invariant positive abiotic-protection vector.
6. For the focal reverse-designed experiment, cross a validated pigment/pathway contrast with heat or UV while holding pollination constant, measure petal and pollen pigments separately, measure floral temperature/oxidative damage and pollen function, and follow each plant to filled achenes. Randomize replicate chambers or blocks; do not use one chamber per environment.

The Chapter 2 claim ceiling is therefore: **flavonoid-pathway state can modify reproductive sensitivity to heat, and pollen flavonols can mediate ROS homeostasis; whether visible anthocyanin differences among *Cirsium* capitula perform the same function remains an open, explicitly testable question.**
