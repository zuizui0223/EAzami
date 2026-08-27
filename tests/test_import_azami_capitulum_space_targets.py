from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "import_azami_capitulum_space_targets.py"
spec = importlib.util.spec_from_file_location("azami_capitulum_import", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)


class AzamiCapitulumImportTests(unittest.TestCase):
    def space(self):
        return pd.DataFrame([
            {
                "target_id": "capitulum_within_module_integration_contrast",
                "scope": "complete18_min5", "scale": "within_taxon",
                "value": 0.16, "ci95_low": 0.12, "ci95_high": 0.18,
                "handoff_status": "observational_structure_target",
            },
            {
                "target_id": "capitulum_among_module_integration_contrast",
                "scope": "complete18_min5", "scale": "among_taxon",
                "value": 0.09, "ci95_low": 0.03, "ci95_high": 0.13,
                "handoff_status": "observational_structure_target",
            },
            {
                "target_id": "capitulum_cross_scale_association_matrix_similarity",
                "scope": "complete18_min5", "scale": "within_vs_among",
                "value": 0.37, "ci95_low": 0.10, "ci95_high": 0.41,
                "handoff_status": "observational_structure_target",
            },
        ])

    def env(self):
        return pd.DataFrame([
            {
                "target_id": "environment_block_r2:core_thermal",
                "scope": "complete18_env_min5", "scale": "within_taxon",
                "value": 0.01,
                "handoff_status": "observational_environment_block_target",
            },
            {
                "target_id": "environment_block_cross_scale_cosine:core_thermal",
                "scope": "complete18_env_min5", "scale": "within_vs_among",
                "value": -0.2,
                "handoff_status": "descriptive_effect_geometry_target",
            },
        ])

    def test_valid_tables_are_normalized_without_causal_promotion(self):
        space, env = self.space(), self.env()
        MOD.validate_space(space)
        MOD.validate_environment(env)
        out = MOD.normalize(
            space, env,
            source_run_id="1", source_artifact_id="2",
            source_artifact_digest="sha256:" + "a" * 64,
            source_head_sha="b" * 40,
            space_sha="c" * 64, env_sha="d" * 64,
        )
        self.assertEqual(len(out), 5)
        self.assertTrue(out["simulation_role"].eq("unscored_observational_target").all())
        self.assertTrue(out["causal_status"].eq("observational_noncausal").all())

    def test_unknown_space_target_is_rejected(self):
        frame = self.space()
        frame.loc[0, "target_id"] = "made_up_target"
        with self.assertRaisesRegex(ValueError, "Unexpected capitulum-space"):
            MOD.validate_space(frame)

    def test_point_estimate_outside_ci_is_rejected(self):
        frame = self.space()
        frame.loc[0, "value"] = 0.5
        with self.assertRaisesRegex(ValueError, "inside its bootstrap interval"):
            MOD.validate_space(frame)

    def test_unknown_environment_target_is_rejected(self):
        frame = self.env()
        frame.loc[0, "target_id"] = "BIO99_magic"
        with self.assertRaisesRegex(ValueError, "Unexpected environment"):
            MOD.validate_environment(frame)


if __name__ == "__main__":
    unittest.main()
