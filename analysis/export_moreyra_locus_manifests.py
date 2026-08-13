#!/usr/bin/env python3
"""Export named locus manifests from the public Moreyra filtering audit.

The input is produced by ``summarize_moreyra_locus_filter.py`` from the three
files in ``ldmoreyra/A-thorny-tale``.  Four reproducible sets are exported:

* the full public 1,061-locus universe;
* the 531 loci passing the public warning-count and raw-occupancy screen;
* the 241 no-warning, high-occupancy loci;
* the 290 high-occupancy loci that still require unavailable manual gene-tree
  decisions.

The script deliberately does not emit or name an "exact Moreyra 350" set.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_INPUT = Path(
    "data/evidence/generated/moreyra_author_repository/"
    "paralog_locus_filter_reconstruction.csv"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/moreyra_author_repository/locus_sets")

SET_FILENAMES = {
    "public_1061": "moreyra_public_1061_loci.txt",
    "reproducible_531": "moreyra_reproducible_531_candidate_loci.txt",
    "conservative_241": "moreyra_conservative_241_no_warning_loci.txt",
    "manual_review_290": "moreyra_manual_review_290_candidate_loci.txt",
}


def clean(value: object) -> str:
    return str(value or "").strip()


def parse_bool(value: object) -> bool:
    return clean(value).casefold() in {"true", "1", "yes", "y"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
    if not rows:
        raise ValueError(f"{path}: no locus rows")
    required = {
        "locus",
        "paralog_warning_class",
        "occupancy_ge_0_80",
        "passes_reproducible_warning_and_occupancy_screen",
        "final_350_membership",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    loci = [row["locus"] for row in rows]
    if len(loci) != len(set(loci)):
        raise ValueError(f"{path}: duplicate locus names")
    return rows


def build_sets(rows: Sequence[Mapping[str, str]]) -> dict[str, list[str]]:
    public = sorted(row["locus"] for row in rows)
    reproducible = sorted(
        row["locus"]
        for row in rows
        if parse_bool(row["passes_reproducible_warning_and_occupancy_screen"])
    )
    conservative = sorted(
        row["locus"]
        for row in rows
        if row["paralog_warning_class"] == "no_paralog_warning"
        and parse_bool(row["occupancy_ge_0_80"])
    )
    manual = sorted(
        row["locus"]
        for row in rows
        if row["paralog_warning_class"]
        == "manual_gene_tree_review_1_to_10_warnings"
        and parse_bool(row["occupancy_ge_0_80"])
    )
    sets = {
        "public_1061": public,
        "reproducible_531": reproducible,
        "conservative_241": conservative,
        "manual_review_290": manual,
    }
    if set(conservative) & set(manual):
        raise ValueError("Conservative and manual-review locus sets overlap")
    if set(reproducible) != set(conservative) | set(manual):
        raise ValueError(
            "The reproducible candidate set must equal conservative plus manual-review loci"
        )
    if not set(reproducible).issubset(public):
        raise ValueError("Candidate loci are not a subset of the public universe")
    return sets


def text_payload(loci: Iterable[str]) -> str:
    return "".join(f"{locus}\n" for locus in loci)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_outputs(outdir: Path, sets: Mapping[str, Sequence[str]]) -> dict[str, object]:
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, object]] = []
    for key, filename in SET_FILENAMES.items():
        payload = text_payload(sets[key])
        path = outdir / filename
        path.write_text(payload, encoding="utf-8")
        manifest_rows.append(
            {
                "set_key": key,
                "filename": filename,
                "locus_count": len(sets[key]),
                "sha256": sha256_text(payload),
                "interpretation": {
                    "public_1061": "all named loci in the public matrices",
                    "reproducible_531": (
                        "warning count <=10 and raw sequence occupancy >=0.80; "
                        "pre-manual candidate set"
                    ),
                    "conservative_241": (
                        "no public paralog warning and raw sequence occupancy >=0.80"
                    ),
                    "manual_review_290": (
                        "1-10 warning samples and raw occupancy >=0.80; manual "
                        "orthology outcome unavailable"
                    ),
                }[key],
            }
        )

    manifest_path = outdir / "locus_set_manifest.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("set_key", "filename", "locus_count", "sha256", "interpretation"),
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    summary = {
        "source": "ldmoreyra/A-thorny-tale public summary matrices",
        "sets": {row["set_key"]: row for row in manifest_rows},
        "exact_moreyra_350_exported": False,
        "reason": (
            "The exact final 350 retained loci depend on unavailable manual gene-tree "
            "and final alignment decisions."
        ),
    }
    (outdir / "locus_set_manifest.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_rows(args.input)
    sets = build_sets(rows)
    summary = write_outputs(args.outdir, sets)
    for key in SET_FILENAMES:
        record = summary["sets"][key]
        print(f"{key}={record['locus_count']} sha256={record['sha256']}")
    print(f"exact_moreyra_350_exported={summary['exact_moreyra_350_exported']}")
    print(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
