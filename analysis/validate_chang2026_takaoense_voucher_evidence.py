#!/usr/bin/env python3
"""Validate the frozen Chang 2026 var. takaoense voucher evidence ledger.

The ledger separates four evidence layers that must not be collapsed:

1. Supplementary Table S1 transcriptome voucher/locality records;
2. Supplementary Table S6 specimens-examined records;
3. main-text references to individual specimens;
4. Figure 1's definition of W and BP, without inventing the six tip labels.

The validator fails if an unresolved voucher is assigned a flower colour, if the
known S1/S6 herbarium conflict is silently harmonized, or if the six-voucher
membership changes.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

DEFAULT_INPUT = Path(
    "data/evidence/chang2026_takaoense_voucher_morph_evidence_2026-08-10.csv"
)
DEFAULT_SUMMARY = Path(
    "data/evidence/generated/chang2026_takaoense_voucher_evidence_summary.json"
)

REQUIRED_FIELDS = (
    "accepted_taxon",
    "location",
    "code",
    "voucher",
    "herbarium_supplement_s1",
    "supplement_s6_status",
    "supplement_s6_transcription",
    "supplement_s6_herbarium",
    "main_text_voucher_evidence",
    "figure1_state_definition",
    "direct_sample_morph_label",
    "flower_colour_state",
    "binary_colour_code",
    "review_status",
    "next_action",
    "source_artifact_sha256",
    "notes",
)

EXPECTED_CODES = {
    "ccy3559": "FC",
    "ccy3807": "TJ",
    "ccy3835": "NH",
    "ccy3560": "WY",
    "ccy3629": "FB",
    "ccy3839": "LT",
}
EXACT_S6 = {"ccy3559", "ccy3560", "ccy3629", "ccy3839"}
NOT_IN_S6 = {"ccy3807", "ccy3835"}
KNOWN_HERBARIUM_CONFLICT = "ccy3839"
EXPECTED_SOURCE_HASH = (
    "650f42cb876e0a7b68aac61b127cb9d7586a3ea0bac4e3070adf204b852251a9"
)
EXPECTED_FIGURE_DEFINITION = (
    "Figure 1 caption defines W=white-corolla and BP=bluish-purple-corolla"
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing header")
        missing = set(REQUIRED_FIELDS) - set(reader.fieldnames)
        extra = set(reader.fieldnames) - set(REQUIRED_FIELDS)
        if missing or extra:
            raise ValueError(
                f"{path}: schema mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        rows = []
        for index, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{path}:{index}: too many CSV fields: {row[None]!r}")
            cleaned = {key: clean(value) for key, value in row.items()}
            if any(cleaned.values()):
                rows.append(cleaned)
        return rows


def validate(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    if len(rows) != 6:
        raise ValueError(f"Expected six voucher rows, observed {len(rows)}")

    vouchers = [row["voucher"] for row in rows]
    counts = Counter(vouchers)
    duplicates = sorted(voucher for voucher, count in counts.items() if count != 1)
    if duplicates:
        raise ValueError(f"Duplicate/missing voucher rows: {duplicates}")
    if set(vouchers) != set(EXPECTED_CODES):
        raise ValueError(
            f"Voucher membership changed: {sorted(set(vouchers))}"
        )

    by_voucher = {row["voucher"]: row for row in rows}
    for voucher, expected_code in EXPECTED_CODES.items():
        row = by_voucher[voucher]
        if row["accepted_taxon"] != "Cirsium japonicum var. takaoense":
            raise ValueError(f"{voucher}: accepted taxon changed")
        if row["code"] != expected_code:
            raise ValueError(
                f"{voucher}: expected code {expected_code}, observed {row['code']}"
            )
        if row["source_artifact_sha256"] != EXPECTED_SOURCE_HASH:
            raise ValueError(f"{voucher}: supplement artifact hash changed")
        if row["figure1_state_definition"] != EXPECTED_FIGURE_DEFINITION:
            raise ValueError(f"{voucher}: Figure 1 state definition changed")
        if any(
            row[field]
            for field in (
                "direct_sample_morph_label",
                "flower_colour_state",
                "binary_colour_code",
            )
        ):
            raise ValueError(f"{voucher}: unsupported sample-level morph assignment")
        if row["review_status"] != "unresolved_figure_or_direct_record_required":
            raise ValueError(f"{voucher}: unresolved review status changed")
        if "no colour inferred" not in row["notes"].casefold() and voucher != "ccy3835":
            raise ValueError(f"{voucher}: no-inference note is missing")

    for voucher in EXACT_S6:
        row = by_voucher[voucher]
        if row["supplement_s6_status"] != "exact_collector_number_found":
            raise ValueError(f"{voucher}: expected an exact S6 collector record")
        if not row["supplement_s6_transcription"]:
            raise ValueError(f"{voucher}: S6 transcription missing")
        if not row["supplement_s6_herbarium"]:
            raise ValueError(f"{voucher}: S6 herbarium missing")

    for voucher in NOT_IN_S6:
        row = by_voucher[voucher]
        if row["supplement_s6_status"] != "collector_number_not_found_in_s6":
            raise ValueError(f"{voucher}: expected S6 non-recovery status")
        if row["supplement_s6_transcription"] or row["supplement_s6_herbarium"]:
            raise ValueError(f"{voucher}: non-recovered S6 record contains invented data")

    conflicts: list[str] = []
    concordant: list[str] = []
    for voucher in EXACT_S6:
        row = by_voucher[voucher]
        if row["herbarium_supplement_s1"] == row["supplement_s6_herbarium"]:
            concordant.append(voucher)
        else:
            conflicts.append(voucher)
    if conflicts != [KNOWN_HERBARIUM_CONFLICT]:
        raise ValueError(f"Unexpected S1/S6 herbarium conflicts: {conflicts}")
    conflict = by_voucher[KNOWN_HERBARIUM_CONFLICT]
    if (
        conflict["herbarium_supplement_s1"],
        conflict["supplement_s6_herbarium"],
    ) != ("TCF", "TNM"):
        raise ValueError("ccy3839 herbarium conflict was altered or harmonized")

    if not by_voucher["ccy3835"]["main_text_voucher_evidence"]:
        raise ValueError("ccy3835 main-text specimen evidence is missing")
    for voucher in set(EXPECTED_CODES) - {"ccy3835"}:
        if by_voucher[voucher]["main_text_voucher_evidence"]:
            raise ValueError(f"{voucher}: unexpected main-text evidence")

    return {
        "accepted_taxon": "Cirsium japonicum var. takaoense",
        "voucher_rows": len(rows),
        "unique_vouchers": len(set(vouchers)),
        "supplement_s6_exact_records": len(EXACT_S6),
        "supplement_s6_not_recovered": len(NOT_IN_S6),
        "s1_s6_herbarium_concordant": sorted(concordant),
        "s1_s6_herbarium_conflicts": conflicts,
        "main_text_individual_specimen_evidence": ["ccy3835"],
        "figure1_state_definition_available": True,
        "direct_sample_morph_assignments": 0,
        "unresolved_vouchers": sorted(vouchers),
        "next_evidence": (
            "Read the W/BP suffixes from Figure 1, inspect linked TNM/TCF voucher "
            "images or labels, or obtain author confirmation."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_rows(args.input)
    summary = validate(rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"voucher_rows={summary['voucher_rows']}")
    print(f"supplement_s6_exact_records={summary['supplement_s6_exact_records']}")
    print(f"supplement_s6_not_recovered={summary['supplement_s6_not_recovered']}")
    print("s1_s6_herbarium_conflicts=" + "|".join(summary["s1_s6_herbarium_conflicts"]))
    print(f"direct_sample_morph_assignments={summary['direct_sample_morph_assignments']}")
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
