#!/usr/bin/env python3
"""Fail-closed consistency checks for the Chapter 2 manuscript package."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"

REQUIRED = [
    CH / "README.md",
    CH / "MANUSCRIPT_V1.md",
    CH / "EVIDENCE_MAP_V1.md",
    CH / "FIGURE_TABLE_PLAN_V1.md",
    CH / "SUBMISSION_GATES_V1.md",
    ROOT / "data" / "evidence" / "chapter2_claim_registry_v1.csv",
    ROOT / "docs" / "RESEARCH_PLAN.md",
    ROOT / "docs" / "archive" / "RESEARCH_PLAN_FLOWER_COLOUR_LEGACY_2026-08-27.md",
]


def require(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise AssertionError(f"{label} missing required statements: {missing}")


def main() -> int:
    for path in REQUIRED:
        if not path.exists() or path.stat().st_size == 0:
            raise AssertionError(f"missing/empty Chapter 2 file: {path.relative_to(ROOT)}")

    manuscript = (CH / "MANUSCRIPT_V1.md").read_text(encoding="utf-8")
    require(
        manuscript,
        [
            "`NULL_COUPLED`",
            "16 paired",
            "0/64",
            "22/24",
            "median primary-cell match = **6/8**",
            "not a single reconstructed history",
            "nuclear population-genomic DNA",
            "plastid haplotype",
            "cytotype",
        ],
        "manuscript",
    )

    evidence = (CH / "EVIDENCE_MAP_V1.md").read_text(encoding="utf-8")
    require(
        evidence,
        [
            "PR #119",
            "PR #120",
            "PR #123",
            "Repeated minimum-change steps prove adaptive convergence",
            "JPN24 update handling",
        ],
        "evidence map",
    )

    gates = (CH / "SUBMISSION_GATES_V1.md").read_text(encoding="utf-8")
    require(
        gates,
        [
            "Submission-essential",
            "Preserve the negative result",
            "No new biological sampling is required",
            "nuclear population-genomic DNA",
        ],
        "submission gates",
    )

    plan = (ROOT / "docs" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
    require(
        plan,
        [
            "present phenotypic fields to admissible generative histories",
            "docs/chapter2/MANUSCRIPT_V1.md",
            "flower-colour loss/regain plan has been archived",
        ],
        "research plan",
    )

    with (ROOT / "data" / "evidence" / "chapter2_claim_registry_v1.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 16:
        raise AssertionError(f"expected >=16 claims, found {len(rows)}")
    ids = {r["claim_id"] for r in rows}
    if ids != {f"C2_{i:02d}" for i in range(1, 17)}:
        raise AssertionError(f"unexpected claim registry IDs: {sorted(ids)}")
    if not all(r["prohibited_interpretation"].strip() for r in rows):
        raise AssertionError("every Chapter 2 claim needs a prohibited interpretation")

    # The manuscript must preserve the distinction between the three model stages.
    for phrase in [
        "preregistered 14-family",
        "Held-out falsification",
        "Post-heldout minimal-structure diagnostic",
    ]:
        if phrase not in manuscript:
            raise AssertionError(f"missing stage distinction: {phrase}")

    print("chapter2_manuscript_v1_valid=true")
    print(f"claim_registry_rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
