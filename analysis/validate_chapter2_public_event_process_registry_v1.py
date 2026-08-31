#!/usr/bin/env python3
from __future__ import annotations
import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/evidence/chapter2_public_event_process_registry_v1.csv"
SUMMARY_PATH = ROOT / "data/evidence/chapter2_public_explanatory_depth_summary_v1.json"
ANTHESIS_PATH = ROOT / "data/evidence/chapter2_taiwan_orientation_anthesis_precipitation_v1.json"
BUILDER = ROOT / "analysis/build_chapter2_public_dated_event_registry_v1.py"

required = {
    "event_id","trait","event_class","trait_transition_status","young_ma","old_ma",
    "distribution_process_context","environment_history_status","azami_bridge",
    "public_data_role","source_refs","claim_boundary"
}
with CSV_PATH.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
assert rows and required.issubset(rows[0])
ids = [r["event_id"] for r in rows]
assert len(ids) == len(set(ids))
by = {r["event_id"]: r for r in rows}
for r in rows:
    if r["event_class"] in {"dated_trait_event", "restricted_taxon_set_dated_sensitivity", "crossstudy_chronology_refinement"}:
        assert r["young_ma"] != "" and r["old_ma"] != ""
        assert float(r["young_ma"]) <= float(r["old_ma"])

assert by["ORI_TAIWAN_TRIO_STEM"]["public_data_role"] == "restricted_tree_environment_sensitivity"
assert "not_robust" in by["ORI_TAIWAN_TRIO_STEM"]["trait_transition_status"]
assert by["ORI_CORE_NIPPONO_CROSSSTUDY_STEM"]["event_class"] == "crossstudy_chronology_refinement"
assert float(by["ORI_CORE_NIPPONO_CROSSSTUDY_STEM"]["young_ma"]) == 0.74
assert float(by["ORI_CORE_NIPPONO_CROSSSTUDY_STEM"]["old_ma"]) == 0.79
assert "location_unresolved" in by["ORI_CORE_NIPPONO_CROSSSTUDY_STEM"]["public_data_role"]
assert by["COL_BREVICAULE_TERMINAL"]["public_data_role"] == "dated_history_only_cause_not_evaluable"
assert by["COL_KAWAKAMII_TERMINAL"]["public_data_role"] == "dated_history_only_cause_not_evaluable"
assert by["SINOCIRSIUM_JAPAN_TAIWAN_SPLIT"]["trait_transition_status"] == "species_tip_transition_not_identifiable"
assert by["DIPSACOLEPIS_SECONDARY_JUMP"]["event_class"] == "biogeographic_process"
assert by["LINEARE_EASTASIA_JAPAN_EXPANSION"]["event_class"] == "biogeographic_process"

# The six-taxon builder remains a valid conditional sensitivity, but its
# orientation placement must not be promoted after adding the public Japanese core.
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "events.json"
    subprocess.run([sys.executable, str(BUILDER), "--out", str(out)], check=True, stdout=subprocess.DEVNULL)
    x = json.loads(out.read_text())
    ev = {e["event_id"]: e for e in x["event_registry"]}
    assert ev["ORI_TAIWAN_TRIO_STEM"]["combined_admissible_window_ma"] == [0.47,0.79]
    assert ev["COL_BREVICAULE_TERMINAL"]["combined_admissible_window_ma"] == [0.0,0.93]
    assert ev["COL_KAWAKAMII_TERMINAL"]["combined_admissible_window_ma"] == [0.0,0.47]
    assert all(e["forced_across_all_topologies_and_min_histories"] for e in ev.values())

summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
assert summary["contract_version"] == "chapter2_public_explanatory_depth_summary_v1"
assert summary["evolutionary_depth"]["orientation"]["minimum_changes"] == "4-6 across Japan38 UFBoot"
restricted = summary["restricted_taiwan_orientation_sensitivity"]
assert restricted["window_ma"] == [0.47, 0.79]
assert math.isclose(restricted["state_trajectory"]["cosine_similarity"], 0.059383853324142886)
assert math.isclose(restricted["state_trajectory"]["null_percentile"], 0.5180851063829788)
assert restricted["directional_results"]["BIO12"]["young_minus_old"] > 0
assert restricted["directional_results"]["BIO15"]["young_minus_old"] < 0
assert restricted["directional_results"]["BIO1"]["young_minus_old"] > 0
assert "not evaluable" in summary["process_model_status"]["ST1_persistent_driver"]

anthesis = json.loads(ANTHESIS_PATH.read_text(encoding="utf-8"))
assert anthesis["contract_version"] == "chapter2_taiwan_orientation_anthesis_precipitation_v1"
assert anthesis["source_workflow_run"] == 33358152401
assert anthesis["phenology_basis"]["shared_intersection"] == "Sep-Oct"
assert anthesis["phenology_basis"]["union_envelope"] == "Aug-Nov"
for key in ("shared_sep_oct", "envelope_aug_nov"):
    result = anthesis[key]
    assert result["directional_change_young_minus_old"] > 0
    assert result["directional_background"]["signed_percentile"] < 0.95
    assert result["cellwise_endpoint_delta"]["fraction_positive"] == 1.0
    assert result["regional_spatial_iqr_over_temporal_sd"] > 10
assert anthesis["decision"]["extremeness"].startswith("neither")

print(json.dumps({
    "status":"ok",
    "n_registry_rows":len(rows),
    "orientation_primary_chronology_status":"crossstudy central estimates 0.79-0.74 Ma; joint age uncertainty and paleolocation unresolved",
    "restricted_tree_orientation_window":[0.47,0.79],
    "dated_colour_event_ids":["COL_BREVICAULE_TERMINAL","COL_KAWAKAMII_TERMINAL"],
    "anthesis_direction":"positive_all_cells_but_not_exceptional",
    "state_trajectory_cosine":restricted["state_trajectory"]["cosine_similarity"]
}, indent=2))
