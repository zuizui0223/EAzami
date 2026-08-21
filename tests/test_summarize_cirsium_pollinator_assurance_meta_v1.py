import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/evidence/cirsium_pollinator_assurance_meta_v1.csv"
JSON_PATH = ROOT / "data/evidence/cirsium_pollinator_assurance_meta_v1.json"
SCRIPT = ROOT / "analysis/summarize_cirsium_pollinator_assurance_meta_v1.py"


def test_registry_and_frozen_summary_are_consistent():
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)

    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    frozen = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    assert len(rows) == 6
    assert len({row["study_id"] for row in rows}) == 6
    assert frozen["independent_study_count"] == 6
    assert frozen["high_pollinator_dependence_studies"] == 5
    assert frozen["variable_dependence_studies"] == 1
    assert frozen["exact_numeric_studies"] == 1
    assert frozen["dependence_vs_pollen_limitation_designs"] == 2
    assert frozen["dependence_vs_limitation_with_no_general_open_pollen_deficit"] == 2
    assert frozen["open_pollen_limitation_categories"] == {
        "absent": 1,
        "context_dependent": 2,
        "mostly_absent": 1,
        "not_directly_tested": 2,
    }
