#!/usr/bin/env python3
"""Tests for the Moreyra pilot target FASTA contract validator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "validate_moreyra_target_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_moreyra_target_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["validate_moreyra_target_contract"] = mod
SPEC.loader.exec_module(mod)


class TargetContractTests(unittest.TestCase):
    @staticmethod
    def base_contract(target: Path, sha256: str) -> dict:
        return {
            "contract_version": "0.1",
            "identity_status": "compatible_compositae1061_target",
            "target_type": "hybpiper_reference_fasta",
            "target_sequence_type": "dna",
            "mapping_mode": "bwa",
            "candidate_label": "synthetic-compatible-target",
            "local_path": str(target),
            "source": {
                "repository": "Synthetic public dataset",
                "dataset_id": "dataset-1",
                "dataset_version": "1",
                "landing_url": "https://example.org/dataset",
                "download_url": "https://example.org/target.fasta",
                "license": "CC0",
                "method_confirmation": ""
            },
            "expected": {
                "sha256": sha256,
                "record_count": 2,
                "unique_first_tokens": 2,
                "moreyra_public_locus_count": 2,
                "minimum_normalized_locus_overlap": 1.0
            },
            "approval": {
                "approved_for_12_sample_pilot": True,
                "approved_by": "test",
                "approval_date": "2026-08-11",
                "basis": "Approved as a compatible target; explicitly not exact."
            },
            "notes": []
        }

    def write_target(self, directory: Path, filename: str = "targets.fasta") -> tuple[Path, str]:
        path = directory / filename
        payload = b">gene1\n" + b"ACGT" * 100 + b"\n>gene2\n" + b"TGCA" * 100 + b"\n"
        path.write_bytes(payload)
        return path, hashlib.sha256(payload).hexdigest()

    def test_approved_compatible_target_allows_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target, sha = self.write_target(Path(tmp))
            report = mod.validate_contract(
                self.base_contract(target, sha),
                contract_path=Path(tmp) / "contract.json",
                loci=["gene1", "gene2"],
            )
        self.assertTrue(report["contract_valid"])
        self.assertTrue(report["execution_allowed"])
        self.assertEqual(report["file_metrics"]["sequence_alphabet"], "dna")
        self.assertEqual(report["file_metrics"]["matched_moreyra_loci"], 2)
        self.assertEqual(report["file_metrics"]["normalized_locus_overlap"], 1.0)

    def test_checksum_mismatch_blocks_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target, sha = self.write_target(Path(tmp))
            contract = self.base_contract(target, "0" * 64)
            report = mod.validate_contract(
                contract,
                contract_path=Path(tmp) / "contract.json",
                loci=["gene1", "gene2"],
            )
        self.assertFalse(report["contract_valid"])
        self.assertFalse(report["execution_allowed"])
        self.assertIn("Observed target SHA256 does not match", " ".join(report["errors"]))

    def test_unresolved_template_is_valid_only_in_allow_unapproved_mode(self) -> None:
        contract = {
            "contract_version": "0.1",
            "identity_status": "unresolved",
            "target_type": "hybpiper_reference_fasta",
            "target_sequence_type": "unresolved",
            "mapping_mode": "unresolved",
            "candidate_label": "",
            "local_path": "/definitely/missing/targets.fasta",
            "source": {},
            "expected": {
                "sha256": "",
                "record_count": None,
                "unique_first_tokens": None,
                "moreyra_public_locus_count": 2,
                "minimum_normalized_locus_overlap": 0.95
            },
            "approval": {
                "approved_for_12_sample_pilot": False,
                "approved_by": "",
                "approval_date": "",
                "basis": "unresolved"
            }
        }
        report = mod.validate_contract(
            contract,
            contract_path=Path("contract.json"),
            loci=["gene1", "gene2"],
            allow_unapproved=True,
        )
        self.assertTrue(report["contract_valid"])
        self.assertFalse(report["execution_allowed"])
        blocked = mod.validate_contract(
            contract,
            contract_path=Path("contract.json"),
            loci=["gene1", "gene2"],
            allow_unapproved=False,
        )
        self.assertFalse(blocked["contract_valid"])

    def test_unresolved_target_cannot_be_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target, sha = self.write_target(Path(tmp))
            contract = self.base_contract(target, sha)
            contract["identity_status"] = "unresolved"
            report = mod.validate_contract(
                contract,
                contract_path=Path(tmp) / "contract.json",
                loci=["gene1", "gene2"],
            )
        self.assertFalse(report["execution_allowed"])
        self.assertIn("unresolved target cannot be approved", " ".join(report["errors"]).lower())

    def test_exact_identity_requires_method_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target, sha = self.write_target(Path(tmp))
            contract = self.base_contract(target, sha)
            contract["identity_status"] = "exact_moreyra_target"
            report = mod.validate_contract(
                contract,
                contract_path=Path(tmp) / "contract.json",
                loci=["gene1", "gene2"],
            )
        self.assertFalse(report["execution_allowed"])
        self.assertIn("method_confirmation", " ".join(report["errors"]))

    def test_bait_filename_and_type_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target, sha = self.write_target(Path(tmp), "Compositae1061_baits.fasta")
            contract = self.base_contract(target, sha)
            contract["target_type"] = "bait_probe_fasta"
            report = mod.validate_contract(
                contract,
                contract_path=Path(tmp) / "contract.json",
                loci=["gene1", "gene2"],
            )
        self.assertFalse(report["execution_allowed"])
        self.assertIn("bait", " ".join(report["errors"]).lower())

    def test_sequence_type_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target, sha = self.write_target(Path(tmp))
            contract = self.base_contract(target, sha)
            contract["target_sequence_type"] = "protein"
            contract["mapping_mode"] = "diamond"
            report = mod.validate_contract(
                contract,
                contract_path=Path(tmp) / "contract.json",
                loci=["gene1", "gene2"],
            )
        self.assertFalse(report["execution_allowed"])
        self.assertIn("observed alphabet=dna", " ".join(report["errors"]))

    def test_contract_json_loader_rejects_non_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.json"
            path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            with self.assertRaises(mod.ContractError):
                mod.read_json(path)


if __name__ == "__main__":
    unittest.main()
