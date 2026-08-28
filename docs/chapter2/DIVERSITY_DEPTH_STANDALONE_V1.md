# Chapter 2 standalone mainline v1 — diversity depth

Status date: 2026-08-28

Machine-readable contract: `data/evidence/chapter2_diversity_depth_contract_v1.json`

Inventory: `data/evidence/chapter2_diversity_depth_inventory_v1.csv`

## 1. One-page Chapter 1–2 research structure

The dissertation should be organized as **diversity breadth -> diversity depth**, not as pattern -> cause and not merely as space -> time.

**Chapter 1 asks how broadly continuous capitulum diversity is distributed in the present.** It partitions phenotype within and among taxa, maps geographic recurrence and tests present environmental associations while retaining spatial dependence and observation uncertainty. Its ceiling is descriptive association: it does not infer history, function or adaptation.

**Chapter 2 asks how deeply capitulum diversity is embedded in evolutionary history.** It starts from an independently assembled EAzami trait database, projects traits onto a nuclear phylogeny, separates recurrence counts from transition placement, and asks whether trait-environment relationships and multi-trait combinations were reconstructed on multiple branches. Its ceiling is historical structure: it does not convert recurrence into convergence or event correspondence into cause.

The chapters are conceptually symmetric but evidentially independent:

| Dimension | Chapter 1: diversity breadth | Chapter 2: diversity depth |
|---|---|---|
| Data ownership | Azami continuous phenomics | EAzami literature/specimen/flora/public-image trait registry |
| Axis | present geographic/environmental space | phylogenetic/biogeographic history |
| Dependence | spatial and sampling structure | ancestry, reconstruction and topology uncertainty |
| Recurrence | repeated geography/environment association | repeated states, branch changes and trait-niche concordance |
| Main inference | where diversity occurs | how long it is retained and how often it is reassembled |
| Claim ceiling | association, not causation | history, not adaptation or mechanism |

Azami and EAzami may share the organismal system and a trait vocabulary. EAzami must not consume Azami values, select endpoints because they were significant in Azami, or use the Azami result as its first result. This keeps both chapters publishable as standalone papers.

Japan is a useful natural experiment, not a calibration shortcut. The current evidence synthesis places 36 of 38 sampled Japanese concepts in one dominant Pleistocene radiation, with *Cirsium lineare* as a replicated phylogenetic exception and *C. dipsacolepis* as a single-study secondary-arrival hypothesis. The published approximately 2.4 Ma founder event and younger lineage anchors motivate contrasts, but they are not automatically node ages on the Comp1061 phylogram.

## 2. Central question and subquestions

**Central question**

> How deeply is present capitulum diversity embedded in evolutionary history, and which trait histories or trait-environment relationships were repeatedly reassembled during a young radiation?

Subquestions:

1. Which independently measured capitulum traits are phylogenetically retained, and which have weak or labile state structure?
2. How many state changes are minimally required for each trait, and how well can the responsible branches be localized after topology uncertainty?
3. Does a present trait-environment association reflect one old clade difference, or does the same directional relationship recur across branches?
4. Do orientation, phyllary posture, stickiness and future continuous traits change together, or are present combinations assembled mosaically through distinct histories?
5. After a dated-tree gate is passed, are changes unusually concentrated around predeclared colonization, fragmentation or niche-opening windows relative to age- and branch-matched nulls?

## 3. Standalone EAzami analysis pipeline

1. **Independent trait admission.** Build an EAzami-owned registry from exact-concept taxonomic authorities, primary literature, vouchers/specimens and independently remeasured public images. Store rights, measurement protocol, identity status and exclusions for every record. Do not import Azami phenotype values or significance decisions.
2. **Phylogenetic admission.** Use the frozen Comp1061 ML phylogram and 1000 UFBoot trees. Prune JPN20 when replicate tips are non-monophyletic and exclude JPN31 while its identity conflict remains unresolved. Treat branch lengths as substitutions/site.
3. **Trait-specific depth.** For continuous traits, estimate signal/model support, conditional ancestral values and branchwise change with family-wise control. For biology-defined discrete traits, report state coverage, minimum steps, root-state ambiguity and transition-placement support.
4. **Recurrence versus localization.** Propagate the topology ensemble. Report counts and edge support separately. Never label a minimum step as an independent origin or adaptive convergence.
5. **Trait-environment recurrence.** Build GBIF + CHELSA tip niches under source-name, jurisdiction, coordinate-uncertainty and thinning gates. Freeze a present-day PGLS before selecting axes. Then test transition-probability-weighted branch niche shifts with a state-permutation null and reconstruction uncertainty.
6. **Historical assembly.** Compare branch-localized changes among traits. For continuous traits rerun the existing reconstruction-aware null on EAzami-native inputs; for discrete traits retain topology-sensitive transition-overlap diagnostics. A positive topology diagnostic cannot replace its estimand-specific null.
7. **Dated extensions.** Only after a taxon-reconciled dated topology ensemble exists, implement phenotypic disparity-through-time and event-window tests. Propagate age intervals and compare to age-/branch-matched nulls.
8. **Model discrimination.** Only after empirical summaries are frozen, implement M0–M5 predictive simulations. Legacy present-state covariance simulations are not evolutionary-history simulations.

Every layer can end in `supported`, `not_supported`, `not_evaluable` or `STOP`. A later layer cannot rescue a failed earlier estimand by changing traits, thresholds, taxa or nulls after viewing results.

