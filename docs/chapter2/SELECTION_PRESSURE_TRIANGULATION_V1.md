# Chapter 2 selection-pressure triangulation v1

Status date: 2026-08-30

## Decision

The cause of capitulum diversity is not evaluated by asking whether the same trait is merely significant in both Azami and EAzami. The active causal programme now asks, for each trait and each predeclared driver:

> **Does the same selection-pressure domain independently align with present spatial sorting, repeated evolutionary change, the relative and calendar placement of those changes, direct mechanism, and reproductive fitness?**

The evidence sequence is:

**present spatial gradient → repeated history → relative event placement → dated environmental change/variability → trait-to-function mechanism → reproductive fitness**.

Agreement across these layers increases explanatory strength because the layers use different observations and estimands. It does not become an adaptation claim until the mechanism and fitness path are directly supported in the focal ancestry-resolved system.

The machine-readable driver ledger is:

- `../../data/evidence/chapter2_selection_pressure_triangulation_v1.csv`

The dated-tree and paleoclimate execution contract is:

- `../../data/evidence/chapter2_temporal_environment_alignment_contract_v1.json`

The public asset audit is:

- `../../data/evidence/chapter2_dated_tree_paleoclimate_asset_audit_v1.csv`

## What space and time mean in this programme

### Azami — environmental gradients across present space

Azami estimates how a continuous image phenotype is distributed along present geographic and environmental gradients. It separates within-taxon and among-taxon relationships and retains sampling-composition, broad-space and historical-placement sensitivities.

Its causal limitation is equally important: a present gradient can reflect environmental filtering, plasticity, taxon turnover, ancestry, correlated predictors, image structure or an unmeasured biotic process. It is a cause-discovery layer, not a historical cause by itself.

### EAzami — repeated assembly and environmental regimes through time

EAzami first estimates how many changes are minimally required and where they can occur in relative lineage depth. The next temporal layer is not another present-niche regression. It must ask whether admissible change-bearing branches fall within calendar-age windows whose environmental level, rate of change or variability is unusual relative to matched non-event branches.

Thus the intended symmetry is:

- Azami: `trait ~ present environmental gradient across space`;
- EAzami: `trait transition windows ~ environmental level/change/variability through time`.

Present taxon niche centroids are an intermediate ecological-correspondence layer. They do not reconstruct ancestral environments.

## Current history: how many times and when, relatively

Exactly three authority-backed discrete histories are complete.

| Trait | Minimum repeated changes | Current relative timing | What is and is not identified |
| --- | ---: | --- | --- |
| Orientation | ML 6; UFBoot 4–6, median 5 | mixed internal-to-terminal; ML mean-depth envelope 0.767–1.000; UFBoot median lower–upper envelope 0.795–0.994 | recurrence is robust; exact branches and calendar ages are weakly resolved |
| Phyllary posture | exactly 3 on ML and all 1,000 UFBoot trees | broad/deeper placements remain admissible; median envelope 0.695–1.000 | the count is strong, but root state and event placement are broad |
| Stickiness | exactly 5 on ML and all 1,000 UFBoot trees | tightly shallow/terminal-biased; median envelope approximately 0.937–0.954 | the history is concentrated toward relatively shallow lineages, but still lacks calendar dates |

Relative lineage-depth equals one on a terminal edge and declines for an edge subtending a broader descendant lineage. It is a topology coordinate, not a fraction of 2.4 million years.

The published global dated analysis supplies only a broad context: the main Japanese radiation is associated with a Pleistocene colonization/diversification window centred near 2.4 Ma, with a reported interval of 1.7–3.6 Ma. This constrains the broad era in which most focal Japanese histories arose, but it does not date any orientation, phyllary or stickiness transition.

Therefore the current answer to “when?” is deliberately two-part:

1. **calendar context:** primarily within a young Pleistocene Japanese radiation;
2. **trait-specific relative timing:** phyllary can extend deepest, orientation spans internal-to-terminal histories, and stickiness is the most shallow/terminal-biased.

