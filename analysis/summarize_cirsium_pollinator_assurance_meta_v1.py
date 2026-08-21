#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/cirsium_pollinator_assurance_meta_v1.csv"
OUTPUT = ROOT / "data/evidence/cirsium_pollinator_assurance_meta_v1.json"


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    ids = [r["study_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("study_id values must be unique")

    dependence = Counter(r["pollinator_dependence"] for r in rows)
    limitation = Counter(r["pollen_limitation_open_conditions"] for r in rows)
    exact = sum(r["exact_numeric_recovered"] == "1" for r in rows)

    # Only PA01 and PA02 explicitly compare current open reproduction with pollen
    # supplementation while also quantifying reproductive assurance/dependence.
    dependence_vs_limitation_designs = [r for r in rows if r["study_id"] in {"PA01", "PA02"}]
    adequate_open_service = sum(
        r["pollen_limitation_open_conditions"] in {"mostly_absent", "absent"}
        for r in dependence_vs_limitation_designs
    )

    result = {
        "version": "v1",
        "independent_study_count": len(rows),
        "high_pollinator_dependence_studies": dependence.get("high", 0),
        "variable_dependence_studies": dependence.get("variable", 0),
        "exact_numeric_studies": exact,
        "dependence_vs_pollen_limitation_designs": len(dependence_vs_limitation_designs),
        "dependence_vs_limitation_with_no_general_open_pollen_deficit": adequate_open_service,
        "open_pollen_limitation_categories": dict(sorted(limitation.items())),
        "headline": (
            "Pollinator contribution to seed production is often large in Cirsium, but pollinator dependence "
            "is not equivalent to pollen limitation under current open conditions. Reproductive assurance varies "
            "with autonomous selfing, mating system, pollen-donor spacing, flowering synchrony and local density, "
            "so visitation alone is an insufficient proxy for fitness benefit."
        ),
        "pooling_status": (
            "No across-study pooled pollinator effect is authorized yet. Only one independent study currently "
            "has a fully recovered Cirsium supplement/open/bagged numeric contrast; other studies use exclusion "
            "failure, donor distance, autonomous-selfing indices or qualitative bagged/open results."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
