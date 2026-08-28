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

> Do orientation, phyllary posture and involucre stickiness share one evolutionary history in a young Japanese thistle radiation, or do recurrence and transition localization differ among modules?

Subquestions:

1. How many unordered state changes are minimally required for each authority-defined trait?
2. Are these recurrence lower bounds robust across 1,000 UFBoot topologies?
3. Are the responsible branches identifiable, or do several histories remain equally admissible?
4. Do module pairs show the same transition localization across branch-length-aware and topology-only diagnostics?
5. Which own-data samples would most strongly distinguish the remaining histories?

The general contribution is that **recurrence count and transition localization are separate properties**. A stable count can coexist with uncertain evolutionary events.

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

The public-evidence core produces five bounded results:

1. Orientation has 20 resolved concepts, requires six changes on the ML tree and four to six across UFBoot trees (median five), but no edge is individually forced on the ML tree.
2. Phyllary posture has ten resolved concepts and requires exactly three changes on all 1,000 trees. The JPN36 terminal edge is forced in 75.4% of trees, while root posture remains ambiguous.
3. Stickiness has 13 resolved concepts after the JPN24 authority extension and requires exactly five changes across all 1,000 trees.
4. No module pair is consistently positive across branch-length-aware and equal-branch topology diagnostics. The simple one-history whole-capitulum common-lability model is not supported.
5. The seven-taxon four-trait continuous diagnostic supports no topology-robust corrected retention result. Phyllary protrusion is a weak measurement-priority hint only.

The corresponding conclusion is:

> Robust repeated states coexist with uneven transition localization across capitulum modules. Existing evidence does not require one shared whole-capitulum history, while topology-conditioned alternatives identify high-information samples for prospective phylogenomic testing.

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

> **Robust recurrence but uncertain localization of capitulum trait evolution in a young thistle radiation**

**Figure sequence**

1. public Comp1061 scaffold, taxon admission and state coverage;
2. module-specific minimum-step distributions and forced-edge fractions;
3. branch-length-aware versus equal-branch module overlap;
4. Chapter 2 uncertainty mapped to Chapter 3 sampling and falsifiers.

The scientific paper no longer waits for own continuous measurements, RAD-seq, a dated tree or field outcomes. Submission authorization is held only for production work: revised figures, anonymous DOCX, reference audit and author declarations.

**Claim ceiling**

> Authority-backed capitulum traits show repeated but trait-specific histories in a young Japanese thistle radiation; recurrence counts, transition localization and present or reconstructed niche concordance are distinct estimands. Current evidence does not establish independent origins, adaptive convergence, a shared historical module, or ecological-event causation.