An exact event age remains `STOP_NOT_IDENTIFIABLE` until a machine-readable dated tree or posterior can be crosswalked to the admitted Japan38 concepts.

## Explanatory-strength ladder

No numerical score is manufactured from heterogeneous tests. Instead, each driver advances only when a new independent evidence layer is passed.

| Tier | Evidence added | Interpretation |
| --- | --- | --- |
| T0 | measured trait or plausible mechanism only | hypothesis available |
| T1 | one axis: spatial gradient, repeated history, or direct mechanism prior | candidate pattern |
| T2 | repeated history plus an independently concordant present spatial/current-niche environmental domain | cross-axis selection-pressure candidate |
| T3 | dated transition windows align with predeclared environmental level, change or variability against a matched branch/window null | historical environmental alignment |
| T4 | direct manipulation or mediator analysis validates trait → function under the relevant environment | causal mechanism supported |
| T5 | the mechanism reaches reproductive fitness in ancestry-resolved repeated lineages | adaptive explanation supportable within the tested scope |

A factor becomes more persuasive as it climbs this ladder. T2 is not “weak adaptation”; it is still an observational cause candidate. T3 is not selection; it is historical alignment. Adaptation becomes supportable only at T5, with recurrence/origin history established independently.

# Trait-by-trait causal synthesis

## 1. Orientation × hydric regime — current strongest cause candidate

### Independent spatial evidence

Azami finds that higher annual precipitation (BIO12) aligns with a larger signed image-axis angle among taxa:

- standardized among-taxon coefficient: +0.304359;
- global-family q: 0.021;
- broad-space coefficient: +0.286086;
- broad-space permutation P: 0.017;
- direction retained in all 52 audited historical-placement trees and every applicable sampling-composition perturbation.

The endpoint is measured relative to EXIF image vertical rather than gravity, so this remains a directional phenotype association rather than a direct rain-shield measurement.

### Independent historical evidence

Orientation requires four to six minimum changes in the Japanese history. Its admissible placements span internal and terminal lineages rather than one uniquely localized event. This establishes repeated reassembly, not independent origins or repeated adaptation.

### Independent present ecological correspondence

In the frozen East-Asian panel, downward/nodding taxa occupy niches with higher precipitation seasonality (BIO15). The positive downward-minus-upward direction remains across the GBIF primary and both Taiwan occurrence-source tiers. The threshold-based class changes between `unresolved` and `tendency_supported`, but the biological direction does not change.

### What is concordant

BIO12 and BIO15 are different predictors:

- BIO12: amount of annual precipitation across present global space;
- BIO15: temporal unevenness of precipitation in the current East-Asian niche comparison.

The concordance is therefore not one coefficient reproducing. It is a higher-level **hydric-regime correspondence**. One biologically coherent possibility is that annual wetness controls broad taxon sorting, while seasonal concentration or episodic exposure controls reproductive wetting risk during the repeated assembly of orientation states.

### Current verdict

**Tier T2: cross-axis selection-pressure candidate.**

Orientation is recurrent, spatially sorted along annual precipitation, and ecologically sorted along precipitation seasonality. Hydric exposure is therefore the most explanatory public-data cause candidate currently available for any capitulum trait.

Still missing are:

- dated transition windows;
- paleohydric level/change/variability at those windows;
- gravity-referenced achieved orientation;
- flowering-period rain interception;
- pollen retention and viability;
- effective pollinator contact;
- filled-achene fitness.

The allowed statement is:

> **Repeated orientation states show independent correspondence with multiple dimensions of hydric regime, elevating reproductive exposure to rainfall as the strongest current selection-pressure hypothesis.**

Do not replace it with “rain adaptation was demonstrated.”

## 2. Orientation × temperature — a useful mismatch, not a failed result

Azami retains a positive within-taxon orientation–BIO1 broad-space relationship, whereas EAzami associates the downward state with lower BIO1 among East-Asian lineages. Thus the directions do not form a simple universal temperature rule.

This mismatch can arise for several non-exclusive reasons:

