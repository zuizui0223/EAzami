# Chapter 2 V10 — final submission metadata handoff

Status date: 2026-10-05

## Current state

Scientific content and production are frozen for the JEB V10 route.

Active manuscript:

- `MANUSCRIPT_JEB_V10_FUNCTIONAL_ASSEMBLY_ORIGIN_DECOUPLING.md`

Validated production outputs:

- anonymous line-numbered main manuscript with five embedded figures and alt text;
- separate title page;
- separate Supporting Information V5;
- separate cover letter;
- metadata/rsid scrub;
- automated manuscript, SI and DOCX-package validation;
- full-page visual QA.

Validated counts:

- abstract: 219 words;
- main text before References: 3,982 words;
- keywords: 8.

The separate Azami image manuscript is not a dependency of V10.

## Human-only fields still required

Before journal submission, the author team must supply or confirm:

1. complete author list and publication order;
2. numbered affiliations;
3. corresponding-author name, postal address and email;
4. ORCID identifiers;
5. acknowledgements;
6. funding agencies and grant numbers;
7. conflict-of-interest wording;
8. CRediT author contributions if used;
9. any access, permission or data-use statement requiring disclosure;
10. originality / not-under-consideration / all-authors-approved confirmation for the cover letter.

These fields are intentionally not inferred from repository history.

## Archive freeze

Archive completion must happen after the human metadata above is final.

Required archive fields:

- immutable public archive URL;
- exact final submission commit or tag;
- DOI/accession.

Do not archive the current placeholder title page as the final public metadata record.

## Final submission files

Production sources:

- `analysis/build_chapter2_jeb_docx_v10.py`;
- `analysis/validate_chapter2_jeb_docx_v10.py`;
- `.github/workflows/build-chapter2-jeb-v10-docx-package.yml`.

Expected files:

- `Chapter2_JEB_Anonymous_Manuscript_V10.docx`;
- `Chapter2_JEB_Title_Page_V10.docx`;
- `Chapter2_JEB_Supporting_Information_V10.docx`;
- `Chapter2_JEB_Cover_Letter_V10.docx`.

## Scientific claim ceiling

The submission supports recurrent mosaic rebuilding of the capitulum, distinct plausible functional interfaces, a structured present orientation transition regime, and failure of that regime as the tested coarse origin model for the sole bounded historical orientation event.

It does not establish adaptation, natural selection, convergence, exact transition ages, complete genetic/developmental independence or one universal historical environmental trigger.
