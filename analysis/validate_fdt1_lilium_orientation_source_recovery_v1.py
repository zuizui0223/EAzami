#!/usr/bin/env python3
"""Validate the bounded access STOP for the Lilium orientation study."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = {
    "route_id",
    "search_route",
    "query_or_identifier",
    "result_status",
    "evidence_source",
    "evidence_locator",
    "observed_content",
    "implication",
    "next_action",
    "claim_limit",
}
EXPECTED_STATUSES = {
    "primary_abstract_verified",
    "publisher_redirects_to_abstract",
    "author_request_only",
    "open_access_label_unresolved",
    "closed_no_pdf",
    "tdm_metadata_route_no_content",
}
FORBIDDEN_PROMOTION_TOKENS = (
    "generic_orientation_rr_ready",
    "interaction_coefficient_ready",
    "meta_analysis_ready",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("source-recovery audit has no header")
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
        return list(reader.fieldnames), rows


def validate(path: Path) -> dict[str, object]:
    fields, rows = read_rows(path)
    missing = sorted(REQUIRED_COLUMNS - set(fields))
    if missing:
        raise ValueError(f"source-recovery audit missing columns: {missing}")
    if len(rows) != 6:
        raise ValueError("the bounded recovery audit must retain six routes")
    route_ids = [row["route_id"] for row in rows]
    if len(route_ids) != len(set(route_ids)):
        raise ValueError("duplicate route_id")
    statuses = {row["result_status"] for row in rows}
    if statuses != EXPECTED_STATUSES:
        raise ValueError(f"source-recovery status drift: {sorted(statuses)}")
    for line, row in enumerate(rows, start=2):
        for field in REQUIRED_COLUMNS:
            if not row[field]:
                raise ValueError(f"line {line}: missing {field}")
        joined = " ".join(row.values()).lower()
        for token in FORBIDDEN_PROMOTION_TOKENS:
            if token in joined:
                raise ValueError(f"line {line}: forbidden promotion token {token!r}")

    primary = next(row for row in rows if row["result_status"] == "primary_abstract_verified")
    primary_text = " ".join(primary.values()).lower()
    if "positive slope-angle correlation" not in primary_text or "negative correlation" not in primary_text:
        raise ValueError("the slope-dependent direction was lost")

    return {
        "contract_version": "fdt1_lilium_orientation_source_recovery_v1",
        "status_date": "2026-08-26",
        "study": {
            "taxon": "Lilium duchartrei",
            "doi": "10.1111/jse.12002",
            "citation": "Sun and Yao 2013, Journal of Systematics and Evolution 51:405-412",
        },
        "routes_checked": len(rows),
        "primary_abstract_verified": True,
        "verified_numeric_fulltext_recovered": False,
        "orientation_by_slope_coefficient_and_covariance_recovered": False,
        "generic_orientation_response_ratio_identified": False,
        "retained_estimand": "direction of the orientation-by-slope interaction",
        "retained_direction_only_finding": "Seed set correlates positively with slope angle for natural down-slope controls and negatively for flowers manipulated to face up slope; visitation has the same reported tendency.",
        "effect_size_ready": False,
        "cross_study_orientation_meta_analysis_addition_ready": False,
        "stop_reason": "The primary abstract identifies a slope-dependent interaction, but bounded public access checks did not yield the model coefficient, covariance, sample sizes, group summaries, figures, or raw data.",
        "reopen_condition": "Obtain verified article tables/models or raw data through a lawful institutional or author route, preserving slope as a continuous moderator.",
        "do_not_repeat": "Do not convert the abstract's opposite slope correlations into a generic down-versus-up response ratio, infer coefficients from significance or direction, or treat an unresolved open-access badge as retrieved full text.",
        "claim_limit": "Lilium supports context dependence of orientation effects along slope. It does not currently supply a common effect size, a universal down-slope fitness advantage, or a transportable Cirsium parameter.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
