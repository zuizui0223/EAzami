# Chapter 3 P01 public population availability audit v1

Status date: 2026-09-03

## Decision

The P01 genetic design requires at least two independently authorized populations per focal concept (16 individuals/concept minimum), with three populations and 24 individuals/concept preferred. Current public official information does **not** establish that this minimum population replication is presently available for either focal concept. Sampling therefore remains fail-closed until current site-specific verification and authorization are obtained outside the public repository.

No exact sensitive coordinates are stored here.

## JPN06 — Cirsium dipsacolepis

Official Ehime Red Data Book information classifies the species as CR within Ehime and reports that, among several historically reported prefectural localities, current occurrence was confirmed in only one locality while other previously reported localities were not confirmed. This is useful evidence that historical locality lists cannot be treated as current populations.

Public-data decision:

`minimum_two_current_populations_not_verified_from_audited_official_public_sources`

Implication for P01:

- retain three anonymous population slots P1–P3;
- do not assign a historical locality to a slot merely because it appears in older distribution text;
- require current occurrence verification, census, land access, DNA tissue permission, voucher permission and conservation review before `admit_for_sampling=yes`;
- if only one current population can be responsibly authorized, P01 cannot test the predeclared ancestry-matched multi-population history and must be downgraded rather than padded with convenience samples.

Official source consulted:

- Ehime Prefecture Red Data Book, Cirsium dipsacolepis: https://www.pref.ehime.jp/reddatabook2014/detail/09_04_009040_6.html

## JPN15 — Cirsium lineare

Official Ehime Red Data Book information classifies Cirsium lineare as CR within Ehime, describes it as originally very rare, and reports a limited confirmed occurrence record. The 2022 Ehime red-list summary also retains CR. Yamaguchi's official red-list material includes Cirsium lineare, providing a second broad prefectural evidence region, but the currently audited public materials do not by themselves establish two extant, collectable, authorization-ready populations.

Public-data decision:

`minimum_two_current_populations_not_verified_from_audited_official_public_sources`

Implication for P01:

- retain anonymous population slots P1–P3 rather than publishing sensitive sites;
- treat Ehime and Yamaguchi only as broad search/authorization regions, not as guaranteed populations;
- do not substitute the related var. discolor records for the exact JPN15 concept without a separate taxonomic admission decision;
- require the full population authorization gate before any sampling slot is activated.

Official sources consulted:

- Ehime Prefecture Red Data Book, Cirsium lineare: https://www.pref.ehime.jp/reddatabook2014/detail/09_04_009050_7.html
- Ehime Red List 2022 summary: https://www.pref.ehime.jp/uploaded/attachment/125862.pdf
- Yamaguchi Prefecture Red List 2018 material containing Cirsium lineare: https://www.pref.yamaguchi.lg.jp/uploaded/attachment/53765.pdf

## Conservation / permission interpretation

A red-list category is not itself a collection permit, and absence from a national red list is not permission to collect. Environment Ministry guidance notes that detailed locations may be withheld to prevent collection pressure and that legal/ordinance restrictions can require confirmation with regional or prefectural authorities. P01 therefore stores only deidentified authorization IDs in the public analysis layer.

Official guidance:

- Ministry of the Environment red-list Q&A: https://www.env.go.jp/nature/kisho/hozen/redlist/qa.html
- Ministry of the Environment protected-plant framework for national/quasi-national parks: https://www.env.go.jp/nature/np/plant_prot/

## Current execution state

The public-data availability audit does not satisfy the field gate. The next required evidence is a private, current population/permission inventory that can map at least two authorized populations per concept onto the anonymous P1/P2 core slots. Until then all six rows in `data/templates/chapter3_p01_population_authorization_gate_v1.csv` remain `admit_for_sampling=no`.
