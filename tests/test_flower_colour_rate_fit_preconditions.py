from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

BUILD_PATH = ANALYSIS / "build_cirsium_flower_colour_atlas_v0_3.py"
BUILD_SPEC = importlib.util.spec_from_file_location("build_colour_atlas_v03_for_rate_gate", BUILD_PATH)
assert BUILD_SPEC and BUILD_SPEC.loader
build = importlib.util.module_from_spec(BUILD_SPEC)
sys.modules[BUILD_SPEC.name] = build
BUILD_SPEC.loader.exec_module(build)

GATE_PATH = ANALYSIS / "validate_flower_colour_rate_fit_preconditions.py"
GATE_SPEC = importlib.util.spec_from_file_location("rate_gate", GATE_PATH)
assert GATE_SPEC and GATE_SPEC.loader
gate = importlib.util.module_from_spec(GATE_SPEC)
sys.modules[GATE_SPEC.name] = gate
GATE_SPEC.loader.exec_module(gate)

BASE = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_2.csv"
EXPANSION = ROOT / "data/evidence/cirsium_flower_colour_atlas_v0_3_expansion_evidence.csv"
TREE = ROOT / "data/evidence/flower_colour_rate_tree_contract_v0_2.json"
REFERENCE = ROOT / "data/evidence/comp1061_original_reference_contract_v1.json"
PRIMARY_TREE = ROOT / "data/evidence/full20_comp1061_primary_tree_v1.nwk"
PRIMARY_ACCEPTANCE = ROOT / "data/evidence/full20_comp1061_primary_tree_acceptance_v1.json"
CONCORDANCE = ROOT / "data/evidence/full20_comp1061_topology_concordance_result_v1.json"
ALT_TOPOLOGY = ROOT / "data/evidence/full20_comp1061_alt_topology_au_result_v1.json"


