#!/usr/bin/env python3
"""Validate the minimal fixed-white target-capture panel.

This is an execution-design validator, not evidence that sequencing has occurred.
The two A1 taxa are chosen because resolving both would add two fixed-white
species-tree tips to the current atlas gate (W=3 -> W=5).  The validator also
prevents the taxonomically conflicted Moreyra ``C. henryi`` label from being
silently treated as the revised white Hubei species.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

EXPECTED_A1 = {"Cirsium boninense", "Cirsium wulongense"}
EXPECTED_ROWS = 5
EXPECTED_GAIN = "+1_fixed_W_taxon_after_credible_nuclear_placement"
REQUIRED = {
    "rank", "decision_tier", "candidate_id", "taxon", "region",
    "white_state_class", "white_evidence_status", "nuclear_status",
    "preferred_target_set", "fallback_modality", "minimum_individuals",
    "ideal_individuals", "voucher_required", "flower_colour_link_required",
    "identity_guard", "existing_comparator", "rate_gate_gain",
    "execution_precondition", "stop_rule", "claim_limit",
}


def clean(value: object) -> str:
    return str(value or "").strip()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("missing header")
        rows = [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]
        return list(reader.fieldnames), rows


def validate(path: Path) -> dict[str, object]:
    fields, rows = read_rows(path)
    missing = REQUIRED - set(fields)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"expected {EXPECTED_ROWS} candidate rows, observed {len(rows)}")

    ranks = [int(row["rank"]) for row in rows]
    if ranks != list(range(1, EXPECTED_ROWS + 1)):
        raise ValueError(f"ranks must be 1..{EXPECTED_ROWS} in order, observed {ranks}")
    if len({row["candidate_id"] for row in rows}) != len(rows):
        raise ValueError("candidate_id values must be unique")
    if len({row["taxon"] for row in rows}) != len(rows):
        raise ValueError("taxon values must be unique")

    a1 = [row for row in rows if row["decision_tier"] == "A1"]
    if {row["taxon"] for row in a1} != EXPECTED_A1 or len(a1) != 2:
        raise ValueError(f"A1 must be exactly {sorted(EXPECTED_A1)}")

    for row in rows:
        taxon = row["taxon"]
        if row["white_state_class"] != "fixed_W":
            raise ValueError(f"{taxon}: target-capture gate panel may contain only fixed_W candidates")
        if row["preferred_target_set"] != "Compositae1061":
            raise ValueError(f"{taxon}: preferred target set must remain Compositae1061 for direct Moreyra locus overlap")
        minimum = int(row["minimum_individuals"])
        ideal = int(row["ideal_individuals"])
        if minimum < 2 or ideal < minimum:
            raise ValueError(f"{taxon}: require >=2 individuals and ideal>=minimum")
        if row["voucher_required"] != "yes" or row["flower_colour_link_required"] != "yes":
            raise ValueError(f"{taxon}: every sequenced individual must retain voucher and colour linkage")
        if row["rate_gate_gain"] != EXPECTED_GAIN:
            raise ValueError(f"{taxon}: unexpected rate-gate gain coding")
        for key in ("identity_guard", "existing_comparator", "execution_precondition", "stop_rule", "claim_limit"):
            if not row[key]:
                raise ValueError(f"{taxon}: missing {key}")

    henryi = next(row for row in rows if row["taxon"] == "Cirsium henryi")
    guard = henryi["identity_guard"]
    required_henryi_tokens = ("western-Hubei", "SAMN44017857", "2464", "C. forrestii")
    if not all(token in guard for token in required_henryi_tokens):
        raise ValueError("C. henryi identity guard lost the Moreyra-voucher conflict")
    if "published_nuclear_label_conflicts" not in henryi["nuclear_status"]:
        raise ValueError("C. henryi must remain a nuclear-label conflict, not an existing white tip")

    sichuanense = next(row for row in rows if row["taxon"] == "Cirsium sichuanense")
    if "direct original-description colour evidence frozen" not in sichuanense["execution_precondition"]:
        raise ValueError("C. sichuanense requires direct original-description colour evidence before promotion")

    summary = {
        "panel_version": "fixed_white_target_capture_panel_v0_1",
        "candidate_count": len(rows),
        "a1_taxa": sorted(row["taxon"] for row in a1),
        "a1_fixed_white_tip_gain_if_both_resolved": 2,
        "current_fixed_white_gate": 3,
        "projected_fixed_white_gate_if_a1_both_resolved": 5,
        "preferred_target_set": "Compositae1061",
        "minimum_individuals_per_taxon": 2,
        "claim_limit": (
            "Passing this panel design only shows that the sampling contract is internally consistent. "
            "Even two successful new white tips merely clear the engineering W>=5 gate; asymmetric transition-rate "
            "inference still requires tree integration, topology/branch-length uncertainty, sampling-bias assessment, "
            "polymorphic-state treatment and model-adequacy checks."
        ),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", type=Path)
    args = parser.parse_args()
    summary = validate(args.panel)
    for key, value in summary.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
