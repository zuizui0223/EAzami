# Chapter 2 standalone mainline v1 — diversity depth

Status date: 2026-08-28

Scientific status: **COMPLETE_EXISTING_PUBLIC_HISTORY_CORE**

Submission status: **HOLD_JEB_PACKAGE_REBUILD_ONLY**

Machine-readable contract: `data/evidence/chapter2_diversity_depth_contract_v1.json`

## 1. One-page Chapter 1–3 research structure

The dissertation proceeds as **diversity breadth -> diversity depth -> own-data discrimination and mechanism**.

| Chapter | Primary axis | Evidence | Main question | Claim ceiling |
|---|---|---|---|---|
| 1 | present geographic and environmental space | continuous phenomics | where and at what scale does diversity recur? | association, not history or cause |
| 2 | published phylogenetic history | public Comp1061 evidence plus authority-backed states | how many changes are required and how well are they localized? | conditional history, not convergence or adaptation |
| 3 | own Japan-wide genomic and phenotypic sampling | RAD-seq, same-individual phenotype and cytotype, later experiments | which Chapter 2 histories survive, and what mechanisms or fitness pathways are supported? | own-data topology and mechanism within predeclared gates |

Chapter 2 is **scientifically complete with existing public evidence**. Chapter 3 is not a completion gate. Chapter 2 supplies a bounded answer and exposes the observations that would most efficiently distinguish the remaining histories; Chapter 3 prospectively tests them.

This dependency is directional. Chapter 2 uncertainty may determine Chapter 3 sampling. A later Chapter 3 result cannot retroactively turn a Chapter 2 minimum step into an independent origin, convergence event or adaptation.

## 2. Central question and subquestions

**Central question**

> How much recurrent change is required in the traits that form alternative capitulum configurations within a young Japanese thistle radiation, and which evolutionary events remain identifiable under phylogenetic and observation uncertainty?

Subquestions:

1. How many unordered state changes are minimally required for each authority-defined trait?
2. Are these recurrence lower bounds robust across 1,000 UFBoot topologies?
3. Are the responsible branches identifiable, or do several histories remain equally admissible?
4. Do observed trait configurations map onto one shared transition-localization pattern?
5. Does species-tip compression hide state multiplicity or minimum changes?
6. Which own-data samples would most strongly distinguish the remaining histories?

The biological contribution is **configuration diversity with recurrent trait change within a dominant radiation**. The inferential contribution is that **recurrence count and transition localization are separate properties**. A stable count can coexist with uncertain evolutionary events.

## 3. Standalone EAzami analysis pipeline

1. **Phylogenetic admission.** Use the independently reconstructed Comp1061 ML phylogram and 1,000 UFBoot trees. Retain JPN20 and JPN31 exclusions exactly as frozen. Interpret branch lengths as substitutions/site, never absolute time.
2. **Independent state admission.** Admit only exact-concept authority descriptions into the orientation, phyllary-posture and stickiness ontologies. Preserve missing and ambiguous states.
3. **Trait-specific recurrence.** Calculate unordered parsimony minima on the ML tree and every bootstrap topology. Treat them as lower bounds, not independent-origin counts.
4. **Placement identifiability.** Record edges forced to change across every minimum-cost assignment and their bootstrap frequencies. Report placement separately from counts.
5. **Historical integration diagnostic.** Compare module-pair transition localization using both the substitution-length ML tree and equal-branch topology sensitivities. Require agreement before claiming a common history.
6. **Bounded secondary layers.** Retain the seven-taxon direct continuous panel and orientation–niche analyses as negative or borderline diagnostics. Neither is required to complete the discrete historical core.
7. **Inverse design.** Convert the unresolved histories into Chapter 3 sampling priorities with explicit falsifiers, linked individual measurements and rights/conservation gates.

Every layer can end in `supported`, `not_supported`, `not_evaluable` or `STOP`. Missing data are not imputed and range descriptions are not converted to midpoints.

## 4. Repository-wide inventory

The 17-row inventory remains the canonical audit of available material. Its roles are now separated from Chapter 2 completion:

- **Primary Chapter 2 core:** Comp1061 admission; orientation, phyllary and stickiness histories; recurrence/localization separation; topology-sensitive module overlap.
- **Supporting diagnostics:** the seven-taxon direct continuous panel; present orientation–niche PGLS; frozen branchwise niche concordance; sparse cytotype and colonization constraints.
- **Routed to Chapter 3:** Japan-wide own RAD-seq, same-individual phenotype and cytotype, population structure, field manipulation and fitness.
- **Routed to later work:** dated event windows, disparity-through-time and evolutionary predictive simulations.

