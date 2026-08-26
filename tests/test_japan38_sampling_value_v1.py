import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sv", ROOT / "analysis/summarize_japan38_sampling_value_v1.py"
)
assert SPEC and SPEC.loader
sv = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sv)


class TestJapan38SamplingValue(unittest.TestCase):
    def test_identity_gate_precedes_analytical_gain(self):
        audit = [
            {
                "paper_japan_member_id": "JPN_A",
                "paper_taxon_concept": "A",
                "tree_codes": "A",
                "paper_japan_membership_confidence": "high",
                "sample_origin_class": "direct_Japan_sample_or_public_locality",
                "current_name_status": "ok",
            },
            {
                "paper_japan_member_id": "JPN_B",
                "paper_taxon_concept": "B",
                "tree_codes": "B",
                "paper_japan_membership_confidence": "medium",
                "sample_origin_class": "cultivated_Japanese_taxon_name_conflict",
                "current_name_status": "pending",
            },
            {
                "paper_japan_member_id": "JPN_C",
                "paper_taxon_concept": "C",
                "tree_codes": "C",
                "paper_japan_membership_confidence": "high",
                "sample_origin_class": "direct_Japan_sample_or_public_locality",
                "current_name_status": "pending",
            },
        ]
        conflicts = [
            {"tree_code": "C", "priority": "critical", "conflict_type": "swap"}
        ]
        idx = sv.identity_index(audit, conflicts)
        self.assertEqual(idx["JPN_A"]["identity_gate"], "pass")
        self.assertEqual(idx["JPN_B"]["identity_gate"], "caution")
        self.assertEqual(idx["JPN_C"]["identity_gate"], "block")

        def metric(mid, gate, worst, best):
            return {
                "paper_japan_member_id": mid,
                "identity_gate": gate,
                "robust_transition_localization_gain": worst,
                "best_case_transition_localization_gain": best,
                "states_reducing_root_state_count": 0,
                "minimum_root_state_count_across_scenarios": 1,
                "states_changing_minimum_steps": 0,
                "maximum_absolute_step_delta": 0,
            }

        transition, _, _ = sv.rank_missing(
            [metric("JPN_B", "caution", 10, 10), metric("JPN_A", "pass", 2, 3)]
        )
        self.assertEqual(transition[0]["paper_japan_member_id"], "JPN_A")

    def test_shortlist_falls_back_to_root_then_steps(self):
        rows = [
            {
                "paper_japan_member_id": "JPN_ROOT",
                "identity_gate": "pass",
                "robust_transition_localization_gain": 0,
                "best_case_transition_localization_gain": 0,
                "states_reducing_root_state_count": 3,
                "minimum_root_state_count_across_scenarios": 1,
                "states_changing_minimum_steps": 1,
                "maximum_absolute_step_delta": 1,
            },
            {
                "paper_japan_member_id": "JPN_STEP",
                "identity_gate": "pass",
                "robust_transition_localization_gain": -1,
                "best_case_transition_localization_gain": 0,
                "states_reducing_root_state_count": 0,
                "minimum_root_state_count_across_scenarios": 3,
                "states_changing_minimum_steps": 3,
                "maximum_absolute_step_delta": 1,
            },
        ]
        transition, root, steps = sv.rank_missing(rows)
        shortlist = sv.trait_shortlist(transition, root, steps)
        self.assertEqual(shortlist["primary_objective"], "ancestral_state_discrimination")
        self.assertEqual(shortlist["primary"]["paper_japan_member_id"], "JPN_ROOT")

    def test_validation_targets_keep_terminal_forced_edges_only(self):
        ident = {
            "bootstrap_identifiability": {
                "orientation": {
                    "top_forced_edge_frequencies": [
                        {"edge_id": "JPN_36", "fraction": 0.20},
                        {"edge_id": "JPN_01|JPN_02", "fraction": 0.90},
                        {"edge_id": "JPN_05", "fraction": 0.05},
                    ]
                },
                "phyllary": {
                    "top_forced_edge_frequencies": [
                        {"edge_id": "JPN_36", "fraction": 0.75}
                    ]
                },
                "stickiness": {
                    "top_forced_edge_frequencies": [
                        {"edge_id": "JPN_06", "fraction": 0.67}
                    ]
                },
            }
        }
        identity = {
            "JPN_36": {
                "paper_taxon_concept": "Cirsium sieboldii",
                "identity_gate": "pass",
            },
            "JPN_06": {
                "paper_taxon_concept": "Cirsium dipsacolepis",
                "identity_gate": "pass",
            },
        }
        seed = [
            {
                "paper_japan_member_id": "JPN_36",
                "orientation_state": "downward_or_nodding",
                "phyllary_posture": "appressed",
                "stickiness_state": "nonsticky_or_nearly_nonsticky",
            },
            {
                "paper_japan_member_id": "JPN_06",
                "orientation_state": "upward_or_erect",
                "phyllary_posture": "spreading_or_recurved",
                "stickiness_state": "nonsticky_or_nearly_nonsticky",
            },
        ]
        by_trait, cross = sv.validation_targets(ident, identity, seed, 0.10)
        self.assertEqual([x["paper_japan_member_id"] for x in by_trait["orientation"]], ["JPN_36"])
        self.assertEqual(cross[0]["paper_japan_member_id"], "JPN_36")
        self.assertEqual(set(cross[0]["traits"]), {"orientation", "phyllary"})


if __name__ == "__main__":
    unittest.main()
