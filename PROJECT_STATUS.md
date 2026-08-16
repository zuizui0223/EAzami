# EAzami current resolution goal

Status date: 2026-08-16

## Main goal

EAzami is the evolutionary-resolution layer downstream of the global public-image macro screen in `zuizui0223/azami`.

The immediate goal is to produce an accepted, sensitivity-tested common-locus East Asian nuclear backbone and then use that framework to convert global trait hypotheses into explicit evolutionary histories.

Program order:

```text
Azami Chapter 1
Global public-image macro pattern / hypothesis generation
        ↓
EAzami nuclear history
Japanese origins + independent capitulum transitions
        ↓
Focal population / mechanism studies
Ancestry + gene flow + expression + pigment + interaction + fitness
```

Cross-project source of truth: `docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md`.

## Accepted public nuclear baseline

The current accepted inventory is:

- **294 biological tips**;
- **295 unique public SRRs**;
- **270 source-preserving analysis taxon labels**.

The old 302/303 inventory is superseded because eight Taiwan RNA-seq BioSamples/SRRs reused across Chang 2025 and Chang 2026 had been double-counted.

The accepted primary remains 294 tips until explicit promotion gates pass.

## Current independent augmentation candidates

| Candidate | Source | Strict loci | Biological-tip role |
|---|---|---:|---|
| EA01 / `PUBEA001` | *C. nipponicum* var. *yoshinoi* public SRA | 236/241 | independent candidate |
| CNIPG / `AUG_ULLEUNG_CNIP2024` | natural-Ulleung *C. nipponicum* public genome | 180/241 | independent cross-data-type candidate |
| EA02 / `PUBEA002` | *C. sairamense* public SRA | 239/241 | duplicate-readset control only; **not** an independent biological tip |

EA02 and the accepted baseline *C. sairamense* library have effectively identical raw-library and recovered-locus profiles. EA02 remains durable provenance / duplicate-control evidence but does not increment the biological-tip count.

If EA01 and CNIPG both pass their independent gates, the maximum public candidate ceiling is **296 tips / 0 new analysis labels**. This is not an accepted 296-tip tree until an explicit common paired-locus combined analysis also passes.

## Current promotion logic

For each independent candidate, augmented and baseline trees are compared on identical paired locus sets.

Automatic promotion requires the predeclared backbone safeguards, including:

1. RF = 0 on the shared 294-tip concatenated backbone;
2. an existing same-taxon baseline tip among the candidate's nearest baseline neighbours;
3. RF = 0 on the shared-species ASTRAL backbone;
4. consistency across the required BWA / BLASTx or cross-data-type sensitivities.

A failed criterion triggers manual biological review, not post-hoc threshold relaxation.

If both independent gates pass, the combined analysis uses exactly four scenarios on one baseline∩EA01∩CNIPG common-locus set within each accepted mapping mode:

- `baseline294`;
- `ea01_295`;
- `cnipg_295`;
- `ea01_cnipg_296`.

EA02 cannot enter these combined-tree inputs.

## Latest execution validation

The current 296-tip contracts are green:

- `Validate maximum public nuclear HPC handoff` run `31937355788` — success; artifact `9261030108`, digest `sha256:d8c4c3ff219a56f87e1deb411c02684b0d843e38096c3d144d78e1bc902a5d68`;
- `Validate maximum public combined-tree handoff` run `31937355816` — success; artifact `9261031804`, digest `sha256:e353612e5db39ac0416a1b3292074f0e58355dbfedfb6dee835eb7938d5f42ea`.

These runs validate code, contracts and fail-closed execution graphs. They do **not** mean the heavy 294-tip BWA/BLASTx + IQ-TREE + ASTRAL analysis has completed.

## Current Japanese-origin hypothesis

The working historical hierarchy is no longer a simple Japanese-monophyly question.

Current synthesis favours one dominant Japanese radiation plus rare secondary histories:

- **minimum defensible = 2 histories**: dominant radiation + *C. lineare*;
- **best current point hypothesis = 3 histories**: add *C. dipsacolepis*;
- **4+ histories = unresolved and not currently supported**.

The maximum-public nuclear tree is therefore a falsification test of 2 vs 3 vs 4+ histories, including explicit continental-neighbour placement and uncertainty.

Arenicola is not currently counted as a fourth entry without an independently bracketed continental source lineage.

