from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_scale_specific_covariance_v4_contract.py"
spec = importlib.util.spec_from_file_location("scale_cov_v4", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

CONTRACT_PATH = ROOT / "data" / "contracts" / "scale_specific_covariance_v4_contract.json"
V3_CONTRACT_PATH = ROOT / "data" / "contracts" / "capitulum_space_mechanism_v3_contract.json"
STRUCTURE_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv"
ENVIRONMENT_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_eazami_targets_run33035785120.csv"
INCREMENTAL_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv"
HANDOFF_PATH = ROOT / "data" / "evidence" / "azami_capitulum_space_handoff_report_v1.json"
V3_RESULT_PATH = ROOT / "data" / "evidence" / "capitulum_space_mechanism_v3_1_result_summary.json"


class ScaleSpecificCovarianceV4ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.v3_contract = json.loads(V3_CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.handoff = json.loads(HANDOFF_PATH.read_text(encoding="utf-8"))
        cls.v3_result = json.loads(V3_RESULT_PATH.read_text(encoding="utf-8"))
        cls.structure_rows = MOD.load_csv(STRUCTURE_PATH)
        cls.environment_rows = MOD.load_csv(ENVIRONMENT_PATH)
        cls.incremental_rows = MOD.load_csv(INCREMENTAL_PATH)
        cls.structure_idx = MOD.index_rows(cls.structure_rows, "structure")
        cls.environment_idx = MOD.index_rows(cls.environment_rows, "environment")
        cls.incremental_idx = MOD.index_rows(cls.incremental_rows, "incremental")

    def test_frozen_contract_validates_against_immutable_sources(self):
        hashes = MOD.validate_source(
            self.contract,
            self.handoff,
            self.v3_result,
            STRUCTURE_PATH,
            ENVIRONMENT_PATH,
            INCREMENTAL_PATH,
        )
        self.assertEqual(hashes["structure"], self.handoff["space_table_sha256"])
        observed = MOD.resolve_observed(self.structure_idx, self.incremental_idx)
        gap = MOD.validate_gap(self.contract, observed, self.v3_result)
        self.assertAlmostEqual(
            gap["observed_among_to_within_module_contrast_ratio"],
            observed["observed_among_module_contrast"]
            / observed["observed_within_module_contrast"],
            places=14,
        )
        MOD.validate_shared_generator(self.contract)
        families = MOD.validate_families(self.contract)
        self.assertEqual([row["family_id"] for row in families], MOD.EXPECTED_FAMILIES)
        MOD.validate_structural_constraints(self.contract)
        MOD.validate_targets(self.contract, self.v3_contract)
        self.assertEqual(MOD.validate_context(self.contract, self.environment_idx), 12)
        self.assertEqual(
            MOD.validate_screen(self.contract)["absolute_primary_adequacy_threshold"],
            1.0,
        )
        MOD.validate_promotion(self.contract)

    def test_gap_ratio_must_match_source_values(self):
        contract = copy.deepcopy(self.contract)
        contract["frozen_gap_diagnosis"][
            "observed_among_to_within_module_contrast_ratio"
        ] += 0.01
        observed = MOD.resolve_observed(self.structure_idx, self.incremental_idx)
        with self.assertRaisesRegex(ValueError, "among/within contrast ratio mismatch"):
            MOD.validate_gap(contract, observed, self.v3_result)

    def test_endpoint_specific_tuning_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["shared_generator_requirements"][
            "endpoint_specific_parameter_tuning"
        ] = True
        with self.assertRaisesRegex(ValueError, "Endpoint tuning"):
            MOD.validate_shared_generator(contract)

    def test_within_only_factor_must_have_exact_zero_taxon_mean(self):
        contract = copy.deepcopy(self.contract)
        contract["structural_constraints"]["within_only_module_factor"][
            "exact_taxon_mean"
        ] = 0.01
        with self.assertRaisesRegex(ValueError, "exact taxon mean zero"):
            MOD.validate_structural_constraints(contract)

    def test_mosaic_family_feature_change_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        family = next(
            row for row in contract["model_families"]
            if row["family_id"] == "among_unit_mosaic_loadings"
        )
        family["within_only_module_factor"] = True
        with self.assertRaisesRegex(ValueError, "Unexpected structural features"):
            MOD.validate_families(contract)

    def test_min2_target_cannot_replace_main_fit_target(self):
        contract = copy.deepcopy(self.contract)
        contract["primary_fit_targets"]["scope"] = "main_and_min2"
        with self.assertRaisesRegex(ValueError, "main min5 only"):
            MOD.validate_targets(contract, self.v3_contract)

    def test_cross_scale_cosines_cannot_enter_context_gate(self):
        contract = copy.deepcopy(self.contract)
        contract["replication_and_context_validation"][
            "main_environment_block_r2_context"
        ]["cross_scale_cosines_excluded"] = False
        with self.assertRaisesRegex(ValueError, "cosines must stay excluded"):
            MOD.validate_context(contract, self.environment_idx)

    def test_source_table_hash_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tampered = Path(tmp) / "structure.csv"
            tampered.write_text(
                STRUCTURE_PATH.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "structure table hash mismatch"):
                MOD.validate_source(
                    self.contract,
                    self.handoff,
                    self.v3_result,
                    tampered,
                    ENVIRONMENT_PATH,
                    INCREMENTAL_PATH,
                )

    def test_overflexible_context_gate_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["screen_design"][
            "maximum_context_r2_rmse_increase_relative_to_parent"
        ] = 0.20
        with self.assertRaisesRegex(ValueError, "v4 gates changed"):
            MOD.validate_screen(contract)


if __name__ == "__main__":
    unittest.main()
