#!/usr/bin/env python3
"""Run the single frozen JPN_29-excluded branch-change provenance sensitivity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import run_japan38_all_continuous_history_v1 as hist
import run_japan38_branch_change_reconstruction_null_v1 as locked

EXCLUSION = "JPN_29"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--bridge", type=Path, required=True)
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--original-null", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--null-out", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=9999)
    p.add_argument("--seed", type=int, default=20260827)
    return p.parse_args()


def validate_original_null(path: Path) -> dict:
    x = json.loads(path.read_text(encoding="utf-8"))
    if x.get("contract_version") != "japan38_branch_change_reconstruction_null_v1":
        raise ValueError("wrong original-null contract")
    if x.get("decision") != "FAIL" or abs(float(x.get("one_sided_reconstruction_null_p")) - 0.3504) > 1e-12:
        raise ValueError("provenance sensitivity requires the frozen original FAIL at P=0.3504")
    if EXCLUSION not in x.get("concept_ids", []):
        raise ValueError("JPN_29 is absent from the original common panel")
    return x


def main() -> int:
    a = parse_args()
    if a.permutations != 9999 or a.seed != 20260827:
        raise ValueError("provenance sensitivity fixes 9999 permutations and seed 20260827")
    original = validate_original_null(a.original_null)
    bridge = hist.apply_concept_exclusions(hist.read_bridge(a.bridge), [EXCLUSION])
    cmap, allowed = hist.base.read_concept_map(a.concept_map)
    result, null = locked.compute_reconstruction_null(
        bridge,
        a.tree,
        cmap,
        allowed,
        threshold=2,
        permutations=a.permutations,
        seed=a.seed,
        expected_common_concepts=7,
        expected_branches=12,
    )
    expected_ids = sorted(set(original["concept_ids"]) - {EXCLUSION})
    if result["concept_ids"] != expected_ids:
        raise ValueError("provenance panel differs from the frozen original panel minus JPN_29")
    result.update(
        {
            "contract_version": "japan38_branch_change_provenance_sensitivity_v1",
            "status": "post_outcome_provenance_sensitivity_frozen",
            "excluded_concepts": [EXCLUSION],
            "source_original_null": str(a.original_null.as_posix()),
            "source_original_decision": original["decision"],
            "source_original_p": original["one_sided_reconstruction_null_p"],
            "analysis_role": "provenance_sensitivity_not_confirmatory_rescue",
            "claim_boundary": (
                "This one fixed rerun removes the identity-unresolved JPN_29 join. Report either "
                "direction, but no result can reinstate the coordinated-remodeling headline, "
                "replace the frozen eight-concept FAIL, or establish independence or mechanism."
            ),
        }
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    a.null_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {"permutation_index": range(a.permutations), "null_global_mean_rho": null}
    ).to_csv(a.null_out, index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
