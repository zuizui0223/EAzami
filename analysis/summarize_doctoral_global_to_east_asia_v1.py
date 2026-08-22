from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/doctoral_global_to_east_asia_hypothesis_map_v1.csv"
OUTPUT = ROOT / "data/evidence/doctoral_global_to_east_asia_summary_v1.json"

REQUIRED_IDS = [
    "G0", "G1", "G2",
    "M1", "M2", "M3", "M4", "M5",
    "D1", "D2", "D3", "O1",
    "E0", "E1", "C1", "C2", "C3", "O2", "R1",
]


def load_rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = load_rows()
    ids = [r["hypothesis_id"] for r in rows]
    if ids != REQUIRED_IDS:
        raise RuntimeError(f"Unexpected hypothesis order/coverage: {ids}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate hypothesis IDs")
    if not all(r["decisive_next_data"].strip() for r in rows):
        raise RuntimeError("Every row must state decisive next data or explicitly state none")
    if not all(r["claim_boundary"].strip() for r in rows):
        raise RuntimeError("Every row must carry a claim boundary")

    by_id = {r["hypothesis_id"]: r for r in rows}

    # Repository boundary guard: global Azami rows are premises/observational only.
    for hid in ("G0", "G1", "G2"):
        if not by_id[hid]["current_status"].startswith("resolved_"):
            raise RuntimeError(f"{hid} must remain an Azami premise/observational result")
        if "Azami" not in by_id[hid]["claim_boundary"]:
            raise RuntimeError(f"{hid} must explicitly remain in the Azami claim boundary")

    # Evolutionary-history guard: do not silently promote live transitions to conclusions.
    expected_unresolved = {
        "E1": "unresolved_central_hypothesis",
        "C1": "live_repeated_state_hypothesis",
        "C2": "unresolved_direction",
        "C3": "mechanistic_candidate",
        "O2": "unresolved_repeated_evolution",
        "R1": "unresolved_high_value",
    }
    for hid, status in expected_unresolved.items():
        if by_id[hid]["current_status"] != status:
            raise RuntimeError(f"{hid} must remain {status}")

    if by_id["D3"]["current_status"] != "weakened":
        raise RuntimeError("Generic stickiness-defence hypothesis must remain weakened")
    if by_id["M3"]["current_status"] != "resolved_general_pressure":
        raise RuntimeError("Antagonist fecundity pressure should remain the narrow resolved meta result")

    scale_counts = Counter(r["scale"] for r in rows)
    status_counts = Counter(r["current_status"] for r in rows)
    module_to_ids: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        module_to_ids[r["module"]].append(r["hypothesis_id"])

    summary = {
        "version": "v1",
        "architecture": [
            "Azami global observational phenotype/environment landscape",
            "quantitative mechanism meta-analysis and structured synthesis",
            "East Asian/Japanese rapid-radiation evolutionary-history zoom",
            "repeated-state and parallel-evolution tests",
            "focal causal trait-to-interaction/protection-to-fitness validation",
        ],
        "hypothesis_count": len(rows),
        "scale_counts": dict(sorted(scale_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "module_to_hypotheses": dict(sorted(module_to_ids.items())),
        "resolved_or_working_general": ["G0", "G1", "G2", "M1", "M2", "M3", "M4", "M5", "D1", "O1", "E0"],
        "weakened": ["D3"],
        "mechanistic_candidates_requiring_focal_validation": ["D2", "C3"],
        "evolutionary_history_not_yet_identified": ["E1", "C1", "C2", "O2", "R1"],
        "doctoral_empirical_gates": {
            "Aim1_history": "same-individual phenotype + nuclear ancestry + plastid + cytotype, plus accepted branch-length East Asian tree for independent transition mapping",
            "Aim2_function": "orientation first; W/coloured where flowering overlaps; display and validated spine/phyllary effects through effective pollination/antagonism to filled achenes",
            "Aim3_colour_reversibility": "at least two independent W/C transitions with coding/regulatory haplotype + matched floral RNA + pigment + calibrated colour",
        },
        "central_working_thesis": "Rapid East Asian/Japanese Cirsium diversification may have been accelerated by reusable capitulum modules that can be redeployed across local selection mosaics before deep genome-wide lineage sorting; this remains a hypothesis until ancestry-resolved repeated transitions and trait-to-fitness paths are demonstrated.",
        "adaptive_radiation_boundary": "Use rapid radiation as a premise. Do not call the radiation adaptive until a focal capitulum trait is causally linked through interaction/protection to reproductive fitness.",
        "generic_meta_stop_rule": "Do not restart broad heterogeneous interaction meta-analysis unless a prespecified reopening condition in the doctoral meta-resolution gate is met. New literature work should target transition history or a missing homologous effect size, not accumulate unrelated studies.",
    }
    OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
