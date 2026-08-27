# Chapter 2 figure and table plan v1

The paper should read visually as one inference line, not as two parallel Azami/EAzami projects.

## Figure 1 — Present phenotypic field → admissible generative histories

### Purpose

Make the dependency explicit before any numerical result appears.

### Layout

Left-to-right or top-to-bottom:

```text
GLOBAL / IMAGE EMPIRICAL LAYER
Azami
18 continuous capitulum endpoints
within-taxon + among-taxon hierarchy
9 environmental predictors
        ↓
PRESENT PHENOTYPIC FIELD
D + Σwithin + Σamong + cross-scale geometry + environment alignment
        ↓
FROZEN HANDOFF
62 exact observational estimands
        ↓
GENERATIVE INVERSE PROBLEM
14 frozen model families
same 1,874-row / 124-taxon exogenous environment design
        ↓
progressively stronger constraints
scalar geometry → held-out inferential geometry
        ↓
ADMISSIBLE / REJECTED HISTORY CLASSES
        ↓
REALIZED-HISTORY DATA
Japan38 nuclear topology
population nuclear DNA + plastid + cytotype
functional intervention
```

### Main visual message

Azami defines the object. EAzami cannot exist as a second independent trait analysis because its scoreable outputs are defined by the Azami handoff.

### Avoid

- `snapshot` as the only label; use `present phenotypic field` in the main panel.
- arrows from EAzami back into the observed Azami results that imply post-hoc retuning.
- `true history` endpoint.

---

## Figure 2 — The empirical field and the 62-target handoff

### Panel A: hierarchical phenotype representation

Show the same 18D phenotype being decomposed into:

- observation-level distributions;
- within-taxon centred structure;
- taxon-median among-taxon structure.

A heatmap or reduced summary of association-strength matrices can illustrate that within and among geometry are related but not identical.

### Panel B: environment blocks

Display the six frozen blocks:

1. core thermal — BIO1, BIO4;
2. core precipitation — BIO12, BIO15;
3. radiative/atmospheric drying — radiation, VPD;
4. mechanical exposure — wind;
5. growing-season water input — GSP;
6. climatic productivity — NPP.

### Panel C: handoff accounting

Use a compact stacked diagram/table:

- 6 structure targets;
- 24 block-R² targets;
- 12 coefficient-cosine targets;
- 20 incremental partial-R² targets;
- total = 62.

### Panel D: fixed model design

Show `n=1,874 observations`, `124 taxa`, all nine predictors retained, observed phenotype removed before simulation.

### Source

- `data/evidence/azami_capitulum_space_handoff_report_v1.json`
- `data/evidence/source/azami_capitulum_space_eazami_targets_run33035785120.csv`
- `data/evidence/source/azami_capitulum_environment_eazami_targets_run33035785120.csv`
- `data/evidence/source/azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv`
- `data/evidence/azami_capitulum_v3_estimand_contract_v1.json`

---

## Figure 3 — Scalar winner, independent falsification, and failed rescue

This is the central result figure.

### Panel A: preregistered 14-family scalar comparison

Recommended plot:

- x = model family;
- y = total scalar discrepancy;
- paired draw points/intervals;
- `NULL_COUPLED` highlighted only by label/annotation, not visually dramatized beyond normal plotting conventions.

Annotate:

- median 2.2133;
- 16/16 primary paired rank 1;
- replication sensitivity also rank 1;
- second family median 14.7612.

### Panel B: held-out 64-draw falsification

Show frequency of the primary 8-cell pattern under frozen `NULL_COUPLED`:

- observed pattern target = 1;
- null matches = 0/64;
- Wilson 95% upper bound ≈ 0.0566.

A binary-cell tile plot should show the observed support pattern alongside marginal null support frequencies.

Critical annotations:

- among omnibus min5 = 6/64;
- among omnibus min2 = 6/64;
- among GSP min5 = 0/64;
- among GSP min2 = 1/64.

### Panel C: post-heldout five-family diagnostic

Plot median primary cells matched out of 8, with full-pattern frequency and paired superiority over NULL indicated separately.

Key family:

