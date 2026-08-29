from __future__ import annotations

import importlib.util
import unittest
from io import StringIO
from pathlib import Path

from Bio import Phylo

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "event_depth",
    ROOT / "analysis" / "summarize_japan38_relative_event_depth_v1.py",
)
assert SPEC and SPEC.loader
target = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(target)


class RelativeEventDepthTests(unittest.TestCase):
    def test_exact_envelope_does_not_weight_equal_minimum_histories(self) -> None:
        tree = Phylo.read(StringIO("((A,B),C);"), "newick")
        states = {"A": {"U"}, "B": {"U"}, "C": {"D"}}
        result = target.analyze_trait(tree, states, {"U", "D"})
        self.assertEqual(result["minimum_steps"], 1)
        self.assertEqual(result["terminal_change_count_interval"], [0, 1])
        self.assertEqual(result["internal_change_count_interval"], [0, 1])
        self.assertEqual(result["mean_relative_lineage_depth_interval"], [0.5, 1.0])

    def test_forced_terminal_history_has_zero_width(self) -> None:
        tree = Phylo.read(StringIO("((A,B),(C,D));"), "newick")
        states = {
            "A": {"D"}, "B": {"U"}, "C": {"U"}, "D": {"U"}
        }
        result = target.analyze_trait(tree, states, {"U", "D"})
        self.assertEqual(result["minimum_steps"], 1)
        self.assertEqual(result["terminal_change_count_interval"], [1, 1])
        self.assertEqual(result["internal_change_count_interval"], [0, 0])
        self.assertEqual(result["mean_relative_lineage_depth_interval"], [1.0, 1.0])

    def test_contract_is_frozen_and_excludes_unready_fourth_traits(self) -> None:
        contract = target.read_json(
            ROOT / "data" / "evidence" / "chapter2_relative_event_depth_contract_v1.json"
        )
        self.assertEqual(
            contract["status"],
            "frozen_with_audited_runtime_and_provenance_amendment_before_result_admission",
        )
        self.assertEqual(contract["runtime_contract"]["biopython_version"], "1.85")
        self.assertEqual(
            contract["runtime_contract"]["accepted_python_major_minor"],
            ["3.10", "3.11"],
        )
        excluded = contract["trait_scope_boundary"]["not_a_fourth_discrete_history"]
        self.assertEqual(set(excluded), {"flower_colour", "display", "cytotype"})


if __name__ == "__main__":
    unittest.main()
