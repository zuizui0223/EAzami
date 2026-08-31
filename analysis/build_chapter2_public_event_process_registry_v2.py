#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/evidence/chapter2_public_event_process_registry_v2.csv"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    with args.input.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("event-process registry is empty")

    for row in rows:
        for key in ("young_ma", "old_ma"):
            row[key] = float(row[key]) if row[key] != "" else None
        if row["young_ma"] is not None and row["old_ma"] is not None:
            row["window_width_ma"] = row["old_ma"] - row["young_ma"]
        else:
            row["window_width_ma"] = None

    result = {
        "contract_version": "chapter2_public_event_process_registry_v2",
        "n_rows": len(rows),
        "trait_event_rows": [r for r in rows if "trait_event" in r["event_class"]],
        "restricted_sensitivity_rows": [r for r in rows if r["event_class"] == "restricted_descendant_lineage_sensitivity"],
        "distribution_process_rows": [r for r in rows if r["event_class"] in {"biogeographic_process", "palaeodemographic_process"}],
        "event_registry": rows,
        "orientation_origin_event_id": "ORI_CORE_NIPPO_STEM",
        "orientation_restricted_sensitivity_id": "ORI_TAIWAN_DESCENDANT_WINDOW",
        "claim_boundary": "Event ages retain their source-specific interval type. Cross-study marginal envelopes are not converted into joint posterior probabilities, and range processes are not trait transitions or selective agents."
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("contract_version", "n_rows", "orientation_origin_event_id", "orientation_restricted_sensitivity_id")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
