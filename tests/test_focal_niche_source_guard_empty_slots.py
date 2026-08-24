from pathlib import Path
import importlib.util
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'analysis' / 'run_focal_occurrence_niche_sample_information_source_guard_v1.py'


def load_module():
    spec = importlib.util.spec_from_file_location('niche_guard', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_append_guard_audit_accepts_empty_slot_csv(tmp_path):
    module = load_module()
    pd.DataFrame([{'taxon':'Cirsium alpicola'}]).to_csv(tmp_path/'focal_niche_sampling_summary.csv', index=False)
    pd.DataFrame([{'query_name':'Cirsium alpicola'}]).to_csv(tmp_path/'gbif_taxon_matches.csv', index=False)
    # This is exactly the pandas-unreadable zero-byte CSV produced when no bridge candidates exist.
    (tmp_path/'p003_p004_niche_stratum_candidates.csv').write_text('', encoding='utf-8')
    module.append_guard_audit(tmp_path)
    slots = pd.read_csv(tmp_path/'p003_p004_niche_stratum_candidates.csv')
    assert slots.empty
    assert 'population_slot' in slots.columns
    assert 'selection_guard' in slots.columns
