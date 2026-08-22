from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

FIELDS = [
    "orientation_experiment_id",
    "individual_id",
    "population_id",
    "capitulum_id",
    "matched_capitulum_id",
    "randomization_block",
    "randomization_seed",
    "randomization_method",
    "assignment",
    "assignment_datetime",
    "phenological_stage_at_assignment",
    "natural_orientation_deg",
    "target_orientation_deg",
    "achieved_orientation_deg",
    "sham_manipulation",
    "attachment_method",
    "early_bout_required",
    "later_bout_required",
    "wetting_event_followup_required",
    "antagonist_followup_required",
    "final_fitness_required",
    "treatment_integrity",
    "attrition_reason",
    "notes",
]


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def read_eligible(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "orientation_experiment_id",
        "individual_id",
        "population_id",
        "capitulum_id",
        "phenological_stage",
        "natural_orientation_deg",
        "eligible",
    }
    missing = required - set(rows[0].keys() if rows else [])
    if rows and missing:
        raise RuntimeError(f"Missing eligible-head columns: {sorted(missing)}")
    seen = set()
    kept = []
    for row in rows:
        cid = row["capitulum_id"].strip()
        if not cid:
            continue
        if cid in seen:
            raise RuntimeError(f"Duplicate capitulum_id in eligible-head table: {cid}")
        seen.add(cid)
        if row["eligible"].strip().lower() in {"1", "true", "yes", "y"}:
            kept.append(row)
    return kept


def randomize(rows: list[dict[str, str]], seed: int) -> tuple[list[dict[str, str]], dict]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row["orientation_experiment_id"],
            row["population_id"],
            row["individual_id"],
            row["phenological_stage"],
        )
        grouped[key].append(row)

    output = []
    unpaired = []
    block_count = 0
    for key in sorted(grouped):
        exp, population, individual, stage = key
        heads = sorted(grouped[key], key=lambda r: (as_float(r["natural_orientation_deg"]), r["capitulum_id"]))
        if len(heads) % 2:
            unpaired.append(heads[-1]["capitulum_id"])
            heads = heads[:-1]
        for pair_index in range(0, len(heads), 2):
            pair = heads[pair_index : pair_index + 2]
            block_count += 1
            active_index = rng.randrange(2)
            block = f"{exp}:{population}:{individual}:{stage}:pair{pair_index // 2 + 1}"
            for idx, row in enumerate(pair):
                assignment = "reoriented" if idx == active_index else "sham"
                mate = pair[1 - idx]["capitulum_id"]
                output.append(
                    {
                        "orientation_experiment_id": exp,
                        "individual_id": individual,
                        "population_id": population,
                        "capitulum_id": row["capitulum_id"],
                        "matched_capitulum_id": mate,
                        "randomization_block": block,
                        "randomization_seed": str(seed),
                        "randomization_method": "within_individual_stage_adjacent_natural_angle_pair_then_coinflip",
                        "assignment": assignment,
                        "assignment_datetime": "",
                        "phenological_stage_at_assignment": stage,
                        "natural_orientation_deg": row["natural_orientation_deg"],
                        "target_orientation_deg": "",
                        "achieved_orientation_deg": "",
                        "sham_manipulation": "0" if assignment == "reoriented" else "1",
                        "attachment_method": "",
                        "early_bout_required": "1",
                        "later_bout_required": "1",
                        "wetting_event_followup_required": "conditional_on_wetting_event",
                        "antagonist_followup_required": "1",
                        "final_fitness_required": "1",
                        "treatment_integrity": "",
                        "attrition_reason": "",
                        "notes": "generated from preregistered eligible-head table",
                    }
                )

    summary = {
        "version": "v1",
        "seed": seed,
        "eligible_head_count": len(rows),
        "assigned_head_count": len(output),
        "randomization_block_count": block_count,
        "unpaired_head_count": len(unpaired),
        "unpaired_capitulum_ids": sorted(unpaired),
        "method": "match within experiment/population/individual/phenological-stage by adjacent baseline natural orientation, then randomize sham versus reoriented within each pair",
        "claim_boundary": "This script randomizes treatment assignment only. It does not choose a biologically optimal target angle and does not replace treatment-integrity recording in the field.",
    }
    return output, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    rows = read_eligible(args.input)
    assigned, summary = randomize(rows, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(assigned)
    summary_path = args.output.with_suffix(args.output.suffix + ".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