1. **biological scale:** within-taxon geographic response is not the same estimand as among-lineage state sorting;
2. **mean versus historical package:** annual mean temperature may proxy snow, elevation, growing season, radiation and precipitation regimes;
3. **different causal pathways:** flower temperature and pollinator presentation may matter locally even when long-term lineage sorting is hydric;
4. **current niche versus ancestral environment:** present descendants need not occupy the environment in which a transition occurred;
5. **measurement and coverage:** image-axis orientation and the small East-Asian state panel carry different errors.

Current verdict: **T1, scale-dependent or confounded**. Temperature remains a competing/interacting factor, but the data reject a simple statement that downward heads are universally a cold-climate phenotype.

## 3. Visible colour × radiative environment — strong spatial cause candidate, temporal test not yet identified

Azami shows robust among-taxon sorting:

- higher shortwave radiation aligns with lower visible CIELAB corolla chroma;
- standardized coefficient −0.345372, q=0.006;
- broad-space coefficient −0.712411, P=0.001;
- direction stable in 52 historical-placement trees;
- corresponding within-taxon RSDS–chroma relationship is unsupported.

However, the Japanese continuous-history family has no colour unit with corrected two-sided phylogenetic-structure support. A repeated colour-event count, direction and event placement are not admitted. Consequently the temporal side cannot yet test whether high-radiation regimes repeatedly preceded or accompanied colour change.

Current verdict: **T1, strong spatial selection-pressure candidate with temporal history unidentified**.

This pattern could mean genuine temporal lability, insufficient matched Japanese coverage, species-tip compression of polymorphism, or a mismatch between JPEG chroma and the biologically selected optical/pigment axis. These alternatives cannot yet be ranked.

The negative visible chroma–radiation direction must not be translated into lower anthocyanin, weaker UV absorption or a demonstrated reflective adaptation. Calibrated visible/UV reflectance, flower-background contrast, pigment chemistry and population-matched ancestry are required before reconstructing colour events.

## 4. Phyllary posture × enemy/access/wetting — strong recurrence, driver unidentified

Phyllary posture changes exactly three times across every admitted topology. Its relative-depth envelope extends farther toward broad/deeper lineages than the other focal traits, consistent with some configuration differentiation early within the radiation plus later reassembly.

Yet the driver comparison is blocked:

- Azami’s continuous projection and involucre geometry are not homologous to authority-coded ascending/spreading/recurved posture;
- the current occurrence-gated ecology overlap has only two resolved taxa, both ascending;
- no historical enemy/access series exists.

Current verdict: **T1 repeated history only; driver unidentified**.

Enemy exclusion, wetness protection and pollinator-access costs remain competing hypotheses. The absence of a space-time concordance is not discordance—it is missing measurement identity and state-diverse overlap.

## 5. Stickiness × enemy/community/cost — shallow recurrence, universal defence weakened

Stickiness requires exactly five changes and has the tightest, most terminal-biased relative-depth envelope. This is compatible with repeated lineage-specific reassembly late within the sampled radiation.

A local biotic-selection model is plausible because enemy communities, oviposition behaviour, trapping benefit and secretion cost can vary rapidly and may not align with coarse climate gradients. But current evidence does not identify that mechanism:

- Azami has no calibrated stickiness endpoint;
- present climate overlap lacks a sticky/nonsticky comparison;
- no historical enemy-pressure series exists;
- a direct *Cirsium discolor* neutralization result weakens a universal “stickiness always defends seeds” sign.

Current verdict: **T1 repeated shallow history, with generic-defence model weakened**.

This is not evidence that stickiness lacks adaptive value. It means any adaptive explanation must be context-specific and must simultaneously measure benefit, pollinator cost, secretion cost and filled-achene output.

## 6. Whole capitulum — no universal synchronized cause

Azami’s 18-D complete-case phenotype has partial within-versus-among organizational correspondence (Spearman rho=0.3663). Thus present components are not random with respect to one another.

The time axis does not support one synchronized history: orientation, phyllary posture and stickiness have different minimum counts and depth envelopes, and zero of three trait pairs passes the robust shared-transition-localization rule.

Therefore current data reject the simplest causal account:

