#!/usr/bin/env python3
"""Reconstruct the quantitative Cirsium palustre white-flower preference range.

The source cases are the six bee-type x population cases in Mogford's Fig. 24
that were reported as significant preferential pollination of the white morph
and for which both white morph availability and white visit shares can be
reconstructed. The resulting range is a soft mechanistic calibration only:
the cases are clustered, non-independent and conditioned on significance.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def load_cases(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 6:
        raise ValueError(f"expected 6 reconstructed white-preference cases, found {len(rows)}")
    return rows


def run(path: Path):
    rows = load_cases(path)
    ratios = []
    for row in rows:
        morph = float(row["white_morph_share"])
        visits = float(row["white_visit_share"])
        stored = float(row["white_selection_ratio"])
        ratio = visits / morph
        if not math.isclose(ratio, stored, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError(f"selection-ratio mismatch for {row['case_id']}: {ratio} != {stored}")
        if ratio <= 1.0:
            raise ValueError(f"white-preference case is not enriched: {row['case_id']}")
        ratios.append(ratio)

    geo = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    ordered = sorted(ratios)
    median = (ordered[2] + ordered[3]) / 2.0
    return {
        "contract_version": "cirsium_palustre_colour_preference_fig24_v1",
        "status_date": "2026-08-21",
        "n_significant_white_preference_cases": len(rows),
        "selection_ratio_definition": "white_visit_share / white_morph_share",
        "geometric_mean_selection_ratio": round(geo, 10),
        "median_selection_ratio": round(median, 10),
        "minimum_selection_ratio": round(min(ratios), 10),
        "maximum_selection_ratio": round(max(ratios), 10),
        "source_statement": "Mogford reports white preferential pollination in all six discriminating cases where white preference was testable; purple was discriminated against in nine of ten discriminating cases containing purple.",
        "decision": "use_as_soft_significance_conditioned_range_not_pooled_effect",
        "claim_boundary": "The six rows are bee-type x population observations from one study system and are selected because they showed significant white preference. The 1.15-1.61 range is a conditional mechanistic calibration, not an unbiased pooled effect or genus-wide estimate."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.cases)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
