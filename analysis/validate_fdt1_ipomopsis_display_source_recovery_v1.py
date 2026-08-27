#!/usr/bin/env python3
"""Validate the bounded source-recovery STOP for the Ipomopsis display study."""
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
    "publisher_record_verified_no_public_numeric_fulltext",
    "closed_no_repository_fulltext",
    "author_abstract_verified",
    "legacy_pdf_route_identified_no_capture",
    "rejected_content_mismatch",
}
FORBIDDEN_PROMOTION_TOKENS = (
    "effect_size_ready",
    "meta_analysis_ready",
    "numeric_fulltext_recovered",
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

    rejected = next(row for row in rows if row["result_status"] == "rejected_content_mismatch")
    rejected_text = " ".join(rejected.values()).lower()
    if "lesquerella fendleri" not in rejected_text or "0a30b448" not in rejected_text:
        raise ValueError("content-mismatch identity or hash was lost")

    return {
        "contract_version": "fdt1_ipomopsis_display_source_recovery_v1",
        "status_date": "2026-08-26",
        "study": {
            "taxon": "Ipomopsis aggregata",
            "doi": "10.1007/s004420050136",
            "citation": "Brody and Mitchell 1997, Oecologia 110:86-93",
        },
        "routes_checked": len(rows),
        "primary_abstract_verified": True,
        "verified_numeric_fulltext_recovered": False,
        "group_means_dispersions_sample_sizes_recovered": False,
        "content_mismatch_artifact_rejected": True,
        "display_effect_size_ready": False,
        "cross_study_display_meta_analysis_ready": False,
        "retained_direction_only_findings": {
            "pollinator_long_distance_attraction": "larger displays favoured",
            "predispersal_seed_predation": "higher on many-flowered plants",
            "maternal_fitness": "potential gain reported, but no common effect size identified",
        },
        "stop_reason": "Primary and author abstracts verify directions, but the bounded public recovery did not yield the article's numerical treatment summaries. The similarly named author PDF is a different article and is rejected.",
        "reopen_condition": "Obtain a verified full-text copy or author-supplied tables containing treatment definitions, sample sizes, group summaries and uncertainty through a lawful institutional or author route.",
        "do_not_repeat": "Do not ingest the rejected Lesquerella PDF, infer means from P-value signs, or repeat the same legacy-link and archive-index checks unless their records change.",
        "claim_limit": "The experiment supports a joint display benefit/enemy-cost direction. It does not yet identify a transportable magnitude, a pooled display effect, or a net adaptation estimate for Cirsium.",
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
