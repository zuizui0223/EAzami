# JEB V7 submission requirements audit

Checked: 2026-09-03  
Official source: https://academic.oup.com/jeb/pages/author-guidelines

## Article type

Target: **Research Article**.

Current JEB limits/requirements:

- main manuscript maximum: **7,500 words**;
- abstract maximum: **250 words**;
- keywords: **4–10**;
- required structure: Abstract, Keywords, Introduction, Materials and methods, Results, Discussion; Conclusions optional;
- references: no numerical limit;
- figures/tables: no numerical limit.

## Double-anonymous review

The reviewer-facing main text must not contain author names or affiliations.

For the main text file, JEB specifically instructs authors **not** to include:

- Data Availability Statement;
- Acknowledgements;
- Funding information;
- Conflict of Interest statement.

These belong in a separate Title Page file and are not shared with reviewers.

The main text should be a single line-numbered file. At initial/revision submission, figures and tables should be embedded near first citation in the main text.

## AI disclosure

JEB requires AI-tool use to be disclosed both:

- in the cover letter; and
- in the Methods or Acknowledgements section.

The V7 working manuscript already contains an AI-assistance disclosure in the `Transparency` subsection of Methods. Therefore a separate reviewer-facing end-matter AI section is unnecessary and should not be duplicated in the anonymous main file.

## Data archiving

JEB requires raw data supporting the results to be archived in an appropriate public repository and a Data Availability Statement to be provided at revision. Scripts/analysis artefacts should also be archived where possible. JEB's Data Editor reviews archives before production.

For this project:

- GitHub remains the live auditable analysis repository;
- before submission/revision freeze, mint an immutable archival snapshot (preferably Zenodo or another DOI-bearing repository) for the exact V7 source/evidence/code package;
- the Title Page Data Availability Statement should point to the immutable archive, not only a mutable branch.

## V7 compliance status

| Requirement | Current status | Action |
| --- | --- | --- |
| Research Article scope | aligned | keep evolutionary-assembly generalization explicit |
| <=7,500 words | likely aligned, not yet machine-counted | add final word-count guard |
| Abstract <=250 | appears aligned, not yet machine-counted | add final word-count guard |
| 4–10 keywords | aligned | current list has 7 |
| double anonymous | aligned in current working text | preserve no authors/affiliations in main |
| line-numbered main file | not built yet | generate at DOCX freeze |
| figures near first citation | figure architecture frozen, files not built | build five V7 figures then embed |
| Data Availability outside anonymous main | working manuscript still carries a repository/end-matter section | strip during anonymous-main freeze; move to title page |
| AI disclosure | aligned in Methods | also repeat in cover letter; avoid duplicate end-matter section in anonymous main |
| immutable data/code archive | not frozen | mint DOI-bearing archive before submission/revision |

## Scientific fit to JEB

JEB states that Research Articles should provide new research or conceptual analyses making a significant contribution to evolutionary biology and prioritizes robust studies with insights generalisable across taxa. Negative results are acceptable when they provide robust new findings.

V7 is therefore better aligned than the earlier trigger-first framing because the submission now leads with:

`repeated multidimensional assembly -> unequal evolutionary depth -> non-synchronized histories -> scale-dependent ecological organization`

and uses the 0/324 and 0/21 historical-trigger ceiling as a final discrimination layer rather than the sole novelty.

## Submission-specific remaining gates

1. PR #160 pinned-runtime result is the final core numerical analysis.
2. Run the V7 manuscript evidence validator.
3. Add automated manuscript/abstract word counts.
4. Freeze the five V7 figures.
5. Build anonymous line-numbered main DOCX with figures embedded near first citation.
6. Build separate Title Page with authors, affiliations, ORCIDs, funding, COI, acknowledgements and Data Availability Statement.
7. Mint immutable DOI-bearing data/code snapshot.
8. Add AI disclosure to cover letter.
9. Prepare <=280-character social-media abstract requested by the JEB submission system.
