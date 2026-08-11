#!/usr/bin/env python3
"""Validate the source-backed Cirsium flower-colour atlas and rate-fit gate.

The original atlas schema tracked colour evidence but did not distinguish a real
flower-colour observation from a phylogenetically valid transition-rate tip.
This validator keeps those layers separate.

Key rules:

* fine colour states are retained alongside an explicit binary code;
* polymorphic taxa remain ``P`` and unresolved records remain ``U`` rather than
  being silently forced to white/coloured;
* sample/population/voucher records may be excellent evidence but cannot enter a
  species-tree rate fit merely because they have W/C labels;
* ``rate_fit_eligible=yes`` requires reviewed, source-located, taxon-level W/C
  evidence and a declared phylogeny-tip mapping candidate;
* readiness for an actual asymmetric transition-rate fit is reported separately
  from row validity.  The v0.1 thresholds are conservative engineering gates,
  not a claim of statistical sufficiency.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

REQUIRED_COLUMNS = {
    "record_id",
    "accepted_taxon",
    "source_taxon_name",
    "country",
    "observation_unit",
    "observation_id",
    "evidence_type",
    "evidence_source",
    "evidence_id",
    "source_url",
    "source_locator",
    "assessable",
    "colour_state",
    "binary_colour_code",
    "binary_collapse_rule",
    "phylogeny_context",
    "phylogeny_tip_candidate",
    "rate_fit_eligible",
    "rate_fit_exclusion_reason",
    "evidence_status",
    "review_status",
}

ALLOWED_COLOURS = {
    "white",
    "near_white",
    "pale_pink",
    "pink",
    "purple",
    "blue_purple",
    "polymorphic",
    "unknown",
}
EXPECTED_BINARY = {
    "white": "W",
    "near_white": "W",
    "pale_pink": "C",
    "pink": "C",
    "purple": "C",
    "blue_purple": "C",
    "polymorphic": "P",
    "unknown": "U",
}
ALLOWED_BINARY = set(EXPECTED_BINARY.values())
ALLOWED_ASSESSABLE = {"yes", "no", "unknown"}
ALLOWED_REVIEW = {"pending", "reviewed", "rejected"}
ALLOWED_OBSERVATION_UNITS = {"taxon", "population", "sample", "voucher"}
ALLOWED_BOOLEAN = {"yes", "no"}
DIRECT_RATE_EVIDENCE = {
    "direct_taxon_text",
    "official_database_text_direct",
    "voucher_flower_direct",
}

DEFAULT_MIN_RATE_TIPS = 20
DEFAULT_MIN_PER_STATE = 5
DEFAULT_MIN_PHYLO_CONTEXTS = 3


def clean(value: object) -> str:
    return str(value or "").strip()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise ValueError(f"file not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("missing header")
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
        return list(reader.fieldnames), rows


def validate_coordinates(row: Mapping[str, str], line_no: int, problems: list[str]) -> None:
    lat = clean(row.get("latitude"))
    lon = clean(row.get("longitude"))
    if bool(lat) != bool(lon):
        problems.append(f"line {line_no}: latitude/longitude must be supplied together")
        return
    if not lat:
        return
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except ValueError:
        problems.append(f"line {line_no}: non-numeric coordinates")
        return
    if not -90 <= lat_f <= 90:
        problems.append(f"line {line_no}: latitude out of range")
    if not -180 <= lon_f <= 180:
        problems.append(f"line {line_no}: longitude out of range")


def validate_rows(fieldnames: Sequence[str], rows: Sequence[Mapping[str, str]]) -> None:
    missing = REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if not rows:
        raise ValueError("atlas contains no records")

    problems: list[str] = []
    seen_ids: set[str] = set()
    seen_evidence_keys: set[tuple[str, str, str]] = set()

    for line_no, row in enumerate(rows, start=2):
        rid = clean(row.get("record_id"))
        if not rid:
            problems.append(f"line {line_no}: empty record_id")
        elif rid in seen_ids:
            problems.append(f"line {line_no}: duplicate record_id {rid}")
        seen_ids.add(rid)

        taxon = clean(row.get("accepted_taxon"))
        if not taxon:
            problems.append(f"line {line_no}: empty accepted_taxon")

        unit = clean(row.get("observation_unit")).lower()
        if unit not in ALLOWED_OBSERVATION_UNITS:
            problems.append(
                f"line {line_no}: invalid observation_unit {unit!r}; "
                f"allowed={sorted(ALLOWED_OBSERVATION_UNITS)}"
            )
        if not clean(row.get("observation_id")):
            problems.append(f"line {line_no}: missing observation_id")

        colour = clean(row.get("colour_state"))
        if colour not in ALLOWED_COLOURS:
            problems.append(
                f"line {line_no}: invalid colour_state {colour!r}; allowed={sorted(ALLOWED_COLOURS)}"
            )
        binary = clean(row.get("binary_colour_code")).upper()
        if binary not in ALLOWED_BINARY:
            problems.append(
                f"line {line_no}: invalid binary_colour_code {binary!r}; allowed={sorted(ALLOWED_BINARY)}"
            )
        if colour in EXPECTED_BINARY and binary != EXPECTED_BINARY[colour]:
            problems.append(
                f"line {line_no}: colour_state={colour} requires binary_colour_code={EXPECTED_BINARY[colour]}, observed {binary}"
            )
        if not clean(row.get("binary_collapse_rule")):
            problems.append(f"line {line_no}: missing binary_collapse_rule")

        assessable = clean(row.get("assessable")).lower()
        if assessable not in ALLOWED_ASSESSABLE:
            problems.append(
                f"line {line_no}: invalid assessable {assessable!r}; allowed={sorted(ALLOWED_ASSESSABLE)}"
            )
        review = clean(row.get("review_status")).lower()
        if review not in ALLOWED_REVIEW:
            problems.append(
                f"line {line_no}: invalid review_status {review!r}; allowed={sorted(ALLOWED_REVIEW)}"
            )
        tip = clean(row.get("phylogeny_tip_candidate")).lower()
        rate = clean(row.get("rate_fit_eligible")).lower()
        if tip not in ALLOWED_BOOLEAN:
            problems.append(f"line {line_no}: phylogeny_tip_candidate must be yes/no")
        if rate not in ALLOWED_BOOLEAN:
            problems.append(f"line {line_no}: rate_fit_eligible must be yes/no")

        if review == "reviewed":
            if not clean(row.get("source_url")):
                problems.append(f"line {line_no}: reviewed record lacks source_url")
            if not clean(row.get("source_locator")):
                problems.append(f"line {line_no}: reviewed record lacks source_locator")
            if not clean(row.get("evidence_status")):
                problems.append(f"line {line_no}: reviewed record lacks evidence_status")

        if assessable == "no" and binary not in {"U", "P"}:
            problems.append(f"line {line_no}: assessable=no cannot carry resolved binary W/C")
        if binary == "P" and colour != "polymorphic":
            problems.append(f"line {line_no}: binary P requires colour_state=polymorphic")
        if binary == "U" and colour != "unknown":
            problems.append(f"line {line_no}: binary U requires colour_state=unknown")

        exclusion = clean(row.get("rate_fit_exclusion_reason"))
        if rate == "yes":
            requirements = {
                "observation_unit=taxon": unit == "taxon",
                "assessable=yes": assessable == "yes",
                "review_status=reviewed": review == "reviewed",
                "binary W/C": binary in {"W", "C"},
                "phylogeny_tip_candidate=yes": tip == "yes",
                "direct evidence status": clean(row.get("evidence_status")) in DIRECT_RATE_EVIDENCE,
                "source_url present": bool(clean(row.get("source_url"))),
                "source_locator present": bool(clean(row.get("source_locator"))),
                "phylogeny_context present": bool(clean(row.get("phylogeny_context"))),
                "empty exclusion reason": not exclusion,
            }
            failed = [name for name, ok in requirements.items() if not ok]
            if failed:
                problems.append(
                    f"line {line_no}: rate_fit_eligible=yes violates {failed}"
                )
        else:
            if not exclusion:
                problems.append(f"line {line_no}: rate_fit_eligible=no requires exclusion reason")

        evidence_key = (
            clean(row.get("evidence_source")),
            clean(row.get("evidence_id")),
            clean(row.get("observation_id")),
        )
        if all(evidence_key):
            if evidence_key in seen_evidence_keys:
                problems.append(
                    f"line {line_no}: duplicate evidence_source/evidence_id/observation_id key {evidence_key}"
                )
            seen_evidence_keys.add(evidence_key)

        validate_coordinates(row, line_no, problems)

    if problems:
        raise ValueError("validation failed with " + str(len(problems)) + " problem(s):\n" + "\n".join(problems))


def readiness_summary(
    rows: Sequence[Mapping[str, str]],
    *,
    min_rate_tips: int = DEFAULT_MIN_RATE_TIPS,
    min_per_state: int = DEFAULT_MIN_PER_STATE,
    min_phylo_contexts: int = DEFAULT_MIN_PHYLO_CONTEXTS,
) -> dict[str, object]:
    if min(min_rate_tips, min_per_state, min_phylo_contexts) < 1:
        raise ValueError("readiness thresholds must be >=1")

    reviewed = [row for row in rows if clean(row.get("review_status")).lower() == "reviewed"]
    eligible = [row for row in rows if clean(row.get("rate_fit_eligible")).lower() == "yes"]
    eligible_taxa = sorted({clean(row.get("accepted_taxon")) for row in eligible})
    eligible_states = Counter(clean(row.get("binary_colour_code")).upper() for row in eligible)
    eligible_contexts = sorted({clean(row.get("phylogeny_context")) for row in eligible if clean(row.get("phylogeny_context"))})

    conditions = {
        "minimum_taxon_tips": len(eligible_taxa) >= min_rate_tips,
        "minimum_white_tips": eligible_states.get("W", 0) >= min_per_state,
        "minimum_coloured_tips": eligible_states.get("C", 0) >= min_per_state,
        "minimum_phylogeny_contexts": len(eligible_contexts) >= min_phylo_contexts,
        "all_eligible_are_taxon_level": all(clean(row.get("observation_unit")).lower() == "taxon" for row in eligible),
        "no_polymorphic_or_unknown_eligible": all(clean(row.get("binary_colour_code")).upper() in {"C", "W"} for row in eligible),
    }
    blockers = [name for name, passed in conditions.items() if not passed]

    return {
        "contract_version": "cirsium_flower_colour_atlas_v0_1",
        "record_count": len(rows),
        "review_status_counts": dict(sorted(Counter(clean(row.get("review_status")).lower() for row in rows).items())),
        "observation_unit_counts": dict(sorted(Counter(clean(row.get("observation_unit")).lower() for row in rows).items())),
        "fine_colour_counts": dict(sorted(Counter(clean(row.get("colour_state")) for row in rows).items())),
        "binary_colour_counts": dict(sorted(Counter(clean(row.get("binary_colour_code")).upper() for row in rows).items())),
        "reviewed_record_count": len(reviewed),
        "rate_fit_eligible_record_count": len(eligible),
        "rate_fit_eligible_unique_taxa": len(eligible_taxa),
        "rate_fit_eligible_taxa": eligible_taxa,
        "rate_fit_eligible_state_counts": dict(sorted(eligible_states.items())),
        "rate_fit_eligible_phylogeny_contexts": eligible_contexts,
        "readiness_thresholds": {
            "min_rate_fit_taxon_tips": min_rate_tips,
            "min_per_binary_state": min_per_state,
            "min_phylogeny_contexts": min_phylo_contexts,
        },
        "readiness_conditions": conditions,
        "transition_rate_fit_ready": not blockers,
        "readiness_blockers": blockers,
        "threshold_note": (
            "These thresholds are a conservative project gate against fitting asymmetric rates to a tiny focal clade; "
            "they are not a statistical guarantee of identifiability or adequate phylogenetic coverage."
        ),
        "claim_limit": (
            "Atlas validation establishes provenance/coding eligibility only. Even when the engineering gate passes, "
            "ER/ARD model adequacy, phylogenetic uncertainty, polymorphic-state treatment and sampling bias must be assessed before interpreting q(C->W) or q(W->C)."
        ),
    }


def validate(path: Path, *, summary_path: Path | None = None) -> dict[str, object]:
    fieldnames, rows = read_rows(path)
    validate_rows(fieldnames, rows)
    summary = readiness_summary(rows)
    if summary_path is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas", type=Path)
    parser.add_argument("--summary", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate(args.atlas, summary_path=args.summary)
    except ValueError as exc:
        raise SystemExit("ERROR: " + str(exc)) from exc
    print(f"OK: {summary['record_count']} records validated in {args.atlas}")
    print(f"rate_fit_eligible_unique_taxa={summary['rate_fit_eligible_unique_taxa']}")
    print("rate_fit_eligible_state_counts=" + json.dumps(summary["rate_fit_eligible_state_counts"], sort_keys=True))
    print(f"transition_rate_fit_ready={str(summary['transition_rate_fit_ready']).lower()}")
    print("readiness_blockers=" + "|".join(summary["readiness_blockers"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
