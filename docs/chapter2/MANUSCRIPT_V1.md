# From present phenotypic fields to admissible generative histories in *Cirsium*

## Working title

**From present phenotypic fields to admissible generative histories: hierarchical constraints on explanations of *Cirsium* capitulum diversity**

Alternative shorter title:

**Hierarchical phenotypic constraints expose limits of generative explanations in *Cirsium***

## One-sentence paper claim

A present-day multivariate phenotype field can be reproduced by a simple snapshot generator while still containing hierarchical, scale-specific information that rejects that generator; therefore historical inference should be framed as progressive restriction of an admissible-history set rather than selection of a single best story from present-day trait values.

---

# Abstract

Inferring evolutionary history from present-day phenotypes is an inverse problem because distinct historical processes can generate similar contemporary trait distributions. We developed a hierarchical workflow in *Cirsium* that first reconstructs a present phenotypic field and then asks which generative-history classes remain compatible with increasingly stringent empirical constraints. The empirical layer summarized capitulum variation with 18 continuous response endpoints and a fixed observation-level environmental design. Rather than passing individual correlations to the generative model, we froze 62 estimands describing multivariate structure, within- and among-taxon environmental alignment, cross-scale coefficient geometry and incremental process-environment information. Fourteen preregistered conditional generator families were then evaluated with paired prior-predictive draws on the same environmental design. A no-explicit-environment model with coupled residual covariance (`NULL_COUPLED`) was the robust structural-sufficiency winner for the 62 scalar targets: it ranked first in all 16 primary paired draws and remained first under the replication-threshold sensitivity analysis. This result did not imply environmental irrelevance, because permutation-based support states had been deliberately held out from the scalar score. In an independent falsification, the frozen `NULL_COUPLED` winner reproduced the preregistered scale-specific support pattern in 0 of 64 draws and reproduced the complete 20-cell support vector in 0 of 64 draws. The strongest mismatch was the repeated among-taxon support for growing-season water input, which occurred in 0/64 null draws at the primary threshold and 1/64 at the sensitivity threshold. A subsequent post-heldout diagnostic showed that models restricting process effects to the among-taxon component improved strongly over the null, but none met the preregistered adequacy rule; the best descriptive family improved on the null in 22/24 paired draws yet reached a median of only 6/8 primary support cells. These results separate reproduction of snapshot scalar geometry from reproduction of hierarchical inferential geometry. We propose that the appropriate output of such analyses is an admissible-history set and that new observations should be chosen for their ability to shrink this set. In *Cirsium*, the next discriminating layers are phylogenomic transition histories, population ancestry from nuclear and plastid data, and trait-to-function-to-fitness experiments.

---

# Introduction

## The problem: present phenotypes do not uniquely encode their histories

Comparative ecology often begins from a present-day association between phenotype and environment and then narrates a historical explanation for that association. This is hazardous because the mapping from history to present phenotype is many-to-one. Similar present-day trait distributions can arise through environmental filtering, shared developmental covariance, retained ancestral variation, gene flow, repeated lineage-specific change, stochastic covariance formation, or combinations of these processes. The inverse mapping from present phenotype to historical cause is therefore generally non-identifiable without additional constraints.

A practical consequence is that a single trait mean, a set of trait–environment coefficients, or even a multivariate covariance matrix may be insufficient to distinguish competing histories. The critical question is not simply which model is closest to the observed data, but which dimensions of the observed present must be preserved before particular historical classes can be rejected.

We treat this as a **phenotypic inverse problem**. Let the empirical present be represented by a hierarchy of constraints

\[
P_{present}=\{D,\Sigma_{within},\Sigma_{among},G_{cross-scale},E_{alignment},I_{support}\},
\]

where \(D\) denotes observed trait distributions, \(\Sigma_{within}\) and \(\Sigma_{among}\) capture within- and among-taxon association structure, \(G_{cross-scale}\) captures the relationship between those structures, \(E_{alignment}\) summarizes environmental alignment, and \(I_{support}\) represents inferential support patterns that distinguish robust structure from scalar effect magnitude alone. A generative model \(M\) is not interpreted as true merely because it minimizes a distance to one projection of this present. Instead, each additional empirical layer can remove models from an admissible set

