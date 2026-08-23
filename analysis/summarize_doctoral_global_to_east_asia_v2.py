from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/doctoral_global_to_east_asia_evidence_ladder_v2.csv"
OUTPUT = ROOT / "data/evidence/doctoral_global_to_east_asia_summary_v2.json"

REQUIRED_IDS = [f"L{i}" for i in range(10)]
REQUIRED_COLUMNS = {
    "order_id", "scope", "module", "question_or_prior_hypothesis",
    "meta_or_literature_result", "meta_status", "azami_self_analysis",
    "eazami_self_analysis", "current_conclusion", "new_hypothesis_or_prediction",
    "existing_data_can_still_resolve", "doctoral_empirical_requirement",
    "doctoral_issue_gate", "claim_boundary",
}


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError("Evidence ladder has no header")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise RuntimeError(f"Evidence ladder missing columns: {sorted(missing)}")
        return [{k: str(v or "").strip() for k, v in row.items()} for row in reader]


def main() -> None:
    rows = read_rows()
    ids = [r["order_id"] for r in rows]
    if ids != REQUIRED_IDS:
        raise RuntimeError(f"Unexpected evidence-ladder order/coverage: {ids}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate evidence-ladder IDs")
    for row in rows:
        for key in REQUIRED_COLUMNS:
            if not row[key]:
                raise RuntimeError(f"{row['order_id']} missing {key}")

    by_id = {r["order_id"]: r for r in rows}

    # Repository boundary: Azami must remain observational, not causal/evolutionary.
    if "no genetic variance" not in by_id["L0"]["claim_boundary"].lower():
        raise RuntimeError("L0 lost the Azami observational boundary")
    if "azami is observational phenomics" not in by_id["L0"]["claim_boundary"].lower():
        raise RuntimeError("L0 must explicitly remain an Azami-only observational claim")

    # Meta-analysis decisions that must not drift.
    if by_id["L2"]["meta_status"] != "resolved_general_pressure":
        raise RuntimeError("Antagonist seed-output pressure must remain the narrow resolved meta result")
    if "RR=2.674" not in by_id["L2"]["meta_or_literature_result"]:
        raise RuntimeError("Antagonist pooled RR drifted")
    if by_id["L6"]["meta_status"] != "weakened_general_hypothesis":
        raise RuntimeError("Generic stickiness defence must remain weakened")
    if "selection mosaic" not in by_id["L1"]["current_conclusion"].lower():
        raise RuntimeError("Selection-mosaic conclusion was lost")

    # Current EAzami evolutionary results.
    orient = by_id["L3"]
    if "minimum of 5 orientation changes" not in orient["eazami_self_analysis"]:
        raise RuntimeError("Orientation repeated-state result drifted")
    if "parallel/convergent adaptation is not yet established" not in orient["claim_boundary"]:
        raise RuntimeError("Orientation overclaim guard was lost")

    colour = by_id["L4"]
    if "C=17/W=3" not in colour["eazami_self_analysis"]:
        raise RuntimeError("Current colour state gate drifted")
    if "regain" not in colour["claim_boundary"].lower():
        raise RuntimeError("Colour regain claim boundary was lost")

    radiation = by_id["L8"]
    if "adaptive radiation" not in radiation["claim_boundary"].lower():
        raise RuntimeError("Adaptive-radiation boundary was lost")
    if "common-lability" not in radiation["new_hypothesis_or_prediction"]:
        raise RuntimeError("Competing common-lability hypothesis was lost")

    scopes = Counter(r["scope"] for r in rows)
    meta_status = Counter(r["meta_status"] for r in rows)
    gate_to_ids: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        gate_to_ids[row["doctoral_issue_gate"]].append(row["order_id"])

    summary = {
        "version": "v2_evidence_ladder",
        "status_date": "2026-08-23",
        "architecture": [
            "Azami global observational phenomics: continuous within/among-taxon phenotype-environment structure",
            "EAzami quantitative literature/meta-analysis: test general ecological mechanism hypotheses",
            "EAzami East-Asian/Japanese rapid-radiation zoom: accepted nuclear history plus repeated-state tests",
            "Doctoral empirical programme: ancestry-resolved trait -> interaction/protection -> reproductive fitness",
            "Mechanistic flagship: repeated flower-colour transitions and regulatory/molecular reuse",
        ],
        "evidence_ladder_rows": len(rows),
        "scope_counts": dict(sorted(scopes.items())),
        "meta_status_counts": dict(sorted(meta_status.items())),
        "meta_conclusions": {
            "direct_climate_or_pollinator_single_axis": "insufficient/weakened as a universal explanation",
            "selection_mosaic": "working general support; focal agent dominance remains unknown",
            "reproductive_antagonist_pressure": "resolved narrow meta result: RR=2.674 (95% CI 2.388-2.993)",
            "reproductive_assurance_and_demographic_gating": "working support; focal population state remains unknown",
            "stickiness_general_defence": "weakened",
            "display_tradeoff": "working mechanistic support",
            "orientation_timing_protection": "mechanistic candidate",
            "phyllary_spine_defence": "mechanistic candidate requiring direct trait validation",
        },
        "self_analysis_resolutions": {
            "global": "Azami establishes large below-taxon visible variance and trait-specific environmental structure, strongest for orientation and visible colour, without causal interpretation.",
            "east_asia_tree": "Accepted 153-locus branch-length framework with explicit six-topology uncertainty set.",
            "orientation": "All six AU-nonrejected topologies require at least five orientation-state changes; direction, root state and adaptation remain unresolved.",
            "colour": "Current exact colour panel is C=17/W=3; tree gate is ready but the fixed-white breadth/rate-identifiability gate blocks loss-versus-regain inference.",
        },
        "new_central_hypothesis": "A young reticulating East-Asian Cirsium radiation diversified rapidly because semi-independent capitulum modules were repeatedly redeployed across local selection mosaics; the competing explanation is a single shared common-lability axis.",
        "multiscale_prediction": "Population-level selection mosaics and ancestry-linked within-species variation should connect to repeated among-lineage states; within- and among-species patterns must be modelled jointly rather than treating species as fixed endpoints.",
        "doctoral_empirical_frontier": {
            "Aim1_history": "same-individual phenotype + nuclear ancestry + plastid + cytotype; validate repeated states at voucher/population level and identify independent transitions",
            "Aim2_function": "orientation first, then W/coloured function and display; phyllary/spine only after direct validation; close trait -> interaction/protection -> filled-achene paths",
            "Aim3_colour_reexpression": "after >=2 independent W/C transitions, link ancestry -> coding/regulatory haplotype -> floral RNA -> pigment -> calibrated colour",
            "adaptive_radiation_gate": "do not use adaptive radiation until at least one repeated focal trait is causally linked through ecological mechanism to reproductive fitness",
        },
        "issue_gate_to_rows": dict(sorted(gate_to_ids.items())),
        "generic_meta_stop_rule": "Generic heterogeneous literature accumulation is complete at the present decision ceiling. Reopen only for a prespecified homologous estimand or a study capable of changing a focal mechanism/sampling decision.",
    }
    OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
