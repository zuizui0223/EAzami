#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/evidence/chapter2_public_event_process_registry_v2.csv"
BUILDER = ROOT / "analysis/build_chapter2_public_event_process_registry_v2.py"

required = {
    "event_id", "trait", "event_class", "transition_identifiability",
    "young_ma", "old_ma", "chronology_type", "location_identifiability",
    "distribution_process_context", "environment_history_status", "azami_bridge",
    "public_data_role", "source_refs", "claim_boundary"
}
with CSV_PATH.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
assert rows and required.issubset(rows[0])
ids = [r["event_id"] for r in rows]
assert len(ids) == len(set(ids))
assert "ORI_TAIWAN_TRIO_STEM" not in ids
by = {r["event_id"]: r for r in rows}

for r in rows:
    if r["young_ma"] != "" or r["old_ma"] != "":
        assert r["young_ma"] != "" and r["old_ma"] != ""
        assert float(r["young_ma"]) <= float(r["old_ma"])

origin = by["ORI_CORE_NIPPO_STEM"]
restricted = by["ORI_TAIWAN_DESCENDANT_WINDOW"]
assert origin["public_data_role"] == "primary_origin_envelope_candidate"
assert origin["event_class"] == "crossstudy_dated_trait_event"
assert origin["chronology_type"] == "crossstudy_marginal_interval_envelope"
assert [float(origin["young_ma"]), float(origin["old_ma"])] == [0.60, 1.18]
assert restricted["event_class"] == "restricted_descendant_lineage_sensitivity"
assert restricted["public_data_role"] == "restricted_environment_sensitivity_not_origin"
assert [float(restricted["young_ma"]), float(restricted["old_ma"])] == [0.47, 0.79]
assert "not_unique_origin" in restricted["transition_identifiability"]

for eid in ("COL_BREVICAULE_TERMINAL", "COL_KAWAKAMII_TERMINAL"):
    assert by[eid]["public_data_role"] == "dated_history_only_cause_not_evaluable"
    assert "conditional" in by[eid]["transition_identifiability"]
for eid in ("JPN_DOMINANT_RADIATION_FOUNDER", "DIPSACOLEPIS_SECONDARY_JUMP", "LINEARE_EASTASIA_JAPAN_EXPANSION"):
    assert by[eid]["event_class"] == "biogeographic_process"
    assert "trait transition" in by[eid]["claim_boundary"].lower() or "transition time" in by[eid]["claim_boundary"].lower()

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "registry.json"
    subprocess.run([sys.executable, str(BUILDER), "--out", str(out)], check=True, stdout=subprocess.DEVNULL)
    x = json.loads(out.read_text(encoding="utf-8"))
    assert x["orientation_origin_event_id"] == "ORI_CORE_NIPPO_STEM"
    assert x["orientation_restricted_sensitivity_id"] == "ORI_TAIWAN_DESCENDANT_WINDOW"
    assert len(x["trait_event_rows"]) == 3
    assert len(x["restricted_sensitivity_rows"]) == 1
    assert len(x["distribution_process_rows"]) >= 5

print(json.dumps({
    "status": "ok",
    "n_rows": len(rows),
    "origin_event": origin["event_id"],
    "restricted_sensitivity": restricted["event_id"]
}, indent=2))
