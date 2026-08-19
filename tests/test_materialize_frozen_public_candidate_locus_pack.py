from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/materialize_frozen_public_candidate_locus_pack.py"
SPEC = importlib.util.spec_from_file_location("materialize_candidate_pack", SCRIPT)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class FrozenCandidatePackTests(unittest.TestCase):
    def test_all_candidate_packs_materialize_with_frozen_counts_and_checksums(self):
        expected = {
            "EA01": ("PUBEA001", 236, "candidate_pack_summary.json"),
            "EA02": ("PUBEA002", 239, "candidate_pack_summary.json"),
            "CNIPG": ("AUG_ULLEUNG_CNIP2024", 180, "cirsium_nipponicum_comp1061_locus_pack_summary.json"),
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for cid, (tip, count, summary_name) in expected.items():
                out = root / cid
                result = m.materialize(cid, out)
                self.assertEqual(result["tip_id"], tip)
                self.assertEqual(result["strict_locus_count"], count)
                self.assertTrue(result["all_per_locus_source_fasta_checksums_verified"])
                self.assertTrue(result["source_artifact_expiry_no_longer_runtime_dependency"])
                self.assertEqual(len(list((out / "loci").glob("*.fasta"))), count)
                self.assertEqual(len((out / "strict_recovered_loci.txt").read_text().splitlines()), count)
                self.assertTrue((out / summary_name).is_file())
                meta = json.loads((out / "durable_materialization.json").read_text())
                self.assertEqual(meta["candidate_id"], cid)


if __name__ == "__main__":
    unittest.main()
