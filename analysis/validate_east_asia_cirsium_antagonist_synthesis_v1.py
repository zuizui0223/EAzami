#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--context", required=True, type=Path)
    p.add_argument("--synthesis", required=True, type=Path)
    args = p.parse_args()

    with args.context.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 2:
        raise ValueError(f"expected two East-Asian evidence rows, found {len(rows)}")
    by_id = {r["evidence_id"]: r for r in rows}
    if set(by_id) != {"EAA001", "EAA002"}:
        raise ValueError(f"unexpected evidence IDs: {sorted(by_id)}")

    synthesis = json.loads(args.synthesis.read_text(encoding="utf-8"))
    focal = synthesis["direct_east_asia_findings"]["focal_taxon_antagonist_channel"]
    assert focal["taxon"] == "Cirsium brevicaule"
    assert focal["flower_heads"] == 837
    assert focal["effective_samples"] == 3
    assert focal["positive_samples"] == 3
    assert focal["mean_attack_rate"] == 26.1

    regime = synthesis["direct_east_asia_findings"]["japan_regime_structure"]
    assert regime["cirsium_taxa"] == 35
    assert regime["core_flower_head_insects_on_cirsium"] == 6

    display = synthesis["direct_east_asia_findings"]["japan_display_cost"]
    assert display["taxon"] == "Cirsium purpuratum"
    assert display["populations"] == 2
    assert display["nikko_heads_infested_percent"] == 90.8
    assert display["nikko_seed_predation_probability_percent"] == 25.3
    assert display["nikko_seed_damage_range_percent"] == [7.9, 51.5]
    assert display["nikko_predator_number_vs_seed_damage_r2"] == 0.48
    assert display["nikko_saturating_floret_vs_seed_damage_r2"] == 0.44

    anchor = synthesis["existing_experimental_magnitude_anchor"]
    assert anchor["pooled_reduced_vs_ambient_herbivory_seed_output_RR"] == 2.674
    assert anchor["ci95"] == [2.388, 2.993]
    assert anchor["transport_status"] == "magnitude_not_transportable_to_east_asia_as_measured_effect"
    assert synthesis["classification"] == "east_asian_antagonist_pathway_and_regime_supported_effect_magnitude_not_transferred"

    print(json.dumps({
        "classification": synthesis["classification"],
        "focal_brevicaule_attack_rate": focal["mean_attack_rate"],
        "focal_positive_samples": f"{focal['positive_samples']}/{focal['effective_samples']}",
        "japanese_cirsium_taxa": regime["cirsium_taxa"],
        "purpuratum_heads_infested_percent": display["nikko_heads_infested_percent"],
        "experimental_RR_anchor": anchor["pooled_reduced_vs_ambient_herbivory_seed_output_RR"],
        "transport_status": anchor["transport_status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