\[
\mathcal{H}_{admissible}=\{M:P_M\text{ satisfies the frozen empirical constraints}\}.
\]

This perspective makes negative model results informative: failure to reproduce a newly introduced constraint identifies missing structure rather than an unsuccessful attempt to tell a preferred evolutionary story.

## Why *Cirsium* is useful for this problem

*Cirsium* provides a tractable system because homologous capitula vary along multiple continuous axes while retaining a common organ architecture. Orientation, involucre geometry, phyllary architecture, stickiness, colour and display-related dimensions can therefore be represented in a shared phenotypic coordinate system rather than compared across fundamentally different floral organizations. The genus also combines extensive geographic variation, regional radiations and known phylogenetic complexity, making similarity of present phenotype explicitly separable from similarity of history.

Our empirical and generative layers are intentionally dependent. The image-based Azami workflow defines the present phenotypic field. EAzami is not a second independent trait project; it receives frozen summaries of that field and tests which generative-history classes can reproduce them. A separate nuclear phylogenomic layer then supplies evidence about realized historical changes, while future population and experimental data are selected to discriminate histories that remain observationally equivalent.

## Questions

We address four ordered questions.

1. **Can the present *Cirsium* capitulum field be compressed into explicit, reproducible constraints that retain within- and among-taxon structure?**
2. **Do scalar summaries of that present require explicit environmental-history structure in a generative model?**
3. **Does a model sufficient for scalar geometry also reproduce independently held-out scale-specific inferential geometry?**
4. **If not, what minimal additional model structure moves toward the observed hierarchy without retroactively changing the original model-selection result?**

The aim is not to recover one true evolutionary trajectory. It is to identify the boundary between generative histories that remain compatible with the present and those that can be rejected.

---

# Methods

## 1. Empirical present: a multivariate capitulum field

The Azami layer treats the capitulum as a multivariate phenotype rather than reducing it to a small number of categorical syndromes. The handoff to EAzami uses 18 continuous response endpoints measured or derived from the frozen image-analysis workflow. The environmental design includes nine named predictors: BIO1, BIO4, BIO12, BIO15, mean solar radiation, mean vapour-pressure deficit, mean surface wind, growing-season precipitation and net primary productivity.

The frozen complete-18 environment design contains 1,874 observation rows representing 124 taxa. Coordinates and original observation identifiers are removed before model execution. The environment table is used as an exogenous design only; observed response phenotypes never enter the generative simulator.

The present is decomposed at two biological scales.

- **Within-taxon:** responses and predictors are taxon-centred and standardized with inverse taxon sample-size weights.
- **Among-taxon:** taxon medians are calculated first, followed by standardized multivariate analyses across taxa.

This decomposition prevents a single cross-species correlation from silently standing in for both within- and among-lineage processes.

## 2. Frozen 62-target empirical handoff

The empirical handoff contains 62 observational estimands grouped into four target classes.

### 2.1 Structure targets — 6

These summarize module integration and cross-scale association geometry, including within-taxon module contrast, among-taxon module contrast and similarity between within- and among-taxon association matrices across the primary and sensitivity scopes.

### 2.2 Environmental block R² targets — 24

Environmental predictors are grouped into predeclared blocks: core thermal, core precipitation, radiative/atmospheric drying, mechanical exposure, growing-season water input and climatic productivity. Multivariate R² is calculated separately within and among taxa.

### 2.3 Cross-scale coefficient-geometry targets — 12

For each environmental block, the flattened standardized coefficient matrices estimated within and among taxa are compared by cosine similarity.

### 2.4 Incremental environment targets — 20

