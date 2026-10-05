# EAzami — recurrent functional rebuilding of the Cirsium capitulum

## Active state — 2026-10-05

EAzami Chapter 2 is frozen for *Journal of Evolutionary Biology* submission as V10.

### Central paper question

> **How is a complex capitulum repeatedly assembled during a young radiation, are its repeatedly changing components plausible functional traits, and can the environmental trigger of their origin be identified?**

### Current answer

> **Orientation, phyllary posture and involucre stickiness repeatedly changed within one young *Cirsium* radiation, but at unequal evolutionary depths and without robust shared transition localization. Independent experiments make the components plausible distinct ecological interfaces. Orientation transitions track a present BIO15-up/BIO1-down regime, yet that regime fails as a model of the sole bounded historical origin event. The supported result is recurrent functional rebuilding; the selective trigger of individual rebuilding events remains unresolved.**

The active manuscript is:

- `docs/chapter2/MANUSCRIPT_JEB_V10_FUNCTIONAL_ASSEMBLY_ORIGIN_DECOUPLING.md`

The active figure/claim architecture is:

- `docs/chapter2/V10_FUNCTIONAL_ASSEMBLY_ORIGIN_DECOUPLING_SPINE.md`

The active validator is:

- `analysis/validate_manuscript_jeb_v10.py`

V10 validation is green:

- abstract: 219 words;
- main text before References: 3,982 words;
- keywords: 8;
- Azami image-paper dependency: none.

The five main figures, Supporting Information V5, anonymous line-numbered DOCX, separate title page and cover letter have passed automated validation and full-page visual QA.

## Historical core

Within the dominant Japanese radiation:

- orientation: ML minimum 6; UFBoot 4–6;
- phyllary posture: exactly 3 minimum changes;
- stickiness: exactly 5 minimum changes;
- phyllary is deeper-permissive than stickiness in 1000/1000 paired topologies;
- phyllary is deeper-permissive than orientation in 993/1000;
- orientation is deeper-permissive than stickiness in 905/1000;
- complete `phyllary < orientation < stickiness` ordering occurs in 898/1000;
- 0/3 trait pairs pass the robust shared-transition-localization rule.

These are topology-sensitivity summaries, not independent biological replicates or posterior probabilities.

## Functional interfaces and fitness leverage

The current leading mechanism domains are:

- orientation -> abiotic reproductive exposure / timing;
- phyllary architecture -> mechanical antagonist access;
- stickiness -> context-dependent arthropod-community filtering.

The pooled *Cirsium* reproductive-herbivory synthesis gives seed-output RR = 2.674 (95% CI 2.388–2.993) under reduced versus ambient insect herbivory, corresponding to an estimated 62.6% loss of potential seed output under ambient herbivory.

This is fitness-pressure context. It is not a pooled adaptive effect of the three focal traits.

## Orientation ecology

The fixed post-result U->D present-niche vector is BIO15 up + BIO1 down.

Exact finite-map ranks:

- n>=5: 16/792 = 2.02%;
- n>=3: 19/1716 = 1.11%;
- n>=10: 4/126 = 3.17%;
- strict bidirectional floor: 3/126 = 2.38%.

The result is explicitly retained as a post-result focused hypothesis, not an independent preregistered confirmation.

## Historical-origin boundary

The sole event with bounded chronology and palaeolocation does not preserve the current orientation regime:

- 99/376 scenarios match;
- only 6/94 chronologies match in all four regions;
- at 0.79–0.74 Ma, BIO15 moves opposite to the present expectation in all four regions;
- robust broader climate classes: 0/324;
- robust global sea-level classes: 0/21.

Therefore the V10 claim is event-specific:

> **For this orientation event, the present ecological association and the tested coarse environment of its reconstructed origin are empirically separable.**

The result does not show that historical environment was irrelevant.

## Azami separation

The separate Azami image-angle dataset is excluded from the V10 manuscript, figures, SI and submission materials. V10 is therefore standalone and does not depend on the submission status of the Azami paper.

## Causal handoff

The next genuinely independent ecological test is the prospective **aza3** field programme:

`gravity-referenced trait manipulation -> ecological mechanism -> pollen/reproductive process -> filled achenes`

Priority order:

1. orientation manipulation/sham;
2. phyllary/spine access experiment;
3. stickiness neutralization/restoration;
4. colour visible/UV/pigment pathway.

Until those experiments, EAzami supports recurrent mosaic rebuilding plus plausible functional interfaces and transition-level ecological structure, not demonstrated adaptation.

## Submission work remaining

Scientific analysis and V10 production are complete. The validated package contains:

- five machine-generated main figures;
- synchronized Supporting Information V5;
- anonymous line-numbered main DOCX with five embedded figures and alt text;
- separate title-page DOCX;
- separate Supporting Information DOCX;
- cover-letter DOCX.

Full visual QA passed on 22 + 2 + 15 + 2 pages.

Only human/archival completion remains:

1. finalize author order, affiliations, corresponding-author details and ORCID;
2. complete acknowledgements, funding, conflict-of-interest and CRediT statements;
3. insert the final immutable archive URL, exact submission commit and DOI/accession;
4. enter the same metadata in the journal submission system.

## Claim boundary

Do not claim:

- minimum changes = independent origins;
- relative lineage depth = calendar time or evolutionary rate;
- 0/3 shared localization = complete genetic/developmental independence;
- transition–niche tracking = climate causation, selection or adaptation;
- the sole historical orientation event generalizes to all trait origins;
- external public confirmation succeeded;
- one universal stickiness defence;
- one recurring coarse historical environmental trigger.

## Legacy audit compatibility

Earlier packages remain **audit snapshots** in Git history. The following exact labels are retained only because historical validators still verify them:

- `COMPLETE_EXISTING_PUBLIC_HISTORY_CORE`;
- `Capitulum configuration diversity, minimum change counts`;
- `MANUSCRIPT_JEB_V3.md`.

They are not the active scientific route.

### Additional frozen routing aliases

The following strings are retained verbatim for historical test compatibility only; they do not define the current repository mainline:

- `Chapter 1: present-day space/environment`
- `Chapter 2: evolutionary time/history`
- `Chapter 3: own RAD-seq + linked phenotype/function`
- `Present-state v3/v4 covariance generators`
