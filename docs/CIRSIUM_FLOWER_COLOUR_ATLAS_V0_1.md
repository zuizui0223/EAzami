# Cirsium flower-colour atlas v0.1 — source-backed seed and rate-fit gate

Date: 2026-08-12

## Why this atlas is now a load-bearing analysis

The partial-calibrated Arenicola Mk sensitivity shows that the inferred direction of the `C. brevicaule` / `C. irumtiense` colour transition depends on assumptions about `q(C->W)` versus `q(W->C)` and the deeper root state. Under symmetric low-to-moderate rates, a coloured Arenicola ancestor is favoured; under faster or asymmetric transition models, that support weakens and some scenarios favour a white ancestor.

Therefore the broad comparative question — how often white flowers evolve and whether coloured flowers can return — is not separate from the Ryukyu case. A broader source-backed *Cirsium* flower-colour atlas is required to constrain biologically plausible transition-rate models.

This v0.1 is **not yet a rate-estimation dataset**. It establishes provenance, unit-of-observation and coding rules before expansion.

## Current frozen state

The expanded v0.1 contains **19 records**:

- 16 reviewed focal records;
- 3 pending Japan seed records;
- 13 taxon-level records;
- 6 direct sample-level var. *takaoense* records.

Nine taxon-level W/C records currently pass the strict rate-fit eligibility contract:

- `C = 6`;
- `W = 3`;
- phylogeny contexts = `Arenicola`, `Nipponocirsium`, `Sinocirsium`.

The atlas therefore now clears the provisional minimum coloured-tip and minimum phylogeny-context gates, but **still fails the minimum total taxon-tip and minimum white-tip gates**. `transition_rate_fit_ready` remains `false`.

## Architecture

Canonical schema:

- `data/schema/flower_colour_records.csv`

Builder:

- `analysis/build_cirsium_flower_colour_atlas_v0_1.py`

Validator/readiness gate:

- `analysis/validate_colour_atlas.py`

Frozen atlas:

- `data/evidence/cirsium_flower_colour_atlas_v0_1.csv`

Readiness summary:

- `analysis/cirsium_flower_colour_atlas_v0_1_readiness.json`

Validation workflow:

- `.github/workflows/validate-cirsium-flower-colour-atlas.yml`

## v0.1 evidence streams

### 1. Taxon-level Arenicola/Nipponocirsium

Six source-backed taxon-level flower states are imported from:

- `data/evidence/arenicola_flower_colour_history_evidence_v1.csv`

| taxon | state | phylogeny context | v0.1 rate-fit status |
|---|---:|---|---|
| *C. brevicaule* | W | Arenicola | eligible |
| *C. irumtiense* | C | Arenicola | eligible |
| *C. morii* | C | Nipponocirsium | eligible |
| *C. pengii* | C | Nipponocirsium | eligible |
| *C. kawakamii* | W | Nipponocirsium | eligible |
| *C. tatakaense* | C | Nipponocirsium | eligible |

### 2. Taxon-level Sinocirsium expansion

Three additional states directly stated in Chang et al. 2026 are frozen in:

- `data/evidence/chang2026_sinocirsium_taxon_colour_evidence_v1.csv`

| taxon | state | treatment |
|---|---:|---|
| *C. japonicum* var. *albescens* | W | source explicitly states white / all-white corollas |
| *C. japonicum* var. *australe* | C | source explicitly states bluish-purple throughout |
| *C. japonicum* var. *fukienense* | C | bluish-purple to light/pale-purple shade variation; all remain binary C |

The *fukienense* shade variation is **not** treated as W/C polymorphism. Under the current binary question it remains anthocyanin-coloured throughout the reported range.

These three records are taxon-level, reviewed, source-located, mapped to the Sinocirsium phylogeny context and currently rate-fit eligible.

### 3. Direct var. takaoense W/BP polymorphism

Six directly morph-linked public samples are imported from:

- `data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv`

They retain three W and three C/BP observations with voucher, locality, SRA and BioSample linkage.

The atlas now also contains an explicit taxon-level aggregate:

- `ATL-T00` = *C. japonicum* var. *takaoense*, state `P`.

This aggregate exists specifically to prevent accidental fixed-state coding of a demonstrably W/C-polymorphic variety. It is not rate-fit eligible without an explicit polymorphic-state model or empirical within-variety genealogy.

The six sample rows are also excluded from cross-species transition-rate fitting. They are real direct observations but are not six independent macroevolutionary taxa. This prevents pseudo-replication.

### 4. Japan evidence seed

The existing seed is imported from:

- `data/japan_colour_evidence_seed.csv`

At v0.1 these remain `pending` because exact page-level provenance and nuclear-tree tip mapping have not yet been frozen.

Important examples:

- *C. pendulum*: purple/white polymorphism is kept as binary `P`, **not** collapsed to W or C;
- *C. yezoense*: textual coloured evidence is retained but excluded from rate fitting until exact provenance/tip mapping is frozen;
- *C. dipsacolepis*: colour remains `U` because the current seed explicitly says the page text does not code corolla colour and image colour has not been independently reviewed.

## Fine state versus binary state

The atlas keeps the original biological distinction and a separate binary analysis code.

Fine states:

- `white`
- `near_white`
- `pale_pink`
- `pink`
- `purple`
- `blue_purple`
- `polymorphic`
- `unknown`

