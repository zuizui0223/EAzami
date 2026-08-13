from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis/recover_comp1061_original_hybpiper_reference.py"
SPEC = importlib.util.spec_from_file_location("recover_comp1061", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class RecoverComp1061ReferenceTests(unittest.TestCase):
    def test_git_blob_sha_matches_git_object_formula(self):
        payload = b">lett-L1\nACGTN\n"
        expected = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
        self.assertEqual(module.git_blob_sha1(payload), expected)

    def test_fasta_parser_accepts_hybpiper_style_headers(self):
        payload = b">lett-L1\nACGTN\n>saff-L1\nACGT\n>sunf-L2\nNNNN\n"
        rows = module.parse_fasta(payload)
        self.assertEqual([row[0] for row in rows], ["lett-L1", "saff-L1", "sunf-L2"])

    def test_parser_rejects_invalid_dna(self):
        with self.assertRaisesRegex(ValueError, "invalid DNA characters"):
            module.parse_fasta(b">lett-L1\nACGTZ\n")

    def test_public_source_is_pinned(self):
        self.assertEqual(module.SOURCE_COMMIT, "c340244907c39579dca42060769678bf8759fa1d")
        self.assertEqual(module.EXPECTED_GITHUB_BLOB_SHA1, "4f89e234007f367ffa8aa5e2be536bc44f31f445")
        self.assertEqual(module.EXPECTED_SIZE_BYTES, 1_162_856)
        self.assertEqual(module.EXPECTED_LOCUS_COUNT, 1_061)
        self.assertEqual(module.EXPECTED_REFERENCE_PREFIXES, {"lett", "saff", "sunf"})


if __name__ == "__main__":
    unittest.main()
