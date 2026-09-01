#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/evidence/chapter2_four_taxon_azami_measurement_result_v1.json"

x = json.loads(PATH.read_text(encoding="utf-8"))
assert x["contract_version"] == "chapter2_four_taxon_azami_measurement_result_v1"
assert x["azami_measurement_commit"] == "03ed29f1f476ca0d0a1ea8e14e75cb0050a213ef"
assert x["sampling"]["candidate_selection_uses_trait_values"] is False
assert x["sampling"]["crop_selection_uses_trait_values"] is False
assert x["sampling"]["balanced_observations_per_taxon"] == 14
assert x["colour_assay_gate"]["passed"] is True

expected = {
    "corolla_lab_chroma": "white_lower",
    "corolla_lab_lightness": "white_higher",
    "shape_circularity": "white_higher",
    "shape_solidity": "white_higher",
    "visible_floret_fraction_extended": "white_lower",
}
assert x["repeated_same_direction_across_two_sister_systems"] == expected

systems = x["systems"]
assert set(systems) == {
    "ARENICOLA_BREVICAULE_IRUMTIENSE",
    "TAIWAN_KAWAKAMII_TATAKAENSE",
}
for system in systems.values():
    c = system["contrasts_white_minus_coloured"]["corolla_lab_chroma"]
    assert c["direction"] == "white_lower"
    assert c["n_white"] >= 3 and c["n_coloured"] >= 3
    assert c["difference"] < 0

# Keep evidence strength distinct from direction replication.
aren = systems["ARENICOLA_BREVICAULE_IRUMTIENSE"]["contrasts_white_minus_coloured"]
assert aren["shape_circularity"]["bootstrap_95"][0] > 0
assert aren["shape_solidity"]["bootstrap_95"][0] > 0

taiwan = systems["TAIWAN_KAWAKAMII_TATAKAENSE"]["contrasts_white_minus_coloured"]
assert taiwan["shape_circularity"]["bootstrap_95"][0] < 0 < taiwan["shape_circularity"]["bootstrap_95"][1]
assert taiwan["shape_solidity"]["bootstrap_95"][0] < 0 < taiwan["shape_solidity"]["bootstrap_95"][1]

for phrase in ["selection", "convergence", "adaptation"]:
    assert any(phrase in item for item in x["claim_boundary"])

print(json.dumps({
    "status": "ok",
    "balanced_n": x["sampling"]["balanced_observations_per_taxon"],
    "colour_assay_gate": x["colour_assay_gate"]["passed"],
    "repeated_directions": expected,
    "interpretive_ceiling": "repeated extant phenotype direction; not correlated evolution or adaptation",
}, indent=2))
