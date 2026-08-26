import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestJapan38TimeCalibrationV1(unittest.TestCase):
    def test_frozen_calibration_audit(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"audit.json"
            subprocess.run([sys.executable,str(ROOT/"analysis/audit_japan38_time_calibration_v1.py"),"--tree",str(ROOT/"data/evidence/japan38_comp1061_primary_tree_v1.nwk"),"--concept-map",str(ROOT/"data/evidence/japan38_comp1061_concept_map_v1.csv"),"--events",str(ROOT/"data/evidence/cirsium_ecological_event_windows_v1.csv"),"--output",str(out)],check=True)
            got=json.loads(out.read_text());expected=json.loads((ROOT/"data/evidence/japan38_time_calibration_audit_v1.json").read_text())
            self.assertEqual(got,expected)
if __name__=="__main__":unittest.main()
