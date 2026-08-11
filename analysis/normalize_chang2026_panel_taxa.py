#!/usr/bin/env python3
"""Create a panel-only accepted-taxon view of the Chang reconciliation table.

The Chang supplement names two Japanese root-context samples as
``C. japonicum var. japonicum``.  The existing gene-tree design groups this
autonym at the species-level panel label ``Cirsium japonicum``.  This script
makes that one exact transformation explicit while retaining the source name in
``source_taxon``.  The original reconciliation evidence is never overwritten.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

DEFAULT_INPUT = Path(
    "data/evidence/generated/chang2026_complete_reconciliation/"
    "chang2026_sample_run_reconciliation.csv"
)
DEFAULT_OUTPUT = Path(
    "data/evidence/generated/chang2026_gene_tree_panel/"
    "chang2026_panel_taxon_normalized_reconciliation.csv"
)
DEFAULT_SUMMARY = Path(
    "data/evidence/generated/chang2026_gene_tree_panel/"
    "chang2026_panel_taxon_normalization_summary.json"
)

AUTONYM = "cirsium japonicum var. japonicum"
PANEL_ACCEPTED = "Cirsium japonicum"


def clean(value: object) -> str:
    return str(value or "").strip()


def canonical_taxon(value: object) -> str:
    text = clean(value).replace("_", " ")
    text = re.sub(r"^C\.\s+", "Cirsium ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip().casefold()


def normalize_rows(
    rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], dict[str, object]]:
    output: list[dict[str, str]] = []
    changed: list[dict[str, str]] = []
    for source in rows:
        row = {key: clean(value) for key, value in source.items()}
        source_taxon = clean(row.get("taxon"))
        row["source_taxon"] = source_taxon
        if canonical_taxon(source_taxon) == AUTONYM:
            row["taxon"] = PANEL_ACCEPTED
            changed.append(
                {
                    "code": clean(row.get("code")),
                    "voucher": clean(row.get("voucher")),
                    "source_taxon": source_taxon,
                    "panel_taxon": PANEL_ACCEPTED,
                }
            )
        output.append(row)

    source_counts = Counter(canonical_taxon(row["source_taxon"]) for row in output)
    panel_counts = Counter(canonical_taxon(row["taxon"]) for row in output)
    summary: dict[str, object] = {
        "input_rows": len(rows),
        "output_rows": len(output),
        "autonym_rows_collapsed_to_species_panel": len(changed),
        "changed_rows": changed,
        "source_taxon_counts": dict(sorted(source_counts.items())),
        "panel_taxon_counts": dict(sorted(panel_counts.items())),
        "normalization_rule": (
            "Cirsium japonicum var. japonicum is retained in source_taxon and "
            "mapped to Cirsium japonicum only for the species-level root-context "
            "role in the Chang gene-tree panel."
        ),
    }
    return output, summary


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
    if "taxon" not in fields:
        raise ValueError(f"{path}: missing taxon column")
    return rows, fields


def write_csv(path: Path, rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    output_fields = list(fields)
    if "source_taxon" not in output_fields:
        taxon_index = output_fields.index("taxon")
        output_fields.insert(taxon_index, "source_taxon")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, fields = read_csv(args.input)
    normalized, summary = normalize_rows(rows)
    write_csv(args.output, normalized, fields)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"input_rows={summary['input_rows']}")
    print(
        "autonym_rows_collapsed_to_species_panel="
        f"{summary['autonym_rows_collapsed_to_species_panel']}"
    )
    for row in summary["changed_rows"]:
        print(
            "PANEL_TAXON_MAP "
            f"{row['code']} {row['voucher']} "
            f"{row['source_taxon']} -> {row['panel_taxon']}"
        )
    print(args.output)
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
