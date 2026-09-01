#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data/evidence/chapter2_colour_rsds_focal_concordance_result_v1.json"
CSV_PATH = ROOT / "data/evidence/chapter2_colour_rsds_focal_system_contrasts_v1.csv"

x = json.loads(JSON_PATH.read_text(encoding="utf-8"))
assert x["contract_version"] == "chapter2_colour_rsds_focal_concordance_result_v1"
assert x["source_workflow_run_id"] == 33464866918
assert x["rsds_source"]["coverage"] == 1.0
assert x["azami_reference"]["among_taxon_beta_std"] < 0
assert x["chapter_summary"]["classification"] == "partial_current_rsds_chroma_directional_concordance"
assert x["chapter_summary"]["primary_concordant_systems"] == 1
assert x["chapter_summary"]["spatial_cell_concordant_systems"] == 1
assert x["chapter_summary"]["locality_robust_two_system_direction"] is False

aren = x["systems"]["ARENICOLA_BREVICAULE_IRUMTIENSE"]
tw = x["systems"]["TAIWAN_KAWAKAMII_TATAKAENSE"]
assert aren["observation_level"]["delta_rsds_white_minus_coloured_raw"] > 0
assert aren["observation_level"]["delta_chroma_white_minus_coloured"] < 0
assert aren["observation_level"]["azami_direction_concordant"] is True
assert aren["spatial_0_05_degree_cell_sensitivity"]["azami_direction_concordant"] is True
assert aren["spatial_0_05_degree_cell_sensitivity"]["delta_rsds_bootstrap_95_raw"][0] > 0

assert tw["observation_level"]["delta_rsds_white_minus_coloured_raw"] < 0
assert tw["observation_level"]["delta_chroma_white_minus_coloured"] < 0
assert tw["observation_level"]["azami_direction_concordant"] is False
assert tw["spatial_0_05_degree_cell_sensitivity"]["azami_direction_concordant"] is False
assert tw["spatial_0_05_degree_cell_sensitivity"]["delta_rsds_bootstrap_95_raw"][1] < 0

pooled = x["chapter_summary"]["pooled_within_taxon_secondary"]
assert pooled["beta_std"] < 0
assert pooled["permutation_p_expected_negative"] == 0.0361
assert pooled["permutation_p_two_sided"] == 0.1141

with CSV_PATH.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 2
assert {r["system_id"] for r in rows} == {
    "ARENICOLA_BREVICAULE_IRUMTIENSE",
    "TAIWAN_KAWAKAMII_TATAKAENSE",
}
assert sum(r["primary_azami_direction_concordant"].lower() == "true" for r in rows) == 1

boundary = " ".join(x["claim_boundary"]).lower()
for forbidden in ("historical", "selection", "adaptation"):
    assert forbidden in boundary

print(json.dumps({
    "status": "ok",
    "classification": x["chapter_summary"]["classification"],
    "primary_concordant_systems": 1,
    "cell_concordant_systems": 1,
    "pooled_within_beta_std": pooled["beta_std"],
    "pooled_within_expected_negative_p": pooled["permutation_p_expected_negative"],
    "interpretive_ceiling": "scale- and lineage-dependent present-state correspondence; historical driver unresolved",
}, indent=2))