A four-predictor core (`BIO1 + BIO4 + BIO12 + BIO15`) is compared with process extensions. The five tests are: all process variables beyond core4, radiative/atmospheric drying, mechanical exposure, growing-season water input and climatic productivity. Each is evaluated within and among taxa at both the primary replication threshold (complete18 ≥5) and the replication sensitivity threshold (complete18 ≥2). The scalar target is partial R².

All 62 targets are observational and non-causal. Matching them establishes only statistical/structural reproduction.

## 3. Conditional generative families

EAzami generates synthetic 18-dimensional phenotype observations on the same fixed empirical environment rows. Fourteen families were frozen before the one-shot comparison. The families vary along three structural axes:

1. **Environmental mode:** no explicit environment, core4, process variables at both scales, or process variables only at the among-taxon component.
2. **Scale-coefficient architecture:** shared versus independently drawn within/among coefficients where applicable.
3. **Residual architecture:** coupled versus modular covariance.

The families are not fitted to the 62 observed target values. They are prior-predictive structural hypotheses. All produce the same observation schema and are passed through the same exact 62-estimand adapter.

## 4. Preregistered scalar-target one-shot comparison

The scoring contract was committed before any target-distance ranking was inspected. It fixed 16 paired seeds for all 14 model families, complete18 ≥5 as the primary channel and complete18 ≥2 as an independent replication sensitivity, target-class discrepancy transforms, equal total weight across the four target classes, tie rules, pairwise-win rules and a no-retuning stop rule.

The total score therefore does not allow the larger environmental target classes to dominate merely because they contain more rows.

A robust leader had to be uniquely best under the frozen primary decision rule, perform consistently across paired draws and remain compatible with the replication-threshold sensitivity. The analysis was explicitly prior-predictive rather than likelihood- or posterior-based.

## 5. Held-out falsification of the frozen winner

Permutation P values, BH-adjusted support states and the geometry of which incremental process tests were supported were deliberately excluded from the scalar score. After the scalar winner had been frozen, these inferential states became an independent falsification target rather than an additional weight in the original score.

The held-out contract fixed the scalar winner (`NULL_COUPLED`), 64 new prior-predictive seeds and 99 Freedman–Lane permutations per nested test. Within-taxon residual rows were permuted only within taxon; among-taxon residual rows were permuted across taxa. Omnibus support was defined as permutation \(P<0.05\); the four block-specific tests were controlled by BH separately within each scale and replication scope.

The primary eight-cell held-out pattern was frozen as follows at both complete18 ≥5 and complete18 ≥2:

- within-taxon all-process extension unsupported;
- among-taxon all-process extension supported;
- within-taxon growing-season-water extension unsupported;
- among-taxon growing-season-water extension supported.

The outcome bins were also frozen before execution: 0–1 matches among 64 = not reproduced/exceptional, 2–6 = rare, ≥7 = compatible frequency.

## 6. Post-heldout minimal-structure diagnostic

The next analysis was intentionally labelled post-heldout and hypothesis-generating. It could not reopen the scalar-target ranking. Five existing coupled-residual families were compared using 24 paired new seeds and the same 99-permutation support test: `NULL_COUPLED`, process-both/shared, process-both/independent, process-among-only/shared and process-among-only/independent.

Adequacy was frozen before this diagnostic: a non-null family had to achieve all of the following:

- median ≥7 of 8 primary cells matched;
- ≥6 of 24 complete eight-cell pattern matches;
- paired superiority over `NULL_COUPLED` in ≥75% of draws.

If multiple families passed, a predeclared minimality order preferred among-only/shared before more complex additions. Failure of every family was accepted in advance.

## 7. Historical bridge: Japan38

A separate source-backed history layer uses the conservative Comp1061 nuclear phylogenomic tree and 1,000 UFBoot trees. Categorical states for head orientation, phyllary posture and involucre stickiness are mapped only when authoritative taxonomic evidence can be translated into the frozen ontology without guessing. Unordered parsimony is used as a lower bound on repeated historical changes.

This layer has a different evidential role from the generative simulation. It shows whether repeated state changes are required by the nuclear topology ensemble; it does not identify adaptive convergence or validate the simulated mechanisms.

