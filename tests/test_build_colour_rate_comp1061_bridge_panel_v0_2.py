from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

PATH = ANALYSIS / "build_colour_rate_comp1061_bridge_panel_v0_2.py"
SPEC = importlib.util.spec_from_file_location("bridge_v02", PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)


class ColourRateBridgeV02Tests(unittest.TestCase):
    def test_official_project_partition_correction_is_frozen(self):
        self.assertEqual(
            bridge.CORRECTED_EXPECTED_STUDIES,
            {"Chang2025": 3, "Chang2026": 10, "Moreyra2025": 7},
        )
        self.assertEqual(sum(bridge.CORRECTED_EXPECTED_STUDIES.values()), 20)

    def test_correction_does_not_change_taxon_partition(self):
        impl = bridge.impl
        self.assertEqual(
            len(impl.CHANG_RECON_TAXA | impl.CHANG2025_DIRECT_TAXA | impl.MOREYRA_TAXA),
            20,
        )
        self.assertEqual(len(impl.CHANG_RECON_TAXA), 10)
        self.assertEqual(len(impl.CHANG2025_DIRECT_TAXA), 3)
        self.assertEqual(len(impl.MOREYRA_TAXA), 7)


if __name__ == "__main__":
    unittest.main()
