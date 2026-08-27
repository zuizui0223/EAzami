from __future__ import annotations

import importlib.util
from pathlib import Path
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

    def incremental(self):
        return pd.DataFrame([
            {
                "target_id": "environment_incremental:all_process_extension_beyond_core4",
                "scope": "complete18_env_min5", "scale": "within_taxon",
                "test_id": "all_process_extension_beyond_core4",
                "test_family": "omnibus", "block_id": "all_process_extension",
                "delta_r2": 0.012, "partial_r2": 0.013,
                "permutation_p": 0.01, "q_bh_block_specific": pd.NA,
                "supported_0_05": True,
                "handoff_status": "observational_incremental_environment_target",
            },
            {
                "target_id": "environment_incremental:mechanical_exposure_beyond_core4",
                "scope": "complete18_env_min5", "scale": "among_taxon",
                "test_id": "mechanical_exposure_beyond_core4",
                "test_family": "block_specific", "block_id": "mechanical_exposure",
                "delta_r2": 0.02, "partial_r2": 0.025,
                "permutation_p": 0.02, "q_bh_block_specific": 0.04,
                "supported_0_05": True,
                "handoff_status": "observational_incremental_environment_target",
            },
        ])

    def test_valid_tables_are_normalized_without_causal_promotion(self):
        space, env, inc = self.space(), self.env(), self.incremental()
        MOD.validate_space(space)
        MOD.validate_environment(env)
        MOD.validate_incremental(inc)
        out = MOD.normalize(
            space, env, inc,
            source_run_id="1", source_artifact_id="2",
            source_artifact_digest="sha256:" + "a" * 64,
            source_head_sha="b" * 40,
            space_sha="c" * 64, env_sha="d" * 64, incremental_sha="e" * 64,
        )
        self.assertEqual(len(out), 7)
        self.assertTrue(out["simulation_role"].eq("unscored_observational_target").all())
        self.assertTrue(out["causal_status"].eq("observational_noncausal").all())
        row = out[out["handoff_status"].eq("observational_incremental_environment_target")].iloc[0]
        self.assertAlmostEqual(float(row["value"]), float(row["partial_r2"]))

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

    def test_unknown_incremental_target_is_rejected(self):
        frame = self.incremental()
        frame.loc[0, "target_id"] = "bad_incremental"
        with self.assertRaisesRegex(ValueError, "Unexpected incremental"):
            MOD.validate_incremental(frame)

    def test_block_specific_incremental_requires_q(self):
        frame = self.incremental()
        frame.loc[frame["test_family"].eq("block_specific"), "q_bh_block_specific"] = pd.NA
        with self.assertRaisesRegex(ValueError, "require q_bh"):
            MOD.validate_incremental(frame)


if __name__ == "__main__":
    unittest.main()
