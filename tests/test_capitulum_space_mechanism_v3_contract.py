from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "validate_capitulum_space_mechanism_v3_contract.py"
spec = importlib.util.spec_from_file_location("v3_contract", SCRIPT)
assert spec is not None and spec.loader is not None
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

CONTRACT_PATH = ROOT / "data" / "contracts" / "capitulum_space_mechanism_v3_contract.json"
STRUCTURE_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_space_eazami_targets_run33035785120.csv"
ENVIRONMENT_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_eazami_targets_run33035785120.csv"
INCREMENTAL_PATH = ROOT / "data" / "evidence" / "source" / "azami_capitulum_environment_incremental_eazami_targets_run33035785120.csv"
REPORT_PATH = ROOT / "data" / "evidence" / "azami_capitulum_space_handoff_report_v1.json"


class CapitulumSpaceMechanismV3ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.structure_rows = MOD.load_csv(STRUCTURE_PATH)
        self.environment_rows = MOD.load_csv(ENVIRONMENT_PATH)
        self.incremental_rows = MOD.load_csv(INCREMENTAL_PATH)
        self.structure_index = MOD.unique_index(self.structure_rows, "structure")
        self.incremental_index = MOD.unique_index(self.incremental_rows, "incremental")

    def test_frozen_contract_resolves_seven_primary_targets(self):
        hashes = MOD.validate_source_provenance(
            self.contract,
            self.report,
            STRUCTURE_PATH,
            ENVIRONMENT_PATH,
            INCREMENTAL_PATH,
        )
        self.assertEqual(hashes["structure"], self.report["space_table_sha256"])
        self.assertEqual(MOD.validate_units(self.contract), MOD.EXPECTED_MODULE_SIZES)
        self.assertEqual(set(MOD.validate_families(self.contract)), MOD.EXPECTED_FAMILIES)
        resolved = MOD.resolve_primary_targets(
            self.contract, self.structure_index, self.incremental_index
        )
        self.assertEqual(len(resolved), 7)
        self.assertFalse(any(row["scope"].endswith("min2") for row in resolved))
        self.assertEqual(
            sum(row["target_id"] in MOD.STRUCTURE_IDS for row in resolved), 3
        )
        replication = MOD.validate_replication(
            self.contract, self.structure_index, self.incremental_index
        )
        self.assertTrue(replication["structure_positive"])
        MOD.validate_context_and_comparison(self.contract)

    def test_min2_row_cannot_enter_primary_distance(self):
        contract = copy.deepcopy(self.contract)
        contract["primary_fit_targets"][0]["scope"] = "complete18_min2"
        with self.assertRaisesRegex(ValueError, "min2 sensitivity rows"):
            MOD.resolve_primary_targets(contract, self.structure_index, self.incremental_index)

    def test_duplicate_primary_target_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["primary_fit_targets"].append(
            copy.deepcopy(contract["primary_fit_targets"][0])
        )
        with self.assertRaisesRegex(ValueError, "double-counted"):
            MOD.resolve_primary_targets(contract, self.structure_index, self.incremental_index)

    def test_support_state_must_match_frozen_observation(self):
        contract = copy.deepcopy(self.contract)
        target = next(
            row for row in contract["primary_fit_targets"]
            if row["target_id"] == "environment_incremental:all_process_extension_beyond_core4"
            and row["scale"] == "among_taxon"
        )
        target["expected_support"] = False
        with self.assertRaisesRegex(ValueError, "expected support"):
            MOD.resolve_primary_targets(contract, self.structure_index, self.incremental_index)

    def test_endpoint_specific_tuning_is_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["generator_constraints"]["endpoint_specific_parameter_tuning"] = True
        with self.assertRaisesRegex(ValueError, "Endpoint-specific"):
            MOD.validate_units(contract)

    def test_table_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tampered = Path(tmp) / "structure.csv"
            tampered.write_text(STRUCTURE_PATH.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "structure table SHA-256"):
                MOD.validate_source_provenance(
                    self.contract,
                    self.report,
                    tampered,
                    ENVIRONMENT_PATH,
                    INCREMENTAL_PATH,
                )


if __name__ == "__main__":
    unittest.main()