`PROCESS_AMONG_ONLY_SHARED_COUPLED`

- median 6/8;
- full pattern 6/24;
- superiority 22/24;
- fails preregistered median ≥7/8 gate.

Add a horizontal adequacy threshold at 7/8.

### Panel D: interpretation

Small conceptual inset:

```text
scalar snapshot constraint
        ↓
NULL remains admissible
        +
held-out hierarchical support
        ↓
NULL rejected as full explanation
        +
existing process additions
        ↓
no adequate family
```

### Source

- `data/evidence/azami_capitulum_v3_one_shot_decision_v1.json`
- `data/evidence/azami_capitulum_v3_one_shot_family_summary_v1.csv`
- `data/evidence/azami_capitulum_v3_null_heldout_support_decision_v1.json`
- `data/evidence/azami_capitulum_v3_null_heldout_support_cell_frequencies_v1.csv`
- PR #123 canonical support-geometry decision/family summary.

---

## Figure 4 — From admissible histories to realized-history discriminators

### Purpose

Keep the historical and empirical follow-up in the same inference line without pretending that simulation recovered actual history.

### Panel A: Japan38 nuclear history layer

Schematic nuclear tree or compact topology panel with three categorical overlays:

- orientation;
- phyllary posture;
- stickiness.

Do not turn unresolved states into inferred tip states.

Report only topology-robust lower bounds:

- orientation: ML 6, UFBoot 4–6;
- phyllary: 3 across all UFBoot trees;
- stickiness: use the latest **merged** canonical authority-extension result at figure-freeze time.

### Panel B: what the tree can and cannot distinguish

Tree-level repeated state changes still leave:

```text
standing ancestral variation
        vs
introgression / gene flow
        vs
lineage-specific origin
```

### Panel C: next ancestry measurement

Show one plant/individual linked to:

- standardized capitulum phenotype;
- nuclear population-genomic ancestry;
- plastid haplotype;
- cytotype/genome size.

This directly answers the user-facing question “nuclear DNA + what?” and makes the next data gate visually concrete.

### Panel D: functional gate

Separate downstream chain:

`trait → mutualist / antagonist / abiotic pathway → viable reproductive output`.

Use dashed arrows until independent field manipulation exists.

---

# Main tables

## Table 1 — Frozen empirical constraints

Columns:

- target class;
- number of targets;
- biological scale;
- statistic;
- interpretation;
- causal status.

Rows: structure, block R², coefficient geometry, incremental partial R².

## Table 2 — Sequential model verdicts

Columns:

- stage;
- models tested;
- data used;
- predeclared decision rule;
- result;
- what was rejected;
- what remains admissible.

Rows:

1. 14-family scalar one-shot;
2. frozen-null held-out support validation;
3. five-family post-heldout diagnostic.

This table should make it impossible for a reader to mistake PR #123 for a reranking of PR #119.

## Table 3 — Evidence ladder and claim boundary

Rows:

- present phenotype;
- structural reproduction;
- inferential support;
- nuclear transition history;
- population ancestry;
- functional causality;
- molecular mechanism.

Columns:

- current evidence;
- strongest allowed claim;
- data still required.

---

# Supplementary figures

## Figure S1

Exact 62-target registry and score class membership.

## Figure S2

All 14 family draw distributions for primary and min2 sensitivity.

## Figure S3

Pairwise win matrix for PR #119.

## Figure S4

20 held-out support cells: observed state, null support frequency, probability of observed state.

## Figure S5

Five-family post-heldout diagnostic full draw distribution.

## Figure S6

Japan38 trait-state source coverage and unresolved concepts.

## Figure S7

Claim-boundary diagram: scalar fit ≠ causal history; repeated parsimony ≠ adaptation.

---

# Figure production order

1. Figure 3 first — it contains the paper's actual discovery.
2. Figure 1 second — align the conceptual story to Figure 3 rather than inventing theory independently.
3. Figure 2 third — explain exactly what the models received.
4. Figure 4 last — use only current merged history evidence.

The manuscript should be considered visually coherent only if a reader can infer the entire logic from Figures 1–4 without treating Azami and EAzami as parallel columns.
