#!/usr/bin/env python3
"""Fail-closed consistency checks for the Chapter 2 scientific mainline."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"

REQUIRED = [
    CH / "README.md",
    CH / "MAINLINE_V2.md",
    CH / "MANUSCRIPT_V1.md",
    CH / "EVIDENCE_MAP_V1.md",
    CH / "FIGURE_TABLE_PLAN_V1.md",
    CH / "SUBMISSION_GATES_V1.md",
    ROOT / "data" / "evidence" / "chapter2_claim_registry_v1.csv",
    ROOT / "data" / "evidence" / "chapter2_result_role_map_v2.csv",
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

    mainline = (CH / "MAINLINE_V2.md").read_text(encoding="utf-8")
    require(
        mainline,
        [
            "phenotype → function → history → origin → convergence",
            "candidate functional trait",
            "trait-specific evolutionary histories",
            "origin discrimination",
            "adaptive convergence",
            "nuclear population-genomic DNA",
            "plastid haplotype",
            "cytotype",
            "62-target simulation programme",
            "auxiliary generative constraint",
        ],
        "MAINLINE_V2",
    )

    readme = (CH / "README.md").read_text(encoding="utf-8")
    require(
        readme,
        [
            "MAINLINE_V2.md",
            "phenotype → function → history → origin → convergence",
            "modular evolvability",
            "endpoint hypothesis",
            "Auxiliary simulation lane",
        ],
        "Chapter 2 README",
    )

    plan = (ROOT / "docs" / "RESEARCH_PLAN.md").read_text(encoding="utf-8")
    require(
        plan,
        [
            "phenotype → function → history → origin → convergence",
            "Stage 1 — phenotype to candidate functional trait",
            "Stage 2 — trait-specific evolutionary histories",
            "Stage 3 — discriminate origins of repeated states",
            "Stage 4 — test convergence",
            "Auxiliary lane — cross-scale generative constraints",
        ],
        "research plan",
    )

    manuscript = (CH / "MANUSCRIPT_V1.md").read_text(encoding="utf-8")
    require(
        manuscript,
        [
            "`NULL_COUPLED`",
            "16 paired",
            "0/64",
            "22/24",
            "median primary-cell match = **6/8**",
            "nuclear population-genomic DNA",
            "plastid haplotype",
            "cytotype",
        ],
        "legacy manuscript source material",
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

    with (ROOT / "data" / "evidence" / "chapter2_result_role_map_v2.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        role_rows = list(csv.DictReader(handle))
    if len(role_rows) < 20:
        raise AssertionError(f"expected >=20 result-role rows, found {len(role_rows)}")
    required_stages = {
        "Azami_phenotypic_decomposition",
        "EAzami_function",
        "EAzami_history",
        "EAzami_origin",
        "EAzami_convergence",
        "Auxiliary_scale_constraint",
        "Higher_order_synthesis",
    }
    observed_stages = {r["mainline_stage"] for r in role_rows}
    if not required_stages.issubset(observed_stages):
        raise AssertionError(f"missing result-role stages: {sorted(required_stages - observed_stages)}")

    with (ROOT / "data" / "evidence" / "chapter2_claim_registry_v1.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 16:
        raise AssertionError(f"expected >=16 legacy claims, found {len(rows)}")
    if not all(r["prohibited_interpretation"].strip() for r in rows):
        raise AssertionError("every legacy Chapter 2 claim needs a prohibited interpretation")

    # Prevent the statistical simulator from silently regaining the top-level history role.
    if "EAzami = constraints on admissible generative histories" in readme:
        raise AssertionError("README still defines EAzami primarily as a generative-history simulator")
    if "modular evolvability = organizing premise" in mainline:
        raise AssertionError("modular evolvability must remain an endpoint hypothesis")

    print("chapter2_mainline_v2_valid=true")
    print(f"result_role_rows={len(role_rows)}")
    print(f"legacy_claim_registry_rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