## 8. Next realized-history discriminator

Species-level nuclear topology cannot distinguish whether repeated present states were generated from ancestral standing variation, introgression/gene flow or lineage-specific change. The next population layer therefore links, preferably within the same biological individual:

- nuclear population-genomic DNA;
- same-individual or tightly matched plastid haplotype;
- flow-cytometry cytotype/genome-size information;
- standardized capitulum phenotype.

Nuclear ancestry, plastid genealogy and cytotype are complementary rather than redundant. Their discordance is itself informative for reticulation and cytoplasmic capture.

---

# Results

## 1. The empirical present can be handed off as a single hierarchical constraint system

The Azami → EAzami interface successfully converts the present-day capitulum field into 62 matched estimands without substituting verbal analogues. All 62 statistics can be regenerated from any model output that supplies the same 18 response endpoints, taxon identity and nine environmental predictors on observation rows. This separates empirical definition of the present from the subsequent generative models.

This is important because the handoff is not a list of isolated trait–environment relationships. It preserves within/among decomposition, multivariate environmental fit, cross-scale coefficient geometry and incremental information beyond the core climate block.

## 2. Scalar present-day geometry does not require explicit environmental structure

The preregistered 14-family comparison selected `NULL_COUPLED` as a robust leader. Its primary median total discrepancy was 2.2133, it formed a unique primary tie set, and it ranked first in all 16 paired primary draws. Its minimum paired-win fraction against every other family was 1.0. Under the complete18 ≥2 replication sensitivity it again ranked first.

The second primary family, `CORE4_INDEPENDENT_COUPLED`, had a substantially larger median discrepancy (14.7612).

Factor diagnostics were consistent with the main ranking in showing that coupled residual architecture often outperformed modular residual architecture and that process-among-only structure tended to outperform process-both structure. However, these factor contrasts do not convert residual coupling into an evolutionary-lability claim.

The direct conclusion is narrow: **the 62 scalar observational estimands do not, by themselves, require explicit environment coefficients in the tested prior-predictive generator family**.

## 3. The scalar winner fails held-out hierarchical inferential geometry

The independently frozen held-out test produced the opposite result once support geometry rather than scalar magnitude was required. The primary eight-cell support pattern was reproduced in **0/64** `NULL_COUPLED` draws. The exact 20-cell support vector was also reproduced in **0/64** draws. The median draw matched 14 of 20 support cells.

The failure was concentrated on the among-taxon process signals rather than on within-taxon false positives. The observed within-taxon non-support states were common under the null. In contrast:

- among-taxon omnibus process support at complete18 ≥5 occurred in 6/64 null draws (0.09375);
- among-taxon omnibus process support at complete18 ≥2 occurred in 6/64 null draws (0.09375);
- among-taxon growing-season-water support at complete18 ≥5 occurred in **0/64** draws;
- among-taxon growing-season-water support at complete18 ≥2 occurred in **1/64** draws (0.015625).

Thus the same generator that was sufficient for scalar snapshot geometry was insufficient for the replication-stable, scale-specific support geometry.

## 4. Restricting process effects to the among-taxon component moves in the correct direction but remains inadequate

No family in the frozen five-family post-heldout diagnostic met all adequacy criteria. The best descriptive family was `PROCESS_AMONG_ONLY_SHARED_COUPLED`.

Across 24 paired draws it achieved:

- median primary-cell match = **6/8**, below the required 7/8;
- mean primary-cell match = 6.375/8;
- full eight-cell pattern = **6/24 (25%)**;
- paired superiority over `NULL_COUPLED` = **22/24 (91.7%)**;
- joint among-taxon omnibus support at both thresholds = 83.3%;
- joint among-taxon growing-season-water support at both thresholds = 25%;
- clean within-taxon non-support at both thresholds = 91.7%;
- exact 20-cell pattern = 0/24.