## Current flower-colour inference

- Repeated white-flower evolution remains the best-supported general pattern in the current East Asian evidence.
- Arenicola currently favours white loss on *C. brevicaule*; regain in *C. irumtiense* is not established.
- var. *takaoense* remains a topology-supported candidate regain under directly documented W/BP sample states.
- species-level state compression is already demonstrable: the current population/sample-aware *takaoense* screen requires more minimum colour transitions than the collapsed species-tip treatment.
- DFR / ANS homologous reads are recoverable at assay level in the current three W and three BP young-leaf public RNA runs, but this is not differential floral expression or causal proof.

Molecular anthocyanin re-expression remains unresolved until population history, candidate orthology/coding state, floral expression, pigment and phenotype are linked.

## Azami → EAzami trait transition program

After the accepted nuclear topology ensemble is available, the analysis order is:

1. **flower colour** — estimate independent W↔C histories first;
2. **orientation** — map the global macro hypothesis onto the same supported nuclear framework;
3. **continuous head shape** — reconstruct history with measurement uncertainty rather than treating image variance as evolutionary variance;
4. **module coupling** — test whether colour, orientation and shape transitions are correlated or remain partly independent;
5. **next-generation defensive traits** — add phyllary spreading/recurvature, spine architecture, visible stickiness/glandularity and display architecture only after ontology and assessability are defined.

The bridge schema is frozen in:

- `data/evidence/azami_eazami_macro_to_micro_contract_v1.json`;
- `data/evidence/azami_eazami_trait_bridge_template_v1.csv`.

Issue #23 tracks the actual bridge / ancestral-state implementation.

## Sampling decisions that do not need to wait for a broad mainland tree

Population-level sampling can already prioritize:

- *C. japonicum* var. *takaoense* W/BP populations;
- Japanese W/coloured *C. pendulum*;
- Japanese W/coloured *C. sieboldii*;
- *C. brevicaule* + *C. irumtiense* Arenicola populations;
- var. *albescens* plus coloured Taiwan controls.

These are population-history / mechanism systems, not generic species-backbone completion.

Broad new China sampling remains deliberately unfrozen until the maximum-public tree identifies the continental branches that actually bracket unresolved Japanese histories.

## Remaining mainline gates

1. Execute the validated 294-tip baseline BWA and BLASTx workflows on HPC / large-memory compute.
2. Accept or reject the baseline concatenated and source-label ASTRAL trees under the frozen gates.
3. Complete EA01 independent paired-tree tests.
4. Complete CNIPG independent paired-tree tests.
5. If both pass, run the explicit 296 common-locus combined analysis.
6. Freeze the supported topology ensemble and taxon crosswalk for Japan-38, *lineare*, *dipsacolepis*, Arenicola and continental neighbours.
7. Populate the Azami→EAzami trait bridge without forcing polymorphic taxa to fixed states.
8. Run colour → orientation → shape ancestral-state / transition-history analyses.
9. Promote only replicated/high-information transitions to population genomics and ecological mechanism experiments.

## Stop rules

- `new_china_sampling_freeze_allowed` remains false until the public nuclear tree resolves the relevant mainland brackets.
- The current Azami grafted mega-tree is not the definitive ancestral-state tree.
- Species-level polymorphism is not collapsed to one fixed state for convenience.
- Macro correlations do not establish adaptation.
- Missing annotation or pathway-table coverage does not establish pathway loss.
- New defensive capitulum traits do not reopen Chapter 1; they form the next comparative layer unless required for a validity repair.

## Navigation

- Operational nuclear state: [docs/CURRENT_STATE_2026-08-14.md](docs/CURRENT_STATE_2026-08-14.md)
- Macro→micro roadmap: [docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md](docs/AZAMI_EAZAMI_MACRO_TO_MICRO_ROADMAP_2026-08-16.md)
- Trait bridge contract: [data/evidence/azami_eazami_macro_to_micro_contract_v1.json](data/evidence/azami_eazami_macro_to_micro_contract_v1.json)
- Current sampling decisions: [sampling/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv](sampling/SEQUENCING_PANEL_V0_3_EXACT_COVERAGE.csv)
- Capitulum-trait foundation: [docs/CAPITULUM_TRAIT_FOUNDATION.md](docs/CAPITULUM_TRAIT_FOUNDATION.md)