## 4. Repository-wide inventory

The 17-row machine-readable inventory is canonical. Summary:

- **Directly usable:** Comp1061 scaffold; discrete orientation/phyllary/stickiness histories; topology propagation; GBIF + CHELSA extraction; Japan + Taiwan orientation-niche PGLS; sparse cytotype evidence; colonization context; trait-function evidence as bounded discussion context.
- **Reanalysis needed:** dated anchors for a reconciled chronogram; all continuous history outputs; the continuous reconstruction-aware null; full ancestral-niche/branchwise concordance after the frozen coverage gate.
- **Design only:** Quaternary/fragmentation event registry; evolutionary M0–M5 simulations; dated DTT/phylomorphospace.
- **New data needed:** no inventory item is wholly absent, but EAzami-native continuous trait records, two near-threshold Taiwan occurrence panels and voucher-linked cytotypes are required to advance their respective gates.

## 5. Analyses runnable now

The following form a genuinely standalone executable core:

1. Rebuild and validate orientation, phyllary and stickiness recurrence/localization from the EAzami NMNS authority registry on the accepted ML + UFBoot ensemble.
2. Rerun the frozen n>=10 Japan + Taiwan orientation-niche PGLS across six accepted topologies.
3. Audit the frozen orientation-transition/niche-shift JSON as a bounded result; do not call it rerunnable until its missing producer is recovered and validated.
4. Report colonization histories and sparse cytotypes as negative constraints, not explanations of trait recurrence.
5. Run the standalone-input preflight in CI. It must keep the current continuous layer at STOP until an EAzami-native registry is admitted.

## 6. Missing analyses for historical trait-environment recurrence

- Recover at least one additional independent, environment-complete record for each of *C. morii* and *C. tatakaense* without lowering the frozen n>=10 threshold.
- Recover and validate the missing producer for the existing branchwise-concordance JSON, then quantify ancestral-niche uncertainty rather than using one conditional BM estimate per topology.
- Predeclare one primary niche axis (currently BIO15) and one secondary axis (BIO1) before the confirmatory rerun.
- Construct a taxon-reconciled dated topology ensemble; do not linearly rescale the whole tree from one local age.
- Create a sourced event registry with event class, start/end interval, geographic scope, taxon/node mapping rule and uncertainty.
- Implement an event-window statistic and an age-/branch-matched null before viewing correspondence results.
- Build EAzami-native continuous traits before testing whether continuous trait-environment relations recur.

## 7. PR #126 disposition

**Keep and reuse**

- the reconstruction-aware tip-label null and both frozen FAIL results;
- the distinction among recurrence, localization and shared branch change;
- the ML/UFBoot uncertainty propagation;
- JPN20/JPN29/JPN31 admission boundaries;
- deterministic serialization, figure/provenance validation, stop rules and negative-result language.

**Remove from the active standalone story**

- the Azami observational handoff as Result 1;
- the exact 62-estimand adapter and present-state covariance generators;
- “present-day phenotypic integration” as the central question;
- the assumption that Azami-exported continuous traits are eligible EAzami primary inputs.

The existing manuscript/DOCX bundle remains an immutable audit snapshot. It is **not submission-ready under the standalone contract**. Its continuous results may return only after independent EAzami measurement and an unchanged rerun.

## 8. Standalone title, figure sequence and claim ceiling

**Recommended title**

> **Recurrence and localization are distinct dimensions of capitulum evolution in a young thistle radiation**

This title is supported by the independent discrete core and states the general evolutionary insight without claiming convergence, lability or adaptation.

**JEB figure sequence**

1. **Natural experiment and admission design:** dominant Japanese radiation, contrasting colonization histories, Comp1061 uncertainty and EAzami-owned trait coverage.
2. **Trait-specific evolutionary depth:** state coverage, minimum-step distributions and root-state uncertainty for orientation, phyllary posture and stickiness.
3. **Recurrence versus localization:** branch placement support across ML/UFBoot trees, emphasizing that stable counts can coexist with uncertain edges.
4. **Trait-environment recurrence:** six-topology present PGLS and transition-weighted BIO15/BIO1 concordance with frozen nulls and coverage gate.
5. **Historical assembly:** discrete overlap now; independently rerun continuous reconstruction-null later. The dated event panel is added only after the chronogram and event-registry gates pass.

For an immediate submission, Figures 1–4 are the core and Figure 5 is supplementary or deferred. DTT and event correspondence must not appear as current results.

**Claim ceiling**

> Authority-backed capitulum traits show repeated but trait-specific histories in a young Japanese thistle radiation; recurrence counts, transition localization and present or reconstructed niche concordance are distinct estimands. Current evidence does not establish independent origins, adaptive convergence, a shared historical module, or ecological-event causation.

## JEB positioning

JEB remains a defensible first target because the general contribution is an estimand distinction in evolutionary morphology, and the [journal's current aims and scope](https://academic.oup.com/jeb/pages/about) explicitly accept robust negative results when they produce new evolutionary insight. The safer current article type is a Research Article only if the independent trait, niche and topology layers are reported together with their full uncertainty. If the manuscript is restricted to three discrete histories without the completed niche recurrence layer, a focused Short Communication or a later submission is more realistic.

The active decision is therefore **JEB target retained; submission authorization withheld until the standalone input gate and manuscript rebuild pass**.
