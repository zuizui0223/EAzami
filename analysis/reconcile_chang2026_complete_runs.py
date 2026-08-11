#!/usr/bin/env python3
"""Reconcile Chang 2026 supplement samples to the complete published run set.

This adapter preserves the conservative scoring rules in
``reconcile_chang2026_ncbi_runs.py`` while adding two source-backed evidence
channels that its generic interface did not originally expose:

* numeric BioSample ``isolate`` values are converted to a ``ccy####`` voucher
  token only when that exact voucher exists in the supplement; and
* Figure 1's ``direct_figure_label`` column is normalized to the core
  ``published_figure_label`` schema.

Neither geography nor flower colour participates in run matching.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import reconcile_chang2026_ncbi_runs as core

DEFAULT_SUPPLEMENT = core.DEFAULT_SUPPLEMENT
DEFAULT_MORPHS = core.DEFAULT_MORPHS
DEFAULT_OUTDIR = Path(
    "data/evidence/generated/chang2026_complete_reconciliation"
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


def numeric_isolate(value: object) -> str:
    match = re.fullmatch(
        r"(?:ccy)?\s*[-_ ]?(\d+)", clean(value), flags=re.IGNORECASE
    )
    return match.group(1) if match else ""


def enrich_runinfo_with_voucher_aliases(
    supplement_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], dict[str, str]]:
    """Add exact supplement voucher aliases derived from BioSample isolate values."""
    supplement_vouchers = {
        clean(row.get("voucher")).casefold(): clean(row.get("voucher"))
        for row in supplement_rows
        if clean(row.get("voucher"))
    }
    alias_to_runs: dict[str, list[str]] = defaultdict(list)
    enriched: list[dict[str, str]] = []

    for source in runinfo_rows:
        row = {key: clean(value) for key, value in source.items()}
        digits = numeric_isolate(row.get("biosample_isolate"))
        alias = f"ccy{digits}" if digits else ""
        canonical = alias.casefold()
        if alias and canonical in supplement_vouchers:
            alias = supplement_vouchers[canonical]
            run = clean(row.get("Run"))
            alias_to_runs[alias].append(run)
            description = clean(row.get("Description"))
            token = f"voucher_alias:{alias}"
            row["Description"] = f"{description} | {token}" if description else token
            row["derived_voucher_alias"] = alias
        else:
            row["derived_voucher_alias"] = ""
        enriched.append(row)

    duplicated = {
        alias: sorted(set(runs))
        for alias, runs in alias_to_runs.items()
        if len(set(runs)) != 1
    }
    if duplicated:
        raise ValueError(
            "BioSample isolate aliases are not unique: "
            + json.dumps(duplicated, sort_keys=True)
        )
    alias_index = {
        alias: next(iter(set(runs))) for alias, runs in alias_to_runs.items()
    }
    return enriched, alias_index


def normalize_morph_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, dict[str, str]]:
    """Map the direct Figure 1 schema onto the core reconciliation schema."""
    output: dict[str, dict[str, str]] = {}
    for source in rows:
        voucher = clean(source.get("voucher"))
        if not voucher:
            continue
        label = clean(
            source.get("published_figure_label")
            or source.get("direct_figure_label")
        ).upper()
        if label and label not in {"W", "BP"}:
            raise ValueError(f"Unexpected Figure 1 morph label for {voucher}: {label}")
        row = {key: clean(value) for key, value in source.items()}
        row["published_figure_label"] = label
        if label == "W":
            row["flower_colour_state"] = clean(
                row.get("flower_colour_state") or "white"
            )
            row["binary_colour_code"] = "W"
        elif label == "BP":
            row["flower_colour_state"] = clean(
                row.get("flower_colour_state") or "bluish-purple"
            )
            row["binary_colour_code"] = "C"
        output[voucher] = row
    return output


def reconcile_complete(
    supplement_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
    morph_rows: Sequence[Mapping[str, str]],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
]:
    enriched, alias_index = enrich_runinfo_with_voucher_aliases(
        supplement_rows, runinfo_rows
    )
    morph_index = normalize_morph_rows(morph_rows)
    matches, candidates = core.reconcile(supplement_rows, enriched, morph_index)
    summary = core.build_summary(matches, candidates, enriched)
    summary.update(
        {
            "complete_runinfo_rows": len(enriched),
            "derived_unique_voucher_aliases": len(alias_index),
            "figure1_morph_rows_loaded": len(morph_index),
            "derived_voucher_alias_to_run": dict(sorted(alias_index.items())),
            "reconciliation_provenance": (
                "Exact embedded SRR accessions plus exact supplement vouchers "
                "derived from official numeric BioSample isolate fields."
            ),
        }
    )
    return matches, candidates, summary


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    core.write_csv(path, rows, fields)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supplement", type=Path, default=DEFAULT_SUPPLEMENT)
    parser.add_argument("--runinfo", type=Path, required=True)
    parser.add_argument("--morphs", type=Path, default=DEFAULT_MORPHS)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    supplement = read_csv(args.supplement)
    runinfo = read_csv(args.runinfo)
    morphs = read_csv(args.morphs)
    if not supplement:
        raise SystemExit(f"No supplement rows in {args.supplement}")
    if not runinfo:
        raise SystemExit(f"No complete runinfo rows in {args.runinfo}")
    if not morphs:
        raise SystemExit(f"No Figure 1 morph rows in {args.morphs}")

    matches, candidates, summary = reconcile_complete(
        supplement, runinfo, morphs
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.outdir / "chang2026_sample_run_reconciliation.csv",
        matches,
        core.MATCH_FIELDS,
    )
    write_csv(
        args.outdir / "chang2026_run_candidates.csv",
        candidates,
        core.CANDIDATE_FIELDS,
    )
    takaoense = [
        row for row in matches if "takaoense" in clean(row.get("taxon")).casefold()
    ]
    write_csv(
        args.outdir / "chang2026_takaoense_sra_manifest.csv",
        takaoense,
        core.MATCH_FIELDS,
    )
    (args.outdir / "chang2026_ncbi_reconciliation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.outdir / "chang2026_ncbi_reconciliation_summary.csv",
        (
            {
                "metric": key,
                "value": json.dumps(value, ensure_ascii=False)
                if isinstance(value, (dict, list))
                else value,
            }
            for key, value in summary.items()
        ),
        core.SUMMARY_FIELDS,
    )

    confidence = Counter(clean(row.get("match_confidence")) for row in matches)
    print(f"supplement_sample_rows={len(matches)}")
    print(f"complete_runinfo_rows={summary['complete_runinfo_rows']}")
    print(f"derived_unique_voucher_aliases={summary['derived_unique_voucher_aliases']}")
    print(f"verified_or_probable_rows={summary['verified_or_probable_rows']}")
    print(f"unique_matched_runs={summary['unique_matched_runs']}")
    print(f"takaoense_verified_or_probable_rows={summary['takaoense_verified_or_probable_rows']}")
    print("confidence_counts=" + json.dumps(dict(sorted(confidence.items()))))
    for row in takaoense:
        print(
            "TAKAOENSE "
            f"{row['code']} {row['voucher']} {row['published_figure_label']} "
            f"{row['matched_run']} {row['match_status']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
