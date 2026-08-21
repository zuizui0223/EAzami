import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/evidence/cirsium_demographic_transmission_meta_v1.csv"
JSON_PATH = ROOT / "data/evidence/cirsium_demographic_transmission_meta_v1.json"
SCRIPT = ROOT / "analysis/summarize_cirsium_demographic_transmission_meta_v1.py"


def test_registry_and_frozen_summary_are_consistent():
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)

    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    frozen = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    assert len(rows) == 6
    assert len({row["study_id"] for row in rows}) == 6
    assert frozen["study_count"] == 6
    assert frozen["taxon_count"] == 4
    assert frozen["fecundity_cost_supported_studies"] == 6
    assert frozen["population_transmission"] == {
        "consistent": 4,
        "context_dependent": 1,
        "blocked": 1,
    }
    assert frozen["broad_abiotic_context_tested_studies"] == 5
    assert frozen["broad_abiotic_general_moderator_support_studies"] == 0
    assert frozen["demographic_gate_tested_studies"] == 4
    assert frozen["demographic_gate_supported_studies"] == 3
