#!/usr/bin/env python3
"""Re-summarize dated Chapter 2 differentiation events without a present-day prior.

The primary orientation source artifact contains both raw PALEO-PGEM branch
trajectories and legacy present-state comparison fields.  This analysis reads only
`delta` and `background_z` from each chronology x paleolocation scenario.  It does
not read or reproduce direction-agreement, cosine, or any Chapter-1 effect vector.

It also converts the public trait-event recovery audit into an identifiability
ledger so that dated sister contrasts and dated range events cannot be mistaken for
resolved trait-transition ages.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

VARIABLES = ("BIO1", "BIO4", "BIO12", "BIO15")
REGIONS = ("taiwan", "ryukyu_corridor", "southern_japan", "east_asia_core_corridor")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--orientation-source", type=Path, required=True)
    p.add_argument("--event-audit", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-variable-csv", type=Path, required=True)
    p.add_argument("--out-event-ledger", type=Path, required=True)
    return p.parse_args()


def qsummary(values: list[float]) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    if len(x) == 0 or not np.all(np.isfinite(x)):
        raise ValueError("Non-finite or empty scenario values")
    return {
        "min": float(np.min(x)),
        "q05": float(np.quantile(x, 0.05)),
        "median": float(np.median(x)),
        "q95": float(np.quantile(x, 0.95)),
        "max": float(np.max(x)),
    }


def direction_from_regions(per_region: dict[str, dict[str, Any]], metric: str) -> str:
    lows = [float(per_region[r][metric]["q05"]) for r in REGIONS]
    highs = [float(per_region[r][metric]["q95"]) for r in REGIONS]
    if all(v > 0 for v in lows):
        return "robust_increase" if metric == "delta" else "consistently_above_matched_windows"
    if all(v < 0 for v in highs):
        return "robust_decrease" if metric == "delta" else "consistently_below_matched_windows"
    return "direction_unresolved" if metric == "delta" else "matched_window_position_unresolved"


def audit_role(row: dict[str, str]) -> str:
    rid = row.get("record_id", "")
    hist = row.get("history_class", "")
    usable = row.get("usable_as_transition", "")
    if rid == "ORI_CORE_NIPPONO_STEM":
        return "calendar_paleolocation_environment_evaluable_transition_envelope"
    if usable.startswith("yes_conditional") or usable == "yes_branch_envelope_only":
        return "conditional_transition_branch_envelope_historical_driver_not_yet_evaluable"
    if hist == "dated_sister_phenotype_contrast":
        return "dated_sister_contrast_not_reconstructed_transition"
    if hist == "range_process_trait_age_unlinked":
        return "dated_range_process_trait_transition_age_unlinked"
    if hist == "lineage_polymorphic_nonidentifiable":
        return "polymorphic_trait_transition_not_identifiable"
    if hist == "biogeographic_process":
        return "dated_distribution_process_not_trait_transition"
    return "not_evaluable_as_dated_trait_transition"


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    source = json.loads(args.orientation_source.read_text(encoding="utf-8"))
    rows = source.get("scenario_rows")
    if not isinstance(rows, list) or len(rows) != 376:
        raise AssertionError(f"Expected 376 orientation scenario rows, got {0 if rows is None else len(rows)}")
    if int(source.get("chronology", {}).get("n_valid_age_pairs", -1)) != 94:
        raise AssertionError("Orientation source chronology is not the frozen 94-pair envelope")

    by_region = {r: [x for x in rows if x.get("region") == r] for r in REGIONS}
    if any(len(by_region[r]) != 94 for r in REGIONS):
        raise AssertionError({r: len(by_region[r]) for r in REGIONS})

    variable_rows: list[dict[str, Any]] = []
    variable_summary: dict[str, Any] = {}
    for var in VARIABLES:
        per_region: dict[str, Any] = {}
        for region in REGIONS:
            rr = by_region[region]
            delta = [float(x["delta"][var]) for x in rr]
            z = [float(x["background_z"][var]) for x in rr]
            dsum = qsummary(delta)
            zsum = qsummary(z)
            central = min(
                rr,
                key=lambda x: abs(float(x["young_ma"]) - 0.74) + abs(float(x["old_ma"]) - 0.79),
            )
            rec = {
                "region": region,
                "delta": dsum,
                "fraction_delta_positive": float(np.mean(np.asarray(delta) > 0)),
                "fraction_delta_negative": float(np.mean(np.asarray(delta) < 0)),
                "background_z": zsum,
                "fraction_background_z_positive": float(np.mean(np.asarray(z) > 0)),
                "fraction_background_z_negative": float(np.mean(np.asarray(z) < 0)),
                "central_pair_delta": float(central["delta"][var]),
                "central_pair_background_z": float(central["background_z"][var]),
            }
            per_region[region] = rec
            variable_rows.append(
                {
                    "variable": var,
                    "region": region,
                    "delta_min": dsum["min"],
                    "delta_q05": dsum["q05"],
                    "delta_median": dsum["median"],
                    "delta_q95": dsum["q95"],
                    "delta_max": dsum["max"],
                    "fraction_delta_positive": rec["fraction_delta_positive"],
                    "fraction_delta_negative": rec["fraction_delta_negative"],
                    "background_z_q05": zsum["q05"],
                    "background_z_median": zsum["median"],
                    "background_z_q95": zsum["q95"],
                    "central_pair_delta": rec["central_pair_delta"],
                    "central_pair_background_z": rec["central_pair_background_z"],
                }
            )
        direction = direction_from_regions(per_region, "delta")
        background_class = direction_from_regions(per_region, "background_z")
        pooled_delta = [float(x["delta"][var]) for x in rows]
        pooled_z = [float(x["background_z"][var]) for x in rows]
        variable_summary[var] = {
            "per_region": per_region,
            "cross_region_direction": direction,
            "cross_region_matched_window_position": background_class,
            "pooled_scenario_delta": qsummary(pooled_delta),
            "pooled_fraction_delta_positive": float(np.mean(np.asarray(pooled_delta) > 0)),
            "pooled_fraction_delta_negative": float(np.mean(np.asarray(pooled_delta) < 0)),
            "pooled_scenario_background_z": qsummary(pooled_z),
        }

    robust_vars = [v for v, x in variable_summary.items() if x["cross_region_direction"] != "direction_unresolved"]
    unusual_vars = [
        v for v, x in variable_summary.items()
        if x["cross_region_matched_window_position"] != "matched_window_position_unresolved"
    ]

    with args.event_audit.open(encoding="utf-8-sig", newline="") as fh:
        audit = list(csv.DictReader(fh))
    ledger = []
    for r in audit:
        ledger.append(
            {
                "event_id": r.get("record_id", ""),
                "trait_module": r.get("trait_module", ""),
                "focal_taxa": r.get("focal_taxa", ""),
                "calendar_constraint": r.get("calendar_constraint", ""),
                "calendar_lower_ma": r.get("calendar_lower_ma", ""),
                "calendar_upper_ma": r.get("calendar_upper_ma", ""),
                "phenotype_resolution": r.get("phenotype_resolution", ""),
                "history_class": r.get("history_class", ""),
                "usable_as_transition_source": r.get("usable_as_transition", ""),
                "historical_environment_analysis_role": audit_role(r),
                "claim_boundary": r.get("claim_boundary", ""),
            }
        )

    orientation_events = [x for x in ledger if x["trait_module"] == "orientation" and x["historical_environment_analysis_role"] == "calendar_paleolocation_environment_evaluable_transition_envelope"]
    recurrence_status = (
        "not_evaluable_single_dated_transition_event"
        if len(orientation_events) < int(contract["repeated_trigger_rule"]["minimum_independent_events"])
        else "requires_same_direction_event_comparison"
    )

    result = {
        "contract_version": contract["contract_version"],
        "status_date": contract["status_date"],
        "analysis_scope": "historical differentiation only; no present-day effect vector or cross-chapter comparison is used",
        "orientation_event": {
            "event_id": "ORI_CORE_NIPPONO_STEM",
            "transition": "erect_or_upward -> nodding_or_downward",
            "chronology_scenarios": 94,
            "paleolocation_scenarios": list(REGIONS),
            "n_region_by_chronology_scenarios": 376,
            "variable_summary": variable_summary,
            "variables_with_robust_cross_region_delta_direction": robust_vars,
            "variables_with_consistent_matched_window_position": unusual_vars,
            "event_direction_class": (
                "one_or_more_tested_climate_directions_survive_full_scenario_envelope"
                if robust_vars else
                "no_tested_climate_direction_survives_full_chronology_paleolocation_envelope"
            ),
            "repeated_trigger_status": recurrence_status,
            "interpretation": "A branch-associated climate direction can be described only when it survives the frozen chronology x paleolocation envelope. Repeated triggering requires at least two independently bounded homologous transitions."
        },
        "event_ledger": ledger,
        "identifiability_summary": {
            "calendar_paleolocation_environment_evaluable_transition_envelopes": int(sum(x["historical_environment_analysis_role"] == "calendar_paleolocation_environment_evaluable_transition_envelope" for x in ledger)),
            "conditional_transition_branch_envelopes": int(sum(x["historical_environment_analysis_role"] == "conditional_transition_branch_envelope_historical_driver_not_yet_evaluable" for x in ledger)),
            "dated_sister_contrasts_not_transitions": int(sum(x["historical_environment_analysis_role"] == "dated_sister_contrast_not_reconstructed_transition" for x in ledger)),
            "dated_range_process_trait_age_unlinked": int(sum(x["historical_environment_analysis_role"] == "dated_range_process_trait_transition_age_unlinked" for x in ledger)),
        },
        "claim_boundary": contract["claim_boundary"],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_variable_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_event_ledger.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(variable_rows).to_csv(args.out_variable_csv, index=False)
    pd.DataFrame(ledger).to_csv(args.out_event_ledger, index=False)
    print(json.dumps({
        "event_direction_class": result["orientation_event"]["event_direction_class"],
        "robust_variables": robust_vars,
        "matched_window_variables": unusual_vars,
        "repeated_trigger_status": recurrence_status,
        "identifiability_summary": result["identifiability_summary"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
