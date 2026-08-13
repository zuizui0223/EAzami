#!/usr/bin/env python3
"""Validate the frozen six-sample Read2Tree panel against source-backed evidence."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

DEFAULT_PANEL = Path("sampling/chang2026_takaoense6_read2tree_panel_v1.csv")
DEFAULT_EVIDENCE = Path(
    "data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv"
)
SOURCE_EVIDENCE_LABEL = DEFAULT_EVIDENCE.as_posix()
EXPECTED_MORPHS = {"BP": 3, "W": 3}
PANEL_FIELDS = (
    "sample_id", "matched_run", "library_layout", "panel_role", "morph",
    "code", "voucher", "biosample", "source_evidence",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def expected_from_evidence(
    evidence: Sequence[Mapping[str, str]],
    evidence_path: Path,
) -> list[dict[str, str]]:
    if len(evidence) != 6:
        raise ValueError(
            f"Expected six morph-linked evidence rows, observed {len(evidence)}"
        )
    rows = []
    for source in evidence:
        code = clean(source.get("code"))
        voucher = clean(source.get("voucher"))
        run = clean(source.get("run"))
        biosample = clean(source.get("biosample"))
        morph = clean(source.get("published_figure_label")).upper()
        status = clean(source.get("evidence_status"))
        if not all((code, voucher, run, biosample, morph)):
            raise ValueError(f"Incomplete morph-linked evidence row: {source!r}")
        if status != "morph_and_public_accession_directly_linked":
            raise ValueError(
                f"Evidence row is not direct morph/accession evidence: {status}"
            )
        rows.append(
            {
                "sample_id": f"{code}_{voucher}",
                "matched_run": run,
                "library_layout": "PAIRED",
                "panel_role": "focal_colour_morph",
                "morph": morph,
                "code": code,
                "voucher": voucher,
                "biosample": biosample,
                "source_evidence": SOURCE_EVIDENCE_LABEL,
            }
        )
    return sorted(rows, key=lambda row: row["sample_id"])


def normalize_panel(
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    if len(rows) != 6:
        raise ValueError(f"Expected six frozen panel rows, observed {len(rows)}")
    normalized = [
        {field: clean(row.get(field)) for field in PANEL_FIELDS}
        for row in rows
    ]
    if any(row["library_layout"] != "PAIRED" for row in normalized):
        raise ValueError("All frozen panel rows must remain official PAIRED libraries")
    if any(row["panel_role"] != "focal_colour_morph" for row in normalized):
        raise ValueError("All frozen panel rows must remain focal_colour_morph")
    morphs = Counter(row["morph"] for row in normalized)
    if dict(morphs) != EXPECTED_MORPHS:
        raise ValueError(
            f"Expected 3 BP and 3 W panel rows, observed {dict(morphs)}"
        )
    return sorted(normalized, key=lambda row: row["sample_id"])


def validate(panel_path: Path, evidence_path: Path) -> list[dict[str, str]]:
    expected = expected_from_evidence(read_csv(evidence_path), evidence_path)
    observed = normalize_panel(read_csv(panel_path))
    if observed != expected:
        for index, (left, right) in enumerate(zip(observed, expected), start=1):
            if left != right:
                differing = [
                    field for field in PANEL_FIELDS if left[field] != right[field]
                ]
                raise ValueError(
                    f"Frozen Read2Tree panel row {index} differs from direct evidence "
                    f"in {differing}: panel={left!r}, expected={right!r}"
                )
        raise ValueError("Frozen Read2Tree panel differs from direct evidence")
    return observed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate(args.panel, args.evidence)
    print(f"validated_samples={len(rows)}")
    print("sample_ids=" + "|".join(row["sample_id"] for row in rows))
    print("runs=" + "|".join(row["matched_run"] for row in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
