from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "global_aug_queue", ROOT / "analysis/build_global_public_nuclear_augmentation_queue.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["global_aug_queue"] = mod
SPEC.loader.exec_module(mod)


class GlobalAugmentationQueueTests(unittest.TestCase):
    def test_collapses_runs_and_never_duplicates_primary_biosamples(self):
        primary = [
            {
                "biosample": "SAMN_CORE",
                "source_taxon_label": "Cirsium alpha",
                "analysis_taxon_label": "Cirsium alpha",
            },
            {
                "biosample": "SAMN_OTHER",
                "source_taxon_label": "Cirsium beta",
                "analysis_taxon_label": "Cirsium beta",
            },
        ]
        audit = [
            {
                "Run": "SRR10", "BioSample": "SAMN_NEW1", "BioProject": "P1",
                "ScientificName": "Cirsium gamma", "LibraryStrategy": "WGS", "LibrarySource": "GENOMIC",
                "LibrarySelection": "RANDOM", "LibraryLayout": "PAIRED", "Platform": "ILLUMINA",
                "size_MB": "500", "bases": "1000", "known_primary_295_srr": "false",
                "common_locus_compatibility_class": "direct_common_locus_candidate",
            },
            {
                "Run": "SRR11", "BioSample": "SAMN_NEW1", "BioProject": "P1",
                "ScientificName": "Cirsium gamma", "LibraryStrategy": "WGS", "LibrarySource": "GENOMIC",
                "LibrarySelection": "RANDOM", "LibraryLayout": "PAIRED", "Platform": "ILLUMINA",
                "size_MB": "400", "bases": "900", "known_primary_295_srr": "false",
                "common_locus_compatibility_class": "direct_common_locus_candidate",
            },
            {
                "Run": "SRR12", "BioSample": "SAMN_NEW2", "BioProject": "P2",
                "ScientificName": "Cirsium alpha", "LibraryStrategy": "Targeted-Capture", "LibrarySource": "GENOMIC",
                "LibrarySelection": "Hybrid Selection", "LibraryLayout": "PAIRED", "Platform": "ILLUMINA",
                "size_MB": "200", "bases": "700", "known_primary_295_srr": "false",
                "common_locus_compatibility_class": "direct_common_locus_candidate",
            },
            {
                "Run": "SRR13", "BioSample": "SAMN_CORE", "BioProject": "P3",
                "ScientificName": "Cirsium alpha", "LibraryStrategy": "WGS", "LibrarySource": "GENOMIC",
                "LibrarySelection": "RANDOM", "LibraryLayout": "PAIRED", "Platform": "ILLUMINA",
                "size_MB": "300", "bases": "800", "known_primary_295_srr": "false",
                "common_locus_compatibility_class": "direct_common_locus_candidate",
            },
            {
                "Run": "SRR14", "BioSample": "SAMN_RAD", "BioProject": "P4",
                "ScientificName": "Cirsium delta", "LibraryStrategy": "RAD-Seq", "LibrarySource": "GENOMIC",
                "LibrarySelection": "RANDOM", "LibraryLayout": "PAIRED", "Platform": "ILLUMINA",
                "size_MB": "100", "bases": "100", "known_primary_295_srr": "false",
                "common_locus_compatibility_class": "not_directly_common_locus_compatible",
            },
        ]
        queue, summary = mod.aggregate_runs(audit, primary)
        self.assertEqual(summary["direct_extra_sra_runs"], 4)
        self.assertEqual(summary["run_groups_after_biosample_collapse"], 3)
        self.assertEqual(summary["new_biological_sample_candidates"], 2)
        self.assertEqual(summary["new_exact_taxon_candidates"], 1)
        self.assertEqual(summary["existing_exact_taxon_independent_replicates"], 1)
        self.assertEqual(summary["existing_primary_biosample_extra_run_groups"], 1)

        by_bs = {row["biosample"]: row for row in queue}
        self.assertEqual(by_bs["SAMN_NEW1"]["run_count"], 2)
        self.assertEqual(by_bs["SAMN_NEW1"]["run_accessions"], "SRR10|SRR11")
        self.assertEqual(by_bs["SAMN_NEW1"]["total_size_mb"], 900.0)
        self.assertEqual(by_bs["SAMN_NEW1"]["priority_tier"], "A_NEW_EXACT_TAXON_BOUNDED")
        self.assertEqual(by_bs["SAMN_NEW2"]["priority_tier"], "B_REPLICATE_BOUNDED")
        self.assertEqual(by_bs["SAMN_CORE"]["priority_tier"], "MERGE_ONLY")
        self.assertFalse(by_bs["SAMN_CORE"]["automatic_tip_admission_allowed"])

    def test_nonpositive_size_metadata_does_not_enter_bounded_tier(self):
        primary = [{"biosample": "SAMN1", "source_taxon_label": "Cirsium a", "analysis_taxon_label": "Cirsium a"}]
        audit = [{
            "Run": "SRR2", "BioSample": "SAMN2", "BioProject": "P2", "ScientificName": "Cirsium b",
            "LibraryStrategy": "Targeted-Capture", "LibrarySource": "GENOMIC", "LibrarySelection": "Hybrid Selection",
            "LibraryLayout": "PAIRED", "Platform": "ILLUMINA", "size_MB": "0", "bases": "0",
            "known_primary_295_srr": "false", "common_locus_compatibility_class": "direct_common_locus_candidate",
        }]
        queue, _ = mod.aggregate_runs(audit, primary)
        self.assertEqual(queue[0]["priority_tier"], "MANUAL_SIZE")
        self.assertFalse(queue[0]["bounded_ci_pilot_shape"])


if __name__ == "__main__":
    unittest.main()
