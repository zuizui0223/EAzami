#!/usr/bin/env python3
from __future__ import annotations
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/evidence/chapter2_public_event_process_registry_v1.csv"
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
    if r["event_class"] == "dated_trait_event":
        assert r["young_ma"] != "" and r["old_ma"] != ""
        assert float(r["young_ma"]) <= float(r["old_ma"])
        assert "forced" in r["trait_transition_status"]

assert by["ORI_TAIWAN_TRIO_STEM"]["public_data_role"] == "primary_local_T3_candidate"
assert by["COL_BREVICAULE_TERMINAL"]["public_data_role"] == "dated_history_only_cause_not_evaluable"
assert by["COL_KAWAKAMII_TERMINAL"]["public_data_role"] == "dated_history_only_cause_not_evaluable"
assert by["SINOCIRSIUM_JAPAN_TAIWAN_SPLIT"]["trait_transition_status"] == "species_tip_transition_not_identifiable"
assert by["DIPSACOLEPIS_SECONDARY_JUMP"]["event_class"] == "biogeographic_process"
assert by["LINEARE_EASTASIA_JAPAN_EXPANSION"]["event_class"] == "biogeographic_process"

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "events.json"
    subprocess.run([sys.executable, str(BUILDER), "--out", str(out)], check=True, stdout=subprocess.DEVNULL)
    x = json.loads(out.read_text())
    ev = {e["event_id"]: e for e in x["event_registry"]}
    assert ev["ORI_TAIWAN_TRIO_STEM"]["combined_admissible_window_ma"] == [0.47,0.79]
    assert ev["COL_BREVICAULE_TERMINAL"]["combined_admissible_window_ma"] == [0.0,0.93]
    assert ev["COL_KAWAKAMII_TERMINAL"]["combined_admissible_window_ma"] == [0.0,0.47]
    assert all(e["forced_across_all_topologies_and_min_histories"] for e in ev.values())

print(json.dumps({"status":"ok","n_registry_rows":len(rows),"dated_event_ids":[r["event_id"] for r in rows if r["event_class"]=="dated_trait_event"]}, indent=2))
