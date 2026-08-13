from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
SPEC = importlib.util.spec_from_file_location(
    "global_cirsium_sra", ROOT / "analysis/audit_global_cirsium_sra_nuclear_data.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["global_cirsium_sra"] = mod
SPEC.loader.exec_module(mod)


class GlobalCirsiumSraAuditTests(unittest.TestCase):
    def test_compatibility_classes(self):
        self.assertEqual(
            mod.compatibility_class(
                {"LibraryStrategy": "RNA-Seq", "LibrarySource": "TRANSCRIPTOMIC", "LibrarySelection": "cDNA"}
            )[0],
            "direct_common_locus_candidate",
        )
        self.assertEqual(
            mod.compatibility_class(
                {"LibraryStrategy": "RNA-Seq", "LibrarySource": "GENOMIC", "LibrarySelection": "PCR"}
            ),
            ("not_directly_common_locus_compatible", "RNA_seq_PCR_selection_not_host_transcriptome"),
        )
        self.assertEqual(
            mod.compatibility_class(
                {"LibraryStrategy": "RNA-Seq", "LibrarySource": "VIRAL RNA", "LibrarySelection": "cDNA"}
            ),
            ("not_directly_common_locus_compatible", "RNA_seq_non_host_viral_source"),
        )
        self.assertEqual(
            mod.compatibility_class({"LibraryStrategy": "RNA-Seq"})[0],
            "manual_assay_review",
        )
        self.assertEqual(
            mod.compatibility_class({"LibraryStrategy": "WGS", "LibrarySource": "GENOMIC"})[0],
            "direct_common_locus_candidate",
        )
        self.assertEqual(
            mod.compatibility_class(
                {"LibraryStrategy": "OTHER", "LibrarySource": "GENOMIC", "LibrarySelection": "Hybrid Selection"}
            )[0],
            "direct_common_locus_candidate",
        )
        self.assertEqual(
            mod.compatibility_class({"LibraryStrategy": "AMPLICON"})[0],
            "not_directly_common_locus_compatible",
        )

    def test_audit_separates_known_and_extra_runs(self):
        rows = [
            {
                "Run":"SRR1","BioSample":"SAMN1","BioProject":"P1","ScientificName":"Cirsium a",
                "LibraryStrategy":"RNA-Seq","LibrarySource":"TRANSCRIPTOMIC","LibrarySelection":"cDNA",
                "LibraryLayout":"PAIRED"
            },
            {
                "Run":"SRR2","BioSample":"SAMN2","BioProject":"P2","ScientificName":"Cirsium b",
                "LibraryStrategy":"WGS","LibrarySource":"GENOMIC","LibraryLayout":"PAIRED"
            },
            {
                "Run":"SRR3","BioSample":"SAMN3","BioProject":"P3","ScientificName":"Cirsium c",
                "LibraryStrategy":"AMPLICON","LibrarySource":"GENOMIC","LibraryLayout":"PAIRED"
            },
        ]
        audited, summary = mod.audit(rows, {"SRR1"})
        self.assertEqual(len(audited), 3)
        self.assertEqual(summary["extra_public_cirsium_runs"], 2)
        self.assertEqual(summary["extra_direct_common_locus_candidate_runs"], 1)
        self.assertEqual(summary["extra_direct_candidate_taxa"], ["Cirsium b"])
        self.assertEqual(summary["contract_version"], "global_cirsium_sra_nuclear_audit_v2")
        self.assertFalse(summary["primary_294_panel_changed"])
        self.assertFalse(summary["automatic_tip_admission_allowed"])

    def test_known_panel_requires_frozen_295_unique_runs(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "panel.csv"
            p.write_text("run_accessions\nSRR1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "295"):
                mod.read_known_runs(p)


if __name__ == "__main__":
    unittest.main()
