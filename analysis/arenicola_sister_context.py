#!/usr/bin/env python3
"""Legacy summary wrapper for the Arenicola sister-context parsimony screen.

The full analysis now lives in ``arenicola_colour_history_sensitivity.py``.
This wrapper preserves the historical CSV path while correcting an important
claim-boundary issue: the C. brevicaule / C. irumtiense pair alone does not
polarize flower-colour change. Equal-cost parsimony prefers a coloured Arenicola
MRCA only after the published Nipponocirsium sister context is included.
"""

from __future__ import annotations

import csv
from pathlib import Path

import arenicola_colour_history_sensitivity as sensitivity


def main() -> int:
    states = sensitivity.load_tip_states(sensitivity.DEFAULT_EVIDENCE)
    rows = sensitivity.scenario_rows(states)

    pair = next(
        row for row in rows
        if row["analysis_context"] == "Arenicola_pair_only"
        and row["constraint"] == "unconstrained"
    )
    primary = {
        str(row["constraint"]): row
        for row in rows
        if row["analysis_context"] == "Arenicola_plus_Nipponocirsium"
        and row["topology_variant"] == "published_pengii_basal"
    }

    output = {
        "analysis": "Arenicola_plus_Nipponocirsium_published_context",
        "minimum_transitions": primary["unconstrained"]["minimum_changes"],
        "fitch_root_states": primary["unconstrained"]["optimal_root_states"],
        "interpretation": (
            "The brevicaule-irumtiense pair alone is directionally ambiguous under equal-cost "
            f"parsimony (Arenicola MRCA={pair['optimal_arenicola_mrca_states']}; one change either "
            "as C->W loss or W->C regain). After adding the published coloured-rich "
            "Nipponocirsium sister context, the unique minimum has a coloured deep root and "
            "coloured Arenicola MRCA with two total changes: C->W on C. brevicaule and C->W "
            "on C. kawakamii. Forcing a white Arenicola MRCA costs three changes (+1), so "
            "irumtiense regain is less parsimonious but remains an explicit competing hypothesis. "
            "Historical treatment as C. brevicaule var. irumtiense is not an ancestor-descendant "
            "constraint. No branch-length Mk probability or molecular reactivation claim is made."
        ),
    }

    out = Path("analysis/arenicola_sister_context.csv")
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output))
        writer.writeheader()
        writer.writerow(output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