Current binary coding contract:

- `white`, `near_white` -> `W`
- visible `pale_pink`, `pink`, `purple`, `blue_purple` -> `C`
- `polymorphic` -> `P`
- `unknown` -> `U`

`P` and `U` are never silently converted to W/C by the validator.

This binary coding is designed for the current anthocyanin-coloured versus white question. It does **not** imply that all coloured states are ecologically or biochemically equivalent. Later analyses may retain multistate colour classes or continuous reflectance/pigment measures.

## Observation unit is explicit

Allowed units:

- `taxon`
- `population`
- `sample`
- `voucher`

A record can be high-quality direct evidence without being a valid species-tree tip. `rate_fit_eligible=yes` currently requires:

1. `observation_unit=taxon`;
2. `assessable=yes`;
3. `review_status=reviewed`;
4. binary state `W` or `C`;
5. `phylogeny_tip_candidate=yes`;
6. direct source status;
7. exact source URL and locator;
8. declared phylogeny context;
9. no exclusion reason.

Thus neither sample-level *takaoense* W/BP records nor taxon-level polymorphic aggregates can leak into a fixed-state cross-species rate fit.

## v0.1 readiness gate

The current conservative engineering gate requires at least:

- 20 eligible taxon-level tips;
- 5 W tips;
- 5 C tips;
- 3 phylogenetic contexts;
- no polymorphic/unknown eligible tips;
- all eligible tips genuinely taxon-level.

Current status:

| gate | current | pass? |
|---|---:|---:|
| eligible taxon tips | 9 / 20 | no |
| W tips | 3 / 5 | no |
| C tips | 6 / 5 | yes |
| phylogeny contexts | 3 / 3 | yes |
| all eligible records taxon-level | yes | yes |
| no P/U in eligible set | yes | yes |

Therefore the remaining engineering blockers are now only:

- `minimum_taxon_tips`;
- `minimum_white_tips`.

These thresholds are **not a statistical theorem** and passing them will not automatically make ARD transition rates identifiable. They are a project gate to prevent fitting an asymmetric model to one tiny focal sister-clade dataset.

Even after the gate passes, actual ER/ARD analyses must still assess:

- phylogenetic coverage and sampling bias;
- branch-length and topology uncertainty;
- treatment of polymorphic taxa;
- hidden state / rate heterogeneity;
- model adequacy and parameter uncertainty;
- whether the number and distribution of W/C transitions can support asymmetric rates.

## Expansion order

### Priority A — white tips and phylogenetically independent contrasts

Because coloured-tip and context thresholds are already cleared, the next evidence search should not simply add more purple taxa. It should prioritize **source-backed white taxa and white/coloured sister contrasts** that sit on the current nuclear backbone.

Highest-value targets include:

- additional Chang 2025/2026 or closely connected East Asian taxa with explicit white corollas;
- verified Korean white forms;
- Japanese/continental *C. pendulum* populations while retaining polymorphism explicitly;
- Japanese/Zhejiang *C. sieboldii* contrasts;
- other independent white-flower lineages whose phylogenetic placement is already resolved.

### Priority B — current East Asian nuclear-tree tips

Continue adding direct flora/revision/voucher evidence for coloured taxa where needed for phylogenetic completeness, but do not inflate the dataset with redundant coloured tips merely to clear a row-count threshold.

Prefer floras, taxonomic revisions, primary descriptions and verified vouchers over image-only inference.

### Priority C — population-level polymorphism

For taxa such as *C. pendulum* and var. *takaoense*, retain each source-backed morph/population record separately and model polymorphism explicitly. Do not manufacture a single fixed species state where the taxon is demonstrably polymorphic.

### Priority D — broader Cirsium transition-rate reference

After East Asian coverage is solid, expand to a broader *Cirsium* backbone to constrain the frequency/asymmetry of white loss and coloured regain. This is what can eventually give a data-informed prior or comparative estimate for `q(C->W)` and `q(W->C)` rather than choosing those rates arbitrarily in the Arenicola sensitivity grid.

## Promotion rule

Do not fit or report a final asymmetric flower-colour transition-rate model from atlas v0.1.

The next promotion requires:

1. enough reviewed, phylogenetically distributed W/C taxon tips to clear the readiness gate;
2. an explicit taxon-name mapping to one or more credible nuclear trees;
3. a declared polymorphism model or exclusion/sensitivity rule;
4. ER versus ARD model comparison with uncertainty;
5. topology/branch-length sensitivity;
6. posterior/predictive or other model-adequacy checks appropriate to the chosen framework.

Only then should the inferred transition-rate distribution be fed back into the Arenicola loss-versus-regain analysis.

## Scientific interpretation

The current project hypothesis is therefore sharpened to:

> White-flower evolution appears recurrent in East Asian *Cirsium*, but whether coloured regain is genuinely rarer cannot be assumed from parsimony alone. The frequency asymmetry of white loss versus coloured regain must be estimated from a broader source-backed phylogenetic character dataset. The expanded v0.1 now spans three focal phylogeny contexts and clears the provisional coloured-tip threshold, but the comparative estimate remains blocked by too few total taxon tips and especially too few independent white tips. That estimated rate asymmetry will be a load-bearing input for deciding whether the *C. brevicaule–C. irumtiense* contrast more plausibly represents white loss, coloured regain, ancestral polymorphism or reticulate history.