The absence of an EAzami-owned Japan38 scalar phenotype panel limits continuous-history generalization. It does not invalidate the independently assembled discrete-history paper.

## 5. Analyses runnable now and final Chapter 2 result

The public-evidence core produces five bounded result groups:

1. **Radiation and configurations.** Published evidence places 36/38 sampled Japanese concepts in the dominant radiation. The authority-covered dominant-radiation subset contains at least three harmonized orientation x stickiness configurations; the source ontology retains four named combinations.
2. **Repeated assembly.** Orientation requires four to six changes, phyllary posture exactly three and stickiness exactly five across the admitted topology ensemble.
3. **Uneven event resolution.** Orientation has no individually forced ML edge and the JPN36 orientation terminal fraction is 0.201; the JPN36 phyllary terminal fraction is 0.754 despite an ambiguous root.
4. **Shared-history boundary.** Zero of three module pairs is consistently positive across branch-length-aware and equal-branch treatments.
5. **Observation-resolution bridge.** Species-tip coding hides white/coloured state multiplicity in 4/4 audited polymorphic systems; in the only morph-linked testable system the minimum changes from one to two.

The corresponding conclusion is:

> A dominant young radiation contains multiple capitulum configurations and requires repeated changes in three constituent traits, but public evidence resolves recurrence counts more reliably than the individual evolutionary events responsible for them.

## 6. Chapter 2 to Chapter 3 inverse design

The machine-readable bridge and priority table are:

- `data/evidence/chapter2_to_chapter3_radseq_bridge_v1.json`
- `data/evidence/chapter2_to_chapter3_sampling_priorities_v1.csv`

The first two focal tests are:

1. **JPN36 phyllary posture.** Test whether the 0.754 terminal-placement concentration survives an own nuclear topology ensemble and same-individual phenotype linkage.
2. **JPN06–JPN15 stickiness.** Test whether the canonical 100/100 sister contrast survives population-aware RAD-seq/network sensitivities. The species contrast remains non-causal; within-JPN15 neutralization versus sham is the separate necessity test.

Orientation requires broad topology discrimination rather than one nominated causal pair. Same-individual measurement across the Japan-wide panel tests whether current module non-synchrony persists when authority-level and sequenced-individual observations are no longer disconnected.

The all-Japan same-library RAD-seq product is a **sensitivity phylogeny/network** unless shared-locus, replicate, ploidy and reticulation gates support a common cross-species estimand. Failure of those gates routes inference to within-cytotype population ancestry and retains Comp1061 target capture as the species backbone.

## 7. PR #126 and legacy V3 disposition

**Retain**

- topology uncertainty and exact-concept admission;
- recurrence versus localization;
- reconstruction-aware null logic and preserved FAIL results as method provenance;
- deterministic outputs, stop rules and prohibited-claim checks.

**Do not use in the active standalone paper**

- Azami observational output as Result 1;
- Azami-derived Japan38 continuous values;
- present-day integration as the Chapter 2 starting estimand;
- field feasibility or function as historical evidence.

`MANUSCRIPT_JEB_V3.md` and its DOCX remain frozen audit history. `MANUSCRIPT_JEB_V4.md` is the active standalone draft.

## 8. JEB positioning and submission state

**Title**

> **Capitulum configuration diversity, recurrent trait change and uneven event resolution in a young thistle radiation**

**Figure sequence**

1. dominant-radiation context, taxon admission and observed configuration diversity;
2. module-specific recurrence-count distributions;
3. recurrence robustness versus forced-edge localization;
4. overlap boundary, species-tip compression and prospective sampling consequences.

The scientific paper no longer waits for own continuous measurements, RAD-seq, a dated tree or field outcomes. Submission authorization is held only for production work: revised figures, anonymous DOCX, reference audit and author declarations.

**Claim ceiling**

> Alternative capitulum configurations occur within the dominant young Japanese radiation and each of three authority-backed traits requires repeated minimum changes. Recurrence counts are resolved more strongly than individual event locations. Current evidence does not establish independent origins, adaptive convergence, developmental modularity, absolute timing or ecological-event causation.