> one globally acting selection pressure caused the entire capitulum to shift together repeatedly.

The better-supported programme model is **trait-specific selection mosaics**: different capitulum components can respond at different times to hydric exposure, thermal/pollinator presentation, enemies, costs or radiative environments. Present integration need not imply shared transition branches.

This is a negative constraint on universal common lability, not proof of genetic modularity or complete historical independence.

# Why space and time can identify different factors

Different results between Azami and EAzami are scientifically informative only after five distinctions are maintained.

## 1. Mean gradient versus environmental variability

Present spatial sorting may follow the mean amount of an environmental resource or stress, whereas transitions may be triggered by variability, extremes or rapid regime shifts. Orientation’s BIO12 versus BIO15 pattern is the leading example.

## 2. Within-taxon versus among-lineage scale

A trait can respond locally within taxa but show a different or opposite long-term lineage pattern because genetic constraints, ancestry, range shifts or taxon turnover operate at the among-lineage scale.

## 3. Present niche versus transition environment

Descendant niches are not ancestral niches. A stable present state–environment association supports ecological correspondence, but it cannot identify the environment on the branch where the state arose.

## 4. Abiotic gradient versus biotic selection mosaic

Climate rasters can capture broad hydric or thermal regimes. They are poor substitutes for pollinator opportunity, enemy identity, plant density or local interaction networks. Stickiness and display may therefore have strong local selection despite weak coarse climate sorting.

## 5. Ontology and observation mismatch

An image projection index, authority-coded phyllary posture, secretion state, spectral colour and JPEG chroma are not interchangeable. Missing homologous measurements must remain `not_evaluable`, not be forced into agreement or disagreement.

# Next executable temporal analysis

The next public-data test is now frozen, but it is blocked by one exact input: a machine-readable dated-tree or posterior crosswalked to the admitted Japan38 concepts.

Once that asset is recovered, orientation is the first execution lane:

1. map every admissible minimum-change edge to its parent–child calendar-age interval;
2. propagate topology, ancestral-history and node-age uncertainty without assigning a midpoint date;
3. define alternative paleolocation scenarios rather than assigning an ancestral branch to one modern coordinate;
4. extract PALEO-PGEM BIO1, BIO12 and BIO15 means and uncertainty at 1-kyr steps;
5. quantify environmental level, net change, absolute change and within-window variability;
6. compare event windows with matched non-event windows preserving event count, branch duration and opportunity;
7. retain a positive result only if the predeclared hydric domain survives uncertainty and null comparisons.

A positive result would move orientation–hydric from T2 to T3: repeated orientation events preferentially aligned with the tested paleohydric regimes. It would still not establish selection. The final causal route remains:

**dated hydric alignment → orientation manipulation → wetting/pollen/effective-contact mediator → filled achenes → replication across ancestry-resolved transition systems**.

Colour cannot enter the same test until a calibrated repeated colour history exists. Phyllary posture and stickiness cannot enter by substituting coarse climate for unobserved historical enemy/access pressure.

# Current programme conclusion

The present public data do not support one universal cause of capitulum diversity. They support a stronger and more specific structure:

1. capitulum components repeatedly changed at different frequencies and relative depths;
2. only orientation currently joins repeated history to independent spatial and present ecological hydric evidence;
3. visible colour has a strong radiative spatial pattern but no resolved temporal event history;
4. phyllary posture and stickiness have clear repeated histories but lack identifiable space-time drivers;
5. whole-capitulum synchronized temporal assembly is not supported under current coverage.

Accordingly, the highest current explanatory statement is:

> **Capitulum diversity appears to have been assembled asymmetrically under trait-specific selection mosaics. Hydric exposure is the strongest current cause candidate for repeated orientation evolution because recurrence, global precipitation sorting and East-Asian precipitation-seasonality correspondence agree independently. Other components retain different evidence profiles, implying either different selection pressures or unresolved measurement/history links rather than one universal capitulum syndrome.**

The claim becomes substantially stronger only when the same hydric factor also predicts dated transition windows and the orientation-to-reproductive-fitness pathway is demonstrated directly.
