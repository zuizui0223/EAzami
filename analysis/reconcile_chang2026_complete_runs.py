#!/usr/bin/env python3
"""Reconcile Chang 2026 supplement samples to the complete published run set.

This adapter preserves the conservative scoring rules in
``reconcile_chang2026_ncbi_runs.py`` while adding source-backed evidence that
its generic interface did not originally expose:

* numeric BioSample ``isolate`` values become ``ccy####`` voucher tokens only
  when that exact voucher exists in the supplement;
* heterogeneous supplement identifiers (SRR, SRX, or SAMN) are resolved against
  the matching runinfo field before scoring;
* the official SRA ``LibraryLayout`` is carried into the reconciled manifest;
  and
* Figure 1's ``direct_figure_label`` is normalized to the core morph schema.

Neither geography nor flower colour participates in run matching. The raw-read
count relation remains a reconciliation diagnostic; it is not used to infer
single- versus paired-end layout when official SRA layout metadata are present.
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
from recover_chang2026_published_runinfo import identifier_kind

DEFAULT_SUPPLEMENT = core.DEFAULT_SUPPLEMENT
DEFAULT_MORPHS = core.DEFAULT_MORPHS
DEFAULT_OUTDIR = Path(
    "data/evidence/generated/chang2026_complete_reconciliation"
)
COMPLETE_MATCH_FIELDS = core.MATCH_FIELDS + ("matched_library_layout",)
VALID_LIBRARY_LAYOUTS = {"PAIRED", "SINGLE"}


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


def identifier_field(kind: str) -> str:
    field = {
        "run": "Run",
        "experiment": "Experiment",
        "biosample": "BioSample",
    }.get(kind)
    if not field:
        raise ValueError(f"Unsupported embedded identifier kind: {kind!r}")
    return field


def choose_identifier_run(
    source: Mapping[str, str],
    candidates: Sequence[Mapping[str, str]],
) -> str:
    """Choose one run within an exact SRX/SAMN set using non-geographic evidence."""
    if len(candidates) == 1:
        return clean(candidates[0].get("Run"))
    ranked = sorted(
        (core.score_candidate(source, candidate) for candidate in candidates),
        key=lambda item: (-int(item["score"]), str(item["run"])),
    )
    status, confidence, note = core.classify_match(source, ranked)
    if confidence not in {"verified", "probable"}:
        raise ValueError(
            "Embedded identifier maps to multiple unresolved runs for "
            f"{clean(source.get('voucher'))}: {status}; {note}"
        )
    return clean(ranked[0]["run"])


def prepare_embedded_identifiers(
    supplement_rows: Sequence[Mapping[str, str]],
    runinfo_rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Resolve every exact SRR/SRX/SAMN identifier to one run for core scoring."""
    prepared: list[dict[str, str]] = []
    resolutions: list[dict[str, str]] = []
    for source in supplement_rows:
        row = {key: clean(value) for key, value in source.items()}
        original = clean(row.get("embedded_public_accession")).upper()
        if not original:
            prepared.append(row)
            resolutions.append(
                {
                    "original_identifier": "",
                    "identifier_kind": "",
                    "resolved_run": "",
                }
            )
            continue
        kind = identifier_kind(original)
        if not kind:
            raise ValueError(f"Unsupported supplement identifier: {original!r}")
        field = identifier_field(kind)
        candidates = [
            candidate
            for candidate in runinfo_rows
            if clean(candidate.get(field)).upper() == original
        ]
        if not candidates:
            raise ValueError(
                f"Embedded identifier {original} has no exact {field} row"
            )
        resolved_run = choose_identifier_run(row, candidates)
        if not resolved_run:
            raise ValueError(f"Embedded identifier {original} resolved to no run")
        row["embedded_public_accession"] = resolved_run
        prepared.append(row)
        resolutions.append(
            {
                "original_identifier": original,
                "identifier_kind": kind,
                "resolved_run": resolved_run,
            }
        )
    return prepared, resolutions


