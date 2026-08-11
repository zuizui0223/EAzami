#!/usr/bin/env python3
"""Compare two Chang 2026 Read2Tree marker-profile topology screens.

The static May-2026 OMA profile and the independent Browser-export profile are
scientific sensitivities, not technical replicates. This comparator therefore
keeps three questions separate:

1. did each profile pass the focal-monophyly gate at a support threshold?
2. when scored, did it prefer the displayed candidate-regain topology or a
   corrected nearest loss-only alternative?
3. is the conclusion stable across support thresholds as well as marker sets?

A profile that is unresolved/not-scored is never counted as agreement with a
decisive profile. Direct candidate-regain versus loss-only disagreement is
reported as a marker-profile conflict and triggers the de-novo gene-tree path.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_THRESHOLDS = ("0", "50", "70", "90")
DECISIVE = frozenset(("candidate_regain", "loss_only"))
OUTPUT_FIELDS = (
    "support_threshold",
    "profile_a_analysis_status",
    "profile_a_classification",
    "profile_a_call",
    "profile_b_analysis_status",
    "profile_b_classification",
    "profile_b_call",
    "agreement_class",
    "interpretation",
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


def validate_details(
    path: Path,
    expected_thresholds: Sequence[str] = EXPECTED_THRESHOLDS,
) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    required = {"support_threshold", "analysis_status", "classification"}
    if not rows:
        raise ValueError(f"{path}: no Read2Tree detail rows")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    by_threshold: dict[str, dict[str, str]] = {}
    for row in rows:
        threshold = clean(row["support_threshold"])
        if threshold in by_threshold:
            raise ValueError(f"{path}: duplicate threshold {threshold}")
        by_threshold[threshold] = row
    if tuple(sorted(by_threshold, key=float)) != tuple(
        sorted(expected_thresholds, key=float)
    ):
        raise ValueError(
            f"{path}: expected thresholds {tuple(expected_thresholds)}, "
            f"observed {tuple(sorted(by_threshold, key=float))}"
        )
    return by_threshold


def normalized_call(row: Mapping[str, str]) -> str:
    status = clean(row.get("analysis_status"))
    classification = clean(row.get("classification"))
    if status != "scored_focal_monophyletic":
        return "not_scored"
    mapping = {
        "published_best": "candidate_regain",
        "loss_only_best": "loss_only",
        "tie_published_loss_only": "unresolved",
        "unresolved_all_hypotheses_tie": "unresolved",
        "not_scored": "not_scored",
    }
    if classification not in mapping:
        raise ValueError(
            f"Unknown scored Read2Tree classification {classification!r}"
        )
    return mapping[classification]


def compare_calls(left: str, right: str) -> tuple[str, str]:
    if {left, right} == set(DECISIVE):
        return (
            "direct_conflict",
            "One marker profile prefers candidate regain and the other prefers a loss-only history.",
        )
    if left == right == "candidate_regain":
        return (
            "concordant_candidate_regain",
            "Both marker profiles rank the displayed candidate-regain history best.",
        )
    if left == right == "loss_only":
        return (
            "concordant_loss_only",
            "Both marker profiles rank a corrected nearest loss-only history best.",
        )
    if left == right == "unresolved":
        return (
            "concordant_unresolved",
            "Both marker profiles pass the focal gate but do not distinguish candidate regain from loss-only alternatives.",
        )
    if left == right == "not_scored":
        return (
            "concordant_not_scored",
            "Neither marker profile provides a score at this threshold because a focal-monophyly gate is not satisfied.",
        )
    if (left in DECISIVE and right in {"unresolved", "not_scored"}) or (
        right in DECISIVE and left in {"unresolved", "not_scored"}
    ):
        return (
            "one_profile_decisive",
            "Only one marker profile is decisive at this threshold; this is not counted as marker-profile concordance.",
        )
    return (
        "nondecisive_mismatch",
        "The two profiles differ only among unresolved/not-scored states.",
    )


def comparison_rows(
    left: Mapping[str, Mapping[str, str]],
    right: Mapping[str, Mapping[str, str]],
    thresholds: Sequence[str] = EXPECTED_THRESHOLDS,
) -> list[dict[str, str]]:
    output = []
    for threshold in thresholds:
        a = left[threshold]
        b = right[threshold]
        a_call = normalized_call(a)
        b_call = normalized_call(b)
        agreement, interpretation = compare_calls(a_call, b_call)
        output.append(
            {
                "support_threshold": threshold,
                "profile_a_analysis_status": a["analysis_status"],
                "profile_a_classification": a["classification"],
                "profile_a_call": a_call,
                "profile_b_analysis_status": b["analysis_status"],
                "profile_b_classification": b["classification"],
                "profile_b_call": b_call,
                "agreement_class": agreement,
                "interpretation": interpretation,
            }
        )
    return output


def overall_summary(
    rows: Sequence[Mapping[str, str]],
    *,
    profile_a: str,
    profile_b: str,
) -> dict[str, object]:
    agreements = [clean(row["agreement_class"]) for row in rows]
    direct_conflicts = agreements.count("direct_conflict")
    partial = sum(
        agreement in {"one_profile_decisive", "nondecisive_mismatch"}
        for agreement in agreements
    )
    concordant_decisive = [
        clean(row["profile_a_call"])
        for row in rows
        if clean(row["agreement_class"])
        in {"concordant_candidate_regain", "concordant_loss_only"}
    ]
    decisive_set = set(concordant_decisive)

    if direct_conflicts:
        overall = "marker_profile_conflict"
        action = (
            "Do not select a preferred biological history. Audit marker overlap, mapping completeness and per-marker support, then prioritize de-novo gene trees/network analyses."
        )
    elif decisive_set == {"candidate_regain", "loss_only"}:
        overall = "support_threshold_direction_change"
        action = (
            "Marker profiles agree with each other at decisive thresholds but the preferred history changes after support collapse; treat the fast screen as support-sensitive and proceed to gene-tree analyses."
        )
    elif partial:
        overall = "marker_profile_partial_disagreement"
        action = (
            "At least one threshold is decisive in only one profile or differs in resolvability; do not call marker-profile concordance. Proceed to mapping/missingness diagnostics and de-novo gene trees."
        )
    elif decisive_set == {"candidate_regain"}:
        if len(concordant_decisive) == len(rows):
            overall = "concordant_candidate_regain_across_thresholds"
        else:
            overall = "support_sensitive_concordant_candidate_regain"
        action = (
            "Candidate-regain topology is marker-profile concordant where the screen is decisive. Continue to independent de-novo gene trees and reticulation tests before any evolutionary regain claim."
        )
    elif decisive_set == {"loss_only"}:
        if len(concordant_decisive) == len(rows):
            overall = "concordant_loss_only_across_thresholds"
        else:
            overall = "support_sensitive_concordant_loss_only"
        action = (
            "Loss-only topology is marker-profile concordant where decisive. Treat the displayed regain topology as weakened and use de-novo gene trees/network tests to resolve the conflict."
        )
    else:
        overall = "concordant_nondecisive"
        action = (
            "Neither profile yields a decisive common history. Continue to the de-novo gene-tree/network workflow without forcing a regain/loss classification."
        )

    return {
        "analysis": "Chang 2026 Read2Tree marker-profile comparison",
        "profile_a": profile_a,
        "profile_b": profile_b,
        "support_thresholds": [clean(row["support_threshold"]) for row in rows],
        "direct_conflict_threshold_count": direct_conflicts,
        "partial_disagreement_threshold_count": partial,
        "concordant_candidate_regain_threshold_count": agreements.count(
            "concordant_candidate_regain"
        ),
        "concordant_loss_only_threshold_count": agreements.count(
            "concordant_loss_only"
        ),
        "concordant_unresolved_threshold_count": agreements.count(
            "concordant_unresolved"
        ),
        "concordant_not_scored_threshold_count": agreements.count(
            "concordant_not_scored"
        ),
        "overall_classification": overall,
        "next_action": action,
        "claim_limit": (
            "Concordance across marker profiles reduces one source of reference-marker sensitivity only. It does not establish a species tree, exclude introgression/ILS, or demonstrate functional anthocyanin reactivation."
        ),
    }


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-a-details", type=Path, required=True)
    parser.add_argument("--profile-b-details", type=Path, required=True)
    parser.add_argument("--profile-a-name", default="oma_static_broadconservation400_may2026_v1")
    parser.add_argument("--profile-b-name", default="oma_browser_export400_may2026_v1")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    left = validate_details(args.profile_a_details)
    right = validate_details(args.profile_b_details)
    rows = comparison_rows(left, right)
    summary = overall_summary(
        rows, profile_a=args.profile_a_name, profile_b=args.profile_b_name
    )
    write_csv(args.output, rows)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"overall_classification={summary['overall_classification']}")
    print(f"direct_conflicts={summary['direct_conflict_threshold_count']}")
    print(
        "concordant_candidate_regain_thresholds="
        f"{summary['concordant_candidate_regain_threshold_count']}"
    )
    print(
        "concordant_loss_only_thresholds="
        f"{summary['concordant_loss_only_threshold_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