`PROCESS_AMONG_ONLY_INDEPENDENT_COUPLED` also improved on the null but reproduced the complete eight-cell pattern only 1/24 times. Both process-both families performed poorly on the primary geometry because explicit within-taxon process effects generated support where the observed within-taxon analyses were consistently unsupported.

The result therefore provides a directional constraint without identifying an adequate mechanism: **the missing information is more consistent with process structure entering the among-taxon component while remaining suppressed within taxa, but generic among-only zero-mean process loadings are insufficient, especially for the stable growing-season-water signal.**

## 5. Historical state changes provide an orthogonal realized-history constraint

The Japan38 nuclear topology ensemble requires repeated changes in multiple capitulum traits. In the current canonical history layer, orientation is resolved for 20 concepts and requires 4–6 minimum unordered changes across the UFBoot ensemble (ML minimum 6), while phyllary posture is resolved for 10 concepts and requires exactly three minimum changes across all 1,000 UFBoot trees. Stickiness has independently repeated state changes as well; the exact canonical count should be read from the current merged authority-extension result when the manuscript is frozen.

These histories show that present capitulum diversity cannot be reduced to a single unchanged ancestral syndrome. They do not, however, establish that the repeated changes were adaptive, developmentally modular, or caused by the environmental process structure diagnosed above.

---

# Discussion

## Scalar fit and historical identifiability are different questions

The main result is the apparent contradiction between the one-shot scalar screen and the held-out support validation. There is no contradiction once the empirical present is treated as layered information. `NULL_COUPLED` can reproduce one projection of the present: scalar summaries of structure and environmental alignment. It cannot reproduce a second projection: which process extensions become reliably supported among taxa while remaining unsupported within taxa.

The consequence is methodological. A good fit to present-day trait values does not necessarily identify the historical process that generated them. Conversely, the failure of a scalar model comparison to prefer an explicit environment family does not imply absence of environmental history. Historical identifiability depends on which properties of the present are retained as constraints.

## The present is not a single snapshot statistic

A conventional snapshot view might preserve only species means or a single trait covariance matrix. Our results show that such a representation can discard information relevant to history. Within-taxon structure, among-taxon structure and the inferential geometry linking environmental extensions to those scales are distinct components of the biological present.

This motivates the term **present phenotypic field** rather than snapshot. The field is a hierarchical object containing variation, covariance and environmental alignment at more than one biological scale. Inverse historical inference should be explicit about which parts of this field are being compressed away.

## Among-taxon process structure is a directional clue, not a solved mechanism

The post-heldout diagnostic consistently disfavors applying the same process effects at both scales. Models with process effects active within taxa tend to destroy the observed within-taxon non-support pattern. Restricting those effects to taxon means greatly improves the held-out geometry.

However, the best among-only model still fails the frozen adequacy threshold and reproduces joint growing-season-water support in only one quarter of diagnostic draws. It would therefore be inappropriate to tune the same generator until it passes. The correct outcome of the diagnostic is that the current family is incomplete.

A new model version should be justified by independent biology rather than by target rescue. Candidate directions include structured or sparse among-taxon loadings, lineage-dependent response distributions, inherited covariance constraints, or a model in which environmental history acts on latent trait combinations rather than independently drawn endpoint coefficients. These are future hypotheses, not conclusions of the current analysis.

## From best model to admissible-history map

The workflow suggests replacing the question “Which model wins?” with “Which histories remain admissible after all frozen constraints are applied?” The scalar screen leaves the null family admissible. The held-out support layer removes it as an adequate full explanation. The post-heldout diagnostic removes the tested generic process additions as sufficient explanations while identifying among-taxon restriction as a useful directional feature.

The product is therefore not a single reconstructed history but a shrinking set of historical possibilities. This framing makes model failure scientifically useful and discourages post-hoc expansion of mechanisms merely to preserve a preferred story.

## Why *Cirsium* is a useful model for the inverse problem