def restore_embedded_provenance(
    matches: Sequence[dict[str, object]],
    resolutions: Sequence[Mapping[str, str]],
) -> None:
    if len(matches) != len(resolutions):
        raise ValueError("Embedded-resolution ledger changed row count")
    for match, resolution in zip(matches, resolutions):
        original = clean(resolution.get("original_identifier"))
        if not original:
            continue
        kind = clean(resolution.get("identifier_kind"))
        resolved = clean(resolution.get("resolved_run"))
        if clean(match.get("matched_run")) != resolved:
            raise ValueError(
                f"Resolved run changed for {original}: "
                f"{match.get('matched_run')} != {resolved}"
            )
        match["embedded_public_accession"] = original
        if kind != "run":
            match["match_status"] = f"verified_exact_embedded_{kind}_accession"
            match["match_confidence"] = "verified"
            match["match_evidence"] = (
                f"exact_embedded_{kind}_accession|"
                + clean(match.get("match_evidence"))
            ).rstrip("|")
            match["review_note"] = (
                f"Supplement {kind} accession {original} resolves exactly to "
                f"official run {resolved}."
            )


def attach_official_library_layout(
    matches: Sequence[dict[str, object]],
    runinfo_rows: Sequence[Mapping[str, str]],
) -> Counter[str]:
    """Attach exact SRA LibraryLayout to every reconciled run."""
    by_run: dict[str, str] = {}
    for row in runinfo_rows:
        run = clean(row.get("Run"))
        if not run:
            continue
        layout = clean(row.get("LibraryLayout")).upper()
        if layout not in VALID_LIBRARY_LAYOUTS:
            raise ValueError(
                f"Official run {run} has unsupported LibraryLayout {layout!r}"
            )
        if run in by_run and by_run[run] != layout:
            raise ValueError(
                f"Official run {run} has conflicting LibraryLayout values: "
                f"{by_run[run]} != {layout}"
            )
        by_run[run] = layout

    counts: Counter[str] = Counter()
    for match in matches:
        run = clean(match.get("matched_run"))
        if not run:
            match["matched_library_layout"] = ""
            continue
        if run not in by_run:
            raise ValueError(f"No official LibraryLayout recovered for matched run {run}")
        layout = by_run[run]
        match["matched_library_layout"] = layout
        counts[layout] += 1
    return counts


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
    supplement_rows: Sequence[Mapping[str,str]],
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
    prepared, resolutions = prepare_embedded_identifiers(
        supplement_rows, enriched
    )
    morph_index = normalize_morph_rows(morph_rows)
    matches, candidates = core.reconcile(prepared, enriched, morph_index)
    restore_embedded_provenance(matches, resolutions)
    layout_counts = attach_official_library_layout(matches, enriched)
    summary = core.build_summary(matches, candidates, enriched)
    resolution_rows = [
        row for row in resolutions if clean(row.get("original_identifier"))
    ]
    resolution_type_counts = Counter(
        clean(row.get("identifier_kind")) for row in resolution_rows
    )
    summary.update(
        {
            "complete_runinfo_rows": len(enriched),
            "derived_unique_voucher_aliases": len(alias_index),
            "figure1_morph_rows_loaded": len(morph_index),
            "embedded_identifier_resolution_count": len(resolution_rows),
            "embedded_identifier_type_counts": dict(
                sorted(resolution_type_counts.items())
            ),
            "embedded_identifier_resolutions": resolution_rows,
            "official_library_layout_counts": dict(sorted(layout_counts.items())),
            "derived_voucher_alias_to_run": dict(sorted(alias_index.items())),
            "reconciliation_provenance": (
                "Exact supplement SRR/SRX/SAMN identifiers, exact vouchers "
                "derived from official numeric BioSample isolate fields, and "
                "official SRA LibraryLayout metadata."
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
        COMPLETE_MATCH_FIELDS,
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
        COMPLETE_MATCH_FIELDS,
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
    print(
        "embedded_identifier_resolution_count="
        f"{summary['embedded_identifier_resolution_count']}"
    )
    print(
        "official_library_layout_counts="
        + json.dumps(summary["official_library_layout_counts"], sort_keys=True)
    )
    print(f"verified_or_probable_rows={summary['verified_or_probable_rows']}")
    print(f"unique_matched_runs={summary['unique_matched_runs']}")
    print(
        "takaoense_verified_or_probable_rows="
        f"{summary['takaoense_verified_or_probable_rows']}"
    )
    print("confidence_counts=" + json.dumps(dict(sorted(confidence.items()))))
    for row in takaoense:
        print(
            "TAKAOENSE "
            f"{row['code']} {row['voucher']} {row['published_figure_label']} "
            f"{row['matched_run']} {row['matched_library_layout']} "
            f"{row['match_status']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