class FlowerColourRateFitPreconditionsTests(unittest.TestCase):
    def current_inputs(self):
        _, _, atlas = build.build(BASE, EXPANSION)
        tree = json.loads(TREE.read_text(encoding="utf-8"))
        return atlas, tree

    def test_frozen_original_reference_contract(self):
        x = json.loads(REFERENCE.read_text(encoding="utf-8"))
        self.assertTrue(x["compatibility_reanalysis_usable"])
        self.assertFalse(x["moreyra_augmented_reference_recovered"])
        self.assertEqual(x["locus_count"], 1061)
        self.assertEqual(x["sequence_record_count"], 2597)
        self.assertEqual(
            x["sha256"],
            "77d510ef101d08a7a23a4df391d077d3b7f75482c66f7f4bea6d32cf290ced2c",
        )

    def test_tree_contract_matches_frozen_empirical_evidence(self):
        tree = json.loads(TREE.read_text(encoding="utf-8"))
        primary = json.loads(PRIMARY_ACCEPTANCE.read_text(encoding="utf-8"))
        concordance = json.loads(CONCORDANCE.read_text(encoding="utf-8"))
        alt = json.loads(ALT_TOPOLOGY.read_text(encoding="utf-8"))
        compatibility = tree["compatibility_reanalysis_route"]

        self.assertEqual(tree["contract_version"], "flower_colour_rate_tree_contract_v0_2")
        self.assertTrue(tree["empirical_branch_length_tree_ready"])
        self.assertTrue(tree["rate_fit_execution_allowed"])
        self.assertEqual(tree["remaining_tree_blockers"], [])
        self.assertEqual(
            hashlib.sha256(PRIMARY_TREE.read_bytes()).hexdigest(),
            compatibility["primary_tree_sha256"],
        )
        self.assertEqual(compatibility["tree_loci"], 153)
        self.assertEqual(compatibility["alignment_length_bp"], 140562)
        self.assertEqual(compatibility["parsimony_informative_sites_acgt"], 2639)
        self.assertEqual(compatibility["root_outgroup"], "OUTGROUP_saff")
        self.assertEqual(
            primary["accepted_tree"]["branch_length_interpretation"],
            compatibility["branch_length_interpretation"],
        )
        self.assertTrue(primary["accepted_tree"]["tree_gate_ready"])
        self.assertEqual(
            concordance["source"]["workflow_run_id"],
            compatibility["topology_concordance_run_id"],
        )
        self.assertTrue(concordance["decision"]["topology_concordance_execution_completed"])
        self.assertEqual(
            alt["source"]["workflow_run_id"],
            compatibility["alternative_topology_run_id"],
        )
        self.assertEqual(
            alt["source"]["artifact_digest"],
            compatibility["alternative_topology_artifact_digest"],
        )
        self.assertEqual(alt["summary"]["au_nonrejected_candidates"], 6)
        self.assertEqual(len(compatibility["au_nonrejected_candidate_ids"]), 6)
        self.assertEqual(
            alt["decision"]["au_nonrejected_candidate_ids"],
            compatibility["au_nonrejected_candidate_ids"],
        )
        self.assertTrue(compatibility["primary_topology_is_maximum_likelihood"])
        self.assertFalse(compatibility["primary_topology_uniquely_supported"])
        self.assertTrue(compatibility["topology_uncertainty_must_propagate"])

    def test_current_project_is_blocked_only_by_white_tips(self):
        atlas, tree = self.current_inputs()
        result = gate.evaluate(atlas, tree)
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["eligible_taxa"], 20)
        self.assertEqual(result["eligible_state_counts"], {"C": 17, "W": 3})
        self.assertEqual(result["blockers"], ["atlas_minimum_white_tips"])
        self.assertTrue(result["empirical_branch_length_tree_ready"])
        self.assertEqual(result["tree_loci"], 153)
        self.assertEqual(result["root_outgroup"], "OUTGROUP_saff")
        self.assertEqual(result["au_nonrejected_topology_count"], 6)
        self.assertFalse(result["primary_topology_uniquely_supported"])
        self.assertTrue(result["comp1061_original_reference_available"])
        self.assertFalse(result["moreyra_augmented_reference_available"])
        self.assertEqual(
            result["target_reference_status"],
            "original_compatible_reference_recovered_augmented_not_recovered",
        )

    def test_two_additional_fixed_white_tips_would_unlock_current_combined_gate(self):
        atlas, tree = self.current_inputs()
        atlas = json.loads(json.dumps(atlas))
        atlas["readiness_conditions"]["minimum_white_tips"] = True
        atlas["transition_rate_fit_ready"] = True
        atlas["rate_fit_eligible_unique_taxa"] = 22
        atlas["rate_fit_eligible_state_counts"] = {"C": 17, "W": 5}
        result = gate.evaluate(atlas, tree)
        self.assertTrue(result["execution_allowed"])
        self.assertEqual(result["blockers"], [])
        self.assertTrue(result["empirical_branch_length_tree_ready"])
        self.assertEqual(result["au_nonrejected_topology_count"], 6)

    def test_tree_gate_remains_independent_if_tree_readiness_is_removed(self):
        atlas, tree = self.current_inputs()
        tree = json.loads(json.dumps(tree))
        tree["empirical_branch_length_tree_ready"] = False
        tree["rate_fit_execution_allowed"] = False
        tree["accepted_tree_route"] = "none"
        result = gate.evaluate(atlas, tree)
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(
            result["blockers"],
            ["atlas_minimum_white_tips", "branch_length_tree_unavailable"],
        )

    def test_tree_readiness_flags_cannot_disagree(self):
        atlas, tree = self.current_inputs()
        tree = json.loads(json.dumps(tree))
        tree["rate_fit_execution_allowed"] = False
        with self.assertRaisesRegex(ValueError, "must agree"):
            gate.evaluate(atlas, tree)


if __name__ == "__main__":
    unittest.main()