*Cirsium* offers a rare combination of a homologous composite floral structure, high-dimensional phenotypic diversity, regional radiations and phylogenetic complexity. The same organ can be quantified continuously across many taxa, but similar present states need not reflect the same ancestry. The genus therefore provides a natural system for testing the difference between present phenotypic similarity and historical equivalence.

The framework is not a claim that *Cirsium* represents all flowering plants. Its broader value is methodological: any system with repeated homologous traits, hierarchical variation and competing historical explanations can in principle be represented by an empirical present followed by an admissible-history analysis.

## Connecting possible history to realized history

The generative layer identifies which abstract structures are insufficient; the phylogenomic and population layers ask which histories actually occurred. Current Japan38 results already show repeated categorical state changes on a nuclear topology ensemble. The next unresolved problem is the origin of repeated states.

For that problem, nuclear population-genomic DNA and plastid haplotypes have complementary roles. Nuclear data estimate ancestry, admixture and gene flow; plastid data preserve a uniparental cytoplasmic genealogy that can reveal discordance or cytoplasmic capture; cytotype information is required because polyploidy can alter ancestry signals and phenotype. Linking all of these to standardized phenotype at the same individual converts a generic repeated-state claim into a test among ancestral standing variation, introgression and lineage-specific origin.

## Function remains a separate evidential gate

The image-derived trait space should not be silently re-labelled as a functional trait space. Orientation, phyllary architecture, stickiness and colour have candidate functional annotations from the literature, but adaptive-function claims require independent tests connecting a focal trait to pollinator, antagonist or abiotic pathways and finally to reproductive fitness.

The Chapter 2 inference line therefore ends with **constraints on history**, not proof of adaptation. Field manipulations and molecular mechanism are downstream discriminators selected by the histories that remain possible.

## Limitations

First, the generator comparison is prior-predictive rather than fitted likelihood inference. The families are deliberately coarse structural hypotheses, and absolute adequacy cannot be inferred from relative scalar distance alone.

Second, the 62 targets are a designed compression of a larger empirical phenotype field. Different valid compressions may retain different historical information, which is part of the conceptual point but also a source of sensitivity.

Third, the held-out support validation uses finite permutation counts to reproduce binary support geometry rather than exact P-value magnitudes.

Fourth, the post-heldout diagnostic is explicitly exploratory because it was designed after observing the null failure. Its direction can motivate a new preregistered model version but cannot be promoted to confirmation.

Fifth, the Japan38 history layer remains sparse for some traits and operates at taxon-concept rather than population resolution. Minimum parsimony steps are lower bounds, not transition-rate estimates or adaptive-convergence counts.

## Conclusion

The present-day phenotype of a lineage is not a direct record of a unique evolutionary history. In *Cirsium*, a simple coupled-residual generator was sufficient for a frozen set of scalar present-day targets but failed an independently held-out hierarchical support pattern. Adding among-taxon process structure improved the missing geometry without providing a fully adequate explanation. These results show that the amount of historical information contained in the present depends on how the present is represented. We therefore propose an inference sequence in which the empirical present is first reconstructed and frozen, generative histories are rejected or retained against progressively richer constraints, and the remaining ambiguity determines the next phylogenetic, population-genomic or experimental observation. The objective is not to narrate a single history from a snapshot, but to move from a present phenotypic field toward a progressively smaller set of admissible histories.

---

# Thesis Chapter 2 placement

## Chapter question

> **How far can the present-day multivariate capitulum field constrain the histories that could have generated it?**

## Chapter answer

> Scalar phenotype geometry alone is historically non-identifying. Hierarchical scale-specific information rejects a snapshot-null explanation, but the current process families remain insufficient. The present therefore constrains history without uniquely recovering it, and the unresolved alternatives define the next ancestry and functional data to collect.

## Bridge to the next chapter

Chapter 2 ends by producing unresolved historical alternatives rather than a preferred adaptive narrative. The next chapter asks which of these possibilities corresponds to realized history using nuclear population genomics, plastid haplotypes, cytotype and morph-linked sampling; downstream functional chapters test trait → interaction/abiotic pathway → reproductive fitness.
