#!/usr/bin/env python3
"""Offline end-to-end test of the Chang 2026 gene-tree workflow interfaces."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

import build_chang2026_gene_tree_panel as panel_builder  # noqa: E402
import prepare_chang2026_single_copy_orthogroups as prepare_ogs  # noqa: E402
import run_chang2026_single_copy_gene_trees as gene_runner  # noqa: E402
import run_chang2026_layout_aware_transcriptome_assembly as assembly_runner  # noqa: E402
import score_chang2026_gene_tree_hypotheses as scorer  # noqa: E402


class ChangGeneTreeWorkflowIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.panel_path = self.root / "panel.csv"
        self.hypothesis_path = self.root / "hypotheses.csv"
        self.panel_rows = self._panel_rows()
        self._write_csv(self.panel_path, self.panel_rows)
        self.hypothesis_rows = self._hypothesis_rows()
        self._write_csv(self.hypothesis_path, self.hypothesis_rows)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _panel_rows(self) -> list[dict[str, str]]:
        specifications = [
            ("C. japonicum var. takaoense", "focal_colour_morph", 6),
            ("C. japonicum var. albescens", "white_sister_control", 2),
            (
                "C. japonicum var. australe",
                "coloured_flanking_introgression_control",
                3,
            ),
            (
                "C. japonicum var. fukienense",
                "coloured_flanking_introgression_control",
                4,
            ),
            ("C. japonicum", "coloured_root_context", 2),
            ("C. lineare", "outgroup", 2),
        ]
        focal_codes = [
            ("FC", "3559", "BP"),
            ("TJ", "3807", "BP"),
            ("NH", "3835", "BP"),
            ("WY", "3560", "W"),
            ("FB", "3629", "W"),
            ("LT", "3839", "W"),
        ]
        rows: list[dict[str, str]] = []
        counter = 0
        for taxon, role, count in specifications:
            for within in range(count):
                counter += 1
                if role == "focal_colour_morph":
                    code, digits, morph = focal_codes[within]
                    voucher = f"ccy{digits}"
                    sample_id = f"{code}_{voucher}"
                else:
                    code = f"S{counter:02d}"
                    voucher = f"ccy{7000 + counter}"
                    morph = ""
                    sample_id = f"{code}_{voucher}"
                run = f"SRR{counter:06d}"
                rows.append(
                    {
                        "sample_id": sample_id,
                        "taxon": taxon,
                        "code": code,
                        "voucher": voucher,
                        "morph": morph,
                        "flower_colour_state": "white"
                        if morph == "W" or "albescens" in taxon
                        else "bluish-purple"
                        if morph == "BP"
                        else "coloured",
                        "panel_role": role,
                        "matched_run": run,
                        "matched_experiment": f"SRX{counter:06d}",
                        "matched_biosample": f"SAMN{counter:06d}",
                        "library_layout": "PAIRED",
                        "matched_spots": str(counter * 1000),
                        "read_count_relation": (
                            "exact_paired_end_raw_reads_equals_2x_spots"
                            if counter <= 9
                            else "not_matching_reported_raw_reads"
                        ),
                        "run_match_status": "verified_unique_read_count_and_taxon",
                        "run_match_confidence": "verified",
                        "public_transcriptome_status": "not_recovered_by_current_ncbi_query",
                        "preferred_sequence_source": run,
                        "tsa_accessions": "",
                        "assembly_accessions": "",
                        "de_novo_required": "true",
                        "analysis_panel": "sinocirsium17_plus_lineare2",
                    }
                )
        return rows

    def _hypothesis_rows(self) -> list[dict[str, object]]:
        nearest_path = (
            REPO_ROOT
            / "analysis"
            / "chang2026_takaoense_nearest_no_regain_topologies.csv"
        )
        summary_path = (
            REPO_ROOT
            / "analysis"
            / "chang2026_takaoense_topology_robustness_summary.json"
        )
        with nearest_path.open(encoding="utf-8-sig", newline="") as handle:
            nearest = list(csv.DictReader(handle))
        robustness = json.loads(summary_path.read_text(encoding="utf-8"))
        return panel_builder.build_hypotheses(nearest, robustness)

    def test_end_to_end_offline_interfaces(self) -> None:
        # 1. Validate the 19-sample official-layout SRA panel and produce plans.
        validated = assembly_runner.validate_panel(self.panel_path)
        self.assertEqual(len(validated), 19)
        self.assertEqual({row["library_layout"] for row in validated}, {"PAIRED"})
        assembly_plans = [
            assembly_runner.command_plan(
                row,
                outdir=self.root / "assembly",
                fasterq_threads=2,
                fastp_threads=2,
                trinity_threads=4,
                trinity_memory_gb=16,
                fasterq_executable="fasterq-dump",
                pigz_executable="pigz",
                fastp_executable="fastp",
                trinity_executable="Trinity",
                transdecoder_longorfs_executable="TransDecoder.LongOrfs",
                transdecoder_predict_executable="TransDecoder.Predict",
                python_executable="python",
                prefix_script=ANALYSIS_DIR / "prefix_fasta_headers.py",
            )
            for row in validated
        ]
        assembly_results = assembly_runner.execute(
            assembly_plans,
            outdir=self.root / "assembly",
            jobs=2,
            dry_run=True,
            force=False,
            keep_raw_reads=False,
        )
        self.assertEqual(
            Counter(row["status"] for row in assembly_results),
            Counter({"planned_dry_run": 19}),
        )
        self.assertEqual(
            Counter(row["library_layout"] for row in assembly_results),
            Counter({"PAIRED": 19}),
        )

        # 2. Synthesize one complete OrthoFinder candidate and revalidate it.
        result_root = self.root / "orthofinder" / "Results_test"
        orthogroups = result_root / "Orthogroups"
        sequences = result_root / "Orthogroup_Sequences"
        orthogroups.mkdir(parents=True)
        sequences.mkdir(parents=True)
        (orthogroups / "Orthogroups_SingleCopyOrthologues.txt").write_text(
            "OG0001\n", encoding="utf-8"
        )
        (sequences / "OG0001.fa").write_text(
            "".join(
                f">{row['sample_id']}|protein1\nMPEPTIDE{index}\n"
                for index, row in enumerate(self.panel_rows, start=1)
            ),
            encoding="utf-8",
        )
        og_out = self.root / "single_copy"
        manifest, og_summary = prepare_ogs.prepare(
            self.root / "orthofinder", self.panel_path, og_out
        )
        self.assertEqual(og_summary["complete_single_copy_count"], 1)
        manifest_path = og_out / "single_copy_orthogroup_manifest.csv"
        prepare_ogs.write_csv(
            manifest_path, manifest, prepare_ogs.MANIFEST_FIELDS
        )

        # 3. Plan rooted MAFFT/ClipKIT/IQ-TREE commands without external tools.
        outgroups = gene_runner.read_outgroups(self.panel_path)
        gene_plans = [
            gene_runner.command_plan(
                row,
                outdir=self.root / "gene_trees",
                outgroups=outgroups,
                threads_per_gene=1,
                bootstrap_replicates=100,
                alrt_replicates=100,
                mafft_executable="mafft",
                clipkit_executable="clipkit",
                iqtree_executable="iqtree2",
            )
            for row in gene_runner.complete_manifest_rows(manifest_path)
        ]
        gene_results = gene_runner.execute(
            gene_plans,
            outdir=self.root / "gene_trees",
            jobs=1,
            dry_run=True,
            force=False,
        )
        self.assertEqual(gene_results[0]["status"], "planned_dry_run")
        self.assertIn(",".join(outgroups), gene_plans[0]["iqtree_command"])

        # 4. Score published, loss-only and unresolved synthetic gene trees.
        tree_dir = self.root / "synthetic_trees"
        tree_dir.mkdir()
        mapping = {
            "FC_3559_BP": "FC_ccy3559",
            "TJ_3807_BP": "TJ_ccy3807",
            "NH_3835_BP": "NH_ccy3835",
            "WY_3560_W": "WY_ccy3560",
            "FB_3629_W": "FB_ccy3629",
            "LT_3839_W": "LT_ccy3839",
        }
        published = self.hypothesis_rows[0]["topology_newick"]
        published_samples = str(published)
        for label, sample in mapping.items():
            published_samples = published_samples.replace(label, sample)
        loss_samples = str(self.hypothesis_rows[1]["topology_newick"])
        for label, sample in mapping.items():
            loss_samples = loss_samples.replace(label, sample)
        star = "(" + ",".join(mapping.values()) + ");"
        (tree_dir / "OGpub.treefile").write_text(
            published_samples, encoding="utf-8"
        )
        (tree_dir / "OGloss.treefile").write_text(
            loss_samples, encoding="utf-8"
        )
        (tree_dir / "OGstar.treefile").write_text(star, encoding="utf-8")

        focal, roles, morphs = scorer.panel_metadata(self.panel_path)
        hypotheses = scorer.hypothesis_metadata(self.hypothesis_path)
        details = []
        for path in scorer.tree_files(tree_dir, "*.treefile"):
            tree = scorer.parse_newick(path.read_text(encoding="utf-8"))
            detail, _ = scorer.score_one_tree(
                gene_id=path.stem,
                tree_file=str(path),
                tree=tree,
                threshold=0,
                focal_labels=focal,
                roles=roles,
                morphs=morphs,
                hypotheses=hypotheses,
            )
            details.append(detail)
        classes = Counter(row["classification"] for row in details)
        self.assertEqual(classes["published_best"], 1)
        self.assertEqual(classes["loss_only_best"], 1)
        self.assertEqual(classes["unresolved_all_hypotheses_tie"], 1)


if __name__ == "__main__":
    unittest.main()
